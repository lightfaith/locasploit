#!/usr/bin/env python3
from source.modules._generic_module import *
import hashlib

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'locasploit.dictionary.export'
        self.short_description = 'Export words from DB into a wordlist.'
        self.references = [
            '',
        ]
        self.date = '2016-07-30'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'locasploit',
            'dictionary',
            'export',
            'database'
        ]
        self.description = """
Words from a wordlist file are imported into locasploit database.
"""
        
        
        self.dependencies = {
        }
        self.changelog = """
"""

        self.reset_parameters() 

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'ACTIVEROOT': Parameter(mandatory=True, description='System to work with'),
            'DICT': Parameter(mandatory=False, description='Dictionary name (empty -> everything)'),
            'OUTPUTFILE': Parameter(mandatory=True, description='Output file'),
        }

    def check(self, silent=None):
        # CHECK_SUCCESS       - this module will do exactly what it is designed for (e.g. successful exploit)
        # CHECK_PROBABLY      - it will probably work
        # CHECK_NOT_SUPPORTED - nothing can be checked, but it may work
        # CHECK_UNLIKELY      - module can be executed, but it will probably fail (e.g. exploit against hardened system)
        # CHECK_FAILURE       - module cannot be executed (missing files, bad parameters etc.)
        
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        root = self.parameters['ACTIVEROOT'].value
        file = self.parameters['OUTPUTFILE'].value
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
        if not io.can_write(root, file) and not io.can_create(root, file):
            if not silent:
                log.err('Cannot write \'%s\'' % (file))
            return CHECK_FAILURE
        return CHECK_SUCCESS
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        dic = self.parameters['DICT'].value
        outputfile = self.parameters['OUTPUTFILE'].value
        # # # # # # # #
        if dic == '':
            words = db['dict'].dump_words()
        else:
            words = db['dict'].get_dictionary(dic)
        if words == DB_ERROR:
            log.err('Cannot get words from the database.')
            return None
        content = '\n'.join(words)
        try:
            result = io.write_file(activeroot, outputfile, content)
        except UnicodeEncodeError:
            result = io.write_file(activeroot, outputfile, content.encode('utf-8'))
        if result == IO_ERROR:
            log.err('Cannot access \'%s\'.' % (inputfile))
        else:
            log.ok('Wordlist \'%s\' created successfully (%d words).' % (outputfile, len(words)))
        return None
    

lib.module_objects.append(Module())
