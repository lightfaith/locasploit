#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'tb.insert'
        self.short_description = 'Loads a specified string into Temporary Base.'
        self.references = [
            '',
        ]
        
        self.date = '2016-02-03'
        self.license = 'GNU GPLv2'
        self.version = '1.1'
        self.tags = [
            'TB', 'temporary', 'base',
            'read', 'load', 'insert', 'string',
        ]
        self.description = """
Loads a specified string into Knowledge Base.
User must provide:
    STRING  desired string
    KEY     key in Temporary base

Any existing data under this key will be overwritten.

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
            'VALUE': Parameter(value='', mandatory=True, description='String value'),
            'KEY': Parameter(value='', mandatory=True, description='TB key'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        return CHECK_SUCCESS
    
    def run(self):
        lib.tb[self.parameters['KEY'].value] = self.parameters['VALUE'].value
        return None
    

lib.module_objects.append(Module())
