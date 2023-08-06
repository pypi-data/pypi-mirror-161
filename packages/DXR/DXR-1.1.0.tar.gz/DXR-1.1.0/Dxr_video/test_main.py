# coding=utf-8

import os
import platform
import time
from tkinter.messagebox import NO

import cv2
from .HCNetSDK import *
from .PlayCtrl import *
from time import sleep
from . import global_values as gv
Objdll = None
# 登录的设备信息
DEV_IP = None
DEV_PORT = 8000
DEV_USER_NAME = None
DEV_PASSWORD = create_string_buffer(b'Asb11023')

WINDOWS_FLAG = True
win = None  # 预览窗口
funcRealDataCallBack_V30 = None  # 实时预览回调函数，需要定义为全局的
PlayCtrl_Port = c_long(-1)  # 播放句柄
Playctrldll = None  # 播放库
FuncDecCB = None   # 播放库解码回调函数，需要定义为全局的

# 获取当前系统环境
def GetPlatform():
    sysstr = platform.system()
    print('' + sysstr)
    if sysstr != "Windows":
        global WINDOWS_FLAG
        WINDOWS_FLAG = False

# 设置SDK初始化依赖库路径
def SetSDKInitCfg():
    global Objdll
    # 设置HCNetSDKCom组件库和SSL库加载路径
    # print(os.getcwd())
    if WINDOWS_FLAG:
        strPath = os.getcwd().encode('gbk')
        sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
        sdk_ComPath.sPath = strPath
        Objdll.NET_DVR_SetSDKInitCfg(2, byref(sdk_ComPath))
        Objdll.NET_DVR_SetSDKInitCfg(3, create_string_buffer(strPath + b'\libcrypto-1_1-x64.dll'))
        Objdll.NET_DVR_SetSDKInitCfg(4, create_string_buffer(strPath + b'\libssl-1_1-x64.dll'))
    else:
        strPath = os.getcwd().encode('utf-8')
        sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
        sdk_ComPath.sPath = strPath
        Objdll.NET_DVR_SetSDKInitCfg(2, byref(sdk_ComPath))
        Objdll.NET_DVR_SetSDKInitCfg(3, create_string_buffer(strPath + b'/libcrypto.so.1.1'))
        Objdll.NET_DVR_SetSDKInitCfg(4, create_string_buffer(strPath + b'/libssl.so.1.1'))

def LoginDev(Objdll):
    # 登录注册设备
    device_info = NET_DVR_DEVICEINFO_V30()
    lUserId = Objdll.NET_DVR_Login_V30(DEV_IP, DEV_PORT, DEV_USER_NAME, DEV_PASSWORD, byref(device_info))
    return (lUserId, device_info)

def DecCBFun(nPort, pBuf, nSize, pFrameInfo, nUser, nReserved2):
    # 解码回调函数
    if pFrameInfo.contents.nType == 3:
        # print('get frame' + str(time.time()))
        # 解码返回视频YUV数据，将YUV数据转成jpg图片保存到本地
        # 如果有耗时处理，需要将解码数据拷贝到回调函数外面的其他线程里面处理，避免阻塞回调导致解码丢帧
        sFileName = ('../../pic/test_stamp.jpg')
        nWidth = pFrameInfo.contents.nWidth
        nHeight = pFrameInfo.contents.nHeight
        nType = pFrameInfo.contents.nType
        dwFrameNum = pFrameInfo.contents.dwFrameNum
        nStamp = pFrameInfo.contents.nStamp
        # print(nWidth, nHeight, nType, dwFrameNum, nStamp, sFileName)

        lRet = Playctrldll.PlayM4_ConvertToJpegFile(pBuf, nSize, nWidth, nHeight, nType, c_char_p(sFileName.encode()))
        if lRet == 0:
            print('PlayM4_ConvertToJpegFile fail, error code is:', Playctrldll.PlayM4_GetLastError(nPort))
        else:
            print('PlayM4_ConvertToJpegFile success' + str(time.time()))
            gv.video_que.queue.clear()
            gv.video_que.put(cv2.imread(sFileName))

def RealDataCallBack_V30(lPlayHandle, dwDataType, pBuffer, dwBufSize, pUser):
    # 码流回调函数
    if dwDataType == NET_DVR_SYSHEAD:
        # 设置流播放模式
        Playctrldll.PlayM4_SetStreamOpenMode(PlayCtrl_Port, 0)
        # 打开码流，送入40字节系统头数据
        if Playctrldll.PlayM4_OpenStream(PlayCtrl_Port, pBuffer, dwBufSize, 1024*1024):
            # 设置解码回调，可以返回解码后YUV视频数据
            global FuncDecCB
            FuncDecCB = DECCBFUNWIN(DecCBFun)
            Playctrldll.PlayM4_SetDecCallBackExMend(PlayCtrl_Port, FuncDecCB, None, 0, None)
            # 开始解码播放
            if Playctrldll.PlayM4_Play(PlayCtrl_Port, None):
                print(u'播放库播放成功')
            else:
                print(u'播放库播放失败')
        else:
            print(u'播放库打开流失败')
    elif dwDataType == NET_DVR_STREAMDATA:
        Playctrldll.PlayM4_InputData(PlayCtrl_Port, pBuffer, dwBufSize)
    else:
        print (u'其他数据,长度:', dwBufSize)

def OpenPreview(Objdll, lUserId, callbackFun):
    '''
    打开预览
    '''
    preview_info = NET_DVR_PREVIEWINFO()
    preview_info.hPlayWnd = 0
    preview_info.lChannel = 1  # 通道号
    preview_info.dwStreamType = 0  # 主码流
    preview_info.dwLinkMode = 0  # TCP
    preview_info.bBlocked = 1  # 阻塞取流

    # 开始预览并且设置回调函数回调获取实时流数据
    lRealPlayHandle = Objdll.NET_DVR_RealPlay_V40(lUserId, byref(preview_info), callbackFun, None)
    return lRealPlayHandle

def InputData(fileMp4, Playctrldll):
    while True:
        pFileData = fileMp4.read(4096)
        if pFileData is None:
            break

        if not Playctrldll.PlayM4_InputData(PlayCtrl_Port, pFileData, len(pFileData)):
            break

def start_hik_sdk():
    global Objdll, PlayCtrl_Port, Playctrldll, DEV_IP,  DEV_USER_NAME
    DEV_IP = create_string_buffer(bytes(gv.hik_ip, encoding='utf-8'))
    DEV_PASSWORD = create_string_buffer(bytes(gv.hik_password, encoding='utf-8'))
    DEV_USER_NAME = create_string_buffer(bytes(gv.hik_username, encoding='utf-8'))
    
    # 获取系统平台
    GetPlatform()
    path = os.path.abspath(__file__)
    path = path.replace('test_main.py', '')
    path += 'lib/linux'
    print(path)
    os.chdir(path)
    Objdll = cdll.LoadLibrary(r'./libhcnetsdk.so')
    Playctrldll = cdll.LoadLibrary(r'./libPlayCtrl.so')
    SetSDKInitCfg()  # 设置组件库和SSL库加载路径
    # 初始化DLL
    Objdll.NET_DVR_Init()
    # 启用SDK写日志
    Objdll.NET_DVR_SetLogToFile(3, bytes('./SdkLog_Python/', encoding="utf-8"), False)
    # 获取一个播放句柄
    if not Playctrldll.PlayM4_GetPort(byref(PlayCtrl_Port)):
        print(u'获取播放库句柄失败')

    # 登录设备
    (lUserId, device_info) = LoginDev(Objdll)
    if lUserId < 0:
        err = Objdll.NET_DVR_GetLastError()
        print('Login device fail, error code is: %d' % Objdll.NET_DVR_GetLastError())
        # 释放资源
        Objdll.NET_DVR_Cleanup()
        exit()

    # 定义码流回调函数
    funcRealDataCallBack_V30 = REALDATACALLBACK(RealDataCallBack_V30)
    # 开启预览
    lRealPlayHandle = OpenPreview(Objdll, lUserId, funcRealDataCallBack_V30)
    if lRealPlayHandle < 0:
        print ('Open preview fail, error code is: %d' % Objdll.NET_DVR_GetLastError())
        # 登出设备
        Objdll.NET_DVR_Logout(lUserId)
        # 释放资源
        Objdll.NET_DVR_Cleanup()
        exit()

    #show Windows
    # win.mainloop()
    while gv.is_hk_start:
        time.sleep(1)
    # # 开始云台控制
    # lRet = Objdll.NET_DVR_PTZControl(lRealPlayHandle, PAN_LEFT, 0)
    # if lRet == 0:
    #     print ('Start ptz control fail, error code is: %d' % Objdll.NET_DVR_GetLastError())
    # else:
    #     print ('Start ptz control success')

    # # 转动一秒
    # sleep(1)

    # # 停止云台控制
    # lRet = Objdll.NET_DVR_PTZControl(lRealPlayHandle, PAN_LEFT, 1)
    # if lRet == 0:
    #     print('Stop ptz control fail, error code is: %d' % Objdll.NET_DVR_GetLastError())
    # else:
    #     print('Stop ptz control success')

    # 关闭预览
    Objdll.NET_DVR_StopRealPlay(lRealPlayHandle)

    # 停止解码，释放播放库资源
    if PlayCtrl_Port.value > -1:
        Playctrldll.PlayM4_Stop(PlayCtrl_Port)
        Playctrldll.PlayM4_CloseStream(PlayCtrl_Port)
        Playctrldll.PlayM4_FreePort(PlayCtrl_Port)
        PlayCtrl_Port = c_long(-1)

    # 登出设备
    Objdll.NET_DVR_Logout(lUserId)

    # 释放资源
    Objdll.NET_DVR_Cleanup()

