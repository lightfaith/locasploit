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
			'http://man7.org/linux/man-pages/man5/passwd.5.html',
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
			#'FILE': Parameter(value='/etc/passwd', mandatory=True, description='File to parse'),
		}

	def Check(self):
		log.info('This module does not support check.')
	
	def Run(self):
		self.kb_init()

		# # # # # # # #
		struct = kb['DISTRIBUTION']
		if os.path.isdir('/etc'):
			if os.path.exists('/etc/issue'):
				with open('/etc/issue', 'r') as f:
					self.kb_save(struct, 'ISSUE', f.read(), '/etc/issue:')
			#		content = f.read()
			#	if content is not None and len(content)>0:
			#		log.ok('/etc/issue:')
			#		log.writeline(content)
			#		kb['DISTRIBUTION']['ISSUE'] = content
			else:
				log.err('/etc/issue does not exist.')
			release_files = [x for x in os.listdir('/etc/') if re.match('.*-release$', x)]
			for x in release_files:
				with open('/etc/' + x, 'r') as f:
					self.kb_save(struct, x.upper(), f.read(), '/etc/%s:' % (x))
		else:
			log.err('/etc does not exist.')
		# # # # # # # #
		pass
	

lib.module_objects.append(Module())
