#!/usr/bin/env python
from _generic_plugin import *

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

		self.ResetParameters()

	def ResetParameters(self):
		self.parameters = {
			'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output', kb=False, dependency=False),
		}

	def Check(self):
		log.info('This module does not support check.')
	
	def Run(self):
		silent = positive(self.parameters['SILENT'].value)
		# # # # # # # #
		old_prompt = lib.prompt
		if lib.python_version[0] == '2':
			func = raw_input
		elif lib.python_version[0] == '3':
			func = input
		else:
			log.err('Invalid PYTHON_VERSION (%s).' % lib.python_version)
			return

		ends = ['exit', 'exit()', 'quit', 'quit()', 'q', 'back']
		end_string = ', '.join(map(log.Color.bold, ends[:-1])) + ' or ' + log.Color.bold(ends[-1])
		if not silent:
			log.info('Type %s to exit.' % (end_string))
		if lib.global_parameters['ROOT'] == lib.global_parameters['USER']:
			lib.prompt = '  # '
		else:
			lib.prompt = '  $ '
		
		while True:
			if not silent:
				log.prompt()
			# check input_commands
			if len(lib.input_commands) > 0:
				line = lib.input_commands[0]
				del lib.input_commands[0]
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
