#!/bin/bash

# Convert from md to rst format
cp ../../README.md source/readme.md
python convert_md_2_rst.py
cp source/readme.rst ../quickstart.rst
cp source/geth.rst ../connect.rst
