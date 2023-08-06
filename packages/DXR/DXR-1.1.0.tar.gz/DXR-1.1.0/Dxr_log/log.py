# -*- coding: utf-8 -*-
import logging
import logging.handlers
import os
from logging import handlers
import platform

from Dxr_mqtt.msg import msg
from Dxr_utils import gvalues
from Dxr_mqtt.dxr_mqtt import *

isPrintDebug = False
isPrintError = True
isPrintInfo = True


def setLogPrint(info=True, error=True, debug=False):
    global isPrintDebug, isPrintError, isPrintInfo
    isPrintInfo = info
    isPrintError = error
    isPrintDebug = debug


class Logger(object):
    #  日志级别关系映射
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self, filename, level='info', when='D', backCount=3,
                 fmt='%(asctime)s line %(lineno)s %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount, encoding='utf-8')
        th.setFormatter(format_str)  # 设置文件里写入的格式
        # self.logger.addHandler(sh)  # 把对象加到logger里
        self.logger.addHandler(th)

    if platform.system() == 'Windows':
        if not os.path.exists('D:\\log'):  # 判断是否存在文件夹如果不存在则创建为文件夹
            try:
                os.makedirs('D:\\log')  # makedirs 创建文件时如果路径不存在会创建这个路径
            except Exception as ex:
                print(ex)
                pass
    else:
        if not os.path.exists(os.environ['HOME'] + '/log/'):  # 判断是否存在文件夹如果不存在则创建为文件夹
            try:
                os.makedirs(os.environ['HOME'] + '/log/')  # makedirs 创建文件时如果路径不存在会创建这个路径
            except Exception as ex:
                print(ex)
                pass


if platform.system() == 'Windows':
    all_log = Logger('D:\\log\\all.log', level='info')
    err_log = Logger('D:\\log\\error.log', level='error')
    debug_log = Logger('D:\\log\\debug.log', level='debug')
else:
    all_log = Logger(os.environ['HOME'] + '/log/all.log', level='info')
    err_log = Logger(os.environ['HOME'] + '/log/error.log', level='error')
    debug_log = Logger(os.environ['HOME'] + '/log/debug.log', level='debug')

all_publisher = Dxr_Publisher('/response/log_manager/' + gvalues.module_name + '/all')
debug_publisher = Dxr_Publisher('/response/log_manager/' + gvalues.module_name + '/debug')
error_publisher = Dxr_Publisher('/response/log_manager/' + gvalues.module_name + '/error')


def print_info(log_str):
    global isPrintInfo
    try:
        all_log.logger.info(log_str)
        m = msg()
        m.data = log_str
        m.status = True
        m.error = 0
        all_publisher.publish(m.get_json())
        if isPrintInfo:
            print(log_str)
    except Exception as ex:
        print(ex)


def print_debug(log_str):
    global isPrintDebug
    try:
        debug_log.logger.debug(log_str)
        all_log.logger.info(log_str)
        m = msg()
        m.data = log_str
        m.status = True
        m.error = 0
        debug_publisher.publish(m.get_json())
        if isPrintDebug:
            print(log_str)
    except Exception as ex:
        print(ex)


def print_error(log_str):
    global isPrintError
    try:
        all_log.logger.info(log_str)
        err_log.logger.error(log_str)
        m = msg()
        m.data = log_str
        m.status = True
        m.error = 0
        error_publisher.publish(m.get_json())
        if isPrintError:
            print(log_str)
    except Exception as ex:
        print(ex)
