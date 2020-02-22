from collections import Generator
from queue import Queue

import requests

from network.NetworkDaemon import NetworkDaemon


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
        terminate: join the daemon with the main thread before exiting
    """

    def __init__(self, uri: str, urls: dict):
        self.uri = uri
        self.urls = urls
        self.pendingRequests = Queue()
        self.responses = Queue()
        self.daemon = NetworkDaemon(requests.Session(), self.pendingRequests, self.responses)
                                        # TODO tls   ^
    def start(self):
        self.daemon.start()

    def uploadFrames(self, frames):
        self.pendingRequests.put(
            requests.Request(
                method='POST',
                url=self.uri + self.urls['frame'],
                files=frames,
            )
        )

    def getResponse(self) -> requests.Response:
        return self.responses.get()

    def getResponses(self) -> Generator:
        while not self.responses.empty():
            yield self.responses.get()

    def terminate(self):
        self.daemon.terminate()
