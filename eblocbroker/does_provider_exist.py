#!/usr/bin/env python3

import sys

if __name__ == "__main__":
    import eblocbroker.Contract as Contract

    Ebb = Contract.eblocbroker

    if len(sys.argv) == 2:
        provider_address = str(sys.argv[1])
        print(Ebb.does_provider_exist(provider_address))
    else:
        print("E: Please provide provider address as argument.")
