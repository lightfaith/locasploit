#!/usr/bin/env python
import log, threading

class KB:
	# now a dictionary, later maybe some database
	def __init__(self):
		self.kb = {}
		self.lock = threading.Lock()
	
	def add(self, key, data):
		# split into words if given as a string
		if type(key) == str:
			key = key.split(' ')
		
		# index of the deepest known keyword (-1 = nowhere)
		existindex = -1
		if not self.exists(key[:-1]):
			# parent does not exist - create dictionaries
			self.lock.acquire()
			for i in range(0, len(key[:-1])):
				if self.exists(key[:len(key)-i-1]):
					existindex = i
					break
			# existindex should be correct here
			if existindex == -1: # not found anything => kb itself
				branch = self.kb
				existindex = 0 # noted, now create from first...
			else: # work with the existing branch
				branch = self.find(key[:existindex])[0]

			# create dictionaries except last one (that will be added as a key)
			for x in key[existindex:-1]:
				branch[x] = {}
				branch = branch[x]
			
			self.lock.release()

			# now the tree should be ok for addition, try again
			self.add(key, data)
			return

		# tree is ok, add it there
		self.lock.acquire()
		branch = self.find(key[:-1])[0]
		# add the last key 
		if type(branch) == dict:
			branch[key[-1]] = data
		elif type(branch) == list:
			branch += data #TODO correct?
		elif type(branch) == str:
			branch += data #TODO correct?
		elif type(branch) == tuple:
			log.err('You cannot add data into an existing tuple.')
		else:
			log.err('Attempt to add structure into one of unsupported type: %s.' % type(branch))
		self.lock.release()


	def dump(self, query=''):
		import json
		keys = [x for x in query.split(' ') if len(x)>0]
		if len(keys) == 0:
			log.attachline(json.dumps(self.kb, indent=4))
		else:
			result = self.find(keys, parent=False, silent=False)
			log.attachline(' > '.join(keys[:result[1]+1])+':', log.Color.PURPLE)
			log.attachline(json.dumps(result[0], indent=4))
	
	def delete(self, query=''):
		keys = [x for x in query.split(' ') if len(x)>0]
		self.lock.acquire()
		if len(keys) == 0:
			self.kb = {}
		else:
			result = self.find(keys, parent=True)
			if result[1]+1<len(keys):
				#log.info('not found, not deleting...')
				pass
			else:
				del result[0][keys[result[1]]]
				log.info('Entry %s has been deleted.' % ' > '.join(keys[:result[1]+1]))
		self.lock.release()
	
	def exists(self, keys):
		return self.find(keys, parent=False, silent=True, boolean=True)
	
	def find(self, keys, parent=False, silent=True, boolean=False):
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
					if not silent:
						log.err('Cannot find key \'%s\'.' % keys[i])
					if boolean:
						return False
					i -= 1
					break		
				if boolean:
					return True
				else:
					if parent:
						return (parentbranch, i)
					else:
						return (tmpbranch, i)
			else:
				if not silent:
					log.err('Cannot find key \'%s\'.' % keys[i])
				if boolean:
					return False
				i -= 1
				break
		if boolean:
			return True
		else:
			if parent:
				return (parentbranch, i)
			else:
				return (branch, i)

