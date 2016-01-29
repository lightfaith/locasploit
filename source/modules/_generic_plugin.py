#!/usr/bin/env python

from source.lib.include import *
from source.lib.parameters import *
from source.lib.author import *

kb = lib.kb

# DO NOT USE THIS MODULE, JUST INHERIT
class GenericModule():
	def __init__(self):
		self.kb_access = []

	def Run(self):
		log.err('[!] You should not run this module!')

