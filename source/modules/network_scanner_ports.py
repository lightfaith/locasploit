#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'network.scanner.ports'
        self.short_description = 'Scans hosts for open ports.'
        self.references = [
            '',
        ]
        
        self.date = '2016-01-27'
        self.license = 'GNU GPLv2'
        self.version = '0.0'
        self.tags = [
            'network',
            'scanner', 'scan', 'scanning',
            'port', 'ports',
            'nmap',
            'syn', 'fin', 'ack', 'xmas', 'null', 'tcp', 'udp', 'win',
            'open', 'closed', 'filtered'

        ]
        self.description = """
This module uses scapy to provide popular port enumeration methods. namely:
    SYN Scan
    TCP Scan
    UDP Scan
    FIN Scan
    NULL Scan
    XMAS Scan
    ACK Scan
    Window Scan
"""
        self.db_access = [
            'NETWORK',
            'HOSTS',
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
        if not command_exists('scapy'): # TODO ACTIVEROOT
            if not silent:
                log.err('Scapy is needed to run this module.')
            result = CHECK_FAILURE
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        # # # # # # # #
        # Define your code here
        log.err('Not implemented yet.')
        # # # # # # # #
        return None
    

lib.module_objects.append(Module())
