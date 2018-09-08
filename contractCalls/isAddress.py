#!/usr/bin/env python

import sys

def isAddress(clusterAddress, web3=None): #{
    if web3 == None: #{
        import os
        sys.path.insert(1, os.path.join(sys.path[0], '..'))
        from imports import getWeb3
        web3 = getWeb3()

    #}    
    return web3.isAddress('0x4e4a0750350796164D8DefC442a712B7557BF282')
#}

if __name__ == '__main__': #{
    if len(sys.argv) == 2:
        clusterAddress = str(sys.argv[1]) 
    else:        
        clusterAddress = "0x4e4a0750350796164D8DefC442a712B7557BF282"  #POA
    print(isAddress(clusterAddress))
#}

