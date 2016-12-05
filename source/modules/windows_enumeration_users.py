#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'windows.enumeration.users'
        self.short_description = 'This module dumps info about users.'
        self.references = [
        ]
        self.date = '2016-08-09'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'windows',
            'user', 
            'users',
            'enumeration',
        ]
        
        
        self.description = ''
        
        self.dependencies = {

        }
        self.changelog = """
1.0 - only local groups are analyzed
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
        # can import win32net?
        try:
            import win32net
        except:
            # TODO implement other methods
            if not silent:
                log.err('Cannot import win32net module.')
            result = CHECK_FAILURE
        # is the system windows?
        if 'win' not in get_system_type_from_active_root(activeroot):
            if not silent:
                log.err('Target system must belong to the Windows family.')
            result = CHECK_FAILURE
        return result

    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        import win32net
        ip = get_address_from_active_root(activeroot)
        if ip is None:
            log.err('Cannot get proper address for active root.')
            return None
       
        # get all users
        rh = 0
        while True:
            users = win32net.NetUserEnum(ip, 1, rh)
            unixusers = [] # prepare list of unix-style values
            for user in users[0]:
                username = user['name']
                uid = str(win32net.NetUserGetInfo(ip, username, 4)['user_sid'])[6:].split('-')[-1]
                admin = is_admin(username, self.parameters['ACTIVEROOT'].value)
                if not silent:
                    if admin:
                        log.ok('User %s - %s (Administrator)' % (uid, username))
                    else:
                        log.ok('User %s - %s' % (uid, username))
                unixusers.append([username, None, uid, None, None, None, None, admin])
                #db['analysis'].add_user(activeroot, uid, username, admin)
            result = db['analysis'].add_users(activeroot, unixusers, USERS_UNIXLIKE)
            if result == DB_ERROR:
                log.err('Cannot insert users into DB.')
            else:
                if not silent:
                    log.ok('%d users added/updated.' % (len(unixusers)))
                #groups = win32net.NetLocalGroupEnum(ip, 1)
                #groups = win32net.NetUserGetLocalGroups(ip, username, 2)
                # TODO how to get GID????
                #for group in groups[0]:
                #    print(group)
                #    print(win32net.NetLocalGroupGetInfo(ip, group['name'], 1))
                
                # insert ug
            if rh == 0:
                break
            
        return None

lib.module_objects.append(Module())
