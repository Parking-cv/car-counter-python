from datetime import datetime
from queue import Queue

from src.network.NetworkDaemon import NetworkDaemon


class NetworkManager(object):
    """
    Flyweight for interacting with the network daemon.

    Parameters
         networkConfig: object containing named properties used by the network connection

    Methods:
        start: start the network daemon
        notifyEntry: put a request in the pending requests queue notifying the server of an entry event
        notifyExit: put a request in the pending requests queue notifying the server of an exit event
        getResponses: get all responses from network requests as a generator
        terminate: call join on the network daemon before ending the program
    """

    def __init__(self, networkConfig):
        self.config = networkConfig
        self.pendingRequests = Queue()
        self.responses = Queue()
        self.daemon = NetworkDaemon(networkConfig, self.pendingRequests, self.responses)

    def start(self):
        self.daemon.start()

    def notifyEntry(self):
        self.pendingRequests.put(
            {
                'method': 'POST',
                'url': self.config.entryUrl,
                'body':
                    {
                        'timestamp': datetime.now().isoformat()
                    }
            }
        )

    def notifyExit(self):
        self.pendingRequests.put(
            {
                'method': 'POST',
                'url': self.config.exitUrl,
                'body': {
                    'timestamp': datetime.now().isoformat()
                }
            }
        )

    def getResponse(self):
        yield self.responses.get()

    def getResponses(self):
        while not self.responses.empty():
            yield self.responses.get()

    def terminate(self):
        self.daemon.join()
