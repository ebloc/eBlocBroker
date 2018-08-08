#!/bin/bash                      
#                                |
# To Run:  sudo bash runDaemon.sh|
#---------------------------------

. venv/bin/activate # source $HOME/.venv-py3/bin/activate

if [[ "$EUID" -ne 0 ]]; then    
    nohup python -Bu Driver.py >> $HOME/.eBlocBroker/clusterDriver.out 2>&1 &
    sudo tail -f $HOME/.eBlocBroker/clusterDriver.out
else
    echo "This script must be run as non-root. Please run without 'sudo'." 
fi

# gopath=$(go env | grep 'GOPATH' | cut -d "=" -f 2 | tr -d '"');
# export PATH=$PATH:$gopath/bin;
