#!/bin/bash
# runs profile for locasploit -c input

if [ $1 ]; then file=$1; else file='input'; fi
python3 -m cProfile -s cumtime ./locasploit.py -c $file
