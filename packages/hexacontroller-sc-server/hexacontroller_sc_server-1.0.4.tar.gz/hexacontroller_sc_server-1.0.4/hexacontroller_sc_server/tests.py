from _pytest.monkeypatch import monkeypatch
import multiprocessing as mp
import pytest
import zmq
import yaml
import logging
import time

# from build.lib.roc_configuration import i2c_utilities

from .ROCv3 import ROCv3
from .i2c_utilities import discover_roc_links
from .mock_io import mock_Xil_gpio
from .mock_io import MockSMBus
from . import hexactrl_io
from . import Hexaboard
from . import server
from . import i2c_utilities


def compose(start_addresses):
    responding_addresses = []
    for bus, address in zip(*start_addresses):
        responding_addresses += \
                list((bus, x) for x in list(range(address, address + 8)))

    return responding_addresses


i2c_test_peripherals = {}
peripherals = compose(([0, 1, 2], [0x20, 0x40, 0x60]))
for bus, peripherals in peripherals:
    i2c_test_peripherals[bus] = peripherals
MockSMBus.set_peripherals(i2c_test_peripherals)


@pytest.fixture
def patched_io(monkeypatch):
    def mock_find_links():
        with open("test_configs/test_hexaboard_description.yaml", "r") as f:
            description = yaml.safe_load(f)

        return ('ld_hexaboard', description)
    monkeypatch.setattr(hexactrl_io, "SMBus", MockSMBus)
    monkeypatch.setattr(Hexaboard, "Xil_gpio", mock_Xil_gpio)
    monkeypatch.setattr(hexactrl_io, "Xil_gpio", mock_Xil_gpio)
    monkeypatch.setattr(i2c_utilities, "find_links", mock_find_links)


def test_i2c_rw(patched_io):
    connection = hexactrl_io.Xil_i2c(0)
    connection.write(50, 200)
    assert 200 == connection.read(50)


@pytest.mark.parametrize("input, expected", [
    (compose(([1, 2, 3], [0x40, 0x20, 0x60])),
        ('ld_hexaboard', {'roc_s0': {'bus_id': 2, 'start_address': 32},
                          'roc_s1': {'bus_id': 1, 'start_address': 64},
                          'roc_s2': {'bus_id': 3, 'start_address': 96}})
     ),
    (compose(([1], [0x28])),
        ('char_board', {'roc_s0': {'bus_id': 1, 'start_address': 0x28}})
     ),
    (compose(([1, 3, 4, 2, 6, 7], [0x18, 0x30, 0x08, 0x20, 0x10, 0x28])),
        ('hd_hexaboard', {'roc_s0_0': {'bus_id': 1, 'start_address': 0x18},
                          'roc_s0_1': {'bus_id': 3, 'start_address': 0x30},
                          'roc_s1_0': {'bus_id': 4, 'start_address': 0x08},
                          'roc_s1_1': {'bus_id': 2, 'start_address': 0x20},
                          'roc_s2_0': {'bus_id': 6, 'start_address': 0x10},
                          'roc_s2_1': {'bus_id': 7, 'start_address': 0x28}}
         )
     )])
def test_discover_roc_links(input, expected):
    assert discover_roc_links(input) == expected


@pytest.mark.parametrize(
        "config, result",
        [
            ({
              'DigitalHalf': {1: {'IdleFrame': 200}}
              },
             True
             ),
            ({
              'GlobalAnalog': {1: {'ON_toa': 3}}
              },
             False
             )
        ])
def test_validator(config, result, patched_io):
    roc_s0 = ROCv3(name='roc_s0', transport=None, base_address=None,
                   reset_pin=hexactrl_io.Xil_gpio('that', 'rst', 'output'),
                   path_to_file='regmaps/HGCROC3_I2C_params_regmap.csv')
    if result is True:
        assert roc_s0._validate(config) == result
    else:
        with pytest.raises(ValueError):
            roc_s0._validate(config)


@pytest.mark.parametrize(
        "config, registers",
        [
            ({
              'DigitalHalf': {1: {'IdleFrame': 200}}
              },
             [(112, 5, 200, 255), (113, 5, 0, 255),
              (114, 5, 0, 255), (115, 5, 0, 15)]
             )
        ])
def test_translator(config, registers, patched_io):
    roc_s0 = ROCv3(name='roc_s0', transport=None, base_address=None,
                   reset_pin=hexactrl_io.Xil_gpio('that', 'rst', 'output'),
                   path_to_file='regmaps/HGCROC3_I2C_params_regmap.csv')
    assert roc_s0._translate(config) == registers


def test_cache(patched_io):
    write = [
            (112, 5, 200, 255), (113, 5, 0, 255),
            (114, 5, 0, 255), (115, 5, 0, 15)]
    cached_write = [(112, 5, 200), (113, 5, 0), (114, 5, 0), (115, 5, 0)]
    roc_s0 = ROCv3(name='roc_s0', transport=None, base_address=None,
                   reset_pin=hexactrl_io.Xil_gpio('that', 'rst', 'output'),
                   path_to_file='regmaps/HGCROC3_I2C_params_regmap.csv')
    assert roc_s0._cache(write) == cached_write
    assert roc_s0._cache(write) == []


@pytest.mark.parametrize(
        "write_dict, read_dict, parameter, value",
        [
            ({'DigitalHalf': {1: {'Adc_TH': 2}}},
             {'DigitalHalf': {1: {'Adc_TH': None}}},
             ['DigitalHalf', 1, 'Adc_TH'], (110, 5, 0, 31)),
            ({'GlobalAnalog': {1: {'ON_toa': 4}}},
             {'GlobalAnalog': {1: {'ON_toa': None}}},
             ['GlobalAnalog', 1, 'ON_toa'], (34, 5, 0, 1))
        ]
)
def test_translate_read(write_dict, read_dict, parameter, value, patched_io):
    roc_s0 = ROCv3(name='roc_s0', transport=None, base_address=0x28,
                   reset_pin=hexactrl_io.Xil_gpio('that', 'rst', 'output'),
                   path_to_file='regmaps/HGCROC3_I2C_params_regmap.csv')
    writes = roc_s0._translate(write_dict)
    _ = roc_s0._cache(writes)
    key_value_pairs = roc_s0._translate_read(read_dict, param_reg_pairs=[])
    assert key_value_pairs[0][0] == parameter
    assert key_value_pairs[0][1] == [value]


@pytest.mark.parametrize(
        "write_config, read_config",
        [
            ({'DigitalHalf': {1: {'Adc_TH': 8}}},
             {'DigitalHalf': {1: {'Adc_TH': None}}}),
            ({'DigitalHalf': {1: {'Adc_TH': 8},
                              0: {'L1Offset': 10}}},
             {'DigitalHalf': {1: {'Adc_TH': None},
                              0: {'L1Offset': None}}}),
            ({'GlobalAnalog': {1: {'ON_toa': 1}}},
             {'GlobalAnalog': {1: {'ON_toa': None}}}),
            ({'GlobalAnalog': {1: {'ON_toa': 0}}},
             {'GlobalAnalog': {1: {'ON_toa': None}}}),
        ]
)
def test_read(write_config, read_config, patched_io):
    roc_s0 = ROCv3(name='roc_s0', transport=None, base_address=0x28,
                   reset_pin=hexactrl_io.Xil_gpio('that', 'rst', 'output'),
                   path_to_file='regmaps/HGCROC3_I2C_params_regmap.csv')
    writes = roc_s0._translate(write_config)
    _ = roc_s0._cache(writes)
    read_config = roc_s0.read(read_config)
    assert read_config == write_config


def test_load_config(patched_io):
    with open('test_configs/roc_test_config.yml', 'r') as f:
        test_config = yaml.safe_load(f)
    with open('test_configs/roc_test_config_none.yml', 'r') as f:
        test_config_none = yaml.safe_load(f)
    rst = hexactrl_io.Xil_gpio(0, 2, 'output')
    test_chip = ROCv3(hexactrl_io.Xil_i2c(0),
                      0, 'test1', rst,
                      path_to_file='regmaps/HGCROC3_I2C_params_regmap.csv')
    test_chip.read(test_config_none)
    test_chip.configure(test_config)
    assert test_chip.read(test_config_none) == test_config


def test_hexaboard_description(patched_io):
    with open('test_configs/test_hexaboard_description.yaml', 'r') as f:
        description = yaml.safe_load(f)
    with open('test_configs/board_test_config.yml', 'r') as f:
        test_config = yaml.safe_load(f)
    with open('test_configs/board_test_config_none.yml', 'r') as f:
        test_config_none = yaml.safe_load(f)
    test_board = Hexaboard.Hexaboard('ld_hexaboard', description,
                                     './regmaps/HGCROC3_I2C_params_regmap.csv')
    test_board.configure(test_config)
    assert test_board.read(test_config_none) == test_config


def test_zmq_i2c_server(patched_io):
    with open("test_configs/board_test_config.yml", "r") as f:
        config = yaml.safe_load(f)
    with open("test_configs/board_test_config_none.yml", "r") as f:
        config_none = yaml.safe_load(f)
    with open("test_configs/board_test_config_empty.yaml", "r") as f:
        config_empty = yaml.safe_load(f)

    sendset = {'type': 'set',
               'status': 'send',
               'args': config}
    sendempty = {'type': 'set',
                 'status': 'send',
                 'args': config_empty}
    sendget = {'type': 'get',
               'status': 'send',
               'args': config_none}

    def proc_run_server():
        logging.basicConfig(filename='roc_configuration.log')
        config_table = 'regmaps/HGCROC3_I2C_params_regmap.csv'
        socket = server.open_socket(5555)
        server.run(config_table, socket)

    proc = mp.Process(target=proc_run_server)
    proc.start()

    time.sleep(2)
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    socket.send_string(str(yaml.dump(sendset)))
    socket.recv()

    socket.send_string(str(yaml.dump(sendget)))
    recv = yaml.safe_load(socket.recv())
    assert config == recv['args']

    socket.send_string(str(yaml.dump(sendempty)))
    recv = yaml.safe_load(socket.recv())
    assert recv['status'] == 'error'

    socket.send_string(str(yaml.dump({'type': 'stop',
                                      'status': 'send',
                                      'args': {}})))
    socket.recv()

    return


def test_describe_type(patched_io):
    with open("./test_configs/hexaboard_tree_description.yaml", "r") as f:
        expected_recv = yaml.safe_load(f)
    send = {'type': 'describe',
            'status': 'send',
            'args': {}}

    def proc_run_server():
        logging.basicConfig(filename='roc_configuration.log')
        config_table = 'regmaps/HGCROC3_I2C_params_regmap.csv'
        socket = server.open_socket(5555)
        server.run(config_table, socket)

    proc = mp.Process(target=proc_run_server)
    proc.start()

    time.sleep(2)
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    socket.send_string(str(yaml.dump(send)))
    recv = yaml.safe_load(socket.recv())
    assert recv['args'] == expected_recv

    socket.send_string(str(yaml.dump({'type': 'stop',
                                      'status': 'send',
                                      'args': {}})))
    socket.recv()

    return
