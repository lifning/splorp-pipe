import socket
import sys
import logging

from ws_client import Telepathy

SPLOON_PORT = 49152
WOB_SOCK = 'ws://hello.buttslol.net:8765'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def rebroadcast(blob):
    sock.sendto(blob, ('192.168.0.255', SPLOON_PORT))


telepathy = Telepathy(WOB_SOCK, rebroadcast)

logging.getLogger().setLevel('DEBUG')

sock.bind(('', SPLOON_PORT))
while True:
    data, addr = sock.recvfrom(1024)
    telepathy.outboundBlobs.put_nowait(data)
    if not data.startswith(b'2\xab\x98d\x02\x00\x00\x00'):
        logging.warning(f'\nweird data from {addr}: {data}')
