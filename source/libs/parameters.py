#!/usr/bin/env python3
from source.libs.include import *

class Parameter:
	def __init__(self, value='', mandatory=True, description=''):#, kb=False, dependency=False):
		self.value=value 				# value
		self.mandatory=mandatory		# if it must be defined
		self.description=description	# description
		#self.kb=kb						# if Knowledge Base item - will be checked for existence
		#self.dependency=dependency		# if another module - will be checked for existence
