import socket
import datetime
from json import encoder, decoder
import os

from config import Config
from ntp_packet import NTPPacket

LOCAL_IP = "127.0.0.2"
PORT = 12300
BUFFER_SIZE = 1024


def main(config: Config):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LOCAL_IP, PORT))

    print("FacelessNTP Server is now listening on port " + str(PORT))

    while True:
        message, addr = sock.recvfrom(BUFFER_SIZE)
        receive_time = datetime.datetime.now()

        ntp_pack = create_ntp_response(message, receive_time) \
            .set_transmit_timestamp(datetime.datetime.now()) \
            .offset(config.time_offset)

        sock.sendto(ntp_pack
                    .set_transmit_timestamp(datetime.datetime.now())
                    .get_bytes(),
                    addr)
        print("Responded to " + addr[0] + ":" + str(addr[1]))


def create_ntp_response(message, receive_time):
    pkt = NTPPacket().from_bytes(message)  # Client message
    resp = pkt.set_mode(4).set_receive_timestamp(receive_time)  # Server message
    return resp


def read_config() -> Config:
    if os.path.exists("config.json"):
        cfg_decoder = decoder.JSONDecoder()
        with open("config.json", 'rt') as f:
            cfg_dict = cfg_decoder.decode('\n'.join(f.readlines()))
            cfg = Config()
            for k in cfg_dict.keys():
                cfg.__dict__[k] = cfg_dict[k]
            return cfg
    else:
        cfg = Config()
        cfg_encoder = encoder.JSONEncoder()
        json = cfg_encoder.encode(cfg)
        with open("config.json", 'wt') as f:
            f.write(json)


if __name__ == "__main__":
    cfg = read_config()
    main(cfg)
