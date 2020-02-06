import json
from collections import Generator

import numpy as np
from datetime import datetime
from queue import Queue

from src.network.NetworkDaemon import NetworkDaemon
from src import NetworkConfig
from src.network.Request import Request
from src.network.Response import Response


class NetworkManager(object):
    """
    Flyweight for interacting with the network daemon.

    Parameters
         networkConfig: object containing named properties used by the network connection

    Methods:
        start: start the network daemon
        sendFrame: send a video frame to the server for analysis
        getResponse: get the most recent response
        getResponses: get all responses from network requests as a generator
        terminate: call join on the network daemon before ending the program
    """

    def __init__(self, networkConfig: NetworkConfig):
        self.config = networkConfig
        self.pendingRequests = Queue()
        self.responses = Queue()
        self.daemon = NetworkDaemon(networkConfig, self.pendingRequests, self.responses)

    def start(self):
        self.daemon.start()

    def uploadFrame(self, frame: np.ndarray):
        if not frame.flags['C_CONTIGUOUS']:
            frame = np.ascontigousarray(frame)

        self.pendingRequests.put(
            Request(
                'POST',
                self.config.frameUrl,
                {
                    'timestamp': datetime.now().isoformat(),
                    'pi_id': 1,
                    'frame': frame.tobytes()
                },
            )
        )

    def testNetwork(self):
        self.pendingRequests.put(
            Request(
                'POST',
                '/test',
                {
                    'message': 'Hello, World!'
                }
            )
        )

    def getResponse(self) -> Response:
        yield self.responses.get()

    def getResponses(self) -> Generator:
        while not self.responses.empty():
            yield self.responses.get()

    def terminate(self):
        self.daemon.join()
