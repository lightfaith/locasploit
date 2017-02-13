#!/usr/bin/env python3
import threading, time
import source.libs.define as lib
import source.libs.log as log
from source.libs.search import search_abbr

class Job:
    def __init__(self, name, start, job, timeout=None, waitfor=None):
        self.name = name
        self.start = start
        self.job = job
        self.timeout = timeout
        self.waitfor = waitfor



class Scheduler(threading.Thread):
    # takes care of modules running in the background
    def __init__(self):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.jobs = {}
        self.waitjobs = {}
        self.user_threads = []
        self.terminate = False


    def run(self):
        while not self.terminate: # quit program not requested
            self.lock.acquire()
            todel = []

            # BACKGROUND JOBS
            for x in self.jobs: # pinpoint dead background jobs
                s = self.jobs[x]
                if not s.job.is_alive():
                    todel.append(x)

            for x in todel: # remove them
                s = self.jobs[x]
                end = time.time()
                log.info('Background job %d (%s) has terminated (%s).' % (x, s.name, log.show_time(end-s.start)))
                del self.jobs[x]
            
            # USER THREADS
            todel = []
            for t in self.user_threads: # pinpoint dead user threads
                if not t.is_alive():
                    todel.append(t)

            for t in todel: # remove them
                self.user_threads.remove(t)

            # check waiting jobs
            # TODO
            todel = []
            for k, v in self.waitjobs.items():
                if len(set(v.waitfor).intersection(self.jobs.keys())) == 0:
                    # move waitjob to jobs, start it
                    todel.append(k)
                    log.info('Background job %d (%s) is no longer waiting.' % (k, v.name))
                    start = time.time()
                    v.job.start()
                    v.start = start
                    self.jobs[k] = v
            for x in todel:
                del self.waitjobs[x]

            self.lock.release()
            time.sleep(0.25)



    def stop(self):
        # scheduler should terminate (program is going to exit)
        self.lock.acquire()
        # kick waiting jobs
        self.waitjobs = {}
        # terminate all jobs and user threads which supports it
        for j in self.jobs:
            if hasattr(self.jobs[j].job, 'stop'):
                self.jobs[j].job.stop()
                #log.info('Background job %d is going to terminate.' % j)
            else:
                log.warn('%s cannot be terminated by force.' % (self.jobs[j].name))

        for u in self.user_threads:
            if hasattr(u, 'stop'):
                u.stop()

        self.lock.release()
        while len(self.jobs) > 0 and len(self.user_threads) > 0: # wait for everything to die
            time.sleep(0.5)
        self.terminate = True # sets DIE flag for itself



    def add(self, name, start, job, timeout=None, waitfor=None):
        # add a new job
        self.lock.acquire()
        jobid = self.newid() # get lowest unused id
        if waitfor is None:
            self.jobs[jobid] = Job(name, start, job, timeout)
            job.start()
            log.info('Module %s will run in the background with id %d.' % (name, jobid))
        else:
            # what to wait for?
            ids_to_wait_for = []
            for x in waitfor:
                if type(x) == int:
                    ids_to_wait_for.append(x)
                elif type(x) == str:
                    if x.isdigit():
                        ids_to_wait_for.append(int(x))
                    else:
                        matches = search_abbr(x, lib.modules.keys())
                        ids_to_wait_for += [k for k,v in self.jobs.items() if v.name in matches]
                else:
                    log.warn('Could not process wait parameter \'%s\', ignoring...' % (x))
                    continue
            ids_to_wait_for = list(set(ids_to_wait_for))
            self.waitjobs[jobid] = Job(name, start, job, timeout, ids_to_wait_for)
            log.info('Module %s with id %d will be executed after following jobs finish: %s' % (name, jobid, ', '.join(map(str, ids_to_wait_for))))

        self.lock.release()
        return jobid



    def newid(self):
        # only called from add() => lock in place
        result = 1
        while True:
            if result not in self.jobs and result not in self.waitjobs:
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
        maxi = max([len(str(x)) for l in [self.jobs, self.waitjobs] for x in l] + [2])
        maxn = max([len(l[x].name) for l in [self.jobs, self.waitjobs] for x in l] + [4])
        times = [log.show_time(now - l[x].start) for l in [self.jobs, self.waitjobs] for x in l]
        waittimes = [log.show_time(0.0) for x in self.waitjobs]
        maxt = max([len(t) for t in times] + [4])
        maxto = max([len(str(l[x].timeout)) for l in [self.jobs, self.waitjobs] for x in l if l[x].timeout is not None] + [7])
        maxs = max([len(x) for x in ['STATUS', 'running', 'waiting']])

        # print header
        log.writeline('%*s  %-*s  %-*s  %-*s  %-*s' % (maxi, 'ID', maxn, 'NAME', maxt, 'TIME', maxto, 'TIMEOUT', maxs, 'STATUS'))
        log.writeline('-' * maxi + '  ' + '-' * maxn + '  ' + '-' * maxt + '  ' + '-' * maxto + '  ' + '-'*maxs, log.Color.PURPLE)
        # sort by ID

        # print running jobs
        keys = sorted(list(self.jobs))
        for i in range(0, len(self.jobs)):
            x = keys[i]
            log.writeline('%*s  %-*s  %*s  %-*s  %-*s' % (maxi, x, maxn, self.jobs[x].name, maxt, times[i], maxto, '' if self.jobs[x].timeout is None else self.jobs[x].timeout, maxs, 'running'))

        # print waiting jobs
        keys = sorted(list(self.waitjobs))
        for i in range(0, len(self.waitjobs)):
            x = keys[i]
            log.writeline('%*s  %-*s  %*s  %-*s  %-*s' % (maxi, x, maxn, self.waitjobs[x].name, maxt, waittimes[i], maxto, '' if self.waitjobs[x].timeout is None else self.waitjobs[x].timeout, maxs, 'waiting'))
        self.lock.release()



    def kill(self, jid):
        # kill specified job
        self.lock.acquire()
        if int(jid) in self.jobs:
            self.jobs[int(jid)].job.stop() # scheduler will remove it properly
        elif int(jid) in self.waitjobs:
            del self.waitjobs[int(jid)]
        else:
            print('[-] no jobid %s' % jid)
        self.lock.release()


# initialize global variable and start
lib.scheduler = Scheduler()
lib.scheduler.start()
