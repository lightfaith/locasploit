#!/usr/bin/env python3
from source.modules._generic_module import *
import hashlib

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'locasploit.dictionary.delete'
        self.short_description = 'Deletes a dictionary from DB.'
        self.references = [
            '',
        ]
        self.date = '2016-07-31'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'locasploit',
            'dictionary',
            'export',
            'database'
        ]
        self.description = """Specified dictionary is deleted.
"""
        
        
        self.dependencies = {
        }
        self.changelog = """
"""

        self.reset_parameters() 

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'DICT': Parameter(mandatory=False, description='Dictionary name (empty -> everything)'),
        }

    def check(self, silent=None):
        # CHECK_SUCCESS       - this module will do exactly what it is designed for (e.g. successful exploit)
        # CHECK_PROBABLY      - it will probably work
        # CHECK_NOT_SUPPORTED - nothing can be checked, but it may work
        # CHECK_UNLIKELY      - module can be executed, but it will probably fail (e.g. exploit against hardened system)
        # CHECK_FAILURE       - module cannot be executed (missing files, bad parameters etc.)
        
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        dict = self.parameters['DICT'].value
        if dict != '': #  dict specified
            dicts = db['dict'].get_dictionaries()
            if dicts == DB_ERROR:
                if not silent:
                    log.err('Cannot get list of dictionaries.')
                return CHECK_FAILURE
            if dict not in dicts:
                if not silent:
                    log.err('Non-existent dictionary \'%s\'' % (dict))
                return CHECK_FAILURE
        return CHECK_SUCCESS
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        dic = self.parameters['DICT'].value
        # # # # # # # #
        if dic=='':
            result = db['dict'].delete_dictionaries()
        else:
            result = db['dict'].delete_dictionary(dic)
        if result == DB_ERROR:
            if not silent:
                log.err('Cannot delete dictionary \'%s\'.' % (dic))
            return None
        if not silent:
            log.ok('Dictionary \'%s\' deleted.' % (dic))
        return None
    

lib.module_objects.append(Module())
