import json


# 定义一个嵌套类
class NestedClass:
    def __init__(self):
        pass

    def __str__(self):
        co = self.__dict__
        return json.dumps(co)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def get_json(self):
        return json.dumps(self.__dict__)


class msg:
    topic = "/not_set_topic"

    def __init__(self):
        pass

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def get_json(self):
        co = self.__dict__
        for key in co.keys():
            if isinstance(co[key], NestedClass):
                co[key] = co[key].__dict__
            if isinstance(co[key], list):
                for i in range(len(co[key])):
                    if isinstance(co[key][i], NestedClass):
                        co[key][i] = co[key][i].__dict__
        return json.dumps(co)

    @staticmethod
    def getMsg(data, msg_type=None):
        if isinstance(data, str):
            data = json.loads(data)
        if msg_type is None:
            msg_test = msg()
            for keyValue in data:
                msg_test.__setattr__(keyValue, data[keyValue])
            return msg_test
        else:
            msg_test = msg_type()
            co = msg_test.__dir__()
            co_final = []
            co_module = None
            # 抛开topic，getMsg以及__开头的属性
            for i in range(len(co)):
                if co[i] == 'topic' or co[i] == 'getMsg' or co[i][0] == '_' or co[i].endswith('get_json'):
                    continue
                if co[i].endswith('_module'):
                    co_module = co[i]
                    continue
                co_final.append(co[i])
            # 找到co_final中的_class结尾的键
            for key in co_final:
                if key.endswith('_class'):
                    tmp_class = getattr(msg_test, key)()
                    # key去掉_class结尾，并且把类型转换为对象
                    tmp_key = key[:-6]
                    tmp_dict = data[tmp_key]
                    # 转成对象
                    for keyValue in tmp_class.__dict__:
                        tmp_class.__setattr__(keyValue, tmp_dict[keyValue])
                    co_final.remove(key)
                    co_final.remove(tmp_key)
                    msg_test.__setattr__(tmp_key, tmp_class)
                    break
            for keyValue in co_final:
                msg_test.__setattr__(keyValue, data[keyValue])
            # msg_test，如果属性是list，则转换为对象
            if co_module is not None:
                for keyValue in msg_test.__dict__:
                    if isinstance(msg_test.__dict__[keyValue], list):
                        tmp_list = []
                        tmp_data = msg_test.__dict__[keyValue]
                        for item in tmp_data:
                            item = json.loads(item)
                            tmp_class = getattr(msg_test, co_module)()
                            for k in item:
                                tmp_class.__setattr__(k, item[k])
                            tmp_list.append(tmp_class)
                        msg_test.__setattr__(keyValue, tmp_list)
            return msg_test


class test_msg(msg):
    """
    定义一个测试消息,消息结构如下：
    {
        "test": {
            "x": 1, //测试消息的x坐标
            "y": 2, //测试消息的y坐标
            "z": 3 //测试消息的z坐标
        }
    }
    """
    topic = "/test"

    class test_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.x = ""
            self.y = ""
            self.z = ""

    def __init__(self):
        super().__init__()
        self.test = self.test_class()


# 底盘控制消息
class app_cmd_vel(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "priority": 2, //消息优先级,默认为2,int类型
        "msg": {
            "v": 1, //线速度,单位m/s,float类型
            "w": 2, //角速度,单位rad/s,float类型
            "sn": "123" //只有web端发送带sn,str类型
        }
    }
    """
    topic = "/app_cmd_vel"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.v = ""
            self.w = ""
            self.sn = ""

    def __init__(self):
        super().__init__()
        self.priority = 2  # 消息优先级，默认为2
        self.msg = self.msg_class()  # 消息体


# 底盘控制消息返回值
class app_cmd_vel_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/app_cmd_vel_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 云台控制
class cloud_platform_c(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "status":"left", //left左;right右;up上;down下;leftup左上;leftdown左下;-rightup右上;rightdown右下;zoomup放大;zoomdown缩小;stop停止;String类型
            "isPreset":"1", //是否到预置点-1:设置预置点;0:保持;1:转到预置点;2:删除预置点,int类型
            "preset_state":"", //当前预置位状态Byte
        }
    }
    """
    topic = "/cloud_platform_c"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.status = ""  # string型
            self.isPreset = ""  # int型
            self.preset_state = ""  # 当前预置位状态Byte

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 云台控制返回值
class cloud_platform_c_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/cloud_platform_c_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体
        
# 启动或关闭录包
class data_record(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn，服务端转发给客户端不需要sn
            "action":1 ,//1:启动录包;0:关闭录包,int类型
        }
    }
    """
    topic = "/data_record"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # # 只有web端发送带sn，服务端转发给客户端不需要sn
            self.action = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 启动或关闭录包返回值
class data_record_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/data_record_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 启动或关闭建图
class slam(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn，服务端转发给客户端不需要sn
            "action":1 ,//1:启动建图;0:关闭建图,int类型
        }
    }
    """
    topic = "/slam"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # # 只有web端发送带sn，服务端转发给客户端不需要sn
            self.action = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 启动或关闭建图返回值
class slam_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/slam_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 启动或关闭导航功能
class ctrl_nav(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn，服务端转发给客户端不需要sn
            "action":1 ,//1:启动建图;0:关闭建图,int类型
        }
    }
    """
    topic = "/ctrl_nav"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # # 只有web端发送带sn，服务端转发给客户端不需要sn
            self.action = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 启动或关闭导航功能返回值
class ctrl_nav_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/ctrl_nav_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 实时位置上报
class pose_message(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            'x':0, //小车的x坐标,int类型
            'y':0, //小车的y坐标,int类型
            'z':0, //小车的z坐标,int类型
            'theta':0 //小车的theta坐标,int类型
        }
    }
    """
    topic = "/pose_message"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.x = ""  # int型
            self.y = ""  # int型
            self.z = ""  # int型
            self.theta = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 获取录包程序运行状态
class get_data_record(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        
    }
    """
    topic = "/get_data_record"

    def __init__(self):
        super().__init__()
        self.msg = ""


# 获取录包程序运行状态返回值
class get_data_record_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/get_data_record_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 获取导航程序运行状态
class get_navigation(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        
    }
    """
    topic = "/get_navigation"

    def __init__(self):
        super().__init__()
        self.msg = ""


# 获取导航程序运行状态返回值
class get_navigation_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/get_navigation_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 获取建图进度
class process_message(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "p":1, //建图进度,int类型
        }
    }
    """
    topic = "/process_message"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.p = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 底盘io操作
class io_ctrl(msg):
    """
    定义一个应用消息,消息结构如下：
    {
       "priority": 1, //优先级0-5 遥操作:0 跟随:1 自主导航:2 其它:3
        "msg":{
            "sn":"123",//只有web端发送带sn,服务端转发给客户端不需要sn
            "io":[
                {
                "name":"",//控制模块名称
                "value":0//值0-255,如果是开关状态,则用0表示关,1表示开
                }
            ]
        }
    }
    """
    topic = "/io_ctrl"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # int型
            self.io = []  # list型

    def __init__(self):
        super().__init__()
        self.priority = 2  # 消息优先级,默认为2
        self.msg = self.msg_class()  # 消息体


# 底盘io操作返回值
class io_ctrl_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "io":[
                {
                "name":"",//控制模块名称
                "value":0//值0-255,如果是开关状态,则用0表示关,1表示开
                }
            ]
        }
    }
    """
    topic = "/io_ctrl_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.io = ""  # list型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 电池电压上报
class get_voltage(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn,服务端转发给客户端不需要sn
            "time":10, //发送周期,int类型
            "status":"subscribe" //subscribe:开始获取,unsubscribe:停止获取
        }
    }
    """
    topic = "/get_voltage"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # string型
            self.time = ""  # int型
            self.status = ""  # string型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 电池电压上报返回值
class get_voltage_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "voltage":[80000,0],//电池1电压，电池2电压,单位mv
            "current":[1000,0], //电池1电流,电池2电流
            "temperature":0, //当前温度,int类型
            "now_percent":0, //剩余电量百分比,单位%,int类型
            "max_capacity":0, //满电容量,单位0.1AH,int类型
            "now_capacity":0, //当前剩余容量,单位0.1AH,int类型	
            "state":0, //电池状态，参考各电池状态说明表
            "charging_state":0, //充电状态	0:未充电 1:充电
        }
    }
    """
    topic = "/get_voltage_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.voltage = ""  # list型
            self.current = ""  # list型
            self.temperature = ""  # int型
            self.now_percent = ""  # int型
            self.max_capacity = ""  # int型
            self.now_capacity = ""  # int型
            self.state = ""  # int型
            self.charging_state = ""  # int型
            

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 轮速反馈
class get_speed(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn,服务端转发给客户端不需要sn
            "time":10, //发送周期,int类型
            "status":"subscribe" //subscribe:开始获取,unsubscribe:停止获取
        }
    }
    """
    topic = "/get_speed"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # string型
            self.time = ""  # int型
            self.status = ""  # string型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 轮速反馈返回值
class get_speed_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "speed":{
                "v":0.1,//float类型
                "w":0.1//float类型
            }, 
            "error_code":0,
            "error_msg":"",
            "result":1
        }
    }
    """
    topic = "/get_speed_response"

    class msg_class(NestedClass):
        
        def __init__(self):
            super().__init__()
            self.speed = {
                "v": "",
                "w": ""
                }  # dict型
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 传感器反馈
class get_sensor_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "collide":0, //防撞触边状态:0:未触发 1:前触边触发 2:后触边触发 3:前后触边触发,int类型
            "button_stop":0, //急停按钮状态:off:正常 on:急停,string类型
            "sonic_stop":0, //超声停障状态:0:未触发 x:触发状态,int类型
            "sonic":[100,100,100,100,100,100] //超声数据 单位mm	,list型
        }
    }
    """
    topic = "/get_sensor_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.collide = ""  # int型
            self.button_stop = ""  # string型
            self.sonic_stop = ""  # int型
            self.sonic = ""  # list型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 获取任务程序运行状态
class get_task_status(msg):
    """
    定义一个应用消息,消息结构如下：
    {
    }
    """
    topic = "/get_task_status"

    def __init__(self):
        super().__init__()
        self.msg = ""


# 获取任务程序运行状态返回值
class get_task_status_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1 //0:执行任务可用，1:停止任务可用
        }
    }
    """
    topic = "/get_task_status_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 开始任务
class start_task(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn，服务端转发给客户端不需要sn
            "id":1 ,//任务id,string类型
        }
    }
    """
    topic = "/start_task"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # 只有web端发送带sn，服务端转发给客户端不需要sn
            self.id = ""  # string类型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 开始任务返回值
class start_task_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1 //0:失败，1:成功
        }
    }
    """
    topic = "/start_task_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 停止任务
class stop_task(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn，服务端转发给客户端不需要sn
            "id":1 ,//任务id,string类型
        }
    }
    """
    topic = "/stop_task"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # 只有web端发送带sn，服务端转发给客户端不需要sn
            self.id = ""  # string类型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 停止任务返回值
class stop_task_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "result":1 //0:失败，1:成功
        }
    }
    """
    topic = "/stop_task_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体


# 获取自主任务列表信息
class get_task_list(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "data":{
            "data":"true" //true: 获取
        }
    }
    """
    topic = "/get_task_list"

    class data_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.data = ""  #

    def __init__(self):
        super().__init__()
        self.data = self.data_class()  # 消息体


# 获取自主任务列表信息返回值
class task_list(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "data":[
            {
                "isStart":true, //是否循环true:循环 false:不循环,bool类型
                "task_id":"line_1654655590", //路线id,string类型
                "task_name":"0608", //路线名称,string类型
                "taskcontent":[
                    {
                        "createtime":"1654655744", //创建时间,string类型
                        "preset":"1", //预置点,string类型
                        "task_id":"task_1654655744", //任务id,string类型
                        "theta":"-1.57", //角度,string类型
                        "time":"1", //周期,string类型
                        "type":"digital", //任务类型,string类型
                        "type_text":"指针表识别",//任务类型文本,string类型
                        "x":"0.37", //x坐标,string类型
                        "y":"-0.73" //y坐标,string类型
                    }
                ]
            }
        ]
    }
    """
    topic = "/task_list"

    class data_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.isStart = ""  # string类型
            self.task_id = ""  # string类型
            self.task_name = ""  # string类型
            self.taskcontent = [{
                "createtime": "",
                "preset": "",
                "task_id": "",
                "theta": "",
                "time": "",
                "type": "",
                "type_text": "",
                "x": "",
                "y": ""
            }]  # list类型

    def __init__(self):
        super().__init__()
        self.data = self.data_class()  # 消息体


# 实时日志
class task_status(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "type":"pointer", //当前任务类型,string类型
        "content":"digital", //任务内容,string类型
        "sn":130, //机器人名称,string类型
        "task_id":"line_1655865282", //任务id,string类型
        "rec_num":"22.8", //识别结果,string类型
        "rec_type":"pointer", //执行任务类型,string类型
        "rec_in":"", //抓拍原图,string类型
        "rec_out":"", //识别图片,string类型
        "status":"end" //机器人状态,string类型
    }
    """
    topic = "/task_status"

    def __init__(self):
        super().__init__()
        self.type = ""  # string类型
        self.content = ""  # string类型
        self.sn = ""  # string类型
        self.task_id = ""  # string类型
        self.rec_num = ""  # string类型
        self.rec_type = ""  # string类型
        self.rec_in = ""  # string类型
        self.rec_out = ""  # string类型
        self.status = ""  # string类型


# 设置自主任务列表信息
class set_task_list(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "data":[
            {
                "isStart":true, //是否循环true:循环 false:不循环,bool类型
                "task_id":"line_1654655590", //路线id,string类型
                "task_name":"0608", //路线名称,string类型
                "taskcontent":[
                    {
                        "createtime":"1654655744", //创建时间,string类型
                        "preset":"1", //预置点,string类型
                        "task_id":"task_1654655744", //任务id,string类型
                        "theta":"-1.57", //角度,string类型
                        "time":"1", //周期,string类型
                        "type":"digital", //任务类型,string类型
                        "type_text":"指针表识别",//任务类型文本,string类型
                        "x":"0.37", //x坐标,string类型
                        "y":"-0.73" //y坐标,string类型
                    }
                ]
            }
        ]
    }
    """
    topic = "/set_task_list"

    class data_class_module(NestedClass):
        def __init__(self):
            super().__init__()
            self.isStart = ""  # string类型
            self.task_id = ""  # string类型
            self.task_name = ""  # string类型
            self.taskcontent = [{
                "createtime": "",
                "preset": "",
                "task_id": "",
                "theta": "",
                "time": "",
                "type": "",
                "type_text": "",
                "x": "",
                "y": ""
            }]  # list类型

    def __init__(self):
        super().__init__()
        self.data = []

# 启动或关闭跟随功能
class ctrl_follow(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn，服务端转发给客户端不需要sn
            "action":1 ,//1:启动跟随;0:关闭跟随,int类型
        }
    }
    """
    topic = "/ctrl_follow"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # # 只有web端发送带sn，服务端转发给客户端不需要sn
            self.action = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体

# 启动或关闭跟随功能返回值
class ctrl_follow_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "action:0, //结果，0:关闭，1:开启
            "result":1 //0:失败，1:成功
        }
    }
    """
    topic = "/ctrl_follow_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.action = ""  # int型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体
        
# 服务器控制机器人进行音频播放
class audio_output_play(msg):
    """
    定义一个应用消息,消息结构如下：
    {   "task_id":"10000", //任务唯一表示符
        "msg":{
            "name":"follow_start", //播放音频名称,string类型
            "volume":"" //播放音量 0-100,string类型
        }
    }
    """
    topic = "/audio/output/play"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.name = ""  # string型
            self.volume = ""  # string型

    def __init__(self):
        super().__init__()
        self.task_id = ''
        self.msg = self.msg_class()  # 消息体
        
# 服务器控制机器人进行音频播放返回值
class audio_output_play_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {   "task_id":"10000", //任务唯一表示符
        "msg":{
            "error_code": 0, //出错代码
            "error_msg": "", //出错信息
            "result": 1 //结果 0:失败,1:成功
        }
    }
    """
    topic = "/audio/output/play_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # string型
            self.error_msg = ""  # string型
            self.result = ""  # string型

    def __init__(self):
        super().__init__()
        self.task_id = ''
        self.msg = self.msg_class()  # 消息体

# 读取或写入单板硬件配置信息
class hardware_ctrl(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        {
            "priority": 0, //优先级0-5 遥操作:0 跟随:1 自主导航:2 其它:3
            "msg":{
                "Mode":1, //uint8_t,操作模式 0:读取 1:写入
                "MaxRPM":1, //uint16_t,电机最高转速 RPM
                "DriverType":1, //uint8_t,控制指令：0x00:惠斯通 0x01:拓达 0x02:中菱
                "ChassisType":1, //uint8_t,底盘类型
                "VoltageType":1, //uint8_t,电压表类型 0:电压表 1:速遥电池 2:RS485电压模块
                "UltrasonicType":1, //uint8_t,超声类型 104:KS104 136:KS136A
                "FrontNumber":1, //uint8_t,前侧超声数量
                "BackNumber":1, //uint8_t,后侧超声数量
                "SideNumber":1, //uint8_t,左右侧超声数量
                "GearBoxDirection":1, //uint8_t,减速器转向 0:反向 1:正向
            }
        }
    }
    """
    topic = "/hardware_ctrl"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.Mode = ""  # uint8_t,
            self.MaxRPM = ""  # uint16_t,
            self.DriverType = ""  # uint8_t,
            self.ChassisType = ""  # uint8_t,
            self.VoltageType = ""  # uint8_t,
            self.UltrasonicType = ""  # uint8_t,
            self.FrontNumber = ""  # uint8_t,
            self.BackNumber = ""  # uint8_t,
            self.SideNumber = ""  # uint8_t,
            self.GearBoxDirection = ""  # uint8_t,
            
    def __init__(self):
        super().__init__()
        self.priority = ""  
        self.msg = self.msg_class()  # 消息体

# 读取或写入单板硬件配置信息返回值
class hardware_ctrl_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        {
            "msg":{
                "Mode":1, //uint8_t,操作模式 0:读取 1:写入
                "MaxRPM":1, //uint16_t,电机最高转速 RPM
                "DriverType":0x00, //uint8_t,控制指令：0x00:惠斯通 0x01:拓达 0x02:中菱
                "ChassisType":1, //uint8_t,底盘类型
                "VoltageType":1, //uint8_t,电压表类型 0:电压表 1:速遥电池 2:RS485电压模块
                "UltrasonicType":104, //uint8_t,超声类型 104:KS104 136:KS136A
                "FrontNumber":1, //uint8_t,前侧超声数量
                "BackNumber":1, //uint8_t,后侧超声数量
                "SideNumber":1, //uint8_t,左右侧超声数量
                "GearBoxDirection":1, //uint8_t,减速器转向 0:反向 1:正向
                "PSC": int(),  //PWM分频系数
                "PER": int(),  //PWM自动重载值 T=(PSC-1)/(PER-1)/72000 ms
                "Retained1": int(),  //备用
                "Retained2": int(),  //备用
                "Retained3": int(),  //备用
                "Retained4": int(),  //备用
                "Retained5": int(),  //备用
                "Retained6": int(),  //备用
                "Retained7": int(),  //备用
                "Retained8": int(),  //备用
                "Retained9": int(),  //备用
                "Retained10": int(),  //备用
            }
        }
    }
    """
    topic = "/hardware_ctrl_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.Mode = ""  # uint8_t,
            self.MaxRPM = ""  # uint16_t,
            self.DriverType = ""  # uint8_t,
            self.ChassisType = ""  # uint8_t,
            self.VoltageType = ""  # uint8_t,
            self.UltrasonicType = ""  # uint8_t,
            self.FrontNumber = ""  # uint8_t,
            self.BackNumber = ""  # uint8_t,
            self.SideNumber = ""  # uint8_t,
            self.GearBoxDirection = ""  # uint8_t,
            self.PSC = ""  # uint8_t
            self.PER = ""  # uint8_t
            self.Retained1 = ""
            self.Retained2 = ""
            self.Retained3 = ""
            self.Retained4 = ""
            self.Retained5 = ""
            self.Retained6 = ""
            self.Retained7 = ""
            self.Retained8 = ""
            self.Retained9 = ""
            self.Retained10 = ""
            
    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体
        
#获取跟随运动参数
class get_navigation_info(msg):
    """
    定义一个应用消息,消息结构如下：
    {
    }
    """
    topic = "/get_navigation_info"

    def __init__(self):
        super().__init__()
        
#获取跟随运动参数返回值
class get_navigation_info_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "move_speed_v":1.0, //最大速度,float型
            "move_speed_w":1.0, //最大角速度,float型
            "follow_dis":1.0, //跟随距离,float型
            "result":1, //跟随状态,0:未开启,1:已开启,2:错误,int型
            "error_msg":"" //错误信息,string型
        }
    }
    """
    topic = "/get_navigation_info_response"
    
    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.move_speed_v = ""  # float型
            self.move_speed_w = ""  # float型
            self.follow_dis = ""  # float型
            self.result = ""  # float型
            self.error_msg = ""  # float型
            
    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体
        
#服务器控制机器人云台进行运动
class actuator_ptz_control(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "status":"",//状态String
            "isPreset":"",//是否设置到预置点Int
            "preset_state":"",//当前预置位状态Byte
            "cam_ex_code:"",//云台异常代码Int
            "x":"", //云台水平轴转动到指定角度;0:初始点;
            "y":"" //云台垂直轴转动到指定角度;0:初始点;
        }
    }
    """
    topic = "/actuator/ptz/control"
    
    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.status = ""  # String型
            self.isPreset = ""  # Int型
            self.preset_state = ""  # Byte型
            self.cam_ex_code = ""  # Int型
            self.x = ""  # Int型
            self.y = ""  # Int型
            
    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体
        
#pc端开启关闭话筒
class audio_voice_control(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "sn":"123",//web端发送带sn,服务端转发给客户端不需要sn
            "action":1 ,//1:话筒开;0:话筒关,int类型
        }
    }
    """
    topic = "/audio_voice_control"
    
    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.sn = ""  # String型
            self.action = ""  # Int型
            
    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体
        
#pc端开启关闭话筒返回值 
class audio_voice_control_response(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":{
            "error_code":0,
            "error_msg":"",
            "action:0, //结果,0:关闭,1:开启
            "result":1 //0:失败,1:成功
        }
    }
    """
    topic = "/audio_voice_control_response"

    class msg_class(NestedClass):
        def __init__(self):
            super().__init__()
            self.error_code = ""  # int型
            self.error_msg = ""  # string型
            self.action = ""  # int型
            self.result = ""  # int型

    def __init__(self):
        super().__init__()
        self.msg = self.msg_class()  # 消息体

#模块管理
class modules_manage_pub(msg):
    """
    定义一个应用消息,消息结构如下：
    {
        "msg":[
            {
                "name":"Joysticks", //模块名称
                "status":true //模块状态,true:开启,false:关闭
            }
        ]
    }
    """
    topic = "/audio/voice/control_response"

    class data_class_module(NestedClass):
        def __init__(self):
            super().__init__()
            self.name = ""  # int型
            self.status = ""  # string型
            
    def __init__(self):
        super().__init__()
        self.msg = []  # 消息体
