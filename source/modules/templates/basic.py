#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
	def __init__(self):
		self.authors = [
			Author(name='', email='', web=''),
		]
		
		self.name = ''
		self.short_description = ''
		self.references = [
			'',
		]
		
		self.date = '2999-12-31'
		self.license = 'GNU GPLv2'
		self.version = '0.0'
		self.tags = [
			'',
		]
		self.description = """
This module is designed to be used as a template for new modules. 
For help with this madness, check the "template_commented" module.
"""
		self.kb_access = [
			'',
		]
		
		self.dependencies = {
			'': '',
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
		# Define your code here
		
		# # # # # # # #
		return None
	

lib.module_objects.append(Module())
