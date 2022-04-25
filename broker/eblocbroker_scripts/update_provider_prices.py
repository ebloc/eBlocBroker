#!/usr/bin/env python3

import sys

from broker import cfg
from broker._utils.tools import print_tb
from broker._utils.web3_tools import get_tx_status


def update_provider_prices(self, available_core, commitment_blk, prices):
    """Update provider prices."""
    if commitment_blk < cfg.ONE_HOUR_BLOCK_DURATION:
        raise Exception(f"Commitment block number should be greater than {cfg.ONE_HOUR_BLOCK_DURATION}")

    if not available_core:
        raise Exception("Please enter positive value for the available core number")

    if not commitment_blk:
        raise Exception("Please enter positive value for the commitment block number")

    try:
        tx = self._update_provider_prices(available_core, commitment_blk, prices)
        return self.tx_id(tx)
    except Exception as e:
        print_tb(e)
        raise e


if __name__ == "__main__":
    Ebb = cfg.Ebb
    available_core = 4
    commitment_blk = 600
    price_core_min = 100
    price_data_transfer = 1
    price_storage = 1
    price_cache = 1
    prices = [price_core_min, price_data_transfer, price_storage, price_cache]
    try:
        tx_hash = Ebb.update_provider_prices(available_core, commitment_blk, prices)
        receipt = get_tx_status(tx_hash)
    except Exception as e:
        print_tb(e)
        sys.exit(1)
