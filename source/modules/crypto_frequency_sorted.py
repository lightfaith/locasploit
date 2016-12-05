#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'crypto.frequency.sorted'
        self.short_description = 'Inserts characters sorted by frequency into TB.'
        self.references = [
        ]
        
        self.date = '2016-08-18'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'frequency', 'ETAOIN', 'SHRDLU'
        ]
        self.description = """
Inserts characters sorted by frequency into TB.
Existing value will be rewritten.
"""
        
        self.dependencies = {
        }
        self.changelog = """
"""

        self.reset_parameters()
        

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'TEXTKEY': Parameter(mandatory=True, description='Temporary base key of input string'),
            'SORTEDKEY': Parameter(mandatory=True, description='Key for storing result'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        textkey = self.parameters['TEXTKEY'].value
        result = CHECK_SUCCESS
        # invalid textkey?
        if textkey not in tb:
            if not silent:
                log.err('\'%s\' is not in TB.' % (textkey))
            result = CHECK_FAILURE
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        textkey = self.parameters['TEXTKEY'].value
        sortedkey = self.parameters['SORTEDKEY'].value
        textvalue = tb[textkey]
        
        charcount = 0
        freqs = {}
        #for letter in 'abcdefghijklmnopqrstuvwxyz':
        #    freqs[letter] = 0
        # count occurences
        for letter in textvalue:
            charcount += 1
            if letter in freqs:
                freqs[letter] += 1
            else:
                freqs[letter] = 1
        # get frequency
        
        for letter in freqs:
            freqs[letter] /= charcount
        print(freqs)
        result = ''.join(sorted(sorted(freqs), key=freqs.get, reverse=True))
        
        if not silent:
            log.ok('Letters sorted by frequency:')
            log.attachline(result)
        tb[sortedkey] = result
        return None


lib.module_objects.append(Module())
