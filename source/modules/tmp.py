#!/usr/bin/env python
from source.lib.include import *
from source.lib.parameters import *
from _generic_plugin import *

class Module(GenericModule):
	def __init__(self):
		self.authors = [
			Author(name='Fantomass', email='N/A', web='google.com'),
			Author(name='NULL'),
		]
		
		self.name = 'tmp'
		self.short_description = 'TMP ONLY'
		self.date = '2014-01-24'
		self.license = 'GNU GPLv2'
		self.tags = ['tmp']

		self.description = ''
		self.references=[]
		self.ResetParameters()

	def ResetParameters(self):
		self.parameters = {
			'HOST': Parameter(mandatory=True, value='', description='ip'),
			'PORT': Parameter(mandatory=True,  description='port'),
			'FILE': Parameter(mandatory=False, description='file'),
			'PASS': Parameter(mandatory=False, value='a', description='pass'),


		}
		
	def Run(self):
		print '[+] Module %s has started.' % (self.name)
		
		print "parameters:"
		for i in self.parameters:
			print i, self.parameters[i].value
		print '[.] Module %s terminated.' % (self.name)

lib.module_objects.append(Module())
