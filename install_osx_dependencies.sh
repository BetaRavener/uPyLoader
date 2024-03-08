#!/bin/bash

echo ""
echo "I will install qt5, pyqt5, pyserial, sip. Tested on El Capitan 10.11.1."
read -p "Are you using Python 3.4 (possibly in a venv)? Is brew installed? [y]es, [n]o: " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    brew install qt5 # Tested with version 5.6.0
    brew install wget
    pip install pyqt5-macos-built==5.5.
    pip install pyserial==3.1.1
    if [ ! -d "sip-4.18.1" ]; then
      wget http://sourceforge.net/projects/pyqt/files/sip/sip-4.18.1/sip-4.18.1.zip
      unzip sip-4.18.1.zip
    fi
    cd sip-4.18.1
    python configure.py --incdir=../ve/include/python2.7
    make
    make install
fi
