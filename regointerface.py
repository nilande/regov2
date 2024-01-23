import serial
from functools import reduce
from binascii import hexlify

class RegoInterface:
    # Constructor
    def __init__(self, port='/dev/ttyACM0', baudrate=19200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=2):
        self.ser = serial.Serial(port=port, baudrate=baudrate, parity=parity, stopbits=stopbits, bytesize=bytesize, timeout=timeout)
        self.ser.flushInput()
        self.ser.flushOutput()

    # Encode 2x 8-bit bytes into 3x 7-bit bytes
    def _encode(self, b):
        val = int.from_bytes(b, "big")
        return bytes([val>>14 & 0x7f, val>>7 & 0x7f, val & 0x7f])

    # Decode 3x 7-bit bytes into 2x 8-bit bytes
    def _decode(self, b):
        val = b[0] << 14 | b[1] << 7 | b[2]
        return val.to_bytes(2, "big")

    # Calculate an XOR checksum over a series of bytes
    def _checksum(self, b):
        return bytes([reduce(lambda x,y:x^y, b)])

    # Build a command package
    def _build_packet(self, device, cmd, reg, data):
        pkt = device + cmd + self._encode(reg) + self._encode(data)
        pkt = pkt + self._checksum(pkt[2:8])
        return pkt

    def _decode_int_packet(self, pkt):
        if len(pkt) != 5:
            return None
        if self._checksum(pkt[1:4])[0] != pkt[4]:
            return None
        return int.from_bytes(self._decode(pkt[1:4]), "big", signed=True)

    # Query register
    def query_register(self, reg):
        request = self._build_packet(b'\x81', b'\x02', reg, bytes(2))

        self.ser.write(request)
        response = self.ser.read(5)

        return self._decode_int_packet(response)
