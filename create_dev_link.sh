#!/bin/bash
cd /home/giorgio/git/Categorise-Deluge-plugin
mkdir temp
export PYTHONPATH=./temp
python setup.py build develop --install-dir ./temp
cp ./temp/Categorise.egg-link /home/giorgio/.config/deluge/plugins
rm -fr ./temp
