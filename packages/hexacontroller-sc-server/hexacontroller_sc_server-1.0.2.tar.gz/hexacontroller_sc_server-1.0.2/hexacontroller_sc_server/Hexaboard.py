from .ROCv3 import ROCv3
from .hexactrl_io import Xil_gpio
from .hexactrl_io import Xil_i2c
import logging


class Hexaboard():
    def __init__(self, type: str, description: dict, config_table: str,
                 parent_logger: logging.Logger = None):
        self.type = type
        self.description = description
        self.rocs = {}
        self.board_description = None  # Description returned by describe()
        if parent_logger is None:
            self.logger = logging.getLogger(f"{type}")
        else:
            self.logger = parent_logger.getChild(f"{type}")
        # instantiate all the busses first, so that we can pass them to
        # the roc instances
        i2c_bus_ids = set(map(lambda x: x['bus_id'], description.values()))
        i2c_busses = {}

        for bus_id in i2c_bus_ids:
            i2c_busses[bus_id] = Xil_i2c(bus_id)
        self.logger.debug(f"found busses {i2c_bus_ids} connected to rocs")

        # Check for the board type here. If a v3 hexaboard is present
        # the pin to reset all the rocs is common to the hexaboard
        # so the reset pin should only be instantiated once and the reset
        # function needs to be aware of the different way to reset the rocs
        if type == 'ld_hexaboard_v3':
            all_reset_pins = [pin for connection in description.values()
                              for pin in connection['gpio']]
            board_reset_pin = list(
                    filter(lambda x: x['line'] == 'hard_resetn',
                           all_reset_pins))[0]
            self.reset_pin = Xil_gpio(board_reset_pin['chip'],
                                      board_reset_pin['line'], 'output')
        else:
            self.reset_pin = None

        for roc, connections in description.items():
            bus_id = connections['bus_id']
            roc_gpio = connections['gpio']
            reset_pin = None
            for entry in roc_gpio:
                chip = entry['chip']
                pin = entry['line']
                if type == 'ld_hexaboard_v3' and 'hard' not in pin:
                    reset_pin = Xil_gpio(chip, pin, 'output')
                elif 'i2c_rstn' in pin:
                    reset_pin = Xil_gpio(chip, pin, 'output')
            assert reset_pin is not None
            self.rocs[roc] = ROCv3(transport=i2c_busses[bus_id],
                                   base_address=connections['start_address'],
                                   name=roc,
                                   reset_pin=reset_pin,
                                   path_to_file=config_table
                                   )
        # finally set the system into the default state
        self.reset()

    def configure(self, configuration: dict, readback: bool = False):
        for roc_name in self.rocs.keys():
            if roc_name in configuration.keys():
                self.rocs[roc_name].configure(configuration[roc_name],
                                              readback=readback)
        common_rocs = [roc for roc in configuration.keys()
                       if roc in self.rocs.keys()]
        # Raise error if there is nothing to configure
        if len(common_rocs) == 0:
            self.logger.error('No ROCs from config found in '
                              f'ROCs {list(self.rocs.keys())}')
            raise ValueError('No ROCs from config found in '
                             f'ROCs {list(self.rocs.keys())}')

    def read(self, configuration):
        recv = {}
        for roc_name in self.rocs.keys():
            if roc_name in configuration:
                recv[roc_name] = \
                    self.rocs[roc_name].read(configuration[roc_name])
        return recv

    def reset(self):
        if self.reset_pin is not None:
            self.reset_pin.write(0)
            self.reset_pin.write(1)
            for roc in self.rocs.values():
                roc.reset_cache()
        else:
            for roc in self.rocs.values():
                roc.reset()

    def describe(self):
        if self.board_description is None:
            self.board_description = self._get_description()

        return self.board_description

    def _get_description(self):
        board_dict = {}
        roc_dict = {}
        for roc, _ in self.description.items():
            roc_dict[roc] = self.rocs[roc].describe()

        board_dict[self.type] = roc_dict

        return board_dict
