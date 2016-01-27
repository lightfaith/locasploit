#!/usr/bin/env python

from source.lib.include import *
from source.lib.parameters import *
from source.lib.author import *

kb = lib.kb

class GenericModule():
	#name = 'generic_module'
	def __init__(self):
		self.kb_access = []
	#short_description = 'This module is parent of all module, do not use. For template use any of the other modules.'

	def Run(self):
		print '[!] You should not run this module!'

	def kb_save(self, key, subkey, content, desc):
		if content is not None and len(content)>0:
			log.ok(desc)
			for l in content.splitlines():
				log.writeline(l)
			lib.kb.save(key, subkey, content)
