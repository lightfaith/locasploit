#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'crypto.rot'
        self.short_description = 'Performs ROT substitution enciphering.'
        self.references = [
        #   '',
        ]
        
        self.date = '2016-01-27'
        self.license = 'GNU GPLv2'
        self.version = '1.1'
        self.tags = [
            'cipher',
            'ROT', 
            'Caesar', 'Caesar\'s'
        ]
        self.description = """
This module performs ROT substitution enciphering.
Results will be stored in the Temporary base under <KEY>_ROT<x> key.
Any existing value will be overwritten.
"""        
        self.dependencies = {
        }
        self.changelog = """
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'KEY': Parameter(mandatory=True, description='Temporary base Key '),
            'ROT': Parameter(mandatory=False, description='Specific ROT (empty = all from 0 to 26)'),
        }

    def check(self, silent=None):
        if silent is None:
           silent = positive(self.parameters['SILENT'].value)
        key = self.parameters['KEY'].value
        rot = self.parameters['ROT'].value
        
        result = CHECK_SUCCESS
        # KEY exists?
        if key not in lib.tb.keys():
            if not silent:
                log.err('Key \'%s\' is not present in the Temporary base.' % (key))
            result = CHECK_FAILURE
        # value is not str?
        elif type(lib.tb[key]) != str:
            if not silent:
                log.err('Value is not a string.')
            result = CHECK_FAILURE
        if not rot.isdigit() and rot != '':
            if not silent:
                log.err('Incorrect ROT value.' % (rot))
            result = CHECK_FAILURE
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        key = self.parameters['KEY'].value
        rot = self.parameters['ROT'].value
        
        # # # # # # # #
        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        lowercase = 'abcdefghijklmnopqrstuvwxyz'
        
        # prepare list of desired ROTS
        if rot == '':
            rots = list(range(1, 26))
        else:
            rots = [int(rot)]
        
        # build result for each rot
        message = lib.tb[key]
        for i in rots:
            result = []
            for c in message:
                if c in uppercase:
                    result.append(uppercase[(uppercase.index(c) + i) % len(uppercase)])
                elif c in lowercase:
                    result.append(lowercase[(lowercase.index(c) + i) % len(lowercase)])
                else:
                    result.append(c)
            
            if not silent:
                log.ok('ROT%d:' % (i))
                for line in ''.join(result).splitlines():
                    log.writeline(line)
                log.writeline()
            lib.tb['%s_ROT%d' % (key, i)] = ''.join(result)
        # # # # # # # #
        return None
    

lib.module_objects.append(Module())
