#!/usr/bin/env python3
import threading, time
import source.libs.define as lib
import source.libs.log as log

class Job:
    def __init__(self, name, start, job, timeout=None):
        self.name = name
        self.start = start
        self.job = job
        self.timeout = timeout




class Scheduler(threading.Thread):
    # takes care of modules running in the background
    def __init__(self):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.jobs = {}
        self.user_threads = []
        self.terminate = False


    def run(self):
        while not self.terminate: # quit program not requested
            self.lock.acquire()
            todel = []

            # BACKGROUND JOBS
            for x in self.jobs: # pinpoint dead background jobs
                s = self.jobs[x]
                if not s.job.isAlive():
                    todel.append(x)

            for x in todel: # remove them
                s = self.jobs[x]
                end = time.time()
                log.info('Background job %d (%s) has terminated (%s).' % (x, s.name, log.show_time(end-s.start)))
                del self.jobs[x]
            
            # USER THREADS
            todel = []
            for t in self.user_threads: # pinpoint dead user threads
                if not t.isAlive():
                    todel.append(t)

            for t in todel: # remove them
                self.user_threads.remove(t)

            self.lock.release()
            time.sleep(0.25)



    def stop(self):
        # scheduler should terminate (program is going to exit)
        self.lock.acquire()
        # terminate all jobs and user threads which supports it
        for j in self.jobs:
            if hasattr(self.jobs[j].job, 'stop'):
                self.jobs[j].job.stop()
                #log.info('Background job %d is going to terminate.' % j)

        for u in self.user_threads:
            if hasattr(u, 'stop'):
                u.stop()

        self.lock.release()
        while len(self.jobs) > 0: # wait for everything to die
            time.sleep(0.5)
        self.terminate = True # sets DIE flag for itself



    def add(self, name, start, job, timeout=None):
        # add a new job
        self.lock.acquire()
        jobid = self.newid() # get lowest unused id
        self.jobs[jobid] = Job(name, start, job, timeout)
        log.info('Module %s will run in the background with id %d.' % (name, jobid))
        self.lock.release()



    def newid(self):
        # only called from add() => lock in place
        result = 1
        while True:
            if result not in self.jobs:
                break
            result += 1
        return result



    def add_user_thread(self, thread):
        with self.lock:
            self.user_threads.append(thread)
    
    
    
    def show(self):
        now = time.time()
        self.lock.acquire()
        # compute column widths
        maxi = max([len(str(x)) for x in self.jobs] + [2])
        maxn = max([len(self.jobs[x].name) for x in self.jobs] + [4])
        times = [log.show_time(now - self.jobs[x].start) for x in self.jobs]
        maxt = max([len(t) for t in times] + [4])
        maxto = max([len(self.jobs[x].timeout) for x in self.jobs if self.jobs[x].timeout is not None] + [7])
        
        # print header
        log.writeline('%*s  %-*s  %-*s  %-*s' % (maxi, 'ID', maxn, 'NAME', maxt, 'TIME', maxto, 'TIMEOUT'))
        log.writeline('-' * maxi + '  ' + '-' * maxn + '  ' + '-' * maxt + '  ' + '-' * maxto, log.Color.PURPLE)
        # sort by ID
        keys = sorted(list(self.jobs))
        # print jobs
        for i in range(0, len(keys)):
            x = keys[i]
            log.writeline('%*s  %-*s  %*s  %-*s' % (maxi, x, maxn, self.jobs[x].name, maxt, times[i], maxto, '' if self.jobs[x].timeout is None else self.jobs[x].timeout))
        self.lock.release()



    def kill(self, jid):
        # kill specified job
        self.lock.acquire()
        if int(jid) in self.jobs:
            self.jobs[int(jid)].job.stop()
        else:
            print('[-] no jobid %s' % jid)
        self.lock.release()


# initialize global variable and start
lib.scheduler = Scheduler()
lib.scheduler.start()
