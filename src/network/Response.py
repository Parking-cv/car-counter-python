import json


class Response:
    def __init__(self, status: int, headers: dict, body: str):
        self.status = status
        self.headers = headers
        self.body = body
