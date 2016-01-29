#!/usr/bin/env python
from _generic_plugin import *

class Module(GenericModule):
	def __init__(self):
		self.authors = [
			Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
		]
		
		self.name = 'network.enumeration.interfaces'
		self.short_description = 'Detects network interfaces.'
		self.references = [
			'',
		]
		
		self.date = '2016-01-28'
		self.license = 'GNU GPLv2'
		self.version = '1.0'
		self.tags = [
			'network',
			'enumeration',
			'interface', 'interfaces',
			'netifaces',
			'eth', 'eth0', 'l0', 'wlan', 'wlan0', 'loopback'
			'NIC',

		]
		self.description = """
This module detects local network interfaces and writes them into the Knowledge Base. It needs 'netifaces' to work.
"""
		self.kb_access = [
			'NETWORK',
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
#		if len([x for x in command('dpkg -s python-netifaces').splitlines() if x[:7] == 'Status:' and 'installed' in x])!=1:
#			log.err('Python-netifaces is needed to run this module.')
#			return None			
		try:
			import netifaces as n
		except:
			log.err('Python-netifaces is needed to run this module.')
			return None

		ifs = n.interfaces()
		result = {}
		for iface in  ifs:
			afs = {}
			for ad in n.ifaddresses(iface):
				afs[n.address_families[ad]] = n.ifaddresses(iface)[ad]
			result[iface] = afs
		
		#output
		if not silent:
			for interface in result:			
				log.ok('%s:' % interface)
				for afamily in result[interface]:
					log.ok('    %s:' %afamily)
					for addressid in range(0, len(result[interface][afamily])):
						log.ok('        address %d:' % addressid)
						address = result[interface][afamily][addressid]
						for key in address:
							log.ok('            %s = %s' % (key, address[key]))

		lib.kb.add('NETWORK', 'INTERFACES', result)
		# # # # # # # #
		return None
	

lib.module_objects.append(Module())
