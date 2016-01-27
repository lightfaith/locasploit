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

	def save(self, key, subkey, value):
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
