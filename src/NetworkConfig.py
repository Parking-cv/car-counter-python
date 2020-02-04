class NetworkConfig:
    def __init__(self, host, token, entryUrl, exitUrl, port=None):
        self.host = host
        self.token = token
        self.entryUrl = entryUrl
        self.exitUrl = exitUrl
        if port is not None:
            self.port = port
