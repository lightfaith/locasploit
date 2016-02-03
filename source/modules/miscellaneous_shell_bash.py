#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
	def __init__(self):
		self.authors = [
			Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
		]
		
		self.name = 'miscellaneous.shell.bash'
		self.short_description = 'Runs any bash command.'
		self.references = [
		]
		
		self.date = '2016-01-27'
		self.license = 'GNU GPLv2'
		self.version = '1.0'
		self.tags = [
			'shell',
			'interpreter',
			'bash',
		]
		
		self.description = """
This module allows bash command execution.
"""
		self.kb_access = [
		]
		self.dependencies = {
		}
		self.changelog = """
"""

		self.reset_parameters()

	def reset_parameters(self):
		self.parameters = {
			'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
		}

	def check(self):
		silent = positive(self.parameters['SILENT'].value)
		if not silent:
			log.info('This module does not support check.')
		return False
	
	def run(self):
		silent = positive(self.parameters['SILENT'].value)
		# # # # # # # #
		# get input source with regards to python version
		old_prompt = lib.prompt
		if lib.python_version[0] == '2':
			func = raw_input
		elif lib.python_version[0] == '3':
			func = input
		else:
			log.err('Invalid PYTHON_VERSION (%s).' % lib.python_version)
			return

		if not silent:
			ends = ['exit', 'exit()', 'quit', 'quit()', 'q', 'back']
			end_string = ', '.join(ends[:-1]) + ' or ' + ends[-1]
			log.info('Type %s to exit.' % (end_string))

		# set console to match privileges
		if is_admin():
			lib.prompt = '  # '
		else:
			lib.prompt = '  $ '
		
		while True:
			if not silent:
				log.prompt()
			# check lib.commands
			if len(lib.commands) > 0:
				line = lib.commands[0]
				del lib.commands[0]
				if not silent:
					log.attachline(line)
			else:
				line = func()

			if line in ends:
				break
			try:
				if not silent:
					log.attach(command(line))
			except:
				log.err(sys.exc_info()[1])
				
		lib.prompt = old_prompt
		# # # # # # # #
		return None


lib.module_objects.append(Module())
