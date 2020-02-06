import json


class Request:
    def __init__(self, method: str, url: str, body: dict):
        self.method = method
        self.url = url
        self.body = json.dumps(body)
