#!/bin/bash

for a in $1/*.tar.gz; do
    if [[ "$a" != $1/result-* ]] ; then
	tar -xvf "$a" -C $1;
    fi
done;
