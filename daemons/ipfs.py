#!/usr/bin/env python3

import sys
from pathlib import Path

import daemon

import libs.ipfs as ipfs
from config import env
from utils import is_ipfs_on, log, popen_communicate


def run():
    # https://stackoverflow.com/a/8375012/2402577
    log("==> Running ipfs daemon")
    with daemon.DaemonContext():
        cmd = ["/usr/local/bin/ipfs", "daemon"]  # , "--mount"]
        _env = {"LIBP2P_FORCE_PNET": "1", "IPFS_PATH": f"{Path.home()}/.ipfs"}
        p, output, error = popen_communicate(cmd=cmd, stdout_file=env.IPFS_LOG, _env=_env)

    # ipfs mounted at: /ipfs
    # output = run(["sudo", "ipfs", "mount", "-f", "/ipfs"])
    # logging.info(output)
    #
    # for home and home2
    # ipfs swarm connect /ip4/192.168.1.3/tcp/4001/p2p/12D3KooWSE6pY7t5NxMLiGd4h7oba6XqxJFD2KNZTQFEjWLeHKsd


if __name__ == "__main__":
    try:
        env.IPFS_LOG
    except:
        log("E: env.IPFS_LOG is not set", color="red")
        sys.exit(1)

    if not is_ipfs_on():
        ipfs.remove_lock_files()
        run()
