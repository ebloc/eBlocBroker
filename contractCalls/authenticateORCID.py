#!/usr/bin/env python3

import sys

def authenticateORCID(userAddress, orcID, eBlocBroker=None, web3=None):
    if eBlocBroker is None and web3 is None:
        import os;
        sys.path.insert(1, os.path.join(sys.path[0], '..'))
        from imports import connectEblocBroker
        from imports import getWeb3
        web3        = getWeb3()
        eBlocBroker = connectEblocBroker(web3)
    
    account     = web3.eth.accounts[0]
    userAddress = web3.toChecksumAddress(userAddress)    
    if eBlocBroker.functions.isUserOrcIDVerified(userAddress).call() == 0 and len(orcID) == 19 and orcID.replace("-", "").isdigit():
        tx = eBlocBroker.transact({"from":account, "gas": 4500000}).authenticateOrcID(userAddress, orcID) 
        return('Tx_hash: ' + tx.hex()) 
    else:
        return('OrcID: ' + orcID + ' is already authenticated.')    
    
if __name__ == '__main__': 
    # USER Inputs----------------------------------------------------------------
    if len(sys.argv) == 3:
        userAddress = str(sys.argv[1]) 
        orcID = str(sys.argv[2]) 
    else:
        # userAddress = '0x4e4a0750350796164D8DefC442a712B7557BF282' # ebloc
        userAddress = '0x57b60037b82154ec7149142c606ba024fbb0f991' # netlab        
        orcID       = '0000-0001-7642-0552'
    # ----------------------------------------------------------------------------
    print(authenticateORCID(userAddress, orcID))
