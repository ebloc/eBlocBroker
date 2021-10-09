#!/usr/bin/env python3

import sys

import broker.cfg as cfg
from broker.utils import print_tb

if __name__ == "__main__":
    Ebb = cfg.Ebb
    if len(sys.argv) == 5:
        key = str(sys.argv[1])
        index = int(sys.argv[2])
        job_id = int(sys.argv[3])
        start_time = int(sys.argv[4])
    else:
        print("Please required related arguments {_key, index, start_time}")
        sys.exit(1)

    try:
        tx_hash = Ebb.set_job_status_running(key, index, job_id, start_time)
        print(f"tx_hash={tx_hash}")
    except Exception as e:
        print_tb(e)
        sys.exit(1)
