from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

from v2donut.appsettings import AppSettings
from v2donut.ping import ping
from v2donut.subscription import fetch
from v2donut.v2conf import gen_v2conf

conf_file = Path.home() / "v2donut.json"


def helpme():
    print("{:<16} {}".format("v2donut", "使用 Ping 测试延迟"))
    print("{:<16} {}".format("v2donut http", "使用 HTTP 测试延迟"))
    print("{:<16} {}".format("v2donut init", f"初始化程序配置, 配置文件路径: {conf_file}"))
    print("{:<16} {}".format("v2donut help", "获取帮助信息"))


def init_appsettings():
    if not os.path.exists(conf_file):
        shutil.copyfile(Path.cwd() / "v2donut.json", conf_file)


def main(mode: str):
    print(
        """
              .oooo.         .o8                                        .   
            .dP""Y88b       "888                                      .o8   
oooo    ooo       ]8P'  .oooo888   .ooooo.  ooo. .oo.   oooo  oooo  .o888oo 
 `88.  .8'      .d8P'  d88' `888  d88' `88b `888P"Y88b  `888  `888    888   
  `88..8'     .dP'     888   888  888   888  888   888   888   888    888   
   `888'    .oP     .o 888   888  888   888  888   888   888   888    888 . 
    `8'     8888888888 `Y8bod88P" `Y8bod8P' o888o o888o  `V88V"V8P'   "888" 
    """
    )

    with open(conf_file) as conf:
        j = json.load(conf)
        setting = AppSettings(**j)

    vs = fetch(setting.url)

    first = ping(vs, setting, mode)
    v = first[0]

    gen_v2conf(v, setting)

    print(f"最快的服务器是 {v.ps} [{v.host}], 时间={first[1]}ms")


def patched_main():
    args = sys.argv[1:]
    subcmd = "ping" if len(args) == 0 else args[0]

    if subcmd == "help":
        helpme()
    else:
        mode = subcmd
        init_appsettings()
        main(mode)
