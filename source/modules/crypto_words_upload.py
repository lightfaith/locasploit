#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'crypto.words.upload'
        self.short_description = 'Moves words from Temporary base into database.'
        self.references = [
            '',
        ]
        self.date = '2016-08-06'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'words', 'tb', 'temporary', 'base',
            'db', 'database'
        ]
        self.description = """
This module moves list of words or string (word by word) from Temporary base into dictionary database for further analysis.
If the whole TB is to be moved into database, keys are used as tags.
"""
        
        self.db_access = [
            'Temporary',
        ]
        
        self.dependencies = {
        }
        self.changelog = """
"""

        self.reset_parameters() 

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'KEY': Parameter(mandatory=False, description='Temporary base key (empty = everything)'),
            'TAG': Parameter(mandatory=False, description='Tag in database'),
            'LOWERCASE': Parameter(value='yes', mandatory=True, description='Words will be in lowercase'),
        }

    def check(self, silent=None):
        # CHECK_SUCCESS       - this module will do exactly what it is designed for (e.g. successful exploit)
        # CHECK_PROBABLY      - it will probably work
        # CHECK_NOT_SUPPORTED - nothing can be checked, but it may work
        # CHECK_UNLIKELY      - module can be executed, but it will probably fail (e.g. exploit against hardened system)
        # CHECK_FAILURE       - module cannot be executed (missing files, bad parameters etc.)
        
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        key = self.parameters['KEY'].value
        tag = self.parameters['TAG'].value
        
        result = CHECK_SUCCESS
        # TBKEY exists or upload everything?
        if key != '' and key not in lib.tb.keys():
            if not silent:
                log.err('No key \'%s\' in the Temporary base.' % (key))
            result = CHECK_FAILURE
        # TBKEY does not exist but not upload everything?
        if tag == '' and key != '':
            if not silent:
                log.err('No tag specified for key \'%s\'.' % (key))
            result = CHECK_FAILURE
        # TAG has correct form?
        elif ' ' in self.parameters['TAG'].value:
            if not silent:
                log.err('Tag cannot contain spaces.')
            result = CHECK_FAILURE
            
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        key = self.parameters['KEY'].value
        tag = self.parameters['TAG'].value
        lowercase = positive(self.parameters['LOWERCASE'].value)
        
        keys = [key] if key != '' else list(lib.tb.keys())
        for key in keys:
            if len(keys) > 1:
                tag = key
            values = lib.tb[key]
            if type(values) == list:
                values = ' '.join(values)
            if lowercase:
                values = values.lower()
            if type(values) == str:
                values = filter(None, values.translate(dict.fromkeys(map(ord, '.,-!?:;\'"'), ' ')).split())
            else:
                log.err('Cannot determine type of TB data for key \'%s\'.' % (key))
                continue
            result = db['dict'].add_tmp_words(tag, values)
            if result == DB_ERROR:
                    log.err('Cannot insert words into database (key \'%s\').' % (key))
        else:
            if not silent:
                log.ok('Words inserted into database succesfully.')
        return None 
    

lib.module_objects.append(Module())
