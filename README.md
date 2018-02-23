# How to Use eBlocBroker 

## About
**eBlocBroker** is a blockchain based autonomous computational resource broker.

- **Website:** [http://ebloc.cmpe.boun.edu.tr](http://ebloc.cmpe.boun.edu.tr) or [http://ebloc.org](http://ebloc.cmpe.boun.edu.tr)
- [Documentation](http://ebloc.cmpe.boun.edu.tr:3003/index.html)

## Build dependencies

[Geth](https://github.com/ethereum/go-ethereum/wiki/geth), [Parity](https://parity.io), [IPFS](https://ipfs.io/docs/install/) .

## How to connect into Private Ethereum Blockchain (eBloc) using geth

Please follow [here](https://github.com/ebloc/eblocGeth).

## How to use eBlocBroker inside an Amazon EC2 Instance

An Amazon image (AMI name: eBlocBroker, AMI Id: **ami-4a5b9530**) is also available that contains
`Geth` to connect to our local Ethereum based blockchain system. First launch an instance using this Amazon image, you will recieve its Public DNS hostname (IPv4). 


```bash
mkdir ~/ebloc-amazon
sshfs -o IdentityFile=full/path/to/my.pem ubuntu@Public-DNS-hostname:/home/ubuntu ~/ebloc-amazon
cd ~/ebloc-amazon

#On an another console you can ssh into the instance:
ssh -v -i "full/path/to/my.pem" ubuntu@Public-DNS-hostname

eblocServer                            #To run eBloc geth-server
cd ../eBlocBroker && python Driver.py  #To run the eBlocBroker
```

### Create your Ethereum Account

Inside your `geth-client`, use:

```
> personal.NewAccount()
Passphrase:
Repeat passphrase:
"0x2384a05f8958f3490fbb8ab6919a6ddea1ca0903"

> eth.accounts
["0x2384a05f8958f3490fbb8ab6919a6ddea1ca0903"]
```

- Open the following file: `$HOME/eBlocBroker/eBlocHeader.js` and change following line with the account you defined under `COINBASE`, 

 `COINBASE = "0x2384a05f8958f3490fbb8ab6919a6ddea1ca0903";`

Connect into eBloc private chain using Geth: `eblocServer `. On another console to attach Geth console please do: `eblocClient`.

Please note that first you have to run `eblocServer` and than `eblocClient`.

<!--- 
### How to create a new account


```bash
parity --chain /home/ubuntu/EBloc/parity.json account new --network-id 23422 --reserved-peers /home/ubuntu/EBloc/myPrivateNetwork.txt --jsonrpc-apis web3,eth,net,parity,parity_accounts,traces,rpc,parity_set --rpccorsdomain=*

Please note that password is NOT RECOVERABLE.
Type password:
Repeat password:
e427c111f968fe4ff6593a37454fdd9abf07c490  //your address is generated
```

- Inside `.profile` change `COINBASE` variable with the generated account address. For example, you could put your newly created address such as `"0xe427c111f968fe4ff6593a37454fdd9abf07c490"` into `COINBASE`. Do not forget to put `0x` at the beginning of the account.


- Update the following file `/home/ubuntu/EBloc/password.txt` with your account's password.
Best to make sure the file is not readable or even listable for anyone but you. You achieve this with: `chmod 700 /home/ubuntu/EBloc/password.txt`

- Open the following file: `/home/ubuntu/eBlocBroker/eBlocHeader.js` and change following line with the account you defined under `COINBASE`, which is `web3.eth.defaultAccount = "0xe427c111f968fe4ff6593a37454fdd9abf07c490";`

Connect into eBloc private chain using Parity: `eblocpserver`. You could also run it via `nohup eblocpserver &` on the background. On another console to attach Geth console to Parity, (on Linux) please do: `geth attach`.

Please note that first you have to run `eblocpserver` and than `geth attach`.

Inside Geth console when you type `eth.accounts` you should see the accounts you already created or imported.

```bash
> eth.accounts
["0xe427c111f968fe4ff6593a37454fdd9abf07c490"]
```

This line is required to update `Parity`'s enode.

```bash
rm  ~/.local/share/io.parity.ethereum/network/key
```

As final you should run Parity as follows which will also unlocks your account:

```bash
parity --chain /home/ubuntu/EBloc/parity.json --network-id 23422 --reserved-peers /home/ubuntu/EBloc/myPrivateNetwork.txt --jsonrpc-apis web3,eth,net,parity,parity_accounts,traces,rpc,parity_set --author $COINBASE --rpccorsdomain=* --unlock "0xe427c111f968fe4ff6593a37454fdd9abf07c490" --password password.txt
```
--->
## Connect to eBlocBroker Contract

```bash
address="0x8cb1d24ddb3d0d410ec60074a86cf695fc4ab3e6";
abi=[{"constant":true,"inputs":[{"name":"clusterAddr","type":"address"},{"name":"jobKey","type":"string"},{"name":"index","type":"uint256"}],"name":"getJobInfo","outputs":[{"name":"","type":"uint8"},{"name":"","type":"uint32"},{"name":"","type":"uint256"},{"name":"","type":"uint256"},{"name":"","type":"uint256"},{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"clusterAddr","type":"address"},{"name":"jobKey","type":"string"},{"name":"core","type":"uint32"},{"name":"jobDesc","type":"string"},{"name":"coreMinuteGas","type":"uint32"},{"name":"storageType","type":"uint8"},{"name":"miniLockId","type":"string"}],"name":"submitJob","outputs":[{"name":"success","type":"bool"}],"payable":true,"type":"function"},{"constant":true,"inputs":[{"name":"clusterAddr","type":"address"}],"name":"getClusterReceivedAmount","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"jobKey","type":"string"},{"name":"index","type":"uint32"},{"name":"jobRunTimeMinute","type":"uint32"},{"name":"ipfsHashOut","type":"string"},{"name":"storageType","type":"uint8"},{"name":"endTimeStamp","type":"uint256"}],"name":"receiptCheck","outputs":[{"name":"success","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"clusterAddr","type":"address"},{"name":"ipfsHash","type":"string"},{"name":"index","type":"uint32"}],"name":"refundMe","outputs":[{"name":"","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"coreLimit","type":"uint32"},{"name":"clusterName","type":"bytes"},{"name":"fID","type":"bytes"},{"name":"miniLockId","type":"bytes"},{"name":"price","type":"uint256"},{"name":"ipfsId","type":"bytes32"}],"name":"updateCluster","outputs":[{"name":"success","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"getClusterAddresses","outputs":[{"name":"","type":"address[]"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"getDeployedBlockNumber","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"clusterAddr","type":"address"}],"name":"getClusterInfo","outputs":[{"name":"","type":"bytes"},{"name":"","type":"bytes"},{"name":"","type":"bytes"},{"name":"","type":"uint256"},{"name":"","type":"uint256"},{"name":"","type":"bytes32"}],"payable":false,"type":"function"},{"constant":false,"inputs":[],"name":"deregisterCluster","outputs":[{"name":"success","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[],"name":"testCallStack","outputs":[{"name":"","type":"int256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"coreLimit","type":"uint32"},{"name":"clusterName","type":"bytes"},{"name":"fID","type":"bytes"},{"name":"miniLockId","type":"bytes"},{"name":"price","type":"uint256"},{"name":"ipfsId","type":"bytes32"}],"name":"registerCluster","outputs":[{"name":"success","type":"bool"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"clusterAddr","type":"address"},{"name":"jobKey","type":"string"}],"name":"getJobSize","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"jobKey","type":"string"},{"name":"index","type":"uint32"},{"name":"stateId","type":"uint8"},{"name":"startTimeStamp","type":"uint256"}],"name":"setJobStatus","outputs":[{"name":"success","type":"bool"}],"payable":false,"type":"function"},{"inputs":[],"payable":false,"type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"name":"cluster","type":"address"},{"indexed":false,"name":"jobKey","type":"string"},{"indexed":false,"name":"index","type":"uint256"},{"indexed":false,"name":"storageType","type":"uint8"},{"indexed":false,"name":"miniLockId","type":"string"},{"indexed":false,"name":"desc","type":"string"}],"name":"LogJob","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"cluster","type":"address"},{"indexed":false,"name":"jobKey","type":"string"},{"indexed":false,"name":"index","type":"uint256"},{"indexed":false,"name":"recipient","type":"address"},{"indexed":false,"name":"recieved","type":"uint256"},{"indexed":false,"name":"returned","type":"uint256"},{"indexed":false,"name":"endTime","type":"uint256"},{"indexed":false,"name":"ipfsHashOut","type":"string"},{"indexed":false,"name":"storageType","type":"uint8"}],"name":"LogReceipt","type":"event"}]
var eBlocBroker = web3.eth.contract(abi).at(address);
```

## Start Running Cluster using eBlocBroker

If you want to provide `IPFS` service please do following: `ipfs init`

### SLURM Setup:
SLURM have to work on the background. Please run: 

```bash 
bash runSlurm.sh
```

Following example should successfully submit the job:

```bash
cd /home/ubuntu/slurmTest
sbatch -U science -N1 run.sh
Submitted batch job 1
```

### Running `IPFS`, `Parity` and eBlocBroker scripts on the background:

```bash
ipfs daemon &
nohup bash eblocpserver.sh &
cd $EBLOCBROKER
nohup python Driver.py &
```

### Cluster Side: How to register a cluster

Please note that: if you don't have any `Federated Cloud ID` or `MiniLock ID` give an empty string: `""`.

```bash
coreNumber         = 128;
clusterName        = "eBlocCluster";
federationCloudId  = "ee14ea28-b869-1036-8080-9dbd8c6b1579@b2drop.eudat.eu";
miniLockId         = "9VZyJy1gRFJfdDtAjRitqmjSxPjSAjBR6BxH59UeNgKzQ"
corePriceMinuteWei = 1000000000000000; //For experimental you could also give 1.
ipfsID             = "QmXsbsmdvHkn2fPSS9fXnSH2YZ382f8nNVojYbELsBEbKb"; //recieved from "ipfs id"

//RegisterCluster
if( federationCloudId.length < 128 && clusterName < 64 && (miniLockId.length == 0 || miniLockId.length == 45) )
	eBlocBroker.registerCluster(coreNumber, clusterName, federationCloudId, miniLockId, corePriceMinuteWei, ipfsID; 

//UpdateCluster
if( federationCloudId.length < 128 && clusterName < 64 && (miniLockId.length == 0 || miniLockId.length == 45) )
	eBlocBroker.updateCluster(coreNumber, clusterName, federationCloudId, miniLockId, corePriceMinuteWei, ipfsID; 

//Deregister
eBlocBroker.deregisterCluster()
```

**Trigger code on start and end of the submitted job:** Cluster should do: `sudo chmod +x /path/to/slurmScript.sh`. This will allow script to be readable and executable by any SlurmUser. Update following line on the slurm.conf file: `MailProg=/home/ubuntu/eBlocBroker/slurmScript.sh`

```bash
sudo chmod 755 ~/.eBlocBroker/*
```

#### **How to return all available Clusters Addresses**

```bash
eBlocBroker.getClusterAddresses(); //returns all 
["0x6af0204187a93710317542d383a1b547fa42e705"]
```

### Client Side: How to obtain IPFS Hash of the job:

It is important that first you should run IPFS daemon on the background: `ipfs daemon &`. If it is not running, cluster is not able to get the IPFS object from the client's node.

If IPFS is successfully running on the background you should see something like this:

```bash
[~] ps aux | grep 'ipfs daemon' | grep -v 'grep'
avatar           24190   1.1  2.1 556620660 344784 s013  SN    3:59PM   4:10.74 ipfs daemon
```

Example code could be seen here:

```
git clone https://github.com/avatar-lavventura/simpleSlurmJob.git 
cd simpleSlurmJob
```

Client should put his SLURM script inside a file called `run.sh`. Please note that you do not have to identify `-n` and `-t` parameters, since they will be overritten with arguments provided by the client on the cluster side.

Target into the folder you want to submit and do: `ipfs add -r .` You will see something similiar with following output:

```bash
added QmYsUBd5F8FA1vcUsMAHCGrN8Z92TdpNBAw6rMxWwmQeMJ simpleSlurmJob/helloworld.cpp
added QmbTzBprmFEABAWwmw1VojGLMf3nv7Z16eSgec55DYdbiX simpleSlurmJob/run.sh
added QmXsCmg5jZDvQBYWtnAsz7rukowKJP3uuDuxfS8yXvDb8B simpleSlurmJob
```

- Main folder's IPFS hash(for example:`QmWmyoMoctfbAaiEs2G46gpeUmhqFRDW6KWo64y5r581Vd`) would be used as key to the submitted job to the `eBlocBroker` by the client.

- If you want to share it through gitHub, please push all files into github repository and share its web URL right after `https://github.com/`, which is `USERNAME/REPOSITORY.git`.

For example, web URL of `https://github.com/avatar-lavventura/simpleSlurmJob.git`, you have to submit: `avatar-lavventura/simpleSlurmJob.git`.

### **How to submit a job using storageTypes**

#### **1. How to submit a job using IPFS**

```bash
clusterID        = "0x6af0204187a93710317542d383a1b547fa42e705"; //clusterID you would like to submit.
clusterInfo      = eBlocBroker.getClusterInfo("0x6af0204187a93710317542d383a1b547fa42e705")
clusterCoreLimit = clusterInfo[3]
pricePerMin      = clusterInfo[4]
jobKey           = "QmefdYEriRiSbeVqGvLx15DKh4WqSMVL8nT4BwvsgVZ7a5"
myMiniLockId     = ""
coreNum          = 1; 
coreGasDay       = 0;
coreGasHour      = 0;
coreGasMin       = 10;
jobDescription   = "Science"
coreMinuteGas    = coreGasMin + coreGasHour * 60 + coreGasDay * 1440;
storageType      = 0 ; // Please note that 0 stands for IPFS , 1 stands for eudat.

if (coreNum <= clusterCoreLimit && jobDescription.length < 128 && jobKey.length == 46) {
	eBlocBroker.insertJob(clusterID, jobHash, coreNum, jobDescription, coreMinuteGas, storageType, myMiniLockId, {from: web3.eth.accounts[0], value: coreNum*pricePerMin*coreMinuteGas, gas: 3000000 } );
}
```
#### **2. How to submit a job using EUDAT**

Before doing this you have to be sure that you have shared your folder with cluster's FId. Please [follow](https://github.com/avatar-lavventura/someCode/issues/4). Otherwise your job will not be accepted.


Now `jobHash` should be your `FederationCloudId` followed by the name of the folder your are sharing having equal symbol in between.

Example:
`jobHash="3d8e2dc2-b855-1036-807f-9dbd8c6b1579=folderName"`

#####  **Script:**

```bash
clusterID      = "0x6af0204187a93710317542d383a1b547fa42e705"; //clusterID you would like to submit.
pricePerMin    = eBlocBroker.getClusterCoreMinutePrice(clusterID);
myMiniLockId   = ""
jobKey         = "3d8e2dc2-b855-1036-807f-9dbd8c6b1579=folderName"
coreNum        = 1; //Before assigning this value please check the coreLimit of the cluster.
coreGasDay     = 0;
coreGasHour    = 0;
coreGasMin     = 10;
jobDescription = "Science"
coreMinuteGas  = coreGasMin + coreGasHour * 60 + coreGasDay * 1440;
storageType    = 1 ; // Please note that 0 stands for IPFS , 1 stands for eudat.

clusterCoreLimit = eBlocBroker.getClusterCoreLimit(clusterID);
if (coreNum <= clusterCoreLimit && jobDescription.length < 128 ) {
	eBlocBroker.insertJob(clusterID, jobHash, coreNum, jobDescription, coreMinuteGas, storageType, myMiniLockId, {from: web3.eth.accounts[0], value: coreNum*pricePerMin*coreMinuteGas, gas: 3000000 } );
}
```

#### **3. How to submit a job using IPFS+miniLock**

###### miniLock Setup

```bash
sudo npm install -g minilock-cli@0.2.13
```

Please check following [tutorial](https://www.npmjs.com/package/minilock-cli):

###### Generate a miniLock  ID

```bash
$ mlck id alice@example.com --save
period dry million besides usually wild everybody
 
Passphrase (leave blank to quit): 
```
You can look up your miniLock ID any time.

```bash
$ mlck id
Your miniLock ID: LRFbCrhCeN2uVCdDXd2bagoCM1fVcGvUzwhfVdqfyVuhi
```

###### How to encripty your folder using miniLock

```bash
myMiniLockId="LRFbCrhCeN2uVCdDXd2bagoCM1fVcGvUzwhfVdqfyVuhi"
clusterMiniLockId="9VZyJy1gRFJfdDtAjRitqmjSxPjSAjBR6BxH59UeNgKzQ";
encrypyFolderPath="./ipfsCode"
tar -cvzf $encrypyFolderPath.tar.gz $encrypyFolderPath

mlck encrypt -f $encrypyFolderPath.tar.gz $clusterMiniLockId --passphrase="$(cat mlck_password.txt)"
ipfs add $ncrypyFolderPath.minilock
added QmefdYEriRiSbeVqGvLx15DKh4WqSMVL8nT4BwvsgVZ7a5 message.tar.gz.minilock
```

###### **Script:**
```bash
clusterID        = "0x6af0204187a93710317542d383a1b547fa42e705"; /* clusterID you would like to submit. */
clusterInfo      = eBlocBroker.getClusterInfo("0x6af0204187a93710317542d383a1b547fa42e705")
clusterCoreLimit = clusterInfo[3]
pricePerMin      = clusterInfo[4]
jobKey           = "QmefdYEriRiSbeVqGvLx15DKh4WqSMVL8nT4BwvsgVZ7a5"
myMiniLockId     = "LRFbCrhCeN2uVCdDXd2bagoCM1fVcGvUzwhfVdqfyVuhi"
coreNum          = 1; 
coreGasDay       = 0;
coreGasHour      = 0;
coreGasMin       = 10;
jobDescription   = "Science"
coreMinuteGas    = coreGasMin + coreGasHour * 60 + coreGasDay * 1440;
storageType      = 2; // Please note that 0 stands for IPFS , 1 stands for eudat. 2 stands for IPFS with miniLock

if (coreNum <= clusterCoreLimit && jobDescription.length < 128 && miniLockId.length == 46 && jobKey.length == 46) {
	eBlocBroker.insertJob(clusterID, jobHash, coreNum, jobDescription, coreMinuteGas, storageType, myMiniLockId, {from: web3.eth.accounts[0], value: coreNum*pricePerMin*coreMinuteGas, gas: 3000000 } );
}
```

#### **4. How to submit a job using GitHub**

```bash
clusterID        = "0x6af0204187a93710317542d383a1b547fa42e705"; //clusterID you would like to submit.
clusterInfo      = eBlocBroker.getClusterInfo("0x6af0204187a93710317542d383a1b547fa42e705")
clusterCoreLimit = clusterInfo[3]
pricePerMin      = clusterInfo[4]
jobKey           = "avatar-lavventura/simpleSlurmJob.git" /* Please write link after "https://github.com/" */
myMiniLockId     = ""
coreNum          = 1; 
coreGasDay       = 0;
coreGasHour      = 0;
coreGasMin       = 10;
jobDescription   = "Science"
coreMinuteGas    = coreGasMin + coreGasHour * 60 + coreGasDay * 1440;
storageType      = 3 ; /* Please note that 3 stands for github repository share */

if (coreNum <= clusterCoreLimit && jobDescription.length < 128) {
	eBlocBroker.insertJob(clusterID, jobHash, coreNum, jobDescription, coreMinuteGas, storageType, myMiniLockId, {from: web3.eth.accounts[0], value: coreNum*pricePerMin*coreMinuteGas, gas: 3000000 } );
}
```

### **How to obtain Submitted Job's Information:**

This will return:

- status  could be `"QUEUED"` or `"RUNNING"` or `"COMPLETED"` 
- `ipfsOut` is Completed Job's folder's ipfs hash. This exists if the job is completed.
...

```bash
clusterID="0x6af0204187a93710317542d383a1b547fa42e705"; //clusterID that you have submitted your job.
index   = 0;      
jobHash = "QmXsCmg5jZDvQBYWtnAsz7rukowKJP3uuDuxfS8yXvDb8B"
eBlocBroker.getJobInfo(clusterID, jobHash, 0);
```

### **Events: In order to keep track of the log of receipts**

```bash
fromBlock = MyContract.eth.blockNumber; //This could be also the blockNumber the job submitted.
var e = eBlocBroker.LogReceipt({}, {fromBlock:fromBlock, toBlock:'latest'});
e.watch(function(error, result){
  console.log(JSON.stringify(result));
});
```

### **Required Installations**

```bash
sudo pip install sphinx_rtd_theme pyocclient

sudo apt-get install davfs2 mailutils
sudo apt-get install -y nodejs

wget -qO- https://deb.nodesource.com/setup_7.x | sudo bash -
```
