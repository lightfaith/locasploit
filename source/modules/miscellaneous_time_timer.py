#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'miscellaneous.time.timer'
        self.short_description = 'Just runs for a specified time.'
        self.references = [
            '',
        ]
        
        self.date = '2016-07-22'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'time',
            'timer',
        ]
        self.description = """
This module just runs for a specified time.
"""
        self.db_access = [
        ]
        
        self.dependencies = {
        }
        self.changelog = """
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'BACKGROUND' : Parameter(value='yes', mandatory=True, description='yes = run in background, no = wait for it...'),
            'TIMEOUT' : Parameter(value='5', mandatory=True, description='Number of seconds to wait'),
            'MESSAGE' : Parameter(value='Time\'s up!', mandatory=True, description='Message to show when module finishes.'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        # check parameteres
        silent = positive(self.parameters['SILENT'].value)
        if not positive(self.parameters['BACKGROUND'].value) and not negative(self.parameters['BACKGROUND'].value):
            if not silent:
                log.err('Bad %s value: %s.', 'BACKGROUND', self.parameters['BACKGROUND'].value)
            return CHECK_FAILURE
        if not self.parameters['TIMEOUT'].value.isdigit() or int(self.parameters['TIMEOUT'].value) < 0:
            if not silent:
                log.err('Bad timeout value: %d', int(self.parameters['TIMEOUT'].value))
            return CHECK_FAILURE
        return CHECK_SUCCESS
    
    def run(self):
        
        # # # # # # # #
        t = Thread(silent, int(self.parameters['TIMEOUT'].value))
        t.start()
        if positive(self.parameters['BACKGROUND'].value):
            return t
        t.join()
        # # # # # # # #
        return None
    
        
class Thread(threading.Thread):
    def __init__(self, silent, timeout):
        threading.Thread.__init__(self)
        self.silent = silent
        self.timeout = timeout
        self.terminate = False
            
    # starts the thread
    def run(self):
        if not self.silent:
            log.info('You have %d seconds.' % (self.timeout))
        while self.timeout > 0:
            self.timeout -= 1
            time.sleep(1)
        if not self.silent:
            log.ok('Time\'s up!')

    # terminates the thread
    def stop(self):
        self.terminate = True
    

lib.module_objects.append(Module())
