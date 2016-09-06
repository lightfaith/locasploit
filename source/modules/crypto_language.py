#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'crypto.language'
        self.short_description = 'Attempts to reveal string\'s language.'
        self.references = [
        ]
        
        self.date = '2016-02-03'
        self.license = 'GNU GPLv2'
        self.version = '2.0'
        self.tags = [
            'language',
        ]
        self.description = """
This module compares strings located in Temporary table of the Dictionary database.
If no language is specified, all languages will be tested.
You can upload words into the database using:
    1. db['dict'].add_tmp_words(self, tag, words) method
    2. crypto.words.upload module
"""
        self.db_access = [
            'Temporary',
        ]
        
        self.dependencies = {
        }
        self.changelog = """
2.0: Words analyzed in database, any character except space is valid
     Threading support removed
1.1: Threading support (not quite efficient)
     Word splitting by punct, numbers and whitespace
1.0: Language recognition
     Words A-Za-z'0-9
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'TAGS': Parameter(mandatory=False, description='Space-separated tags to analyze (empty = all)'),
            'DICTS': Parameter(mandatory=False, description='Space-separated dictionary names (empty = all)'),
            'THRESHOLD': Parameter(value='0.4', mandatory=True, description='Threshold value'),
            'MATCHONLY': Parameter(value='no', mandatory=True, description='Print only positive matches'),
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        dicts = self.parameters['DICTS'].value.split()
        tags = self.parameters['TAGS'].value.split()
        result = CHECK_SUCCESS
        
        # DICTS EXIST?
        dicts_present = db['dict'].get_dictionaries()
        if dicts_present == DB_ERROR:
            if not silent:
                log.err('Cannot get list of dictionaries.')
            result = CHECK_FAILURE
        
            for d in dicts:
                if d not in dicts_present:
                    if not silent:
                        log.err('\'%s\' dictionary is not in the database.' % (d))
                    result = CHECK_FAILURE
                    
        # TAGS EXIST?
        tags_present = db['dict'].get_tmp_tags()
        if tags_present == DB_ERROR:
            if not silent:
                log.err('Cannot get list of tags from the database.')
            result = CHECK_FAILURE
            for t in tags:
                if t not in tags_present:
                    if not silent:
                        log.err('\'%s\' tag is not in the database.' % (t))
                    result = CHECK_FAILURE
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        tags = self.parameters['TAGS'].value.split() if self.parameters['TAGS'] != '' \
            else db['dict'].get_tmp_tags()
        dicts = self.parameters['DICTS'].value.split()
        matchonly = positive(self.parameters['MATCHONLY'].value)
        if len(dicts) == 0:
            dicts = db['dict'].get_dictionaries()
            if dicts == DB_ERROR:
                log.err('Cannot get list of dictionaries.')
                return None
        
        for d in dicts:
            matches = db['dict'].get_match_percent(d, tags)
            if matches == DB_ERROR:
                log.err('Cannot get results for \'%s\' dictionary' % (d))
                continue
            for match in matches:
                if not silent:
                    if match[2]<float(self.parameters['THRESHOLD'].value):
                        if not matchonly:
                            log.info('%s analysis of %s: %.2f %%' % (match[1], match[0], match[2]*100))
                    else:
                        log.ok('%s analysis of %s: %.2f %%' % (match[1], match[0], match[2]*100))
        return None


lib.module_objects.append(Module())
