#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'linux.enumeration.users'
        self.short_description = 'This module dumps info about users.'
        self.references = [
        ]
        self.date = '2016-08-11'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'linux',
            'user', 
            'users',
            'enumeration',
        ]
        
        
        self.description = ''
        self.db_access = [
        'USER', #'GROUP', 'UG',
        ]
        self.dependencies = {

        }
        self.changelog = """
1.0 - only local users and groups are analyzed
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'ACTIVEROOT': Parameter(mandatory=True, description='System to work with'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        result = CHECK_SUCCESS
        # is the system linux?
        if not get_system_type_from_active_root(activeroot).startswith('lin'):
            if not silent:
                log.warn('Target system does not belong to Linux family.')
            result = CHECK_UNLIKELY
        # can open /etc/passwd?
        if not io.can_read(activeroot, '/etc/passwd'):
            if not silent:
                log.err('Cannot open /etc/passwd file.')
            result = CHECK_FAILURE
        # can open /etc/group?
        #if not io.can_read(activeroot, '/etc/group'):
        #    if not silent:
        #        log.err('Cannot open /etc/group file.')
        #    result = CHECK_FAILURE
        return result

    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        
        ip = get_address_from_active_root(activeroot)
        if ip is None:
            log.err('Cannot get proper address for active root.')
            return None
        
        users = io.read_file(activeroot, '/etc/passwd')
        if users == IO_ERROR:
            return None
        users = [u.split(':') for u in users.splitlines() if len(u.split(':')) == 7]
        result = db['analysis'].add_users(activeroot, users, USERS_UNIX)
        if result == DB_ERROR:
            log.err('Cannot insert users into database.')
        if not silent:
            log.ok('%d users added/updated.' % (len(users)))
        return None

lib.module_objects.append(Module())

