# -*- encoding=utf-8 -*-

from .baseDriver import BaseDriver
from .protocolHandler import *
from . import LOGGER
import time

tarVersion = "V20210823"

VersionDetail = "当前版本:" + tarVersion + """
---------------------------版本更新信息----------------------------

可调用方法的API文档请访问:http://www.chuangfeigu.com:9900/web/#/60?page_id=1128

V20210823:
1.使用新的框架来实现旧的api

V20220624:
1、添加注释.

------------------------------------------------------------------
"""


class AgricultureDeviceDriver(BaseDriver):
    def __init__(self, host="localhost", port=4001):
        super().__init__(host, port)
        self.addProtocol(K12ProtocolHandler())
        self.wait_time = 1
        self.status = {}

    # 此处result为按协议定义的字段解析过的dict
    # 可根据具体设备进行自定义 状态信息维护、状态查询结果返回等操作。
    # 根据不同的协议返回，包装返回值，使其包含"orderName", 并被查询指令接收。
    def doHandleResult(self, result):
        if result is None or result.get("data") is None:
            if result is not None:
                LOGGER.logger.warning("不能解析的协议:%s" % result)
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

    # 单参数状态获取返回为true or false
    def isSingleStatusTrueOrFalse(self, moduleID=None, moduleAddr=0):
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   moduleAddr, 0x01, 0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] == 1:
                return True
            else:
                return False
        else:
            return False

    def setWaitTime(self, wait_recv_time=1):
        """设置查询指令的响应等待时间.

        Note:
            该参数为全局变量.影响查询类方法的执行速度和成功率.
            一般情况下,响应等待时间越久,执行速度越慢,成功率越高.
            应根据实际的网络状况来谨慎配置.
            不建议设置到0.5以下.

        Args:
            wait_recv_time (float, optional): 等待时间,单位:秒. Defaults to 1.

        """
        if wait_recv_time < 0:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        self.wait_time = wait_recv_time

    def getVersion(self):
        """获取当前驱动的版本信息.

        Returns:
            Str: 当前驱动的版本号.
        """
        return tarVersion

    def showVersion(self):
        """打印历史版本的更新记录
        """
        print(VersionDetail)

    ########################## 以下是大棚内的设备控制/查询方法 ############################
    # 补光灯
    def isLightOpen(self, moduleID=4):
        """查询补光灯状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 4.

        Returns:
            Boolean: False:查询失败或未打开;True: 已打开.
            
        """
        return self.isSingleStatusTrueOrFalse(int(moduleID), 0x00AA)
        # return self.queryOrder(self.wait_time, "03号查询指令", int(moduleID), 0x00AA, 0x01, 0)

    def openLight(self, moduleID=4):
        """打开补光灯

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 4.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AA, 0x01, 0x02,
                                  0x0001, 0)

    def closeLight(self, moduleID=4):
        """关闭补光灯

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 4.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AA, 0x01, 0x02,
                                  0x0000, 0)

    # 通风
    def isRoomFanOpen(self, moduleID=3):
        """查询通风状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 3.

        Returns:
            Boolean: False:查询失败或未打开;True: 已打开.
            
        """
        return self.isSingleStatusTrueOrFalse(int(moduleID), 0x00AC)
        # return self.queryOrder(self.wait_time, "03号查询指令", int(moduleID), 0x00AC, 0x01, 0)

    def openRoomFan(self, moduleID=3):
        """打开通风

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 3.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AC, 0x01, 0x02,
                                  0x0001, 0)

    def closeRoomFan(self, moduleID=3):
        """关闭通风

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 3.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AC, 0x01, 0x02,
                                  0x0000, 0)

    # 卷帘
    def currentTCurtainStatus(self, moduleID=1):
        """查询卷帘状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 1.

        Returns:
            Boolean: False:查询失败或未打开;True: 已打开.
            
        """
        return self.isSingleStatusTrueOrFalse(int(moduleID), 0x00BC)
        # return self.queryOrder(self.wait_time, "03号查询指令", int(moduleID), 0x00BC, 0x01, 0)

    def openTCurtain(self, moduleID=1):
        """打开卷帘

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 1.
        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00BC, 0x01, 0x02,
                                  0x0001, 0)

    def closeTCurtain(self, moduleID=1):
        """关闭卷帘

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 1.
        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00BC, 0x01, 0x02,
                                  0x0000, 0)

    # 灌溉
    def isWaterOpen(self, moduleID=2):
        """查询灌溉状态

        Args:
            moduleID (int, optional): 灌溉. Defaults to 2.

        Returns:
            Boolean: False:查询失败或未打开;True: 已打开.
            
        """
        return self.isSingleStatusTrueOrFalse(int(moduleID), 0x00BA)
        # return self.queryOrder(self.wait_time, "03号查询指令", int(moduleID), 0x00BA, 0x01, 0)

    def openWater(self, moduleID=2):
        """打开灌溉

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 2.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00BA, 0x01, 0x02,
                                  0x0001, 0)

    def closeWater(self, moduleID=2):
        """关闭灌溉

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 2.
            
        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00BA, 0x01, 0x02,
                                  0x0000, 0)
