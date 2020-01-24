#!/usr/bin/env python3

import sys, time, os
import lib
from imports import getWeb3, connectEblocBroker

web3 = getWeb3()
eBlocBroker = connectEblocBroker(web3)


def processLog(log):
    print(log)
    print("-----------")
    print(log[0].args["index"])


if __name__ == "__main__":
    if len(sys.argv) == 2:
        tx_hash = str(sys.argv[1])
        event = "LogJob"
    else:
        tx_hash = "0xe7f0bdc249458d36105120cf1a0fa5036a9368c5fd13aa37448dae5993d92a33"
        event = "LogReceipt"

    receipt = web3.eth.getTransactionReceipt(tx_hash)
    if event == "LogJob":
        logs = eBlocBroker.events.LogJob().processReceipt(receipt)
        processLog(logs)

    if event == "LogReceipt":
        logs = eBlocBroker.events.LogReceipt().processReceipt(receipt)
        processLog(logs)
