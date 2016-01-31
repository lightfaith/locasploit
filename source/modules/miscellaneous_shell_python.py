#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
	def __init__(self):
		self.authors = [
			Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
		]
		
		self.name = 'miscellaneous.shell.python'
		self.short_description = 'Runs any python command.'
		self.references = [
		]
		
		self.date = '2016-01-27'
		self.license = 'GNU GPLv2'
		self.version = '1.0'
		self.tags = [
			'shell',
			'interpreter',
			'python',
		]
		
		self.description = """
This module uses Python's exec() function to execute any commands. These will run in the context of the framework, so, you know, do not break anything.
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
		
		if not silent:
			ends = ['exit', 'exit()', 'quit', 'quit()', 'q', 'back']
			end_string = ', '.join( ends[:-1]) + ' or ' + ends[-1]
			log.info('Type %s to exit.' % (end_string))
		lib.prompt = '>>> '
		
		while True:
			if not silent:
				log.prompt()
			# check input commands first
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
				exec(line)
			except:
				log.err(sys.exc_info()[1])
				
		lib.prompt = old_prompt
		# # # # # # # #
		return None


lib.module_objects.append(Module())
