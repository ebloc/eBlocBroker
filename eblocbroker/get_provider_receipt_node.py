#!/usr/bin/env python3

import sys

if __name__ == "__main__":
    import eblocbroker.Contract as Contract

    ebb = Contract.eblocbroker

    if len(sys.argv) == 2:
        provider_address = str(sys.argv[1])
        print(ebb.does_provider_exist(provider_address))
    else:
        provider_address = "0x4e4a0750350796164d8defc442a712b7557bf282"
        index = 0

    print(ebb.get_provider_receipt_node(provider_address, index))
