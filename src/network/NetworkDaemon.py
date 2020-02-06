from http.client import HTTPConnection
from threading import Thread
from time import sleep
from queue import Queue

from src import NetworkConfig
from src.network.Response import Response


class NetworkDaemon(Thread):
    """
    Thread used to execute network actions separate from the main (computer vision) thread.
    Gets requests from a concurrent queue shared by the network manager, and waits for
    successful send before moving to the next one

    Parameters:
        networkConfig: network configuration, contains hostname and JWT token

    Methods:
        run: overrides Thread.run(). Creates a connection to the server and reuses it for each network request.
            Loops forever, and sends requests whenever it receives one from the queue
    """

    def __init__(self, networkConfig: NetworkConfig, requests: Queue, responses: Queue):
        Thread.__init__(self)
        self.daemon = True
        self.pendingRequests = requests
        self.responses = responses
        self.headers = {'Authorization': 'Bearer ' + networkConfig.token}
        self.client = HTTPConnection(networkConfig.host, networkConfig.port)

    def run(self):
        self.client.connect()

        while True:
            # Blocks until an object is put in the queue
            request = self.pendingRequests.get()
            sent = False

            # Try to send a message to the server, if the request isn't successful,
            # try again after 1 second.
            while not sent:
                try:
                    self.client.request(
                        request.method,
                        request.url,
                        request.body,
                        self.headers
                    )

                    res = self.client.getresponse()

                    self.responses.put(
                        Response(res.status, res.getheaders(), res.read())
                    )

                    sent = True
                except ConnectionError:
                    sleep(15)
