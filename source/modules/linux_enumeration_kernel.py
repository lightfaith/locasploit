#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'linux.enumeration.kernel'
        self.short_description = 'Extracts information about current kernel.'
        self.references = [
            'https://blog.g0tmi1k.com/2011/08/basic-linux-privilege-escalation/',
        ]
        
        self.date = '2016-01-25'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'linux',
            'kernel',
            'uname',
            'vmlinuz',
            'dmesg',
        ]
        
        self.description = """
This module extracts various info about the kernel.
Specifically, the following commands are issued:
    cat /proc/version
    uname -a
    uname -mrs
    rpm -q kernel
    dmesg | grep Linux
    ls /boot | grep vmlinuz-
"""
        self.db_access = [
            'KERNEL',
            'KERNEL PROC_VERSION',
            'KERNEL UNAME-A',
            'KERNEL UNAME-MRS',
            'KERNEL RPM',
            'KERNEL DMESG_LINUX',
            'KERNEL VMLINUZ',

        ]
        self.dependencies = {

        }
        self.changelog = ''
        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'ACTIVEROOT': Parameter(mandatory=True, description='System to work with'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        return CHECK_NOT_SUPPORTED
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        # # # # # # # #
        # get /proc/version
        proc_version = io.read_file(self.parameters['ACTIVEROOT'].value, '/proc/version')
        if proc_version != IO_ERROR:
            log.ok('/proc/version:')
            for x in result.splitlines():
                log.writeline(x)
        else:
            log.err('/proc/version cannot be accessed.')
        
        """
        # run uname -a and uname -mrs
        if command_exists('uname'):
            unamea = command('uname -a')
            lib.kb.add('KERNEL UNAME-A', unamea)
            if not silent:
                log.ok('uname -a:')
                for x in unamea.splitlines():
                    log.writeline(x)
            unamemrs = command('uname -mrs')
            lib.kb.add('KERNEL UNAME-MRS', unamemrs)
            if not silent:
                log.ok('uname -mrs:')
                for x in unamemrs.splitlines():
                    log.writeline(x)
        else:
            log.err('Uname cannot be executed.')
        
        # run rpm -q kernel
        if command_exists('rpm'):
            rpm = command('rpm -q kernel')
            lib.kb.add('KERNEL RPM', rpm)
            if not silent:
                log.ok('rpm -q kernel:')
                for x in rpm.splitlines():
                    log.writeline(x)
        else:
            log.err('Rpm cannot be executed.')
        
        # run dmesg | grep Linux
        if command_exists('dmesg'):
            dm = command('dmesg | grep Linux')
            lib.kb.add('KERNEL DMESG_LINUX', dm)
            if not silent:
                log.ok('dmesg | grep Linux:')
                for x in dm.splitlines():
                    log.writeline(x)
                
        else:
            log.err('Dmesg cannot be executed.')
        
        # what vmlinuz?
        if os.access('/boot', os.R_OK) and os.access('/boot', os.X_OK):
            vmlinuzes = [x for x in os.listdir('/boot') if x[:8] == 'vmlinuz-']
            lib.kb.add('KERNEL VMLINUZ', '\n'.join(vmlinuzes))
            if not silent:
                log.ok('vmlinuz in /boot/:')
                for x in vmlinuzes:
                    log.writeline(x)
        else:
            log.err('/boot cannot be accessed.')
        # # # # # # # #
        """
        return None


lib.module_objects.append(Module())
