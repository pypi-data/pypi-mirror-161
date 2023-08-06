from __future__ import annotations

import base64
import json
from pathlib import Path

import httpx

vmess_protocol = "vmess"


class VmessShare:
    def __init__(self, **params):
        self.host = params.get("host", "")
        self.path = params.get("path", "")
        self.tls = params.get("tls", "")
        self.verify_cert = params.get("verify_cert", False)
        self.add = params.get("add", "")
        self.port = params.get("port", "")
        self.aid = params.get("aid", "")
        self.net = params.get("net", "")
        self.type = params.get("type", "")
        self.v = params.get("v", "")
        self.ps = params.get("ps", "")
        self.id = params.get("id", "")
        self.cls = params.get("class", "")


def fetch(url: str) -> list[VmessShare]:
    if not url:
        raise ValueError(f"请设置订阅地址, 配置文件: {Path.home() / 'v2donut.json'}")

    vs: list[VmessShare] = []

    res = httpx.get(url)
    if res.status_code != 200:
        return vs

    content = base64.b64decode(res.read())
    vmess = [v.decode("utf-8") for v in content.split()]
    for v in vmess:
        vmess_prefix = vmess_protocol + "://"

        if not v.startswith(vmess_prefix):
            continue

        j = base64.b64decode(v.removeprefix(vmess_prefix))
        json_object = json.loads(j)
        vs.append(VmessShare(**json_object))

    return vs
