#!/usr/bin/env python3

import eblocbroker.Contract as Contract

Ebb = Contract.eblocbroker

if __name__ == "__main__":
    print(Ebb.get_deployed_block_number())
