I2C_SMBUS_BLOCK_MAX = 32


class mock_Xil_gpio():
    def __init__(self, chip, pin, mode):
        if mode not in ['input', 'output']:
            raise ValueError(
                    "the gpio 'mode' needs to be either 'input' or 'output'")
        self.mode = mode
        self.chip = chip
        self.pin = pin
        self.state = 0

    def write(self, val):
        if val not in [0, 1]:
            raise ValueError(
                    'A gpio can only be set "HIGH" => 1, or "LOW" => 0')
        if self.mode != 'output':
            raise ValueError(
                    'To set the output of the pin it needs to '
                    'be set as "output"')
        self.state = val

    def read(self):
        return self.state

    def __str__(self):
        return f"Pin {self.pin} of chip {self.chip}"


class MockSMBus():
    """
    Class to create an object that imitate an i2c connection
    """
    peripherals = []

    @classmethod
    def set_peripherals(cls, peripherals):
        MockSMBus.peripherals = peripherals

    def __init__(self):
        """
        Initialize the class, When doing so, specify the peripherals
        that are to appear on the bus
        """
        self.id = None
        self.bus = {}

    def open(self, id: int):
        self.id = id
        try:
            # The address of peripheral on the bus must be 0-127
            for address in range(127):
                self.bus[address] = 0
        except KeyError:
            pass

    def write_byte(self, address, byte):
        if self.id is not None:
            if address in self.bus:
                self.bus[address] = byte
            else:
                raise OSError("Input/output Error")
        else:
            raise TypeError("Argument must have a fileno method")

    def read_byte(self, address):
        if self.id is not None:
            try:
                return self.bus[address]
            except KeyError:
                raise OSError("Input/output Error")
        else:
            raise TypeError("Argument must have a fileno method")

    def write_i2c_block_data(self, address, offset, data):
        if self.id is not None:
            if address + offset in self.bus:
                self.bus[address + offset] = data[-1]
            else:
                raise OSError("Input/output Error")
        else:
            raise TypeError("Argument must have a fileno method")

    def read_i2c_block_data(self, address, offset, count):
        if self.id is not None:
            try:
                val = self.bus[address + offset]
                return [val for i in range(count)]
            except KeyError:
                raise OSError("Input/output Error")
        else:
            raise TypeError("Argument must have a fileno method")

    def close(self):
        self.id = None
