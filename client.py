import socket
import datetime

import server
from ntp_packet import NTPPacket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto(NTPPacket(datetime.datetime.now(), mode=3).get_bytes(),
            (server.LOCAL_IP, server.PORT))
response = sock.recvfrom(server.BUFFER_SIZE)
print(response)
