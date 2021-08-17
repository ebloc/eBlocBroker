#!/bin/bash

# source $HOME/v/bin/activate

cd ~/eBlocBroker/contract

cat <<EOF | brownie console --network eblocpoa
import json
with open('abi.json','w') as fp: json.dump(eBlocBroker.abi, fp)
EOF

# mv abi.json $HOME/eBlocBroker/eblocbroker/abi.json
