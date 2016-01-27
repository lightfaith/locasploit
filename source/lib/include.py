#!/usr/bin/env python
import os, sys, re, time, importlib, imp, subprocess, threading, traceback, signal
import define as lib
import log

def signal_handler(signal, frame):
	lib.scheduler.stop()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

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

def command(provided_command, value=False, stdout=True): # TODO definitely not complete - &&, ||, &, ;
	#commands = provided_command.split('|')
	sp = subprocess.Popen(provided_command, shell=True, env={'PATH': os.environ['PATH']}, stdout=subprocess.PIPE)
	if stdout:
		return sp.stdout.read()
	if value:
		return sp.returncode

def command_exists(c):
	com = command('which %s' % (c))
	return len(command('which %s' % (c))) > 0
