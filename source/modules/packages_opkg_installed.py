#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'packages.opkg.installed'
        self.short_description = 'Finds versions of installed packages.'
        self.references = [
        ]
        self.date = '2016-11-05'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'linux',
            'package',
            'packages',
            'opkg',
            'installed',
            'version',
        ]
        
        
        self.description = """This module looks into /usr/lib/opkg/info/*.control files to determine version of all installed packages.
"""
        self.db_access = [
        #''
        ]
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
        # can open /usr/lib/opkg/info ??
        if not io.can_read(activeroot, '/usr/lib/opkg/info'):
            if not silent:
                log.err('Cannot open /usr/lib/opkg/info/ directory.')
            result = CHECK_FAILURE
        return result

    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        tag = self.parameters['TAG'].value
        path = '/usr/lib/opkg/info'
        # get control files
        from os import listdir
        cfiles = [x for x in io.list_dir(activeroot, path) if x.endswith('.control')]
        results = []
        # read files
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

