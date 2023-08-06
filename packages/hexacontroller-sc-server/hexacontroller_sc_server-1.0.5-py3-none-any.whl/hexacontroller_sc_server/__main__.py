import click
import logging
from importlib import resources

from hexacontroller_sc_server import server


log_level_dict = {'DEBUG': 10,
                  'INFO': 20,
                  'WARNING': 30,
                  'ERROR': 40,
                  'CRITICAL': 50}


def check_port(port) -> None:
    if port <= 1024:
        click.echo(f"Port {port} is unavailable. \
                The port must be greater than 1024")
        exit("Terminating Program")

    return


def retrieve_config_path(roc) -> str:
    match roc:
        case 'ROCv3':
            config_path = resources.path('hexacontroller_sc_server.regmaps',
                                         'HGCROC3_I2C_params_regmap.csv')
        case 'ROCv2':
            config_path = resources.path('hexacontroller_sc_server.regmaps',
                                         'HGCROCv2_I2C_params_regmap.csv')
        case 'ROCv3-sipm':
            config_path = resources.path('hexacontroller_sc_server.regmaps',
                                         'HGCROC3_sipm_I2C_params_regmap.csv')
        case 'ROCv2-sipm':
            config_path = resources.path('hexacontroller_sc_server.regmaps',
                                         'HGCROCv2_sipm_I2C_params_regmap.csv')

    return config_path


@click.command()
@click.option('--logfile', default='sc_server.log',
              help='Output logfile. Defaults to ./sc_server.log')
@click.option('--port', default='5555',
              help='Port for zmq communication. Defaults to 5555')
@click.option('--roc', default='ROCv3',
              type=click.Choice(['ROCv3', 'ROCv3-sipm',
                                 'ROCv2', 'ROCv2-sipm'],
                                case_sensitive=False),
              help='Type of ROC on the hexaboard. Defaults to ROCv3')
@click.option('--loglevel', default='INFO',
              type=click.Choice(['DEBUG', 'INFO',
                                 'WARNING', 'ERROR',
                                 'CRITICAL'], case_sensitive=False),
              help='Sets the verbosity of the logging')
def run_server(logfile, port, roc, loglevel):
    port = int(port)
    check_port(port)
    logging.basicConfig(filename=logfile, level=log_level_dict[loglevel],
                        format='[%(asctime)s] %(levelname)-20s:'
                               '%(name)-30s %(message)s')
    logging.info('Starting zmq-i2c_server instance...')
    config_table = retrieve_config_path(roc)
    socket = server.open_socket(port)
    server.run(config_table, socket)


if __name__ == "__main__":
    run_server()
