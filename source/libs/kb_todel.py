#!/usr/bin/env python3
import re, threading
import source.libs.log as log
import source.libs.define as lib

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
				branch = self.find(key[:existindex])

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
		branch = self.find(key[:-1])
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
		keys = [x for x in query.split(' ') if len(x)>0]
		# print the knowledge base/selected branch
		if len(keys) == 0:
			#log.attachline(json.dumps(self.kb, indent=4)) # not working in python3
			KB.get_structure(self.kb)
		else:
			# find the desired branch
			result = self.search(keys, parent=False, silent=False)
			log.attachline(' > '.join(keys[:result[1]+1])+':', log.Color.PURPLE)
			#log.attachline(json.dumps(result[0], indent=4))
			KB.get_structure(result[0])
	
	def delete(self, query=''):
		keys = [x for x in query.split(' ') if len(x)>0]
		# delete specified branch
		keys = [x for x in query.split(' ') if len(x)>0]
		self.lock.acquire()
		if len(keys) == 0:
			# delete everything
			self.kb = {}
		else:
			# find node holding branch to delete
			result = self.search(keys, parent=True)
			if result[1]+1<len(keys):
				# not found, not deleting
				pass
			else:
				# delete branch
				del result[0][keys[result[1]]]
				log.info('Entry %s has been deleted.' % ' > '.join(keys[:result[1]+1]))
		self.lock.release()
	
	def exists(self, keys):
		# check if a branch exists
		return self.search(keys, parent=False, silent=True, boolean=True)
	
	def find(self, keys):
		return self.search(keys, parent=False, silent=True, boolean=False)[0]

	def search(self, keys, parent=False, silent=True, boolean=False):
		i = 0
		if type(keys) is bytes:
			keys = keys.decode('utf-8')
		if type(keys) is str:
			keys = [x for x in keys.split(' ') if len(x)>0]
		branch = self.kb
		parentbranch = None
		# search branch one key at a time
		for i in range(0, len(keys)):
			parentbranch = branch
			# working with dict? is the key present?
			if type(branch) == dict and keys[i] in branch:
				branch = branch[keys[i]]
			# list or tuple? is key a number? is the key there?
			elif (type(branch) == list or type(branch) == tuple) and keys[i].isdigit() and int(keys[i])<len(branch):
				branch = branch[int(keys[i])]
			# dealing with last key and the branch is only a string?
			elif i == len(keys)-1 and type(branch) == str:
				tmpbranch = [x for x in branch.splitlines() if keys[i] in x]
				if len(tmpbranch) == 0:
					if not silent:
						log.err('Cannot find key \'%s\'.' % keys[i])
					if boolean:
						return False # key not found
					i -= 1
					break		
				if boolean:
					return True
				else:
					if parent:
						return (parentbranch, i)
					else:
						return (tmpbranch, i)
			# weird branch type
			else:
				if not silent:
					log.err('Cannot find key \'%s\'.' % keys[i])
				if boolean:
					return False # key not found
				i -= 1
				break
		if boolean:
			return True # key found
		else:
			if parent:
				return (parentbranch, i) # return parent node of last branch found
			else:
				return (branch, i) # return last branch found


	@staticmethod
	def get_structure(data, tab = 0):
		""" print a given Knowledge Base branch """
		# dictionary
		if type(data) is dict:
			log.attachline(' ' * tab + '{')
			for key in natural_sort(data):
				log.attachline(' ' * tab + '  ' + key + ':')
				KB.get_structure(data[key], tab + 4)
			log.attachline(' ' * tab + '}')
		# list
		elif type(data) is list and len(data) > 0:
			log.attachline(' ' * tab + '[')
			KB.get_structure(data[0], tab+4)
			log.attachline(' ' * tab + ']')
		# unicode string
		elif type(data) is str:
			for line in data.splitlines():
				log.attachline(' ' * tab + line)
		# bytes, transform to unicode string
		elif type(data) is bytes:
			data = data.decode('utf-8')
			for line in data.splitlines():
				log.attachline(' ' * tab + line)

def natural_sort(data):
	return sorted(data, key=lambda x: [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', x)])

# initialize global variable
lib.kb = KB()
