import socket
import datetime

from ntp_packet import NTPPacket

LOCAL_IP = "127.0.0.2"
PORT = 12300
BUFFER_SIZE = 1024


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LOCAL_IP, PORT))

    print("FacelessNTP Server is now listening on port " + str(PORT))

    while True:
        message, addr = sock.recvfrom(BUFFER_SIZE)
        receive_time = datetime.datetime.now()

        ntp_pack = create_ntp_response(message, receive_time)

        ntp_pack.set_transmit_timestamp(datetime.datetime.now())
        sock.sendto(ntp_pack
                    .set_transmit_timestamp(datetime.datetime.now())
                    .get_bytes(),
                    addr)
        print("Responded to " + addr)


def create_ntp_response(message, receive_time):
    pkt = NTPPacket().from_bytes(message)  # Client message
    resp = pkt.set_mode(4).set_receive_timestamp(receive_time)  # Server message
    return resp


if __name__ == "__main__":
    main()
