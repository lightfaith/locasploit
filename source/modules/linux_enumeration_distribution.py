#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
	def __init__(self):
		self.authors = [
			Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
		]
		
		self.name = 'linux.enumeration.distribution'
		self.short_description = 'Extracts information about current distro.'
		self.references = [
			'https://blog.g0tmi1k.com/2011/08/basic-linux-privilege-escalation/'
		]
		
		self.date = '2016-01-25'
		self.license = 'GNU GPLv2'
		self.version = '1.0'
		self.tags = [
			'linux',
			'distribution',
			'issue',
			'release',
			'/etc/issue',
		]
		
		self.description = 'This module extracts various info about current distribution from specific files (namely /etc/issue and /etc/*-release).'
		self.kb_access = [
			'DISTRIBUTION',
			'ISSUE',
			'LSB-RELEASE',
			'OS-RELEASE',
			'REDHAT-RELEASE',
		]
		self.dependencies = {

		}
		self.changelog = ''
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
		
		if os.access('/etc', os.R_OK) and os.access('/etc', os.X_OK):
			# get /etc/issue
			if os.access('/etc/issue', os.R_OK):
				with open('/etc/issue', 'r') as f:
					result = f.read()
					lib.kb.add('DISTRIBUTION ISSUE', result)
					if not silent:
						log.ok('/etc/issue:')
						for x in result.splitlines():
							log.writeline(x)
			else:
				log.err('/etc/issue cannot be accessed.')
		
			# get /etc/*-release
			release_files = [x for x in os.listdir('/etc/') if re.match('.*-release$', x)]
			for x in release_files:
				with open('/etc/' + x, 'r') as f:
					result = f.read()
					lib.kb.add('DISTRIBUTION %s' % (x.upper()), result)
					if not silent:
						log.ok('%s:' % x)
						for l in result.splitlines():
							log.writeline(l)
		else:
			log.err('/etc cannot be accessed.')
		# # # # # # # #
		return None
	

lib.module_objects.append(Module())
