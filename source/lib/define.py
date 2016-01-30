#!/usr/bin/env python
import os, threading
from kb import *
from scheduler import *

appname = 'Locasploit'
python_version = '2.7.9' # TODO determine on the fly
prompt = ' >  '
module_objects = []
modules = {}
active_module = None
input_commands = []
command_history = []
module_history = []
kb = KB()
main_thread = threading.current_thread()
scheduler = Scheduler()
scheduler.start()

if sys.platform.startswith('linux'):
	import pwd
	global_parameters = {
		#'USER': pwd.getpwuid(os.getuid())[0], 
		#'HOME': pwd.getpwuid(os.getuid())[5],
		#'SHELL': pwd.getpwuid(os.getuid())[6], 
		'USER': os.environ['SUDO_USER'] if 'SUDO_USER' in os.environ 
				else os.environ['USERNAME'], # takes SUID into consideration
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