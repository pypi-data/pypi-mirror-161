import os
import time
import hashlib
import shutil
import pickle
import base64
from multiprocessing import Process, JoinableQueue
import subprocess
from collections import Counter
import configparser
config = configparser.ConfigParser()

def write2path(lines,path='',encoding='utf-8',method='lines',append='w',wrap=False):
    if not path: path=getTime()+'.txt'
    lines = [str(f) for f in lines]
    with open(path,append,encoding=encoding) as fw:
        if method=='lines':
            if wrap: lines = [f+'\n' for f in lines]
            fw.writelines(lines)
        else:
            fw.write(lines)

def append2path(line,path,encoding='utf-8',method='line',append='a'):
    with open(path,append,encoding=encoding) as fw:
        if method=='line':
            fw.write(line+'\n')
        else:
            fw.writelines(line)

def read_path(path,method='lines',encoding='utf-8',errors='strict',strip=False):
    with open(path,'r',encoding=encoding,errors=errors) as fr:
        if method == "lines":
            all_lines = fr.readlines()
            if strip:
                all_lines = [l.strip() for l in all_lines]
        else:
            all_lines = fr.read()
        return all_lines

def print_list(array,index=False):
    if index:
        for i,val in enumerate(array):
            print(i,val)
    else:
        for val in array:
            print(val)
    print(f"length:{len(array)}")

def get_top_n_files(folder_path,n):
    if not os.path.exists(folder_path):
        return []
    if folder_path[-1] != '/':
        folder_path=folder_path+'/'
    top_n_files = [folder_path+f for f in os.listdir(folder_path)[:n]]
    return top_n_files

def copy_top_n_file(folder_path,n,dst_folder):
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
    top_n_files = get_top_n_files(folder_path,n)
    for f in top_n_files:
        copyfile(f,dst_folder)

def save2pkl(obj,path,protocol=-1):
    with open(path,'wb') as fw:
        pickle.dump(obj,fw,protocol=protocol)

def read_pkl(path):
    with open(path, 'rb') as fr:
        obj = pickle.load(fr)
        return obj

def getTime(timestamp=''):
    if timestamp:
        return time.strftime("%y-%m-%d %H:%M:%S", time.localtime(timestamp))
    else:
        return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

def getTimestamp():
    return time.time()

def getTimeSpan(begin_time, end_time, format='minute'):
    begin_time = time.strptime(begin_time, "%y-%m-%d %H:%M:%S")
    end_time = time.strptime(end_time, "%y-%m-%d %H:%M:%S")

    begin_timeStamp = int(time.mktime(begin_time))
    end_timeStamp = int(time.mktime(end_time))
    span_seconds = abs(end_timeStamp - begin_timeStamp)

    if format == 'second':
        return int(round(span_seconds, 2))
    elif format == 'minute':
        return int(round(span_seconds / 60, 2))
    elif format == 'hour':
        return int(round(span_seconds / 3600, 2))
    elif format == 'day':
        return int(round(span_seconds / 86400, 2))
    else:
        return int(round(span_seconds, 2))

def get_file_md5(file_path):
    md5 = None
    if os.path.isfile(file_path):
        f = open(file_path, 'rb')
        md5_obj = hashlib.md5()
        md5_obj.update(f.read())
        hash_code = md5_obj.hexdigest()
        f.close()
        md5 = str(hash_code).lower()
    return md5

def get_str_md5(parmStr):
    if isinstance(parmStr, str):
        parmStr = parmStr.encode("utf-8")
    m = hashlib.md5()
    m.update(parmStr)
    return m.hexdigest()

def getfilesize(filePath):
    fsize = os.path.getsize(filePath)
    fsize = fsize / (1000 * 1000)
    return round(fsize, 2)

def listDir(rootDir,only_file=False,only_folder=False):
    list_filepath = []
    for filename in os.listdir(rootDir):
        pathname = os.path.join(rootDir, filename)
        if filename == '.DS_Store':
            continue
        if only_file:
            if os.path.isfile(pathname):
                list_filepath.append(pathname)
            continue
        if only_folder:
            if os.path.isdir(pathname):
                list_filepath.append(pathname)
            continue
        list_filepath.append(pathname)
    return list_filepath

def makedir(dir_path,delete_exists=False):
    if os.path.exists(dir_path):
        if delete_exists:
            rmfolder(dir_path)
            os.makedirs(dir_path)
        else:
            print("--------创建文件夹失败:" + dir_path + ",路径已存在--------")
    else:
        os.makedirs(dir_path)

def touchfile(path):
    if not os.path.exists(path):
        f = open(path,'w')
        f.close()

def counter(lst):
    return Counter(lst)

def copyfile(origin_path, target_path):
    if os.path.isfile(origin_path):
        shutil.copy(origin_path, target_path)
    else:
        print("--------复制文件失败:" + origin_path + ",路径不存在--------")

def movefile(origin_path, target_path):
    if os.path.isfile(origin_path):
        shutil.move(origin_path, target_path)
    else:
        print("--------移动文件失败:" + origin_path + ",路径不存在--------")

def copyfolder(origin_folder, target_folder, *args):
    # 目标文件夹名为 target_path，不能已经存在；方法会自动创建目标文件夹。
    if os.path.isdir(origin_folder):
        shutil.copytree(origin_folder, target_folder, ignore=shutil.ignore_patterns(*args))
    else:
        print("--------复制文件夹失败:" + origin_folder + ",路径不存在--------")

def rmfile(del_file):
    if os.path.isfile(del_file):
        os.remove(del_file)
    else:
        print("--------删除文件失败:" + del_file + ",路径不存在--------")

def rmfolder(del_folder):
    if os.path.isdir(del_folder):
        shutil.rmtree(del_folder)
    else:
        print("--------删除文件夹失败:" + del_folder + ",路径不存在--------")

def base64decode(strings,encoding='utf-8'):
    try:
        base64_decrypt = base64.b64decode(strings.encode('utf-8'))
        return str(base64_decrypt, encoding)
    except:
        return ''

def base64encode(strings,encoding='utf-8'):
    try:
        base64_encrypt = base64.b64encode(strings.encode('utf-8'))
        return str(base64_encrypt, encoding)
    except:
        return ''

def run_cmd(cmd,with_output=False):
    if with_output:
        return subprocess.getstatusoutput(cmd)
    else:
        return subprocess.call(cmd, shell=True)

def func_time(func):
    begin_time= time.time()
    func()
    end_time= time.time()
    print(f'{func.__name__} 耗时:{int(end_time-begin_time)}')

def run_multi_task(all_items,user_func,done_path='',cpu_num=os.cpu_count(),print_log=False):
    begin_time = time.time()
    if done_path:
        touchfile(done_path)
        done_items = [f.strip() for f in read_path(done_path)]
    else:
        done_items = []
    undone_items = list(set(all_items) - set(done_items))
    print(f'检测到全部:{len(all_items)}个')
    print(f'检测到已完成的:{len(done_items)}个')
    print(f'重新计算需要处理的个数为:{len(undone_items)}个')
    print(f'启动{cpu_num}个进程,开始运行')

    q = JoinableQueue()
    for item in undone_items:
        q.put(item)

    def func_task(q):
        while True:
            item = q.get()
            user_func(item)
            if done_path:
                append2path(f'{item}',done_path)

            q.task_done()
            if print_log:
                print(f'当前:{item}')

    for i in range(cpu_num):
        p = Process(target=func_task, args=(q,))
        p.daemon = True
        p.start()
    q.join()
    print(f'全部已完成，用时:{float(time.time() - begin_time)}')

def read_config(config_path,config_name,section='default',type='str'):
    config = configparser.ConfigParser()
    config.read(config_path)
    if section in config.sections():
        if config_name in config.options(section):
            if type=='str':
                return config.get(section, config_name)
            elif type=='float':
                return config.getfloat(section, config_name)
            elif type=='int':
                return config.getint(section, config_name)
            elif type=='bool':
                return config.getboolean(section, config_name)
    return ''

def write_config(config_path,config_name,config_value,section='default'):
    config = configparser.ConfigParser()
    config.read(config_path)
    if not config.has_section(section): config.add_section(section)
    config.set(section, config_name, config_value)

    with open(config_path, 'w') as configfile:
        config.write(configfile)
