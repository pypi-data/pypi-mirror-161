import os,sys
import tarfile as tf
import zipfile as zf
import time
import shutil
import re

def untgz(ifn, untgz_path,jobname):
    try:
        ifn = ifn.split(sep = '"')[1]
    except:
        pass
    ofn = untgz_path
    #with tf.open(ifn, 'r:gz') as tar:
    tar = tf.open(ifn)
    fname=tar.getnames()[0]
    dirlist=os.listdir(untgz_path)
    ddd=str(int(time.time()))
    if fname in dirlist:
        os.mkdir(os.path.join(ofn,ddd))
        ofn=os.path.join(ofn,ddd)
    for tarinfo in tar:
        tarinfo.name=re.sub(r'[:]','_',tarinfo.name)
        if os.path.exists(os.path.join(ofn, tarinfo.name)):
            for root, dirs, files in os.walk(os.path.join(ofn, tarinfo.name), topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
        tar.extract(tarinfo.name, ofn)
    os.rename(ofn+r'/'+fname,ofn+r'/'+jobname)
    if fname in dirlist:
        shutil.move(ofn+r'/'+jobname,untgz_path+r'/'+jobname)
        shutil.rmtree(ofn)
    print('uncompress success!')
    return os.path.dirname(tarinfo.name)
    #os.system('pause')
    return 

#解压tgz文件到指定目录
def untgz1(ifn, untgz_path):
    try:
        ifn = ifn.split(sep = '"')[1]
    except:
        pass
    ofn = untgz_path
    #with tf.open(ifn, 'r:gz') as tar:
    tar = tf.open(ifn)
    for tarinfo in tar:
        if os.path.exists(os.path.join(ofn, tarinfo.name)):
            for root, dirs, files in os.walk(os.path.join(ofn, tarinfo.name), topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
        tar.extract(tarinfo.name, ofn)
    print('uncompress success!')
    return os.path.dirname(tarinfo.name)
    #os.system('pause')
    return 

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('usage: {} json_path'.format(sys.argv[0]))
        sys.exit(1)
    # a= r'C:\job\output\666_ep.tgz'
    # b= r'C:\job\output'
    # c='cadad'
    src_path = sys.argv[1]
    dst_path = sys.argv[2]
    jobname=sys.argv[3]
    untgz(src_path, dst_path,jobname)
    #untgz(a, b,c)


