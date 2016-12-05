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
        self.dependencies = {
        }
        self.changelog = """
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'ACTIVEROOT': Parameter(mandatory=True, description='System to work with'),
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            #'BACKGROUND' : Parameter(value='yes', mandatory=True, description='yes = run in background, no = wait for it...'),
            'BINFILE': Parameter(mandatory=True, description='File to analyze'),
            'TMPDIR' : Parameter(mandatory=True, description='Directory to store files into'),
            'CLEAN' : Parameter(value='yes', mandatory=True, description='Delete carved files after extraction'),
        }

    def check(self, silent=None):
        result = CHECK_PROBABLY
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        binfile = self.parameters['BINFILE'].value
        tmpdir = self.parameters['TMPDIR'].value
        systemroot = global_parameters['SYSTEMROOT']
        # binwalk available?
        try:
            import binwalk
        except:
            if not silent:
                log.err('Binwalk is not available.')
            result = CHECK_FAILURE
        # binfile exists?
        if not io.can_read(activeroot, binfile):
            if not silent:
                log.err('Cannot access bin file \'%s\'.' % (binfile))
                result = CHECK_FAILURE
        # tmp directory exists (or can be created)?
        try:
            if not os.path.isdir(tmpdir):
                os.mkdir(tmpdir)
        except:
            if not silent:
                log.err('Cannot access directory \'%s\'.' % (tmpdir))
                result = CHECK_FAILURE
        # sasquatch?
        if not command_exists(systemroot, 'sasquatch'):
            if not silent:
                log.warn('Sasquatch is not installed. SquashFS images may not be extracted.')
        # jefferson?
        if not command_exists(systemroot, 'jefferson'):
            if not silent:
                log.warn('Jefferson is not installed. JFFS2 file systems may not be extracted.')
        # ubi_reader?
        if not command_exists(systemroot, 'ubi_reader'):
            if not silent:
                log.warn('Ubi_reader is not installed. UBIFS file systems may not be extracted.')
        # yaffshiv?
        if not command_exists(systemroot, 'yaffshiv'):
            if not silent:
                log.warn('Yaffshiv is not installed. YAFFS file systems may not be extracted.')
        # unstuff?
        if not command_exists(systemroot, 'unstuff'):
            if not silent:
                log.warn('Unstuff is not installed. StuffIt archives may not be extracted.')
        return result
    

    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        clean = positive(self.parameters['CLEAN'].value)
        import binwalk
        try:
            path = io.get_fullpath(self.parameters['ACTIVEROOT'].value, self.parameters['BINFILE'].value)
            for module in binwalk.scan(path, **{'signature' : True, 'quiet' : True, 
                'extract' : True, 'directory' : self.parameters['TMPDIR'].value, 'matryoshka' : True, 'rm': clean}):
                pass
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
