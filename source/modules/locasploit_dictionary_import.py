#!/usr/bin/env python3
from source.modules._generic_module import *
import hashlib

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'locasploit.dictionary.import'
        self.short_description = 'Imports a wordlist into dictionary DB.'
        self.references = [
            '',
        ]
        self.date = '2016-07-28'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'locasploit',
            'dictionary',
            'import',
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
            'DICT': Parameter(mandatory=True, description='Dictionary name'),
            'INPUTFILE': Parameter(mandatory=True, description='Wordlist file'),
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
        file = self.parameters['INPUTFILE'].value
        dict = self.parameters['DICT'].value
        dicts = db['dict'].get_dictionaries()
        if dicts == DB_ERROR:
            if not silent:
                log.err('Cannot get list of dictionaries.')
            return CHECK_FAILURE
        if dict in dicts:
            if not silent:
                log.err('Dictionary \'%s\' already exists.' % (dict))
            return CHECK_FAILURE
        if not io.can_read(root, file):
            if not silent:
                log.err('Cannot read \'%s\'' % (file))
            return CHECK_FAILURE
        return CHECK_SUCCESS
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        dic = self.parameters['DICT'].value
        inputfile = self.parameters['INPUTFILE'].value
        # # # # # # # #
          # get hash from binary
        f = io.read_file(activeroot, inputfile, usedb=False, forcebinary=True)
        checksum = hashlib.sha1(f).hexdigest()
        #
        f = io.read_file(activeroot, inputfile, usedb=False)
        if f == IO_ERROR:
            log.err('Cannot access \'%s\'.' % (inputfile))
            return None
        words = [w for w in f.splitlines() if w.strip() != '']
        result = db['dict'].add_words(words, dic, checksum)
        if result == DB_ERROR:
            log.err('Dictionary cannot be created properly.')
        else:
            if not silent:
                log.ok('Dictionary %s created successfully (%d words).' % (dic, len(words)))
        return None 
    

lib.module_objects.append(Module())
