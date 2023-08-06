import struct

"""
用于进行bytes、bytearray、list数组相关操作
输出统一采用bytearray
"""

# crc16_modbus表
table_crc_hi = (
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
    0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
    0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
    0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
    0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
    0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40,
    0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1,
    0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40)

table_crc_lo = (
    0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06,
    0x07, 0xC7, 0x05, 0xC5, 0xC4, 0x04, 0xCC, 0x0C, 0x0D, 0xCD,
    0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09,
    0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A,
    0x1E, 0xDE, 0xDF, 0x1F, 0xDD, 0x1D, 0x1C, 0xDC, 0x14, 0xD4,
    0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
    0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3,
    0xF2, 0x32, 0x36, 0xF6, 0xF7, 0x37, 0xF5, 0x35, 0x34, 0xF4,
    0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A,
    0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29,
    0xEB, 0x2B, 0x2A, 0xEA, 0xEE, 0x2E, 0x2F, 0xEF, 0x2D, 0xED,
    0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
    0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60,
    0x61, 0xA1, 0x63, 0xA3, 0xA2, 0x62, 0x66, 0xA6, 0xA7, 0x67,
    0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F,
    0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68,
    0x78, 0xB8, 0xB9, 0x79, 0xBB, 0x7B, 0x7A, 0xBA, 0xBE, 0x7E,
    0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
    0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71,
    0x70, 0xB0, 0x50, 0x90, 0x91, 0x51, 0x93, 0x53, 0x52, 0x92,
    0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C,
    0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B,
    0x99, 0x59, 0x58, 0x98, 0x88, 0x48, 0x49, 0x89, 0x4B, 0x8B,
    0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
    0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42,
    0x43, 0x83, 0x41, 0x81, 0x80, 0x40)


# 格式符         C语言类型                 Python类型                Standard_size
# x             pad byte                no value                    -
# c	            char	                string of length 1          1
# b	            signed char	            integer	                    1
# B	            unsigned char	        integer	                    1
# ?	            _Bool	                bool	                    1
# h	            short	                integer	                    2
# H	            unsigned short          integer	                    2
# i	            int	                    integer	                    4
# I(大写的i)	    unsigned int	        integer	                    4
# l(小写的L)	    long                    integer	                    4
# L	            unsigned long	        long	                    4
# q	            long long	            long	                    8
# Q	            unsigned long long      long	                    8
# f	            float	                float	                    4
# d	            double	                float	                    8
# s	            char[]	                string                      -
# p	            char[]	                string                      -
# P	            void *	                long                        -


# Character	    Byte order	    Size	    Alignment
# @(默认)	    本机	            本机	        本机,凑够4字节
# =	            本机	            标准	        none,按原字节数
# <	            小端	            标准	        none,按原字节数
# >	            大端	            标准	        none,按原字节数
# !	            network(大端)	标准	        none,按原字节数

# region 显示功能
# 数组转16进制字符串
def bytes_to_hex_str(bs):
    """ 数组转16进制字符串
    :param bs: bytes、bytearray、list数组
    :return: 2位表示的16进制字符串
    """
    try:
        return ''.join(['%02X ' % b for b in bs])
    except Exception as e:
        print(e)


# 16进制字符串转bytearray数组
def hex_str_to_bytes(str_data):
    """ 16进制字符串转bytearray数组
    :param str_data: 16进制字符串
    :return: 对应bytearray数组
    """
    try:
        return bytearray.fromhex(str_data.replace(" ", ""))
    except Exception as e:
        print(e)


# endregion
# region 从数组获取数据
# 从bytes获取int8
def get_int8_from_bytes(bytes_data, index=0):
    """ 从bytes获取int8
    :param1 bytes_data: 所要读取的数组，bytes、bytearray、list类型
    :param2 index: 所要读取的索引位置，默认为0
    :return: 对应int8值
    """
    try:
        return struct.unpack("b", bytearray([bytes_data[index]]))[0]
    except Exception as e:
        print(e)


# 从bytes获取uint8
def get_uint8_from_bytes(bytes_data, index=0):
    """ 从bytes获取uint8
    :param1 bytes_data: 所要读取的数组，bytes、bytearray、list类型
    :param2 index: 所要读取的索引位置，默认为0
    :return: 对应uint8值
    """
    try:
        return int(struct.unpack("c", bytearray([bytes_data[index]]))[0][0])
    except Exception as e:
        print(e)


# 从bytes获取int16
def get_int16_from_bytes(bytes_data, index=0, order=""):
    """ 从bytes获取int16
    :param1 bytes_data: 所要读取的数组，bytes、bytearray、list类型
    :param2 index: 所要读取的索引位置，默认为0
    :param3 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应int16值
    """
    try:
        if type(bytes_data) != bytearray:
            bytes_data = bytearray(bytes_data)
        if (order is "") or (order.lower() == "little"):
            return struct.unpack("<h", bytes_data[index:index + 2])[0]
        elif order.lower() == "big":
            return struct.unpack(">h", bytes_data[index:index + 2])[0]
        else:
            print("order is not little or big")
    except Exception as e:
        print(e)


# 从bytes获取uint16
def get_uint16_from_bytes(bytes_data, index=0, order=""):
    """ 从bytes获取uint16
    :param1 bytes_data: 所要读取的数组，bytes、bytearray、list类型
    :param2 index: 所要读取的索引位置，默认为0
    :param3 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应uint16值
    """
    try:
        if type(bytes_data) != bytearray:
            bytes_data = bytearray(bytes_data)
        if (order is "") or (order.lower() == "little"):
            return struct.unpack("<H", bytes_data[index:index + 2])[0]
        elif order.lower() == "big":
            return struct.unpack(">H", bytes_data[index:index + 2])[0]
        else:
            print("order is not little or big")
    except Exception as e:
        print(e)


# 从bytes获取int32
def get_int32_from_bytes(bytes_data, index=0, order=""):
    """ 从bytes获取int32
    :param1 bytes_data: 所要读取的数组，bytes、bytearray、list类型
    :param2 index: 所要读取的索引位置，默认为0
    :param3 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应int32值
    """
    try:
        if type(bytes_data) != bytearray:
            bytes_data = bytearray(bytes_data)
        if (order is "") or (order.lower() == "little"):
            return struct.unpack("<i", bytes_data[index:index + 4])[0]
        elif order.lower() == "big":
            return struct.unpack(">i", bytes_data[index:index + 4])[0]
        else:
            print("order is not little or big")
    except Exception as e:
        print(e)


# 从bytes获取uint32
def get_uint32_from_bytes(bytes_data, index=0, order=""):
    """ 从bytes获取uint32
    :param1 bytes_data: 所要读取的数组，bytes、bytearray、list类型
    :param2 index: 所要读取的索引位置，默认为0
    :param3 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应uint32值
    """
    try:
        if type(bytes_data) != bytearray:
            bytes_data = bytearray(bytes_data)
        if (order is "") or (order.lower() == "little"):
            return struct.unpack("<I", bytes_data[index:index + 4])[0]
        elif order.lower() == "big":
            return struct.unpack(">I", bytes_data[index:index + 4])[0]
        else:
            print("order is not little or big")
    except Exception as e:
        print(e)


# 从bytes获取float
def get_float_from_bytes(bytes_data, index=0, order=""):
    """ 从bytes获取float
    :param1 bytes_data: 所要读取的数组，bytes、bytearray、list类型
    :param2 index: 所要读取的索引位置，默认为0
    :param3 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应float值
    """
    try:
        if type(bytes_data) != bytearray:
            bytes_data = bytearray(bytes_data)
        if (order is "") or (order.lower() == "little"):
            return struct.unpack("<f", bytes_data[index:index + 4])[0]
        elif order.lower() == "big":
            return struct.unpack(">f", bytes_data[index:index + 4])[0]
        else:
            print("order is not little or big")
    except Exception as e:
        print(e)


# 从bytes获取double
def get_double_from_bytes(bytes_data, index=0, order=""):
    """ 从bytes获取double
    :param1 bytes_data: 所要读取的数组，bytes、bytearray、list类型
    :param2 index: 所要读取的索引位置，默认为0
    :param3 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应double值
    """
    try:
        if type(bytes_data) != bytearray:
            bytes_data = bytearray(bytes_data)
        if (order is "") or (order.lower() == "little"):
            return struct.unpack("<d", bytes_data[index:index + 4])[0]
        elif order.lower() == "big":
            return struct.unpack(">d", bytes_data[index:index + 4])[0]
        else:
            print("order is not little or big")
    except Exception as e:
        print(e)


# 从bytes获取指定格式数据
def get_data_from_bytes(bytes_data, type="", index=0, order=""):
    """ 从bytes获取指定格式数据
    :param1 bytes_data: 所要读取的数组，bytes、bytearray、list类型
    :param2 type: 所要读取的数据格式，默认为“”，需输入字符串：int8、uint8、int16、uint16、int32、uint32、float、double，不区分大小写
    :param3 index: 所要读取的索引位置，默认为0
    :param4 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应值
    """
    if type.lower() == "":
        print("miss input: type")
        return None
    elif type.lower() == "int8":
        return get_int8_from_bytes(bytes_data, index)
    elif type.lower() == "uint8":
        return get_uint8_from_bytes(bytes_data, index)
    elif type.lower() == "int16":
        return get_int16_from_bytes(bytes_data, index, order)
    elif type.lower() == "uint16":
        return get_uint16_from_bytes(bytes_data, index, order)
    elif type.lower() == "int32":
        return get_int32_from_bytes(bytes_data, index, order)
    elif type.lower() == "float":
        return get_float_from_bytes(bytes_data, index, order)
    elif type.lower() == "double":
        return get_double_from_bytes(bytes_data, index, order)
    else:
        print("error input: type")
        return None


# endregion
# region 将数据加入数组
# 加入int8至bytes
def add_int8_to_bytes(bytes_data, value, index=None):
    """ 加入int8至bytes
    :param1 bytes_data: 所要加入的数组，bytes、bytearray、list类型
    :param2 value: 所要加入的对象，int8类型
    :param3 index: 所要加入的索引位置，默认为最后
    :return: 对应bytearray结果
    """
    try:
        if value > 127 or value < -128:
            print("value is not between -128~127, input do not change")
            return bytes_data
        if type(bytes_data) != bytearray:
            bytes_data = bytearray(bytes_data)
        if index is not None:
            bytes_data[index] = struct.pack("b", value)[0]
        else:
            bytes_data.append(struct.pack("b", value)[0])
        return bytes_data
    except Exception as e:
        print(e)
        return bytes_data


# 加入uint8至bytes
def add_uint8_to_bytes(bytes_data, value, index=None):
    """ 加入uint8至bytes
    :param1 bytes_data: 所要加入的数组，bytes、bytearray、list类型
    :param2 value: 所要加入的对象，uint8类型
    :param3 index: 所要加入的索引位置，默认为最后
    :return: 对应bytearray结果
    """
    try:
        if value > 0xFF or value < 0:
            print("value is not between 0~255, input do not change")
            return bytes_data
        if type(bytes_data) != bytearray:
            bytes_data = bytearray(bytes_data)
        if index is not None:
            bytes_data[index] = struct.pack("b", value)[0]
        else:
            bytes_data.append(struct.pack("b", value)[0])
        return bytes_data
    except Exception as e:
        print(e)
        return bytes_data


# 加入int16至bytes
def add_int16_to_bytes(bytes_data, value, index=None, order=""):
    """ 加入int16至bytes
    :param1 bytes_data: 所要加入的数组，bytes、bytearray、list类型
    :param2 value: 所要加入的对象，int16类型
    :param3 index: 所要加入的索引位置，默认为最后
    :param4 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应bytearray结果
    """
    try:
        if (type(value) != int) or (value > 32767 or value < -32768):
            print("type of value or value is error, input do not change")
            return bytes_data
        if type(bytes_data) != bytearray:
            bytes_data = bytearray(bytes_data)
        temp_bytes = bytearray()
        if (order is "") or (order.lower() == "little"):
            temp_bytes = struct.pack("<h", value)
        elif order.lower() == "big":
            temp_bytes = struct.pack(">h", value)
        else:
            print("order is not little or big")
        for x in range(2):
            if index is not None:
                bytes_data[index + x] = temp_bytes[x]
            else:
                bytes_data.append(temp_bytes[x])
        return bytes_data
    except Exception as e:
        print(e)
        return bytes_data


# 加入uint16至bytes
def add_uint16_to_bytes(bytes_data, value, index=None, order=""):
    """ 加入uint16至bytes
    :param1 bytes_data: 所要加入的数组，bytes、bytearray、list类型
    :param2 value: 所要加入的对象，uint16类型
    :param3 index: 所要加入的索引位置，默认为最后
    :param4 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应bytearray结果
    """
    try:
        if (type(value) != int) or (value > 65535 or value < 0):
            print("type of value is error, input do not change")
            return bytes_data
        if type(bytes_data) != bytearray:
            bytes_data = bytearray(bytes_data)
        temp_bytes = bytearray()
        if (order is "") or (order.lower() == "little"):
            temp_bytes = struct.pack("<H", value)
        elif order.lower() == "big":
            temp_bytes = struct.pack(">H", value)
        else:
            print("order is not little or big")
        for x in range(2):
            if index is not None:
                bytes_data[index + x] = temp_bytes[x]
            else:
                bytes_data.append(temp_bytes[x])
        return bytes_data
    except Exception as e:
        print(e)
        return bytes_data


# 加入int32至bytes
def add_int32_to_bytes(bytes_data, value, index=None, order=""):
    """ 加入int32至bytes
    :param1 bytes_data: 所要加入的数组，bytes、bytearray、list类型
    :param2 value: 所要加入的对象，int32类型
    :param3 index: 所要加入的索引位置，默认为最后
    :param4 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应bytearray结果
    """
    try:
        if type(value) != int:
            print("type of value is error, input do not change")
            return bytes_data
        if type(bytes_data) != bytearray:
            bytes_data = bytearray(bytes_data)
        temp_bytes = bytearray()
        if (order is "") or (order.lower() == "little"):
            temp_bytes = struct.pack("<i", value)
        elif order.lower() == "big":
            temp_bytes = struct.pack(">i", value)
        else:
            print("order is not little or big")
        for x in range(4):
            if index is not None:
                bytes_data[index + x] = temp_bytes[x]
            else:
                bytes_data.append(temp_bytes[x])
        return bytes_data
    except Exception as e:
        print(e)
        return bytes_data


# 加入uint32至bytes
def add_uint32_to_bytes(bytes_data, value, index=None, order=""):
    """ 加入uint32至bytes
    :param1 bytes_data: 所要加入的数组，bytes、bytearray、list类型
    :param2 value: 所要加入的对象，uint32类型
    :param3 index: 所要加入的索引位置，默认为最后
    :param4 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应bytearray结果
    """
    try:
        if type(value) != int:
            print("type of value is error, input do not change")
            return bytes_data
        if type(bytes_data) != bytearray:
            bytes_data = bytearray(bytes_data)
        temp_bytes = bytearray()
        if (order is "") or (order.lower() == "little"):
            temp_bytes = struct.pack("<I", value)
        elif order.lower() == "big":
            temp_bytes = struct.pack(">I", value)
        else:
            print("order is not little or big")
        for x in range(4):
            if index is not None:
                bytes_data[index + x] = temp_bytes[x]
            else:
                bytes_data.append(temp_bytes[x])
        return bytes_data
    except Exception as e:
        print(e)
        return bytes_data


# 加入float至bytes
def add_float_to_bytes(bytes_data, value, index=None, order=""):
    """ 加入float至bytes
    :param1 bytes_data: 所要加入的数组，bytes、bytearray、list类型
    :param2 value: 所要加入的对象，float、int类型
    :param3 index: 所要加入的索引位置，默认为最后
    :param4 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应bytearray结果
    """
    try:
        if (type(value) != float) and (type(value) != int):
            print("type of value is error, input do not change")
            return bytes_data
        if type(bytes_data) != bytearray:
            bytes_data = bytearray(bytes_data)
        temp_bytes = bytearray()
        if (order is "") or (order.lower() == "little"):
            temp_bytes = struct.pack("<f", float(value))
        elif order.lower() == "big":
            temp_bytes = struct.pack(">f", float(value))
        else:
            print("order is not little or big")
        for x in range(4):
            if index is not None:
                bytes_data[index + x] = temp_bytes[x]
            else:
                bytes_data.append(temp_bytes[x])
        return bytes_data
    except Exception as e:
        print(e)
        return bytes_data


# 加入double至bytes
def add_double_to_bytes(bytes_data, value, index=None, order=""):
    """ 加入float至bytes
    :param1 bytes_data: 所要加入的数组，bytes、bytearray、list类型
    :param2 value: 所要加入的对象，double、int类型
    :param3 index: 所要加入的索引位置，默认为最后
    :param4 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应bytearray结果
    """
    try:
        if (type(value) != float) and (type(value) != int):
            print("type of value is error, input do not change")
            return bytes_data
        if type(bytes_data) != bytearray:
            bytes_data = bytearray(bytes_data)
        temp_bytes = bytearray()
        if (order is "") or (order.lower() == "little"):
            temp_bytes = struct.pack("<d", float(value))
        elif order.lower() == "big":
            temp_bytes = struct.pack(">d", float(value))
        else:
            print("order is not little or big")
        for x in range(8):
            if index is not None:
                bytes_data[index + x] = temp_bytes[x]
            else:
                bytes_data.append(temp_bytes[x])
        return bytes_data
    except Exception as e:
        print(e)
        return bytes_data


# endregion
# region 将数据转换数组
# 获得int8对应bytearray
def get_int8_bytes(value):
    """ 获得int8对应bytearray
    :param1 value: 所要获取的对象，int8类型
    :return: 对应bytearray结果
    """
    try:
        if value > 127 or value < -128:
            print("value is not between 0~255, do not get bytes")
            return
        bytes_data = bytearray()
        bytes_data.append(struct.pack("b", value)[0])
        return bytes_data
    except Exception as e:
        print(e)
        return


# 获得uint8对应bytearray
def get_uint8_bytes(value):
    """ 获得uint8对应bytearray
    :param1 value: 所要获取的对象，uint8类型
    :return: 对应bytearray结果
    """
    try:
        if value > 0xFF or value < 0:
            print("value is not between 0~255, do not get bytes")
            return
        bytes_data = bytearray()
        bytes_data.append(value)
        return bytes_data
    except Exception as e:
        print(e)
        return


# 获得int16对应bytearray
def get_int16_bytes(value, order=""):
    """ 获得int16对应bytearray
    :param1 value: 所要获取的对象，int16类型
    :param2 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应bytearray结果
    """
    try:
        if (type(value) != int) or (value > 32767 or value < -32768):
            print("type of value or value is error, do not get bytes")
            return
        if (order is "") or (order.lower() == "little"):
            bytes_data = bytearray(struct.pack("<h", value))
        elif order.lower() == "big":
            bytes_data = bytearray(struct.pack(">h", value))
        else:
            print("order is not little or big")
            return
        return bytes_data
    except Exception as e:
        print(e)
        return


# 获得uint16对应bytearray
def get_uint16_bytes(value, order=""):
    """ 获得uint16对应bytearray
    :param1 value: 所要获取的对象，uint16类型
    :param2 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应bytearray结果
    """
    try:
        if (type(value) != int) or (value > 65535 or value < 0):
            print("type of value or value is error, do not get bytes")
            return
        if (order is "") or (order.lower() == "little"):
            bytes_data = bytearray(struct.pack("<H", value))
        elif order.lower() == "big":
            bytes_data = bytearray(struct.pack(">H", value))
        else:
            print("order is not little or big")
            return
        return bytes_data
    except Exception as e:
        print(e)
        return


# 获得int32对应bytearray
def get_int32_bytes(value, order=""):
    """ 获得int32对应bytearray
    :param1 value: 所要获取的对象，int32类型
    :param2 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应bytearray结果
    """
    try:
        if (type(value) != int) or (value > 2147483647 or value < -2147483648):
            print("type of value or value is error, do not get bytes")
            return
        if (order is "") or (order.lower() == "little"):
            bytes_data = bytearray(struct.pack("<i", value))
        elif order.lower() == "big":
            bytes_data = bytearray(struct.pack(">i", value))
        else:
            print("order is not little or big")
            return
        return bytes_data
    except Exception as e:
        print(e)
        return


# 获得uint32对应bytearray
def get_uint32_bytes(value, order=""):
    """ 获得uint32对应bytearray
    :param1 value: 所要获取的对象，uint32类型
    :param2 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应bytearray结果
    """
    try:
        if (type(value) != int) or (value > 4294967295 or value < 0):
            print("type of value or value is error, do not get bytes")
            return
        if (order is "") or (order.lower() == "little"):
            bytes_data = bytearray(struct.pack("<I", value))
        elif order.lower() == "big":
            bytes_data = bytearray(struct.pack(">I", value))
        else:
            print("order is not little or big")
            return
        return bytes_data
    except Exception as e:
        print(e)
        return


# 获得float对应bytearray
def get_float_bytes(value, order=""):
    """ 获得float对应bytearray
    :param1 value: 所要获取的对象，float、int类型
    :param2 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应bytearray结果
    """
    try:
        if (type(value) != float) and (type(value) != int):
            print("type of value or value is error, do not get bytes")
            return
        if (order is "") or (order.lower() == "little"):
            bytes_data = bytearray(struct.pack("<f", float(value)))
        elif order.lower() == "big":
            bytes_data = bytearray(struct.pack(">f", float(value)))
        else:
            print("order is not little or big")
            return
        return bytes_data
    except Exception as e:
        print(e)
        return


# 获得double对应bytearray
def get_double_bytes(value, order=""):
    """ 获得float对应bytearray
    :param1 value: 所要获取的对象，double、int类型
    :param2 order: 大小端，默认为小端，输入"big"或”little“
    :return: 对应bytearray结果
    """
    try:
        if (type(value) != float) and (type(value) != int):
            print("type of value or value is error, do not get bytes")
            return
        if (order is "") or (order.lower() == "little"):
            bytes_data = bytearray(struct.pack("<d", float(value)))
        elif order.lower() == "big":
            bytes_data = bytearray(struct.pack(">d", float(value)))
        else:
            print("order is not little or big")
            return
        return bytes_data
    except Exception as e:
        print(e)
        return


# endregion
# region crc16_modbus功能
# bytes加入crc16_modbus
def bytes_add_crc16_modbus(bytes_data, start_index=0, front=""):
    """ bytes加入crc16_modbus
    :param1 bytes_data: 所需加入CRC校验码的数组，bytes、bytearray、list类型
    :param2 start_index: 所需计算CRC校验码的开始索引，默认为0
    :param3 front: CRC校验码低位还是高位在前，默认低位在前，输入"low"或”high“
    :return: 对应bytearray结果
    """
    if type(bytes_data) != bytearray:
        bytes_data = bytearray(bytes_data)
    temp = crc16_modbus_bytes(bytes_data, start_index)
    if (front is "") or (front.lower() == "low"):
        bytes_data.append(temp[0])
        bytes_data.append(temp[1])
    elif front.lower() == "high":
        bytes_data.append(temp[1])
        bytes_data.append(temp[0])
    else:
        print("front is not low or high")
        return
    return bytes_data


# crc16_modbus返回int16
def crc16_modbus_int16(bytes_data, start_index=0):
    """ bytes加入crc16_modbus
    :param1 bytes_data: 所需加入CRC校验码的数组，bytes、bytearray、list类型
    :param2 start_index: 所需计算CRC校验码的开始索引，默认为0
    :return: CRC16数值 int16结果
    """
    crc_hi = crc_lo = 0xFF
    for ch in bytes_data[start_index:]:
        i = crc_hi ^ ch
        crc_hi = crc_lo ^ table_crc_hi[i]
        crc_lo = table_crc_lo[i]
    result = crc_hi << 8 | crc_lo
    print([crc_hi, crc_lo])
    return result


# crc16_modbus返回[crc_L,crc_H]
def crc16_modbus_bytes(bytes_data, start_index=0):
    """ bytes加入crc16_modbus
    :param1 bytes_data: 所需加入CRC校验码的数组，bytes、bytearray、list类型
    :param2 start_index: 所需计算CRC校验码的开始索引，默认为0
    :return: CRC16数值 bytearray结果[crc_L,crc_H]
    """
    crc_hi = crc_lo = 0xFF
    for ch in bytes_data[start_index:]:
        i = crc_hi ^ ch
        crc_hi = crc_lo ^ table_crc_hi[i]
        crc_lo = table_crc_lo[i]
    result = bytearray()
    result.append(crc_hi)
    result.append(crc_lo)
    return result


# endregion
# region 其他功能
# 返回帧头
def find_head(bytes_data, head_data):
    """ bytes加入crc16_modbus
    :param1 bytes_data: 所需寻找帧头的数组，bytes、bytearray、list类型
    :param2 head_data: 所需寻找的帧头，bytes、bytearray、list类型
    :return: 帧头的索引
    """
    try:
        if type(bytes_data) != bytearray:
            bytes_data = bytearray(bytes_data)
        if type(head_data) != bytearray:
            head_data = bytearray(head_data)
        num = len(head_data)
        for x in range(len(bytes_data) - num):
            if bytes_data[x:x + num] == head_data:
                return x
        return None
    except Exception as e:
        print(e)
        return None


# endregion

# 测试代码
if __name__ == '__main__':
    input_data = [0x01, 0x03, 0x00, 0x01, 0x00, 0x01]
    print("*" * 50)
    print(bytes_to_hex_str(input_data))
    print(bytes_to_hex_str(crc16_modbus_bytes(input_data)))
    print(crc16_modbus_int16(input_data))
    print("*" * 50)
    print(bytes_to_hex_str(bytes_add_crc16_modbus(input_data, front="low")))
    pass
