#!/usr/bin/env python

import os, json, sys, time
from web3 import Web3
from web3.providers.rpc import HTTPProvider
sys.path.insert(1, os.path.join(sys.path[0], '..')); import constants
os.chdir(sys.path[0]);

web3 = Web3(HTTPProvider('http://localhost:' + str(constants.RPC_PORT)))

fileAddr = open("address.json", "r")
contractAddress = fileAddr.read().replace("\n", "")

with open('abi.json', 'r') as abi_definition:
    abi = json.load(abi_definition)

contractAddress = web3.toChecksumAddress(contractAddress);
eBlocBroker = web3.eth.contract(contractAddress, abi=abi);

if __name__ == '__main__': #{
    if len(sys.argv) == 2:
        orcid = str(sys.argv[1]);
    else:
        orcid = "0000-0001-7642-0552";

    print(eBlocBroker.functions.isOrcIdVerified(orcid).call())
#}
