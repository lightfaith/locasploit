#!/usr/bin/env python

from source.lib.include import *
import source.lib.parameters
from source.lib.author import *

kb = lib.kb

class GenericModule():
	#name = 'generic_module'
	def __init__(self):
		self.kb_access = []
	#short_description = 'This module is parent of all module, do not use. For template use any of the other modules.'

	def Run(self):
		print '[!] You should not run this module!'

	def kb_init(self):
		for x in self.kb_access:
			if x not in kb:
				kb[x] = {}
	
	def kb_save(self, struct, key, content, desc):
		if content is not None and len(content)>0:
			log.ok(desc)
			for l in content.splitlines():
				log.writeline(l)
			struct[key] = content
