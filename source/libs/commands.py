#!usr/bin/env python3
from source.libs.include import *
from source.libs.include import command as cmd
from source.libs.define import *
#import source.libs.author
from source.libs.search import *
from source.libs.db import *
#import source.libs.log

def execute_command(command):
    command = command.strip()
    lib.command_history.append(command)

    # any $variables present? replace it with tb (or global parameter) value
    newcommand = []
    parts = command.split(' ')
    for part in parts:
        if part.startswith('$'):
            # key present?
            if part[1:] in tb.keys():
                newcommand.append(tb[part[1:]])
            elif part[1:] in global_parameters.keys():
                newcommand.append(global_parameters[part[1:]])
            else:
                log.err('Key \'%s\' is not present in Temporary Base or Global Parameters.' % (part[1:]))
                pass
        else:
            # escaped $?
            if part.startswith('\$'):
                part = part[1:]
            newcommand.append(part)
    command = ' '.join(newcommand)

    # # # # # # # # # 
    # OK, what to do?
    # # # # # # # # #
    
    # system command
    if command.startswith('!'):
        result = cmd(command[1:])
        log.writeline(result)
    
    # test playground
    elif command == 'test':
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import KeepTogether, SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        styles = getSampleStyleSheet()
        
        #c = canvas.Canvas('test.pdf')
        doc = SimpleDocTemplate('test.pdf', pagesize=A4)
        entries = []
        for c in cves:
            if c[3] == '2.0': # CVSS 2.0
                data = [['', c[0], c[1]+' '+c[2], 'Base:', c[5]], ['', '', '', 'Impact:', c[6]], ['', '', '', 'Exploitability:', c[7]], ['', '', '', 'Score:', c[4]], [Paragraph('<para align=justify>'+c[9]+'</para>', styles['BodyText']), '', '', '', ''], ['', '', '', '']]
            t = Table(data, colWidths=(0.5*cm, 8*cm, 5*cm, 3*cm, 2*cm))
            color = colors.yellow # low severity
            if c[8] == 'Medium':
                color = colors.orange
            elif c[8] == 'High':
                color = colors.lavender
            t.setStyle(TableStyle([
                #('GRID', (0, -2), (-1, -2), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                #('BACKGROUND', (0, 0), (-1, 3), color),
                ('BACKGROUND', (0, 0), (0, 3), color),
                #('LINEBEFORE', (-1, 0), (-1, -3), 1, color),
                #('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.black),
                #('LINEABOVE', (0, -2), (-1, -2), 1, colors.black),
                ('SPAN', (0, -2), (-1, -2)), # description
                ('SPAN', (1, 0), (1, -3)), # cve
                ('SPAN', (2, 0), (2, -3)), # package
            ]))
            entries.append(KeepTogether(t))
        doc.build(entries)
        #c.showPage()
        #c.save()
        print('-' * 20)
    
    # help
    elif command == 'help':
        print_help()
    
    # reload modules
    elif command == 'reload':
        load_modules()
        lib.prompt = ' >  '
        lib.active_module = None

    # list modules
    elif command in ['list', 'ls']:
        print_modules(list(lib.modules))
    
    # list modules sorted by date
    elif command in ['list date', 'ls date']:
        print_modules(list(lib.modules), order_by_date=True)
    
    # module search
    elif command[:7] == 'search ':
        if len(command[7:].split(' ')) == 1 and not re.search('[!|&\(\)]', command[7:]):
            # simple search, group by categories
            if command[7] in ['>', '<', '='] and len(command[8:]) == 4 and command[8:].isdigit(): # date
                year = int(command[8:])
                by_year = []
                for m in lib.modules:
                    myear = int(lib.modules[m].date[:4]) if lib.modules[m].date[:4].isdigit() else 0
                    if (command[7] == '<' and myear <= year) or (command[7]=='>' and myear>=year) or (command[7]=='=' and myear==year):
                        by_year.append(m)
                print_modules(by_year)
                log.writeline('')

            else: # not a year, an expression
                modules = lib.modules
                
                # search by module
                by_module_tmp = search_abbr(command[7:].lower(), [x.lower() for x in list(modules)]) + [x for x in modules if command[7:].lower() in x.lower()]
                by_module = []
                for x in by_module_tmp:
                    if x not in by_module:
                        by_module.append(x)
                if len(by_module) > 0:
                    log.attachline('By module:', log.Color.PURPLE)
                    print_modules(by_module)
                    log.writeline('')
        
                # search by tag
                by_tag = [x for x in modules if command[7:].lower() in [y.lower() for y in modules[x].tags]]
                if len(by_tag) > 0:
                    log.attachline('By tags:', log.Color.PURPLE)
                    print_modules(by_tag)
                    log.writeline('')
        
                
                # search by parameter
                by_parameter = [x for x in modules if command[7:].lower() in [y.lower() for y in modules[x].parameters]]
                if len(by_parameter) > 0:
                    log.attachline('By parameters:', log.Color.PURPLE)
                    print_modules(by_parameter)
                    log.writeline('')
            
                # search by author
                by_author = [x for x in modules for authors in modules[x].authors if command[7:].lower() in authors.name.lower() or command[7:].lower() in authors.email.lower() or command[7:].lower() in authors.web.lower()]
                if len(by_author) > 0:
                    log.attachline('By authors:', log.Color.PURPLE)
                    print_modules(by_author)
                    log.writeline('')
                
                # search by knowledge base
                by_db = [x for x in modules if command[7:].upper() in [y.upper() for y in modules[x].db_access]]
                if len(by_db) > 0:
                    log.attachline('By Knowledge Base:', log.Color.PURPLE)
                    print_modules(by_db)
                    log.writeline('')
                
                # search by dependency
                by_dependency = [x for x in modules if len(search_abbr(command[7:].lower(), [y.lower() for y in list(modules[x].dependencies)])) > 0]
                if len(by_dependency) > 0:
                    log.attachline('By dependencies:', log.Color.PURPLE)
                    print_modules(by_dependency)
                    log.writeline('')

                # search by version
                by_version = [x for x in modules if command[7:].lower() == modules[x].version.lower()]
                if len(by_version) > 0:
                    log.attachline('By version:', log.Color.PURPLE)
                    print_modules(by_version)
                    log.writeline('')

        else: # complicated search, use search()
            print_modules(search(command[7:]))

    # module selection
    elif command[0:4] == "use " and len(command)>4:
        set_module(command[4:].strip())
    
    # back to root
    elif command == 'back':
        lib.prompt = ' >  '
        lib.active_module = None

    # use previous module
    elif command in ['prev', 'previous']:
        if lib.active_module is None:
            if len(lib.module_history)>0:
                set_module(lib.module_history[-1])
        else:
            if len(lib.module_history)>1:
                set_module(lib.module_history[-2])
    
    # module info
    elif command == 'info':
        print_module_info()

    # show options
    elif command == 'show options' or command == 'show parameters':
        print_module_info(basics=False, authors=False, description=False, references=False, tags=False, db=False, dependencies=False, dependent=False, changelog=False)
    
    # show only undefined options
    elif command == 'show missing':
        print_module_info(basics=False, authors=False, description=False, references=False, tags=False, db=False, dependencies=False, dependent=False, changelog=False, missing=True)

    # show global options
    elif command == 'getg':
        maxp = max([4]+[len(x) for x in lib.global_parameters])
        log.writeline('%-*s  %s' % (maxp, 'NAME', 'VALUE'))
        log.writeline('%s  %s' % ('-' * maxp, '-' * 5), log.Color.PURPLE)
        for p in natural_sort(lib.global_parameters.keys()):
            log.writeline('%-*s  %s' % (maxp, p, lib.global_parameters[p]))

    # set global option
    elif command[:5] == 'setg ':
        command = command.replace('=', ' ')
        try:
            spaceindex = command[5:].index(' ')
        except ValueError:
            log.err('Parameters are set differently.')
            return
        # are there both key and value?
        if spaceindex <= 0 or spaceindex == len(command[5:])-1:
            log.err('Parameters are set differently.')
        else:
            # get key and value
            parts = [command[5:5+spaceindex].strip(), command[5+spaceindex:].strip()]
            lib.global_parameters[parts[0]]=parts[1]
            if lib.active_module is not None and parts[0] in lib.active_module.parameters:
                lib.active_module.parameters[parts[0]].value=parts[1]
            log.info('%s = %s (global)' % (parts[0], parts[1]))
        
    
    # delete global option
    elif command[:5] == 'delg ' or command[:7] == 'unsetg ':
        length = 5 if command[:5] == 'delg ' else 7
        if command[length:] in lib.global_parameters:
            log.info('Parameter %s = %s removed from global parameters.' % (command[length:].strip(), lib.global_parameters[command[length:]].strip()))
            del lib.global_parameters[command[length:].strip()]
        else:
            log.warn('Parameter %s not in global parameters.' % (command[length:].strip()))
        
    # set option
    elif command [:4] == 'set ':
        command = command.replace('=', ' ')
        try:
            spaceindex = command[4:].index(' ')
        except ValueError:
            log.err('Parameters are set differently.')
            return
        if lib.active_module is None:
            log.warn('Choose a module first.')
        # are there both key and value?
        elif spaceindex <= 0 or spaceindex == len(command[4:])-1:
            log.err('Parameters are set differently.')
        else:
            # get key and value
            parts = [command[4:4+spaceindex].strip(), command[4+spaceindex:].strip()]
            if parts[0] in lib.active_module.parameters:
                lib.active_module.parameters[parts[0]].value=parts[1]
                log.info('%s = %s' % (parts[0], parts[1]))
            else:
                log.warn('Non-existent parameter %s.' % (parts[0]))
    
    # delete option
    elif command[:4] == 'del ' or command[:6] == 'unset ':
        length = 4 if command[:4] == 'del ' else 6
        if command[length:] in lib.active_module.parameters:
            log.info('Parameter %s = \'%s\' unset.' % (command[length:].strip(), lib.active_module.parameters[command[length:]].value.strip()))
            lib.active_module.parameters[command[length:].strip()].value = ''
        else:
            log.warn('Parameter %s not in parameters.' % (command[length:].strip()))
    
    # check
    elif command == 'check':
        m = lib.active_module
        if m is None:
            log.warn('Choose a module first.')
        # are all parameters in place?
        elif len([p for p in m.parameters if m.parameters[p].mandatory and m.parameters[p].value==''])>0:
                log.warn('Some parameters are undefined:')
                for x in sorted([p for p in m.parameters if m.parameters[p].mandatory and m.parameters[p].value=='']):
                    log.warn('    %s' % x)
        else:
            # check and measure time
            start = time.time()
            check_result = m.check()
            end = time.time()
            if check_result == CHECK_SUCCESS:
                log.ok('Module will succeed.')
            if check_result == CHECK_PROBABLY:
                log.ok('Module can be executed, but we do not know whether it will succeed or not.')
            elif check_result == CHECK_NOT_SUPPORTED:
                log.warn('This module does not support check.')
            elif check_result == CHECK_UNLIKELY:
                log.err('This module can be executed, but it will fail.')
            elif check_result == CHECK_FAILURE:
                log.err('This module cannot be executed.')
            log.info('Module %s has been checked in %s.' % (m.name, log.show_time(end-start)))
    
    # run
    elif command in ['run', 'execute']:
        m = lib.active_module
        if m is None:
            log.warn('Choose a module first.')
        # are all parameters in place?
        elif len([p for p in m.parameters if m.parameters[p].mandatory and m.parameters[p].value==''])>0:
                log.warn('Some parameters are undefined:')
                for x in sorted([p for p in m.parameters if m.parameters[p].mandatory and m.parameters[p].value=='']):
                    log.warn('    %s' % x)
        else:
            if m.check() != CHECK_FAILURE:
                # run the module
                log.info('Module %s has started.' % (m.name))
                
                start = time.time()
                job = m.run() # result = None or thread
                if job is None: 
                    # no thread running
                    end = time.time()
                    log.info('Module %s has terminated (%s).' % (m.name, log.show_time(end-start)))                     
                    
                    # flush stdin 
                    if len(lib.commands) == 0 or True:
                        try:
                            import termios
                            termios.tcflush(sys.stdin, termios.TCIFLUSH)
                        except ImportError:
                            import msvcrt
                            while msvcrt.kbhit():
                                msvcrt.getch()
                        except:
                            print('Y')
                            log.err(sys.exc_info()[1])
                else: 
                    # thread returned, will run in the background
                    if 'TIMEOUT' in lib.active_module.parameters:
                        lib.scheduler.add(m.name, start, job, lib.active_module.parameters['TIMEOUT'].value)
                    else:
                        lib.scheduler.add(m.name, start, job)
            
    # print command history
    elif command == 'history':
        lib.command_history.pop()
        for h in lib.command_history:
            log.writeline(h)
    
    # print module history
    elif command == 'module_history':
        lib.command_history.pop()
        for h in lib.module_history:
            log.writeline(h)

    # print temporary base
    elif command == 'tb':
        maxlen = 80
        maxk = max([len(k) for k in lib.tb.keys()] + [3])
        # print header
        print()
        log.attachline("%-*s  %-s" % (maxk, 'KEY', 'VALUE'))
        log.attachline('-' * maxk + '  ' + '-' * maxlen, log.Color.PURPLE)
    
        toescape = {x : '\\x%02x' % x for x in range(0, 32)}
        for key in natural_sort(lib.tb.keys()):
            valpart = '%s' % lib.tb[key]
            if type(valpart) == str:
                #valpart = valpart.translate(dict.fromkeys(range(0, 32), ' '))
                valpart = valpart.translate(toescape)
            if len(valpart) > maxlen:
                valpart = valpart[:maxlen-3]+'...'
            log.attachline('%-*s  %s' % (maxk, key, valpart))
    
    # tb delete key
    elif command[:6] == 'tb del':
        if len(command)>7 and command[6] == ' ':
            if command[7:] in lib.tb.keys():
                #lib.tb.delete(command[7:])
                del lib.tb[command[7:]]
        else:
            #lib.tb.delete()
            lib.tb = {}

    # tb specific value
    elif command[:3] == 'tb ':
        keys = command[3:].split(' ')
        value = lib.tb
        for key in keys:
            try:
                # if not present, try int
                if key not in value and key.isdigit():
                    key = int(key)
                value = value[key]
            except:
                log.err('Non existent key \'%s\'' % command[3:])
                break
        
        log.attachline(value)
        
        #key = command[3:]
        #if key in tb:
        #    log.attachline(tb[key])
        #else:
        #    log.err('Key \'%s\' does not exist in TB.' % (key))

    # jobs
    elif command == 'jobs':
        lib.scheduler.show()

    elif command[:10] == 'jobs kill ':
        if command[10:].strip().isdigit():
            lib.scheduler.kill(command[10:].strip())
        else:
            log.err('You must specify job ID.')

    elif command == 'session':
        log.info('Currently working with session #%d.' % lib.active_session)
    
    elif command[:8] == 'session ':
        newid = command [8:]
        if len(lib.scheduler.jobs) == 0:
            if newid.isdigit():
                lib.active_session = int(newid)
                log.info('Currently working with session #%d.' % lib.active_session)
                if is_admin():
                    log.ok('Administrator privileges already granted on "%s".' % (global_parameters['ACTIVEROOT']), dbnote=DBNOTE_UNIQUE)
            elif command[8:] == 'new':
                lib.active_session = db['analysis'].get_new_session()
                log.info('Currently working with session #%d.' % lib.active_session)
                if is_admin():
                    log.ok('Administrator privileges already granted on "%s".' % (global_parameters['ACTIVEROOT']), dbnote=DBNOTE_UNIQUE)
            else:
                log.err('Invalid session number, session #%d remains active.' % lib.active_session)
        else:
            log.err('Some modules are still running in background:')
            lib.scheduler.show()
        
    elif command == 'authors':
        everyone = {}
        # gather author info: {(name, email): (num_of_modules, [web pages])}
        for m in lib.modules:
            for a in lib.modules[m].authors:
                if (a.name, a.email) in everyone:
                    everyone[(a.name, a.email)][0] += 1
                    if a.web not in everyone[(a.name, a.email)][1]:
                        everyone[(a.name, a.email)][1].append(a.web)
                else:
                    everyone[(a.name, a.email)] = [1, [a.web]]
        
        # compute column widths
        maxn = max([len(x[0]) for x in everyone] + [4])
        maxe = max([len(x[1]) for x in everyone] + [5])
        maxp = max([len(str(everyone[x][0])) for x in everyone] + [7])
        maxw = max([len(w) for x in everyone for w in everyone[x][1]] + [3])
        # print header
        log.writeline('%*s  %-*s  %*s  %-*s' % (maxn, 'NAME', maxe, 'EMAIL', maxp, 'MODULES', maxw, 'WEB'))
        log.writeline('%s  %s  %s  %s' % ('-' * maxn, '-' * maxe, '-' *maxp, '-' * maxw), log.Color.PURPLE)
        # sort by number of plugins, then by name
        keys = sorted(sorted(list(everyone), key = lambda x: x[0]), key = lambda x: everyone[x][0], reverse=True)
        # print authors
        for a in everyone:
            wcounter = 0
            for w in everyone[a][1]:
                if wcounter == 0:
                    log.writeline('%*s  %-*s  %*d  %-*s' % (maxn, a[0], maxe, a[1], maxp, everyone[a][0], maxw, w))
                else:
                    log.writeline('%*s  %-*s  %*s  %*s' % (maxn, '', maxe, '', maxp, '', maxw, w))

                wcounter += 1

    # dictionaries
    elif command in ['dict', 'dicts', 'dictionary', 'dictionaries']:
        
        log.info('Wait for it...')
        dicts = db['dict'].get_summary()
        print(dicts)
        """if len(dicts) > 0:
            # compute column width
            maxd = max([len(x) for x in dicts] + [10])
            maxn = max([len(str(len(dicts[x]))) for x in dicts] + [5])
            
            # print header
            log.writeline('%*s  %-*s' % (maxd, 'DICTIONARY', maxn, 'WORDS'))
            log.writeline('%s  %s' % ('-' * maxd, '-' * maxn), log.Color.PURPLE)
            
            # print entries
            keys = sorted(list(dicts))
            for k in keys:
                log.writeline('%*s  %d' % (maxd, k, len(dicts[k])))
            log.writeline()"""


    # empty, new line, comment
    elif command == '' or command[0] == '#':
        lib.command_history.pop()
        pass
    
    # exit
    elif command.lower() in QUIT_STRINGS:
        log.warn('Do you really want to quit? ', end=False)
        if positive(input()):
            exit_program(None, None)
        else:
            lib.command_history.pop()
    
    # something else
    else:
        log.warn('Bad command "%s".' % (command))
        lib.command_history.pop()

"""
   / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /
  / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /
 / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /
/ / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /
"""

def set_module(module): # set selected module as active
    m = None
    # first, direct match
    if module in lib.modules:
        m = module
    else:
        # find matching modules
        matches = search_keyword(module, moduleonly=True)   
        if len(matches) == 0:
            pass # module does not exist
        elif len(matches) > 1:
            log.warn('Ambiguous module name: \'%s\'.' % module)
            return
        else:
            m = matches[0]

    # found exactly one?
    if m is not None:
        # check dependencies
        dependency_missing = False
        for x in lib.modules[m].dependencies:
            if x not in lib.modules:
                log.err('Dependency module \'%s\' does not exist.' % x)
                dependency_missing = True

        # dependencies ok, select the module
        if not dependency_missing:
            lib.active_module = lib.modules[m]
            lib.prompt = "%s > " % (m)
            lib.module_history.append(m)
            lib.active_module.reset_parameters()
            # select parameters to global values if possible
            for p in lib.active_module.parameters:
                if lib.active_module.parameters[p].value == '' and p in lib.global_parameters:
                    lib.active_module.parameters[p].value = lib.global_parameters[p]
                    log.info('Parameter %s is set to global value \'%s\'.' % (p, lib.global_parameters[p]))
    else:
        log.err('Module %s does not exist.' % (module))




def print_modules(modules, order_by_date=False):
    # compute column widths
    maxv = max([len(lib.modules[m].version) for m in modules] + [7])
    maxm = max([len(m) for m in modules] + [6])
    maxa = max([len(a.name) for m in modules for a in lib.modules[m].authors] + [7])
    # print header
    log.attachline("%*s  %-*s  %-*s  %-10s  %-s" % (maxv, 'VERSION', maxm, 'MODULE', maxa, 'AUTHORS', 'DATE', 'DESCRIPTION'))
    log.attachline('-' * maxv + '  ' + '-' * maxm + '  ' + '-' * maxa + '  ' + '-' * 10 + '  ' + '-' * 11, log.Color.PURPLE)
    
    # do some sorting
    if order_by_date:
        keys = sorted(sorted(list(modules), key=lambda x: x), key=lambda x: lib.modules[x].date, reverse=True)
    else:
        keys = sorted(list(modules), key=lambda x: x)
        
    # print rows
    for m in keys:
        acounter=0 # if more authors, do not print other cells over and over
        for a in lib.modules[m].authors:
            if acounter == 0:
                log.attachline("%*s  %-*s  %-*s  %-10s  %-s" % (maxv, lib.modules[m].version, maxm, m, maxa, a.name, lib.modules[m].date, lib.modules[m].short_description))
            else:
                log.attachline("%*s  %-*s  %-*s  %-10s  %-s" % (maxv, '', maxm, '', maxa, a.name, '', ''))
            acounter += 1
    log.info('Returned %d/%d modules.' % (len(modules), len(lib.modules)))




def print_module_info(basics=True, authors=True, options=True, missing=False, description=True, references=True, tags=True, db=True, dependencies=True, dependent=True, changelog=True):
    m = lib.active_module
    if m == None:
        log.warn('Choose a module first.')
        return

    # general info 
    if basics:
        length = max([0] + [len(x) for x in ['Name', 'Date', 'Version', 'License']])
        log.attach('%*s: ' % (length, 'Name'), log.Color.PURPLE) 
        log.attachline('%s' % (m.name))
        log.attach('%*s: ' % (length, 'Date'), log.Color.PURPLE) 
        log.attachline('%s' % (m.date))
        log.attach('%*s: ' % (length, 'Version'), log.Color.PURPLE)
        log.attachline('%s' % (m.version))
        log.attach('%*s: ' % (length, 'License'), log.Color.PURPLE) 
        log.attachline('%s' % (m.license))
        log.attachline()
    
    # authors
    if authors:
        log.attachline('Authors:', log.Color.PURPLE)
        for a in m.authors:
            log.writeline('%s %s %s' % (a.name, '<%s>' % (a.email) if len(a.email) > 0 else '', '{%s}' % (a.web) if len(a.web) > 0 else ''))
        log.attachline()

    # parameters
    if options and len(m.parameters) > 0:
        log.attachline('Parameters:', log.Color.PURPLE)
        params = list(m.parameters) if not missing else [p for p in list(m.parameters) if m.parameters[p].value == '']
        # compute column widths
        maxn = max([4]+[len(p) for p in params])
        maxv = max([5]+[len(m.parameters[p].value) for p in params])
        # print header
        log.writeline('%-*s  %-*s  %s  %s' %(maxn, 'NAME', maxv, 'VALUE', 'MANDATORY', 'DESCRIPTION'))
        log.writeline('%s  %s  %s  %s' %('-' * maxn, '-' * maxv, '-' * 9, '-' * 11), log.Color.PURPLE)
        
        # sort by mandatory, then by name
        keys = sorted(sorted(params, key = lambda y: y), key = lambda x: m.parameters[x].mandatory, reverse=True)
        for p in keys:
            log.writeline('%-*s  %-*s      %s      %s' %(maxn, p, maxv, m.parameters[p].value, '+' if m.parameters[p].mandatory else ' ', m.parameters[p].description))
        log.writeline()
    
    # description
    if description:
        log.attachline('Description:', log.Color.PURPLE)
        log.attachline(m.description)
        log.writeline()

    # references
    if references and len(m.references)>0:
        log.attachline('References:', log.Color.PURPLE)
        for r in m.references:
            log.writeline(r)
        log.writeline()
    
    # tags
    if tags and len(m.tags) > 0:
        log.attachline('Tags:', log.Color.PURPLE)
        for i in range(0, len(m.tags)):
            if i == 0:
                log.write('%s' % m.tags[i])
            else:
                log.attach(', %s' % m.tags[i])
        log.writeline('\n')
        
    # database accessed
    if db and len(m.db_access) > 0:
        log.attachline('Data Base:', log.Color.PURPLE)
        for d in m.db_access:
            log.writeline(d)
        log.writeline()

    # modules the active module depends on
    if dependencies and len(m.dependencies) > 0:
        log.attachline('Dependencies:', log.Color.PURPLE)
        maxd = max([6] + [len(d) for d in m.dependencies])
        log.writeline('%-*s  %s' % (maxd, 'MODULE', 'VERSION'))
        log.writeline('%s  %s' % ('-' * maxd, '-' * 7), log.Color.PURPLE)
        for d in m.dependencies:
            log.writeline('%-*s  %s  ' % (maxd, d, m.dependencies[d]))
        log.writeline()

    # modules dependent on the active module
    if dependent:
        dep = [x for x in lib.modules if len([y for y in lib.modules[x].dependencies if y == m.name and lib.modules[x].dependencies[y] == m.version]) > 0]
        if len(dep) > 0:
            log.attachline('Dependent modules:', log.Color.PURPLE)
            maxd = max([6] + [len(d) for d in dep])
            log.writeline('%-*s  %s' % (maxd, 'MODULE', 'VERSION'))
            log.writeline('%s  %s' % ('-' * maxd, '-' * 7), log.Color.PURPLE)
            for d in dep:
                log.writeline('%-*s  %s  ' % (maxd, d, lib.modules[d].version))
            log.writeline()

            
    # changelog
    if changelog and len(m.changelog.strip()) > 0:
        log.attachline('Changelog:', log.Color.PURPLE)
        log.attachline(m.changelog)
        log.writeline()
    




def print_help():
    commands = [
        ('$key', 'use variable value (from Temporary Base (preferably) or Global Parameters)'),
        ('!touch /tmp/file', 'run system command'),
        ('help', 'print this help'),
        ('list, ls', 'show all modules ordered by name'),
        ('list date, ls date', 'show all modules ordered by date'),
        ('search abc', 'show modules which has something to do with abc'),
        ('search <2014', 'show modules from 2014 and older'),
        ('search =2015', 'show modules from 2015'),
        ('search >2016', 'show modules from 2016 and newer'),
        ('search ! (l.e and (<2000 or =2014))', 'solid searching'),
        ('use module', 'select a module'),
        ('back', 'go to main menu'),
        ('previous', 'use previous module'),
        ('info', 'show info about selected module'),
        ('show options, show parameters', 'show options for selected module'),
        ('show missing', 'show only undefined options for selected module'),
        ('getg', 'show global parameters'),
        ('setg NAME=VALUE, setg NAME VALUE', 'set global parameter'),
        ('delg NAME, unsetg NAME', 'delete global parameter'),
        ('set NAME=VALUE, set NAME VALUE', 'set parameter for selected module'),
        ('del NAME, unset NAME', 'unset global parameter'),
        ('check', 'check if module will be successful'),
        ('run, execute', 'run the module'),
        ('history', 'show command history'),
        ('module_history', 'show history of selected modules'),
        ('tb', 'show the Temporary Base'),
        ('tb a 1', 'show content of TB > a > 1'),
        ('tb del a', 'delete content of TB > a'),
        ('jobs', 'show jobs in background'),
        ('jobs kill 1', 'kill background job #1'),
        ('session', 'show number of actual session'),
        ('session new', 'set session number to a new value'),
        ('session 1', 'set session number to 1'),
        # ('session del 1', 'delete session #1'),
        ('authors', 'show information about authors'),
        ('dict', 'list available dictionaries'),
        ('exit, exit(), quit, quit(), q', 'exit the program'),
        ('# comment', 'comment (nothing will happen)'),
    ]
    maxc = max([7] + [len(x) for x, y in commands])
    log.writeline('%-*s  %s' % (maxc, 'COMMAND', 'DESCRIPTION'))
    log.writeline('%-s  %s' % ('-' * maxc, '-' * 11), log.Color.PURPLE)
    for c in commands:
        log.writeline('%-*s  %s' % (maxc, c[0], c[1]))
