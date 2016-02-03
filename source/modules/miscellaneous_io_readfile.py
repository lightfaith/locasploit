#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
	def __init__(self):
		self.authors = [
			Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
		]
		
		self.name = 'miscellaneous.io.readfile'
		self.short_description = 'Loads a specified file into Knowledge Base.'
		self.references = [
			'',
		]
		
		self.date = '2016-02-03'
		self.license = 'GNU GPLv2'
		self.version = '1.0'
		self.tags = [
			'KB', 'Knowledge', 'Base',
			'read', 'load', 'file', 'content',
		]
		self.description = """
Loads a specified file into Knowledge Base.
User must provide:
    PATH    path to file
    KEY     part of the resulting KB key

Data will be saved under 'DATA > {key} > RAW' key. Any existing data under this key will be overwritten.

"""
		self.kb_access = [
			'DATA',
		]
		
		self.dependencies = {
		}
		self.changelog = """
"""

		self.reset_parameters()

	def reset_parameters(self):
		self.parameters = {
			'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
			'PATH': Parameter(value='', mandatory=True, description='Location of the input file'),
			'KEY': Parameter(value='', mandatory=True, description='Part of KB key'),
		}

	def check(self):
		silent = positive(self.parameters['SILENT'].value)
		if not silent:
			log.info('This module does not support check.')
		return False
	
	def run(self):
		silent = positive(self.parameters['SILENT'].value)
		# # # # # # # #
		# read file
		path = self.parameters['PATH'].value
		if os.access(path, os.R_OK):
			with open(path, 'r') as f:
				content = f.read()

		# write data into KB
		key = 'DATA %s RAW' % self.parameters['KEY'].value
		lib.kb.add(key, content)

		# check if successful
		if not silent:
			if lib.kb.exists(key):
				log.ok('Data successfuly added into KB.')
			else:
				log.err('Error adding data into KB.')
		# # # # # # # #
		return None
	

lib.module_objects.append(Module())
