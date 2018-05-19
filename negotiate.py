import socket
import sys
import logging

from ws_client import Telepathy

SPLOON_PORT_RECV = 49152
SPLOON_PORT_SEND = 49153
WOB_SOCK = 'ws://hello.buttslol.net:8765'

send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
send_sock.bind(('', SPLOON_PORT_SEND))

recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_sock.bind(('', SPLOON_PORT_RECV))


def rebroadcast(blob):
    send_sock.sendto(blob, ('192.168.0.255', SPLOON_PORT_RECV))


telepathy = Telepathy(WOB_SOCK, rebroadcast)

logging.getLogger().setLevel('DEBUG')

while True:
    data, addr = recv_sock.recvfrom(1024)
    telepathy.outboundBlobs.put_nowait(data)
    if not data.startswith(b'2\xab\x98d\x02\x00\x00\x00'):
        logging.warning(f'\nweird data from {addr}: {data}')
