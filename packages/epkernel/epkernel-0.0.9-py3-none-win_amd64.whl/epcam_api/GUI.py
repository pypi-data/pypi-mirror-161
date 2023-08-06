import os, sys, json
import ctypes
from epcam_api import epcam

def view_cmd(job,step,layer):
    data2 = {"cmd":"show_layer", "job":job, "step": step, "layer": layer}
    js = json.dumps(data2)
    epcam.view_cmd(js)

def showlayer(job, step, layer):
    data = {
        'cmd':'show_layer',
        'job':job,
        'step':step,
        'layer':layer
        }
    js = json.dumps(data)
    # print(js)
    return epcam.view_cmd(js)
