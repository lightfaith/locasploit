#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'crypto.xor'
        self.short_description = 'Performs ROT substitution enciphering.'
        self.references = [
        #   '',
        ]
        
        self.date = '2016-08-18'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'cipher',
            'XOR', 
        ]
        self.description = """
This module performs XOR encryption/decryption.
Results will be stored in the Temporary base under the key <KEY1>_XOR, respectively.
Key 2 will be repeated to key 1 length or trimmed.
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
            'KEY1': Parameter(mandatory=True, description='Temporary base Key 1'),
            'KEY2': Parameter(mandatory=True, description='Temporary base Key 2'),
        }

    def check(self, silent=None):
        if silent is None:
           silent = positive(self.parameters['SILENT'].value)
        key1 = self.parameters['KEY1'].value
        key2 = self.parameters['KEY2'].value
        
        result = CHECK_SUCCESS
        # KEYS exists? Values are strings?
        if key1 not in lib.tb.keys():
            if not silent:
                log.err('Key \'%s\' is not present in the Temporary base.' % (key1))
            result = CHECK_FAILURE
        elif type(lib.tb[key1]) != str:
            if not silent:
                log.err('Value of key \'%s\' is not a string.' % (key1))
            result = CHECK_FAILURE
        
        if key2 not in lib.tb.keys():
            if not silent:
                log.err('Key \'%s\' is not present in the Temporary base.' % (key2))
            result = CHECK_FAILURE
        elif type(lib.tb[key2]) != str:
            if not silent:
                log.err('Value of key \'%s\' is not a string.' % (key2))
            result = CHECK_FAILURE
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        key1 = self.parameters['KEY1'].value
        key2 = self.parameters['KEY2'].value
        value1 = tb[key1]
        value2 = (tb[key2] * (1+int(len(value1) / len(tb[key2]))))[:len(value1)]
        result = ''.join([chr(ord(x) ^ ord(y)) for x, y in zip(value1, value2)])
        if not silent:
            log.ok('%s_XOR = %s' % (key1, result))
        tb['%s_XOR' % (key1)] = result
        
        # # # # # # # #
        return None
    

lib.module_objects.append(Module())
