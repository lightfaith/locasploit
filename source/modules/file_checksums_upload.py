#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'file.checksums.upload'
        self.short_description = 'Uploads file checksums into checksum database.'
        self.references = [
            '',
        ]
        self.date = '2016-08-13'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'file', 'checksum', 'hash', 'md5', 'sha1'
        ]
        self.description = """
This module computes MD5 and SHA1 checksums of a given file and stores these results in checksum database for further analysis (such as app version detection).
"""
        
        self.db_access = [
            'Temporary',
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
            'TAG': Parameter(mandatory=True, description='Tag for hash identification'),
            'INPUTFILE': Parameter(mandatory=True, description='Input file'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        inputfile = self.parameters['INPUTFILE'].value
        # can import hashlib?
        result = CHECK_SUCCESS
        try:
            import hashlib
        except:
            if not silent:
                log.err('Cannot import hashlib.')
            result = CHECK_FAILURE
        # can read file?
        if not io.can_read(activeroot, inputfile):
            if not silent:
                log.err('Cannot read \'%s\'.' % (inpufile))
            result = CHECK_FAILURE
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        tag = self.parameters['TAG'].value
        inputfile = self.parameters['INPUTFILE'].value
        # # # # # # # #
        import hashlib
        content = io.read_file(activeroot, inputfile, False)
        md5 = hashlib.md5(content.encode('utf-8')).hexdigest()
        sha1 = hashlib.sha1(content.encode('utf-8')).hexdigest()
        result = db['checksum'].add_tmp_checksum(tag, md5, sha1)
        if result == DB_ERROR:
            log.err('Cannot access database.')
        else:
            if not silent:
                log.ok('Checksums for \'%s\' successfully acquired:' % (inputfile))
                log.writeline('MD5:  %s' % md5)
                log.writeline('SHA1: %s' % sha1)
        return None 
    

lib.module_objects.append(Module())
