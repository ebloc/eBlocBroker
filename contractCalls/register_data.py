#!/usr/bin/env python3

import traceback

from imports import connect
from lib import get_tx_status

from settings import init_env

env = init_env()


def register_data(sourceCodeHash, price, commitmentBlockDuration):
    eBlocBroker, w3 = connect()
    if eBlocBroker is None or w3 is None:
        return

    try:
        tx = eBlocBroker.functions.registerData(sourceCodeHash, price, commitmentBlockDuration).transact(
            {"from": env.PROVIDER_ID, "gas": 100000}
        )

    except Exception:
        return False, traceback.format_exc()

    return True, tx.hex()


if __name__ == "__main__":
    sourceCodeHash = "0x68b8d8218e730fc2957bcb12119cb204"
    success, output = register_data(sourceCodeHash, 20, 240)

    if success:
        receipt = get_tx_status(success, output)
    else:
        print(output)
