#!/bin/bash


# install mandatory packages
yum install epel-release
yum install wget unzip python34 python34-pip python-reportlab python34-paramiko

LOCATION=`pwd`
# get binwalk
cd /tmp/
wget https://github.com/devttys0/binwalk/archive/master.zip -O master.zip
unzip master.zip
cd binwalk-master && sudo python3 setup.py uninstall && sudo python3 setup.py install && sudo ./deps.sh
cd "$LOCATION"
# set empty database files
for db in 'analysis' 'checksum' 'dict' 'module' 'vuln'; do
	cp -i $db.db.empty $db.db;
done

# install necessary python packages
sudo pip3 install paramiko reportlab
