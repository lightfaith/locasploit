#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
    def __init__(self):
        self.authors = [
            Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
        ]
        
        self.name = 'analysis.iot'
        self.short_description = 'Scans image for known vulnerabilities.'
        self.references = [
            '',
        ]
        
        self.date = '2016-11-06'
        self.license = 'GNU GPLv2'
        self.version = '1.0'
        self.tags = [
            'IoT',
            'Internet of Things',
            'CVE',
            'binwalk',
        ]
        self.description = """This module takes advantage of other modules to scan files for known vulnerabilities.
Requirements:
    - linux-based image
    - package manager (such as dpkg, opkg, ...) present

Functionality can be divided in 5 steps:

    1. Extraction
        'iot.binwalk.extract' module is used for this purpose. User supplies image's path and a folder for extraction. Folder path must be absolute, as it will be used as root.

    2. Root location
        Program guesses the root of the directory tree by searching for etc/passwd file.

    3. Package enumeration
        'package.*.install' modules will be used for this purpose. Results are stored in <TAG>_packages. Accuracy of package versions can be altered by the ACCURACY parameter.

        Let's say detected version is '0.9.8j-r13.0.4'. Then following values for ACCURACY will match different entries:
            none  - version is completely ignored, matching will be only based on package names
            major - version '0' will be tested
            minor - version '0.9' will be tested
            build - version '0.9.8j' will be used
            full  - only entries describing version '0.9.8j-r13.0.4' will match

        For non-standard versioning, full accuracy will be used (unless 'none' ACCURACY is chosen).

    4. CVE detection
        CVEs which match packages will be listed and saved into Temporary Base as <TAG>_cves.

    At this point, all data are ready to be processed by report.iot and report.iot.diff modules.
"""
        self.db_access = [
        ]
        
        self.dependencies = {
            'iot.binwalk.extract': '1.0',
            'packages.dpkg.installed': '1.0',
            'packages.opkg.installed': '1.0',
            'report.iot': '1.0',
        }
        self.changelog = """
1.0: for linux-based firmware only
     dpkg and opkg managers supported
     vendor is not detected nor taken into consideration, but is mentioned for matched CVEs

"""

        self.reset_parameters()
        self.packathors = ['dpkg', 'opkg']

    def reset_parameters(self):
        self.parameters = {
            'ACTIVEROOT': Parameter(mandatory=True, description='System to work with'),
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'BINFILE': Parameter(mandatory=True, description='File to analyze'),
            'TMPDIR': Parameter(mandatory=True, description='Absolute path of extraction directory'),
            'ACCURACY': Parameter(value='build', mandatory=True, description='Version match accuracy (none, major, minor, build, full)'),
            'TAG': Parameter(mandatory=True, description='Package info tag'),
            #'OUTPUTFILE': Parameter(mandatory=True, description='Report path'),

        }
    

    def check(self, silent=None):
        result = CHECK_PROBABLY
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        # check modules
        ibe = lib.modules['iot.binwalk.extract']
        ibe.parameters['ACTIVEROOT'].value = self.parameters['ACTIVEROOT'].value
        ibe.parameters['BINFILE'].value = self.parameters['BINFILE'].value
        ibe.parameters['TMPDIR'].value = self.parameters['TMPDIR'].value
        result = min(result, ibe.check())

        #ri = lib.modules['report.iot']
        #ri.parameters['TAG'].value = self.parameters['TAG'].value
        #ri.parameters['OUTPUTFILE'].value = self.parameters['OUTPUTFILE'].value
        #result = min(result, ri.check())

        #for p in self.packathors:
        #    m = lib.modules['packages.%s.installed' % (p)]
        #    m.parameters['ACCURACY'].value = self.parameters['ACCURACY'].value
        #    m.parameters['TAG'].value = self.parameters['TAG'].value
        #    result = min(result, m.check())
        # TODO !!!!!! REVALIDATE !!!!
        return result
    
    def run(self):
        silent = positive(self.parameters['SILENT'].value)
        activeroot = self.parameters['ACTIVEROOT'].value
        binfile = self.parameters['BINFILE'].value
        tmpdir = self.parameters['TMPDIR'].value
        accuracy = self.parameters['ACCURACY'].value
        tag = self.parameters['TAG'].value
        #outputfile = self.parameters['OUTPUTFILE'].value
        # # # # # # # #
        import time, hashlib

        # 1. Extraction
        log.info('Gathering file stats...')
        tb[tag+'_general'] = []
        tb[tag+'_general'].append(('Date', time.strftime("%d. %m. %Y")))
        tb[tag+'_general'].append(('File', binfile))
        tb[tag+'_general'].append(('MD5', io.md5(activeroot, binfile)))
        tb[tag+'_general'].append(('SHA1', io.sha1(activeroot, binfile)))
        tb[tag+'_general'].append(('SHA256', io.sha256(activeroot, binfile)))

        
        log.info('Extracting firmware...')
        ibe = lib.modules['iot.binwalk.extract']
        ibe.parameters['ACTIVEROOT'].value = activeroot
        ibe.parameters['BINFILE'].value = binfile
        ibe.parameters['TMPDIR'].value = tmpdir
        #ibe.run()
        
        # 2. Root location
        log.info('Looking for directory trees..')
        found = [x[:-len('/etc/passwd')] for x in io.find(activeroot, tmpdir, 'passwd') if x.endswith('/etc/passwd')]
        if len(found) > 0 and not silent:
            log.ok('Found %d linux directory trees.' % len(found))

        oses = []
        kernels = []
        pms = []
        users = []
        pusers = []
        crons = []
        startups = []

        for f in found:
            # System info enumeration
            log.info('Dumping system info...')
            tb[tag+'_system'] = []

            leu = lib.modules['linux.enumeration.users']
            leu.parameters['ACTIVEROOT'].value = f
            leu.run()
            users += [x[2] for x in db['analysis'].get_users(f) if x[0] >= 1000]
            pusers += [(x[2] if x[2] == x[2].strip() else '%s' % (x[2])) for x in db['analysis'].get_users(f) if x[0] == 0]

            
            # 3. Package enumeration
            log.info('Enumerating packages...')
            for p in self.packathors:
                m = lib.modules['packages.%s.installed' % (p)]
                m.parameters['ACTIVEROOT'].value = f
                m.parameters['TAG'].value = tag+'_packages'
                #m.parameters['SILENT'].value = 'no'
                m.parameters['SILENT'].value = 'yes'
                if m.check() == CHECK_FAILURE:
                    continue
                pms.append(p)
                log.info('Detected \'%s\' package manager' % (p))
                m.parameters['SILENT'].value = 'yes'
                m.run()
        
            tb[tag+'_system'].append(('OS', oses))
            tb[tag+'_system'].append(('Kernel', kernels))
            tb[tag+'_system'].append(('Users', users))
            tb[tag+'_system'].append(('Privileged users', pusers))
            #tb[tag+'_system'].append(('Cron entries', crons))
            tb[tag+'_system'].append(('Startup scripts', startups))
            tb[tag+'_system'].append(('Package managers', pms))
            
            log.info('Getting cron data...')
            lec = lib.modules['linux.enumeration.cron']
            lec.parameters['ACTIVEROOT'].value = f
            lec.run()
            crons += db['analysis'].get_cron(f)
        
        tb[tag+'_cron'] = crons

        packages = [(tag, x[0], x[1], self.get_accurate_version(accuracy, x[2])) for x in tb[tag+'_packages']]

        db['vuln'].add_tmp(packages)
        if not silent:
            log.ok('Found %d packages.' % (db['vuln'].count_tmp(tag)))
        
        # 4. CVE detection
        log.info('Detecting CVEs...')
        
        cves = db['vuln'].get_cves_for_apps(tag, accuracy!='none')
        #print(cves)
        #print()
        #print(tb[tag+'_packages'])
        # create dictionary of vulnerable packages (cause we want original version to be shown, too)
        vulnerable = {k:v for k in [(x[0], x[1]) for x in cves] for v in [x[2] for x in tb[tag+'_packages'] if x[0] == k[1] and (x[1] == k[0] or x[1] is None)]}
        #print()
        #print(vulnerable)
        cves = [list(x)+[vulnerable[(x[0], x[1])]] for x in cves]
        #print(cves)
        tb[tag+'_cves'] = cves
        if not silent:
            log.ok('Found %d CVEs.' % (len(cves)))

        ## 5. Report generation
        #log.info('Generating report...')
        #ri = lib.modules['report.iot']
        #ri.parameters['OUTPUTFILE'].value = outputfile
        #ri.parameters['TAG'].value = tag
        #ri.run()
        #log.ok('Report generated!')
        # # # # # # # #
        return None
    
    def get_accurate_version(self, accuracy, version):
        if accuracy != 'full' and accuracy != 'none':
            # some alteration, TODO check
            if ':' in version:
                version = version.partition(':')[2]
    
            majorparts = version.partition('.')
            if accuracy in ['major', 'minor', 'build'] and majorparts[0].isdigit():
                version = majorparts[0]
            minorparts = majorparts[2].partition('.')
            if accuracy in ['minor', 'build'] and minorparts[0] != '': 
                version = '.'.join([majorparts[0], minorparts[0]])
            buildparts = minorparts[2].partition('.')
            if accuracy == 'build' and buildparts[2] != '': 
                version = '.'.join([majorparts[0], minorparts[0], buildparts[0]])
        return version


lib.module_objects.append(Module())
