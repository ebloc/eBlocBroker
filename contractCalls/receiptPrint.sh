#!/bin/bash

val=$(python3 getProviderReceiptSize.py 0xf2129928bd1e6f4aa1ad131a37db2e55810cbbff)

for i in `seq 1 $val`;
do
    printVal=$(python getProviderReceiptNode.py 0xf2129928bd1e6f4aa1ad131a37db2e55810cbbff $i)
    echo $printVal
done    
