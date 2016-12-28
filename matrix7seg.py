class Matrix7seg:

    _NOOP = 0
    _DIGIT0 = 1
    _DIGIT1 = 2
    _DIGIT2 = 3
    _DIGIT3 = 4
    _DIGIT4 = 5
    _DIGIT5 = 6
    _DIGIT6 = 7
    _DIGIT7 = 8
    _DECODEMODE = 9
    _INTENSITY = 10
    _SCANLIMIT = 11
    _SHUTDOWN = 12
    _DISPLAYTEST = 15

    _DIGITS = {
        ' ': 0x00,
        '0': 0x7e,
        '1': 0x30,
        '2': 0x6d,
        '3': 0x79,
        '4': 0x33,
        '5': 0x5b,
        '6': 0x5f,
        '7': 0x70,
        '8': 0x7f,
        '9': 0x7b,
    }

    NUM_DIGITS = 8

    def __init__(self, spi, cs):
        self.spi = spi
        self.cs = cs
        self.buffer = bytearray(8)
        spi.init()
        self.init()

    def _register(self, command, data):
        # write to display
        self.cs.write_digital(0)
        self.spi.write(bytearray([command, data]))
        self.cs.write_digital(1)

    def init(self):
        for command, data in (
            (self._SHUTDOWN, 0),
            (self._DISPLAYTEST, 0),
            (self._SCANLIMIT, 7),
            (self._DECODEMODE, 0),
            (self._SHUTDOWN, 1),
        ):
            self._register(command, data)

    def write_number(self, value, zeroPad=False, leftJustify=False):
        # Take number, format it, look up characters then pass to buffer.

        if len(str(value)) > self.NUM_DIGITS:
            raise OverflowError('{0} too large for display'.format(value))

        size = self.NUM_DIGITS
        formatStr = '%'

        if zeroPad:
            formatStr += '0'

        if leftJustify:
            size *= -1

        formatStr = '{fmt}{size}i'.format(fmt=formatStr, size=size)
        position = self._DIGIT7
        strValue = formatStr % value

        # look up each digit's character
        # then send to buffer
        for char in strValue:
            self.buffer[position - 1] = self.letter(char)
            position -= 1

    def letter(self, char):
        # Look up character on digits table & return
        value = self._DIGITS.get(str(char))
        return value

    def show(self):
        for y in range(8):
            self._register(self._DIGIT0 + y, self.buffer[y])
