#!/usr/bin/env python
import os, pwd

prompt = ' >  '
module_objects = []
modules = {}
active_module = None
command_history = []
module_history = []
kb = {}
global_parameters = {
	'USER': pwd.getpwuid(os.getuid())[0], 
	'HOME': pwd.getpwuid(os.getuid())[5],
	'SHELL': pwd.getpwuid(os.getuid())[6], 
	'ROOT' : pwd.getpwuid(0)[0],
	'ROOT_HOME' : pwd.getpwuid(0)[5],
}
