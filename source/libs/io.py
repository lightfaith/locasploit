#!/usr/bin/env python3
"""
Universal file/directory methods are defined here.
"""

import stat, hashlib
from source.libs.define import *
#import source.libs.define as lib
import source.libs.log as log
from source.libs.db import *


def get_fullpath(system, path):
    #print(system, path)
    if system.startswith('/'): # local or sub
        if path.startswith('./') or  path.startswith('../') or path.startswith('.\\') or path.startswith('..\\'): # enable relative path also
            return path
        if path.startswith('~/'): #TODO test
            print('IO returning ~ address...')
            return os.path.join(lib.global_parameters['HOME'], path[2:])

        while path.startswith('/'): # remove leading slashes
            path = path[1:]
        return os.path.join(system, path)
    elif system.startswith('ssh://'):
        return system+('/' if not system.endswith('/') else '')+path
    else: 
        # TODO NOT IMPLEMENTED
        return IO_ERROR

def get_fd(system, path, mode):
    fullpath = get_fullpath(system, path)
    if system.startswith('/'): # local or sub
        return open(fullpath, mode)
    elif system.startswith('ssh://'):
        c = get_ssh_connection(system)
        sftp = c.connectors[0].open_sftp() # will be closed on connection kill or program termination
        c.connectors.append(sftp)
        return sftp.open(path, mode)
    else:
        # TODO NOT IMPLEMENTED
        return None

def read_file(system, path, f=None, usedb=False, forcebinary=False, chunk=0, verbose=False):
    fullpath = get_fullpath(system, path)
    if fullpath == IO_ERROR:
        return IO_ERROR
    if not can_read(system, path):
        if verbose:
            if is_link(system, path):
                log.err('\'%s\' (on \'%s\') is a symlink to \'%s\' but it cannot be read.' % (path, system, get_link(system, path)))
            else:
                log.err('Cannot read \'%s\'.' % (fullpath))
        return IO_ERROR
        
    open_and_close = (f is None)
        
    if system.startswith('/'): # local or sub
        if open_and_close:
            try:
                if forcebinary:
                    raise TypeError # will be opened as binary
                f = open(fullpath, 'r', encoding='utf-8')
            except: # a binary file?
                f = open(fullpath, 'rb')
        result = f.read() if chunk == 0 else f.read(chunk)
        if open_and_close:
            f.close()
                
        if usedb == True or usedb == DBFILE_NOCONTENT:
            fileinfo = get_file_info(system, path)
            if fileinfo == IO_ERROR:
                return IO_ERROR # cannot access file info - something is weird
            add = db['analysis'].add_file(system, path, fileinfo['type'], fileinfo['permissions'], fileinfo['UID'], fileinfo['GID'], result if usedb else None, fileinfo['ATIME'], fileinfo['MTIME'], fileinfo['CTIME'])
            if not add:
                log.err('Database query failed.')
                return IO_ERROR
        return result

    elif system.startswith('ssh://'):        
        c = get_ssh_connection(system)
        if c is not None:
            if open_and_close:
                try:
                    sftp = c.connectors[0].open_sftp()
                except:
                    log.err('Cannot create SFTP connection.')
                    return IO_ERROR
                try:
                    if forcebinary:
                        raise TypeError # will be treated as binary
                    f = sftp.open(path, 'r')
                except:
                    f = sftp.open(path, 'rb')
            result = f.read() if chunk == 0 else f.read(size=chunk)
            if open_and_close:
                sftp.close()
            if forcebinary:
                return result
            else:
                return result.decode('utf-8')
        else:
            log.err('Cannot read file on \'%s\' - no such connection' % (system))
            return IO_ERROR
        # TODO usedb, chunk etc.
    else: # FTP/TFTP/HTTP
        # TODO NOT IMPLEMENTED
        return IO_ERROR

def write_file(system, path, content, lf=True, utf8=False):
    fullpath = get_fullpath(system, path)
    if fullpath == IO_ERROR:
        return IO_ERROR
    if not can_write(system, path) and not can_create(system, path):
        if is_link(system, path):
            log.err('\'%s\' (on %s) is a symlink to \'%s\' but it cannot be written.' % (path, system, get_link(system, path)))
        else:
            log.err('Cannot write \'%s\'.' % (fullpath))
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
        except TypeError:
            # str, not bytes? write as binary
            with open(fullpath, 'wb') as f:
                f.write(content)
        return True
    else: # SSH/FTP/TFTP/HTTP
        # TODO NOT IMPLEMENTED
        return IO_ERROR


def mkdir(system, path):
    fullpath = get_fullpath(system, path)
    if can_read(system, path):
        typ = get_file_info(system, path)['type']
        if typ != 'd':
            log.err('This file already exists (and is not a directory).')
        return
    
    if system.startswith('/'): # local or sub
        os.mkdir(fullpath)
    else:
        #TODO NOT IMPLEMENTED
        pass

def delete(system, path):
    typ = get_file_info(system, path)['type']
    fullpath = get_fullpath(system, path)

    if system.startswith('/'): # local or sub
        if typ == 'f':
            os.remove(fullpath)
        elif typ == 'd':
            try:
                # empty directory?
                os.rmdir(fullpath)
            except:
                # recursively?
                import shutil
                shutil.rmtree(fullpath)


def get_file_info(system, path, verbose=False):
    fullpath = get_fullpath(system, path)
    if fullpath == IO_ERROR:
        return IO_ERROR
    
    result = {}    
    if system.startswith('/'): # local or sub
        if can_read(system, path):
            # TODO platform-specific
            stats = os.stat(fullpath)
            stm = stats.st_mode
            result['type'] = get_file_type_char(stat.S_IFMT(stm))
            result['permissions'] = '%o' % (stat.S_IMODE(stm))
            result['UID'] = stats[stat.ST_UID]
            result['GID'] = stats[stat.ST_GID]
            result['ATIME'] = stats[stat.ST_ATIME]
            result['MTIME'] = stats[stat.ST_MTIME]
            result['CTIME'] = stats[stat.ST_CTIME] # actually mtime on UNIX, TODO
        else:
            if verbose:
                log.info('File \'%s\' is not accessible.' % (fullpath))
            result['type'] = None
            result['permissions'] =  None
            result['UID'] = None
            result['GID'] = None
            result['ATIME'] = None
            result['MTIME'] = None
            result['CTIME'] = None
        return result

    else: # SSH/FTP/TFTP/HTTP
        # TODO NOT IMPLEMENTED
        return IO_ERROR

def can_read(system, path):
    fullpath = get_fullpath(system, path)
    if fullpath == IO_ERROR:
        return False
    if system.startswith('/'):
        if os.access(fullpath, os.R_OK):
            return True
        else: 
            return False
    elif system.startswith('ssh://'):
        c = get_ssh_connection(system)
        if c is not None:
            try:
                sftp = c.connectors[0].open_sftp()
                fs = sftp.listdir(path)
                result = len(fs)>0
            except: # not a directory
                try:
                    f = sftp.open(path)
                    #result = f.readable()
                    # no readable() on Debian??? # TODO monitor this situation, meanwhile:
                    tmpbuf = f.read(size=1)
                    result = True if len(tmpbuf)>0 else False
                except (PermissionError, FileNotFoundError):
                    return False
                except Exception as e:
                    return False
            sftp.close()
            return result
        else:
            return False # no connection
    else: # unknown system
        return False

def can_write(system, path):
    fullpath = get_fullpath(system, path)
    if fullpath == IO_ERROR:
        return False
    if system.startswith('/'):
        if os.access(fullpath, os.W_OK):
            return True
        else:
            return False

def can_execute(system, path):
    fullpath = get_fullpath(system, path)
    if fullpath == IO_ERROR:
        return False
    if system.startswith('/'):
        if os.access(fullpath, os.X_OK):
            return True
        else:
            return False
    else:
        # TODO NOT IMPLEMENTED
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

def is_link(system, path):
    #os = get_system_type_from_active_root(system)
    if system.startswith('/'):
        return os.path.islink(get_fullpath(system, path))
    #TODO NOT IMPLEMENTED
    return False

def get_link(system, path):
    # system is not in the output!
    if is_link(system, path):
        if system.startswith('/'): # local or sub
            return os.readlink(get_fullpath(system, path))
        else:
            return path # TODO not implemented
    else:
        return path

def list_dir(system, path, sortby=IOSORT_NAME):
    result = []
    if system.startswith('/'): # local or sub
        try:
            result = os.listdir(get_fullpath(system, path))
        except:
            result = []
    elif system.startswith('ssh://'):
        c = get_ssh_connection(system)
        try:
            sftp = c.connectors[0].open_sftp()
            result = sftp.listdir(path)
        except:
            result = []
    else:
        # TODO NOT IMPLEMENTED
        return []
    
    # sort if necessary
    if sortby == IOSORT_NAME:
        return sorted(result)
    else: # by some parameter
        fileinfos = {k:get_file_info(system, os.path.join(path, k)) for k in result} # TODO not really platform-independent
        if sortby == IOSORT_MTIME:
            return [k for k,v in sorted(fileinfos.items(), key=lambda x: x[1]['MTIME'])]
        else:
            return result
        # TODO more possibilities would be great




def find(system, start, filename, location=False):
    result = []
    if system.startswith('/'): # local or sub
        for root, dirs, files in os.walk(get_fullpath(system, start)):
            if filename in files or filename in dirs:
                if location:
                    result.append(get_fullpath(system, root))
                else:
                    result.append(get_fullpath(system, os.path.join(root, filename)))
    else:
        #TODO NOT IMPLEMENTED
        result = []
    return result


def hash(system, path, function, hexdigest=True):
    # TODO universal?
    hasher = function()
    f = get_fd(system, path, 'rb')
    if f == IO_ERROR:
        result = 'UNKNOWN'
    else:
        while True:
            buf = read_file(system, path, f=f, chunk=65535)
            if len(buf) <= 0:
                break
            hasher.update(buf)
            result = hasher.hexdigest() if hexdigest else hasher.digest()
        f.close()
    return result
    
def md5(system, path, hexdigest=True):
    return hash(system, path, hashlib.md5, hexdigest)

    
def sha1(system, path, hexdigest=True):
    return hash(system, path, hashlib.sha1, hexdigest)

    
def sha256(system, path, hexdigest=True):
    return hash(system, path, hashlib.sha256, hexdigest)


def get_file_type_char(mask):
    #chars = '??????????????df'
    #for i in range(0, len(chars)):
    #    x = 2**i
    #    if x == mask:
    #        return chars[i]
    known = {
        0x6000: 'b',
        0x4000: 'd',
        0x8000: 'f',
        0x2000: 'c',
    }
    if mask in known:
        return known[mask]
    return '?'

def get_system_type_from_active_root(activeroot, verbose=False, dontprint=''):
    if activeroot == '/':
        return sys.platform
    #
    # check db if the system is known
    #

    # TODO 

    #
    # new system - detect it and write into db
    #
    
    # chroot or similar?
    if activeroot.startswith(('/', 'ssh://')): # sub or ssh
        # linux should have some folders in / ...
        success = 0
        linux_folders = ['/bin', '/boot', '/dev', '/etc', '/home', '/lib', '/media', '/opt', '/proc', '/root', '/sbin', '/srv', '/sys', '/tmp', '/usr']
        for folder in linux_folders:
            if can_read(activeroot, folder):
                success += 1
        linux_score = success/len(linux_folders)
        
        if verbose:
            if type(dontprint) != str or dontprint=='':
                log.info('Linux score for \'%s\': %f' % (activeroot, linux_score))
            else:
                log.info('Linux score for \'%s\': %f' % (activeroot.partition(dontprint)[2], linux_score))
        if linux_score > 0.3: # this should be linux
            #TODO write into DB
            return 'linux'
        
    #TODO NOT IMPLEMENTED
    return 'unknown'

def get_ssh_connection(system):
    # returns first connection for desired system
    cs = [x for x in lib.connections if x.description == system]
    if len(cs)>0:
        return cs[0]
    return None
    
