#!/usr/bin/env python33
import os, sys, re, time, importlib, imp, subprocess, threading, traceback, signal, logging
import source.libs.define as lib
import source.libs.kb
import source.libs.scheduler
import source.libs.log as log

def exit_program(signal, frame):
	log.attachline()
	log.info('Killing all the threads...')
	lib.scheduler.stop()
	while lib.scheduler.isAlive():
		time.sleep(0.1)
	log.info('%s out.' % lib.appname)
	sys.exit(0)

signal.signal(signal.SIGINT, exit_program)

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


def command(provided_command, value=False, stdout=True):
	sp = subprocess.Popen(provided_command, shell=True, env={'PATH': os.environ['PATH']}, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if stdout:
		return sp.stdout.read()
	if value:
		return sp.returncode

def command_exists(c):
	com = command('which %s' % (c))
	return len(command('which %s' % (c))) > 0

def positive(string):
	return string.lower() in ['y', 'yes', 'true', 't', '1']

def negative(string):
	return string.lower() in ['n', 'no', 'false', 'f', '0']

def is_admin():
	if sys.platform.startswith('linux'):
		if os.geteuid() == 0:
			return True
		return False
	
	elif sys.platform.startswith('win'):
		# can write to C:\Windows\temp?
		if os.access(os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'temp'), os.W_OK):
			return True
		return False
	else:
		log.warn('Cannot check root privileges, platform is not fully supported (%s).' % sys.platform)
