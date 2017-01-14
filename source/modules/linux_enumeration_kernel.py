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
    rpm -q kernel
    dmesg | grep Linux
    ls /boot | grep vmlinuz-
    uname -r
    cat /proc/version
"""
        
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
        activeroot = self.parameters['ACTIVEROOT'].value

        # # # # # # # #
        known = db['analysis'].get_data_system('KERNEL', activeroot)
        if len(known) > 0:
            known = known[0][3]
            log.info('Already known: %s' % known)
        else:
            known = None
        
        # from least confident to the most
        # TODO rpm -q kernel
        
        # TODO dmesg | grep Linux

        # /boot/vmlinuz-*
        boots = sorted([x[8:] for x in io.list_dir(activeroot, '/boot') if x.startswith('vmlinuz-')], reverse=True)
        # let's use the highest one (#TODO is that enough?)
        if len(boots)>0:
            if not silent:
                log.ok('/boot/vmlinuz: %s' % (boots[0]))
            db['analysis'].add_data_system('VMLINUZ', activeroot, boots[0])
            known = boots[0]

        # TODO uname -r 
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
        
        else:
            log.err('/boot cannot be accessed.')
        # # # # # # # #
        """
        # get /proc/version
        if io.can_read(activeroot, '/proc/version'):
            proc_version = io.read_file(activeroot, '/proc/version')
            if proc_version != IO_ERROR:
                proc_version = re.search(r'Linux version ([^ ]+)', proc_version).group(1)
                if not silent:
                    log.ok('/proc/version: %s' % (proc_version))
                db['analysis'].add_data_system('PROC_VERSION', activeroot, proc_version)
                known = proc_version
        

        # save best result as KERNEL
        if known is not None:
            db['analysis'].add_data_system('KERNEL', activeroot, known.partition('-')[0])
        
        return None


lib.module_objects.append(Module())
