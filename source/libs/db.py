#from source.libs.include import *
#from source.libs.define import *
import time
import source.libs.define as lib
import source.libs.log as log

import sqlite3 as sqlite

DB_ERROR = lib.DB_ERROR

class DB():
    def __init__(self, file):
        self.connection = sqlite.connect(file)
        self.cursor = self.connection.cursor()
    
    def close(self):
        self.commit()
        self.connection.close()
    
    def execute(self, command, parameters=None, commit=True):
        try:
            if parameters is None:
                self.cursor.execute(command)
            else:
                self.cursor.execute(command, parameters)
            if commit:
                self.commit()
            return self.cursor.fetchall()
        except Exception as e:
            log.err(str(e) + ' -- ' + command)
            return DB_ERROR
    
    def executemany(self, command, parameters):
        try:
            self.connection.executemany(command, parameters)
            self.commit()
            return True
        except Exception as e:
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
        print("SQLite version: %s" % data)
    
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
    
    def add_words(self, words, dict, checksum=None):
        d = self.add_dictionary(dict, checksum)
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
    
    def get_dictionary(self, dict):
        select =  self.execute("SELECT word from Word WHERE wordid IN ( \
                                    SELECT fk_word FROM DWord WHERE fk_dictionary = ( \
                                        SELECT dictionaryid from Dictionary WHERE name = :d)) \
                                ORDER BY word", {'d' : dict})
        if select == DB_ERROR:
            return DB_ERROR
        return [t[0] for t in select]
    
    def dump_words(self):
        select = self.execute("SELECT word FROM Word ORDER BY word")
        if select == DB_ERROR:
            return DB_ERROR
        return [t[0] for t in select]
    
    def delete_dictionary(self, dict):
        self.execute("DELETE FROM DWord WHERE fk_dictionary IN (SELECT dictionaryid FROM Dictionary WHERE name = :d)", {'d': dict})
        self.execute("DELETE FROM Dictionary WHERE name = :d", {'d': dict})
        self.clean()
    
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
    
    def get_match_percent(self, dict, tags):
        result = self.execute("SELECT t1.tag, COUNT(t1.word), (SELECT COUNT(t2.word) FROM Temporary t2 WHERE t2.tag = t1.tag) \
                    FROM Temporary t1 WHERE t1.word IN (SELECT w.word FROM Word w JOIN DWord dw ON w.wordid = dw.fk_word \
                    WHERE dw.fk_dictionary IN (SELECT dictionaryid FROM Dictionary WHERE name = :d)) GROUP BY tag", {'d': dict})
        if result == DB_ERROR:
            return DB_ERROR
        return [(t[0], dict, t[1]/t[2]) for t in result]
        

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
    
    def add_tmp_checksum(self, tag, md5=None, sha1=None):
        select = self.execute("SELECT * FROM Temporary WHERE tag = :t AND md5 = :m AND sha1=:s", {'t': tag, 'm': md5, 's': sha1})
        if select == DB_ERROR:
            return DB_ERROR
        if len(select) == 0:
            result = self.execute("INSERT OR REPLACE INTO Temporary(tag, md5, sha1) VALUES(:t, :m, :s)", {'t': tag, 'm': md5, 's': sha1})
            if result == DB_ERROR:
                return DB_ERROR
        return True

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
        result = self.get_column(self.execute("SELECT MAX(sessionid) FROM session"), 0)[0]
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
    def add_note(self, text, type, unique=False):
        if self.create_session(lib.active_session) == DB_ERROR:
            return DB_ERROR
        if unique:
            select = self.execute("SELECT * FROM Note WHERE fk_sessionid = :sid AND type = :type AND text=:t", {'sid': lib.active_session, 'type': type, 't': text})
            if select ==  DB_ERROR:
                return DB_ERROR
            if len(select) > 0:
                return True # already there
        result = self.execute("INSERT INTO Note(text, type, fk_sessionid, timestamp) VALUES(:text, :type, :sid, :ts)", {'text': text, 'type': type, 'sid': lib.active_session, 'ts': time.time()})
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
                result = self.add_property(root, 'platform', platform)
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
    def add_file(self, root, path, type, permissions, uid, gid, content, atime, mtime, ctime, md5=None, sha1=None):
        if self.create_system(root) == DB_ERROR:
            return DB_ERROR
        systemid = self.get_systemid(root)
        if systemid == DB_ERROR:
            return DB_ERROR
        """select = self.execute("SELECT * FROM File WHERE fk_systemid = :sid AND path=:p", {'sid': systemid, 'p': path})
        if select ==  DB_ERROR:
            return DB_ERROR
        if len(select) == 0:
            result = self.execute(
            "INSERT INTO File(path, fk_systemid, type, permissions, uid, gid, content, atime, mtime, ctime, timestamp) VALUES(:p, :sid, :t, :perm, :u, :g, :c, :at, :mt, :ct, :ts)", 
            {'p': path, 'sid': systemid, 't': type, 'perm': permissions, 'u': uid, 'g': gid, 'c': content, 'at': atime, 'mt': mtime, 'ct': ctime, 'ts': time.time()})
        else:
            result = self.execute(
            "UPDATE File SET type = :t, permissions = :perm, uid = :u, gid = :g, content = :c, atime = :at, mtime = :mt, ctime = :ct, timestamp = :ts WHERE fk_systemid = :sid AND path=:p",
           {'p': path, 'sid': systemid, 't': type, 'perm': permissions, 'u': uid, 'g': gid, 'c': content, 'at': atime, 'mt': mtime, 'ct': ctime, 'ts': time.time()})
        """
        md5 = None
        sha1 = None
        if content is not None:
            import hashlib
            if md5 is None:
                md5 = hashlib.md5(content.encode('utf-8')).hexdigest()
            if sha1 is None:
                sha1 = hashlib.sha1(content.encode('utf-8')).hexdigest()
        print(md5, sha1)
        result = self.execute(
            "INSERT OR REPLACE INTO File(path, fk_systemid, type, permissions, uid, gid, content, atime, mtime, ctime, timestamp, md5, sha1) VALUES(:p, :sid, :t, :perm, :u, :g, :c, :at, :mt, :ct, :ts, :m, :s)", 
            {'p': path, 'sid': systemid, 't': type, 'perm': permissions, 'u': uid, 'g': gid, 'c': content, 'at': atime, 'mt': mtime, 'ct': ctime, 'ts': time.time(), 'm': md5, 's':sha1})
        if result == DB_ERROR:
            return DB_ERROR
        
        return True
    
    # PROPERTY
    
    def add_property(self, systemroot, type, value, uniquetype=False):
        if self.create_system(systemroot) == DB_ERROR:
            return DB_ERROR
        systemid = self.get_systemid(systemroot)
        if systemid == DB_ERROR:
            return DB_ERROR
        if uniquetype: 
            select = self.execute("SELECT * FROM Property WHERE fk_systemid = :sid AND type = :t", {'sid': systemid, 't': type})
        else:
            select = self.execute("SELECT * FROM Property WHERE fk_systemid = :sid AND type = :t and value = :v", {'sid': systemid, 't': type, 'v': value})
        if select ==  DB_ERROR:
            return DB_ERROR
        if len(select) == 0:
            result = self.execute("INSERT INTO Property(fk_systemid, type, value) VALUES (:sid, :t, :v)", {'sid': systemid, 't': type, 'v': value})
            if result == DB_ERROR:
                return DB_ERROR
        return True
        
    
    # USER
    def add_users(self, systemroot, users, type):
        if self.create_system(systemroot) == DB_ERROR:
            return DB_ERROR
        systemid = self.get_systemid(systemroot)
        if systemid == DB_ERROR:
            return DB_ERROR
        
        # what is the structure?
        targs = None
        if type == lib.USERS_UNIX:
            targs = [(systemid, u[0], u[2], u[5], u[6], 1 if u[2] == 0 else 0) for u in users]
        elif type == lib.USERS_UNIXLIKE:
            targs = [(systemid, u[0], u[2], u[5], u[6], u[7]) for u in users]
        
        if targs is None:
            return DB_ERROR
        result = self.executemany("INSERT OR REPLACE INTO User (fk_systemid,  name, uid, home, shell, privileged) VALUES(?, ?, ?, ?, ?, ?)", targs)
        
        if result == DB_ERROR:
            return DB_ERROR
        return True
        
    
    def add_group(self, systemroot, gid, name, comment=None):
        # NOT IMPLEMENTED
        pass
    
    
# inicialization
lib.db = {}
lib.db['analysis'] = DBAnalysis('analysis.db')
lib.db['dict'] = DBDictionary('dict.db')
lib.db['checksum'] = DBChecksum('checksum.db')
