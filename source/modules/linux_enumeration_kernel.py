#!/usr/bin/env python3
"""
This module determines installed kernel version.
"""
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        super().__init__()
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
            'vmlinuz',
            '/proc/version',
        ]
        
        self.description = """
This module extracts various info about the kernel.
For running system, reading /proc/version should be sufficient.
Otherwise, /boot/vmlinuz-* is searched for best match.
Other methods exist, such as
    dmesg | grep Linux,
    uname -r,
but they are not implemented.

Sometimes, kernel version can be detected from package manager database - as in analysis.iot module.
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
        result = CHECK_SUCCESS
        activeroot = self.parameters['ACTIVEROOT'].value
        if not get_system_type_from_active_root(activeroot).startswith('lin'):
            if not silent:
                log.warn('Target system does not belong to Linux family.')
            result = CHECK_UNLIKELY
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value

        # # # # # # # #
        known = db['analysis'].get_data_system('KERNEL', activeroot)
        if len(known) > 0:
            known = known[0][3]
            if not silent:
                log.ok('Kernel version already known: %s' % known)
        else:
            known = None
        
        # from least confident to the most
        
        # /boot/vmlinuz-*
        boots = sorted([x[8:] for x in io.list_dir(activeroot, '/boot') if x.startswith('vmlinuz-')], reverse=True)
        # let's use the highest one
        if len(boots)>0:
            if not silent:
                log.ok('/boot/vmlinuz: %s' % (boots[0]))
            db['analysis'].add_data_system('VMLINUZ', activeroot, boots[0])
            known = boots[0]

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
