#!/usr/bin/env python3
"""
SQL queries for core databases are here.
"""
#from source.libs.include import *
#from source.libs.define import *
import time, re
import sqlite3 as sqlite
import source.libs.define as lib
import source.libs.log as log


DB_ERROR = lib.DB_ERROR

class DB(object):
    def __init__(self, file):
        self.connection = sqlite.connect(file, check_same_thread=False)
        self.cursor = self.connection.cursor()
    
    def close(self):
        self.commit()
        self.connection.close()
    
    def execute(self, command, parameters=None, commit=True, ignoreerrors=False):
        try:
            #print('$', command)
            if parameters is None:
                self.cursor.execute(command)
            else:
                self.cursor.execute(command, parameters)
            if commit:
                self.commit()
            return self.cursor.fetchall()
        except Exception as e:
            if not ignoreerrors:
                log.err(str(e) + ' -- ' + command)
            return DB_ERROR
    
    def executemany(self, command, parameters, ignoreerrors=False):
        try:
            self.connection.executemany(command, parameters)
            self.commit()
            return True
        except Exception as e:
            if not ignoreerrors:
                log.err(str(e) + ' for ' + command)
            return DB_ERROR
    
    def query(self, command):
        return self.execute(command)
        
    def commit(self):
        self.connection.commit()
    
    def get_column(self, result, column):
        return [c[column] for c in result]
    # -------------------------------------------------- 
    def version(self):
        self.execute('SELECT SQLITE_VERSION()')
        data = self.cursor.fetchone()
        log.info("SQLite version: %s" % data)
    
    def get_tables(self):
        return [x for x in self.get_column(self.execute("SELECT name FROM sqlite_master WHERE type='table'"), 0) if x != 'sqlite_sequence']

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class DBDictionary(DB):
    def __init__(self, file):
        super().__init__(file)
    
    def add_dictionary(self, name, checksum=None):
        select = self.execute("SELECT dictionaryid FROM Dictionary WHERE name = :n", {'n' : name})
        if select ==  DB_ERROR:
            return DB_ERROR
        if len(select) == 0:
            if checksum is None:
                self.execute("INSERT INTO Dictionary (name) VALUES(:n)", {'n' : name})
            else:
                self.execute("INSERT INTO Dictionary (name, checksum) VALUES(:n, :c)", {'n' : name, 'c' : checksum})
        return True
    
    def add_words(self, words, dictionary, checksum=None):
        d = self.add_dictionary(dictionary, checksum)
        if d == DB_ERROR:
            return DB_ERROR
        # add new words
        # transaction method 1
        targs = [(w,) for w in words]
        #iw = self.executemany("INSERT OR IGNORE INTO Word(word) VALUES(?)", twords)
        iw = self.executemany("INSERT OR IGNORE INTO Word(word) VALUES(?)", targs)
        if iw == DB_ERROR:
            return DB_ERROR
        # make relationships betweek words and dictionary
        # transaction method 2
        self.execute("BEGIN", commit=False)
        for word in words:
            idw = self.execute(
                "INSERT OR IGNORE INTO DWord(fk_dictionary, fk_word) SELECT d.dictionaryid, w.wordid from Dictionary d, Word w WHERE d.name = :d AND w.word = :w",
                {'d' : dict, 'w' : word}, commit=True if word == words[-1] else False)
            if idw == DB_ERROR:
                return DB_ERROR
        self.commit() 
        if idw == DB_ERROR:
            return DB_ERROR
        return True
    
    def get_summary(self):
        select = self.execute("SELECT d.name, COUNT(dw.fk_word), d.checksum FROM Dictionary d LEFT JOIN DWord dw ON d.dictionaryid = dw.fk_dictionary GROUP BY d.name, d.checksum")
        if select == DB_ERROR:
            return DB_ERROR
        return select
     
    def get_dictionaries(self):
        select = self.execute("SELECT name FROM Dictionary")
        if select == DB_ERROR:
            return DB_ERROR
        return [t[0] for t in select]
    
    def get_dictionary(self, dictionary):
        select =  self.execute("SELECT word from Word WHERE wordid IN ( \
                                    SELECT fk_word FROM DWord WHERE fk_dictionary = ( \
                                        SELECT dictionaryid from Dictionary WHERE name = :d)) \
                                ORDER BY word", {'d' : dictionary})
        if select == DB_ERROR:
            return DB_ERROR
        return [t[0] for t in select]
    
    def dump_words(self):
        select = self.execute("SELECT word FROM Word ORDER BY word")
        if select == DB_ERROR:
            return DB_ERROR
        return [t[0] for t in select]
    
    def delete_dictionary(self, dictionary):
        self.execute("DELETE FROM DWord WHERE fk_dictionary IN (SELECT" \
            "dictionaryid FROM Dictionary WHERE name = :d)", {'d': dictionary})
        self.execute("DELETE FROM Dictionary WHERE name = :d", {'d': dictionary})
        self.clean()
   
    def delete_dictionaries(self):
        self.execute("DELETE FROM DWord")
        self.execute("DELETE FROM Word")
        self.execute("DELETE FROM Dictionary")


    def clean(self):
        # discard words with no dictionary
        self.execute("DELETE FROM Word WHERE wordid NOT IN (SELECT fk_word FROM DWord)")
        # clear temporary table
        self.execute("DELETE FROM Temporary")

    def add_tmp_words(self, tag, words):
        targs = [(tag, w) for w in words]
        it = self.executemany("INSERT OR IGNORE INTO Temporary(tag, word) VALUES(?, ?)", targs)
        if it == DB_ERROR:
            return DB_ERROR
        return True
    
    def get_tmp_tags(self):
        select = self.execute("SELECT DISTINCT tag FROM Temporary")
        if select == DB_ERROR:
            return DB_ERROR
        return [t[0] for t in select]
    
    def get_match_percent(self, dictionary, tags):
        result = self.execute("SELECT t1.tag, COUNT(t1.word), (SELECT COUNT(t2.word) FROM Temporary t2 WHERE t2.tag = t1.tag) \
                    FROM Temporary t1 WHERE t1.word IN (SELECT w.word FROM Word w JOIN DWord dw ON w.wordid = dw.fk_word \
                    WHERE dw.fk_dictionary IN (SELECT dictionaryid FROM Dictionary WHERE name = :d)) GROUP BY tag", {'d': dictionary})
        if result == DB_ERROR:
            return DB_ERROR
        return [(t[0], dictionary, t[1]/t[2]) for t in result]
        

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class DBVuln(DB):
    def __init__(self, file):
        super().__init__(file)
    

    def add_cves(self, cvetuples):
        attribs = ['name', 'severity', 'CVSS_version', 'CVSS_score', 'CVSS_base_score', 'CVSS_impact_subscore', 'CVSS_exploit_subscore', 'CVSS_vector', 'description']
        
        self.execute("BEGIN", commit=False)
        for cvetuple in cvetuples:
            # add missing parameters
            for a in attribs:
                if a not in cvetuple[0].keys():
                    cvetuple[0][a] = ''
            cvetuple[0]['description'] = cvetuple[1]
            result = self.execute('INSERT OR REPLACE INTO CVE(name, severity, cvss_version, cvss_score, cvss_base, cvss_impact, cvss_exploit, cvss_vector, description) VALUES(:name, :severity, :CVSS_version, :CVSS_score, :CVSS_base_score, :CVSS_impact_subscore, :CVSS_exploit_subscore, :CVSS_vector, :description)', cvetuple[0], commit=False)
        self.commit() 
        
    def get_sortable_version(self, version):
        result = []
        for part in version.split('.'):
            try:
                digit = re.search(r'\d+', part).group()
                if digit.isdigit():
                    result.append('%08d%s' % (int(digit), part[len(digit):]))
                else:
                    raise TypeError # use whole part
            except:
                result.append(part)
        return '.'.join(result)
        

    def add_apps_for_cves(self, actuples):
        # (cveid, product, vendor, version, prev)
        
        self.execute("BEGIN", commit=False)
        for cve, product, vendor, version, prev in actuples:
            sortable = self.get_sortable_version(version)
            cveids = self.execute("SELECT cveid FROM CVE WHERE name=:c", {'c': cve}, commit=False)
            if len(cveids) == 0:
                continue
            self.execute("INSERT OR IGNORE INTO Vendor(name) VALUES(:v)", {'v': vendor}, commit=False, ignoreerrors=True)
            vendorid = int(self.execute("SELECT vendorid FROM vendor WHERE name=:v", {'v': vendor}, commit=False)[0][0])
            self.execute("INSERT OR IGNORE INTO Product(vendorid, name) VALUES(:vid, :p)", {'vid': vendorid, 'p': product}, commit=False, ignoreerrors=True)
            productid = int(self.execute("SELECT productid FROM product WHERE vendorid=:vid AND name=:p", {'vid': vendorid, 'p': product}, commit=False)[0][0])
            self.execute("INSERT OR IGNORE INTO Version(productid, value, sortable, prev) VALUES(:pid, :v, :s, :p)", {'pid': productid, 'v': version, 's': sortable, 'p': prev}, commit=False, ignoreerrors=True)
            versionid = int(self.execute("SELECT versionid FROM Version WHERE productid=:pid AND value=:v", {'pid': productid, 'v': version}, commit=False)[0][0])
            self.execute('INSERT OR IGNORE INTO CV(cveid, versionid) VALUES(:cid, :vid)', {'cid': cveids[0][0], 'vid': versionid}, commit=False, ignoreerrors=True)
            
        self.commit()
        return True

    
    def delete_cves_apps(self):
        from datetime import datetime
        self.execute("BEGIN", commit=False)
        self.execute("DELETE FROM CV", commit=False)
        self.execute("DELETE FROM Version", commit=False)
        self.execute("DELETE FROM Product", commit=False)
        self.execute("DELETE FROM Vendor", commit=False)
        self.execute("DELETE FROM CVE", commit=False)
        for year in range(2002, datetime.now().year+1):
            self.execute("DELETE FROM Property WHERE key='%d_sha1'" % (year), commit=False)
        self.commit()


    def add_property(self, key, value):
        result = self.execute("INSERT OR REPLACE INTO Property(key, value) VALUES(:k, :v)", {'k': key, 'v': value})
        if result == DB_ERROR:
            return DB_ERROR
        return True

    def get_property(self, key):
        result = self.execute("SELECT value FROM Property WHERE key=:k", {'k': key})
        if result == DB_ERROR or len(result)<1:
            return DB_ERROR
        return result[0][0]

    def add_tmp(self, data):
        self.execute("BEGIN", commit=False)
        for tag, name, vendor, version in data:
            sortable = self.get_sortable_version(version)
            result = self.execute("INSERT OR IGNORE INTO Temporary(tag, name, vendor, version, sortable) VALUES(:t, :n, :vn, :vr, :s)", {'t': tag, 'n': name, 'vn':vendor, 'vr':version, 's': sortable}, commit=False)
        self.commit()
        if result == DB_ERROR:
            return DB_ERROR
        return True


    def count_tmp(self, tag):
        result = self.execute("SELECT COUNT(*) FROM Temporary WHERE tag = :t", {'t': tag})
        if result == DB_ERROR:
            return DB_ERROR
        return result[0][0]


    def get_cves_for_apps(self, tag, checkversion=True):
        #result = self.execute("SELECT DISTINCT Ven.name, P.name, V.value, CVE.*, (case CVE.severity when 'High' then 2 when 'Medium' then 1 else 0 end) as sort FROM Vendor Ven INNER JOIN Product P ON Ven.vendorid = P.vendorid INNER JOIN Version V ON P.productid = V.productid INNER JOIN CV ON CV.versionid = V.versionid INNER JOIN CVE ON CVE.cveid = CV.cveid WHERE EXISTS(SELECT * FROM Temporary where name = p.name %s AND tag=:t) ORDER BY sort DESC, CVE.name DESC" % ("AND (version LIKE v.value||'%%' OR v.value='' OR v.value='-' OR (v.prev=1 AND v.sortable>sortable))" if checkversion else ''), {'t': tag})
        result = self.execute("SELECT DISTINCT Ven.name, P.name, V.value, CVE.*, (case CVE.severity when 'High' then 2 when 'Medium' then 1 else 0 end) as sort FROM Vendor Ven INNER JOIN Product P ON Ven.vendorid = P.vendorid INNER JOIN Version V ON P.productid = V.productid INNER JOIN CV ON CV.versionid = V.versionid INNER JOIN CVE ON CVE.cveid = CV.cveid WHERE EXISTS(SELECT * FROM Temporary where name = p.name %s AND tag=:t) ORDER BY sort DESC, CVE.name DESC" % ("AND (sortable LIKE v.sortable||'%%' OR v.value='' OR v.value='-' OR (v.prev=1 AND v.sortable>sortable))" if checkversion else ''), {'t': tag})
        if result == DB_ERROR:
            return []
        # return only unique cves, sort by severity and CVE
        return sorted(dict((x[4], x) for x in result).values(), key=lambda x: (x[13], x[4]), reverse=True)


    def add_exploits(self, exploits):
        # add all exploits first
        self.execute("BEGIN", commit=False)
        for eid in sorted(exploits.keys()):
            self.execute("INSERT OR IGNORE INTO Exploit(name) VALUES(:e)", {'e': eid}, commit=False)
        self.commit()
        # add ce relationships
        cepairs = [(k, x) for k,v in exploits.items() for x in v]
        self.execute("BEGIN", commit=False)
        for exploit, cve in cepairs:
            self.execute("INSERT OR IGNORE INTO CE(exploitid, cveid) SELECT e.exploitid, c.cveid FROM Exploit e, CVE c WHERE e.name=:e and c.name=:c", {'e': exploit, 'c': cve}, commit=False)
        self.commit()

    def get_exploits_for_cve(self, cve):
        result = self.execute("SELECT e.name FROM Exploit e INNER JOIN CE ce ON e.exploitid=ce.exploitid WHERE ce.cveid IN (SELECT cveid FROM CVE WHERE name=:c)", {'c': cve})
        if result == DB_ERROR or len(result) == 0:
            return []
        return [x[0] for x in result]

    def clean(self):
        result = self.execute("DELETE FROM Temporary")
        return result

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class DBChecksum(DB):
    def __init__(self, file):
        super().__init__(file)
    
    def clean(self):
        # clear temporary table
        self.execute("DELETE FROM Temporary")
    
    def add_checksum(self, name, version, _file, app_comment=None, md5=None, sha1=None, sha256=None):
        if md5 is None:
            md5 = ''
        if sha1 is None:
            sha1 = ''
        if sha256 is None:
            sha256 = ''
        self.execute("BEGIN", commit=False)
        self.execute("INSERT OR IGNORE INTO Application(name, version, comment) VALUES(:n, :v, :c)", {'n': name, 'v': version, 'c': app_comment}, commit=False, ignoreerrors=True)
        appid = int(self.execute("SELECT id from Application WHERE name=:n AND version=:v AND comment=:c", {'n': name, 'v': version, 'c': app_comment})[0][0])
        if appid == DB_ERROR:
            return DB_ERROR
        self.execute("INSERT OR IGNORE INTO Checksum(file, fk_appid, md5, sha1, sha256) VALUES(:f, :id, :m, :s1, :s2)", {'f': _file, 'id': appid, 'm': md5, 's1': sha1, 's2': sha256}, commit=False, ignoreerrors=True)
        self.commit()

    def add_tmp_checksum(self, tag, md5=None, sha1=None, sha256=None):
        select = self.execute("SELECT * FROM Temporary WHERE tag = :t AND md5 = :m AND sha1=:s1 AND sha256=:s256", {'t': tag, 'm': md5, 's1': sha1, 's256': sha256})
        if select == DB_ERROR:
            return DB_ERROR
        if len(select) == 0:
            result = self.execute("INSERT OR REPLACE INTO Temporary(tag, md5, sha1, sha256) VALUES(:t, :m, :s1, :s256)", {'t': tag, 'm': md5, 's1': sha1, 's256': sha256})
            if result == DB_ERROR:
                return DB_ERROR
        return True

    def get_apps_for_checksums(self, tag):
        result = self.execute("SELECT A.name, A.version, A.comment, C.file, C.md5, C.sha1, C.sha256 FROM Application A INNER JOIN Checksum C ON A.id = C.fk_appid WHERE EXISTS(SELECT T.* from Temporary T WHERE T.tag = :t AND (T.md5=C.md5 OR T.sha1=C.sha1 OR T.sha256=C.sha256))", {'t': tag})
        if result == DB_ERROR:
            return []
        return result
    
    def clean(self):
        result = self.execute("DELETE FROM Temporary")
        return result
        

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class DBAnalysis(DB):
    def __init__(self, file):
        super().__init__(file)
    
    # SESSION 
    def get_last_session(self):
    
        result = self.execute("SELECT MAX(sessionid) FROM session")
        try:
            result = self.get_column(result, 0)[0]
        except:
            return None
        if result is None:
            return 1
        return result
    
    def get_new_session(self):
        result = self.get_last_session()
        return result + 1
    
    def create_session(self, sessionid):
        select = self.execute("SELECT sessionid FROM Session WHERE sessionid = :sid", {'sid': sessionid})
        if select == DB_ERROR:
            return DB_ERROR
        if len(select) == 0:
            result = self.execute("INSERT INTO Session (sessionid, created) VALUES(:sid, :created)", {'sid': sessionid, 'created': time.time()})
            if result == DB_ERROR:
                return DB_ERROR
        return True
    
    # NOTE
    def add_note(self, text, typ, unique=False):
        if self.create_session(lib.active_session) == DB_ERROR:
            return DB_ERROR
        if unique:
            select = self.execute("SELECT * FROM Note WHERE fk_sessionid = :sid AND type = :type AND text=:t", {'sid': lib.active_session, 'type': typ, 't': text})
            if select ==  DB_ERROR:
                return DB_ERROR
            if len(select) > 0:
                return True # already there
        result = self.execute("INSERT INTO Note(text, type, fk_sessionid, timestamp) VALUES(:text, :type, :sid, :ts)", {'text': text, 'type': typ, 'sid': lib.active_session, 'ts': time.time()})
        if result == DB_ERROR:
            return DB_ERROR
        return True
    
    # SYSTEM
    def create_system(self, root):
        #if self.create_session(sessionid) == DB_ERROR:
        #    return DB_ERROR
        select = self.execute("SELECT * FROM System WHERE root = :r AND fk_sessionid=:sid AND local_uuid = :u", 
                              {'r': root, 'sid': lib.active_session, 'u': lib.global_parameters['UUID']})
        if select ==  DB_ERROR:
            return DB_ERROR
        if len(select) == 0:
            result = self.execute("INSERT INTO System(root, this, fk_sessionid, local_uuid) VALUES(:r, :this, :sid, :u)", 
                                  {'r': root, 'this': 1 if root == '/' else 0, 'sid': lib.active_session, 'u': lib.global_parameters['UUID']})
            if result == DB_ERROR:
                return DB_ERROR
            # try to determine platform
            platform = None
            if root == '/':
                import sys
                platform = sys.platform
            if platform is not None:
                log.ok("Detected OS platform for '%s': %s" % (root, platform))
                #result = self.add_property(root, 'platform', platform)
                systemid = self.get_systemid(root)
                if systemid == DB_ERROR:
                    return DB_ERROR
                result = self.add_data('platform', systemid, platform)
                if result == DB_ERROR:
                    return DB_ERROR
        return True
    
    def get_systemid(self, root, sessionid=None):
        if sessionid is None:
            sessionid = lib.active_session
        select = self.execute("SELECT systemid FROM System WHERE root=:r AND fk_sessionid=:sid AND local_uuid=:u", {'r': root, 'sid' :sessionid, 'u': lib.global_parameters['UUID']})
        if select == DB_ERROR:
            return DB_ERROR
        if len(select) != 1:
            return DB_ERROR
        return select[0][0]
        
    # FILE
    def add_file(self, root, path, typ, permissions, uid, gid, content, atime, mtime, ctime, md5=None, sha1=None):
        if self.create_system(root) == DB_ERROR:
            return DB_ERROR
        systemid = self.get_systemid(root)
        if systemid == DB_ERROR:
            return DB_ERROR

        md5 = None
        sha1 = None
        if content is not None:
            import hashlib
            if md5 is None:
                md5 = hashlib.md5(content.encode('utf-8')).hexdigest()
            if sha1 is None:
                sha1 = hashlib.sha1(content.encode('utf-8')).hexdigest()
        result = self.execute(
            "INSERT OR REPLACE INTO File(path, fk_systemid, type, permissions, uid, gid, content, atime, mtime, ctime, timestamp, md5, sha1) VALUES(:p, :sid, :t, :perm, :u, :g, :c, :at, :mt, :ct, :ts, :m, :s)", 
            {'p': path, 'sid': systemid, 't': typ, 'perm': permissions, 'u': uid, 'g': gid, 'c': content, 'at': atime, 'mt': mtime, 'ct': ctime, 'ts': time.time(), 'm': md5, 's':sha1})
        if result == DB_ERROR:
            return DB_ERROR
        
        return True
    
    # PROPERTY
    
    """def add_property(self, systemroot, typ, value, uniquetype=False):
        if self.create_system(systemroot) == DB_ERROR:
            return DB_ERROR
        systemid = self.get_systemid(systemroot)
        if systemid == DB_ERROR:
            return DB_ERROR
        if uniquetype: 
            select = self.execute("SELECT * FROM Property WHERE fk_systemid = :sid AND type = :t", {'sid': systemid, 't': typ})
        else:
            select = self.execute("SELECT * FROM Property WHERE fk_systemid = :sid AND type = :t and value = :v", {'sid': systemid, 't': typ, 'v': value})
        if select ==  DB_ERROR:
            return DB_ERROR
        if len(select) == 0:
            result = self.execute("INSERT INTO Property(fk_systemid, type, value) VALUES (:sid, :t, :v)", {'sid': systemid, 't': typ, 'v': value})
            if result == DB_ERROR:
                return DB_ERROR
        return True
    """    
    
    # USER
    def add_users(self, systemroot, users, typ):
        if self.create_system(systemroot) == DB_ERROR:
            return DB_ERROR
        systemid = self.get_systemid(systemroot)
        if systemid == DB_ERROR:
            return DB_ERROR

        # what is the structure?
        targs = None
        if typ == lib.USERS_UNIX:
            targs = [(systemid, u[0], u[2], u[5], u[6], 1 if u[2] == 0 else 0) for u in users]
        elif typ == lib.USERS_UNIXLIKE:
            targs = [(systemid, u[0], u[2], u[5], u[6], u[7]) for u in users]
        
        if targs is None:
            return DB_ERROR
        result = self.executemany("INSERT OR REPLACE INTO User (fk_systemid,  name, uid, home, shell, privileged) VALUES(?, ?, ?, ?, ?, ?)", targs)
        
        if result == DB_ERROR:
            return DB_ERROR
        return True
        
    def get_users(self, systemroot):
        systemid = self.get_systemid(systemroot)
        if systemid == DB_ERROR:
            return []
        return self.execute("SELECT * FROM User WHERE fk_systemid = :sid", {'sid': systemid})


    def add_group(self, systemroot, gid, name, comment=None):
        # NOT IMPLEMENTED
        pass
    
    # CRON
    def add_cron(self, systemroot, entries):
        systemid = self.get_systemid(systemroot)
        if systemid == DB_ERROR:
            return DB_ERROR
        self.execute("BEGIN", commit=False)
        result = True
        for entry in entries:
            if len(entry)==3:
                result = self.execute("INSERT OR IGNORE INTO Cron(fk_systemid, timing, user, command) VALUES(:s, :t, :u, :c)", {'s': systemid, 't': entry[0], 'u': entry[1], 'c': entry[2]}, commit=False)
                if result == DB_ERROR:
                    break
        self.commit()
        return result
    
    def get_cron(self, systemroot):
        systemid = self.get_systemid(systemroot)
        if systemid == DB_ERROR:
            return []
        return self.execute("SELECT timing, user, command FROM Cron WHERE fk_systemid=:s", {'s': systemid})
    

    # DATA
    def get_data(self, key, subkey, like=False):
        if like:
            result = self.execute("SELECT * FROM Data WHERE key LIKE :k AND subkey=:s", {'k': '%'+key+'%', 's': subkey})
        else:
            result = self.execute("SELECT * FROM Data WHERE key=:k AND subkey=:s", {'k': key, 's': subkey})
        if result == DB_ERROR or len(result) == 0:
            return []
        return result
    
    def add_data(self, key, subkey, value):
        if self.execute("INSERT OR REPLACE INTO Data(key, subkey, value) VALUES(:k, :s, :v)", {'k': key, 's': subkey, 'v': value}) == DB_ERROR:
            return DB_ERROR
        return True
    
    def get_data_system(self, key, systemroot, like=False):
        systemid = self.get_systemid(systemroot)
        if systemid == DB_ERROR:
            return []
        return self.get_data(key, systemid, like)
    
    def add_data_system(self, key, systemroot, value):
        systemid = self.get_systemid(systemroot)
        if systemid == DB_ERROR:
            return DB_ERROR
        return self.add_data(key, systemid, value)

# inicialization
lib.db = {}
lib.db['analysis'] = DBAnalysis('analysis.db')
lib.db['dict'] = DBDictionary('dict.db')
lib.db['checksum'] = DBChecksum('checksum.db')
lib.db['vuln'] = DBVuln('vuln.db')

