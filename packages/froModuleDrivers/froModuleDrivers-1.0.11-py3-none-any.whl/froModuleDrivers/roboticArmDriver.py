# -*- encoding=utf-8 -*-

from .baseDriver import BaseDriver
from .protocolHandler import *
from . import LOGGER
import time

tarVersion = "V20210821"

VersionDetail = "当前版本:" + tarVersion + """
---------------------------版本更新信息----------------------------

可调用方法的API文档请访问:http://www.chuangfeigu.com:9900/web/#/61?page_id=1150

V20210821:
1.使用新的框架来实现旧的api

------------------------------------------------------------------
"""


class RoboticArmDriver(BaseDriver):
    def __init__(self, host="localhost", port=4001):
        super().__init__(host, port)
        self.wait_time = 1
        self.status = {}

    # 此处result为按协议定义的字段解析过的dict
    # 可根据具体设备进行自定义 状态信息维护、状态查询结果返回等操作。
    # 根据不同的协议返回，包装返回值，使其包含"orderName", 并被查询指令接收。
    def doHandleResult(self, result):
        if result is None or result.get("data") is None:
            return None, False
        else:
            LOGGER.logger.debug("doHandleResult:%s" % result)
            return result, True

    # 查询指令样本，需要等待返回状态值
    def queryOrder(self, *args):
        argList = list(args)
        timeout = argList.pop(0)
        orderName = argList.pop(0)
        data = self.parseOrder(orderName, *argList)
        if data is None:
            return
        self.connector.waitResponse(self.getClientId(), orderName)
        self.connector.sendData(self.getClientId(), data, prior=False)
        time.sleep(timeout)
        return self.connector.getResponse(self.getClientId(), orderName)

    # 不等待返回值，比如上位机软件更新内部设备状态信息
    def excuteOrderRightAway(self, *args):
        argList = list(args)
        orderName = argList.pop(0)
        data = self.parseOrder(orderName, *argList)
        if data is None:
            return
        self.connector.sendData(self.getClientId(), data, prior=False)

    def setWaitTime(self, wait_recv_time=1):
        self.wait_time = wait_recv_time

    def getVersion(self):
        return tarVersion

    def showVersion(self):
        print(VersionDetail)

    # 直接发送指令的原始数据帧
    def sendRawDataRightAway(self, hex_array):
        if hex_array is None:
            return
        self.connector.sendData(self.getClientId(),
                                bytes(bytearray(hex_array)),
                                prior=False)

    # 以下是机械臂控制
    def startAction(self, actionId):
        """执行动作组

        Args:
            actionId (int): 动作组编号（1~255）
        """
        my_order = [0x55, 0x55, 0x05, 0x06, 0x00, 0x01, 0x00]
        my_order[4] = actionId & 0xFF
        self.sendRawDataRightAway(my_order)
