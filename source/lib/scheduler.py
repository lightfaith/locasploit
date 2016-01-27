#!/usr/bin/env python
import threading
from include import *

class Job:
    def __init__(self, name, start, job):
        self.name = name
        self.start = start
        self.job = job

class Scheduler(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.lock = threading.Lock()
		self.jobs = {}
		self.terminate = False
	
	def run(self):
		# clear complete
		while not self.terminate:
			todel = []
			self.lock.acquire()
			for x in self.jobs: # pinpoint dead ones
				s = self.jobs[x]
				if not s.job.isAlive():
					todel.append(x)

			for x in todel: # remove them
				s = self.jobs[x]
				end = time.time()
				log.info('Background job %d (%s) has terminated (%s).' % (x, s.name, show_time(end-s.start)))
				del self.jobs[x]

			self.lock.release()
			time.sleep(0.5)


	def stop(self):
		self.terminate = True
	
	def add(self, name, start, job):
		self.lock.acquire()
		#jobid = self.newid()
		jobid = 1
		self.jobs[jobid] = Job(name, start, job)
		log.info('Module %s will run in the background with id %d.' % (name, jobid))
		self.lock.release()

	def newid(self):
		result = 1
		self.lock.acquire()
		while True:
			if result not in self.jobs:
				break
			result += 1
		self.lock.release()
		return result
	
	def show(self):
		now = time.time()
		self.lock.acquire()
		for x in self.jobs:
			s = self.jobs[x]
			print x, s.name, now-s.start
		self.lock.release()
