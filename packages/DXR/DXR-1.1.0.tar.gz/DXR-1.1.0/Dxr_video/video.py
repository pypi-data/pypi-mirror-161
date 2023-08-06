from concurrent import futures
import re
import threading
import time
import cv2
import grpc
import base64
import numpy as np
from . import Datas_pb2
from . import Datas_pb2_grpc
import sys
import cv2
from . import global_values as gv


def setIP(ip):
    gv.ip = ip


def setPort(port):
    gv.port = port


def start_run():
    gv.isStart = True
    threading.Thread(target=run, daemon=True).start()


def run():
    # サーバーの宛先
    channel = grpc.insecure_channel(gv.ip + ':' + str(gv.port))
    stub = Datas_pb2_grpc.MainServerStub(channel)

    try:

        # リクエストデータを作成
        message = [Datas_pb2.Request(msg='give me the stream!!')]
        responses = stub.getStream(iter(message))

        for res in responses:
            # print(res.datas)

            # 画像を文字列などで扱いたい場合
            # b64d = base64.b64decode(res.datas)

            # バッファを作成
            dBuf = np.frombuffer(res.datas, dtype=np.uint8)

            # 作成したバッファにデータを入れる
            dst = cv2.imdecode(dBuf, cv2.IMREAD_COLOR)
            gv.video_que.queue.clear()
            gv.video_que.put(dst)
            if not gv.isStart:
                break

    except grpc.RpcError as e:
        gv.isStart = False
        print(e.details())


def get_frame():
    try:
        frame = gv.video_que.get(timeout=0.5)
        return 1, frame
    except Exception as ex:
        print(ex)
        return 0, None


def get_status():
    return gv.isStart


def start_get_frame_from_url_thread(url):
    if not gv.isStart_from_url:
        gv.isStart_from_url = True
        threading.Thread(target=start_get_frame_from_url, args=(url,), daemon=True).start()


def start_get_frame_from_url(url):
    cap = cv2.VideoCapture(gv.url)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while gv.isStart_from_url:
        ret, frame = cap.read()
        gv.video_from_url_que.queue.clear()
        gv.video_from_url_que.put(frame)


def get_frame_from_url_status():
    return gv.isStart_from_url


def get_frame_from_url():
    try:
        frame = gv.video_from_url_que.get(timeout=0.5)
        return 1, frame
    except Exception as ex:
        print(ex)
        return 0, None


def stop_get_frame_from_url():
    gv.isStart_from_url = False
