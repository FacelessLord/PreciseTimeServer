import socket
import datetime

import server
from ntp_packet import NTPPacket, CALENDAR_BEGINNING

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto(NTPPacket(datetime.datetime.now(), mode=3).get_bytes(),
            (server.LOCAL_IP, server.PORT))
response = sock.recvfrom(server.BUFFER_SIZE)
arrive_timestamp = (
        datetime.datetime.now() - CALENDAR_BEGINNING).total_seconds()

if len(response[0]) <= 0:
    print("Server not responded")
    exit(1)

ntp_packet: NTPPacket = NTPPacket().from_bytes(response[0])
# time_delta = (Receive – Originate – Arrive + Transmit)/2
time_delta = (ntp_packet.receive - ntp_packet.origin
              - arrive_timestamp + ntp_packet.transmit) / 2
datetime_delta = datetime.timedelta(seconds=time_delta)
real_time = datetime.datetime.now() + datetime_delta

print("Now is " + str(real_time))
