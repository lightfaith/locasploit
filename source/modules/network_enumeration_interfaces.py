#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'network.enumeration.interfaces'
        self.short_description = 'Detects network interfaces.'
        self.references = [
            '',
        ]
        
        self.date = '2016-01-28'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'network',
            'enumeration',
            'interface', 'interfaces',
            'netifaces',
            'eth', 'eth0', 'l0', 'wlan', 'wlan0', 'loopback'
            'NIC',

        ]
        self.description = """
This module detects local network interfaces and writes them into the Knowledge Base. It needs 'netifaces' to work.
"""
        self.db_access = [
            'NETWORK',
            'INTERFACES',
        ]
        
        self.dependencies = {
        }
        self.changelog = """
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
        }

    def check(self, silent=None):
        result = CHECK_SUCCESS
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        try:
            import netifaces as n
        except:
            if not silent:
                log.err('Python-netifaces is needed to run this module.')
            result = CHECK_FAILURE
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        
        import netifaces as n
        ifs = n.interfaces()
        result = {}
        for iface in  ifs:
            afs = {}
            for ad in n.ifaddresses(iface):
                afs[n.address_families[ad]] = n.ifaddresses(iface)[ad]
            result[iface] = afs
        
        #output
        if not silent:
            for interface in result:            
                log.ok('%s:' % interface)
                for afamily in result[interface]:
                    log.ok('    %s:' %afamily)
                    for addressid in range(0, len(result[interface][afamily])):
                        log.ok('        address %d:' % addressid)
                        address = result[interface][afamily][addressid]
                        for key in address:
                            log.ok('            %s = %s' % (key, address[key]))

        #lib.kb.add('NETWORK INTERFACES', result)
        for x in result:
            lib.kb.add('NETWORK INTERFACES %s' % (x), result[x])
        # # # # # # # #
        return None
    

lib.module_objects.append(Module())
