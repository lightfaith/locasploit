#!/usr/bin/env python3
from source.modules._generic_module import *

# File should be named according to its name (it is not mandatory, but it is good for clarity). It must have a .py extension.
# It would be cool if you follow naming conventions:
        #   analysis_*    - modules performing complex analysis of something (possibly using other modules)
        #   locasploit_*  - modules operating on locasploit itself (like dict import etc.)
        #   private_*     - (test) modules which are not supposed to be published (ignored by Git automatically)
        #   report_*      - modules generating nice PDF (and other) reports

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            # Define all authors of this module here. Email and Web is optional.
            Author(name='', email='', web=''),
        ]
        
        # Module name must be unique and should be in dot notation (e.g. linux.enumeration.distribution).
        # For clarity, the file name should be the same, with dots replaced by underscores (_) and .py extension. 
        # Do not use search symbols (brackets, ~, |, &)
        
        self.name = 'template'
        # Use this field as a SHORT description. This will be shown when modules are listed.
        self.short_description = 'Serves as a module template.'
        # Here you can specify links to books, blogs, whitepapers, CVEs etc.
        self.references = [
            '',
        ]
        # Specify the date in exactly this format (yyyy-mm-dd). This can be used for searching or sorting.
        self.date = '2999-12-31'
        # You can define the license of the module here.
        self.license = 'GNU GPLv2'
        # If any change affecting functionality or output is made after publishing, you must change the version.
        self.version = '0.0'
        # Tags are useful for searching. Do not use search keywords and symbols (and, not, or, &, |, !, brackets)
        self.tags = [
            'template',
        ]
        # This is long description. You can (and should) write anything important and useful here. You should define what the module does, what files it access and whether it can do harm.
        self.description = """
This module is designed to be used as a template for new modules. 
Tired of the comments? Check the "basic" module.
"""
        
        # If other modules are run directly from this module, you must specify the name and version. Dependencies will be checked for existence prior to execution.
        self.dependencies = {
            #'linux.enumeration.distribution': '1.0',
        }
        # If you like to redefine the modules frequently, consider to write some changelog.
        self.changelog = """
"""

        self.reset_parameters() # just leave it here

    def reset_parameters(self):
        # Define module parameters here. You should use UPPERCASE letters as a name. If value is not inialized and a global parameter with the same name exists, its value is used. Do not use spaces.
        # Always define SILENT parameter and do not print anything (except cricital errors) if positive(self.parameters['SILENT'].value) - this is for intermodular calls.
        # Check boolean values using positive() and negative() functions, so user can choose between multiple possible answers (e.g. yes, true, 1, +, ...)

        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'ACTIVEROOT': Parameter(mandatory=True, description='System to work with'), # usually set automatically; '/' - local system
        }

    def check(self, silent=None):
        # Perform checks to determine whether the module can succeed/be executed and make sure one of the following constants is returned:
        # CHECK_SUCCESS       - this module will do exactly what it is designed for (e.g. successful exploit)
        # CHECK_PROBABLY      - it will probably work
        # CHECK_NOT_SUPPORTED - nothing can be checked, but it may work
        # CHECK_UNLIKELY      - module can be executed, but it will probably fail (e.g. exploit against hardened system)
        # CHECK_FAILURE       - module cannot be executed (missing files, bad parameters etc.)
        
        # Check is performed automatically before the module is executed. 
        # Do not use any dependencies. # TODO why?
        # If the module is not meant to run as silent, you should print error and warning messages.
        # Do not print any other messages.
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        result = CHECK_NOT_SUPPORTED
        # You should not "return CHECK_FAILURE", set "result = CHECK_FAILURE" and then "return result" instead.
        # This allows user to see all problems at once.
        return result
    
    def run(self):
        # Always print error and warning messages.
        # If the module is not meant to run as silent, you can print info and success messages.
        silent = positive(self.parameters['SILENT'].value)
        # # # # # # # #
        # Define your code here
        if not silent:
            log.ok('Template module says: "Hello World!"')
        # # # # # # # #
        # If the module should terminate, return None. If it should run in the background, return the instance of the thread (see thread.py template).
        return None 
    

lib.module_objects.append(Module()) # just leave it here
