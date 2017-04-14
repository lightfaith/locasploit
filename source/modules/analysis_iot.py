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
        self.version = '1.1'
        self.tags = [
            'IoT',
            'Internet of Things',
            'CVE',
            'binwalk',
        ]
        self.description = """This module takes advantage of other modules to scan systems for known vulnerabilities.
Requirements:
    - linux-based extractable image or system running SSH server
    - package manager (such as dpkg, opkg, ...) present

Functionality can be divided in 5 steps:

    1. Extraction
        'iot.binwalk.extract' module is used for this purpose. User supplies image's path and a folder for extraction. Folder path must be absolute, as it will be used as root. Extraction can be skipped by setting the EXTRACT parameter to NO - this is useful if same image is analyzed repeatedly. This phase is skipped when scanning running system.

    2. Root location
        Program guesses the root of the directory tree by searching for etc/passwd file. This phase is skipped when scanning running system.

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
        
        self.dependencies = {
            'iot.binwalk.extract': '1.0',
            'packages.dpkg.installed': '1.0',
            'packages.opkg.installed': '1.0',
            'packages.ipkg.installed': '1.0',
            'connection.ssh': '1.0',
        }
        self.changelog = """
1.1: SSH support
1.0: for linux-based firmware only
     dpkg and opkg managers supported
     vendor is not detected nor taken into consideration, but is mentioned for matched CVEs

"""

        self.reset_parameters()
        self.packathors = ['dpkg', 'opkg', 'ipkg']

    def reset_parameters(self):
        self.parameters = {
            'ACTIVEROOT': Parameter(mandatory=True, description='System to work with'),
            'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
            'METHOD': Parameter(mandatory=True, description='\'local\', \'image\' or \'ssh\''),
            'TARGET': Parameter(mandatory=True, description='File to analyze / SSH connection string'),
            'TMPDIR': Parameter(mandatory=True, description='Absolute path of extraction directory'),
            'ACCURACY': Parameter(value='build', mandatory=True, description='Version match accuracy (none, major, minor, build, full)'),
            'TAG': Parameter(mandatory=True, description='Package info tag'),
            'EXTRACT': Parameter(value='yes', mandatory=True, description='Extraction will happen'),
            'EPOCH': Parameter(value='no', mandatory=True, description='Version epoch will be taken into consideration'),
            'ALIASES': Parameter(value='yes', mandatory=True, description='Also analyze common aliases for packages'),
        }
    

    def check(self, silent=None):
        result = CHECK_PROBABLY
        if silent is None:
            silent = positive(self.parameters['SILENT'].value)
        method = self.parameters['METHOD'].value
        target = self.parameters['TARGET'].value

        # supported method?
        if method not in ['local', 'image', 'ssh']:
            log.err('Unsupported method \'%s\'' % (method))
            result = CHECK_FAILURE

        if method == 'image':
            # check binwalk module
            ibe = lib.modules['iot.binwalk.extract']
            ibe.parameters['ACTIVEROOT'].value = self.parameters['ACTIVEROOT'].value
            ibe.parameters['BINFILE'].value = self.parameters['TARGET'].value
            ibe.parameters['TMPDIR'].value = self.parameters['TMPDIR'].value
            result = min(result, ibe.check())

            # target not a directory TODO

        if method == 'ssh':
            # existing connection?
            c = io.get_ssh_connection(target)
            if c is None:
                log.err('Non-existent SSH connection \'%s\'' % (target))
                result = CHECK_FAILURE
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
        method = self.parameters['METHOD'].value
        target = self.parameters['TARGET'].value
        tmpdir = self.parameters['TMPDIR'].value
        accuracy = self.parameters['ACCURACY'].value
        tag = self.parameters['TAG'].value
        extract = positive(self.parameters['EXTRACT'].value)
        use_epoch = positive(self.parameters['EPOCH'].value)
        use_aliases = positive(self.parameters['ALIASES'].value)
        #outputfile = self.parameters['OUTPUTFILE'].value
        # # # # # # # #
        import time, hashlib

        # 0. Preparation
        tb[tag+'_accuracy'] = accuracy
        tb[tag+'_general'] = []
        tb[tag+'_general'].append(('Date', time.strftime("%d. %m. %Y")))
        if method == 'ssh':
            tb[tag+'_general'].append(('Target', target))
        elif method == 'image':
            path, filename = os.path.split(target)
            tb[tag+'_general'].append(('Target', filename))
            tb[tag+'_general'].append(('Location', path))
            
        tb[tag+'_filesystems'] = []
        exploits = {}
        tb[tag+'_fake_packages'] = [] # like kernel for Debian systems (version is detected, but it is not a package)
        tb[tag+'_alias_packages'] = [] # kernel is defined as linux_kernel in most CVEs
        
        aliases_lines = io.read_file('/', './source/support/package_aliases.csv')
        aliases_lines = [] if aliases_lines == IO_ERROR else aliases_lines.splitlines()
        package_aliases = [tuple(x.split(';')) for x in aliases_lines if x[0] not in ['#'] and len(x.strip()) > 0]

        # 1. Extraction
        if method == 'image':
            log.info('Gathering file stats...')
            tb[tag+'_general'].append(('MD5', io.md5(activeroot, target)))
            tb[tag+'_general'].append(('SHA1', io.sha1(activeroot, target)))
            tb[tag+'_general'].append(('SHA256', io.sha256(activeroot, target)))

            if extract:
                log.info('Extracting firmware...')
                ibe = lib.modules['iot.binwalk.extract']
                ibe.parameters['ACTIVEROOT'].value = activeroot
                ibe.parameters['BINFILE'].value = target
                ibe.parameters['TMPDIR'].value = tmpdir
                ibe.run()
            
            # get extracted dir (last-modified dir with matching name)
            tmpdirs = [x for x in io.list_dir(activeroot, tmpdir, sortby=IOSORT_MTIME) if x.startswith('_%s' % (os.path.basename(target))) and x.endswith('.extracted')]
            if len(tmpdirs) > 0:
                tmpdir = os.path.join(tmpdir, tmpdirs[-1])
            else:
                log.err('Cannot access extract folder.')

            #tmpdir = os.path.join(tmpdir, '_%s.extracted/' % (os.path.basename(target))) # TODO how about rescans?
            log.info('', end='')
            log.attachline('========================', log.Color.BLUE)
            if io.can_read(activeroot, tmpdir):
                log.info('Analyzing data in \'%s\'...' % (tmpdir))
            else:
                log.err('Cannot access %s' % (tmpdir))

            # 2. Root location
            log.info('Looking for directory trees..')
            #found = [x[:-len('/etc/passwd')] for x in io.find(activeroot, tmpdir, 'passwd') if x.endswith('/etc/passwd')]
            found = [x[:-len('/etc')] for x in io.find(activeroot, tmpdir, 'etc') if io.get_system_type_from_active_root(x[:-len('/etc')], verbose=True, dontprint=tmpdir) == 'linux'] 
            if len(found) > 0 and not silent:
                log.ok('Found %d linux directory trees.' % len(found))
        
        if method == 'local':
            found = [target]

        if method == 'ssh':
            found = [target]
        
        tb[tag+'_general'].append(('Aliases enabled', 'YES' if use_aliases else 'NO'))

        fscount = -1
        for f in found:
            fscount+=1
            log.info('', end='')
            log.attachline('------------------------', log.Color.BLUE)
            log.info('Analyzing %s:' % (f))
            data = {} # FS-specific, to be stored in TB

            oses = []
            kernels = []
            pms = []
            users = []
            pusers = []
            crons = []
            startups = []
    
            if method == 'image':
                data['name'] = f[len(tmpdir):]
            elif method == 'ssh':
                data['name'] = f[len(target):]
                if not data['name'].startswith('/'):
                    data['name'] = '/'+data['name']
            else: # in case of new method
                data['name'] = 'UNDEFINED DUE TO WEIRD METHOD'
                
            # System info enumeration
            log.info('Dumping system info...')
            data['system'] = []

            led = lib.modules['linux.enumeration.distribution']
            led.parameters['ACTIVEROOT'].value = f
            led.parameters['SILENT'].value = 'yes'
            led.run()
            issue = db['analysis'].get_data_system('ISSUE', f)
            if len(issue)>0:
                oses.append(('Issue', issue[0][3]))
            releases = db['analysis'].get_data_system('RELEASE', f, like=True)
            for x in releases:
                oses.append((x[1], x[3]))
            
            lek = lib.modules['linux.enumeration.kernel']
            lek.parameters['ACTIVEROOT'].value = f
            lek.parameters['SILENT'].value = 'yes'
            lek.run()
            kernel = db['analysis'].get_data_system('KERNEL', f)
            if len(kernel) > 0:
                kernels.append(kernel[0][3])

            leu = lib.modules['linux.enumeration.users']
            leu.parameters['ACTIVEROOT'].value = f
            # leu.parameters['SILENT'].value = 'yes'
            leu.run()
            users += [x[2] for x in db['analysis'].get_users(f) if x[0] >= 1000]
            pusers += [(x[2] if x[2] == x[2].strip() else '%s' % (x[2])) for x in db['analysis'].get_users(f) if x[0] == 0]

            
            # 3. Package enumeration
            tb[tag+':%d_tmp_packages' % (fscount)] = [] # array for detected packages
            tmp_packages = [] # cause multiple package managers overwrite tmp data in tb
            log.info('Enumerating package managers...')
            for p in self.packathors:
                m = lib.modules['packages.%s.installed' % (p)]
                m.parameters['ACTIVEROOT'].value = f
                m.parameters['TAG'].value = tag+':%d_tmp_packages' % (fscount)
                m.parameters['SILENT'].value = 'yes'
                if m.check() == CHECK_FAILURE:
                    continue
                m.run()
                if len(tb[tag+':%d_tmp_packages' % (fscount)]) == 0:
                    continue
                pms.append(p)
                log.ok('Detected \'%s\' package manager' % (p))
                tmp_packages += tb[tag+':%d_tmp_packages' % (fscount)]
                # add also known aliases for packages (e.g. kernel = linux_kernel)
                # 'kernel' package is present when dealing with opkg or ipkg, so...
                if p in ['opkg', 'ipkg']:
                    if len(kernels) == 0 and tag+':%d_tmp_packages' % (fscount) in tb:
                        kernels += [ps[2] for ps in [x for x in tb[tag+':%d_tmp_packages' % (fscount)] if x[0] == 'kernel']]
                # add kernel as "package" for other package managers
                else:
                    if len(kernels)>0:
                        tmp_packages.append(('kernel', None, kernels[0]))
                        tb[tag+'_fake_packages'].append('kernel')
       
            if len(kernels) == 0:
                kernels.append('UNKNOWN')
            # push gathered data into TB
            
            data['os'] = oses
            data['system'].append(('Kernel', set(kernels)))
            if len(users)>0:
                data['system'].append(('Users', users))
            if len(pusers)>0:
                data['system'].append(('Privileged users', pusers))
            #data['system'].append(('Startup scripts', startups))
            data['system'].append(('Package managers', pms))
            
            log.info('Getting cron data...')
            lec = lib.modules['linux.enumeration.cron']
            lec.parameters['ACTIVEROOT'].value = f
            lec.run()
            crons += db['analysis'].get_cron(f)
        
            data['cron'] = crons

            log.info('Enumerating packages...')
            if use_aliases:
                alias_names, alias_packages = self.get_alias_packages(tmp_packages, package_aliases)
            else:
                alias_names = []
                alias_packages = []
            tb[tag+'_alias_packages'] += alias_names
            data['packages'] = tmp_packages + alias_packages
            del tb[tag+':%d_tmp_packages' % (fscount)]
            packages = []
            if 'packages' in data:
                packages = [(tag+':%d' % (fscount), x[0], x[1], self.get_accurate_version(accuracy, x[2], use_epoch)) for x in data['packages']]

            if len(packages) > 0:
                db['vuln'].add_tmp(packages)
                if not silent:
                    log.ok('Found %d packages.' % (db['vuln'].count_tmp(tag+':%d' % (fscount))))
        
            # 4. CVE detection
            log.info('Detecting CVEs...')
            
            cves = db['vuln'].get_cves_for_apps(tag+':%d' % (fscount), accuracy!='none')
            # accuratize the returned version for report
            cves = [list(x[:2]) + [self.get_accurate_version(accuracy, x[2], use_epoch)] + list(x[3:]) for x in cves]
            #print(cves)
            #print()
            #print(tb[tag+'_packages'])
            # create dictionary of vulnerable packages (cause we want original version to be shown, too)
            vulnerable = {k:v for k in [(x[0], x[1]) for x in cves] for v in [x[2] for x in data['packages'] if x[0] == k[1] and (x[1] == k[0] or x[1] is None)]}
            #print()
            #print(vulnerable)
            cves = [list(x)+[vulnerable[(x[0], x[1])]] for x in cves]
            #print(cves)
            data['cves'] = cves
            if not silent:
                if len(cves)>0:
                    log.ok('Found %d CVEs.' % (len(cves)))
                else:
                    log.info('No CVEs found.')

            # 5. Exploit detection
            log.info('Detecting exploits...')
            for cve in set([x[4] for x in cves]):
                exlist = db['vuln'].get_exploits_for_cve(cve)
                if len(exlist)>0:
                    exploits[cve] = exlist
            
            # nothing? don't report this filesystem
            if len(data['cves'])+len(data['packages'])+len(oses+users+pusers+crons+startups) == 0 and 'UNKNOWN' in kernels:
                continue
            tb[tag+'_filesystems'].append(data)

        log.attachline('------------------------', log.Color.BLUE)
        if len(exploits)>0:
            if not silent:
                log.ok('%d exploits found.' % (len(set([x for _,v in exploits.items() for x in v]))))
            tb[tag+'_exploits'] = exploits
        # # # # # # # #
        return None
    


    def get_alias_packages(self, packages, known):
        alias_matches = []
        result = []
        for k in known:
            for p in packages:
                if p[0] in k:
                    aliases = [(x, p[1], p[2]) for x in k if x != p[0]]
                    alias_matches += [x[0] for x in aliases]
                    result += aliases
                    break
        return alias_matches, result


    def get_accurate_version(self, accuracy, version, use_epoch):
        #print('[ ] Getting "%s" version of "%s": ' % (accuracy, version), end='')
        #if accuracy != 'full' and accuracy != 'none':
        # deal with epoch
        if use_epoch:
            version = version.replace(':', '.')
        else:
            if ':' in version:
                version = version.partition(':')[2]

        if accuracy == 'none':
            return ''
        if accuracy in ['major', 'minor', 'build']:
    
            majorparts = version.partition('.')
            if accuracy in ['major', 'minor', 'build'] and majorparts[0].isdigit():
                version = majorparts[0].partition('-')[0]
            minorparts = majorparts[2].partition('.')
            if accuracy in ['minor', 'build'] and minorparts[0] != '': 
                version = '.'.join([majorparts[0], minorparts[0].partition('-')[0]])
            buildparts = minorparts[2].partition('.')
            if accuracy == 'build' and buildparts[0] != '': 
                version = '.'.join([majorparts[0], minorparts[0], buildparts[0].partition('-')[0]])
        #print(version)
        return version


lib.module_objects.append(Module())
