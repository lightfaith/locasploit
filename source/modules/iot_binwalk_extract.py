#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'iot.binwalk.extract'
        self.short_description = 'Extracts components of a .bin file.'
        self.references = [
            '',
        ]
        
        self.date = '2016-07-25'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'IoT',
            'Internet of Things',
            'binwalk',
            'firmware'
        ]
        self.description = """
Extracts components of a .bin file.
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
            #'BACKGROUND' : Parameter(value='yes', mandatory=True, description='yes = run in background, no = wait for it...'),
            'BINFILE': Parameter(mandatory=True, description='File to analyze'),
            'TMPDIR' : Parameter(mandatory=True, description='Directory to store files into')
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        # binwalk available?
        try:
            import binwalk
        except:
            if not silent:
                log.err('Binwalk is not available.')
            return CHECK_FAILURE
        # binfile exists?
        try:
            tmpdir = self.parameters['TMPDIR'].value
            if not os.path.isdir(tmpdir):
                os.mkdir(tmpdir)
        except:
            if not silent:
                log.err('Cannot access directory \'%s\'.' % (tmpdir))
                return CHECK_FAILURE
        # tmp directory exists (or can be created)?
        try:
            tmpdir = self.parameters['TMPDIR'].value
            if not os.path.isdir(tmpdir):
                os.mkdir(tmpdir)
        except:
            if not silent:
                log.err('Cannot access directory \'%s\'.' % (tmpdir))
                return CHECK_FAILURE
        return CHECK_PROBABLY
    

    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        import binwalk
        try:
            module in binwalk.scan(self.parameters['BINFILE'].value, **{'signature' : True, 'quiet' : True, 
                'extract' : True, 'directory' : self.parameters['TMPDIR'].value, 'matryoshka' : True})
        except binwalk.ModuleException as e:
            log.err(str(e))
        
        return None
    
"""        
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
"""    

lib.module_objects.append(Module())
