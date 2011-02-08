from __future__ import division
"""
Functions that belong in any other module

Created on 15/10/2010

@author: peter
"""
import os, pickle

def quote(s):
    return '<<' + s + '>>'

def checkExists(file_path):
    if not os.path.exists(file_path):
        print file_path, 'does not exist'
        exit()
        
def rm(file_path):
    try:
        os.remove(file_path)
    except:
        pass

def mkDir(dir):
    try:
        os.mkdir(dir)
    except:
        pass

def detectNumberCpus():
    """
    Detects the number of CPUs on a system.
    
    From  http://codeliberates.blogspot.com/2008/05/detecting-cpuscores-in-python.html
    """
    # Linux, Unix and MacOS:
    if hasattr(os, 'sysconf'):
        if os.sysconf_names.has_key('SC_NPROCESSORS_ONLN'):
            # Linux & Unix:
            ncpus = os.sysconf('SC_NPROCESSORS_ONLN')
            if isinstance(ncpus, int) and ncpus > 0:
                return ncpus
        else: # OSX:
            return int(os.popen2('sysctl -n hw.ncpu')[1].read())
 
    # Windows:
    if os.environ.has_key('NUMBER_OF_PROCESSORS'):
        ncpus = int(os.environ['NUMBER_OF_PROCESSORS']);
        if ncpus > 0:
            return ncpus
        
    return 1 # Default

def removeDuplicates(a_list):
    """ Remove duplicates from a list """
    if not a_list:
        return None
    out = [a_list[0]]
    for a in a_list[1:]:
        if not a in out:
            out.append(a)
    return out

def transpose(arr2d):
    """ Transpose a 2d array """
    width = len(arr2d[0])
    for row in arr2d[1:]:
        assert(len(row) == width)
    columns = [[] for i in range(width)]
    for row in arr2d:
        for i in range(width):
            columns[i].append(row[i])
    return columns

def padRight(arr, width, pad_val):
    out = arr[:]
    while len(out) < width:
        out.append(pad_val)
    return out

def get_short_name(filename):
    """ Return name with directory and extension removed """
    return os.path.splitext(os.path.basename(filename))[0]

def get_full_path(dir, short_name, modifier, ext):
    """ Return a full path of dir/short_name[.modifier][.ext] """
    #print 'get_full_path:', dir, short_name, modifier, ext
    path = os.path.join(dir, short_name)
    path.rstrip('.')
    if modifier:
        path += '.' + modifier.strip('.')
    if ext:
        path += '.' + ext.strip('.')
    return path

def _get_pickled_base(filename):
    f = open(filename, 'rb')
    val = pickle.load(f)
    f.close()
    return val

def set_pickled(filename, val):
    f = open(filename, 'wb')
    val = pickle.dump(val,f)
    f.close()

def get_pickled(filename, default = None):
    try:
        val = _get_pickled_base(filename)
    except:
        if default is not None:
            set_pickled(filename, default)
        val = _get_pickled_base(filename)
    return val

if __name__ == '__main__':
    pass

