#!/usr/bin/env python3

import os, sys,json, pprint
from lib     import EBLOCPATH
from dotenv  import load_dotenv
from imports import connectEblocBroker, getWeb3
from os.path import expanduser
from contractCalls.isProviderExists import isProviderExists

home = expanduser("~")
load_dotenv(os.path.join(home + '/.eBlocBroker/', '.env')) # Load .env from the given path
   
w3           = getWeb3()
eBlocBroker  = connectEblocBroker(w3)
PROVIDER_ID  = w3.toChecksumAddress(os.getenv('PROVIDER_ID'))

def registerProvider(availableCoreNum, email, federationCloudId, miniLockId, priceCoreMin, priceDataTransfer, priceStorage, priceCache, ipfsAddress, commitmentBlockNum):
    if not os.path.isfile(home + '/.eBlocBroker/whisperInfo.txt'):
        return False, 'Please first run: ../scripts/whisperInitialize.py'
    else:
        with open(home + '/.eBlocBroker/whisperInfo.txt') as json_file:
            data = json.load(json_file)
            kId = data['kId']
            whisperPubKey = data['publicKey']
            
        if not w3.geth.shh.hasKeyPair(kId):
            return False, "Whisper node's private key of a key pair did not match with the given ID.\nPlease re-run: " + EBLOCPATH + "/scripts/whisperInitialize.py"
    
    if isProviderExists(PROVIDER_ID):
        return False, 'Provider is already registered. Please call the updateProvider() function for an update.'
    
    if len(federationCloudId) < 128 and len(email) < 128 and (len(miniLockId) == 0 or len(miniLockId) == 45):
        try:
            tx = eBlocBroker.functions.registerProvider(email, federationCloudId, miniLockId, availableCoreNum, priceCoreMin, priceDataTransfer, priceStorage, priceCache, commitmentBlockNum, ipfsAddress, whisperPubKey).transact({"from":PROVIDER_ID, "gas": 4500000})
        except Exception:
            return False, traceback.format_exc()
        
        return True, tx.hex()

if __name__ == '__main__':
    availableCoreNum   = 128 
    email              = "alper01234alper@gmail.com" 
    federationCloudId  = "5f0db7e4-3078-4988-8fa5-f066984a8a97@b2drop.eudat.eu" 
    miniLockId         = "9VZyJy1gRFJfdDtAjRitqmjSxPjSAjBR6BxH59UeNgKzQ" 
    priceCoreMin       = 100
    priceDataTransfer  = 1
    priceStorage       = 1
    priceCache         = 1
    commitmentBlockNum = 10
    ipfsAddress        = "/ip4/79.123.177.145/tcp/4001/ipfs/QmWmZQnb8xh3gHf9ZFmVQC4mLEav3Uht5kHJxZtixG3rsf"

    status, result = registerProvider(availableCoreNum, email, federationCloudId, miniLockId, priceCoreMin, priceDataTransfer, priceStorage, priceCache, ipfsAddress, commitmentBlockNum)    
    if status:
        print('tx_hash=' + result)        
        receipt = w3.eth.waitForTransactionReceipt(result)
        print("Transaction receipt mined: \n")
        pprint.pprint(dict(receipt))
        print("Was transaction successful?")
        pprint.pprint(receipt['status'])        
    else:
        print(result)
