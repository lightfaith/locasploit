#!/bin/bash

# install mandatory packages
sudo apt-get update &&
sudo apt-get install wget unzip python3 python3-pip python3-reportlab python3-paramiko

LOCATION=`pwd`
# get binwalk
cd /tmp/
wget https://github.com/devttys0/binwalk/archive/master.zip -O master.zip
unzip master.zip
cd binwalk-master && sudo python3 setup.py uninstall && sudo python3 setup.py install && sudo ./deps.sh || echo '[-] Binwalk installation failed, extracting functionality might not be successful. Consider installing desired packages manually.'
cd "$LOCATION"
# set empty database files
for db in 'analysis' 'checksum' 'dict' 'module' 'vuln'; do
	cp -i $db.db.empty $db.db;
done

# install necessary python packages
sudo pip3 install paramiko
