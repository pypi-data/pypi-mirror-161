# -*- encoding=utf-8 -*-
import abc
import re
from .protocol import ProtocolDefine
from . import LOGGER


class BaseHandler(metaclass=abc.ABCMeta):
    """
    自定义协议处理类，需继承BaseHandler
    并覆写其中的以下方法：
    parseResponse：解析出协议里的orderCode 和 定义的数据段
    checkRawData： 自定义返回数据校验
    modifyCmd： 自定义发送指令
    """
    def __init__(self):
        self.protocolDefine = None
        self.protocolDefineRequest = None
        self.protocolDefineResponse = None

    def init(self):
        if self.protocolName in ProtocolDefine:
            self.protocolDefine = ProtocolDefine.get(self.protocolName)
            self.protocolDefineRequest = self.protocolDefine.get("request")
            self.protocolDefineResponse = self.protocolDefine.get("response")

    def canHandle(self, data):
        responsePattern = self.protocolDefine["responsePattern"]
        if re.search(responsePattern, data):
            rawData = re.search(responsePattern, data).group()
            return self.checkRawData(rawData)
        else:
            return False

    def checkRawData(self, rawData):
        """
        协议自定义数据校验方法
        :param rawData:根据协议定义匹配到的原始字节
        :return:True 校验通过
                False 校验不通过
        """
        return True if rawData is not None else False

    @abc.abstractmethod
    def parseResponse(self, data):
        """
        从原始返回数据中解析出对应protocol里定义的指令号，
        若协议定义规范，可将数据主体交由baseHandler，按协议定义的字段解析
        :param data:从协议栈收上来的数据，未经过模式匹配。
        :return:返回 经过解析的数据
        """
        pass

    def haveOrder(self, orderName):
        return orderName in self.protocolDefineRequest

    def parseCmd(self, orderName, *args):
        if orderName not in self.protocolDefineRequest:
            return None

        cmdDefine = self.protocolDefineRequest[orderName]["cmd"]
        argsDefine = self.protocolDefineRequest[orderName]["args"]

        if len(args) != len(argsDefine):
            LOGGER.logger.debug("arg num dismatch: got %s(%s)" %
                                (orderName, args))

        parsedCmd = bytearray()
        argMap = {}
        rIndex = 0
        argList = list(args)

        for ad in argsDefine:
            index = ad["index"]
            if rIndex < index:
                parsedCmd.extend(cmdDefine[rIndex:index])
            if isinstance(ad["length"], int):
                length = ad["length"]
                rIndex = index + length
            elif ad["length"] in argMap:
                length = argMap[ad["length"]]
                rIndex = index + 1
            else:
                LOGGER.logger("invalid argsDefine(%s:%s)" %
                              (self.protocolName, orderName))
                return None

            arg = argList.pop(0)
            argMap[ad["argName"]] = arg
            try:
                argBytes = arg.to_bytes(length=length,
                                        byteorder='big',
                                        signed=False)
            except Exception:
                LOGGER.logger("int to bytes error(%d, len:%d)" % (arg, length))
                return None
            parsedCmd.extend(argBytes)
        parsedCmd.extend(cmdDefine[rIndex:])
        parsedCmd = self.modifyCmd(parsedCmd)
        resultCmd = bytes(parsedCmd)
        LOGGER.logger.debug("parsedCmd(%s)" % resultCmd.hex())
        return resultCmd

    def modifyCmd(self, rawCmd):
        """
        给子类一个定制修改指令的接入点
        :param rawCmd: bytearray类型，已按照protocol的定义填充数据。
        :return:返回 经过定制修改的bytearray类型数据
        """
        return rawCmd

    def parseData(self, orderCode, response):
        result = {}
        if orderCode not in self.protocolDefineResponse:
            LOGGER.logger.debug("orderCode(%02x) not found in (%s)" %
                                (orderCode, self.protocolName))
            return None

        # 检查并解析数据
        orderDefine = self.protocolDefineResponse[orderCode]
        orderName = orderDefine["orderName"]
        dataDefine = orderDefine["dataDefine"]
        dataMap = {}
        index = 0
        for dd in dataDefine:
            if isinstance(dd["length"], int):
                length = dd["length"]
            elif dd["length"] in dataMap:
                length = dataMap[dd["length"]]
            if length < 0 or index + length > len(response):
                LOGGER.logger.debug("parsedData on fail, out of index:%s" %
                                    dataMap)
                dataMap = None
                break
            elif length == 0:
                continue
            if length == 1:
                dataMap[dd["fieldName"]] = response[index]
            else:
                dataMap[dd["fieldName"]] = int.from_bytes(
                    response[index:index + length],
                    byteorder='big',
                    signed=False)
            index = index + length
        if index != len(response):
            LOGGER.logger.debug(
                "parsedData on fail, remain data unresolved:%s" % dataMap)
            dataMap = None

        result["orderName"] = orderName
        result["data"] = dataMap
        LOGGER.logger.debug("parsedData:%s" % result)
        return result


class K210ProtocolHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.protocolName = "K210"
        self.init()

    def parseResponse(self, data):
        pattern = self.protocolDefine["responsePattern"]
        response = re.search(pattern, data).group(1)
        orderCode = response[0]
        return self.parseData(orderCode, response[1:])


class K12ProtocolHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.protocolName = "K12"
        self.init()

    # insert CRC check here
    def checkRawData(self, rawData):
        if rawData is not None:
            return CRC16.check_crc(rawData)
        return False

    #  从原始返回数据中解析出对应protocol里定义的指令号
    #  并将数据主体交由baseHandler，按协议定义的返回字段解析
    def parseResponse(self, data):
        pattern = self.protocolDefine["responsePattern"]
        response = re.search(pattern, data).group(1)
        orderCode = response[1]
        return self.parseData(orderCode, response)

    # 如果标准的指令生成无法满足要求，覆写modifyCmd以在自动生成cmd后再定制修改
    def modifyCmd(self, rawCmd):
        return CRC16.create_array(rawCmd[:-2])


# CRC 校验数据完整性
class CRC16(object):
    tableCRCHigh = [
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
        0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40
    ]

    tableCRCLow = [
        0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06, 0x07, 0xC7,
        0x05, 0xC5, 0xC4, 0x04, 0xCC, 0x0C, 0x0D, 0xCD, 0x0F, 0xCF, 0xCE, 0x0E,
        0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09, 0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9,
        0x1B, 0xDB, 0xDA, 0x1A, 0x1E, 0xDE, 0xDF, 0x1F, 0xDD, 0x1D, 0x1C, 0xDC,
        0x14, 0xD4, 0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
        0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3, 0xF2, 0x32,
        0x36, 0xF6, 0xF7, 0x37, 0xF5, 0x35, 0x34, 0xF4, 0x3C, 0xFC, 0xFD, 0x3D,
        0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A, 0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38,
        0x28, 0xE8, 0xE9, 0x29, 0xEB, 0x2B, 0x2A, 0xEA, 0xEE, 0x2E, 0x2F, 0xEF,
        0x2D, 0xED, 0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
        0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60, 0x61, 0xA1,
        0x63, 0xA3, 0xA2, 0x62, 0x66, 0xA6, 0xA7, 0x67, 0xA5, 0x65, 0x64, 0xA4,
        0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F, 0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB,
        0x69, 0xA9, 0xA8, 0x68, 0x78, 0xB8, 0xB9, 0x79, 0xBB, 0x7B, 0x7A, 0xBA,
        0xBE, 0x7E, 0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
        0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71, 0x70, 0xB0,
        0x50, 0x90, 0x91, 0x51, 0x93, 0x53, 0x52, 0x92, 0x96, 0x56, 0x57, 0x97,
        0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C, 0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E,
        0x5A, 0x9A, 0x9B, 0x5B, 0x99, 0x59, 0x58, 0x98, 0x88, 0x48, 0x49, 0x89,
        0x4B, 0x8B, 0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
        0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42, 0x43, 0x83,
        0x41, 0x81, 0x80, 0x40
    ]

    def __init__(self):
        pass

    @staticmethod
    def create_crc(array):
        """
        计算array的CRC校验值
        :param array:要计算的数组
        :return:CRC校验值，2字节
        """
        crc_high = 0xff
        crc_low = 0xff
        for i in range(0, len(array)):
            crc_index = crc_high ^ array[i]
            crc_high = crc_low ^ CRC16.tableCRCHigh[crc_index]
            crc_low = CRC16.tableCRCLow[crc_index]
        return crc_high << 8 | crc_low

    @staticmethod
    def create_array(array):
        """
        生成添加过CRC校验值的数组
        :param array:要添加CRC校验位的数组
        :return:添加过CRC校验值的数组
        """
        crc_value = CRC16.create_crc(array)
        array.append(crc_value >> 8)
        array.append(crc_value & 0xff)
        return array

    @staticmethod
    def check_crc(array):
        """
        校验CRC数据；
        传入数组的最后两位默认为CRC位；
        计算剔除了最后两位数据的CRC校验值与最后两位进行比对。
        :param array: 要校验的数组
        :return:校验通过返回True，否则返回False
        """
        crc_high = 0xff
        crc_low = 0xff
        len_array = len(array)
        for i in range(0, len_array - 2):
            crc_index = crc_high ^ array[i]
            crc_high = crc_low ^ CRC16.tableCRCHigh[crc_index]
            crc_low = CRC16.tableCRCLow[crc_index]
        if crc_high == array[len_array - 2] and crc_low == array[len_array -
                                                                 1]:
            return True
        else:
            return False
