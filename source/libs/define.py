#!/usr/bin/env python3
import os, sys, threading

appname = 'Locasploit'                                    # application name
python_version = '.'.join(map(str, sys.version_info[:3])) # python version
prompt = ' >  '                                           # current prompt string
module_objects = []                                       # temporary list for module loading
modules = {}                                              # dictionary of all modules
active_module = None                                      # currently active module
#from_input_file = False                                   # commands provided from input file
commands = []                                             # list of commands to execute
command_history = []                                      # history of commands
module_history = []                                       # history of selected modules

dicts = {}                                                # dictionaries (for crypto, cracking etc.)
if 'kb' not in vars():
	kb = None                                             # knowledge base, initialized in kb.py


main_thread = threading.current_thread()
if 'scheduler' not in vars():
	scheduler = None                                      # thread scheduler, initialized in scheduler.py

if sys.platform.startswith('linux'):                      # global parameters
	import pwd
	global_parameters = {
		#'USER': pwd.getpwuid(os.getuid())[0], 
		#'HOME': pwd.getpwuid(os.getuid())[5],
		#'SHELL': pwd.getpwuid(os.getuid())[6], 
		'USER': os.environ['SUDO_USER'] if 'SUDO_USER' in os.environ 
				else os.environ['USER'],
		'HOME': os.environ['HOME'],
		'SHELL': os.environ['SHELL'],
		'ENVPATH': os.environ['PATH'],
		'TEMPDIR': '/tmp',
		'SYSTEMROOT': '/',
		'ROOT' : pwd.getpwuid(0)[0],
		'ROOT_HOME' : pwd.getpwuid(0)[5],
		
	}
elif sys.platform.startswith('win'):
	global_parameters = {
		'USER': os.environ['USERNAME'],
		'HOME': os.environ['HOMEPATH'],
		'TEMPDIR': os.environ['TEMP'],
		'WINDIR': os.environ['WINDIR'],
		'SYSTEMROOT': os.environ['SYSTEMROOT'],
		'ENVPATH': os.environ['PATH'],
	}
else:
	global_parameters = {}
