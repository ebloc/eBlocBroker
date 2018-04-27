#!/usr/bin/env python

import os, json, sys, time
from web3 import Web3
from web3.providers.rpc import HTTPProvider
sys.path.insert(1, os.path.join(sys.path[0], '..')); import constants
os.chdir(sys.path[0]);

'''
def ipfsBytesToString(ipfsID):
    val= web3.fromAscii(ipfsID);
    os.environ['val'] = '1220'+val[2:];
    return os.popen('node bs58.js decode $val').read().replace("\n", "");
'''

web3 = Web3(HTTPProvider('http://localhost:' + str(constants.RPC_PORT)))

if not web3.isConnected():
    print('notconnected')
    sys.exit()

fileAddr = open("address.json", "r")
contractAddress = fileAddr.read().replace("\n", "")

with open('abi.json', 'r') as abi_definition:
    abi = json.load(abi_definition)

contractAddress = web3.toChecksumAddress(contractAddress);
eBlocBroker = web3.eth.contract(contractAddress, abi=abi);

if __name__ == '__main__': #{
    if(len(sys.argv) == 2):
        clusterAddress = str(sys.argv[1]);
    else:
        clusterAddress = "0x6af0204187a93710317542d383a1b547fa42e705";

    clusterAddress = web3.toChecksumAddress(clusterAddress);
    
    if (str(eBlocBroker.functions.isClusterExist(clusterAddress).call()) == "False"):
        print("Cluster is not registered. Please try again with registered Ethereum Address as cluster.")
        sys.exit();

    blockReadFrom, coreNumber, coreMinutePrice = eBlocBroker.functions.getClusterInfo(clusterAddress).call();
    my_filter = eBlocBroker.eventFilter('LogCluster',{'fromBlock': int(blockReadFrom),'toBlock': int(blockReadFrom) + 1})
           
    print('{0: <17}'.format('blockReadFrom: ')   + str(blockReadFrom));
    print('{0: <17}'.format('coreNumber: ')      + str(coreNumber));
    print('{0: <17}'.format('coreMinutePrice: ') + str(coreMinutePrice));
    print('{0: <17}'.format('clusterEmail: ')    + my_filter.get_all_entries()[0].args['clusterEmail']);
    print('{0: <17}'.format('miniLockID: ')      + my_filter.get_all_entries()[0].args['miniLockID']);
    print('{0: <17}'.format('ipfsAddress: ')     + my_filter.get_all_entries()[0].args['ipfsAddress']);   
    print('{0: <17}'.format('fID: ')             + my_filter.get_all_entries()[0].args['fID']);
    print('.');
#}
