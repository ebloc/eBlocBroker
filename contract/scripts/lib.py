#!/usr/bin/env python3

import base58, binascii

class cacheType:
    private = 0
    public = 1
    none = 2
    ipfs = 3

class storageID:
    ipfs = 0
    eudat = 1
    ipfs_miniLock = 2
    github = 3
    gdrive = 4

Qm = b'\x12'

def convertIpfsToBytes32(hash_string):
    bytes_array = base58.b58decode(hash_string)
    b = bytes_array[2:]
    return binascii.hexlify(b).decode("utf-8")

def cost(coreArray, coreMinArray, account, eB, sourceCodeHash, web3, dataTransferIn, dataTransferOut, cacheTime, sourceCodeSize):
    clusterPriceInfo   = eB.getClusterInfo(account)
    blockReadFrom      = clusterPriceInfo[0]
    availableCoreNum   = clusterPriceInfo[1]
    priceCoreMin       = clusterPriceInfo[2]
    priceDataTransfer  = clusterPriceInfo[3]
    priceStorage       = clusterPriceInfo[4]
    priceCache         = clusterPriceInfo[5]
    commitmentBlockNum = clusterPriceInfo[6]
   
    assert len(coreArray) == len(coreMinArray)

    jobPriceValue     = 0
    computationalCost = 0
    cacheCost         = 0
    storageCost       = 0    
    _dataTransferIn   = 0
    
    for i in range(len(coreArray)):
        computationalCost += priceCoreMin * coreArray[i] * coreMinArray[i]                           
        
    # print(sourceCodeHash[0])
    for i in range(len(sourceCodeHash)):    
        jobReceivedBlocNumber, jobGasStorageHour = eB.getJobStorageTime(account, sourceCodeHash[i])
        if jobReceivedBlocNumber + jobGasStorageHour * 240 < web3.eth.blockNumber:
            _dataTransferIn += dataTransferIn[i]
            if cacheTime[i] > 0:
                storageCost += priceStorage * dataTransferIn[i] * cacheTime[i]
            else:
                cacheCost += priceCache * dataTransferIn[i]
                
    dataTransferCost = priceDataTransfer * (_dataTransferIn + dataTransferOut)
    jobPriceValue = computationalCost + dataTransferCost + cacheCost + storageCost
    
    print('\njobPriceValue=' + str(jobPriceValue)       + ' | ' +
          'cacheCost='         + str(cacheCost)         + ' | ' +
          'storageCost='       + str(storageCost)       + ' | ' +
          'dataTransferCost='  + str(dataTransferCost)  + ' | ' +
          'computationalCost=' + str(computationalCost))          

    return jobPriceValue
