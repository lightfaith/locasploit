#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'ssl.certificate.view'
        self.short_description = 'Shows info about certificate.'
        self.references = [
        ]
        self.date = '2016-10-27'
        self.license = 'GNU GPLv2'
        self.version = '0.5'
        self.tags = [
            'ssl',
            'openssl', 
            'certificate',
            'view',
            'cer',
            'crt',
            'der',
            'pem',
            'x509',
        ]
        
        
        self.description = 'This module uses openssl library to read certificate information.'
        
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
            'INPUTFILE': Parameter(mandatory=True, description='.cer, .crt, .pem or .der file'),
            'ENCODING': Parameter(mandatory=False, description='Encoding specification (pem, der)'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        inputfile = self.parameters['INPUTFILE'].value
        activeroot = self.parameters['ACTIVEROOT'].value
        #commandroot = self.parameters['COMMANDROOT'].value
        encoding = self.parameters['ENCODING'].value
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
        # valid encoding?
        if encoding not in ['', 'der', 'pem']:
            if not silent:
                log.err('Invalid encoding!')
            result = CHECK_FAILURE
        return result

    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        inputfile = self.parameters['INPUTFILE'].value
        activeroot = self.parameters['ACTIVEROOT'].value
        #commandroot = self.parameters['COMMANDROOT'].value
        encoding = self.parameters['ENCODING'].value
        
        encoding_part = '' if encoding == '' else '-inform %s' % encoding
        result = command('openssl x509 %s -in %s -noout -text' % (encoding_part, inputfile), value=True)
        log.ok(result)
        return None

lib.module_objects.append(Module())

