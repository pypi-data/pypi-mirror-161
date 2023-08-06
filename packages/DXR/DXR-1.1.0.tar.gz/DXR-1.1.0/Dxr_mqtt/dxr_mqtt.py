# -*- coding: utf-8 -*-
import json
from multiprocessing import RLock
import threading
import time

import paho.mqtt.client as mqtt

server_url = '127.0.0.1'
server_port = 1883
callback_dit = {}
publish_dit = []
mqttc = None
rc = -1
isPrintLog = False
client_id = str(int(time.time() * 1000))
topic_list_str_pub = ''
topic_list_str_sub = ''
isReconnect = False
mqtt_thread = None


def setServerUrl(url='127.0.0.1', port=1883, clientID=str(int(time.time() * 1000))):
    global server_url, server_port, client_id
    server_url = url
    server_port = int(port)
    client_id = clientID


def setMqttLog(PrintLog=False):
    global isPrintLog
    isPrintLog = PrintLog


class Dxr_url_port:
    pass


def get_cond(topic):
    global callback_dit
    if not isinstance(topic, str):
        topic = topic.topic
    if topic not in callback_dit:
        Dxr_Subscriber(topic, None)
    return callback_dit[topic]['cond']


def on_connect(client, userdata, flags, rrc):
    global rc, isReconnect, mqttc
    rc = rrc
    print("Connected with result code " + str(rc))
    if isReconnect:
        # 获取callback_dit中的所有topic,键
        keys = callback_dit.keys()
        # 重新订阅
        for item in keys:
            client.unsubscribe(item)
            client.subscribe(item, 0)


# 一旦订阅到消息，回调此方法
def on_message(client, obj, msg):
    global callback_dit
    topic = msg.topic
    print(f'on_message topic={topic}')
    try:
        # threading.Thread(target=callback, args=(topic, msg, client), daemon=True).start()
        callback(topic, msg, client)
    except Exception as ex:
        print(ex)
        keys = callback_dit.keys()
        topic_arr = topic.split("/")[1:]
        for item in keys:
            item_arr = item.split("/")[1:]
            isThisTopic = True
            if len(item_arr) == len(topic_arr):
                for i in range(len(item_arr)):
                    if item_arr[i] == "+":
                        continue
                    if item_arr[i] != topic_arr[i]:
                        isThisTopic = False
                        break
            if isThisTopic:
                # threading.Thread(target=callback, args=(item, msg, client), daemon=True).start()
                callback(item, msg, client)
                break


def callback(topic, msg, client):
    global callback_dit
    msg = str(msg.payload.decode("utf-8"))
    if type(msg) is str:
        msg = json.loads(msg)
    if topic not in callback_dit:
        callback_dit[topic] = {'func': None, 'cond': threading.Event(), 'msg': None}
    callback_dit[topic]['msg'] = msg
    cond = get_cond(topic)
    cond.set()
    cond.clear()
    if callback_dit[topic]['func'] is not None:
        func = callback_dit[topic]['func']
        func(msg, topic)


# 一旦订阅成功，回调此方法
def on_subscribe(mqttc, obj, mid, granted_qos):
    # print("Subscribed: " + str(mid) + " " + str(granted_qos))
    pass


# 一旦有log，回调此方法
def on_log(mqttc, obj, level, string):
    global isPrintLog
    if isPrintLog:
        print(string)


def on_disconnect(client, userdata, rrc):
    global rc, isReconnect, mqttc
    rc = rrc
    isReconnect = True
    print("Disconnected with result code " + str(rc))


def Mqtt():
    global mqttc, server_url, server_port, client_id, mqtt_thread
    if mqttc is None:
        try:
            # 新建mqtt客户端，默认没有clientid，clean_session=True, transport="tcp"
            mqttc = mqtt.Client(client_id=client_id)
            mqttc.will_set('/topic/' + client_id, '', retain=True)
            mqttc.on_message = on_message
            mqttc.on_connect = on_connect
            mqttc.on_subscribe = on_subscribe
            mqttc.on_disconnect = on_disconnect
            mqttc.on_log = on_log
            # 连接broker，心跳时间为60s
            mqttc.connect(server_url, server_port, 5)
            # 订阅该主题，QoS=0
            mqtt_thread = threading.Thread(target=mqttc.loop_forever, daemon=True)
            mqtt_thread.start()
            return mqttc
        except Exception as ex:
            print(ex)
            return None
    else:
        return mqttc


def get_mqtt_status():
    global mqttc
    if mqttc is None:
        return False
    else:
        if mqttc.is_connected():
            return True
        else:
            return False


class Dxr_Subscriber:
    def __init__(self, topic, callback):
        global callback_dit, topic_list_str_pub, topic_list_str_sub, mqttc
        if mqttc is None:
            mqttc = Mqtt()
        if isinstance(topic, str):
            mqttc.subscribe(topic)
            self.topic = topic
        else:
            mqttc.subscribe(topic.topic)
            self.topic = topic.topic
        self.callback = callback
        if self.topic not in callback_dit:
            cond = threading.Event()
            callback_dit[self.topic] = {'func': self.callback, 'cond': cond, 'msg': None}
        else:
            callback_dit[self.topic]['func'] = self.callback
        topic_list_str_sub = client_id + '_sub:\n'
        for item in callback_dit.keys():
            topic_list_str_sub = '' + topic_list_str_sub + item + '\n'
        if mqttc is not None:
            if mqttc.is_connected():
                mqttc.publish('/topic/' + client_id, retain=True, payload=topic_list_str_pub + topic_list_str_sub)


# 定义一个订阅者类的解释器
class dxr_subscriber:
    def __init__(self, msg):
        # 如果msg的类型是str,则将msg赋值给self.topic
        if isinstance(msg, str):
            self.topic = msg
        else:
            self.topic = msg.topic
        self.func = None

    def __call__(self, func):
        # 将函数绑定到解释器上
        self.func = func
        Dxr_Subscriber(self.topic, self.func)


class Dxr_Publisher:
    def __init__(self, topic):
        global publish_dit, topic_list_str_pub, topic_list_str_sub, callback_dit, mqttc
        if mqttc is None:
            mqttc = Mqtt()
        if isinstance(topic, str):
            self.topic = topic
            self.data_type = None
        else:
            self.topic = topic.topic
            self.data_type = topic
        if self.topic not in publish_dit:
            publish_dit.append(self.topic)
        topic_list_str_pub = client_id + '_pub:\n'
        for item in publish_dit:
            topic_list_str_pub = '' + topic_list_str_pub + item + '\n'
        if mqttc is not None:
            if mqttc.is_connected():
                mqttc.publish('/topic/' + client_id, retain=True, payload=topic_list_str_pub + topic_list_str_sub)

    def publish(self, msg):
        global mqttc
        if mqttc is None:
            mqttc = Mqtt()
        try:
            if self.data_type:
                if mqttc is not None:
                    if mqttc.is_connected():
                        mqttc.publish(self.topic, msg.get_json(), qos=0)
            else:
                if mqttc is not None:
                    if mqttc.is_connected():
                        mqttc.publish(self.topic, json.dumps(msg), qos=0)
        except Exception as ex:
            print(f'publish error: {ex}')

    '''
    使用await_publish来实现消息闭环
    await_publish(msg, timeout, topic)
    {
        msg 为发送的消息
        timeout 不指定的时候，为一直等待设定话题的消息，指定后超时时间中未收到消息，会接收到一个None消息
        topic 为指定闭环消息的话题类型，如果不指定，则默认为原话题类型后追加'_response',可以传递字符串类型的话题，也可以传递消息类型
    }
    '''

    def await_publish(self, msg, timeout=None, topic=None):
        global callback_dit, mqttc
        if mqttc is None:
            mqttc = Mqtt()
        if self.data_type:
            if mqttc is not None:
                if mqttc.is_connected():
                    mqttc.publish(self.topic, msg.get_json(), qos=0)
        else:
            if mqttc is not None:
                if mqttc.is_connected():
                    mqttc.publish(self.topic, json.dumps(msg), qos=0)
        await_topic = None
        if topic is None:
            await_topic = self.topic + '_response'
        else:
            if isinstance(topic, str):
                await_topic = topic
            else:
                await_topic = topic.topic
        if await_topic is None:
            return None
        # print('await_publish: ' + await_topic)
        cond = get_cond(await_topic)
        if cond is None:
            return None
        if timeout is None:
            cond.wait()
        else:
            cond.wait(timeout)
        return callback_dit[await_topic]['msg']


class Dxr_UnSubscriber:
    def __init__(self, topic):
        global callback_dit, mqttc
        if mqttc is None:
            mqttc = Mqtt()
        self.topic = topic
        mqttc.unsubscribe(self.topic)
        callback_dit.pop(self.topic)
