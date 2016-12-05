#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'ssl.csr.generate'
        self.short_description = 'Generates key and CSR.'
        self.references = [
        ]
        self.date = '2016-10-27'
        self.license = 'GNU GPLv2'
        self.version = '0.5'
        self.tags = [
            'ssl',
            'openssl', 
            'generate',
            'key',
            'csr',
            'pem',
        ]
        
        
        self.description = 'This module uses openssl library to generate private key and matching Certificate Signing Request. Configuration file can be optionally used.'
        
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
            'CSRFILE': Parameter(mandatory=True, description='Resulting csr file (.pem)'),
            'KEYFILE': Parameter(mandatory=True, description='Resulting encoded key file (.pem)'),
            'CONFIGFILE': Parameter(mandatory=False, description='Configuration file'),

        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        csrfile = self.parameters['CSRFILE'].value
        keyfile = self.parameters['KEYFILE'].value
        configfile = self.parameters['CONFIGFILE'].value
        activeroot = self.parameters['ACTIVEROOT'].value
        #commandroot = self.parameters['COMMANDROOT'].value
        result = CHECK_PROBABLY
        # openssl?
        #if not command_exists(commandroot, 'openssl'):
        if not command_exists('/', 'openssl'):
            if not silent:
                log.err('Command \'openssl\' is not available on the system.')
            result = CHECK_FAILURE
        # can read config?
        if configfile != '' and not io.can_read(configfile):
            if not silent:
                log.err('Cannot read config file.')
            result = CHECK_FAILURE
        # can write?
        if not (io.can_write(activeroot, csrfile) and io.can_write(activeroot, keyfile)):
            if not silent:
                log.err('Cannot write output files!')
            result = CHECK_FAILURE
        return result

    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        csrfile = self.parameters['CSRFILE'].value
        keyfile = self.parameters['KEYFILE'].value
        configfile = self.parameters['CONFIGFILE'].value
        activeroot = self.parameters['ACTIVEROOT'].value
        #commandroot = self.parameters['COMMANDROOT'].value
        
        config_part = '' if configfile == '' else '-config %s' % configfile
        result = command('openssl req %s -new -out %s -keyout %s' % (config_part, csrfile, keyfile), value=True)
        log.ok(result)
        return None

lib.module_objects.append(Module())

