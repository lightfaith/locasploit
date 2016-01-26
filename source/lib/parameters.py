#!/usr/bin/env python
from include import *

class Parameter:
	def __init__(self, value='', mandatory=True, description=''):
		self.value=value
		self.mandatory=mandatory
		self.description=description
