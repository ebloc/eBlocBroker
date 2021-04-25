#!/usr/bin/env python3

import eblocbroker.Contract as Contract
from utils import _colorize_traceback

Ebb = Contract.eblocbroker

if __name__ == "__main__":
    try:
        print(f"is_contract_exists={Ebb.is_contract_exists()}")
    except:
        _colorize_traceback()
        print("is_contract_exists=False")
