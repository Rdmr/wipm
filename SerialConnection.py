#class from pymite0.9/src/tools/ipm.py

ESCAPE_CHAR = '\x1B'
REPLY_TERMINATOR = '\x04'

class SerialConnection:
    """Provides ipm-host to target connection over a serial device.
    This connection should work on any platform that PySerial supports.
    The ipm-device must be running at the same baud rate (19200 default).
    """

    def __init__(self, serdev="/dev/ttyUSB0", baud=19200):
        try:
            import serial
        except Exception, e:
            print NEED_PYSERIAL
            raise e

        self.s = serial.Serial(serdev, baud)
        self.s.setTimeout(4)

    def read(self,):
        """Yields each character as it arrives, observing the escape character.
        """
        b = bytearray()
        c = None
        while True:
            c = self.s.read(1)
            # If it's an escape character, get the next char
            if c == ESCAPE_CHAR:
                c = self.s.read(1)
                if c == '':
                    return
                yield c
                continue

            if len(c) == 0 or c == REPLY_TERMINATOR:
                return
            yield c
        return

    def write(self, msg):
        self.s.write(msg)
        self.s.flush()

    def close(self,):
        self.s.close()
