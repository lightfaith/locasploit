#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'tb.move'
        self.short_description = 'Move value in Temporary Base.'
        self.references = [
            '',
        ]
        
        self.date = '2016-08-18'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'TB', 'temporary', 'base',
            'move', 'key'
        ]
        self.description = """
This module moves TB value from KEY1 to KEY2.

Existing value will be overwritten.

"""
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
            'KEY1': Parameter(value='', mandatory=True, description='Source TB key'),
            'KEY2': Parameter(value='', mandatory=True, description='Destination TB key'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        key1 = self.parameters['KEY1'].value
        result = CHECK_SUCCESS
        if key1 not in tb:
            if not silent:
                log.err('No key \'%s\' in Temporary base.' % (key1))
            result = CHECK_FAILURE
        # key 1 exists
        return result
    
    def run(self):
        key1 = self.parameters['KEY1'].value
        key2 = self.parameters['KEY2'].value
        tb[key2] = tb[key1]
        del tb[key1]
        return None
    

lib.module_objects.append(Module())
