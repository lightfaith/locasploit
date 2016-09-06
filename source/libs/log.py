#!/usr/bin/env python3
import source.libs.define as lib
#from source.libs.db import *
import sys, threading

if sys.platform.startswith('win'):
    from ctypes import windll
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12
    win_stdout_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)


loglock = threading.Lock()
should_newline = True # threads use this to print to newlines

class Color:
    # ANSI CODES (should work for everything except Windows)
    
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
        # color will be set with regards to platform
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
        else:
            # TODO really everything?
            print(color, end='')

    @staticmethod
    def reset():
        # revert any color settings with regards to platform
        if sys.platform.startswith('win'):
            windll.kernel32.SetConsoleTextAttribute(win_stdout_handle, Color.WIN_FG_GREY)
        else: # TODO really everything?
            print(Color.END, end='')
            
# at start set default colors
Color.reset()

def prompt():
    # print prompt string
#   loglock.acquire()                         # acquire screen writing lock
    threadline()                              # print newline if not main thread and main thread printed last
    Color.set(Color.PURPLE)                   # set colors
    Color.set(Color.BOLD)
    print(lib.prompt.expandtabs(4), end='')   # print prompt
    Color.reset()                             # reset colors
#   loglock.release()                         # release the lock

def write(string='', *colors):
    # write with indent 4, no newline
    if type(string) is bytes:
        string = string.decode('utf-8')
#   loglock.acquire()
    threadline()
    for color in colors:
        Color.set(color)
    print('    %s'.expandtabs(4) % str(string), end='')
    Color.reset()
#   loglock.release()

def writeline(string='', *colors):
    # write with indent 4, newline
    if type(string) is bytes:
        string = string.decode('utf-8')
#   loglock.acquire()
    threadline()
    for color in colors:
        Color.set(color)
    print('    %s'.expandtabs(4) % str(string))
    Color.reset()
#   loglock.release()

def attach(string='', *colors):
    # write with no indent, no newline
    if type(string) is bytes:
        string = string.decode('utf-8')
#   loglock.acquire()
    threadline()
    for color in colors:
        Color.set(color)
    print('%s'.expandtabs(4) % str(string), end='')
    Color.reset()
#   loglock.release()

def attachline(string='', *colors):
    # write with no indent, newline
    if type(string) is bytes:
        string = string.decode('utf-8')
#   loglock.acquire()
    threadline()
    for color in colors:
        Color.set(color)
    print('%s'.expandtabs(4) % str(string))
    Color.reset()
#   loglock.release()

def info(string='', end=True, dbnote=False):
    # print line with blue [.]
    if type(string) is bytes:
        string = string.decode('utf-8')
#   loglock.acquire()
    threadline()
    Color.set(Color.BLUE)
    Color.set(Color.BOLD)
    print('[.] ', end='')
    Color.reset()
    if end:
        print('%s'.expandtabs(4) % str(string))
    else:
        print('%s'.expandtabs(4) % str(string), end='')
    if dbnote == True:
        lib.db['analysis'].add_note(string, '.', lib.active_session)
    elif dbnote == lib.DBNOTE_UNIQUE:
        lib.db['analysis'].add_note(string, '.', lib.active_session, dbnote=True)
#   loglock.release()

def ok(string='', end=True, dbnote=False):
    # print line with green [+]
    if type(string) is bytes:
        string = string.decode('utf-8')
#   loglock.acquire()
    threadline()
    Color.set(Color.GREEN)
    Color.set(Color.BOLD)
    print('[+] ', end='')
    Color.reset()
    if end:
        print('%s'.expandtabs(4) % str(string))
    else:
        print('%s'.expandtabs(4) % str(string), end='')
    if dbnote == lib.DBNOTE_UNIQUE:
        lib.db['analysis'].add_note(string, '+', unique=True)
    elif dbnote == True:
        lib.db['analysis'].add_note(string, '+')
    
#   loglock.release()

def warn(string='', end=True, dbnote=False):
    # print line with yellow [!]
    if type(string) is bytes:
        string = string.decode('utf-8')
#   loglock.acquire()
    threadline()
    Color.set(Color.YELLOW)
    Color.set(Color.BOLD)
    print('[!] ', end='')
    Color.reset()
    if end:
        print('%s'.expandtabs(4) % str(string))
    else:
        print('%s'.expandtabs(4) % str(string), end='')
    if dbnote == True:
        lib.db['analysis'].add_note(string, '!', lib.active_session)
    elif dbnote == lib.DBNOTE_UNIQUE:
        lib.db['analysis'].add_note(string, '!', lib.active_session, dbnote=True)
#   loglock.release()

def err(string='', end=True, dbnote=False):
    # print line with red [-]
    if type(string) is bytes:
        string = string.decode('utf-8')
#   loglock.acquire()
    threadline()
    Color.set(Color.RED)
    Color.set(Color.BOLD)
    print('[-] ', end='')
    Color.reset()
    if end:
        print('%s'.expandtabs(4) % str(string))
    else:
        print('%s'.expandtabs(4) % str(string), end='')
    if dbnote == True:
        lib.db['analysis'].add_note(string, '-', lib.active_session)
    elif dbnote == lib.DBNOTE_UNIQUE:
        lib.db['analysis'].add_note(string, '-', lib.active_session, dbnote=True)
#   loglock.release()

def threadline():
    # print newline if not main thread and main thread printed last
    global should_newline
    if lib.main_thread is not threading.current_thread() and should_newline:
        should_newline = False
        print('')
    else:
        should_newline = True
    

def show_time(time):
    # convert number of miliseconds to h:mm:ss.sss
    if type(time) != float:
        return '/'
    hours = time / 3600
    time = time % 3600
    minutes = time / 60
    time = time % 60
    return '%d:%02d:%06.3f' % (hours, minutes, time)

