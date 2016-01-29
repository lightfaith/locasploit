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
	
#	def delete(self, key, subkey):
#		if key in self.kb:
#			self.lock.acquire()
#			if subkey in self.kb[key]:
#				del self.kb[key][subkey]
#			if len(self.kb[key]) == 0:
#				del self.kb[key]
#			self.lock.release()
	
	def dump(self, query=''):
		import json
		keys = [x for x in query.split(' ') if len(x)>0]
		if len(keys) == 0:
			log.attachline(json.dumps(self.kb, indent=4))
		else:
			result = self.find(keys)
			log.attachline(log.Color.purple(' > '.join(keys[:result[1]+1])+':'))
			log.attachline(json.dumps(result[0], indent=4))
	
	def delete(self, query=''):
		keys = [x for x in query.split(' ') if len(x)>0]
		self.lock.acquire()
		if len(keys) == 0:
			self.kb = {}
		else:
			result = self.find(keys, True)
			if result[1]+1<len(keys):
				#log.info('not found, not deleting...')
				pass
			else:
				print result[0]
				del result[0][keys[result[1]]]
				log.info('Entry %s has been deleted.' % ' > '.join(keys[:result[1]+1]))
		self.lock.release()
	
	def find(self, keys, parent=False):
		i = 0
		branch = self.kb
		parentbranch = None
		for i in range(0, len(keys)):
			parentbranch = branch
			if type(branch) == dict and branch.has_key(keys[i]):
				branch = branch[keys[i]]
			elif (type(branch) == list or type(branch) == tuple) and keys[i].isdigit() and int(keys[i])<len(branch):
				branch = branch[int(keys[i])]
			elif i == len(keys)-1 and type(branch) == str:
				tmpbranch = [x for x in branch.splitlines() if keys[i] in x]
				if len(tmpbranch) == 0:
					log.err('Cannot find key \'%s\'.' % keys[i])
					i -= 1
					break		
				if parent:
					return (parentbranch, i)
				else:
					return (tmpbranch, i)
			else:
				log.err('Cannot find key \'%s\'.' % keys[i])
				i -= 1
				break
		if parent:
			return (parentbranch, i)
		else:
			return (branch, i)

