#!/usr/bin/env python
from include import *

loglock = threading.Lock()

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
	loglock.acquire()
	sys.stdout.write(Color.bold(Color.purple(lib.prompt.expandtabs(4))))
	loglock.release()

def write(string=''):
	loglock.acquire()
	sys.stdout.write('    %s'.expandtabs(4) % str(string))
	loglock.release()

def writeline(string=''):
	loglock.acquire()
	print('    %s'.expandtabs(4) % str(string))
	loglock.release()

def attach(string=''):
	loglock.acquire()
	sys.stdout.write(str(string).expandtabs(4))
	loglock.release()

def attachline(string=''):
	loglock.acquire()
	print(str(string).expandtabs(4))
	loglock.release()

def info(string=''):
	loglock.acquire()
	print('%s %s'.expandtabs(4) % (Color.bold(Color.blue('[.]')), string))
	loglock.release()

def ok(string=''):
	loglock.acquire()
	print('%s %s'.expandtabs(4) % (Color.bold(Color.green('[+]')), string))
	loglock.release()

def warn(string=''):
	loglock.acquire()
	print('%s %s'.expandtabs(4) % (Color.bold(Color.yellow('[!]')), string))
	loglock.release()

def err(string=''):
	loglock.acquire()
	print('%s %s'.expandtabs(4) % (Color.bold(Color.red('[-]')), string))
	loglock.release()


