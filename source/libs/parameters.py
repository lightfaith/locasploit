#!/usr/bin/env python3
from source.libs.include import *

class Parameter:
	def __init__(self, value='', mandatory=True, description=''):#, kb=False, dependency=False):
		self.value=value 				# value
		self.mandatory=mandatory		# if it must be defined
		self.description=description	# description
