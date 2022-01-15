#!/usr/bin/env python3

import sys

import daemon

from broker import cfg
from broker._utils.tools import print_tb
from broker.config import env
from broker.utils import is_ganache_on, is_npm_installed, log, popen_communicate


def run(port=8547, hardfork_name="istanbul"):
    """Run ganache daemon on the background.

    https://stackoverflow.com/a/8375012/2402577
    """
    print(f"## Running Ganache CLI on port={port}")
    with daemon.DaemonContext():
        cmd = [
            "ganache-cli",
            "--port",
            port,
            "--hardfork",
            hardfork_name,
            "--gasLimit",
            "6721975",
            "--accounts",
            "10",
            # "--blockTime",
            # cfg.BLOCK_DURATION,
            "--allowUnlimitedContractSize",
        ]
        popen_communicate(cmd, env.GANACHE_LOG)


if __name__ == "__main__":
    port = 8547
    if len(sys.argv) == 2:
        port = int(sys.argv[1])

    # try:
    #     npm_package = "ganache-cli"
    #     if not is_npm_installed(npm_package):
    #         log(f"E: {npm_package} is not installed within npm")
    #         sys.exit()
    # except Exception as e:
    #     print_tb(e)

    if not is_ganache_on(port):
        run(port)
