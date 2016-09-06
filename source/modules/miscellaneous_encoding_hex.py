#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'miscellaneous.encoding.hex'
        self.short_description = 'Performs hex encoding/decoding.'
        self.references = [
        #   '',
        ]
        
        self.date = '2016-08-18'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'cipher',
            'hex',
        ]
        self.description = """
This module performs hex encoding/decoding.
Resulting value will be inserted into Temporary base under the key '<KEY>_HEXe' or '<KEY>_HEXd', respectively.
Any existing value will be overwritten.
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
            'KEY': Parameter(mandatory=True, description='Temporary base Key '),
            'MODE': Parameter(mandatory=True, description='e = encoding, d = decoding'),
        }

    def check(self, silent=None):
        if silent is None:
           silent = positive(self.parameters['SILENT'].value)
        key = self.parameters['KEY'].value
        mode = self.parameters['MODE'].value
        
        if mode == 'e':
            result = CHECK_SUCCESS
        else:
            result = CHECK_PROBABLY # cause it could be invalid data
            
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
        # bad mode?
        if mode not in ['e', 'd']:
            if not silent:
                log.err('Bad mode.' % (mode))
            result = CHECK_FAILURE
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        key = self.parameters['KEY'].value
        mode = self.parameters['MODE'].value
        
        if mode == 'e':
            estr = bytearray.fromhex(tb[key]).encode()
            if not silent:
                log.ok('%s_HEXe = %s' % (key, estr))
            tb['%s_HEXe' % (key)] = estr
        elif mode == 'd':
            dstr = bytearray.fromhex(tb[key]).decode()
            if not silent:
                log.ok('%s_HEXd = %s' % (key, dstr))
            tb['%s_HEXd' % (key)] = dstr
        # # # # # # # #
        return None
    

lib.module_objects.append(Module())
