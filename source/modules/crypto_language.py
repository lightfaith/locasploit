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
		#	'',
		]
		
		self.date = '2016-02-03'
		self.license = 'GNU GPLv2'
		self.version = '1.0'
		self.tags = [
			'cipher',
			'language',
		]
		self.description = """
This module compares strings located at 'DATA > <key>' to dictionaries.
For huge sets of data, this could take a long time. If possible, you should specify the KB key as accurate as possible. 
Language code can be also specified.
"""
		self.kb_access = [
			'DATA',
		]
		
		self.dependencies = {
		}
		self.changelog = """
"""

		self.reset_parameters()

	def reset_parameters(self):
		self.parameters = {
			'SILENT': Parameter(value='no', mandatory=True, description='Suppress the output'),
			'KEY': Parameter(value='', mandatory=True, description='KB Data Key to analyze'),
			'CODE': Parameter(value='', mandatory=False, description='Language code (empty = all)'),
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
		
		messages = []
		# deal with message/messages
		datakey = lib.kb.find('DATA %s' % key)[0]
		if type(datakey) is list or type(datakey) is tuple:
			messages = datakey
		elif type(datakey) is dict:
			messages += list(datakey.values())
		elif type(datakey) is bytes:
			messages.append(datakey.decode('utf-8'))
		elif type(datakey) is str:
			messages.append(datakey)
		else:
			log.err('Unexpected message type %s, exiting...' % type(datakey))
			return None

		messages = natural_sort(messages)
		# for each string to analyze
		for message in messages:
			# prepare dictionary {language:rate}
			score = {}
			if len(code) > 0: # only one language
				score[code] = 0
			else: # all languages
				for lang in lib.dicts:
					score[lang] = 0

			# for each language
			for lang in list(score):
				# for each word
				words = re.findall(r"[A-Za-z'0-9]+", message)
				for word in words:
					if word.lower() in lib.dicts[lang]:
						score[lang] += 1
				score[lang] /= float(len(words))

			# print results
			if not silent:
				toshow = message.replace('\n', '\\n')
				if max([score[x] for x in score]+[]) >= 0.5:
					log.ok('Results for \'%s%s\'' % (toshow[:40], '...' if len(toshow) > 43 else ''))
				else:
					log.writeline('Analysis for \'%s%s\'' % (toshow[:40], '...' if len(toshow) > 43 else ''))
				
				sortscore = sorted(sorted(list(score), key=lambda x: score[x], reverse=True))
				for lang in score:
					line = '%*s: %7.3f%%' % (6, lang, score[lang] * 100.0)
					if score[lang] >= 0.5:
						log.ok(line)
					else:
						log.writeline(line)
			log.writeline()
		# # # # # # # #
		return None
	

lib.module_objects.append(Module())
