'''Various useful utilities for the pipeline.'''

import sys
import errno
import os
import os.path

def mk_dir(dir):
    if not os.path.exists(dir):
        try:
            os.mkdir(dir, 0777)
        except IOError, e:
            sys.exit('%s\nFailed to make directory %s' % (e, dir))

def mk_link(source, target):
    try:
        os.symlink(source, target)
    except OSError, e:
        if e.errno != errno.EEXIST:
            sys.exit('%s\nFailed to create symlink %s from %s' %
                     (e, target, source))
            # or just raise?

def mk_force_link(source, target):
    """Create a symlink, overwriting any existing symlink."""
    if os.path.isfile(target):
        os.remove(target)
    os.symlink(source, target)

def split_path(path):
    '''split a file path into its prefix, filename, and filename suffix'''
    (prefix, base) = os.path.split(path)
    (name, ext) = os.path.splitext(base)
    return (prefix, name, ext)

def drop_py_suffix(filename):
    '''drop the .py suffix from a filename,
    otherwise return the name unchanged.'''
    prefix, suffix = os.path.splitext(filename)
    if suffix == '.py':
        return prefix
    else:
        return filename

def zeroFile(file):
    '''truncate a file to zero bytes, and preserve its original
    modification time'''
    if os.path.exists(file):
        # save the current time of the file
        timeInfo = os.stat(file)
        try:
            f = open(file, 'w')
        except IOError:
            pass
        else:
            f.truncate(0)
            f.close()
            # change the time of the file back to what it was
            os.utime(file, (timeInfo.st_atime, timeInfo.st_mtime))
