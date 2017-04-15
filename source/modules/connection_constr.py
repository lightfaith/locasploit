#!/usr/bin/env python3
"""
This module creates connection based on connection string.
"""
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        super().__init__()
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'connection.constr'
        self.short_description = 'Creates a connection according to connection string.'
        self.references = [
        ]
        self.date = '2017-04-15'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'SSH',
            'connection',
            'string',
            'constr',
        ]
        
        
        self.description = """This module calls other connection modules according to CONSTR parameter (for example 'ssh://root@localhost:22/'). Method is passed to desired connection modules.
"""
        
        self.dependencies = {
            'connection.ssh': '1.0',
        }
        self.changelog = """
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'METHOD': Parameter(mandatory=False, description='Method (argument to final module)'),
            'CONSTR': Parameter(mandatory=True, description='Connection string')
        }

    def check(self, silent=None):
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        result = CHECK_NOT_SUPPORTED
        return result

    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        method = self.parameters['METHOD'].value
        constr = self.parameters['CONSTR'].value

        if constr.startswith('ssh://'):
            tmpparts = constr[6:].partition('@')
            user = tmpparts[0]
            if len(user)<=0:
                log.err('User not specified in \'%s\'.' % (constr))
                return None
                
            tmpparts = tmpparts[2].rpartition(':')
            host = tmpparts[0]
            if len(host)<=0:
                log.err('Host not specified in \'%s\'.' % (constr))
                return None

            tmpparts = tmpparts[2].partition('/')
            port = tmpparts[0]
            if not (port.isdigit() and int(port)>0 and int(port)<=65535):
                log.err('Port not specified in \'%s\'.' % (constr))
                return None
            
            cs = lib.modules['connection.ssh']
            cs.parameters['METHOD'].value = method
            cs.parameters['HOST'].value = host
            cs.parameters['PORT'].value = port
            cs.parameters['USER'].value = user
            if cs.check(silent) == CHECK_FAILURE:
                log.err('Connection to \'%s\' cannot be established.' % (constr))
            else:
                cs.run()
        else: 
            log.err('Connection to ''%s'' failed (unknown type).' % (constr))
        return None

lib.module_objects.append(Module())

