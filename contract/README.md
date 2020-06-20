# Upgrades

## MAC solc upgrade

brew update
brew upgrade
brew tap ethereum/ethereum
brew install solidity

## Brownie Upgrade

```
pip install --upgrade pip
pip install -U eth-brownie
```

-----------------------------------------------

source $HOME/venv/bin/activate
brownie console --network private
> web3.eth.blockNumber

Paste following to get abi into console:

```
import json
with open('../eblocbroker/abi.json','w') as fp:
    json.dump(eBlocBroker.abi, fp)
```

# // , indent=2
