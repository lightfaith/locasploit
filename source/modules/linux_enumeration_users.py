#!/usr/bin/env python
from source.lib.include import *
from source.lib.parameters import *
from _generic_plugin import *

class Module(GenericModule):
	def __init__(self):
		self.authors = [
			Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='badsulog.blogspot.com'),
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
			'/etc/passwd'
		]
		
		
		self.description = ''
		self.kb_access = [

		]
		self.dependencies = {

		}
		self.changelog = ''

		self.ResetParameters()

	def ResetParameters(self):
		self.parameters = {
			'FILE': Parameter(value='/etc/passwd', mandatory=True, description='File to parse'),
		}

	def Check(self):
		log.warn('This module does not support check.')

	def Run(self):
		
		# FILL IN YOUR CODE HERE
		pass

lib.module_objects.append(Module())
