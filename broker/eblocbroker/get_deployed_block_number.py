#!/usr/bin/env python3

import broker.eblocbroker.Contract as Contract

Ebb: "Contract.Contract" = Contract.EBB()

if __name__ == "__main__":
    print(Ebb.get_deployed_block_number())
