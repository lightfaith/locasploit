#!/usr/bin/env python3
from source.modules._generic_module import *
from source.libs.db import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'locasploit.db.query'
        self.short_description = 'Allows to run arbitrary queries on connected databases.'
        self.references = [
            '',
        ]
        
        self.date = '2016-07-23'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'DB',
            'SQLite',
            'Locasploit',
            'firmware'
        ]
        self.description = """
Allows to run arbitrary queries on connected databases. Changes are commited when this module is terminated.

Connected databases: """ + str(list(db.keys()))
        
        self.dependencies = {
        }
        self.changelog = """
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            #'BACKGROUND' : Parameter(value='yes', mandatory=True, description='yes = run in background, no = wait for it...'),
            'DB': Parameter(mandatory=True, description='Connected database'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        if self.parameters['DB'].value not in db.keys():
            if not silent:
                log.err('%s is not among connected databases..' % (self.parameters['DB'].value))
                log.info('Available databases: %s' % str(list(db.keys())))
            return CHECK_FAILURE
        return CHECK_SUCCESS
    
    def run(self):
        
        silent = positive(self.parameters['SILENT'].value)
        old_prompt = lib.prompt
        lib.prompt = 'DB: '
        if lib.python_version[0] == '2':
            func = raw_input
        elif lib.python_version[0] == '3':
            func = input
        else:
            log.err('Invalid PYTHON_VERSION (%s).' % lib.python_version)
            return None
        
        while True:
            if not silent:
                log.prompt()
            # check lib.commands
            if len(lib.commands) > 0:
                line = lib.commands[0]
                del lib.commands[0]
                if not silent:
                    log.attachline(line)
            else:
                line = func()

            # exit?
            if line in QUIT_STRINGS:
                db[self.parameters['DB'].value].commit()
                break
            # list tables?
            if line.lower() in ['tables', 'show_tables', 'show tables']:
                log.attachline(db[self.parameters['DB'].value].get_tables())
                continue
            # SQL command
            try:
                if not silent:
                    results = db[self.parameters['DB'].value].query(line)
                    if len(results) == 1:
                        results = results[0]
                    if len(results) != 0:
                        log.attachline(results)
            except Exception as e:
                log.err(str(e))

        lib.prompt = old_prompt
        # # # # # # # #
        return None

lib.module_objects.append(Module())
