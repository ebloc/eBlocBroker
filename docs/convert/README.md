# eBlocBroker

## About
Recently, peer-to-peer based blockchain infrastructures have emerged as disruptive technologies and have lead to the realization of crypto-currencies and smart contracts that can used in a globally trustless manner. eBlocBroker is a blockchain based autonomous computational resource broker

----

## Build dependencies

geth, parity, [IPFS](https://ipfs.io/docs/install/)

## Using via Amazon AWS

**Public AMI:** `eBlocBroker  ami-42173a54`

```bash
mkdir ~/ebloc-amazon
sshfs -o IdentityFile=full/path/to/my.pem ubuntu@Public-DNS-hostname:/home/ubuntu ~/ebloc-amazon
cd ~/ebloc-amazon

#On an another console do:
ssh -v -i "full/path/to/my.pem" ubuntu@Public-DNS-hostname
cd mybin && nohup eblocpserver &
cd ../eBlocBroker
python Driver.py
```

### Create New Account

This line is required to update `Parity`'s enode.

```bash
rm  ~/.local/share/io.parity.ethereum/network/key
```

```bash
> parity --chain /home/ubuntu/EBloc/parity.json account new --network-id 23422 --reserved-peers /home/ubuntu/EBloc/myPrivateNetwork.txt --jsonrpc-apis web3,eth,net,parity,parity_accounts,traces,rpc,parity_set --author $COINBASE --rpccorsdomain=*
Please note that password is NOT RECOVERABLE.
Type password:
Repeat password:
e427c111f968fe4ff6593a37454fdd9abf07c490
```

- Inside `.profile` change `COINBASE` variable with the account owner of the mined block reward. For example, you could but your newly created account: `"0xe427c111f968fe4ff6593a37454fdd9abf07c490"` into `COINBASE`. Do not forget to put `0x` at the beginning of the account.


- Update following file `/home/ubuntu/EBloc/password.txt` with your account's password, that is stored under `COINBASE`:
Best to make sure the file is not readable or even listable for anyone but you. You achieve this with: `chmod 700 /home/ubuntu/EBloc/password.txt`

- Open following file: `/home/ubuntu/eBlocBroker/eBlocBrokerHeader.js` and change following line with the account you defined under `COINBASE`: `web3.eth.defaultAccount = "0xe427c111f968fe4ff6593a37454fdd9abf07c490";`

Connect into eBloc private chain using Parity: `eblocpserver`. You could also run it via `nohup eblocpserver &` on the background. On another console to attach Geth console to Parity, (on Linux) please do: `geth attach ~/.local/share/io.parity.ethereum/jsonrpc.ipc`. Its alias is: `eblocpclient`.

Please note that first you have to run `eblocpserver` and than `eblocpclient`.

Inside Geth console when you type `eth.accounts` you should see the accounts you already created or imported.

```bash
> eth.accounts
["0xe427c111f968fe4ff6593a37454fdd9abf07c490"]
```

As final you should run Parity as follows which will unlock the account:

```bash
parity --chain /home/ubuntu/EBloc/parity.json --network-id 23422 --reserved-peers /home/ubuntu/EBloc/myPrivateNetwork.txt --jsonrpc-apis web3,eth,net,parity,parity_accounts,traces,rpc,parity_set --author $COINBASE --rpccorsdomain=* --unlock "0xe427c111f968fe4ff6593a37454fdd9abf07c490" --password password.txt
```

**Required path changes you have to do on the script files:**

export EBLOCBROKER=/home/netlab/contract

Additinoal changes have to make on: since SLURM script functon won't able to access .profile file.
start_code.py endCode.py slurmScript.sh

### Start Running Provider using eBlocBroker

If you want to provide `IPFS` service please do following:

```bash
ipfs uses a repository in the local file system. By default, the repo is located at ~/.ipfs.
To change the repo location, set the $IPFS_PATH environment variable:
> export IPFS_PATH=/path/to/ipfsrepo
> ipfs init

initializing ipfs node at /path/to/ipfsrepogenerating 2048-bit RSA keypair...done
peer identity: QmXudqoQUyHjmS2s8j59tY6GKCz3KR2qPXS6uMskbFV8mH
to get started, enter:

	ipfs cat /ipfs/QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG/readme
```

#### First SLURM have to work on the background SLURM Setup:

```bash
sudo slurmd
sudo munged -f
/etc/init.d/munge start #Do to Amazon AWS, you may need to create new user with a password.
sudo slurmdbd
mkdir /tmp/slurmstate && sudo slurmctld -c
```

Following example should successfully submit the job:

```bash
cd /home/ubuntu/slurmTest
sbatch -U science -N1 run.sh
Submitted batch job 1
```

#### Running `IPFS`, `Parity` and eBlocBroker scripts on the background:

```bash
ipfs daemon &
nohup eblocpserver &
cd $EBLOCBROKER
nohup python py_providerDriver.py &
```

----

## Connect to eBlocBroker Contract

```bash
address="";
abi=[]

var eBlocBroker = web3.eth.contract(abi).at(address);
```

### Provider Owner: How to create a provider:

Please note that: if you don't have any `Federated Cloud ID` or `MiniLock ID` give an empty string: `""`.

```bash
coreNumber         = 128;
providerName        = "eBlocProvider";
federationCloudId  = "ee14ea28-b869-1036-8080-9dbd8c6b1579@b2drop.eudat.eu";
provider_minilock_id  = "9VZyJy1gRFJfdDtAjRitqmjSxPjSAjBR6BxH59UeNgKzQ"
corePriceMinuteWei = 1000000000000000; //For experimental you could also give 1.
ipfsID             = "QmXsbsmdvHkn2fPSS9fXnSH2YZ382f8nNVojYbELsBEbKb"; //recieved from "ipfs id"
eBlocBroker.createProvider(coreNumber, providerName, federationCloudId, provider_minilock_id, corePriceMinuteWei, ipfsID;
```

**Trigger code on start and end of the submitted job:** Provider should do: `sudo chmod +x /path/to/slurmScript.sh`. This will allow script to be readable and executable by any SlurmUser. Update following line on the slurm.conf file: `MailProg=/home/ubuntu/eBlocBroker/slurmScript.sh`

```bash
sudo chmod 755 ~/.eBlocBroker/*
```


-----

### Client Side: How to submit a Job with IPFS Hash:

Is is important that first you should run IPFS daemon on the background: `ipfs daemon &`. If it is not running, provider is not able to get the IPFS object from the client's node.

If IPFS is successfully running on the background you should see something like this:

```bash
$ ps aux | grep -E 'ipfs daemon' | grep -v 'grep'
avatar           24190   1.1  2.1 556620660 344784 s013  SN    3:59PM   4:10.74 ipfs daemon
```

`mkdir ipfsCode && cd ipfsCode`

Create `helloworld.cpp`:

```bash
#include <iostream>
#include <fstream>
using namespace std;

int main () {
  ofstream myfile;
  myfile.open ("helloworld.txt");
  myfile << "Hello World.\n";
  myfile.close();
  return 0;
}
```

Client should put his SLURM script inside a file called `run.sh`. Please note that you do not have to identify `-n` and `-t` parameters, since they will be overritten with arguments provided by the client on the provider side.

**For example:**

Create `run.sh`:

```bash
#!/bin/bash
#SBATCH -o slurm.out        # STDOUT
#SBATCH -e slurm.err        # STDERR
#SBATCH --mail-type=ALL
#SBATCH --mail-user=alper.alimoglu@gmail.com
#SBATCH --requeue

g++ helloworld.cpp -o hello
./hello
sleep 60;
```

Target into the folder you want to submit and please do: `ipfs add -r .` You will face something similiar with following output:

```bash
added QmYsUBd5F8FA1vcUsMAHCGrN8Z92TdpNBAw6rMxWwmQeMJ ipfs_code/helloworld.cpp
added QmbTzBprmFEABAWwmw1VojGLMf3nv7Z16eSgec55DYdbiX ipfs_code/run.sh
added QmXsCmg5jZDvQBYWtnAsz7rukowKJP3uuDuxfS8yXvDb8B ipfs_code
```
Main folder's IPFS hash(for example:`QmWmyoMoctfbAaiEs2G46gpeUmhqFRDW6KWo64y5r581Vd`) would be used as key to the submitted job to the `eBlocBroker` by the client.

**How To Submit a Job:**

```bash
eBlocBroker.get_providers(); # Returns all available Providers Addresses.
["0x6af0204187a93710317542d383a1b547fa42e705"]
```
###**Submit a Job using IPFS:**

```bash
providerID        = "0x6af0204187a93710317542d383a1b547fa42e705"; //providerID you would like to submit.
provider_info      = eBlocBroker.getProviderInfo("0x6af0204187a93710317542d383a1b547fa42e705")
providerCoreLimit = provider_info[3]
pricePerMin      = provider_info[4]
jobHash          = "QmefdYEriRiSbeVqGvLx15DKh4WqSMVL8nT4BwvsgVZ7a5"
user_minilock_id     = ""
coreNum          = 1;
coreGasDay       = 0;
coreGasHour      = 0;
coreGasMin       = 10;
jobDescription   = "Science"
coreMinuteGas    = coreGasMin + coreGasHour * 60 + coreGasDay * 1440;
storageType       = 0 ; // Please note that 0 stands for IPFS , 1 stands for eudat.

if (coreNum <= providerCoreLimit ) {//Before assigning coreNum checks the coreLimit of the provider.
	//Following line submits the Job:
	eBlocBroker.insertJob(providerID, jobHash, coreNum, jobDescription, coreMinuteGas, storageType, user_minilock_id, {from: web3.eth.accounts[0], value: coreNum*pricePerMin*coreMinuteGas, gas: 3000000 } );
}
```

###**Submit a Job using IPFS+miniLock**

####miniLock Setup
First do following installations:

```bash
sudo npm install -g minilock-cli@0.2.13
```

Please check following [tutorial](https://www.npmjs.com/package/minilock-cli):

#####Generate an ID

First, you need a miniLock ID.

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

#####How to encripty your folder using miniLock

```bash
user_minilock_id="LRFbCrhCeN2uVCdDXd2bagoCM1fVcGvUzwhfVdqfyVuhi"
provider_minilock_id="9VZyJy1gRFJfdDtAjRitqmjSxPjSAjBR6BxH59UeNgKzQ";
encrypyFolderPath="./ipfsCode"
tar -cvzf $encrypyFolderPath.tar.gz $encrypyFolderPath

mlck encrypt -f $encrypyFolderPath.tar.gz $provider_minilock_id --passphrase="$(cat mlck_password.txt)"
ipfs add $ncrypyFolderPath.minilock
added QmefdYEriRiSbeVqGvLx15DKh4WqSMVL8nT4BwvsgVZ7a5 message.tar.gz.minilock
```

```bash
providerID        = "0x6af0204187a93710317542d383a1b547fa42e705"; //providerID you would like to submit.
provider_info      = eBlocBroker.getProviderInfo("0x6af0204187a93710317542d383a1b547fa42e705")
providerCoreLimit = provider_info[3]
pricePerMin      = provider_info[4]
jobHash          = "QmefdYEriRiSbeVqGvLx15DKh4WqSMVL8nT4BwvsgVZ7a5"
user_minilock_id     = "LRFbCrhCeN2uVCdDXd2bagoCM1fVcGvUzwhfVdqfyVuhi"
coreNum          = 1;
coreGasDay       = 0;
coreGasHour      = 0;
coreGasMin       = 10;
jobDescription   = "Science"
coreMinuteGas    = coreGasMin + coreGasHour * 60 + coreGasDay * 1440;
storageType       = 2; // Please note that 0 stands for IPFS , 1 stands for eudat. 2 stands for IPFS with miniLock

if (coreNum <= providerCoreLimit ) {//Before assigning coreNum checks the coreLimit of the provider.
	//Following line submits the Job:
	eBlocBroker.insertJob(providerID, jobHash, coreNum, jobDescription, coreMinuteGas, storageType, user_minilock_id, {from: web3.eth.accounts[0], value: coreNum*pricePerMin*coreMinuteGas, gas: 3000000 } );
}
```

###**Submit a Job using EUDAT**

Before doing this you have to be sure that you have shared your folder with provider's FId. Please follow ...<github issue>. Otherwise your job will not accepted.


Now `jobHash` should be your `FederationCloudId` followed by the name of the folder your are sharing having equal symbol in between.

Example:
`jobHash="3d8e2dc2-b855-1036-807f-9dbd8c6b1579=folderName"`


```bash
providerID      = "0x6af0204187a93710317542d383a1b547fa42e705"; //providerID you would like to submit.
pricePerMin    = eBlocBroker.getProviderCoreMinutePrice(providerID);
user_minilock_id   = ""
jobHash        = "3d8e2dc2-b855-1036-807f-9dbd8c6b1579=folderName"
coreNum        = 1; //Before assigning this value please check the coreLimit of the provider.
coreGasDay     = 0;
coreGasHour    = 0;
coreGasMin     = 10;
jobDescription = "Science"
coreMinuteGas  = coreGasMin + coreGasHour * 60 + coreGasDay * 1440;
storageType     = 1 ; // Please note that 0 stands for IPFS , 1 stands for eudat.

providerCoreLimit = eBlocBroker.getProviderCoreLimit(providerID);
if (coreNum <= providerCoreLimit ) {
	//Following line submits the Job:
	eBlocBroker.insertJob(providerID, jobHash, coreNum, jobDescription, coreMinuteGas, storageType, user_minilock_id, {from: web3.eth.accounts[0], value: coreNum*pricePerMin*coreMinuteGas, gas: 3000000 } );
}
```



**Obtain Submitted Job's Information:**

This will return:

- status  == `"QUEUED"` or `"RUNNING"` or `"COMPLETED"`
- ipfsOut == Completed Job's resulted folder. This exists if the job is completed.
...

```bash
providerID="0x6af0204187a93710317542d383a1b547fa42e705"; //providerID that you have submitted your job.
index   = 0;
jobHash = "QmXsCmg5jZDvQBYWtnAsz7rukowKJP3uuDuxfS8yXvDb8B"
eBlocBroker.getJobInfo(providerID, jobHash, 0);
```

**Events: In order to keep track of the log of receipts**

```bash
fromBlock = MyContract.eth.blockNumber; //This could be also the blockNumber the job submitted.
var e = eBlocBroker.LogReceipt({}, {fromBlock:fromBlock, toBlock:'latest'});
e.watch(function(error, result){
  console.log(JSON.stringify(result));
});
```

**Required Installations**

```bash
npm i --save bs58  //https://www.npmjs.com/package/bs58
npm install web3
npm install web3_ipc --save
sudo npm install -g minilock-cli@0.2.13
sudo pip install sphinx_rtd_theme
sudo apt-get install davfs2
pip install pyocclient
apt-get install mailutils
sudo npm install binstring

wget -qO- https://deb.nodesource.com/setup_7.x | sudo bash -
sudo apt-get install -y nodejs
```
