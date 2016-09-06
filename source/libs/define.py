#!/usr/bin/env python3
import os, sys, threading

appname = 'Locasploit'                                    # application name
python_version = '.'.join(map(str, sys.version_info[:3])) # python version
prompt = ' >  '                                           # current prompt string
module_objects = []                                       # temporary list for module loading
modules = {}                                              # dictionary of all modules
active_module = None                                      # currently active module
#from_input_file = False                                   # commands provided from input file
commands = []                                             # list of commands to execute
command_history = []                                      # history of commands
module_history = []                                       # history of selected modules
active_session = None                                     # active session (for DB purposes)

dicts = {}                                                # dictionaries (for crypto, cracking etc.)
if 'tb' not in vars():
    tb = {}                                             ## temporary base, initialized in tb.py

main_thread = threading.current_thread()
if 'scheduler' not in vars():
    scheduler = None                                      # thread scheduler, initialized in scheduler.py

if 'db' not in vars():
    db = None                                             # dict of .db handlers, initialized in db.py

if sys.platform.startswith('linux'):                      # global parameters
    import pwd
    global_parameters = {
        #'USER': pwd.getpwuid(os.getuid())[0], 
        #'HOME': pwd.getpwuid(os.getuid())[5],
        #'SHELL': pwd.getpwuid(os.getuid())[6], 
        'USER': os.environ['SUDO_USER'] if 'SUDO_USER' in os.environ 
                else os.environ['USER'],
        'HOME': os.environ['HOME'],
        'SHELL': os.environ['SHELL'],
        'ENVPATH': os.environ['PATH'],
        'TEMPDIR': '/tmp',
        'SYSTEMROOT': '/',
        'ROOT' : pwd.getpwuid(0)[0],
        'ROOT_HOME' : pwd.getpwuid(0)[5],
        
    }
elif sys.platform.startswith('win'):
    global_parameters = {
        'USER': os.environ['USERNAME'],
        'HOME': os.environ['HOMEPATH'],
        'TEMPDIR': os.environ['TEMP'],
        'WINDIR': os.environ['WINDIR'],
        'SYSTEMROOT': os.environ['SYSTEMROOT'],
        'ENVPATH': os.environ['PATH'],
    }
else:
    global_parameters = {}

global_parameters['ACTIVEROOT'] = '/'                    # unless changed, all info treated as on local OS

# Miscellaneous constants
POSITIVE_STRINGS = ['y', 'yes', 'true', 't', '1', '+']
NEGATIVE_STRINGS = ['n', 'no', 'false', 'f', '0', '-']
QUIT_STRINGS = ['exit', 'exit()', 'quit', 'quit()', 'q', 'back']

# module check results
CHECK_SUCCESS = 2
CHECK_PROBABLY = 1
CHECK_NOT_SUPPORTED = 0
CHECK_UNLIKELY = -1
CHECK_FAILURE = -2

DB_ERROR = -1                                           # returned by db.execute if an exception is thrown
IO_ERROR = -1

DBNOTE_UNIQUE = 2                                       # note is added if no note with same text and session exists
DBFILE_NOCONTENT = 3                                    # only file info is added into database, not the content

USERS_UNIX = 1                                          # user info in [name, password, uid, gid, comment, home, shell] format
USERS_UNIXLIKE = 2                                      # user info in USERS_UNIX format + admin (not determined from uid)
