#!/usr/bin/env python
#from source.lib.include import *
#from source.lib.parameters import *
from _generic_plugin import *

class Module(GenericModule):
	def __init__(self):
		self.authors = [
			Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='badsulog.blogspot.com'),
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
		]
		self.dependencies = {

		}
		self.changelog = ''
		self.ResetParameters()

	def ResetParameters(self):
		self.parameters = {
		}

	def Check(self):
		self.kb_init()
		log.info('This module does not support check.')
	
	def Run(self):
		self.kb_init()

		# # # # # # # #
		struct = kb['DISTRIBUTION']
		
		if os.path.isdir('/etc'):
			if os.path.exists('/etc/issue'):
				# get /etc/issue
				with open('/etc/issue', 'r') as f:
					self.kb_save(struct, 'ISSUE', f.read(), '/etc/issue:')
			else:
				log.err('/etc/issue does not exist.')
			# get /etc/*-release
			release_files = [x for x in os.listdir('/etc/') if re.match('.*-release$', x)]
			for x in release_files:
				with open('/etc/' + x, 'r') as f:
					self.kb_save(struct, x.upper(), f.read(), '/etc/%s:' % (x))
		else:
			log.err('/etc does not exist.')
		# # # # # # # #
		pass
	

lib.module_objects.append(Module())
