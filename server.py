import socket
import datetime
import time
from json import encoder, decoder
import os

from ntp_packet import NTPPacket

LOCAL_IP = "127.0.0.2"
PORT = 123
SECONDARY_PORT = 12300
BUFFER_SIZE = 1024


def main(config: dict):
    used_port = PORT
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((LOCAL_IP, PORT))
    except PermissionError:
        print(f"Can't get permission to bind server to port {PORT}.")
        if input(f"Use secondary port {SECONDARY_PORT}? [Y/n]") in {"Y", "y"}:
            print(f"Using secondary port {SECONDARY_PORT}")
            used_port = SECONDARY_PORT
            sock.bind((LOCAL_IP, SECONDARY_PORT))
        else:
            exit(0)

    print("FacelessNTP Server is now listening on port " + str(used_port))

    try:
        while True:
            message, addr = sock.recvfrom(BUFFER_SIZE)
            receive_time = datetime.datetime.now()

            ntp_pack = create_ntp_response(message, receive_time) \
                .set_transmit_timestamp(datetime.datetime.now()) \
                .offset(config["time_offset"])

            sock.sendto(ntp_pack.set_transmit_timestamp(datetime.datetime.now())
                        .get_bytes(), addr)
            print("Responded to " + addr[0] + ":" + str(addr[1]))
    except KeyboardInterrupt:
        print("Stopping server")


def create_ntp_response(message, receive_time):
    pkt = NTPPacket().from_bytes(message)  # Client message
    resp = pkt.set_mode(4).set_receive_timestamp(receive_time)  # Server message
    return resp


def read_config() -> dict:
    if os.path.exists("config.json"):
        cfg_decoder = decoder.JSONDecoder()
        with open("config.json", 'rt') as f:
            return cfg_decoder.decode('\n'.join(f.readlines()))
    else:
        cfg = {"time_offset": 60}
        cfg_encoder = encoder.JSONEncoder()
        json = cfg_encoder.encode(cfg)
        with open("config.json", 'wt') as f:
            f.write(json)
            f.flush()
        return cfg


if __name__ == "__main__":
    cfg = read_config()
    main(cfg)
