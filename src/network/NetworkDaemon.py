import json
from http.client import HTTPConnection
import requests
from queue import Queue
from threading import Thread
from time import sleep

from src import NetworkConfig


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
        self.client = HTTPConnection(networkConfig.host, networkConfig.port)

    def run(self):
        self.client.connect()

        while True:
            # Blocks until an object is put in the queue
            request = self.pendingRequests.get()
            sent = False

            # Try to send a message to the server, if the request isn't successful,
            # try again after 15 seconds.
            while not sent:
                try:
                    res = requests.request(
                        request['method'],
                        request['url'],
                        headers=request['headers'],
                        data=request['data'],
                        json=request['json'],
                        files=request['files'],
                    )

                    self.responses.put({
                        'status': res.status_code,
                        'headers': res.headers,
                        'body': res.json()
                    })

                    sent = True
                except ConnectionError:
                    sleep(15)
