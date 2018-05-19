#!/usr/bin/env python

import asyncio
import threading
import time
import signal
import sys
import logging
import websockets

clients = set()


async def handleClient(websocket, path):
    clients.add(websocket)

    try:
        while True:
            message = await websocket.recv()
            logging.debug("< {}".format(message))

            await broadcastMessage(websocket, message)
            logging.debug("sent {}".format(message))
    finally:
        clients.remove(websocket)


async def broadcastMessage(origin, message):
    destinations = clients - {origin}
    messagesSent = 0
    for dest in destinations:
        await dest.send(message)
        messagesSent = messagesSent + 1
    logging.debug("Sent message {} times: {}".format(messagesSent, message))


def websocketServer():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(handleClient, '0.0.0.0', 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


thread = threading.Thread(target=websocketServer, args=())
thread.daemon = True
thread.start()


def signal_handler(signal, frame):
    logging.info("\nStopping server.")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

while True:
    time.sleep(20)
