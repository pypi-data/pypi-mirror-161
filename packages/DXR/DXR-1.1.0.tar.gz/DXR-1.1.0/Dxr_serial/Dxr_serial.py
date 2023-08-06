from Dxr_log.log import *
import threading
import time
import serial


class serial_class:
    # 初始化
    def __init__(self):
        self.obj_name = ""  # 对象名称
        self.port_name = ""  # 端口，GNU / Linux上的/ dev / ttyUSB0 等 或 Windows上的 COM3 等
        self.bps = 115200  # 波特率，标准值之一：50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,19200,38400,57600,115200
        self.time_out = 5  # 超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
        self.parity = ""  # N E O
        self.serial = {}  # 串口对象
        self.is_open = False  # 连接状态
        self.auto_connect_flag = True  # 内部重连标志
        self.callback_func = None  # 默认的回调函数
        self._auto_connect_thread = threading.Thread()  # 内部自动重连连接线程
        self._receive_thread = threading.Thread()  # 内部接收线程
        self.debug_flag = False  # debug模式

    # 串口连接 连接成功之后接收线程自动开启
    def connect(self):
        try:
            # 检查串口是否开启
            if self.is_open:
                self.close()
            self.is_open = False
            # 串口实例生成
            if not self.debug_flag:
                self.serial = serial.Serial(self.port_name, self.bps, timeout=self.time_out, parity=self.parity)
            self.is_open = True
            # 检查是否绑定接受回调
            if self.callback_func is None:
                print_error(self.obj_name + " " + "without dispose_func")
            print_info(self.obj_name + " " + "connect to " + self.port_name)
            # 内部接收线程开启
            self._receive_thread = threading.Thread(target=self._receive_thread_poc)
            self._receive_thread.daemon = True
            self._receive_thread.start()
            return True
        except Exception as e:
            print_error(self.obj_name + " " + "connect error:" + e.__str__())
            return False

    # 串口断开连接
    def close(self):
        try:
            # 关闭
            self.is_open = False
            time.sleep(0.5)
            if not self.debug_flag:
                self.serial.close()
            print_info(self.obj_name + " " + "close")
        except Exception as e:
            print_error(self.obj_name + " " + "close error:" + e.__str__())

    # 串口接收
    def read_msg(self):
        # 接收串口发送过来的数据
        if self.is_open:
            try:
                if not self.debug_flag:
                    if self.serial.in_waiting > 0:
                        data = self.serial.read(self.serial.in_waiting)
                        if self.callback_func is not None:
                            self.callback_func(data)
                        else:
                            print("receive:" + data)
                    else:
                        time.sleep(0.001)
            except Exception as e:
                raise e

    # 串口发送
    def send_msg(self, msg):
        try:
            if msg:
                # 检查串口状态
                if self.is_open:
                    if not self.debug_flag:
                        self.serial.write(msg)
                    else:
                        print(msg)
                else:
                    raise Exception("is not open")
        except Exception as e:
            # 非主动停止进行重启
            if self.is_open:
                print_debug(self.obj_name + " " + "send_msg Error:" + e.__str__())
                self._auto_connect()
            # 主动停止退出
            else:
                print_debug(self.obj_name + " " + "send fail and exit")

    # 自动重连线程
    def _auto_connect_thread_poc(self):
        print_info(self.obj_name + " " + "start auto_connect_thread_poc")
        while 1:
            try:
                # 检查初值
                if self.port_name != "" and self.bps != 0:
                    # 连接
                    if self.connect():
                        break
                    else:
                        # 连接失败则重复进行
                        time.sleep(5)
            except Exception as e:
                # 连接异常则重复进行
                print_error(self.obj_name + " " + "failed to connect to server: " + e.__str__())
                time.sleep(5)

    # 自动重连
    def _auto_connect(self):
        # 需要自动重连则开启自动重连线程
        if self.auto_connect_flag:
            # 检查是否重复开启
            if not self._auto_connect_thread.is_alive():
                self._auto_connect_thread = threading.Thread(target=self._auto_connect_thread_poc)
                self._auto_connect_thread.daemon = True
                self._auto_connect_thread.start()
            else:
                print_error(self.obj_name + " " + "auto_connect_thread has been started")
        # 不需要自动重连则断开连接
        else:
            self.close()

    # 接收线程
    def _receive_thread_poc(self):
        try:
            print_info(self.obj_name + " " + "start receive_thread")
            while self.is_open:
                self.read_msg()
            print_info("receive_thread normal exit")
        except Exception as e:
            # 中止属于程序主动执行，跳过重启
            if e.__str__().find("中止") > 0:
                pass
            else:
                # 非主动停止
                if self.is_open:
                    print_error(self.obj_name + " " + "receive_thread error:" + e.__str__())
                    self._auto_connect()


if __name__ == '__main__':
    # 接收回调方法
    def com_callback(data):
        print(data)


    # 生成串口实例
    com = serial_class()
    # 串口实例属性配置
    com.obj_name = "rs485_1"
    com.port_name = "COM4"
    com.bps = 9600
    com.time_out = 10
    com.parity = "N"
    com.auto_connect_flag = True
    com.callback_func = com_callback
    com.debug_flag = False
    # 串口连接
    com.connect()
    send_data = [0x01, 0x02, 0x03, 0x04]
    for x in range(10):
        # 串口发送
        com.send_msg(send_data)
        time.sleep(0.5)
    # 串口关闭
    com.close()
