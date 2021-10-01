#!/usr/bin/env python3

import sys

from broker.utils import print_tb

if __name__ == "__main__":
    import broker.eblocbroker.Contract as Contract

    Ebb: "Contract.Contract" = Contract.EBB()
    if len(sys.argv) == 2:
        requester = str(sys.argv[1])
    else:
        requester = "0x57b60037B82154eC7149142c606bA024fBb0f991"

    try:
        print(Ebb.is_orcid_verified(requester))
    except:
        print_tb()
