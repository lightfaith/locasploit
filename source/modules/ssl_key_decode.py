#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'ssl.key.decode'
        self.short_description = 'Decodes key file.'
        self.references = [
        ]
        self.date = '2016-10-27'
        self.license = 'GNU GPLv2'
        self.version = '0.5'
        self.tags = [
            'ssl',
            'openssl', 
            'key',
            'decode',
            'pem',
            'rsa',
        ]
        
        
        self.description = 'This module uses openssl library to decode encrypted key file. Password must be known.'
        
        self.dependencies = {

        }
        self.changelog = """
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'ACTIVEROOT': Parameter(mandatory=True, description='System with file'),
            #'COMMANDROOT': Parameter(value='/', mandatory=True, description='System with openssl'),
            'INPUTFILE': Parameter(mandatory=True, description='Encrypted file (.key, .pem)'),
            'OUTPUTFILE': Parameter(mandatory=True, description='File to create (.key, .pem)'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        inputfile = self.parameters['INPUTFILE'].value
        outputfile = self.parameters['OUTPUTFILE'].value
        activeroot = self.parameters['ACTIVEROOT'].value
        #commandroot = self.parameters['COMMANDROOT'].value
        result = CHECK_PROBABLY
        # file exists?
        if not io.can_read(activeroot, inputfile):
            if not silent:
                log.err('Cannot read input file!')
            result = CHECK_FAILURE
        # openssl?
        #if not command_exists(commandroot, 'openssl'):
        if not command_exists('/', 'openssl'):
            if not silent:
                log.err('Command \'openssl\' is not available on the system.')
            result = CHECK_FAILURE
        # can write output?
        if not io.can_write(activeroot, outputfile):
            if not silent:
                log.err('Cannot create output file!')
            result = CHECK_FAILURE
        return result

    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        inputfile = self.parameters['INPUTFILE'].value
        outputfile = self.parameters['OUTPUTFILE'].value
        activeroot = self.parameters['ACTIVEROOT'].value
        #commandroot = self.parameters['COMMANDROOT'].value
        encoding = self.parameters['ENCODING'].value
        
        encoding_part = '' if encoding == '' else '-inform %s' % encoding
        command('openssl rsa -in %s -out %s' % (inputfile, outputfile))
        return None

lib.module_objects.append(Module())

