from __future__ import annotations


class AppSettings:
    def __init__(self, **params):
        self.url = params.get("url", "")
        self.v2conf = params.get("v2conf", "")
        self.v2program = params.get("v2program", "")
        self.count = params.get("count", 4)
        self.timeout = params.get("timeout", 0.8)
        self.socks_port = params.get("socks_port", 1080)
        self.http_port = params.get("http_port", 1081)
