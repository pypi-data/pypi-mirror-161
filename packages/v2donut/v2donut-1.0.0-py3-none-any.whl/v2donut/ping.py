from __future__ import annotations

import pythonping

from v2donut.appsettings import AppSettings
from v2donut.subscription import VmessShare


def ping(vs: list[VmessShare], settings: AppSettings, mode="ping") -> tuple[VmessShare, float]:
    c: tuple[VmessShare, float] | None = None

    for v in vs:
        if not v.host or v.host.isspace():
            continue

        res = pythonping.ping(v.host, count=settings.count, timeout=settings.timeout)
        if not res.success():
            print(f"Ping {v.ps} [{v.host}], 时间=Timeout")
            continue

        ms = res.rtt_avg_ms
        print(f"Ping {v.ps} [{v.host}], 时间={ms}ms")

        if c is None or ms < c[1]:
            c = (v, ms)

    return c
