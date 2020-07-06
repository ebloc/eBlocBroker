#!/bin/bash

# ignore deleted files to prevent them to added into git commit which will
# increase the file size

for i in `git status | grep deleted | awk '{print $2}'`;
do
    git update-index --assume-unchanged $i;
done
