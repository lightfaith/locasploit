#!/usr/bin/env python
from _generic_plugin import *

class Module(GenericModule):
	def __init__(self):
		self.authors = [
			Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='badsulog.blogspot.com'),
		]
		
		self.name = 'linux.enumeration.kernel'
		self.short_description = 'Extracts information about current kernel.'
		self.references = [
			'https://blog.g0tmi1k.com/2011/08/basic-linux-privilege-escalation/',
		]
		
		self.date = '2016-01-25'
		self.license = 'GNU GPLv2'
		self.version = '1.0'
		self.tags = [
			'linux',
			'kernel',
			'uname',
			'vmlinuz',
			'dmesg',
		]
		
		self.description = """
This module extracts various info about the kernel.
Specifically, the following commands are issued:
	cat /proc/version
	uname -a
	uname -mrs
	rpm -q kernel
	dmesg | grep Linux
	ls /boot | grep vmlinuz-
"""
		self.kb_access = [
			'KERNEL',
		]
		self.dependencies = {

		}
		self.changelog = ''
		self.ResetParameters()

	def ResetParameters(self):
		self.parameters = {
		}

	def Check(self):
		log.info('This module does not support check.')
	
	def Run(self):

		# # # # # # # #
		if os.path.isdir('/proc'):
			if os.path.exists('/etc/issue'):
				# get /proc/version
				with open('/proc/version', 'r') as f:
					self.kb_save('KERNEL', 'PROC_VERSION', f.read(), '/proc/version:')
			else:
				log.err('/proc/version does not exist.')
		else:
			log.err('/proc does not exist.')
		# run uname -a and uname -mrs
		if command_exists('uname'):
			self.kb_save('KERNEL', 'UNAME-A', command('uname -a'), 'uname -a:')
			self.kb_save('KERNEL', 'UNAME-MRS', command('uname -mrs'), 'uname -mrs:')
		else:
			log.err('Uname cannot be executed.')
		# run rpm -q kernel
		if command_exists('rpm'):
			self.kb_save('KERNEL', 'RPM', command('rpm -q kernel'), 'rpm -q kernel:')
		else:
			log.err('Rpm cannot be executed.')
		# run dmesg | grep Linux
		if command_exists('dmesg'):
			self.kb_save('KERNEL', 'DMESG_LINUX', command('dmesg | grep Linux'), 'gmesg | grep Linux:')
		else:
			log.err('Dmesg cannot be executed.')
		# what vmlinuz?
		if os.path.isdir('/boot'):
			vmlinuzes = [x for x in os.listdir('/boot') if x[:8] == 'vmlinuz-']
			self.kb_save('KERNEL', 'VMLINUZ', '\n'.join(vmlinuzes), 'vmlinuz in /boot/:')
		else:
			log.err('/boot does not exist.')
		# # # # # # # #
		return None


lib.module_objects.append(Module())
