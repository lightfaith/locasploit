#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'locasploit.cleanup'
        self.short_description = 'Removes unnecessary files.'
        self.references = [
            '',
        ]
        
        self.date = '2017-02-12'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'locasploit',
            'cleanup',
        ]
        self.description = """
This module removes useless files from locasploit folder, namely:
    vulnerabilities/
    dictionaries/
"""
        
        self.dependencies = {
        }
        self.changelog = """
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'BACKGROUND' : Parameter(value='yes', mandatory=True, description='yes = run in background, no = wait for it...'),

        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        result = CHECK_SUCCESS
        # check parameters
        silent = positive(self.parameters['SILENT'].value)
        if not positive(self.parameters['BACKGROUND'].value) and not negative(self.parameters['BACKGROUND'].value):
            if not silent:
                log.err('Bad %s value: %s.', 'BACKGROUND', self.parameters['BACKGROUND'].value)
            result = CHECK_FAILURE
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value) 
        # # # # # # # #
        #t = Thread(silent, int(self.parameters['TIMEOUT'].value))
        t = Thread(silent)
        if positive(self.parameters['BACKGROUND'].value):
            return t
        t.start()
        t.join()
        # # # # # # # #
        return None
    
        
class Thread(threading.Thread):
    def __init__(self, silent):
        threading.Thread.__init__(self)
        self.silent = silent
        self.terminate = False
    
    def run(self):
        todel = [
            './vulnerabilities/',
            './dictionaries',
        ]

        for target in todel:
            if self.terminate:
                break
            io.delete('/', target)

        
    # terminates the thread
    def stop(self):
        self.terminate = True
    

lib.module_objects.append(Module())
