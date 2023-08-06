# -*- encoding=utf-8 -*-

from .baseDriver import BaseDriver
from .protocolHandler import *
from . import LOGGER
import time

tarVersion = "V20210823"

VersionDetail = "当前版本:" + tarVersion + """
---------------------------版本更新信息----------------------------

可调用方法的API文档请访问:http://www.chuangfeigu.com:9900/web/#/63?page_id=1178

V20210823:
1.使用新的框架来实现旧的api

V20220627:
1.添加API说明

------------------------------------------------------------------
"""


class ConveyerBeltDriver(BaseDriver):
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

    ########################## 以下是传送带控制方法 ############################
    def checkConveyerBeltStatus(self):
        """查询传送带状态

        Returns:
            Int或Boolen:Boolean: False:查询失败;Int: 状态编码(0-关闭;1-前进;2-后退).

        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(255), 0x0101,
                                   0x01, 0)
        if recv_buf is not None:
            return (recv_buf["data"]["数据"] & 0xFF)
        else:
            return False

    def checkConveyerBeltInfr(self):
        """查询传送带探头状态

        Returns:
            List或Boolen:Boolean: False:查询失败;List: [status1, status2]状态编码(0-未触发;1-触发).

        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(255), 0x0102,
                                   0x02, 0)
        if recv_buf is not None:
            return [((recv_buf["data"]["数据"] >> 16) & 0xFF),
                    (recv_buf["data"]["数据"] & 0xFF)]
        else:
            return False

        # return self.queryOrder(self.wait_time, "03号查询指令", 0xFF, 0x0102, 0x02, 0)

    def checkConveyerBeltInfrFront(self):
        """查询传送带前探头状态

        Returns:
            Int或Boolen:Boolean: False:查询失败;Int: 状态编码(0-未触发;1-触发).

        """
        recv_buf = self.checkConveyerBeltInfr()
        if recv_buf is not False:
            return recv_buf[0]
        else:
            return False
        # return ((self.queryOrder(self.wait_time, "03号查询指令", 0xFF, 0x0102, 0x02, 0)) >> 16)

    def checkConveyerBeltInfrBack(self):
        """查询传送带后探头状态

        Returns:
            Int或Boolen:Boolean: False:查询失败;Int: 状态编码(0-未触发;1-触发).
            
        """
        recv_buf = self.checkConveyerBeltInfr()
        if recv_buf is not False:
            return recv_buf[1]
        else:
            return False
        # return ((self.queryOrder(self.wait_time, "03号查询指令", 0xFF, 0x0102, 0x02, 0)) & 0xFF)

    def startConveyerBelt(self):
        """控制传送带前进
        """
        self.excuteOrderRightAway("10号写指令", 0xFF, 0x0101, 0x01, 0x02, 0x0001,
                                  0)

    def backConveyerBelt(self):
        """控制传送带后退
        """
        self.excuteOrderRightAway("10号写指令", 0xFF, 0x0101, 0x01, 0x02, 0x0002,
                                  0)

    def stopConveyerBelt(self):
        """控制传送带停止
        """
        self.excuteOrderRightAway("10号写指令", 0xFF, 0x0101, 0x01, 0x02, 0x0000,
                                  0)

    def controlConveyerBelt(self, direction=0):
        """通过编码控制传送带

        Args:
            direction (int, optional): 传送带状态编码(0-关闭;1-前进;2-后退). Defaults to 0.
        """
        if direction > 0:
            self.startConveyerBelt()
        elif direction < 0:
            self.backConveyerBelt()
        else:
            self.stopConveyerBelt()
