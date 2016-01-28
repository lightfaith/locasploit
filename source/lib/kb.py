#!/usr/bin/env python
import log, threading

class KB:
	# now a dictionary, later maybe some database
	def __init__(self):
		self.kb = {}
		self.lock = threading.Lock()
	
	def add_key(self, key):
		if key not in self.kb:
			self.lock.acquire()
			self.kb[key] = {}
			self.lock.release()

	def add(self, key, subkey, value):
		self.add_key(key)
		self.lock.acquire()
		self.kb[key][subkey] = value
		self.lock.release()

	def keys(self):
		self.lock.acquire()
		result = self.kb.keys()
		self.lock.release()
		return result

	def subkeys(self, key):
		self.add_key(key)
		self.lock.acquire()
		result = self.kb[key].keys()
		self.lock.release()
		return result

	def get(self, key, subkey):
		self.add_key(key)
		self.lock.acquire()
		if subkey in self.kb[key]:
			result = self.kb[key][subkey]
		else:
			result = None
		self.lock.release()
		return result
	
	def delete(self, key, subkey):
		if key in self.kb:
			self.lock.acquire()
			if subkey in self.kb[key]:
				del self.kb[key][subkey]
			if len(self.kb[key]) == 0:
				del self.kb[key]
			self.lock.release()
	
	def dump(self, query=''):
		import json
		keys = [x for x in query.split(' ') if len(x)>0]
		if len(keys) == 0:
			log.attachline(json.dumps(self.kb, indent=4))
		else:
			i = 0
			branch = self.kb
			for i in range(0, len(keys)):
				if type(branch) == dict and branch.has_key(keys[i]):
					branch = branch[keys[i]]
				elif (type(branch) == list or type(branch) == tuple) and keys[i].isdigit() and int(keys[i])<len(branch):
					branch = branch[int(keys[i])]
				elif i == len(keys)-1 and type(branch) == str:
					branch = [x for x in branch.splitlines() if keys[i] in x]
					return
				else:
					log.err('Cannot find key \'%s\'.' % keys[i])
					i -= 1
					break
			#if keys[len(keys)-1] in branch:
			log.attachline(log.Color.purple(' > '.join(keys[:i+1])+':'))
			log.attachline(json.dumps(branch, indent=4))
			#else:
			#	log.err('nope2')

#		for a in sorted(lib.kb.keys()):
#			if len(lib.kb.subkeys(a)) == 0:
#				continue
#			log.attachline(log.Color.purple('%s:' % a)) 
#			for b in sorted(lib.kb.subkeys(a)):
#				log.writeline(log.Color.purple('%s: ' % b)) 
#				item = lib.kb.get(a, b)
#				for c in item:
#					if type(item) == str:
#						log.writeline('    %s' % c)
#					elif type(item) == dict:
#						log.writeline('    %s: %s' % (str(c), lib.kb.get(a, b)[c]))
#					else:
#						print type(c)

