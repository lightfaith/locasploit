#!/usr/bin/env python3

from source.libs.include import *
from source.libs.parameters import *
from source.libs.author import *

kb = lib.kb

# DO NOT USE THIS MODULE, JUST INHERIT
class GenericModule():
	def __init__(self):
		self.kb_access = []

	def Run(self):
		log.err('[!] You should not run this module!')

