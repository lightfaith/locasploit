#!/usr/bin/env python3
from source.modules._generic_module import *

class Module(GenericModule):
	def __init__(self):
		self.authors = [
			Author(name='Vitezslav Grygar', email='vitezslav.grygar@gmail.com', web='https://badsulog.blogspot.com'),
		]
		
		self.name = 'crypto.language'
		self.short_description = 'Attempts to reveal string\'s language.'
		self.references = [
		]
		
		self.date = '2016-02-03'
		self.license = 'GNU GPLv2'
		self.version = '1.1'
		self.tags = [
			'cipher',
			'language',
		]
		self.description = """
This module compares strings located at 'DATA > <key>' to dictionaries.
For huge sets of data, this could take a long time. If possible, you should specify the KB key as accurate as possible. 
Language code can be also specified.
For some reason, adding threads does not help. This should be fixed...
"""
		self.kb_access = [
			'DATA',
		]
		
		self.dependencies = {
		}
		self.changelog = """
1.1: Threading support (not quite efficient)
     Word splitting by punct, numbers and whitespace
1.0: Language recognition
     Words A-Za-z'0-9
"""

		self.reset_parameters()

	def reset_parameters(self):
		self.parameters = {
			'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
			'KEY': Parameter(value='', mandatory=True, description='KB Data Key to analyze'),
			'CODE': Parameter(value='', mandatory=False, description='Language code (empty = all)'),
			'THREADS': Parameter(value='1', mandatory=True, description='Number of threads to use concurrently'),
		}

	def check(self):
		silent = positive(self.parameters['SILENT'].value)
		if not silent:
			log.info('This module does not support check.')
		return False
	
	def run(self):
		silent = positive(self.parameters['SILENT'].value)
		# # # # # # # #
		# check parameters
		code = self.parameters['CODE'].value
		if len(code) > 0 and not code in lib.dicts:
			log.err('Dictionary for \'%s\' does not exist.' % code)
			return None
		key = self.parameters['KEY'].value
		if not lib.kb.exists('DATA %s' % key):
			log.err('Key \'%s\' does not exist.' % key)
			return None
		if not self.parameters['THREADS'].value.isdigit():
			log.err('THREADS parameter must be a number.')
			return None
		threadnum = int(self.parameters['THREADS'].value)

		data = {}

		# deal with message/messages
		datakey = lib.kb.find('DATA %s' % key)
		if type(datakey) is list or type(datakey) is tuple:
			for i in range(len(datakey)):
				data[i]=datakey[i]
		elif type(datakey) is dict:
			for x in datakey:
				data[x] = datakey[x]
		elif type(datakey) is bytes:
			data[key] = datakey.decode('utf-8')
		elif type(datakey) is str:
			data[key] = datakey
		else:
			log.err('Unexpected message type %s, exiting...' % type(datakey))
			return None

		keys = list(data)
		# for each string to analyze

		# run desired number of threads
		threads = []
		for i in range(0, threadnum):
			t = Thread({k:data[k] for k in keys[i::threadnum]})
			t.start()
			lib.scheduler.add_user_thread(t)
			threads.append(t)
		
		counter = 0  # counts number of evaluations processed
		while counter < len(keys):
			# check if there is something in the pool
			if len(Thread.dic) > 0:
				key = list(Thread.dic)[0] # get the first key (basically random)

				#print header
				if not silent:
					log.writeline()
					toshow = data[key].replace('\n', '\\n')[:40]
					log.writeline('Results for \'%s\' (%s%s):' % (key, toshow, '...' if len(data[key]) > 43 else ''))

				# for each language
				for lang in Thread.dic[key]:
					# print results
					if not silent:
						value = Thread.dic[key][lang]
						line = '%*s: %7.3f%%' % (6, lang, value * 100.0)
						if value >= 0.5:
							log.ok(line)
						else:
							log.writeline(line)

				# update pool and counter
				del Thread.dic[key]
				counter += 1
			else: # pool empty, wait for a while
				time.sleep(1)


		for t in threads:
			t.join()
		# # # # # # # #
		return None
	
# Thread checks single message to multiple languages relationships
class Thread(threading.Thread):
	lock = threading.Lock()
	dic = {}
	
	def __init__(self, data):
		threading.Thread.__init__(self)
		self.data = data
		self.terminate = False
		self.lock = threading.Lock()


	def run(self):
		for key in self.data:	
			score = {}
			for lang in lib.dicts:
				if self.terminate:
					break
				score[lang] = 0.0
				#words = re.findall("[A-Za-z'0-9]+", self.data[key])
				#words = re.split(r"[\s\d!\?@#\$%\^&\*\(\)_\+{}[]:|'\"\\-.,]", self.data[key])
				words = list(filter(None, re.split(r"[\s.!,?\-0-9@]", self.data[key])))
				for word in words:
					if word.lower() in lib.dicts[lang]:
						score[lang] += 1

				score[lang] /= float(len(words))
			Thread.dic[key] = score

	
	def stop(self):
		self.terminate = True

lib.module_objects.append(Module())
