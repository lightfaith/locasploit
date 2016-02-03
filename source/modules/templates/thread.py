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
			'SILENT': Parameter(value='yes', mandatory=True, description='Suppress the output'),
			'BACKGROUND' : Parameter(value='yes', mandatory=True, description='yes = run in background, no = wait for it...'),
			'TIMEOUT' : Parameter(value='60', mandatory=True, description='Number of seconds to run'),
		}

	def check(self):
		silent = positive(self.parameters['SILENT'].value)
		if not silent:
			log.info('This module does not support check.')
		return False
	
	def run(self):
		silent = positive(self.parameters['SILENT'].value)
		if not positive(self.parameters['BACKGROUND'].value) and not negative(self.parameters['BACKGROUND'].value):
			log.err('Bad %s value: %s.', 'BACKGROUND', self.parameters['BACKGROUND'].value)
			return None
		if not self.parameters['TIMEOUT'].value.isdigit() or int(self.parameters['TIMEOUT'].value) < 0:
			log.err('Bad timeout value: %d', int(self.parameters['TIMEOUT'].value))
			return None
		# # # # # # # #
		
		t = T(silent, int(self.parameters['TIMEOUT'].value))
		t.start()
		if positive(self.parameters['BACKGROUND'].value):
			return t
		t.join()
		return None
		# # # # # # # #
	
class T(threading.Thread):
	def __init__(self, silent, timeout):
		threading.Thread.__init__(self)
		self.silent = silent
		self.timeout = timeout
		self.terminate = False
	
	def run(self):
		
	def stop(self):
		self.terminate = True

lib.module_objects.append(Module())

