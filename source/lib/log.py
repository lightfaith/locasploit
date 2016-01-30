#!/usr/bin/env python
from include import *

if sys.platform.startswith('win'):
	from ctypes import windll
	STD_INPUT_HANDLE = -10
	STD_OUTPUT_HANDLE = -11
	STD_ERROR_HANDLE = -12
	win_stdout_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)


loglock = threading.Lock()
should_newline = True

class Color:
	# ANSI CODES (should work for everythin except Windows)
	
	PURPLE = '\033[95m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	END = '\033[0m'
	BOLD = "\033[1m"
	
	# WIN FLAGS FOR WinAPI
	
	WIN_WIN_FG_BLACK = 0x0000
	WIN_FG_BLUE      = 0x0001
	WIN_FG_GREEN     = 0x0002
	WIN_FG_CYAN      = 0x0003
	WIN_FG_RED       = 0x0004
	WIN_FG_MAGENTA   = 0x0005
	WIN_FG_YELLOW    = 0x0006
	WIN_FG_GREY      = 0x0007
	WIN_FG_INTENSITY = 0x0008

	WIN_BG_BLACK     = 0x0000
	WIN_BG_BLUE      = 0x0010
	WIN_BG_GREEN     = 0x0020
	WIN_BG_CYAN      = 0x0030
	WIN_BG_RED       = 0x0040
	WIN_BG_MAGENTA   = 0x0050
	WIN_BG_YELLOW    = 0x0060
	WIN_BG_GREY      = 0x0070
	WIN_BG_INTENSITY = 0x0080


	@staticmethod
	def set(color=''):
		if sys.platform.startswith('win'):
			if color == Color.PURPLE:
				windll.kernel32.SetConsoleTextAttribute(win_stdout_handle, Color.WIN_FG_MAGENTA | Color.WIN_FG_INTENSITY)
			elif color == Color.RED:
				windll.kernel32.SetConsoleTextAttribute(win_stdout_handle, Color.WIN_FG_RED | Color.WIN_FG_INTENSITY)
			elif color == Color.GREEN:
				windll.kernel32.SetConsoleTextAttribute(win_stdout_handle, Color.WIN_FG_GREEN | Color.WIN_FG_INTENSITY)
			elif color == Color.BLUE:
				windll.kernel32.SetConsoleTextAttribute(win_stdout_handle, Color.WIN_FG_BLUE | Color.WIN_FG_INTENSITY)
			elif color == Color.YELLOW:
				windll.kernel32.SetConsoleTextAttribute(win_stdout_handle, Color.WIN_FG_YELLOW | Color.WIN_FG_INTENSITY)
			else:
				pass # leave as is
		else: # really everything?
			sys.stdout.write(color)
	
	@staticmethod
	def reset():
		if sys.platform.startswith('win'):
			windll.kernel32.SetConsoleTextAttribute(win_stdout_handle, Color.WIN_FG_GREY)
		else: # really everything?
			sys.stdout.write(Color.END)
			
#	@staticmethod
#	def purple(string=''):
#		if sys.platform.startswith('win'):
#		return Color.PURPLE + string + Color.END
#	@staticmethod
#	def blue(string=''):
#		return Color.BLUE + string + Color.END
#	@staticmethod
#	def green(string=''):
#		return Color.GREEN + string + Color.END
#	@staticmethod
#	def yellow(string=''):
#		return Color.YELLOW + string + Color.END
#	@staticmethod
#	def red(string=''):
#		return Color.RED + string + Color.END
#	@staticmethod
#	def bold(string=''):
#		return Color.BOLD + string + Color.END

Color.reset()

def prompt():
	loglock.acquire()
	threadline()
	Color.set(Color.PURPLE)
	Color.set(Color.BOLD)
	sys.stdout.write(lib.prompt.expandtabs(4))
	Color.reset()
	loglock.release()

def write(string='', *colors):
	loglock.acquire()
	threadline()
	for color in colors:
		Color.set(color)
	sys.stdout.write('    %s'.expandtabs(4) % str(string))
	Color.reset()
	loglock.release()

def writeline(string='', *colors):
	loglock.acquire()
	threadline()
	for color in colors:
		Color.set(color)
	sys.stdout.write('    %s\n'.expandtabs(4) % str(string))
	Color.reset()
	loglock.release()

def attach(string='', *colors):
	loglock.acquire()
	threadline()
	for color in colors:
		Color.set(color)
	sys.stdout.write('%s'.expandtabs(4) % str(string))
	Color.reset()
	loglock.release()

def attachline(string='', *colors):
	loglock.acquire()
	threadline()
	for color in colors:
		Color.set(color)
	sys.stdout.write('%s\n'.expandtabs(4) % str(string))
	Color.reset()
	loglock.release()

def info(string=''):
	loglock.acquire()
	threadline()
	Color.set(Color.BLUE)
	Color.set(Color.BOLD)
	sys.stdout.write('[.] ')
	Color.reset()
	sys.stdout.write('%s\n'.expandtabs(4) % str(string))
	loglock.release()

def ok(string=''):
	loglock.acquire()
	threadline()
	Color.set(Color.GREEN)
	Color.set(Color.BOLD)
	sys.stdout.write('[+] ')
	Color.reset()
	sys.stdout.write('%s\n'.expandtabs(4) % str(string))
	loglock.release()

def warn(string=''):
	loglock.acquire()
	threadline()
	Color.set(Color.YELLOW)
	Color.set(Color.BOLD)
	sys.stdout.write('[!] ')
	Color.reset()
	sys.stdout.write('%s\n'.expandtabs(4) % str(string))
	loglock.release()

def err(string=''):
	loglock.acquire()
	threadline()
	Color.set(Color.RED)
	Color.set(Color.BOLD)
	sys.stdout.write('[-] ')
	Color.reset()
	sys.stdout.write('%s\n'.expandtabs(4) % str(string))
	loglock.release()

def threadline():
	if lib.main_thread is not threading.current_thread() and log.should_newline:
		log.should_newline = False
		sys.stdout.write('\n')
	else:
		log.should_newline = True
	
