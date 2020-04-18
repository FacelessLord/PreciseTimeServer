import datetime
import struct


def get_fraction(number, precision) -> int:
    return int((number - int(number)) * (2 ** precision))


CALENDAR_BEGINNING = datetime.datetime(1900, 1, 1)
REFERENCE = datetime.datetime.now()


class NTPPacket:
    _FORMAT = "!B B b b 2I 4s 8I"

    def __init__(self,
                 send_timestamp=datetime.datetime.now(),
                 version_number=2,
                 mode=4):
        """
        :param version_number:
        :param mode: 3 - client, 4 - server
        """
        # 59 or 61 seconds in last minute (2 bits)
        self.leap_indicator = 0
        # Version of protocol (3 bits)
        self.version_number = version_number
        # Mode of sender (3 bits)
        self.mode = mode
        # Interval between requests (1 byte)
        self.poll = 0
        self.precision = 0
        # Interval for the clock reach NTP server (4 bytes)
        self.root_delay = 0
        # Scatter the clock NTP-server (4 bytes)
        self.root_dispersion = 0
        # Indicator of clocks (4 bytes)
        self.ref_id = b"PPS\0"
        # Last update time on server (8 bytes)
        self.reference = (REFERENCE - CALENDAR_BEGINNING).total_seconds()
        if mode == 3:  # client
            # Time of sending packet from local machine (8 bytes)
            self.origin = (send_timestamp - CALENDAR_BEGINNING) \
                .total_seconds()
            # Time of sending answer from server (8 bytes)
            self.transmit = 0
            # The level of "layering" reading time (1 byte)
            self.stratum = 0  # Client don't know server NTP stratum
        elif mode == 4:  # server
            # Time of sending packet from local machine (8 bytes)
            self.transmit = (send_timestamp - CALENDAR_BEGINNING) \
                .total_seconds()
            # Time of sending answer from server (8 bytes)
            self.origin = 0
            # The level of "layering" reading time (1 byte)
            self.stratum = 1

        self.receive = 0

    def set_receive_timestamp(self, receive_timestamp: datetime.datetime):
        # Time of receipt on server (8 bytes)
        self.receive = (receive_timestamp - CALENDAR_BEGINNING).total_seconds()
        return self

    def set_transmit_timestamp(self, transmit_timestamp: datetime.datetime):
        # Time of receipt on server (8 bytes)
        self.transmit = (transmit_timestamp - CALENDAR_BEGINNING) \
            .total_seconds()
        return self

    def set_mode(self, mode: int):
        self.mode = mode
        return self

    def get_bytes(self):
        # "!B B b b 2I 4s 8I"
        print(self.ref_id[3])
        return struct.pack(NTPPacket._FORMAT,
                           (self.leap_indicator << 6) +
                           (self.version_number << 3) + self.mode,  # B
                           self.stratum,  # B
                           self.poll,  # b
                           self.precision,  # b
                           int(self.root_delay) + get_fraction(
                               self.root_delay, 16),  # I
                           int(self.root_dispersion) +
                           get_fraction(self.root_dispersion, 16),  # I
                           self.ref_id,
                           int(self.reference),
                           get_fraction(self.reference, 32),
                           int(self.origin),
                           get_fraction(self.origin, 32),
                           int(self.receive),
                           get_fraction(self.receive, 32),
                           int(self.transmit),
                           get_fraction(self.transmit, 32))

    def from_bytes(self, data: bytes):
        unpacked_data = struct.unpack(NTPPacket._FORMAT, data)

        self.leap_indicator = unpacked_data[0] >> 6  # 2 bits
        self.version_number = unpacked_data[0] >> 3 & 0b111  # 3 bits
        self.mode = unpacked_data[0] & 0b111  # 3 bits

        self.stratum = unpacked_data[1]  # 1 byte
        self.poll = unpacked_data[2]  # 1 byte
        self.precision = unpacked_data[3]  # 1 byte

        # 2 bytes - integer part | 2 bytes - fractional part
        self.root_delay = (unpacked_data[4] >> 16) + \
                          (unpacked_data[4] & 0xFFFF) / 2 ** 16
        # 2 bytes - integer part | 2 bytes - fractional part
        self.root_dispersion = (unpacked_data[5] >> 16) + \
                               (unpacked_data[5] & 0xFFFF) / 2 ** 16

        # 4 bytes
        self.ref_id = unpacked_data[6]

        # 8 bytes
        self.reference = unpacked_data[7] \
                         + unpacked_data[8] / 2 ** 32
        # 8 bytes
        self.origin = unpacked_data[9] \
                      + unpacked_data[10] / 2 ** 32
        # 8 bytes
        self.receive = unpacked_data[11] \
                       + unpacked_data[12] / 2 ** 32
        # 8 bytes
        self.transmit = unpacked_data[13] \
                        + unpacked_data[14] / 2 ** 32

        return self

    def copy(self, mode=3):
        return NTPPacket(mode=mode).from_bytes(self.get_bytes())

    def with_values(self, **kwargs):
        cp = self.copy()
        for k in kwargs.keys():
            cp.__dict__[k] = kwargs[k]
        return cp

    def set_values(self, **kwargs):
        for k in kwargs.keys():
            self.__dict__[k] = kwargs[k]
        return self

    def offset(self, seconds):
        self.reference += seconds
        self.receive += seconds
        self.transmit += seconds
        return self
