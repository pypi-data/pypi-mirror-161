DXR
=========
Installation / 首次安装
--------------------------
    pip install DXR
Installation / 更新安装
--------------------------
    pip install -U DXR
Usage / 使用
--------------------------
```
from Dxr_mqtt.dxr_mqtt import *
from Dxr_mqtt.msg import *
from Dxr_utils.dxr_utils import *

# 设置mqtt连接地址，端口号，客户端id
setServerUrl(url="xxx.xxx.xxx.xxx", port=1883, clientID="dxr_mqtt")
# 设置模块名称，用于自动绑定日志话题
setModuleName("dxr_mqtt")

# 日志模块这边需要注意的是
# 如果mqtt连接不是本地的，那么需要先设置mqtt连接地址，端口号，客户端id
# 之后才能调用log模块
from Dxr_log.log import *

# 设置日志的打印,主要分为info,error,debug三种级别
setLogPrint(info=False, error=False, debug=False)

# 定义一个发布器，并绑定消息类型app_cmd_vel
pub = Dxr_Publisher(app_cmd_vel)


# 使用dxr_subscriber的装饰器直接绑定订阅回调
@dxr_subscriber(app_cmd_vel)
def app_cmd_vel_callback(data, topic):
    # 用msg中的静态方法getMsg来获取消息,并指定消息类型为app_cmd_vel
    mm: app_cmd_vel = msg.getMsg(data, app_cmd_vel)
    # 鼠标放到消息类型上，可以看到消息类型的结构体，可以根据结构体的字段来解析消息
    print_info(f'priority: {mm.priority},v: {mm.msg.v},w: {mm.msg.w}')
    # 进行后续的操作
    pass


# 绑定一个日志的话题，用来接收日志消息
# 话题格式为/response/log_manager/{模块名}/{日志类型}
# 日志类型分为all,debug,error
# 模块名和日志类型如果不确定或者不固定可以用'+'进行通配
@dxr_subscriber('/response/log_manager/dxr_mqtt/all')
def all_log_callback(data, topic):
    mm = msg.getMsg(data)
    print(f'data: {mm.data}, status: {mm.status}, error: {mm.error}')


# 为了测试回调函数的调用，这里使用一个简单的发布消息
i = 100
while i > 0:
    # 使用对应的消息类型的构造函数来创建一个消息
    m = app_cmd_vel()
    m.priority = time.time()
    m.msg.v = time.time()
    m.msg.w = time.time()
    m.msg.sn = time.time()
    # 发布消息
    pub.publish(m)
    i -= 1
    time.sleep(1)

```
Usage / 进阶使用（闭环消息的实现）
--------------------------
使用await_publish订阅闭环消息
```
import threading
import time
from Dxr_mqtt.dxr_mqtt import *
from Dxr_mqtt.msg import *

setServerUrl("127.0.0.1")

# 创建消息发布器，消息类型为data_record
data_record_pub = Dxr_Publisher(data_record)


def test():
    # 循环发布消息类型为data_record的消息
    while True:
        # 实例化消息
        m = data_record()
        m.msg.action = "stop"
        m.msg.sn = "123456789"
        """
        使用await_publish来实现消息闭环
        await_publish(msg, timeout, topic)
        {
            msg 为发送的消息
            timeout 不指定的时候，为一直等待设定话题的消息，指定后超时时间中未收到消息，会接收到一个None消息
            topic 为指定闭环消息的话题类型，如果不指定，则默认为原话题类型后追加'_response',可以传递字符串类型的话题，也可以传递消息类型
        }
        """
        res = data_record_pub.await_publish(m, timeout=5, topic=app_cmd_vel)
        print(f'test: {res}')


# threading.Thread(target=test1).start()
test()
```
在另外一个文件中实现消息的发布
```
import threading
import time
from Dxr_mqtt.dxr_mqtt import *
from Dxr_mqtt.msg import *

setServerUrl("127.0.0.1")
app_cmd_vel_pub = Dxr_Publisher(app_cmd_vel)
    
# 每1s发送app_cmd_vel消息    
while True:
    time.sleep(1)
    m = app_cmd_vel()
    m.priority = 1
    m.msg.v = 0.1
    m.msg.w = 0.1
    m.msg.sn = time.time()
    app_cmd_vel_pub.publish(m)
    print(f'test: {m}')
```
Dxr_bytes / 使用说明
--------------------------
包含的方法说明
```
显示功能：
    # 数组转16进制字符串
    bytes_to_hex_str(bs)
    # 16进制字符串转bytearray数组
    def hex_str_to_bytes(str_data)
从数组获取数据：
    # 从bytes获取int8
    def get_int8_from_bytes(bytes_data, index=0)
    # 从bytes获取uint8
    def get_uint8_from_bytes(bytes_data, index=0)
    # 从bytes获取int16
    def get_int16_from_bytes(bytes_data, index=0, order="")
    # 从bytes获取uint16
    def get_uint16_from_bytes(bytes_data, index=0, order="")
    # 从bytes获取int32
    def get_int32_from_bytes(bytes_data, index=0, order="")
    # 从bytes获取uint32
    def get_uint32_from_bytes(bytes_data, index=0, order="")
    # 从bytes获取float
    def get_float_from_bytes(bytes_data, index=0, order="")
    # 从bytes获取double
    def get_double_from_bytes(bytes_data, index=0, order="")
    # 从bytes获取指定格式数据
    def get_data_from_bytes(bytes_data, type="", index=0, order="")
将数据加入数组：
    # 加入int8至bytes
    def add_int8_to_bytes(bytes_data, value, index=None)
    # 加入uint8至bytes
    def add_uint8_to_bytes(bytes_data, value, index=None)
    # 加入int16至bytes
    def add_int16_to_bytes(bytes_data, value, index=None, order="")
    # 加入uint16至bytes
    def add_uint16_to_bytes(bytes_data, value, index=None, order="")
    # 加入int32至bytes
    def add_int32_to_bytes(bytes_data, value, index=None, order="")
    # 加入uint32至bytes
    def add_uint32_to_bytes(bytes_data, value, index=None, order="")
    # 加入float至bytes
    def add_float_to_bytes(bytes_data, value, index=None, order="")
    # 加入double至bytes
    def add_double_to_bytes(bytes_data, value, index=None, order="")
将数据转换数组：
    # 获得int8对应bytearray
    def get_int8_bytes(value)
    # 获得uint8对应bytearray
    def get_uint8_bytes(value)
    # 获得int16对应bytearray
    def get_int16_bytes(value, order="")
    # 获得uint16对应bytearray
    def get_uint16_bytes(value, order="")
    # 获得int32对应bytearray
    def get_int32_bytes(value, order="")
    # 获得uint32对应bytearray
    def get_uint32_bytes(value, order="")
    # 获得float对应bytearray
    def get_float_bytes(value, order="")
    # 获得double对应bytearray
    def get_double_bytes(value, order="")
crc16_modbus功能：
    # bytes加入crc16_modbus
    def bytes_add_crc16_modbus(bytes_data, start_index=0, front="")
    # crc16_modbus返回int16
    def crc16_modbus_int16(bytes_data, start_index=0)
    # crc16_modbus返回[crc_L,crc_H]
    def crc16_modbus_bytes(bytes_data, start_index=0)
其他功能：
    # 返回帧头
    def find_head(bytes_data, head_data)
```
使用说明
```
from Dxr_bytes.Dxr_bytes import *
#测试代码
if __name__ == '__main__':
    input_data = [0x01, 0x03, 0x00, 0x01, 0x00, 0x01]
    print(bytes_to_hex_str(input_data))
    print(bytes_to_hex_str(crc16_modbus_bytes(input_data)))
    print(crc16_modbus_int16(input_data))
    print(bytes_to_hex_str(bytes_add_crc16_modbus(input_data,front="low")))
```
Dxr_serial / 使用说明
--------------------------
包含的方法说明
```
# 初始化，实例属性如下，需生成实例后配置
    def __init__(self):
        setLogPrint(info=True, error=True, debug=True)
        self.obj_name = ""  # 对象名称
        self.port_name = ""  # 端口，GNU / Linux上的/ dev / ttyUSB0 等 或 Windows上的 COM3 等
        self.bps = 115200  # 波特率，标准值之一：50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,19200,38400,57600,115200
        self.time_out = 5  # 超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
        self.parity = ""  # N E
        self.serial = {}  # 串口对象
        self.is_open = False  # 连接状态
        self.receive_thread = threading.Thread()  # 内部接收线程
        self.auto_connect_thread = threading.Thread()  # 内部自动重连连接线程
        self.auto_connect_flag = True  # 内部重连标志
        self.callback_func = None  # 默认的回调函数
# 控制方法
    # 串口连接 连接成功之后接收线程自动开启
    def connect(self)
    # 串口断开连接
    def close(self)
    # 串口接收
    def read_msg(self)
    # 串口发送
    def send_msg(self, msg)
```
使用说明
```
from Dxr_serial.Dxr_serial import *
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
```
Dxr_yaml_read / 使用说明
--------------------------
包含的方法说明
```
# 读取批量参数
def read_yaml_file(file)
# 获取值-通过目标名字（仅支持第一级目标）
def get_value_by_target_name(file, name)
# 更新对象-通过目标对象（仅支持第一级目标）
def update_object_by_target_object(target, data)
# 更新部分文件内容-通过目标对象（仅支持第一级目标）
def update_file_by_target_object(file, target_object, target_object_name)
# 更新整个文件内容-通过目标对象
def update_file_all(file, target_object)
```
使用说明
```
from Dxr_yaml.Dxr_yaml import *
# 测试代码
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
```