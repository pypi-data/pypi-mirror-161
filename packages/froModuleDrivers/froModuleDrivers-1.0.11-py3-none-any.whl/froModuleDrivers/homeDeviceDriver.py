# -*- encoding=utf-8 -*-

from .baseDriver import BaseDriver
from .protocolHandler import *
from . import LOGGER
import time

tarVersion = "V20220428"

VersionDetail = "当前版本:" + tarVersion + """
---------------------------版本更新信息----------------------------

可调用方法的API文档请访问:http://www.chuangfeigu.com:9900/web/#/54?page_id=1029

V20210821:
1.使用新的框架来实现旧的api

V20210824:
1.修复了窗帘状态返回错误的BUG：def isCurtainOpen(self, moduleID=1):

V20220428:
1.窗帘模块的编码统一改为0x00B9,以下api有改动:
  删除: def currentCurtainStatus(self, moduleID=1)
  删除: def currentCurtainSpeed(self, moduleID=1)
  删除: def setCurtain(self, cMode=None, cSpeed=None):
  修改: def openCurtain(self, moduleID=1):
  修改: def closeCurtain(self, moduleID=1):
  修改: def currentCurtainStatus(self, moduleID=1):

V20220623:
1、添加注释.

------------------------------------------------------------------
"""


class HomeDeviceDict():
    last_speech = 0xFF


class HomeDeviceDriver(BaseDriver, HomeDeviceDict):

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
        """打印历史版本的更新记录.
        """
        print(VersionDetail)

    ########################## 以下是设备控制器控制方法 ############################

    # 灯光
    def openLight(self, moduleID=4):
        """打开灯光

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 4.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AA, 0x01, 0x02,
                                  1, 0)

    def closeLight(self, moduleID=4):
        """关闭灯光

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 4.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AA, 0x01, 0x02,
                                  0, 0)

    # 门禁
    def closeDoor(self, moduleID=2):
        """关闭门禁

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 2.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00B0, 0x01, 0x02,
                                  0, 0)

    def openDoor(self, moduleID=2):
        """打开门禁

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 2.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00B0, 0x01, 0x02,
                                  1, 0)

    # 彩灯
    def openColorfulLight(self, moduleID=5, lightMode=1, lightNum=50):
        """彩灯控制

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 5.
            lightMode (int, optional): 彩灯模式:(0~8);0:关闭. Defaults to 1.
            lightNum (int, optional): 彩灯数量:(1~200). Defaults to 50.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AE, 0x02, 0x04,
                                  ((int(lightMode) << 16) | (int(lightNum))),
                                  0)

    def setColorfulLight(self, lightMode, lightNum):
        """彩灯控制(固定硬件接口号)

        Args:
            lightMode (int): 彩灯模式:(0~8).
            lightNum (int): 彩灯数量:(1~200).

        """
        self.openColorfulLight(5, lightMode, lightNum)

    def closeColorfulLight(self, moduleID=5, lightMode=0, lightNum=255):
        """关闭彩灯

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 5.
            lightMode (int, optional): 彩灯模式:0:关闭. Defaults to 0.
            lightNum (int, optional): 彩灯数量:(1~200). Defaults to 255.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AE, 0x02, 0x04,
                                  ((int(lightMode) << 16) | (int(lightNum))),
                                  0)

    # 窗帘
    def openCurtain(self, moduleID=1):
        """打开窗帘

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 1.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00B9, 0x01, 0x02,
                                  1, 0)

    def closeCurtain(self, moduleID=1):
        """关闭窗帘

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 1.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00B9, 0x01, 0x02,
                                  0, 0)

    # 警报
    def alarm(self, moduleID=6):
        """打开报警器

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 6.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00A8, 0x01, 0x02,
                                  1, 0)

    def quitAlarm(self, moduleID=6):
        """关闭报警器

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 6.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00A8, 0x01, 0x02,
                                  0, 0)

    # 扩展风扇
    def openRoomFan(self, moduleID=3):
        """打开风扇

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 3.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AC, 0x01, 0x02,
                                  1, 0)

    def closeRoomFan(self, moduleID=3):
        """关闭风扇

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 3.

        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AC, 0x01, 0x02,
                                  0, 0)

    # 垃圾桶
    def setServoAngle(self, moduleID=8, angle=0):
        """设置舵机角度

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 8.
            angle (int, optional): 角度:范围(0~180). Defaults to 0.

        """
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00BE, 0x01, 0x02,
                                  angle, 0)

    def openAshcan(self, moduleID=8):
        """打开垃圾桶

        Note:
            实际操作为舵机角度设置为45.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 8.

        """
        self.setServoAngle(moduleID, 45)

    def closeAshcan(self, moduleID=8):
        """关闭垃圾桶

        Note:
            实际操作为舵机角度设置为0.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 8.

        """
        self.setServoAngle(moduleID, 0)

    # 饮水机
    def openDrinkingFountain(self, moduleID=11):
        """打开饮水机

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 11.

        """
        self.openRoomFan()

    def closeDrinkingFountain(self, moduleID=11):
        """关闭饮水机

        Args:
            moduleID (int, optional): _description_. Defaults to 11.

        """
        self.closeRoomFan()

    # 显示数字
    def displayTwoNum(self, moduleID=9, value1=0, value2=0):
        """显示数字

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 9.
            value1 (int, optional): 数字1:范围(0~65535). Defaults to 0.
            value2 (int, optional): 数字2:范围(0~65535). Defaults to 0.

        """
        if value1 < 0:
            value1 = 0
        elif value1 > 0xFFFF:
            value1 = 0xFFFF

        if value2 < 0:
            value2 = 0
        elif value2 > 0xFFFF:
            value2 = 0xFFFF
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00B2, 0x02, 0x04,
                                  ((int(value1) << 16) | (int(value2))), 0)

    # 显示交通灯信息
    def setTrafficLightMessage(self, moduleID=12, status=0, value=0):
        """显示交通灯信息

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 12.
            status (int, optional): 状态:0-禁止通行;1-可以通行. Defaults to 0.
            value (int, optional): 等待时间:范围(0~65535). Defaults to 0.

        """
        if status != 0:
            status = 1

        if value < 0:
            value = 0
        elif value > 0xFFFF:
            value = 0xFFFF
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00C1, 0x02, 0x04,
                                  ((int(status) << 16) | (int(value))), 0)

    ################### 以下是获取状态 #####################
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

    # 报警器
    def isAlarming(self, moduleID=6):
        """查询报警器状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 6.

        Returns:
            Boolean: False:查询失败或未打开;True: 已打开.

        """
        return self.isSingleStatusTrueOrFalse(moduleID, 0x00A8)

    # 灯光
    def isLightOpen(self, moduleID=4):
        """查询灯光状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 4.

        Returns:
            Boolean: False:查询失败或未打开;True: 已打开.
            
        """
        return self.isSingleStatusTrueOrFalse(moduleID, 0x00AA)

    # 扩展风扇
    def isRoomFanOpen(self, moduleID=3):
        """查询风扇状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 3.

        Returns:
            Boolean: False:查询失败或未打开;True: 已打开.
            
        """
        return self.isSingleStatusTrueOrFalse(moduleID, 0x00AC)

    # 门禁
    def isDoorOpen(self, moduleID=2):
        """查询门禁状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 2.

        Returns:
            Boolean: False:查询失败或未打开;True: 已打开.
            
        """
        return self.isSingleStatusTrueOrFalse(moduleID, 0x00B0)

    def isCurtainOpen(self, moduleID=1):
        """查询窗帘状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 1.

        Returns:
            Boolean: False:查询失败或未打开;True: 已打开.
            
        """
        return self.isSingleStatusTrueOrFalse(moduleID, 0x00B9)

    # 彩灯
    def currentColorfulLightStatus(self, moduleID=5):
        """查询彩灯状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 5.

        Returns:
            List: 查询失败返回[-1,-1];查询成功返回[lightMode,lightNum]具体含义如下.
            lightMode: 彩灯模式.
            lightNum: 彩灯数量.

        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x00AE, 0x02, 0)
        if recv_buf is not None:
            return [((recv_buf["data"]["数据"] >> 16) & 0xFFFF),
                    ((recv_buf["data"]["数据"]) & 0xFFFF)]
        else:
            return [-1, -1]

    def isColorfulLightOpen(self, moduleID=5):
        """查询彩灯是否打开

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 5.

        Returns:
            Boolean: False:查询失败或未打开;True: 已打开.
            
        """
        recv_buf = self.currentColorfulLightStatus(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            if recv_buf[0] != 0 and recv_buf[1] > 0:
                return True
            else:
                return False
        else:
            return False

    def currentColorfulLightMode(self, moduleID=5):
        """查询当前彩灯模式

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 5.

        Returns:
            Int或Boolen:Boolean: False:查询失败;Int: 彩灯模式编码.

        """
        recv_buf = self.currentColorfulLightStatus(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[0]
        else:
            return False

    def currentColorfulLightNum(self, moduleID=5):
        """查询当前彩灯数量

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 5.

        Returns:
            Int: 查询失败返回-1.

        """
        recv_buf = self.currentColorfulLightStatus(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[1]
        else:
            return -1

    def getRoomIRDegree(self, moduleID=7):
        """查询红外对射状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 7.

        Returns:
            Boolean: False:查询失败或未触发;True: 已触发.
            
        """
        return self.isSingleStatusTrueOrFalse(int(moduleID), 0x00B6)
