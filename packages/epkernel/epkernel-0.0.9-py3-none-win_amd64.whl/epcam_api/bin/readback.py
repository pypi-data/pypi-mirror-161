import sqlite3 as db
import os,sys,time,json
import shutil
import re
import json
current_path = os.path.dirname(os.path.realpath(__file__))
loaddll_path=current_path+r"\CAMGuide\base\epcam"
sys.path.append(loaddll_path)

import epcam
import epcam_api

def load_layer(jobname, stepname, layername):
    try:
        epcam_api.load_layer(jobname, stepname, layername)
    except Exception as e:
        print(e)
    return 0 

#获取step列表
def get_all_steps(job):
    try:
        ret = epcam_api.get_matrix(job)
        data = json.loads(ret)
        steps = data['paras']['steps']
        return steps
    except Exception as e:
        print(e)
    return []

#获取layer列表
def get_all_layers(job):
    try:
        ret = epcam_api.get_matrix(job)
        data = json.loads(ret)
        layer_infos = data['paras']['info']
        layer_list = []
        for i in range(0, len(layer_infos)):
            layer_list.append(layer_infos[i]['name'])
        return layer_list
    except Exception as e:
        print(e)
    return []




def main(odbpath,dbpath):
    ofn=os.path.dirname(odbpath) 
    fname = os.path.basename(odbpath)
    temp=os.path.join(ofn,str(int(time.time())))
    shutil.copytree(odbpath,temp)
    epcam.init()
    job=os.path.basename(odbpath)
    path=os.path.dirname(odbpath)   
    epcam_api.open_job(path,job)
    step_list = []
    layer_list = []
    step_list = get_all_steps(job)
    layer_list = get_all_layers(job)
    if len(step_list) and len(layer_list):
        for i in range(len(step_list)):
            for j in range(len(layer_list)):
                load_layer(job, step_list[i], layer_list[j])


    con=db.connect(dbpath)
    cur=con.cursor()
    cur.execute('select * from funlog')
    all_records=[]
    row=cur.fetchall()
    i=0
    for r in row:
        all_records.append(r[4])
    for data in all_records:
        size=len(data)
        if size<8:
            continue
        func=data[6:10]
        if func!='func':
            continue
        ret = epcam.process(data)
    epcam_api.save_job(job)
    epcam_api.close_job(job)
    outpath=os.path.join(os.path.dirname(os.path.realpath(__file__)),'job')  
    jobname=fname+'_readback'
    os.rename(odbpath,ofn+r'/'+jobname)
    shutil.move(ofn+r'/'+jobname,outpath+r'/'+jobname)
    os.rename(temp,odbpath)
   

def read_text(odbpath,jsonpath):
    epcam.init()
    job=os.path.basename(odbpath)
    path=os.path.dirname(odbpath)   
    epcam_api.open_job(path,job)
    step_list = []
    layer_list = []
    step_list = get_all_steps(job)
    layer_list = get_all_layers(job)
    if len(step_list) and len(layer_list):
        for i in range(len(step_list)):
            for j in range(len(layer_list)):
                load_layer(job, step_list[i], layer_list[j])
    else :
        print('no step or layer in this job')
        return
 
    with open(jsonpath, 'r', encoding='utf8')as fp:
        json_data = fp.readlines()
        for data in json_data:
            if data !='\n':
                size=len(data)
                if size<8:
                    continue
                func=data[2:6]
                if func!='func':
                    continue
                ret = epcam.process(data)
    epcam_api.save_job(job)

    outpath=os.path.join(os.path.dirname(os.path.realpath(__file__)),'job')
    fname = os.path.basename(odbpath)  
    ofn=os.path.dirname(odbpath) 
    jobname=fname+'_readback'
    os.rename(odbpath,ofn+r'/'+jobname)
    shutil.move(ofn+r'/'+jobname,outpath+r'/'+jobname)
  


  
 

if __name__ == '__main__':
    odbpath=r'C:\project\trunk\EPCAM\EP-CAM-Engineering\backup\2021.12.22-15.16.48\bbb'
    dbpath=r'C:\project\trunk\EPCAM\EP-CAM-Engineering\db\2021.12.22-15.16.48\testcam.db'
   # main(odbpath,dbpath)
    jsonpath=r'C:\Users\wei.zhu\Desktop\ipc_record\api.json'
    main(odbpath,dbpath)