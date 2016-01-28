#!/usr/bin/env python
import threading
from include import *

class Job:
	def __init__(self, name, start, job, timeout=None):
		self.name = name
		self.start = start
		self.job = job
		self.timeout = timeout

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
			time.sleep(0.25)


	def stop(self):
		self.lock.acquire()
		for j in self.jobs:
			if hasattr(self.jobs[j].job, 'stop'):
				self.jobs[j].job.stop()
				#log.info('Background job %d is going to terminate.' % j)
		self.lock.release()
		while len(self.jobs) > 0: # wait for everything to die
			time.sleep(0.5)
		self.terminate = True
	
	def add(self, name, start, job, timeout=None):
		self.lock.acquire()
		jobid = self.newid()
		self.jobs[jobid] = Job(name, start, job, timeout)
		log.info('Module %s will run in the background with id %d.' % (name, jobid))
		self.lock.release()

	def newid(self):
		result = 1
		#self.lock.acquire()
		while True:
			if not self.jobs.has_key(result):
				break
			result += 1
		#self.lock.release()
		return result
	
	def show(self):
		now = time.time()
		self.lock.acquire()
		maxi = max([len(str(x)) for x in self.jobs] + [2])
		maxn = max([len(self.jobs[x].name) for x in self.jobs] + [4])
		times = [show_time(now - self.jobs[x].start) for x in self.jobs]
		maxt = max([len(t) for t in times] + [4])
		maxto = max([len(self.jobs[x].timeout) for x in self.jobs if self.jobs[x].timeout is not None] + [7])
		
		log.writeline('%*s  %-*s  %-*s  %-*s' % (maxi, 'ID', maxn, 'NAME', maxt, 'TIME', maxto, 'TIMEOUT'))
		log.writeline(log.Color.purple('-' * maxi + '  ' + '-' * maxn + '  ' + '-' * maxt + '  ' + '-' * maxto))
		keys = sorted(self.jobs.keys())
		for i in range(0, len(keys)):
			x = keys[i]
			log.writeline('%*s  %-*s  %*s  %-*s' % (maxi, x, maxn, self.jobs[x].name, maxt, times[i], maxto, '' if self.jobs[x].timeout is None else self.jobs[x].timeout))
		self.lock.release()

	def kill(self, jid):
		if int(jid) in self.jobs:
			self.jobs[int(jid)].job.stop()


