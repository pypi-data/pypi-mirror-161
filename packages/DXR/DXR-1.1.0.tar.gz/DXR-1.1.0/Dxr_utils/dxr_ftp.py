#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
FTP常用操作
"""
from ftplib import FTP
import os


class FTP_OP(object):
    def __init__(self, host, port=2121, username="", password=""):
        """
            初始化ftp
        :param host: ftp主机ip
        :param username: ftp用户名
        :param password: ftp密码
        :param port:  ftp端口 （默认21）
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port

    def ftp_connect(self):
        """
        连接ftp
        :return:
        """
        ftp = FTP()
        ftp.set_debuglevel(0)  # 不开启调试模式
        ftp.connect(host=self.host, port=self.port)  # 连接ftp
        ftp.login(self.username, self.password)  # 登录ftp
        return ftp

    @staticmethod
    def download_file(url_, dst_file_path_):
        """
        从ftp下载文件到本地
        :param url_: ftp下载文件路径
        :param dst_file_path_: 本地存放路径
        :return:
        """
        ftp_arr = url_.split('//')[1].split('/')
        host_, port_ = ftp_arr[0].split(":")
        # print(host_, port_)
        ftp_file_path_ = ""
        for item in ftp_arr[1:]:
            ftp_file_path_ = ftp_file_path_ + "/" + item
        # print(ftp_file_path_)
        ftp_ = FTP_OP(host=host_, port=int(port_))
        buffer_size = 1024000  # 默认是8192
        ftp_servcie = ftp_.ftp_connect()
        print(ftp_servcie.getwelcome())  # 显示登录ftp信息
        ftp_file = ftp_file_path_
        write_file = dst_file_path_
        if not os.path.exists(write_file):
            open(write_file, 'w').close()
        with open(write_file, "wb") as f:
            ftp_servcie.retrbinary('RETR {0}'.format(ftp_file), f.write, buffer_size)
            f.close()
        ftp_servcie.quit()


if __name__ == '__main__':
    url = "ftp://192.168.10.102:2121/all.log"
    dst_file_path = os.environ['HOME'] + "/lu/all.log"
    FTP_OP.download_file(url, dst_file_path)