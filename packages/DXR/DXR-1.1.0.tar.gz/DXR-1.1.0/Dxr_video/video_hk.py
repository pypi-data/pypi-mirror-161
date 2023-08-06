# カメラ映像を接続されたクライアントに送信する

# ============================================================
# import packages
# ============================================================
import queue
import threading
from concurrent import futures
import grpc
from . import Datas_pb2
from . import Datas_pb2_grpc
import time
import cv2
import base64
import sys
from . import global_values as gv
from . import test_main

# ============================================================
# property
# ============================================================
# カメラを設定


captureBuffer = None
captureBuffer_push_server = None
push_queue = queue.Queue(maxsize=1)


# ============================================================
# class
# ============================================================
# サーバークラス
class Greeter(Datas_pb2_grpc.MainServerServicer):

    # ==========
    def __init__(self):
        pass

    # ==========
    def getStream(self, request_iterator, context):

        for req in request_iterator:

            # リクエストメッセージを表示
            print("request message = ", req.msg)

            while True:
                ret, buf = cv2.imencode('.jpg', captureBuffer)
                if ret != 1:
                    return

                # データを送信
                yield Datas_pb2.Reply(datas=buf.tobytes())

                # 60FPSに設定
                time.sleep(1 / 60)


# ============================================================
# class
# ============================================================
# サーバークラス
class Greeter_push_server(Datas_pb2_grpc.MainServerServicer):

    # ==========
    def __init__(self):
        pass

    # ==========
    def getStream(self, request_iterator, context):

        for req in request_iterator:

            # リクエストメッセージを表示
            print("request message = ", req.msg)

            while True:
                global captureBuffer_push_server
                # print(captureBuffer_push_server)
                ret, buf = cv2.imencode('.jpg', captureBuffer_push_server)
                if ret != 1:
                    return

                # データを送信
                yield Datas_pb2.Reply(datas=buf.tobytes())

                # 60FPSに設定
                time.sleep(1 / 60)


# ============================================================
# functions
# ============================================================
def serve():
    # cap = cv2.VideoCapture(gv.url)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # サーバーを生成
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Datas_pb2_grpc.add_MainServerServicer_to_server(Greeter(), server)

    # ポートを設定
    server.add_insecure_port('[::]:' + str(gv.port))

    # 動作開始
    server.start()

    print('server start')

    while True:
        try:
            # カメラ映像から読み込み
            frame = gv.video_que.get(timeout=3)
            global captureBuffer
            captureBuffer = frame
            time.sleep(0)
            if not gv.server_isStart:
                break
        except KeyboardInterrupt:
            # server.stop(0)
            pass


def set_url(url):
    gv.url = url


def setPort(port):
    gv.port = port
    
    
def setHik_IP(ip):
    gv.hik_ip = ip
    

def setHik_Username(username):
    gv.hik_username = username
    

def setHik_Password(password):
    gv.hik_password = password


def start_server():
    gv.server_isStart = True
    gv.is_hk_start = True
    threading.Thread(target=test_main.start_hik_sdk).start()
    threading.Thread(target=serve, daemon=True).start()


def stop_server():
    gv.server_isStart = False
    

