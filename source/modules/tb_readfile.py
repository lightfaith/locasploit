#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'tb.readfile'
        self.short_description = 'Loads a specified file into Temporary Base.'
        self.references = [
            '',
        ]
        
        self.date = '2016-02-03'
        self.license = 'GNU GPLv2'
        self.version = '1.1'
        self.tags = [
            'TB', 'temporary', 'base',
            'read', 'load', 'file', 'content',
        ]
        self.description = """
Loads a specified file into Temporary base.
User must provide:
    PATH    path to file
    KEY     part of the resulting KB key

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
            'ACTIVEROOT': Parameter(mandatory=True, description='System to work with'),
            'INPUTFILE': Parameter(value='', mandatory=True, description='Path to the input file'),
            'KEY': Parameter(value='', mandatory=True, description='TB key'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        inputfile = self.parameters['INPUTFILE'].value
        if not io.can_read(activeroot, inputfile):
            if not silent:
                log.err('Cannot read \'%s\'' % (inputfile))
            return CHECK_FAILURE
        return CHECK_SUCCESS
    
    def run(self):
        inputfile = self.parameters['INPUTFILE'].value
        activeroot = self.parameters['ACTIVEROOT'].value
        key = self.parameters['KEY'].value
        f = io.read_file(activeroot, inputfile, usedb=False)
        if f == IO_ERROR:
            log.err('Cannot access \'%s\'.' % (inputfile))
            return None
        lib.tb[key] = f
        return None
    

lib.module_objects.append(Module())
