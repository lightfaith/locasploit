#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
	def __init__(self):
		self.authors = [
			Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
		]
		
		self.name = 'linux.enumeration.users'
		self.short_description = 'This module dumps info about users in /etc/passwd.'
		self.references = [
			'http://man7.org/linux/man-pages/man5/passwd.5.html',
		]
		self.date = '2016-01-24'
		self.license = 'GNU GPLv2'
		self.version = '0.0'
		self.tags = [
			'linux',
			'user', 
			'users',
			'enumeration',
			'passwd',
			'/etc/passwd',
		]
		
		
		self.description = ''
		self.kb_access = [

		]
		self.dependencies = {

		}
		self.changelog = ''

		self.reset_parameters()

	def reset_parameters(self):
		self.parameters = {
			'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
			'FILE': Parameter(value='/etc/passwd', mandatory=True, description='File to parse'),
		}

	def check(self):
		silent = positive(self.parameters['SILENT'].value)
		if not silent:
			log.warn('This module does not support check.')
		return False

	def run(self):
		silent = positive(self.parameters['SILENT'].value)
		# # # # # # # #
		# FILL IN YOUR CODE HERE
		# TODO
		# # # # # # # #
		return None

lib.module_objects.append(Module())
