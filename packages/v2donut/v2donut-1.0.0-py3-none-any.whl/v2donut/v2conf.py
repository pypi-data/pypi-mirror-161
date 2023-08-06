from __future__ import annotations

import json
import os

from v2donut.appsettings import AppSettings
from v2donut.subscription import VmessShare


def gen_policy_settings():
    policy = {
        "levels": {"0": {"uplinkOnly": 0, "downlinkOnly": 0}},
        "system": {
            "statsInboundUplink": False,
            "statsInboundDownlink": False,
            "statsOutboundUplink": False,
            "statsOutboundDownlink": False,
        },
    }

    return policy


def gen_dns_settings():
    dns = {
        "hosts": {
            "domain:v2fly.org": "www.vicemc.net",
            "domain:github.io": "pages.github.com",
            "domain:wikipedia.org": "www.wikimedia.org",
            "domain:shadowsocks.org": "electronicsrealm.com",
            "geosite:category-ads": "127.0.0.1",
            "example.com": "1.2.3.4",
        },
        "servers": [
            "1.1.1.1",
            {"address": "114.114.114.114", "port": 53, "domains": ["geosite:cn"]},
            "8.8.8.8",
            "localhost",
        ],
    }

    return dns


def gen_routing_settings():
    routing = {
        "domainStrategy": "IPOnDemand",
        "rules": [
            {"type": "field", "ip": ["8.8.8.8", "1.1.1.1"], "outboundTag": "proxy"},
            {
                "type": "field",
                "domain": ["geosite:microsoft", "geosite:stackexchange", "geosite:google"],
                "outboundTag": "proxy",
            },
            {"type": "field", "ip": ["geoip:private"], "outboundTag": "blocked"},
            {"type": "field", "domain": ["geosite:category-ads"], "outboundTag": "blocked"},
        ],
    }

    return routing


def gen_inbounds_settings(settings: AppSettings):
    socks_inbound = {
        "port": settings.socks_port,
        "listen": "0.0.0.0",
        "tag": "socks-inbound",
        "protocol": "socks",
        "settings": {"auth": "noauth", "udp": True},
        "sniffing": {"enabled": True, "destOverride": ["http", "tls"]},
    }

    http_inbound = {
        "port": settings.http_port,
        "listen": "0.0.0.0",
        "tag": "http-inbound",
        "protocol": "http",
        "settings": {"auth": "noauth", "udp": True},
        "sniffing": {"enabled": True, "destOverride": ["http", "tls"]},
    }

    return [socks_inbound, http_inbound]


def gen_outbounds_settings(v: VmessShare):
    proxy_outbound = {
        "tag": "proxy",
        "protocol": "vmess",
        "settings": {
            "vnext": [
                {
                    "address": v.host,
                    "port": v.port,
                    "users": [
                        {
                            "id": v.id,
                            "alterId": v.aid,
                            "security": "auto",
                        }
                    ],
                }
            ],
        },
        "streamSettings": {
            "network": "ws",
            "security": "tls",
            "tlsSettings": {"allowInsecure": False, "serverName": v.host},
            "wsSettings": {"connectionReuse": True, "path": "/v2ray", "headers": {"Host": v.host}},
        },
        "mux": {"enabled": True, "concurrency": 8},
    }

    return [
        proxy_outbound,
        {"protocol": "freedom", "settings": {}, "tag": "direct"},
        {"protocol": "blackhole", "settings": {}, "tag": "blocked"},
    ]


def gen_v2conf(v: VmessShare, settings: AppSettings):
    if not os.path.exists(settings.v2conf):
        raise ValueError(f"指定的 V2Ray 配置文件不存在")

    v2conf = {
        "log": {"loglevel": "warning"},
        "policy": gen_policy_settings(),
        "dns": gen_dns_settings(),
        "routing": gen_routing_settings(),
        "inbounds": gen_inbounds_settings(settings),
        "outbounds": gen_outbounds_settings(v),
        "other": {},
    }

    with open(settings.v2conf, "w") as v2conf_file:
        json.dump(v2conf, v2conf_file, indent=4)
