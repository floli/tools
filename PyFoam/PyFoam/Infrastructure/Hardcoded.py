#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Infrastructure/Hardcoded.py 6471 2010-04-16T19:46:47.669328Z bgschaid  $ 
"""Hardcoded values"""

from os import path,makedirs,environ

_pyFoamDirName="pyFoam"

_pyFoamConfigName="pyfoamrc"

def globalDirectory():
    """@return: the global directory"""
    return path.join("/etc",_pyFoamDirName)

def globalConfigFile():
    """@return: The name of the global configuration File"""
    return path.join(globalDirectory(),_pyFoamConfigName)

def globalConfigDir():
    """@return: The name of the global configuration directory where .cfg-files can be placed"""
    return globalConfigFile()+".d"

def userDirectory():
    """@return: the user directory"""
    return path.expanduser(path.join("~","."+_pyFoamDirName))

def userConfigFile():
    """@return: The name of the user configuration File"""
    return path.join(userDirectory(),_pyFoamConfigName)

def userConfigDir():
    """@return: The name of the user configuration directory where .cfg-files can be placed"""
    return userConfigFile()+".d"

def userName():
    """@return: name of the current user"""
    user=""
    if environ.has_key("USER"):
        user=environ["USER"]
    return user

def logDirectory():
    """Path to the log directory that this user may write to.
    /var/log/pyFoam for root, ~/.pyFoam/log for all others 
    @return: path to the log directory."""
    if userName()=="root":
        return path.join("/var/log","pyFoam")
    else:
        return path.join(userDirectory(),"log")
    
def assertDirectory(name):
    """Makes sure that the directory exists
    @param name: the directory"""
    if path.exists(name):
        return
    else:
        makedirs(name,mode=0755)
