#!/usr/bin/env python
from include import *

class Color:
	PURPLE = '\033[95m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	END = '\033[0m'
	BOLD = "\033[1m"

	@staticmethod
	def purple(string=''):
		return Color.PURPLE + string + Color.END
	@staticmethod
	def blue(string=''):
		return Color.BLUE + string + Color.END
	@staticmethod
	def green(string=''):
		return Color.GREEN + string + Color.END
	@staticmethod
	def yellow(string=''):
		return Color.YELLOW + string + Color.END
	@staticmethod
	def red(string=''):
		return Color.RED + string + Color.END
	@staticmethod
	def bold(string=''):
		return Color.BOLD + string + Color.END

def prompt():
	sys.stdout.write(Color.bold(Color.purple(lib.prompt)))

def write(string=''):
	sys.stdout.write('    %s' % str(string))

def writeline(string=''):
	print '    %s' % str(string)

def attach(string=''):
	sys.stdout.write(str(string))

def attachline(string=''):
	print str(string)

def info(string=''):
	print '%s %s' % (Color.bold(Color.blue('[.]')), string)

def ok(string=''):
	print '%s %s' % (Color.bold(Color.green('[+]')), string)

def warn(string=''):
	print '%s %s' % (Color.bold(Color.yellow('[!]')), string)

def err(string=''):
	print '%s %s' % (Color.bold(Color.red('[-]')), string)


