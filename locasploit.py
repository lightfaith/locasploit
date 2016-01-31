#!/usr/bin/env python3
import os, sys, importlib, re, argparse
from source.libs.define import *
#import source.lib.define as lib
from source.libs.parameters import *
from source.libs.commands import *
from source.libs.include import *
import source.libs.log as log


parser = argparse.ArgumentParser(prog='locasploit', description='Local enumeration and exploitation framework.')
parser.add_argument('-c', type=str, help = 'Load the specified configuration file', nargs=1, metavar='input_file', dest='input_file')
args = parser.parse_args()


def main():
	if is_admin():
		log.ok('Administrator privileges already granted.')
	
	# input from file?
	if args.input_file is not None:
		with open(args.input_file[0], 'r') as f:
			lib.input_commands = f.read().splitlines()
			#print commands
			while len(lib.input_commands)>0:
				c = lib.input_commands[0]
				del lib.input_commands[0]
				log.prompt()
				log.attachline(c)
				execute_command(c)

	# main program loop
	while True:
		log.prompt()
		if lib.python_version[0] == '2':
			func = raw_input
		elif lib.python_version[0] == '3':
			func = input
		else:
			log.err('Undefined python version (%s).' % lib.python_version)
			break
		command = func()
		execute_command(command)
	# end of main program loop


load_modules()
main()
