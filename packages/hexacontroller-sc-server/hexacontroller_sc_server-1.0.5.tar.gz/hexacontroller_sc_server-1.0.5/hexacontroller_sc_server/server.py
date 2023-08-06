from schema import Schema, Or, Optional, SchemaError
import zmq
import yaml
import logging

from . import i2c_utilities
from . import Hexaboard


cmd_schema_recv = Schema({'type':
                          Or('set', 'get', 'describe', 'reset', 'stop'),
                          Optional('read_back', default=False): bool,
                          'status': 'send',
                          'args': dict})


class Postman():
    """
    A message handler for incoming requests from the clients.
    """

    def __init__(self, letter: str, config_table: str, logger: object) -> None:
        self.letter = letter
        self.config_table = config_table
        self.logger = logger

        return

    def validate_letter(self, letter: str) -> dict:
        """
        Checks that the letter is parsable

        :param letter: Message received from the client which needs to
            be validated
        :type letter: str
        :return: Any errors which occurred during validation
        :rtype: dict
        """
        errors = None
        directives = yaml.safe_load(letter)
        try:
            directives = cmd_schema_recv.validate(directives)
        except SchemaError as err:
            errors = {'type': directives['type'],
                      'status': 'error',
                      'args': {},
                      'errmsg': str(err)}
        self.directives = directives

        return errors

    def deliver_letter(self, hexaboard_instance: object, persist) -> str:
        """
        Perform the configuration on the ROC as directed by the message.

        :param hexaboard_instance: A Hexaboard object to write to
        :type hexaboard_instance: object
        :param persist: A flag which specifies the state of the server.
            True to run and False to stop.
        :type persist: bool
        :return: A message containing the response of the hexaboard and the
            persist flag.
        :rtype: tuple
        """
        recv = {}
        err = None
        directives = self.directives
        self.logger.info(f"Received request of type {self.directives['type']}")
        self.logger.debug("Recieved request contains args "
                          f"{self.directives['args']}")
        match directives['type']:
            case 'get':
                try:
                    recv = hexaboard_instance.read(directives['args'])
                except KeyError as error:
                    err = error
                except ValueError as error:
                    err = error
            case 'set':
                try:
                    hexaboard_instance.configure(directives['args'],
                                                 directives['read_back'])
                except KeyError as error:
                    err = error
                except ValueError as error:
                    err = error
                except IOError as error:
                    err = error
            case 'describe':
                recv = hexaboard_instance.describe()
            case 'reset':
                hexaboard_instance.reset()
            case 'stop':
                persist = False
        if err is None:
            response = {'type': directives['type'],
                        'status': 'success',
                        'args': recv}
        else:
            response = {'type': directives['type'],
                        'status': 'error',
                        'args': recv,
                        'errmsg': str(err)}
            self.logger.error(f'Request returned error: "{err}"')

        return response, persist


def open_socket(port: int) -> object:
    """
    Opens the zmq socket on the specified port.

    :param port: The port to bind the socket to
    :type port: int
    :return: A zmq socket object
    :rtype: object
    """
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f'tcp://0.0.0.0:{port}')

    return socket


def run(config_table: str, socket: object):
    """
    Runs the zmq server and listens for requests

    :param config_table: A file path to a register map for the ROC version
    :type config_table: str
    :param socket: The zmq socket to use
    :type socket: object
    """
    logger = logging.getLogger()
    persist = True
    try:
        board_type, description = i2c_utilities.find_links()
        hexaboard_instance = Hexaboard.Hexaboard(board_type,
                                                 description,
                                                 config_table)
    except IndexError as e:
        logger.critical(f'{e.args[0]}', exc_info=True)
        persist = False

    # Listen for communications
    while persist:
        try:
            letter = socket.recv()
            if letter:
                mail = Postman(letter, config_table, logger)
                errors = mail.validate_letter(letter)
                if errors is not None:
                    response = errors
                    logger.error(f'Message is invalid: "{errors}"')
                else:
                    response, persist = mail.deliver_letter(hexaboard_instance,
                                                            persist)
            socket.send_string(yaml.dump(response, sort_keys=False))
        except KeyboardInterrupt:
            persist = False

    socket.close()
    logger.info("Closing i2c server...")
    print("Closing server...")
