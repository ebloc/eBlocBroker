#!/usr/bin/env python3

import sys

from imports import connect_to_eblocbroker


def getJobSize(provider, key):
    eBlocBroker = connect_to_eblocbroker()
    return eBlocBroker.call().getJobSize(provider, key)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        provider = str(sys.argv[1])
        key = str(sys.argv[2])
    else:
        provider = "0x4e4a0750350796164d8defc442a712b7557bf282"
        key = "QmRsaBEGcqxQcJbBxCi1LN9iz5bDAGDWR6Hx7ZvWqgqmdR"

    print(getJobSize(provider, key))
