#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'network.scanner.passive'
        self.short_description = 'Detects connected devices by passive listening.'
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
            'eth', 'eth0', 'l0', 'wlan', 'wlan0', 'loopback',
            'NIC',

        ]
        self.description = """
This module detects devices by passively listening to the traffic. It needs scapy to operate.
"""
        self.db_access = [
            'NETWORK',
            'INTERFACES',
            'HOSTS',
        ]
        
        self.dependencies = {
            'network.enumeration.interfaces': '1.0',
        }
        self.changelog = """
"""

        self.reset_parameters()

    def reset_parameters(self):
        self.parameters = {
            'ACTIVEROOT': Parameter(mandatory=True, description='System to work with'),
            'SILENT': Parameter(value='yes', mandatory=True, description='Suppress the output'),
            'BACKGROUND' : Parameter(value='yes', mandatory=True, description='yes = run in background, no = wait for it...'),
            'TIMEOUT' : Parameter(value='30', mandatory=True, description='Number of seconds to listen'),
            'INTERFACE' : Parameter(value='', mandatory=False, description='Interface to listen on (default: all)'),
        }

    def check(self, silent=None):
        result = CHECK_SUCCESS
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        root = self.parameters['ACTIVEROOT'].value
        # # # # # # # #
        # check parameteres
        
        if not positive(self.parameters['BACKGROUND'].value) and not negative(self.parameters['BACKGROUND'].value):
            log.err('Bad %s value: %s.', 'BACKGROUND', self.parameters['BACKGROUND'].value)
            return CHECK_FAILURE
        if not self.parameters['TIMEOUT'].value.isdigit() or int(self.parameters['TIMEOUT'].value) < 0:
            log.err('Bad timeout value: %d', int(self.parameters['TIMEOUT'].value))
            return CHECK_FAILURE
        # # # # # # # #
        # check scapy and tcpdump support
        if not command_exists(root, 'scapy'):
            if not silent:
                log.err('Scapy is needed to run this module.')
            result = CHECK_FAILURE
        if not command_exists(root, 'tcpdump'):
            if not silent:
                log.err('Tcpdump is needed to run this module.')
            result = CHECK_FAILURE
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        iface = self.parameters['INTERFACE'].value

        """ # TODO save into DB
        if iface != '' and not lib.kb.exists(('NETWORK INTERFACES %s' % iface).split(' ')):
            # run network.enumeration.interfaces first
            if not silent:
                log.info('Detecting existing interfaces...')
            nei = lib.modules['network.enumeration.interfaces']
            nei.parameters['SILENT'].value = 'yes'
            nei.Run()
        
        # check whether interface (if needed) is present
        if iface != '' and not lib.kb.exists(('NETWORK INTERFACES %s' % iface).split(' ')):
            log.err('Interface \'%s\' does not exist.' % iface)
            return None
        """
        



        # # # # # # # #
        t = Thread(silent, int(self.parameters['TIMEOUT'].value), iface)
        t.start()
        if positive(self.parameters['BACKGROUND'].value):
            return t
        t.join()
        # # # # # # # #
        return None
    
        
class Thread(threading.Thread):
    def __init__(self, silent, timeout, iface):
        threading.Thread.__init__(self)
        self.silent = silent
        self.timeout=timeout
        self.terminate = False
        self.scapy = importlib.import_module('source.support.myscapy')
        self.iface = iface
        self.hosts = {}
    
    # starts the thread
    def run(self):
        if not self.silent:
            log.info('Passive reconnaisance has started.')
        if self.iface == '':
            self.scapy.sniff(prn=self.process, filter='ip or arp', store=0, timeout=self.timeout, stopper=self.stopper)
        else:
            self.scapy.sniff(iface=self.iface, prn=self.process, filter='ip or arp', store=0, timeout=self.timeout, stopper=self.stopper)
        # update knowledge base
        #TODO db
        """
        for x in self.hosts:
            lib.kb.add('NETWORK HOSTS %s' % (x), self.hosts[x])
        """

    # terminates the thread
    def stop(self):
        self.terminate = True
    
    # here every captured packet will be dealt with
    def process(self, packet):
        scapy = self.scapy
        ip=None
        if not packet.haslayer(scapy.Ether):
            return
        mac=packet.getlayer(scapy.Ether).src
        if packet.haslayer(scapy.IP):
            ip=packet['IP'].src
        if packet.haslayer(scapy.ARP):
            mac=packet['ARP'].hwsrc
            ip=packet['ARP'].psrc
        if mac=='00:00:00:00:00:00':
            return
        if ip is None:
            return
        #TODO check 0.0.0.0, local, remote etc.
        #TODO put in KB
        if not self.silent:
            log.ok('%s - %s' % (ip, mac))
        
        if ip not in self.hosts:
            self.hosts[ip] = {}
            self.hosts[ip]['ip'] = ip
            self.hosts[ip]['mac'] = []
        
        if mac not in self.hosts[ip]['mac']:
            self.hosts[ip]['mac'].append(mac)
    # tells scapy to stop sniffing prematurely
    def stopper(self):
        return self.terminate

lib.module_objects.append(Module())
