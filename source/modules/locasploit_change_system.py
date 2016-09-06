#!/usr/bin/env python3
from source.modules._generic_module import *
from source.libs.db import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'locasploit.change.system'
        self.short_description = 'Allows to change current system.'
        self.references = [
            '',
        ]
        
        self.date = '2016-07-25'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'Locasploit',
            'System',
            'root'
        ]
        self.description = """
        Allows to change active system id (current: '%s').
        
        Common system ids:
           /                  - this system
           /path/to/system    - chroot directory / extracted FS
           ssh://machine/path - NOT IMPLEMENTED
           ftp://machine/path - NOT IMPLEMENTED
           tftp://machine/path - NOT IMPLEMENTED
           http://machine/path - NOT IMPLEMENTED
           https://machine/path - NOT IMPLEMENTED
        """ % (global_parameters['ACTIVEROOT'])
        self.db_access = [
        ]
        
        self.dependencies = {
        }
        self.changelog = """
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'ACTIVEROOT': Parameter(mandatory=True, description='Which system to set'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        return CHECK_SUCCESS
    
    def run(self):
        # check parameteres
        
        global_parameters['ACTIVEROOT'] = self.parameters['ACTIVEROOT'].value
        log.ok('Current system root: \'%s\'' % (global_parameters['ACTIVEROOT']))
        # # # # # # # #
        return None

lib.module_objects.append(Module())
