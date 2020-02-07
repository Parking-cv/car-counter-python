import base64
import json
from collections import Generator
from datetime import datetime
from queue import Queue

import cv2
import numpy as np

from src import NetworkConfig
from src.network.NetworkDaemon import NetworkDaemon


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

    def uploadFrame(self, frame):
        self.pendingRequests.put({
            'method': 'POST',
            'url': 'http://localhost:3000' + self.config.urls['frame'],
            'headers': {
                'Authorization': 'Bearer ' + self.config.token
            },
            'data': None,
            'json': None,
            'files': {
                'media': frame
            }
        })

    def testNetwork(self):
        self.pendingRequests.put({
            'method': 'POST',
            'url': 'http://localhost:3000' + self.config.urls['test'],
            'headers': {
                'Authorization': 'Bearer ' + self.config.token
            },
            'data': None,
            'json': {
                'message': 'Hello, World!'
            },
            'files': None
        })

    def getResponse(self) -> dict:
        yield self.responses.get()

    def getResponses(self) -> Generator:
        while not self.responses.empty():
            yield self.responses.get()

    def terminate(self):
        self.daemon.join()
