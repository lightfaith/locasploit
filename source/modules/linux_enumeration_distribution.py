#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'linux.enumeration.distribution'
        self.short_description = 'Extracts information about current distro.'
        self.references = [
            'https://blog.g0tmi1k.com/2011/08/basic-linux-privilege-escalation/'
        ]
        
        self.date = '2016-01-25'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'linux',
            'distribution',
            'issue',
            'release',
            '/etc/issue',
        ]
        
        self.description = 'This module extracts various info about current distribution from specific files (namely /etc/issue and /etc/*-release).'
        
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
        result = CHECK_NOT_SUPPORTED
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        # # # # # # # #
        
        # get /etc/issue
        issue = io.read_file(activeroot, '/etc/issue')
        if issue != IO_ERROR:
            issue = '\n'.join([x for x in issue.splitlines() if len(x.strip())>0])
            if not silent:
                log.ok('/etc/issue:')
                for line in issue.splitlines():
                    if len(line.strip())>0:
                        log.ok('  ' + line)
            db['analysis'].add_data_system('ISSUE', activeroot, issue)

        # get /etc/*-release
        releases = [x for x in io.list_dir(activeroot, '/etc') if x.endswith('-release')]
        for x in releases:
            path = os.path.join('/etc/', x)
            release = io.read_file(activeroot, path)
            if release == IO_ERROR:
                continue
            release = '\n'.join([x for x in release.splitlines() if len(x.strip())>0])
            if not silent:
                log.ok('%s:' % (x))
                for line in release.splitlines():
                    log.ok('  ' + line)
            db['analysis'].add_data_system(x.upper(), activeroot, release)
          
        # TODO uname -m?

        # # # # # # # #
        return None
    

lib.module_objects.append(Module())
