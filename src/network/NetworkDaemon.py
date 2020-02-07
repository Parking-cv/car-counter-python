from queue import Queue
from threading import Thread
from time import sleep


class NetworkDaemon(Thread):
    """
    Thread used to execute network actions separate from the main thread.
    Gets requests from concurrent queue shared by the network manager, and waits for
    successful send before moving to the next one. Places responses in a queue
    to be used by the main thread later

    Parameters:
        session: the pi's session with the server, configured in network manager
        requests: requests queue
        response: response queue

    Methods:
        run: overrides Thread.run(). Prepares a request from the queue and sends it using the
            current session
    """

    def __init__(self, session, requests: Queue, responses: Queue):
        Thread.__init__(self)
        self.daemon = True
        self.pendingRequests = requests
        self.responses = responses
        self.session = session

    def run(self):
        while True:
            # Blocks until an object is put in the queue
            req = self.pendingRequests.get()
            prep = req.prepare()
            sent = False

            # Try to send a message to the server, if the request isn't successful,
            # try again after 15 seconds.
            while not sent:
                try:
                    res = self.session.send(prep)
                    self.responses.put(res)
                    sent = True

                except ConnectionError:
                    sleep(15)
