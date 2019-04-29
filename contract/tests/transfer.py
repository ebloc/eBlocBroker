#!/usr/bin/python3

from brownie import *
import os, time
import scripts.token, scripts.lib

def setup():
    scripts.token.main()
    global eB, whisperPubKey, cwd
    eB = eBlocBroker[0]
    whisperPubKey = "0x04aec8867369cd4b38ce7c212a6de9b3aceac4303d05e54d0da5991194c1e28d36361e4859b64eaad1f95951d2168e53d46f3620b1d4d2913dbf306437c62683a6"
    cwd           = os.getcwd()
            
def getOwner(skip=True):
    '''Get Owner'''
    assert eB.getOwner() == accounts[0]
    
def registerCluster(printFlag=True):
    '''Register Cluster'''
    priceCoreMin      = 1
    priceDataTransfer = 1
    priceStorage      = 1
    priceCache        = 1
    web3.eth.defaultAccount = accounts[0]

    tx = eB.registerCluster("cluster@gmail.com",
                                "ee14ea28-b869-1036-8080-9dbd8c6b1579@b2drop.eudat.eu",
                                "9VZyJy1gRFJfdDtAjRitqmjSxPjSAjBR6BxH59UeNgKzQ",
                                128,
                                priceCoreMin,
                                priceDataTransfer,
                                priceStorage,
                                priceCache,
                                "/ip4/79.123.177.145/tcp/4001/ipfs/QmWmZQnb8xh3gHf9ZFmVQC4mLEav3Uht5kHJxZtixG3rsf",
                                whisperPubKey, {'from': accounts[0]})
    if printFlag:
        print(' => GasUsed:' + str(tx.__dict__['gas_used']))       

def registerUser(printFlag=True):
    '''Register User'''
    tx     = eB.registerUser("email@gmail.com",
                             "ee14ea28-b869-1036-8080-9dbd8c6b1579@b2drop.eudat.eu",
                             "9VZyJy1gRFJfdDtAjRitqmjSxPjSAjBR6BxH59UeNgKzQ",
                             "/ip4/79.123.177.145/tcp/4001/ipfs/QmWmZQnb8xh3gHf9ZFmVQC4mLEav3Uht5kHJxZtixG3rsf",
                             'ebloc',
                             whisperPubKey, {'from': accounts[1]})
    if printFlag:
        print(' => GasUsed:' + str(tx.__dict__['gas_used']))
    
    blockReadFrom, b = eB.getUserInfo(accounts[1])

    tx = eB.authenticateOrcID(accounts[1], '0000-0001-7642-0552', {'from': accounts[0]}) # ORCID should be registered.
    print('authenticateOrcID => GasUsed:' + str(tx.__dict__['gas_used']))    
    assert eB.isUserOrcIDVerified(accounts[1]), "isUserOrcIDVerified is failed"
    

def workFlow():
    registerCluster(False)
    registerUser(False)                    
    clusterAddress = accounts[0]
    userAddress = accounts[1]    

    jobKey = "QmWmyoMoctfbAaiEs2G46gpeUmhqFRDW6KWo64y5r581Vd"
    ipfsBytes32 = scripts.lib.convertIpfsToBytes32(jobKey)
    sourceCodeHash = web3.toBytes(hexstr= ipfsBytes32)

    dataTransferIn  = 100
    dataTransferOut = 100
    gasStorageHour  = 1
    
    coreArray       = [2, 4]
    gasCoreMinArray = [10, 20]
    workFlowJobID = 0
    storageID_cacheType = [scripts.lib.storageID.ipfs, scripts.lib.cacheType.private]
    dataTransfer = [dataTransferIn, dataTransferOut]

    jobPriceValue = scripts.lib.cost(coreArray, gasCoreMinArray, clusterAddress,
                                     eB, sourceCodeHash, web3,
                                     dataTransferIn, dataTransferOut, gasStorageHour)
    print('jobPriceValue: ' + str(jobPriceValue))

    tx = eB.submitJob(clusterAddress,
                      jobKey,
                      coreArray,
                      gasCoreMinArray,
                      dataTransfer,
                      storageID_cacheType,
                      gasStorageHour,
                      sourceCodeHash,
                      {"from": userAddress, "value": web3.toWei(jobPriceValue, "wei")})
    print('submitJob => GasUsed:' + str(tx.__dict__['gas_used']))

def submitJob():
# def submitJob(skip=True):    
    registerCluster(False)
    registerUser(False)                    
    clusterAddress = accounts[0]
    userAddress = accounts[1]    
    
    print(cwd)
    fname = cwd + '/files/test.txt'
    # fname = cwd + '/files/test_.txt'
    
    blockReadFrom, coreLimit, priceCoreMin, priceDataTransfer, priceStorage, priceCache = eB.getClusterInfo(accounts[0])
    print("Cluster's coreLimit:  "    + str(coreLimit))
    print("Cluster's priceCoreMin:  " + str(priceCoreMin))

    index = 0
    with open(fname) as f: 
        for line in f:
            arguments = line.rstrip('\n').split(" ")

            gasCoreMin     = int(arguments[1]) - int(arguments[0])
            dataTransferIn  = 100
            dataTransferOut = 100
            gasStorageHour  = 1
            core            = int(arguments[2])

            # time.sleep(1)
            # rpc.mine(int(arguments[0]))
            
            jobKey = "QmWmyoMoctfbAaiEs2G46gpeUmhqFRDW6KWo64y5r581Vd"
            ipfsBytes32 = scripts.lib.convertIpfsToBytes32(jobKey)
            sourceCodeHash = web3.toBytes(hexstr= ipfsBytes32)
            # print(sourceCodeHash)
            # sourceCodeHash = "e3fbef873405145274256ee0ee2b580f"
            miniLockId     = "jj2Fn8St9tzLeErBiXA6oiZatnDwJ2YrnLY3Uyn4msD8k"
 
			# print("Client Balance before: " + str(web3.eth.getBalance(account)))
			# print("Contract Balance before: " + str(web3.eth.getBalance(accounts[0])))

            coreArray       = [core]            
            gasCoreMinArray = [gasCoreMin]

            jobPriceValue = scripts.lib.cost(coreArray, gasCoreMinArray, clusterAddress, eB, sourceCodeHash, web3, dataTransferIn, dataTransferOut, gasStorageHour)
            print('jobPriceValue: ' + str(jobPriceValue))
            storageID_cacheType = [scripts.lib.storageID.ipfs, scripts.lib.cacheType.private]
            dataTransfer = [dataTransferIn, dataTransferOut]
            
            tx = eB.submitJob(clusterAddress,
                              jobKey,
                              coreArray,
                              gasCoreMinArray,
                              dataTransfer,
                              storageID_cacheType,
                              gasStorageHour,
                              sourceCodeHash,
                              {"from": userAddress, "value": web3.toWei(jobPriceValue, "wei")})
            print('submitJob => GasUsed:' + str(tx.__dict__['gas_used']))
    
			# print("Contract Balance after: " + str(web3.eth.getBalance(accounts[0])))
			# print("Client Balance after: " + str(web3.eth.getBalance(accounts[8])))				
            # sys.stdout.write('jobInfo: ')
            # sys.stdout.flush()

            print(eB.getJobInfo(clusterAddress, jobKey, index))
            index += 1

    print('----------------------------------')
    print(blockReadFrom)
    rpc.mine(100)
    print(web3.eth.blockNumber)

    index = 0
    with open(fname) as f: 
        for line in f: 
            arguments = line.rstrip('\n').split(" ")
            tx = eB.setJobStatus(jobKey, index, 4, int(arguments[0]), {"from": accounts[0]})
            index += 1

    print('----------------------------------')
    ipfsBytes32    = scripts.lib.convertIpfsToBytes32("QmWmyoMoctfbAaiEs2G46gpeUmhqFRDW6KWo64y5r581Ve")
    resultIpfsHash = web3.toBytes(hexstr= ipfsBytes32)
    
    index = 0
    receivedAmount_temp = 0
    with open(fname) as f: 
        for line in f: 
            arguments = line.rstrip('\n').split(" ")
            dataTransferIn  = 0
            dataTransferOut = 100

            dataTransfer = [0, 100]
            workFlowJobID = 0
            tx = eB.receiptCheck(jobKey, index,
                            int(arguments[1]) - int(arguments[0]),
                            resultIpfsHash,
                            0,
                            int(arguments[1]),
                            workFlowJobID,
                            dataTransfer,
                            {"from": accounts[0]})
            print('receiptCheck => GasUsed:' + str(tx.__dict__['gas_used']))
            
            receivedAmount = eB.getClusterReceivedAmount(clusterAddress)            
            print('Cluster Receeived Amount: ' + str(receivedAmount - receivedAmount_temp))
            receivedAmount_temp = receivedAmount
            index += 1

    # Prints finalize version of the linked list.
    size = eB.getClusterReceiptSize(clusterAddress)
    for i in range(0, size):
        print(eB.getClusterReceiptNode(clusterAddress, i))

    print('----------------------------------')
    print('StorageTime for job: ' + jobKey)
    
    print(eB.getJobStorageTime(clusterAddress, sourceCodeHash))
    print('----------------------------------')
    print(eB.getReceiveStoragePayment(userAddress, sourceCodeHash, {"from": clusterAddress}))
    
    tx = eB.receiveStoragePayment(userAddress, sourceCodeHash, {"from": clusterAddress});
    print('receiveStoragePayment => GasUsed:' + str(tx.__dict__['gas_used']))
            
    print(eB.getReceiveStoragePayment(userAddress, sourceCodeHash, {"from": clusterAddress}))
    print('----------------------------------')


    