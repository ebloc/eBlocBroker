import binascii, base58

Qm = b'\x12 '

def convertBytes32Ipfs(bytes_array):
    bytes_init = base58.b58decode("Qm")    
    merge = Qm + bytes_array
    return base58.b58encode(merge).decode("utf-8")
    
    
def convertIpfsBytes32(hash_string):           
    bytes_array = base58.b58decode(hash_string)    
    b = bytes_array[2:]
    return binascii.hexlify(b).decode("utf-8")

def IPFS_chech(greeter, chain, web3):
    ipfsHash = "QmWmyoMoctfbAaiEs2G46gpeUmhqFRDW6KWo64y5r581Vz"
    hex_str = convertIpfsBytes32(ipfsHash) # "7d5a99f603f231d53a4f39d1521f98d2e8bb279cf29bebfd0687dc98458e7f89";  
    data    = web3.toBytes(hexstr= hex_str)    
    set_txn_hash = greeter.transact().setGreeting(data)        
    contract_address = chain.wait.for_receipt(set_txn_hash)
    print('setGreeting_' + 'gasUsed=' + str(contract_address["gasUsed"]))
    
    ret = greeter.call().greet()   
    ret = ret.encode('latin-1')    
    ipfsHashRet = convertBytes32Ipfs(ret)
    assert ipfsHash == ipfsHashRet   

def test_custom_greeting(web3, chain):
    print('\n')
    greeter, _ = chain.provider.get_or_deploy_contract('Greeter')   
    # IPFS_chech(greeter, chain, web3)

    
    key = 'acfd2fd8a1e9ccf031db0a93a861f6eb'
    set_txn_hash = greeter.transact().mapWorkflow(key)        
    contract_address = chain.wait.for_receipt(set_txn_hash)
    print('mapWorkflow_' + 'gasUsed=' + str(contract_address["gasUsed"]))