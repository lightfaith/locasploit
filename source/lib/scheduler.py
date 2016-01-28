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
		jobid = self.newid()
		self.jobs[jobid] = Job(name, start, job)
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
		
		log.writeline('%*s  %-*s  %-*s' % (maxi, 'ID', maxn, 'NAME', maxt, 'TIME'))
		log.writeline(log.Color.purple('-' * maxi + '  ' + '-' * maxn + '  ' + '-' * maxt))
		keys = sorted(self.jobs.keys())
		for i in range(0, len(keys)):
			x = keys[i]
			log.writeline('%*s  %-*s  %*s' % (maxi, x, maxn, self.jobs[x].name, maxt, times[i]))
		self.lock.release()
