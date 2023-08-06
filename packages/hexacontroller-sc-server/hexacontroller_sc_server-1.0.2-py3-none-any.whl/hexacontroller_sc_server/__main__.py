import click
import logging

from roc_configuration import server


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
            config_path = 'regmaps/HGCROC3_I2C_params_regmap.csv'
        case 'ROCv2':
            config_path = 'regmaps/something else'
        # add all cases when I have all the regmaps

    return config_path


@click.command()
@click.option('--logfile', default='roc_configuration.log',
              help='Output file for the logger. \
                      Defaults to ./roc_configuration.log')
@click.option('--port', default='5555',
              help='Port for zmq communication')
@click.option('--roc', default='ROCv3',
              help='Type of chip in use. Can be ROCv3, ROCv2, ROCv3S. \
                      Defaults to ROCv3')
@click.option('--loglevel', default='INFO',
              type=click.Choice(['DEBUG', 'INFO',
                                 'WARNING', 'ERROR',
                                 'CRITICAL'], case_sensitive=False))
def run_server(logfile, port, roc, loglevel):
    port = int(port)
    check_port(port)
    logging.basicConfig(filename=logfile, level=log_level_dict[loglevel],
                        format='[%(asctime)s] %(levelname)s:'
                               '%(name)-30s %(message)s')
    logging.info('Starting zmq-i2c_server instance...')
    config_table = retrieve_config_path(roc)
    socket = server.open_socket(port)
    server.run(config_table, socket)


if __name__ == "__main__":
    run_server()
