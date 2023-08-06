#from ctypes import *
import ctypes
import sys
import os
import threading

bin_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bin')

# ld_path = os.getenv('LD_LIBRARY_PATH')

#print(epbin_path +  r"\EPCAM_CTYPE.dll")
#dll = ctypes.cdll.LoadLibrary(pp)

#epbin_path = os.getcwd() + r'py\bin"
os.environ['path'] += (r";" + bin_path)

dll = ctypes.CDLL(bin_path + r"\EPCAM_CTYPE.dll")
dmsdll = ctypes.CDLL(bin_path + r"\DMS_CTYPE.dll")
vdll = ctypes.CDLL(bin_path + r"\Form_View.dll")


dll.process.restype =  ctypes.c_char_p
dll.init_func_map.restype =  ctypes.c_char_p
dll.init_orig_func_map.restype =  ctypes.c_char_p
dll.process.argtypes = [ctypes.c_char_p]
vdll.init.argtypes = [ctypes.c_char_p]
vdll.view_cmd.argtypes = [ctypes.c_char_p]
dmsdll.init.restype = ctypes.c_char_p
dmsdll.uploadmongo.restype = ctypes.c_char_p
dmsdll.getParam.restype = ctypes.c_char_p
dmsdll.downloadjob.restype = ctypes.c_char_p

dmsdll.downloadorigin.restype = ctypes.c_char_p
dmsdll.downloadpre.restype = ctypes.c_char_p
#cdef extern from"stdio.h":
#    extern int printf(const char* format, ...)
dmsdll.upload_robot2mongo.restype = ctypes.c_char_p

dmsdll.getOrderInfoByJobName.restype = ctypes.c_char_p
dmsdll.set_robot_status.restype = ctypes.c_int
dmsdll.epdms_order_status_update.restype = ctypes.c_char_p
dmsdll.epdms_flow_status_update.restype = ctypes.c_char_p
dmsdll.get_mongo_fsname.restype = ctypes.c_char_p

def SayHello():
    print("hello, world!\n")

def init():
    ret = dll.init_func_map()
    ret = dll.init_orig_func_map()
    vstring_path = bytes(bin_path, encoding='utf-8')
    vdll.init(vstring_path)
    return ret.decode('utf-8')

def set_use_times(times):
    times.encode('utf-8')
    #print(type(json))
    times_str = bytes(times, encoding='utf-8')
    dll.setUseTimes(times_str)

def process(json):
    json.encode('utf-8')
    #print(type(json))
    string_buff = bytes(json, encoding='utf-8')
    #print(type(string_buff), string_buff)
    ret = dll.process(string_buff)
    #print(ret)
    return ret.decode('utf-8')


def view_cmd(vjson):
    string_vjson = bytes(vjson, encoding='utf-8')
    vdll.view_cmd(string_vjson)
