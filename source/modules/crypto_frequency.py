#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'crypto.frequency'
        self.short_description = 'Inserts language-specific letter frequency dict into TB.'
        self.references = [
        ]
        
        self.date = '2016-08-18'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'frequency', 'language'
        ]
        
        self.frequencies = {
            'en': {'c': 0.02782, 'z': 0.00074, 'b': 0.01492, 'x': 0.0015, 'e': 0.12702, 'g': 0.02015, 'k': 0.00772, 'y': 0.01974, 'w': 0.0236, 'h': 0.06094, 'u': 0.02758, 'a': 0.08167, 'o': 0.07507, 'f': 0.02228, 'v': 0.00978, 's': 0.06327, 'q': 0.00095, 'r': 0.05987, 'd': 0.04253, 'j': 0.00153, 'i': 0.06966, 'p': 0.01929, 't': 0.09056, 'l': 0.04025, 'm': 0.02406, 'n': 0.06749}
        }
        
        self.description = """
This module inserts a dictionary of letter frequencies for specified language into Temporary Base.
Known languages: [%s]""" % (', '.join(self.frequencies.keys()))
        
        self.dependencies = {
        }
        self.changelog = """
"""

        self.reset_parameters()
        
        

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'LANG': Parameter(mandatory=True, description='Language'),
            'KEY': Parameter(mandatory=True, description='Destination in Temporary Base'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        lang = self.parameters['LANG'].value
        result = CHECK_SUCCESS
        # valid language?
        if lang not in self.frequencies.keys():
            if not silent:
                log.err('\'%s\' is not a valid language.' % (lang))
            result = CHECK_FAILURE
        return result
    
    def run(self):
        #silent = positive(self.parameters['SILENT'].value)
        lang = self.parameters['LANG'].value
        key = self.parameters['KEY'].value 
        tb[key] = self.frequencies[lang]
        return None


lib.module_objects.append(Module())
