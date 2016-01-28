#!/usr/bin/env python
import os, pwd, threading
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
scheduler = Scheduler()
scheduler.start()
global_parameters = {
	'USER': pwd.getpwuid(os.getuid())[0], 
	'HOME': pwd.getpwuid(os.getuid())[5],
	'SHELL': pwd.getpwuid(os.getuid())[6], 
	'ROOT' : pwd.getpwuid(0)[0],
	'ROOT_HOME' : pwd.getpwuid(0)[5],
}
