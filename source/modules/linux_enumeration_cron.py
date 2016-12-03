#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'linux.enumeration.cron'
        self.short_description = 'Dumps cron entries.'
        self.references = [
        ]
        self.date = '2016-12-02'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'linux',
            'cron', 
            'crontab',
            'enumeration',
        ]
        
        
        self.description = 'This module dumps /etc/crontab, /etc/anacrontab, /etc/cron.d/* and /var/spool/cron/crontabs/* to determined what is scheduled.'
        self.db_access = [
        'USER', #'GROUP', 'UG',
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
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        result = CHECK_SUCCESS
        
        return result

    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        lines = []
        # solve files in /etc
        for etcfile in ['/etc/anacrontab', '/etc/crontab'] + [os.path.join('/etc/cron.d/', x) for x in io.list_dir(activeroot, '/etc/cron.d/')]:
            if not io.can_read(activeroot, etcfile):
                continue
            tmp = io.read_file(activeroot, etcfile)
            if tmp != IO_ERROR:
                lines += tmp.splitlines()
#                if type(lines) in (list, tuple):
#                    lines += tmp.splitlines()
#                else:
#                    lines.append(tmp.splitlines())
        
        # solve user crons
        for user in io.list_dir(activeroot, '/var/spool/cron/crontabs'):
            path = os.path.join('/var/spool/cron/crontabs/', user)
            if not io.can_read(activeroot, path):
                continue
            tmp = io.read_file(activeroot, path)
            if tmp != IO_ERROR:
                for line in tmp.splitlines():
                    data = re.split('[ \t]+', line)
                    lines.append(' '.join(data[:5] + [user] + data[5:]))

        # scrap comments, variable definitions and add run-parts files
        ignore = ('#', 'SHELL=', 'PATH=', 'MAILTO=', 'DEFAULT=', 'NICETIGER=')
        lines = [x for x in lines if len(x.strip())>0 and not x.startswith(ignore)]
        for line in lines:
            if 'run-parts --report ' in line: # another folder
                how = ' '.join(x for x in re.split('[ \t]+', line)[:(2 if line.startswith('@') else 6)])
                folder = line.partition('run-parts --report ')[2].split(' ')[0]
                for f in io.list_dir(activeroot, folder):
                    lines.append('%s %s' % (how, f))
        #    else:
        #        print(line)
        todb = []
        for line in lines:
            words = re.split('[ \t]+', line)
            if words[0].startswith('@'):
                todb.append([words[0], words[1], ' '.join(words[2:])])
            else:
                todb.append([' '.join(words[:5]), words[5], ' '.join(words[6:])])

        if db['analysis'].add_cron(activeroot, todb) == DB_ERROR:
            log.err('Cannot add cron entries into DB.')
        
        return None

lib.module_objects.append(Module())

