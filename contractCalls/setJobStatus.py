#!/usr/bin/env python

import sys

def setJobStatus(jobKey, index, stateID, startTime, eBlocBroker=None, web3=None): #{
    if eBlocBroker == None and web3 == None: #{
        import os
        sys.path.insert(1, os.path.join(sys.path[0], '..'))
        from imports import connectEblocBroker
        from imports import getWeb3
        web3           = getWeb3()
        eBlocBroker    = connectEblocBroker(web3)
    #}
    import lib
    tx = eBlocBroker.transact({"from":web3.toChecksumAddress(lib.CLUSTER_ID), "gas": 4500000}).setJobStatus(jobKey, index, stateID, startTime) 
    return 'Tx: ' + tx.hex()
#}

if __name__ == '__main__': #{
    if len(sys.argv) == 5:
        jobKey    = str(sys.argv[1]) 
        index     = int(sys.argv[2]) 
        stateID   = int(sys.argv[3]) 
        startTime = int(sys.argv[4]) 

    print(setJobStatus(jobKey, index, stateID, startTime))
#}
