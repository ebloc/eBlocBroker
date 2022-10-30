#!/bin/bash

# https://github.com/duaraghav8/solium-plugin-security
# install:
# npm install -g ethlint --force
# npm install -g --save-dev prettier prettier-plugin-solidity

# macOS
# $HOME/node_modules/.bin/prettier --write contracts/**/*.sol --config .prettierrce

# Linux
prettier --write contracts/**/*.sol --config .prettierrce
rm -f contracts/.#*
solium --config contracts/.soliumrc.json -d contracts/
