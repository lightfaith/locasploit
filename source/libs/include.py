#!/usr/bin/env python3
import os, sys, re, time, importlib, imp, subprocess,  signal, threading
#import logging, traceback
import source.libs.define as lib
#import source.libs.kb
import source.libs.scheduler
from source.libs.db import *
import source.libs.log as log

def exit_program(signal, frame):
    log.attachline()
    log.info('Killing all the threads...')
    # stop the scheduler (will stop all threads)
    lib.scheduler.stop()
    # wait for scheduler termination
    while lib.scheduler.isAlive():
        time.sleep(0.1)
    log.info('Cleaning databases...')
    lib.db['dict'].clean()
    # disconnect from databases
    log.info('Disconnecting from databases...')
    for dbname in lib.db.keys():
        if lib.db[dbname]:
            lib.db[dbname].close()
    log.info('%s out.' % lib.appname)
    sys.exit(0)

# run exit program on SIGINT
signal.signal(signal.SIGINT, exit_program)


def load_modules():
    """ Import modules from source/modules/ folder """
    lib.module_objects = []
    lib.modules = {}
    module_names = [x[:-3] for x in os.listdir('source/modules') if x[0]!='_' and x[-3:] == '.py']

    # import/reimport modules
    for m in module_names:
        if 'source.modules.' + m in sys.modules:
            imp.reload(sys.modules['source.modules.' + m]) # TODO deprecated?
        else:
            importlib.import_module('source.modules.' + m)
    
    # initialize modules dictionary
    for v in lib.module_objects:
        if v.name in lib.modules:
            log.warn('Duplicit module %s.' % (v.name))
        lib.modules[v.name] = v 
    
    log.info('%d modules loaded.' % (len(lib.modules)))


"""
def load_dicts():
    lib.dicts = {}
    dicts = [x for x in os.listdir('dictionaries') if x[-4:].lower() in ['.txt', '.dic']]
    for d in dicts:
        lines = []
        path = os.path.join('dictionaries', d)
        if os.access(path, os.R_OK):
            with open(path, 'r') as f:
                #print(path)
                try:
                    lines = [x.strip() for x in f.readlines()]
                except:
                    pass
                lib.dicts[d[:-4].upper()] = lines
    log.info('%d dictionaries loaded.' % (len(lib.dicts)))
"""

def natural_sort(data):
    return sorted(data, key=lambda x: [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', x)])

def command(provided_command, value=False, stdout=True):
    """ Run a given command """
    sp = subprocess.Popen(provided_command, shell=True, env={'PATH': os.environ['PATH']}, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if stdout:
        return sp.stdout.read()
    if value:
        return sp.returncode



def command_exists(activeroot, c):
    """ Check if a given command exists """
    if 'linux' in get_system_type_from_active_root(activeroot):
        # get path to the command
        com = command('which %s' % (c))
        return len(com) > 0
    else:
        log.warn('Cannot determine \'%s\' existence.' % c)
        return False


def positive(string):
    """ Check if parameter represents positive state """
    return string.lower() in lib.POSITIVE_STRINGS


def negative(string):
    """ Check if parameter represents negative state """
    return string.lower() in lib.NEGATIVE_STRINGS


def is_admin(user=lib.global_parameters['USER'], activeroot='/'):
    """ Check if the specified user has administrative privileges on given system"""
    platform = get_system_type_from_active_root(activeroot)
    ip = get_address_from_active_root(activeroot)
    if activeroot.startswith('/'):
        if platform.startswith('linux'):
            # on linux check if euid is 0
            from pwd import getpwnam
            if getpwnam(user).pw_uid == 0:
                return True
            return False
        
        elif platform.startswith('win'):
            from win32net import NetUserGetLocalGroups
            return 'Administrators' in NetUserGetLocalGroups(ip, user) # should work on remote systems too
            # on Windows only admins can write to C:\Windows\temp
            #if os.access(os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'temp'), os.W_OK):
            #    return True
            #return False
        else:
            log.warn('Cannot check root privileges, platform is not fully supported (%s).' % platform)
            return False
    else:
        log.warn('Cannot check root privileges, remote system analysis (%s) not supported yet.' % activeroot)
        return False


def get_address_from_active_root(activeroot):
    if activeroot == '/':
        return '127.0.0.1'
    if activeroot[:6] in ['ssh://', 'ftp://']:
        rest = activeroot[6:]
        if '/' in rest:
            rest = rest[:rest.index('/')]
        return rest
    # NOT IMPLEMENTED
    return None
    
def get_system_type_from_active_root(activeroot):
    if activeroot == '/':
        return sys.platform
    # for remote systems check database, else return 'unknown' (appropriate module must get the answer then)
    # NOT IMPLEMENTED
    return 'unknown'

def get_local_uuid():
    if sys.platform.startswith('lin'):
        partition = command("cat /etc/mtab | grep ' / ' | cut -d' ' -f1").splitlines()[0].decode('utf-8')
        uuid = [x[6:-1] for x in source.libs.include.command('blkid | grep %s' % (partition)).decode('utf-8').split(' ') if x.startswith('UUID="')][0]
        return uuid
    elif sys.platform.startswith('win'):
        systemdrive = lib.global_parameters['SYSTEMROOT'][0]
        uuid = command('mountvol %c: /L' % (systemdrive)).decode('utf-8')
        return uuid[uuid.index('{')+1:uuid.index('}')]
    else:
        return 'unknown'
