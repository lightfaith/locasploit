#!usr/bin/env python
from include import *
import author
from search import *
import log

def execute_command(command):
	command = command.strip()
	lib.command_history.append(command)

	# exit
	if command in ['exit', 'exit()', 'quit', 'quit()', 'q']:
		exit_program(None, None)
	
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
		print_modules(lib.modules.keys())
	
	# list modules sorted by date
	elif command in ['list date', 'ls date']:
		print_modules(lib.modules.keys(), order_by_date=True)
	
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
				
				by_module_tmp = SearchAbbr(command[7:].lower(), [x.lower() for x in modules.keys()]) + [x for x in modules if command[7:].lower() in x.lower()]
				by_module = []
				for x in by_module_tmp:
					if x not in by_module:
						by_module.append(x)
				if len(by_module) > 0:
					log.attachline(log.Color.purple('By module:'))
					print_modules(by_module)
					log.writeline('')
		
				by_tag = [x for x in modules if command[7:].lower() in [y.lower() for y in modules[x].tags]]
				if len(by_tag) > 0:
					log.attachline(log.Color.purple('By tags:'))
					print_modules(by_tag)
					log.writeline('')
		
				
				by_parameter = [x for x in modules if command[7:].lower() in [y.lower() for y in modules[x].parameters]]
				if len(by_parameter) > 0:
					log.attachline(log.Color.purple('By parameters:'))
					print_modules(by_parameter)
					log.writeline('')
			
				by_author = [x for x in modules for authors in modules[x].authors if command[7:].lower() in authors.name.lower() or command[7:].lower() in authors.email.lower() or command[7:].lower() in authors.web.lower()]
				if len(by_author) > 0:
					log.attachline(log.Color.purple('By authors:'))
					print_modules(by_author)
					log.writeline('')
				
				by_kb = [x for x in modules if command[7:].upper() in [y.upper() for y in modules[x].kb_access]]
				if len(by_kb) > 0:
					log.attachline(log.Color.purple('By Knowledge Base:'))
					print_modules(by_kb)
					log.writeline('')
				
				by_dependency = [x for x in modules if len(SearchAbbr(command[7:].lower(), [y.lower() for y in modules[x].dependencies.keys()])) > 0]
				if len(by_dependency) > 0:
					log.attachline(log.Color.purple('By dependencies:'))
					print_modules(by_dependency)
					log.writeline('')

				by_version = [x for x in modules if command[7:].lower() == modules[x].version.lower()]
				if len(by_version) > 0:
					log.attachline(log.Color.purple('By version:'))
					print_modules(by_version)
					log.writeline('')

		else: # complicated search, use Search()
			print_modules(Search(command[7:]))

	# module selection
	elif command[0:4] == "use " and len(command)>4:
		set_module(command[4:])
	
	# back to root
	elif command == 'back':
		lib.prompt = ' >  '
		lib.active_module = None

	# use previous module
	elif command == 'previous':
		if len(lib.module_history)>1:
			set_module(lib.module_history[-2])
	
	# module info
	elif command == 'info':
		print_module_info()

	# show options
	elif command == 'show options' or command == 'show parameters':
		print_module_info(basics=False, authors=False, description=False, references=False, tags=False, kb=False, dependencies=False, changelog=False)
	
	# show missing
	elif command == 'show missing':
		print_module_info(basics=False, authors=False, description=False, references=False, tags=False, kb=False, dependencies=False, changelog=False, missing=True)

	# show global options
	elif command == 'getg':
		maxp = max([4]+[len(x) for x in lib.global_parameters])
		log.writeline('%-*s  %s' % (maxp, 'NAME', 'VALUE'))
		log.writeline(log.Color.purple('%s  %s' % ('-' * maxp, '-' * 5)))
		for p in lib.global_parameters:
			log.writeline('%-*s  %s' % (maxp, p, lib.global_parameters[p]))

	# set global option
	elif command[:5] == 'setg ':
		command = command.replace('=', ' ')
		try:
			spaceindex = command[5:].index(' ')
		except ValueError:
			log.err('Parameters are set differently.')
			return
		if spaceindex <= 0 or spaceindex == len(command[5:])-1:
			log.err('Parameters are set differently.')
		else:
			parts = [command[5:5+spaceindex].strip(), command[5+spaceindex:].strip()]
			lib.global_parameters[parts[0]]=parts[1]
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
		elif spaceindex <= 0 or spaceindex == len(command[4:])-1:
			log.err('Parameters are set differently.')
		else:
			parts = [command[4:4+spaceindex].strip(), command[4+spaceindex:].strip()]
			if parts[0] in lib.active_module.parameters:
				lib.active_module.parameters[parts[0]].value=parts[1]
				log.info('%s = %s' % (parts[0], parts[1]))
			else:
				log.warn('Non-existent parameter %s.' % (parts[0]))
	
	# delete global option
	elif command[:4] == 'delg ' or command[:6] == 'unset ':
		length = 4 if command[:4] == 'del ' else 6
		if command[length:] in lib.global_parameters:
			log.info('Parameter %s = %s unset.' % (command[length:].strip(), lib.active_module.parameters[command[length:]].strip()))
			del lib.active_module.parameters[command[length:].strip()]
		else:
			log.warn('Parameter %s not in parameters.' % (command[length:].strip()))
	
	# check
	elif command == 'check':
		m = lib.active_module
		if m is None:
			log.warn('Choose a module first.')
		elif len([p for p in m.parameters if m.parameters[p].mandatory and m.parameters[p].value==''])>0:
				log.warn('Some parameters are undefined:')
				for x in sorted([p for p in m.parameters if m.parameters[p].mandatory and m.parameters[p].value=='']):
					log.warn('    %s' % x)
		else:
			start = time.time()
			m.Check()
			end = time.time()
			log.info('Module %s has been checked in %s.' % (m.name, show_time(end-start)))
	
	# run, check if module is not None and all arguments are set
	elif command in ['run', 'execute']:
		m = lib.active_module
		if m is None:
			log.warn('Choose a module first.')
		elif len([p for p in m.parameters if m.parameters[p].mandatory and m.parameters[p].value==''])>0:
				log.warn('Some parameters are undefined:')
				for x in sorted([p for p in m.parameters if m.parameters[p].mandatory and m.parameters[p].value=='']):
					log.warn('    %s' % x)
		else:
			kb_dep_ok = True
			for p in m.parameters:
				if m.parameters[p].kb:
					parts = m.parameters[p].value.split('.')
					if len(parts) == 1 and parts[0] not in lib.kb.keys():
						kb_dep_ok = False
						log.err('Key %s is not present in the Knowledge Base.' % parts[0])
					elif len(parts) == 2 and parts[1] not in lib.kb.subkeys(parts[0]):
						kb_dep_ok = False
						log.err('Key %s.%s is not present in the Knowledge Base.' % parts[0], parts[1])

				if m.parameters[p].dependency:
					matches = SearchKeyword(m.parameters[p].value)
					if len(matches) == 0:
						kb_dep_ok = False
						log.err('Module %s does not exist.' % m.parameters[p].value)
					elif len(matches) > 1:
						kb_dep_ok = False
						log.err('Ambiguous module name: %s.', m.parameters[p].value)
			
			if kb_dep_ok:
				log.info('Module %s has started.' % (m.name))
				try:
					start = time.time()
					job = m.Run()
					if job is None: # no thread created
						end = time.time()
						log.info('Module %s has terminated (%s).' % (m.name, show_time(end-start)))						
						# flush stdin (if not from file!)
						if len(lib.input_commands) == 0:
							try:
								import termios
								termios.tcflush(sys.stdin, termios.TCIOFLUSH)
							except ImportError:
								import msvcrt
								while msvcrt.kbhit():
									msvcrt.getch()
							except:
								log.err(sys.exc_info()[1])

					else: # thread will run in the background
						if lib.active_module.parameters.has_key('TIMEOUT'):
							lib.scheduler.add(m.name, start, job, lib.active_module.parameters['TIMEOUT'].value)
						else:
							lib.scheduler.add(m.name, start, job)
						
				except:
					traceback.format_exc()
					log.err(sys.exc_info()[1])
			
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

	elif command == 'kb':
		lib.kb.dump()

	elif command[:3] == 'kb ':
		lib.kb.dump(command[3:])	

	elif command == 'jobs':
		lib.scheduler.show()

	elif command[:10] == 'jobs kill ':
		if command[10:].strip().isdigit():
			lib.scheduler.kill(command[10:].strip())
		else:
			print 'cannot kill'

	elif command == 'authors':
		everyone = {}
		for m in lib.modules:
			for a in lib.modules[m].authors:
				if everyone.has_key((a.name, a.email)):
					everyone[(a.name, a.email)][0] += 1
					if a.web not in everyone[(a.name, a.email)][1]:
						everyone[(a.name, a.email)][1].append(a.web)
				else:
					everyone[(a.name, a.email)] = [1, [a.web]]
		
		maxn = max([len(x[0]) for x in everyone] + [4])
		maxe = max([len(x[1]) for x in everyone] + [5])
		maxp = max([len(str(everyone[x][0])) for x in everyone] + [7])
		maxw = max([len(w) for x in everyone for w in everyone[x][1]] + [3])
		log.writeline('%*s  %-*s  %*s  %-*s' % (maxn, 'NAME', maxe, 'EMAIL', maxp, 'PLUGINS', maxw, 'WEB'))
		log.writeline(log.Color.purple('%s  %s  %s  %s' % ('-' * maxn, '-' * maxe, '-' *maxp, '-' * maxw)))
		# sort by number of plugins, then by name
		keys = sorted(sorted(everyone.keys(), key = lambda x: x[0]), key = lambda x: everyone[x][0], reverse=True)
		for a in everyone:
			wcounter = 0
			for w in everyone[a][1]:
				if wcounter == 0:
					log.writeline('%*s  %-*s  %*d  %-*s' % (maxn, a[0], maxe, a[1], maxp, everyone[a][0], maxw, w))
				else:
					log.writeline('%*s  %-*s  %*d  %*s' % (maxn, '', maxe, '', maxp, '', maxw, w))

				wcounter += 1

	# empty, new line, comment
	elif command == '' or command[0] == '#':
		lib.command_history.pop()
		pass
	
	# something else
	else:
		log.warn('[!] Bad command "%s".' % (command))
		lib.command_history.pop()

"""
   / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /
  / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /
 / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /
/ / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /
"""

def set_module(module):
	m = None
	# first, direct match
	if module in lib.modules:
		m = module
	else:
		# find matching modules
		matches = SearchKeyword(module, moduleonly=True)	
		if len(matches) == 0:
			pass # module does not exist
		elif len(matches) > 1:
			log.warn('Ambiguous module name: %s.' % module)
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

		if not dependency_missing:
			lib.active_module = lib.modules[m]
			lib.prompt = "%s > " % (m)
			lib.module_history.append(m)
			lib.active_module.ResetParameters()
			for p in lib.active_module.parameters:
				if lib.active_module.parameters[p].value == '' and p in lib.global_parameters:
					lib.active_module.parameters[p].value = lib.global_parameters[p]
					log.info('Parameter %s is set to global value \'%s\'.' % (p, lib.global_parameters[p]))
	else:
		log.err('Module %s does not exist.' % (module))




def print_modules(modules, order_by_date=False):
	# compute column sizes
	maxv = max([len(lib.modules[m].version) for m in modules] + [7])
	maxm = max([len(m) for m in modules] + [6])
	maxa = max([len(a.name) for m in modules for a in lib.modules[m].authors] + [7])
	log.attachline("%*s  %-*s  %-*s  %-10s  %-s" % (maxv, 'VERSION', maxm, 'MODULE', maxa, 'AUTHORS', 'DATE', 'DESCRIPTION'))
	log.attachline(log.Color.purple('-' * maxv + '  ' + '-' * maxm + '  ' + '-' * maxa + '  ' + '-' * 10 + '  ' + '-' * 11))
	# do some sorting
	if order_by_date:
		modules.sort(key=lambda x: x)
		modules.sort(key=lambda x: lib.modules[x].date, reverse=True)
	else:
		modules.sort(key=lambda x: x)
	# print rows
	for m in modules:
		acounter=0 # if more authors, do not print other cells over and over
		for a in lib.modules[m].authors:
			if acounter == 0:
				log.attachline("%*s  %-*s  %-*s  %-10s  %-s" % (maxv, lib.modules[m].version, maxm, m, maxa, a.name, lib.modules[m].date, lib.modules[m].short_description))
			else:
				log.attachline("%*s  %-*s  %-*s  %-10s  %-s" % (maxv, '', maxm, '', maxa, a.name, '', ''))
			acounter += 1
	log.info('Returned %d/%d modules.' % (len(modules), len(lib.modules)))




def print_module_info(basics=True, authors=True, options=True, missing=False, description=True, references=True, tags=True, kb=True, dependencies=True, changelog=True):
	m = lib.active_module
	if m == None:
		log.warn('Choose a module first.')
		return

	if basics:
		length = max([0] + [len(x) for x in ['Name', 'Date', 'Version', 'License']])
		log.attachline(log.Color.purple('%*s: ' % (length, 'Name')) + '%s' % (m.name))
		log.attachline(log.Color.purple('%*s: ' % (length, 'Date')) + '%s' % (m.date))
		log.attachline(log.Color.purple('%*s: ' % (length, 'Version')) + '%s' % (m.version))
		log.attachline(log.Color.purple('%*s: ' % (length, 'License')) + '%s' % (m.license))
		log.attachline()
	
	if authors:
		log.attachline(log.Color.purple('Authors:'))
		for a in m.authors:
			log.writeline('%s %s %s' % (a.name, '<%s>' % (a.email) if len(a.email) > 0 else '', '{%s}' % (a.web) if len(a.web) > 0 else ''))
		log.attachline()

	if options and len(m.parameters) > 0:
		log.attachline(log.Color.purple('Parameters:'))
		params = m.parameters.keys() if not missing else [p for p in m.parameters.keys() if m.parameters[p].value == '']
		maxn = max([4]+[len(p) for p in params])
		maxv = max([5]+[len(m.parameters[p].value) for p in params])

		log.writeline('%-*s  %-*s  %s  %s' %(maxn, 'NAME', maxv, 'VALUE', 'MANDATORY', 'DESCRIPTION'))
		log.writeline(log.Color.purple('%s  %s  %s  %s' %('-' * maxn, '-' * maxv, '-' * 9, '-' * 11)))
		# sort by mandatory, then by name
		keys = sorted(sorted(params, key = lambda y: y), key = lambda x: m.parameters[x].mandatory, reverse=True)
		for p in keys:
			log.writeline('%-*s  %-*s      %s      %s' %(maxn, p, maxv, m.parameters[p].value, '+' if m.parameters[p].mandatory else ' ', m.parameters[p].description))
		log.writeline()
	
	if description:
		log.attachline(log.Color.purple('Description:'))
		log.attachline(m.description)
		log.writeline()

	if references and len(m.references)>0:
		log.attachline(log.Color.purple('References:'))
		for r in m.references:
			log.writeline(r)
		log.writeline()
	
	if tags and len(m.tags) > 0:
		log.attachline(log.Color.purple('Tags:'))
		for i in range(0, len(m.tags)):
			if i == 0:
				log.write('%s' % m.tags[i])
			else:
				log.attach(', %s' % m.tags[i])
		log.writeline('\n')
		
	if kb and len(m.kb_access) > 0:
		log.attachline(log.Color.purple('Knowledge Base:'))
		for k in m.kb_access:
			log.writeline(k)
		log.writeline()

	if dependencies and len(m.dependencies) > 0:
		log.attachline(log.Color.purple('Module dependencies:'))
		maxd = max([6] + [len(d) for d in m.dependencies])
		log.writeline('%-*s  %s' % (maxd, 'MODULE', 'VERSION'))
		log.writeline(log.Color.purple('%s  %s' % ('-' * maxd, '-' * 7)))
		for d in m.dependencies:
			log.writeline('%-*s  %s  ' % (maxd, d, m.dependencies[d]))
		log.writeline()

	if changelog and len(m.changelog.strip()) > 0:
		log.attachline(log.Color.purple('Changelog:'))
		log.attachline(m.changelog)
		log.writeline()
	




def print_help():
	commands = [
		('exit, exit(), quit, quit(), q', 'exit the program'),
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
		('kb', 'show the Knowledge Base'),
		('kb a b', 'show content of KB > a > b'),
		('jobs', 'show jobs in background'),
		('authors', 'show information about authors'),
		('# comment', 'comment (nothing will happen)'),
	]
	maxc = max([7] + [len(x) for x, y in commands])
	log.writeline('%-*s  %s' % (maxc, 'COMMAND', 'DESCRIPTION'))
	log.writeline(log.Color.purple('%-s  %s' % ('-' * maxc, '-' * 11)))
	for c in commands:
		log.writeline('%-*s  %s' % (maxc, c[0], c[1]))
