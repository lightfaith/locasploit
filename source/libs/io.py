from source.libs.define import *
#import source.libs.define as lib
import source.libs.log as log
from source.libs.db import *

import stat

def get_fullpath(system, path):
    if system.startswith('/'): # local or sub
        if path.startswith('./') or  path.startswith('../') or path.startswith('.\\') or path.startswith('..\\'): # enable relative path also
            return path
        else:
            while path.startswith('/'):
                path = path[1:]
            return os.path.join(system, path)
    else: 
        # NOT IMPLEMENTED
        return IO_ERROR

#def read_file(system, path, dbfile=True, utf8=False):
def read_file(system, path, usedb=False):
    fullpath = get_fullpath(system, path)
    if fullpath == IO_ERROR:
        return IO_ERROR
    if not can_read(system, path):
        log.err('Cannot read \'%s\'' % (fullpath))
        return IO_ERROR
    
    if system.startswith('/'): # local or sub
        try:
            with open(fullpath, 'r', encoding='utf-8') as f:
                result = f.read()
        except: # a binary file?
            with open(fullpath, 'rb') as f:
                result = f.read()
                
        if usedb == True or usedb == DBFILE_NOCONTENT:
            fileinfo = get_file_info(system, path)
            if fileinfo == IO_ERROR:
                return IO_ERROR # cannot access file info - something is weird
            add = db['analysis'].add_file(system, path, fileinfo['type'], fileinfo['permissions'], fileinfo['UID'], fileinfo['GID'], result if usedb else None, fileinfo['ATIME'], fileinfo['MTIME'], fileinfo['CTIME'])
            if not add:
                log.err('Database query failed.')
                return IO_ERROR
        return result
    else: # SSH/FTP/TFTP/HTTP
        # NOT IMPLEMENTED
        return IO_ERROR

def write_file(system, path, content, lf=True, utf8=False):
    fullpath = get_fullpath(system, path)
    if fullpath == IO_ERROR:
        return IO_ERROR
    if not can_write(system, path) and not can_create(system, path):
        log.err('Cannot write \'%s\'' % (fullpath))
        return IO_ERROR
    
    if system.startswith('/'): # local or sub
        # LF? UTF-8?
        args = {}
        if lf:
            args['newline'] = ''
        if utf8:
            args['encoding'] = 'utf-8'
        try:
            # write file
            with open(fullpath, 'w', **args) as f:
                f.write(content)
        except UnicodeEncodeError:
            # weird char? try utf8
            args['encoding'] = 'utf-8'
            with open(fullpath, 'w', **args) as f:
                f.write(content)
        """if utf8:
            with codecs.open(fullpath, 'w', 'utf-8') as f:
                f.write(content)
        else:
            try:
                if lf: # ending = \n
                    with open(fullpath, 'w', newline='') as f:
                        f.write(content)
                else: # respect OS newline style
                    with open(fullpath, 'w') as f:
                        f.write(content)
            except UnicodeEncodeError:
                write_file(system, path, content, lf, utf8=True)
        """
        return True
    else: # SSH/FTP/TFTP/HTTP
        # NOT IMPLEMENTED
        return IO_ERROR

def get_file_info(system, path):
    fullpath = get_fullpath(system, path)
    if fullpath == IO_ERROR:
        return IO_ERROR
        
    if system.startswith('/'): # local or sub
        if can_read(system, path):
            result = {}
            # TODO platform-specific
            stats = os.stat(fullpath)
            stm = stats.st_mode
            result['type'] = get_file_type_char(stat.S_IFMT(stm))
            result['permissions'] = '%o' % (stat.S_IMODE(stm))
            result['UID'] = stat.ST_UID
            result['GID'] = stat.ST_GID
            result['ATIME'] = stat.ST_ATIME
            result['MTIME'] = stat.ST_MTIME
            result['CTIME'] = stat.ST_CTIME # actually mtime on UNIX, TODO
            return result
        else:
            log.err('Cannot get stats of \'%s\'.' % (fullpath))
            return IO_ERROR
    else: # SSH/FTP/TFTP/HTTP
        # NOT IMPLEMENTED
        return IO_ERROR

def can_read(system, path):
    fullpath = get_fullpath(system, path)
    if fullpath == IO_ERROR:
        return False
    if os.access(fullpath, os.R_OK):
            return True
    else:
        return False

def can_write(system, path):
    fullpath = get_fullpath(system, path)
    if fullpath == IO_ERROR:
        return False
    if os.access(fullpath, os.W_OK):
            return True
    else:
        return False

def can_execute(system, path):
    fullpath = get_fullpath(system, path)
    if fullpath == IO_ERROR:
        return False
    if os.access(fullpath, os.X_OK):
            return True
    else:
        return False

def can_create(system, path):
    fullpath = get_fullpath(system, path)
    if fullpath == IO_ERROR:
        return False
    # file does not exist but can be created
    if not can_write(system, path):
        try:
            with open(fullpath, 'w') as f:
                f.write('.')
            os.remove(fullpath)
            return True
        except:
            return False
    else:
        return False

def get_file_type_char(mask):
    chars = '??????????????df'
    for i in range(0, len(chars)):
        x = 2**i
        if x == mask:
            return chars[i]
    return '?'

def get_system_type_from_active_root(activeroot):
    if activeroot == '/':
        return sys.platform
    #
    # check db if the system is known
    #
    
    #
    # new system - detect it and write into db
    #
    
    # chroot or similar?
    if activeroot.startswith('/'):
        # linux should have some folders in / ...
        success = 0
        linux_folders = ['/bin', '/boot', '/dev', '/etc', '/home', 'lib', '/media', '/opt', '/proc', '/root', '/sbin', '/srv', '/sys', '/tmp', '/usr']
        for folder in linux_folders:
            if can_read(activeroot, folder):
                success += 1
        if float(success)/len(linux_folders) > 0.7: # this should be linux
            #TODO write into DB
            return linux
        
    #TODO NOT IMPLEMENTED
    return 'unknown'
