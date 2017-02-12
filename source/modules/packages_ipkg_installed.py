#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'packages.ipkg.installed'
        self.short_description = 'Finds versions of installed packages.'
        self.references = [
        ]
        self.date = '2017-01-17'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'linux',
            'package',
            'packages',
            'ipkg',
            'installed',
            'version',
        ]
        
        
        self.description = """This module looks into /usr/lib/ipkg/status file to determine version of all installed packages.
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
            'TAG': Parameter(mandatory=True, description='Tag'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        result = CHECK_SUCCESS
        # is the system linux?
        if not get_system_type_from_active_root(activeroot).startswith('lin'):
            if not silent:
                log.warn('Target system does not belong to Linux family.')
            result = CHECK_UNLIKELY
        if not io.can_read(activeroot, '/usr/lib/ipkg/status'):
            if not silent:
                log.err('Cannot open /usr/lib/ipkg/status file.')
            result = CHECK_FAILURE
        return result

    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        tag = self.parameters['TAG'].value
        
        results = []
        """
        # TODO also /var/lib/ipkg/info/?
        path = '/usr/lib/opkg/info'
        # get control files
        from os import listdir
        cfiles = [x for x in io.list_dir(activeroot, path) if x.endswith('.control')]
        
        # read .control files
        for cfile in cfiles:
            path = os.path.join('/usr/lib/opkg/info', cfile)
            content = io.read_file(activeroot, path)
            if content == IO_ERROR:
                log.err('Cannot read %s' % (path))
                continue
            # get info
            pkgdata = [x.partition(' ')[2] for x in content.splitlines() if x.startswith(('Package', 'Version'))]
            product = pkgdata[0]
            # get version
            version = pkgdata[1]
            results.append((product, None, version))
        """
        # read status file
        content = io.read_file(activeroot, '/usr/lib/ipkg/status')
        if content == IO_ERROR:
            if len(results) == 0:
                log.err('Cannot read /usr/lib/ipkg/status')
        else:
            info = [x.partition(' ')[2] for x in content.splitlines() if x.startswith(('Package', 'Status', 'Version'))]
            results += [(info[i], None, info[i+2]) for i in range(0, len(info)-2, 3) if 'installed' in info[i+1]]

        # insert into TB
        tb[tag] = results
        #db['vuln'].add_tmp(results)
        #if not silent and len(results)<100:
        #    for result in results:
        #        log.info(result)
        if not silent:
            log.ok('%d packages revealed.' % (len(results)))
        return None

lib.module_objects.append(Module())

