# This file was created automatically by SWIG.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.

import _PCSCHandle

def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "this"):
        if isinstance(value, class_type):
            self.__dict__[name] = value.this
            if hasattr(value,"thisown"): self.__dict__["thisown"] = value.thisown
            del value.thisown
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static) or hasattr(self,name) or (name == "thisown"):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types


DEBUG_PCSC = _PCSCHandle.DEBUG_PCSC
PCSC_INITIALISED = _PCSCHandle.PCSC_INITIALISED
PCSC_OK = _PCSCHandle.PCSC_OK
PCSC_ERROR = _PCSCHandle.PCSC_ERROR
class PCSCHandle(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, PCSCHandle, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, PCSCHandle, name)
    def __repr__(self):
        return "<%s.%s; proxy of C++ PCSCHandle instance at %s>" % (self.__class__.__module__, self.__class__.__name__, self.this,)
    def __init__(self, *args):
        _swig_setattr(self, PCSCHandle, 'this', _PCSCHandle.new_PCSCHandle(*args))
        _swig_setattr(self, PCSCHandle, 'thisown', 1)
    def __del__(self, destroy=_PCSCHandle.delete_PCSCHandle):
        try:
            if self.thisown: destroy(self)
        except: pass

    def getReaderName(*args): return _PCSCHandle.PCSCHandle_getReaderName(*args)
    def listAllReaders(*args): return _PCSCHandle.PCSCHandle_listAllReaders(*args)
    def openSession(*args): return _PCSCHandle.PCSCHandle_openSession(*args)
    def closeSession(*args): return _PCSCHandle.PCSCHandle_closeSession(*args)
    def getATR(*args): return _PCSCHandle.PCSCHandle_getATR(*args)
    def getAttribute(*args): return _PCSCHandle.PCSCHandle_getAttribute(*args)
    def sendAPDU(*args): return _PCSCHandle.PCSCHandle_sendAPDU(*args)
    __swig_setmethods__["numberReaders"] = _PCSCHandle.PCSCHandle_numberReaders_set
    __swig_getmethods__["numberReaders"] = _PCSCHandle.PCSCHandle_numberReaders_get
    if _newclass:numberReaders = property(_PCSCHandle.PCSCHandle_numberReaders_get, _PCSCHandle.PCSCHandle_numberReaders_set)
    __swig_setmethods__["status"] = _PCSCHandle.PCSCHandle_status_set
    __swig_getmethods__["status"] = _PCSCHandle.PCSCHandle_status_get
    if _newclass:status = property(_PCSCHandle.PCSCHandle_status_get, _PCSCHandle.PCSCHandle_status_set)

class PCSCHandlePtr(PCSCHandle):
    def __init__(self, this):
        _swig_setattr(self, PCSCHandle, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, PCSCHandle, 'thisown', 0)
        _swig_setattr(self, PCSCHandle,self.__class__,PCSCHandle)
_PCSCHandle.PCSCHandle_swigregister(PCSCHandlePtr)


printDebug = _PCSCHandle.printDebug

