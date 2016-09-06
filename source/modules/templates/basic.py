#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='', email='', web=''),
        ]
        
        self.name = 'template'
        self.short_description = 'Serves as a module template.'
        self.references = [
            '',
        ]
        self.date = '2999-12-31'
        self.license = 'GNU GPLv2'
        self.version = '0.0'
        self.tags = [
            'template',
        ]
        self.description = """
This module is designed to be used as a template for new modules. 
Need help with this madness? Check the "basic_commented" module.
"""
        
        self.db_access = [
            #'USERS',
        ]
        
        self.dependencies = {
            #'linux.enumeration.distribution': '1.0',
        }
        self.changelog = """
"""

        self.reset_parameters() 

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'ACTIVEROOT': Parameter(mandatory=True, description='System to work with'),
        }

    def check(self, silent=None):
        # CHECK_SUCCESS       - this module will do exactly what it is designed for (e.g. successful exploit)
        # CHECK_PROBABLY      - it will probably work
        # CHECK_NOT_SUPPORTED - nothing can be checked, but it may work
        # CHECK_UNLIKELY      - module can be executed, but it will probably fail (e.g. exploit against hardened system)
        # CHECK_FAILURE       - module cannot be executed (missing files, bad parameters etc.)
        
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        result = CHECK_NOT_SUPPORTED
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        # # # # # # # #
        # Define your code here
        log.ok('Template module says: "Hello World!"')
        return None 
    

lib.module_objects.append(Module())
