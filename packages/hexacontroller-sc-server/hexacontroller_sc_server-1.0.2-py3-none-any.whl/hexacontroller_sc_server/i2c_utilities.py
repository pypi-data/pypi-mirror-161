import gpiod
from smbus2 import SMBus
from functools import reduce
import operator as op
from hgcal_utilities import dict_utils as dtu

expected_roc_addresses = {
    'char_board':      [('roc_s0', list(range(0x28, 0x30)))],
    'ld_hexaboard':    [('roc_s0', list(range(0x20, 0x28))),
                        ('roc_s1', list(range(0x40, 0x48))),
                        ('roc_s2', list(range(0x60, 0x68)))],
    'ld_hexaboard_v3': [('roc_s0', list(range(0x08, 0x10))),
                        ('roc_s1', list(range(0x18, 0x20))),
                        ('roc_s2', list(range(0x28, 0x30)))],
    'hd_hexaboard':    [('roc_s0_0', list(range(0x18, 0x20))),
                        ('roc_s0_1', list(range(0x30, 0x38))),
                        ('roc_s1_0', list(range(0x08, 0x10))),
                        ('roc_s1_1', list(range(0x20, 0x28))),
                        ('roc_s2_0', list(range(0x10, 0x18))),
                        ('roc_s2_1', list(range(0x28, 0x30)))]
}

expected_roc_gpios = {
    'char_board': [
        ('roc_s0', ['hgcroc_rstB', 'resyncload', 'hgcroc_i2c_rstB'])
        ],
    'ld_hexaboard': [
        ('roc_s0', ['s0_resetn', 's0_resyncload', 's0_i2c_rstn']),
        ('roc_s1', ['s1_resetn', 's1_resyncload', 's1_i2c_rstn']),
        ('roc_s2', ['s2_resetn', 's2_resyncload', 's2_i2c_rstn'])
        ],
    'ld_hexaboard_v3': [
        ('roc_s0', ['s1_resetn', 'hard_resetn']),
        ('roc_s1', ['s2_resetn', 'hard_resetn']),
        ('roc_s2', ['s3_resetn', 'hard_resetn'])
        ],
    'hd_hexaboard': [
        ('roc_s0_0', ['s0_resetn', 's0_resyncload', 's0_i2c_rstn']),
        ('roc_s0_1', ['s1_resetn', 's1_resyncload', 's1_i2c_rstn']),
        ('roc_s1_0', ['s2_resetn', 's2_resyncload', 's2_i2c_rstn']),
        ('roc_s1_1', ['s3_resetn', 's3_resyncload', 's3_i2c_rstn']),
        ('roc_s2_0', ['s4_resetn', 's4_resyncload', 's4_i2c_rstn']),
        ('roc_s2_1', ['s5_resetn', 's5_resyncload', 's5_i2c_rstn'])
        ]
    }


def find_gpio_pins(board_type: str):
    """
    Attempt to find the GPIO pins that are associated with the rocs
    """
    all_lines = [(chip.label, line.name) for chip in gpiod.chip_iter()
                 for line in gpiod.line_iter(chip)]
    # check if line names are in char map
    gpio_pins = {}
    for (roc_name, pins) in expected_roc_gpios[board_type]:
        roc_connections = {}
        roc_connections['gpio'] = []

        for pin in pins:
            found_pin = False
            for (chip, line) in all_lines:
                if pin == line:
                    try:
                        roc_connections['gpio'].append(
                                {'chip': chip, 'line': line})
                    except KeyError:
                        roc_connections['gpio'] = \
                                [{'chip': chip, 'line': line}]
                    found_pin = True
                    break
            if not found_pin:
                raise IOError(f"The gpio pin {pin} does not exist but "
                              f"is needed for the control of roc {roc_name}")
        gpio_pins[roc_name] = roc_connections
    return gpio_pins


def find_links():
    """
    convenience function that performs the discovery of the rocs and boardtype.
    Also create the objects that will wrap the io
    """
    i2c_responses = gather_i2c_connections()
    board_type, roc_i2c_links = discover_roc_links(i2c_responses)
    pins = find_gpio_pins(board_type)
    board_description = dtu.update_dict(roc_i2c_links, pins)
    return board_type, board_description


def gather_i2c_connections():
    """
    Gather all responding peripherals on all available i2c busses
    """
    responding_addresses = []
    for bus_id in range(8):
        try:
            bus = SMBus()
            bus.open(bus_id)
            for address in range(128):  # 128 addrs per bus line
                try:
                    bus.read_byte(address)
                except OSError:
                    pass
                else:
                    responding_addresses.append((bus_id, address))
            bus.close()
        except FileNotFoundError:
            pass  # skip undefined i2c busses
    return responding_addresses


def discover_roc_links(responding_addresses):
    """
    Try and find the patterns in the collection of peripherals that indicate a
    ROC
    """
    # scan to find a the combination of i2c addresses that indicate a
    # board of different types rocs come as a sequence of 8
    # consecutive addresses
    busses_with_responses = set(map(lambda x: x[0], responding_addresses))
    possible_board_types = {}
    for btype, req_addrs in expected_roc_addresses.items():
        addr_block_found = []
        for roc_name, addr_block in req_addrs:
            for bus in busses_with_responses:
                addresses_with_response = \
                    list(map(lambda x: x[1],
                             filter(lambda x: x[0] == bus,
                                    responding_addresses)))
                start_address = min(addr_block)
                found_block = reduce(op.and_,
                                     [True if addr in addresses_with_response
                                      else False
                                      for addr in addr_block])
                if found_block:
                    addr_block_found.append(
                        {roc_name: {'bus_id': bus,
                         'start_address': start_address}})
                    break
        if len(addr_block_found) == len(req_addrs):
            possible_board_types[btype] = addr_block_found.copy()

    if 'char_board' in possible_board_types \
            and 'ld_hexaboard_v3' in possible_board_types:
        del possible_board_types['char_board']
    if 'ld_hexaboard_v3' in possible_board_types \
            and 'hd_hexaboard' in possible_board_types:
        del possible_board_types['ld_hexaboard_v3']
    try:
        board_type = list(possible_board_types.keys())[0]
    except IndexError as e:
        message = str(e.args[0])+" This error is likely a problem with the "\
                                 "firmware. Reload the firmware and try "\
                                 "again. If the problem persists, there may "\
                                 "be a deeper problem"
        raise IndexError(message)
    output_dict = {}
    rocs = possible_board_types[board_type]
    for roc in rocs:
        dtu.update_dict(output_dict, roc, in_place=True)
    return board_type, output_dict
