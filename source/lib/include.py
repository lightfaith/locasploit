#!/usr/bin/env python
import os, sys, re, time, importlib, imp, subprocess
import define as lib
import log

def load_modules():
	""" Import modules from modules/ folder """
	lib.module_objects = []
	lib.modules = {}
	module_names = [x[:-3] for x in os.listdir('source/modules') if x[0]!='_' and x[-3:] == '.py']

	for m in module_names:
		if 'source.modules.' + m in sys.modules:
			imp.reload(sys.modules['source.modules.' + m]) # TODO deprecated?
		else:
			importlib.import_module('source.modules.' + m)

	#print module_objects
	for v in lib.module_objects:
		if v.name in lib.modules:
			log.warn('Duplicit module %s.' % (v.name))
		lib.modules[v.name] = v 
	
	#log.writeline(lib.modules)
	log.info('%d modules loaded.' % (len(lib.modules)))

def show_time(time):
	if type(time) != float:
		return '/'
	hours = time / 3600
	time = time % 3600
	minutes = time / 60
	time = time % 60
	return '%d:%02d:%06.3f' % (hours, minutes, time)

def command(c, value=False, stdout=True):
	commands = filter(None, c.split('|'))
	pss = []
	for i in range(0, len(commands)):
		com = filter(None, commands[i].split(' '))
		if i==0:
			pss.append(subprocess.Popen(com, stdout=subprocess.PIPE, env={'PATH': os.environ['PATH']}))
		else:
			pss.append(subprocess.Popen(com, stdout=subprocess.PIPE, env={'PATH': os.environ['PATH']}, stdin=pss[i-1].stdout))
		i += 1
	
	if stdout:
		return pss[-1].stdout.read()
	elif value:
		return pss[-1].returncode

def command_exists(c):
	com = command('which %s' % (c))
	return len(command('which %s' % (c))) > 0
