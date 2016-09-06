#!/usr/bin/env python3
import os,  argparse
#import sys, importlib, re
from source.libs.define import *
from source.libs.parameters import *
from source.libs.commands import *
from source.libs.include import *
import source.libs.log as log

# program arguments
parser = argparse.ArgumentParser(prog='locasploit', description='Local enumeration and exploitation framework.')
parser.add_argument('-c', type=str, help = 'Load the specified configuration file', nargs=1, metavar='input_file', dest='input_file')
try:
    args = parser.parse_args()
except SystemExit:
    exit_program(None, None)



def main():
    global_parameters['UUID'] = get_local_uuid()
    lib.active_session = db['analysis'].get_last_session()
    db['analysis'].create_session(lib.active_session)
    log.info('Currently working with session #%d.' % lib.active_session)
    # check if already admin
    if is_admin():
        log.ok('Administrator privileges already granted on \'%s\'.' % (global_parameters['ACTIVEROOT']), dbnote=DBNOTE_UNIQUE)
    # if input from file, load commands into queue
    if args.input_file is not None:
        if os.access(args.input_file[0], os.R_OK):
            with open(args.input_file[0], 'r') as f:
                lib.commands = f.read().splitlines()
                lib.from_input_file = True
        else:
            log.err('Input file cannot be read!')

    # run all input commands
    while len(lib.commands) > 0:
        c = lib.commands[0]
        del lib.commands[0]
        if lib.from_input_file:
            log.prompt()            # print prompt
            log.attachline(c)       # print command
        execute_command(c)          # run the command

    lib.from_input_file = False
        
    # main loop
    while True:
        # input from stdin
        log.prompt()
        if lib.python_version[0] == '2':
            func = raw_input
        elif lib.python_version[0] == '3':
            func = input
        else:
            log.err('Undefined python version (%s).' % lib.python_version)
            break
        # add command into queue
        #lib.commands.append(func())
        execute_command(func())
    # end of main program loop

# ###################
# program starts here
#
load_modules()
"""
try:
    load_dicts()
except:
    pass
"""
main()

