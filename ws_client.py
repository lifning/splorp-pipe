import asyncio
import logging
import queue
import threading
import websockets


class Telepathy:
    # inboundMemoryWrites = queue.Queue()
    outboundBlobs = queue.Queue()

    def __init__(self, server, inbound_cb):
        self.server = server
        self.inbound_cb = inbound_cb
        thread = threading.Thread(target=self.threadMain, args=())
        thread.daemon = True
        thread.start()

    def threadMain(self):
        loop = asyncio.new_event_loop()
        loop.create_task(self.handleSocket())
        loop.run_forever()

    async def handleSocket(self):
        async with websockets.connect(self.server) as websocket:
            logging.info("connected to websocket")
            consumerTask = asyncio.ensure_future(self.messageConsumer(websocket))
            producerTask = asyncio.ensure_future(self.messageProducer(websocket))
            done, pending = await asyncio.wait(
                    [consumerTask, producerTask],
                    return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()

    async def messageConsumer(self, websocket):
        while True:
            data = await websocket.recv()
            logging.debug("received data: {}".format(data))
            # self.inboundMemoryWrites.put_nowait(data)
            self.inbound_cb(data)

    async def messageProducer(self, websocket):
        while True:
            try:
                message = await asyncio.get_event_loop().run_in_executor(None, self.bgThreadGetOutboundMemoryReads)
                # logging.debug("sending a message: {}".format(message))
                await websocket.send(message)
            except queue.Empty:
                pass

    def bgThreadGetOutboundMemoryReads(self):
        timeoutSeconds = 3 # wait at most this many seconds, then call .get again
        # if we do not timeout here then the app will hang indefinitely when interrupted.
        return self.outboundBlobs.get(block=True, timeout=timeoutSeconds)
