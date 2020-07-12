#!/bin/bash

# git fetch
# git checkout origin/master -- README.md

wget -O geth.md https://raw.githubusercontent.com/ebloc/eBlocPOA/master/README.md
mv geth.md source/geth.md
cp $HOME/eBlocBroker/README.md /home/alper/eBlocBroker/docs/convert/source/readme.md

./convert_md_2_rst.py

mv source/readme.rst ../quickstart.rst
mv source/geth.rst   ../connect.rst
