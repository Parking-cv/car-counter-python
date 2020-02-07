class NetworkConfig:
    def __init__(self, host, token, urls, port=None):
        self.host = host
        self.token = token
        self.urls = urls
        if port is not None:
            self.port = port
