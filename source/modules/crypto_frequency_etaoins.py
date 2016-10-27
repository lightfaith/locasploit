#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'crypto.frequency.etaoins'
        self.short_description = 'Inserts language-specific ETAOIN into TB.'
        self.references = [
        ]
        
        self.date = '2016-08-18'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'frequency', 'ETAOIN', 'SHRDLU'
        ]
        
        self.etaoins = {
        'en' : 'etaoinshrdlcumwfgypbvkjxqz',                # https://en.wikipedia.org/wiki/Letter_frequency
        'cz' : 'oenatvsilkrdpímuázjyěcbéhřýžčšůfgúňxťóďwq', # https://www.algoritmy.net/article/40/Cetnost-znaku-CJ
        'cz_ascii' : 'eoaintsrvulkcdpmzyhjbfgxwq'           # https://www.algoritmy.net/article/40/Cetnost-znaku-CJ
        }
        
        self.description = """
This module writes language-specific ETAOIN into Temporary base.
'ETAOIN' is a string of characters sorted by their frequency (and then ASCII value) of occurence for a given language.
Known languages: [%s]""" % (' '.join(self.etaoins.keys()))
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
            'LANG': Parameter(mandatory=True, description='Language'),
            'KEY': Parameter(mandatory=True, description='Destination in Temporary Base'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        lang = self.parameters['LANG'].value
        result = CHECK_SUCCESS
        # valid language?
        if lang not in self.etaoins.keys():
            if not silent:
                log.err('\'%s\' is not a valid language.' % (lang))
            result = CHECK_FAILURE
        return result
    
    def run(self):
        #silent = positive(self.parameters['SILENT'].value)
        lang = self.parameters['LANG'].value
        key = self.parameters['KEY'].value 
        tb[key] = self.etaoins[lang]
        return None


lib.module_objects.append(Module())
