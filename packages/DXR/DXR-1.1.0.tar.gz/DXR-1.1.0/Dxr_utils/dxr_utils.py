import yaml

from . import gvalues
import os
import platform

ConfigFiles = []
KEY_ARR_TMP = dict()


def setModuleName(name):
    gvalues.module_name = name


def initConfig():
    global ConfigFiles
    if platform.system() == 'Windows':
        ConfigPath = 'D:\\Config'
    else:
        ConfigPath = os.path.expanduser('~') + '/Config'
    ConfigFiles = GetFileFromThisRootDir(ConfigPath, ['yaml'])
    print(ConfigFiles)
    gvalues.ConfigList = dict()
    for file in ConfigFiles:
        f = open(file['path'])
        gvalues.ConfigList[file['moduleName']] = yaml.load(f, Loader=yaml.FullLoader)
    print(gvalues.ConfigList)


# 获取指定路径下所有指定后缀的文件
# dir 指定路径
# ext 指定后缀，链表&不需要带点 或者不指定。例子：['xml', 'java']
def GetFileFromThisRootDir(dir, ext=None):
    allfiles = []
    needExtFilter = (ext is not None)
    for root, dirs, files in os.walk(dir):
        for filespath in files:
            filepath = os.path.join(root, filespath)
            fileName = filepath.split('/')[-1]
            moduleName = fileName.split('.')[0]
            extension = os.path.splitext(filepath)[1][1:]
            if needExtFilter and extension in ext:
                allfiles.append(
                    {
                        'path': filepath,
                        'fileName': fileName,
                        'moduleName': moduleName
                    }
                )
            elif not needExtFilter:
                allfiles.append(
                    {
                        'path': filepath,
                        'fileName': fileName,
                        'moduleName': moduleName
                    }
                )
    return allfiles


# 设置配置文件内容
def setConfig(moduleName, key, value):
    global ConfigFiles
    loader = gvalues.ConfigList[moduleName]

    key_arr = key.split('.')
    tmp_arr = []
    for key_str in key_arr:
        if len(tmp_arr) == 0:
            tmp_arr.append(loader[key_str])
        elif len(tmp_arr) == len(key_arr) - 1:
            tmp_arr[-1][key_str] = value
    for file in ConfigFiles:
        if file['moduleName'] == moduleName:
            with open(file['path'], 'w', encoding='utf-8') as w_f:
                # 覆盖原先的配置文件
                yaml.dump(loader, w_f)
            break


# 获取配置文件内容
def getConfig(moduleName, key):
    loader = gvalues.ConfigList[moduleName]
    key_arr = key.split('.')
    for key_str in key_arr:
        loader = loader[key_str]
    return loader


# 设置快捷键值对
def setKeyName(moduleName, old_key, new_key):
    global KEY_ARR_TMP
    KEY_ARR_TMP[new_key] = {
        'old_key': old_key,
        'module_name': moduleName
    }


# 使用快捷键获设置yaml内容
def setKey(new_key, value):
    global KEY_ARR_TMP
    if new_key in KEY_ARR_TMP:
        old_key = KEY_ARR_TMP[new_key]['old_key']
        moduleName = KEY_ARR_TMP[new_key]['module_name']
        setConfig(moduleName, old_key, value)


# 使用快捷键获取yaml内容
def getKey(new_key):
    global KEY_ARR_TMP
    if new_key in KEY_ARR_TMP:
        old_key = KEY_ARR_TMP[new_key]['old_key']
        moduleName = KEY_ARR_TMP[new_key]['module_name']
        return getConfig(moduleName, old_key)
    else:
        return ''


