#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'crypto.bruteforce'
        self.short_description = 'Bruteforces hashex.'
        self.references = [
        #   '',
        ]
        
        self.date = '2016-12-08'
        self.license = 'GNU GPLv2'
        self.version = '0.0'
        self.tags = [
            'brute',
            'force', 
        ]
        self.algorithms = [
            'md5',
        ]
        self.description = """
This module performs bruteforce on values stored in TB.
Multiple values must be space-separated.

Currently supported algorithms:
"""+'\n'.join(['   %s' % x for x in self.algorithms])
        
        self.dependencies = {
        }
        self.changelog = """
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'INPUTKEY': Parameter(mandatory=True, description='Temporary base key of hashes'),
            'OUTPUTKEY': Parameter(mandatory=True, description='Temporary base key for results'),
            'ALGORITHM': Parameter(mandatory=True, description='Algorithm'),
            'ALPHABET': Parameter(mandatory=True, description='Characters to test'),
            'MINLENGTH': Parameter(mandatory=True, description='Minimal length'),
            'MAXLENGTH': Parameter(mandatory=True, description='Maximal length'),
            'STOPONMATCH': Parameter(value='yes', mandatory=True, description='Execution is terminated on first match'),
            
        }

    def check(self, silent=None):
        if silent is None:
           silent = positive(self.parameters['SILENT'].value)
        key = self.parameters['INPUTKEY'].value
        algorithm = self.parameters['ALGORITHM'].value
        minlength = self.parameters['MAXLENGTH'].value
        maxlength = self.parameters['MINLENGTH'].value
        result = CHECK_PROBABLY
        
        # bad algorithm?
        if algorithm.lower() not in self.algorithms:
            if not silent:
                log.err('Algorithm \'%s\' is not supported.' % algorithm)
            result = CHECK_FAILURE
        # KEY exists? Value is string or list?
        if key not in lib.tb.keys():
            if not silent:
                log.err('Key \'%s\' is not present in the Temporary base.' % (key))
            result = CHECK_FAILURE
        elif type(lib.tb[key]) not in [str, list]:
            if not silent:
                log.err('Value of key \'%s\' is not a string nor list.' % (key))
            result = CHECK_FAILURE
        # min max ok?
        if not minlength.isdigit():
            if not silent:
                log.err('MINLENGTH is not a digit.')
            result = CHECK_FAILURE
        if not maxlength.isdigit():
            if not silent:
                log.err('MINLENGTH is not a digit.')
            result = CHECK_FAILURE
        if not minlength.isdigit() and maxlength.isdigit() and int(minlength) > int(minmax):
            if not silent:
                log.err('MINLENGTH should be smaller than MAXLENGTH.')
            result = CHECK_FAILURE
        # can import?
        try:
            import itertools
        except:
            if not silent:
                log.err('Cannot import itertools.')
            result = CHECK_FAILURE
        try:
            import hashlib
        except:
            if not silent:
                log.err('Cannot import hashlib.')
            result = CHECK_FAILURE
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        inputkey = self.parameters['INPUTKEY'].value
        outputkey = self.parameters['OUTPUTKEY'].value
        algorithm = self.parameters['ALGORITHM'].value.lower()
        alphabet = self.parameters['ALPHABET'].value
        minlength = int(self.parameters['MINLENGTH'].value)
        maxlength = int(self.parameters['MAXLENGTH'].value)
        stoponmatch = positive(self.parameters['STOPONMATCH'].value)
        
        import itertools, hashlib
        f = {
            'md5': hashlib.md5,
        }
        
        values = lib.tb[inputkey].split()
        
        results = {k: None for k in values}
            
        log.info('Bruteforcing words of alphabet \'%s\' of length %d - %d.' % (alphabet, minlength, maxlength))
        
        repeats = range(minlength, maxlength+1)
        for repeat in repeats:
            for pchars in itertools.product(alphabet, repeat=repeat):
                password = ''.join(pchars).encode('utf-8')
                h = f[algorithm](password).hexdigest()
                #print('Password: ', password)
                if h in results.keys():
                    if not silent:
                        log.ok('Found match: %s(%s) = %s' % (algorithm, password.decode('utf-8'), h))
                    results[h] = password
                    if stoponmatch and len([x for x in results.values() if x is None]) == 0:
                        break
            if stoponmatch and len([x for x in results.values() if x is None]) == 0:
                break
        print(results)
        lib.tb['OUTPUTKEY'] = results
        # # # # # # # #
        return None
    

lib.module_objects.append(Module())
