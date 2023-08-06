from Dxr_log.log import *
import yaml
import re


# 读取批量参数
def read_yaml_file(file):
    """ 读取批量参数
    :param file: 目标yaml文件完整路径
    :return: data 目标yaml文件内容以Dict对象返回
    """
    # 分割路径名称，提取文件对象
    target = re.split(r'[/,\\]', file)[-1]
    # 打开文件
    print_info("start read " + target)
    fd = open(file, "r", encoding="utf-8")
    data_str = fd.read()
    fd.close()
    # yaml读取
    try:
        data = yaml.load(data_str, Loader=yaml.FullLoader)
    except:
        data = yaml.load(data_str)
    print_info("finish read " + target)
    return data


# 获取对象-通过目标名字（仅支持第一级目标）
def get_value_by_target_name(file, name):
    """ 获取对象-通过目标名字（仅支持第一级目标）
    :param1 file: 目标yaml文件完整路径
    :param2 name: 目标对象名称
    :return: 目标yaml文件中目标对象值，无匹配{}
    """
    # 分割路径名称，提取文件对象
    target = re.split(r'[/,\\]', file)[-1]
    # 打开文件
    print_info("start read " + target)
    fd = open(file, "r", encoding="utf-8")
    data_str = fd.read()
    fd.close()
    # yaml读取
    try:
        data = yaml.load(data_str, Loader=yaml.FullLoader)
    except:
        data = yaml.load(data_str)
    print_info("finish read " + target)
    # 读取键值为name
    if name in data.keys():
        print("[" + name + "]" + str(data[name]))
        return data[name]
    else:
        print_error("config file do not has " + name)
        return {}


# 更新对象-通过目标对象（仅支持第一级目标）
def update_object_by_target_object(target, data):
    """ 更新对象-通过目标对象（仅支持第一级目标）
    :param1 target: 更新对象
    :param2 data: 目标对象
    """
    if target:
        for x in target.keys():
            if x in data.keys():
                if type(target[x]) == type(data[x]):
                    target[x] = data[x]
                    print("[" + x + "]" + str(data[x]))
                else:
                    print_error("[" + x + "]" + "data type error")
            else:
                print_error("config file do not has " + x)
    else:
        print_error("target is empty")


# 更新部分文件内容-通过目标对象（仅支持第一级目标）
def update_file_by_target_object(file, target_object, target_object_name):
    """ 更新部分文件内容-通过目标对象（仅支持第一级目标）
    :param1 file: 目标yaml文件完整路径
    :param2 target_object: 目标对象
    :param3 target_object_name: 目标对象在文件中的名称
    :return: 更新文件是否成功
    """
    # 分割路径名称，提取文件对象
    target = re.split(r'[/,\\]', file)[-1]
    # 打开文件
    print_info("start read " + target)
    fd = open(file, "r", encoding="utf-8")
    data_str = fd.read()
    print_info("finish read " + target)
    fd.close()
    # yaml读取
    try:
        data = yaml.load(data_str, Loader=yaml.FullLoader)
    except:
        data = yaml.load(data_str)
    # yaml文件内容与目标对象匹配
    result = True
    if target_object_name in data.keys():
        for x in target_object.keys():
            if x in data[target_object_name].keys():
                if type(target_object[x]) != type(data[target_object_name][x]):
                    result = False
                    print_error("[" + x + "]" + "data type error, save failed")
                    break
            else:
                result = False
                print_error("target_object do not has " + x)
                break
    else:
        result = False
        print_error("config file do not has " + target_object_name)
    # 匹配成功，写入target_object
    if result:
        data[target_object_name] = target_object
        fd_1 = open(file, "w", encoding="utf-8")
        str_temp = yaml.dump(data)
        fd_1.write(str_temp)
        return True
    # 失败返回
    else:
        return False


# 更新整个文件内容-通过目标对象
def update_file_all(file, target_object):
    """ 更新整个文件内容-通过目标对象
    :param1 file: 目标yaml文件完整路径
    :param2 target_object: 写入对象
    :return: 更新文件是否成功
    """
    try:
        target = re.split(r'[/,\\]', file)[-1]
        print_info("start open " + target)
        fd = open(file, "w", encoding="utf-8")
        str_temp = yaml.dump(target_object)
        fd.write(str_temp)
        fd.close()
        return True
    except:
        return False


# 测试代码
if __name__ == '__main__':
    # 读取yaml文件
    config_test = read_yaml_file("./config_test.yaml")
    print("config_test:" + str(config_test))
    com_config_set = {
        "port_name": "COM5",
        "bps": 9600,
        "parity": "N"
    }
    # 获取对象-通过目标名字
    com_config_read = get_value_by_target_name("./config_test.yaml", "com_config")
    print("com_config_read:" + str(com_config_read))
    # 更新对象-通过目标对象
    update_object_by_target_object(com_config_read, com_config_set)
    print("com_config_read update:" + str(com_config_read))
    com_config_set = {
        "port_name": "COM3",
        "bps": 115200,
        "parity": "N"
    }
    # 更新部分文件内容-通过目标对象
    print(str(update_file_by_target_object("./config_test.yaml", com_config_set, "com_config")))
    print("update_file_by_target_object:" + str(read_yaml_file("./config_test.yaml")))
    # 更新整个文件内容-通过目标对象
    print(str(update_file_all("./config_test.yaml", config_test)))
    print("update_file_all:" + str(read_yaml_file("./config_test.yaml")))
