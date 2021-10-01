#!/usr/bin/env python3

import sys

import broker.eblocbroker.Contract as Contract
from broker._utils.tools import log
from broker.config import env, setup_logger
from broker.utils import print_tb

logging = setup_logger()


if __name__ == "__main__":
    Ebb: "Contract.Contract" = Contract.EBB()
    is_write_to_file = False
    if len(sys.argv) == 2:
        if sys.argv[1] in ("1", "True", "true"):
            is_write_to_file = True

    try:
        output = Ebb.get_block_number()
        if is_write_to_file:
            env.config["block_continue"] = output
        else:
            log(f"block_number={output}")
    except Exception:
        print_tb()

    sys.exit(0)
