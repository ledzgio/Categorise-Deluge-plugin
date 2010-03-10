#!/bin/bash
cd /home/marciano/workspace/Deluge_plugins/categorise
mkdir temp
export PYTHONPATH=./temp
python setup.py build develop --install-dir ./temp
cp ./temp/Categorise.egg-link /home/marciano/.config/deluge/plugins
rm -fr ./temp
