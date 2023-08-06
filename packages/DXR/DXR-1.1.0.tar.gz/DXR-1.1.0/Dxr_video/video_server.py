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
    cap = cv2.VideoCapture(gv.url)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

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
            ret, frame = cap.read()
            if ret != 1:
                continue

            global captureBuffer
            captureBuffer = frame
            time.sleep(0)
            if not gv.server_isStart:
                break

        except KeyboardInterrupt:
            server.stop(0)


def set_url(url):
    gv.url = url


def setPort(port):
    gv.port = port


def start_server():
    gv.server_isStart = True
    threading.Thread(target=serve, daemon=True).start()


def stop_server():
    gv.server_isStart = False


def start_push_server_thread(port):
    gv.push_server_isStart = True
    threading.Thread(target=start_push_server, args=(port,), daemon=True).start()


def stop_push_server_thread():
    gv.push_server_isStart = False


def start_push_server(port):
    # サーバーを生成
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Datas_pb2_grpc.add_MainServerServicer_to_server(Greeter_push_server(), server)
    # ポートを設定
    server.add_insecure_port('[::]:' + str(port))

    # 動作開始
    server.start()

    print('push server start')
    while True:
        try:
            # カメラ映像から読み込み
            global push_queue
            frame = push_queue.get(timeout=0.5)
            global captureBuffer_push_server
            captureBuffer_push_server = frame
            time.sleep(0)
            if not gv.push_server_isStart:
                break

        except KeyboardInterrupt:
            server.stop(0)
        except Exception as ex:
            print(ex)
            continue


def push_frame(frame):
    global captureBuffer_push_server, push_queue
    push_queue.queue.clear()
    push_queue.put(frame)
    # print(captureBuffer_push_server)
    pass

