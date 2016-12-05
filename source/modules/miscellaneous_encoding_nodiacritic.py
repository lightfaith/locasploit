#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'miscellaneous.encoding.nodiacritic'
        self.short_description = 'Copies file while replacing special characters.'
        self.references = [
            '',
        ]
        self.date = '2016-07-28'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'template',
        ]
        self.description = """
This module reads a file, replaces special characters and writes the result into a new file.
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
            'INPUTFILE': Parameter(mandatory=True, description='Input file with diacritic'),
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
        ifile = self.parameters['INPUTFILE'].value
        ofile = self.parameters['OUTPUTFILE'].value
        if not io.can_read(root, ifile):
            log.err('Cannot read \'%s\'' % (ifile))
            return CHECK_FAILURE
        if not io.can_write(root, ofile) and not io.can_create(root, ofile):
            log.err('Cannot write \'%s\'' % (ofile))
            return CHECK_FAILURE
        return CHECK_SUCCESS
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        root = self.parameters['ACTIVEROOT'].value
        ifile = self.parameters['INPUTFILE'].value
        ofile = self.parameters['OUTPUTFILE'].value
        # # # # # # # #
        i = io.read_file(root, ifile)
        if i == IO_ERROR:
            return None
        o = ''.join([self.replace(c) for c in i]+[''])
        out = io.write_file(root, ofile, o)
        if out != IO_ERROR:
            if not silent:
                log.ok('Diacritic-free file succesfully created.')
        return None 
    
    def replace(self, c):
        substitutes = {
        'á' : 'a', 
        'č' : 'c', 
        'ď' : 'd',
        'ě' : 'e',
        'é' : 'e', 
        'í' : 'i',
        'ň' : 'n',
        'ó' : 'o',
        'ř' : 'r', 
        'š' : 's', 
        'ť' : 't', 
        'ú' : 'u', 
        'ů' : 'u', 
        'ý' : 'y', 
        'ž' : 'z',
        }
        if c in substitutes.keys():
            return substitutes[c]
        if c.lower() in substitutes.keys():
            return substitutes[c.lower()].upper()
        return c
        
lib.module_objects.append(Module())
