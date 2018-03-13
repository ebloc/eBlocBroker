#!/usr/bin/env python -W ignore::DeprecationWarning

from __future__ import print_function
import os
from web3 import Web3
import json
from web3.providers.rpc import HTTPProvider
import sys

os.chdir(sys.path[0]);

def ipfsBytesToString(ipfsID):
    val= web3.fromAscii(ipfsID);
    os.environ['val'] = '1220'+val[2:];
    return os.popen('node bs58.js decode $val').read().replace("\n", "");
    
web3 = Web3(HTTPProvider('http://localhost:8545'))

fileAddr = open("address.json", "r")
contractAddress = fileAddr.read().replace("\n", "")

with open('abi.json', 'r') as abi_definition:
    abi = json.load(abi_definition)
    
eBlocBroker = web3.eth.contract(contractAddress, abi=abi);

# To test driverFunc.py executed as script.
if __name__ == '__main__': #{
    if(len(sys.argv) == 4):
        clusterAddress = str(sys.argv[1]);
        jobKey         = str(sys.argv[2]);
        index          = int(sys.argv[3]);
    else:
        clusterAddress = "0x6af0204187a93710317542d383a1b547fa42e705";
        jobKey         = "3d8e2dc2-b855-1036-807f-9dbd8c6b1579=267575587427153420186990249657380315186";
        index          = 5;
    
    print(eBlocBroker.call().getJobInfo(clusterAddress, jobKey, index));
#}
