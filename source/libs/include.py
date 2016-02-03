#!/usr/bin/env python3
import os, sys, re, time, importlib, imp, subprocess, threading, traceback, signal, logging
import source.libs.define as lib
import source.libs.kb
import source.libs.scheduler
import source.libs.log as log

def exit_program(signal, frame):
	log.attachline()
	log.info('Killing all the threads...')
	# stop the scheduler (will stop all threads)
	lib.scheduler.stop()
	# wait for scheduler termination
	while lib.scheduler.isAlive():
		time.sleep(0.1)
	log.info('%s out.' % lib.appname)
	sys.exit(0)

# run exit program on SIGINT
signal.signal(signal.SIGINT, exit_program)


def load_modules():
	""" Import modules from source/modules/ folder """
	lib.module_objects = []
	lib.modules = {}
	module_names = [x[:-3] for x in os.listdir('source/modules') if x[0]!='_' and x[-3:] == '.py']

	# import/reimport modules
	for m in module_names:
		if 'source.modules.' + m in sys.modules:
			imp.reload(sys.modules['source.modules.' + m]) # TODO deprecated?
		else:
			importlib.import_module('source.modules.' + m)
	
	# initialize modules dictionary
	for v in lib.module_objects:
		if v.name in lib.modules:
			log.warn('Duplicit module %s.' % (v.name))
		lib.modules[v.name] = v 
	
	log.info('%d modules loaded.' % (len(lib.modules)))



def load_dicts():
	lib.dicts = {}
	dicts = [x for x in os.listdir('dictionaries') if x[-4:].lower() in ['.txt', '.dic']]
	for d in dicts:
		lines = []
		path = os.path.join('dictionaries', d)
		if os.access(path, os.R_OK):
			with open(path, 'r') as f:
				lines = [x.strip() for x in f.readlines()]
				lib.dicts[d[:-4].upper()] = lines
	log.info('%d dictionaries loaded.' % (len(lib.dicts)))



def command(provided_command, value=False, stdout=True):
	""" Run a given command """
	sp = subprocess.Popen(provided_command, shell=True, env={'PATH': os.environ['PATH']}, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if stdout:
		return sp.stdout.read()
	if value:
		return sp.returncode



def command_exists(c):
	""" Check if a given command exists """
	if sys.platform.startswith('linux'):
		# get path to the command
		com = command('which %s' % (c))
		return len(command('which %s' % (c))) > 0
	else:
		log.warn('Cannot determine \'%s\' existence.' % c)
		return False




def positive(string):
	""" Check if parameter represents positive state """
	return string.lower() in ['y', 'yes', 'true', 't', '1']




def negative(string):
	""" Check if parameter represents negative state """
	return string.lower() in ['n', 'no', 'false', 'f', '0']




def is_admin():
	""" Check if the actual user has administrative privileges """
	
	if sys.platform.startswith('linux'):
		# on linux check if euid is 0
		if os.geteuid() == 0:
			return True
		return False
	
	elif sys.platform.startswith('win'):
		# on Windows only admins can write to C:\Windows\temp
		if os.access(os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'temp'), os.W_OK):
			return True
		return False
	else:
		log.warn('Cannot check root privileges, platform is not fully supported (%s).' % sys.platform)




def natural_sort(data):
	return sorted(data, key=lambda x: [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', x)])
