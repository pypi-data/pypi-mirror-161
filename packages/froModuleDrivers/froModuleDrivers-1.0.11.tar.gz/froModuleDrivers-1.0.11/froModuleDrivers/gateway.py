# -*- encoding=utf-8 -*-

from .baseDriver import BaseDriver
from .protocolHandler import *
from . import LOGGER
import time

tarVersion = "V20220621"

VersionDetail = "当前版本:" + tarVersion + """
---------------------------版本更新信息----------------------------

可调用方法的API文档请访问:http://www.chuangfeigu.com:9900/web/#/54?page_id=1029

V20210818:
1.使用新的框架来实现旧的api，注意该版本并未实现节点号缺省功能

V20210823:
1、添加了硬件语音联动状态查询接口:def isSpeechAutoMode(self):

V20210824:
1、修复了温湿度获取API显示错位:def getTemperatureHumidity(self, moduleID):
2、修复了语音识别API未识别到时引发错误的BUG:def recognizeSpeech(self, moduleID):
3、增加了识别一条新语句的方法：def recognizeNewSpeech(self, moduleID):

V20220425:
1、修复了RGB控制API入参错位BUG:
    def setRGBRed(self, moduleID, redValue):
    def setRGBGreen(self, moduleID, greenValue):
    def setRGBBlue(self, moduleID, blueValue):
2、修复了蜂鸣器控制API调用API入参错误BUG:def playSongBySongID(self, moduleID, songID):

V20220427:
1、添加了语音识别API识别失败时的回参:def recognizeSpeech(self, moduleID):
2、添加了手势识别API识别失败时的回参:def checkGesture(self, moduleID):

V20220621:
1、添加注释.

------------------------------------------------------------------
"""


class GatewayDict():
    last_speech = 0xFF
    gestureEncode = {0: "None", 1: "left", 2: "right", 3: "up", 4: "down"}
    voiceEncodeV2 = {
        # 0:"未识别到语音",
        1: "小飞同学",
        2: "打开灯光",
        3: "关闭灯光",
        4: "开一下灯",
        5: "关一下灯",
        6: "请开灯",
        7: "请关灯",
        8: "开始采摘",
        9: "开始运输",
        10: "开始入库",
        11: "开始出库",
        12: "播放音乐",
        13: "关闭音乐",
        14: "打开客厅灯光",
        15: "关闭客厅灯光",
        16: "打开厨房灯光",
        17: "关闭厨房灯光",
        18: "打开主人房灯光",
        19: "关闭主人房灯光",
        20: "打开客房灯光",
        21: "关闭客房灯光",
        22: "开启演示模式",
        23: "关闭演示模式",
        24: "打开路灯",
        25: "关闭路灯",
        26: "打开厕所灯光",
        27: "关闭厕所灯光",
        28: "娱乐模式",
        29: "学习模式",
        30: "打开所有灯光",
        31: "关闭所有灯光",
        32: "打开台灯",
        33: "关闭台灯",
        34: "上一首",
        35: "下一首",
        36: "打开儿童房灯光",
        37: "关闭儿童房灯光",
        38: "打开客厅窗帘",
        39: "关闭客厅窗帘",
        40: "客厅窗帘停止",
        41: "打开主人房窗帘",
        42: "关闭主人房窗帘",
        43: "主人房窗帘停止",
        44: "打开客房窗帘",
        45: "关闭客房窗帘",
        46: "客房窗帘停止",
        47: "打开书房窗帘",
        48: "关闭书房窗帘",
        49: "打开窗帘",
        50: "打开儿童房窗帘",
        51: "关闭儿童房窗帘",
        52: "关闭窗帘",
        53: "打开客厅风扇",
        54: "关闭客厅风扇",
        55: "打开主人房风扇",
        56: "关闭主人房风扇",
        57: "打开客房风扇",
        58: "关闭客房风扇",
        59: "打开书房风扇",
        60: "关闭书房风扇",
        61: "打开儿童房风扇",
        62: "关闭儿童房风扇",
        63: "打开通风",
        64: "关闭通风",
        65: "打开客厅门",
        66: "关闭客厅门",
        67: "打开主人房门",
        68: "关闭主人房门",
        69: "打开客房门",
        70: "关闭客房门",
        71: "打开厨房门",
        72: "关闭厨房门",
        73: "打开彩灯",
        74: "关闭彩灯",
        75: "最高亮度",
        76: "中等亮度",
        77: "最低亮度",
        78: "亮一点",
        79: "暗一点",
        80: "照明模式",
        81: "阅读模式",
        82: "夜灯模式",
        83: "红色模式",
        84: "绿色模式  ",
        85: "蓝色模式",
        86: "彩色模式",
        87: "流水灯模式",
        88: "打开防盗报警",
        89: "关闭防盗报警",
        90: "打开报警",
        91: "关闭报警",
        92: "打开空调",
        93: "关闭空调",
        94: "小车启动",
        95: "小车停止",
        96: "小车向前",
        97: "小车后退",
        98: "小车向左",
        99: "小车向右",
        100: "打开车灯",
        101: "开启避障",
        102: "关闭避障",
        103: "1号车启动",
        104: "2号车启动",
        105: "3号车启动",
        106: "4号车启动",
        107: "1号车停止",
        108: "2号车停止",
        109: "3号车停止",
        110: "4号车停止",
        111: "1号车进充电桩",
        112: "2号车进充电桩",
        113: "打开电视",
        114: "关闭电视",
        115: "上一台",
        116: "下一台",
        117: "1号车出充电桩",
        118: "2号车出充电桩",
        119: "晚安小飞",
        120: "早上好",
        121: "你好",
        122: "打开门",
        123: "关闭门",
        124: "打开风扇",
        125: "关闭风扇",
        126: "音量增",
        127: "我回来了",
        128: "我出去了",
        129: "进停车场",
        130: "出停车场",
        131: "开启布防",
        132: "撤销布防",
        133: "音量减",
        137: "大声点",
        138: "小声点",
        139: "最大声",
        140: "最小声",
    }


class GatewayDriver(BaseDriver, GatewayDict):

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
        # if result is None or result.get("data") is None:
        #     return None, False
        # else:
        #     LOGGER.logger.debug("doHandleResult:%s" % result)
        #     # if result["orderName"] == "03号查询指令":
        #     #     if result["data"].get("设备号") == 0x0101:
        #     #         print("my test", result["data"].get("数据"))
        #     # result["adiditon"] = "hello  world"
        #     return result, True

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
    def isSingleStatusTrueOrFalse(self, moduleID, moduleAddr=0):
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

    ########################## 以下是网关节点配置方法 ############################
    def isSpeechAutoMode(self):
        """查询联动开关状态.

        Returns:
            Boolean: False:查询失败/联动开关未开启;True:联动开关已开启.
        """
        return self.isSingleStatusTrueOrFalse(int(255), 0xff03)

    def enableSpeechAutoMode(self):
        """使能语音联动开关.
        """
        self.excuteOrderRightAway("10号写指令", int(255), 0xff03, 0x01, 0x02, 1, 0)

    def disableSpeechAutoMode(self):
        """失能语音联动开关.
        """
        self.excuteOrderRightAway("10号写指令", int(255), 0xff03, 0x01, 0x02, 0, 0)

    ########################## 以下是通用的执行器控制方法 ############################
    # 风扇
    def openFan(self, moduleID):
        """打开风扇.

        Args:
            moduleID (int): 硬件接口号.
        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x0048, 0x01, 0x02,
                                  1, 0)

    def closeFan(self, moduleID):
        """关闭风扇.

        Args:
            moduleID (int): 硬件接口号.
        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x0048, 0x01, 0x02,
                                  0, 0)

    # RGB灯
    def openRGBLight(self, moduleID, redValue, greenValue, blueValue):
        """控制RGB灯.

        Args:
            moduleID (int): 硬件接口号.
            redValue (int): 红色亮度值(0~255),0为关闭.
            greenValue (int): 绿色亮度值(0~255),0为关闭.
            blueValue (int): 蓝色亮度值(0~255),0为关闭.
        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x009e, 0x03, 0x06,
                                  ((int(redValue) & 0xFF) << 32) |
                                  ((int(greenValue) & 0xFF) << 16) |
                                  (int(blueValue) & 0xFF), 0)

    # todo
    # def setRGBLight(self, redValue=None, greenValue=None, blueValue=None):
    #     self.openRGBLight(self, moduleID, redValue, greenValue, blueValue)

    def setRGBRed(self, moduleID, redValue):
        """控制RGB灯亮红色.

        Args:
            moduleID (int): 硬件接口号.
            redValue (int): 红色亮度值(0~255),0为关闭.
        """
        self.openRGBLight(moduleID, redValue, 0, 0)

    def setRGBGreen(self, moduleID, greenValue):
        """控制RGB灯亮绿色.

        Args:
            moduleID (int): 硬件接口号.
            redValue (int): 绿色亮度值(0~255),0为关闭.
        """
        self.openRGBLight(moduleID, 0, greenValue, 0)

    def setRGBBlue(self, moduleID, blueValue):
        """控制RGB灯亮蓝色.

        Args:
            moduleID (int): 硬件接口号.
            redValue (int): 蓝色亮度值(0~255),0为关闭.
        """
        self.openRGBLight(moduleID, 0, 0, blueValue)

    def closeRGBLight(self, moduleID):
        """关闭RGB灯.

        Args:
            moduleID (int): 硬件接口号.
        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x009e, 0x03, 0x06,
                                  0, 0)

    # 蜂鸣器
    def playAudioPlayer(self, moduleID, songID=1, songVolume=100):
        """控制蜂鸣器.

        Args:
            moduleID (int): 硬件接口号.
            songID (int, optional): 歌曲编号:范围(1~5). Defaults to 1.
            songVolume (int, optional): 音量:范围(0~100). Defaults to 100.
        """
        if songID != None and songVolume != None:
            if songID <= 0 or songID > 5 or songVolume < 0 or songVolume > 100:
                return
        else:
            return
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x0096, 0x02, 0x04,
                                  ((int(songID) << 16) | (int(songVolume))), 0)

    def playSongBySongID(self, moduleID, songID):
        """控制蜂鸣器播放乐曲.
        默认音量为100.
        Args:
            moduleID (int): 硬件接口号.
            songID (int): 歌曲编号:范围(1~5). 
        """
        self.playAudioPlayer(int(moduleID), int(songID), 100)

    # todo
    # def playSong(self, songID, songVolumn):
    #     self.playAudioPlayer(None, songID, songVolumn)

    def stopAudioPlayer(self, moduleID):
        """关闭蜂鸣器.

        Args:
            moduleID (int): 硬件接口号.
        """
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x0096, 0x02, 0x04,
                                  0x00000000, 0)

    # 红外转发
    def sendIRTrans(self, moduleID, param):
        """红外转发

        Args:
            moduleID (int): 硬件接口号.
            param (int): 红外遥控编码:(0:OK功能;1-6:频道1-6;10-11;频道+，频道－;12-13:声音－,声音＋).
        """
        param = param % 14
        if param in [7, 8, 9]:
            return
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x009A, 0x01, 0x02,
                                  param, 0)

    def addChannel(self, moduleID):
        """频道增加.

        Args:
            moduleID (int): 硬件接口号.
        """
        param = 10
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x009A, 0x01, 0x02,
                                  param, 0)

    def descChannel(self, moduleID):
        """频道减小.

        Args:
            moduleID (int): 硬件接口号.
        """
        param = 11
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x009A, 0x01, 0x02,
                                  param, 0)

    def addVolumn(self, moduleID):
        """音量增加.

        Args:
            moduleID (int): 硬件接口号.
        """
        param = 13
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x009A, 0x01, 0x02,
                                  param, 0)

    def descVolumn(self, moduleID):
        """音量减小.

        Args:
            moduleID (int): 硬件接口号.
        """
        param = 12
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x009A, 0x01, 0x02,
                                  param, 0)

    ################### 以下是获取状态 #####################

    # 手势
    def checkGesture(self, moduleID):
        """识别手势.

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Int或Boolen: Boolean: False:查询失败;查询成功返回识别到的语音编码.手势编码可参考字典gestureEncode.
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x00A6, 0x01, 0)
        if recv_buf is not None:
            current_gesture = recv_buf["data"]["数据"]
            if current_gesture in self.gestureEncode:
                return current_gesture
            else:
                return False
        else:
            return False

    # 语音识别
    def recognizeSpeech(self, moduleID):
        """语音识别.

        Args:
            moduleID (int): 硬件接口号. 

        Returns:
            Int或Boolen: Boolean: False:查询失败;查询成功返回识别到的语音编码.Int: 语音编码可参考字典voiceEncodeV2.
        
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x00b8, 0x01, 0)
        if recv_buf is not None:
            current_speech = recv_buf["data"]["数据"]
            if current_speech in self.voiceEncodeV2:
                return current_speech
            else:
                return False
        return False

    def recognizeNewSpeech(self, moduleID):
        """识别新语句.

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Int或Boolen: Boolean: False:查询失败或查询的语句未改变;Int: 查询到新语句返回识别到的语音编码.语音编码可参考字典voiceEncodeV2.
        
        """
        recv_buf = self.recognizeSpeech(moduleID)
        if recv_buf is not False and recv_buf != self.last_speech:
            self.last_speech = recv_buf
            return self.last_speech
        return False

    # 场景代码-红外对射场景
    def getIRDegree(self, moduleID):
        """获取红外对射状态.

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Boolean: False:查询失败或未触发;True: 已触发.
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x002C, 0x01, 0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] == 1:
                return True
            else:
                return False
        else:
            return False

    # 场景代码-红外反射传感器
    def getAIRDegree(self, moduleID):
        """获取红外反射状态.

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Boolean: False:查询失败或未触发;True: 已触发.
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x0036, 0x01, 0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] == 1:
                return True
            else:
                return False
        else:
            return False

    # 场景代码-红外转发
    def getIRSend(self, moduleID):
        """获取红外转发状态.

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Int或Boolen:Boolean: False:查询失败;Int: 返回发送的红外遥控编码:(0:OK功能;1-6:频道1-6;10-11;频道+，频道－;12-13:声音－,声音＋).
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x009A, 0x01, 0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"]
        else:
            return False

    # 场景代码-红外接收
    def getIRRecv(self, moduleID):
        """获取红外接收状态.

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Int或Boolen:Boolean: False:查询失败;Int: 返回接收的红外遥控编码:(0:OK功能;1-6:频道1-6;10-11;频道+，频道－;12-13:声音－,声音＋).
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x009C, 0x01, 0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"]
        else:
            return False

    # 场景代码-人体
    def checkHuman(self, moduleID):
        """获取人体传感器状态.

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Boolean: False:查询失败或未触发;True: 已触发.
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x003C, 0x01, 0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] == 1:
                return True
            else:
                return False
        else:
            return False

    # 场景代码-获取光照值场景
    def getShineDegree(self, moduleID):
        """获取光照数据.

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Int: 返回光照数据, 单位Lux; 0:查询失败.
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x002A, 0x01, 0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"]
        else:
            return 0

    # 场景代码-烟雾
    def checkSmoke(self, moduleID):
        """获取烟雾数据.

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Int: 返回烟雾数据; 0:查询失败.
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x0034, 0x01, 0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"]
        else:
            return 0

    # 场景代码-声音
    def checkSound(self, moduleID):
        """获取声音传感器状态.

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Boolean: False:查询失败或未触发;True: 已触发.
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x003A, 0x01, 0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] == 1:
                return True
            else:
                return False
        else:
            return False

    # 场景代码-结露
    def checkRain(self, moduleID):
        """获取结露数据.

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Int: 返回结露数据; -1:查询失败.
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x002E, 0x01, 0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"]
        else:
            return -1

    # 场景代码-火焰
    def checkFire(self, moduleID):
        """获取火焰传感器状态.

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Boolean: False:查询失败或未触发;True: 已触发.
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x0038, 0x01, 0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] == 1:
                return True
            else:
                return False
        else:
            return False

    # 场景代码-燃气
    def checkCGas(self, moduleID):
        """获取燃气数据.

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Int: 返回燃气数据; -1:查询失败.
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x00A4, 0x01, 0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"]
        else:
            return -1

    # 场景代码-温湿度
    def getTemperatureHumidity(self, moduleID):
        """查询温湿度

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            List: 查询失败返回[-1,-1];查询成功返回[Temperature,Humidity]具体含义如下.
            Temperature: 温度,单位°.
            Humidity: 湿度,单位%.

        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x0014, 0x02, 0)
        if recv_buf is not None:
            return [((recv_buf["data"]["数据"]) & 0xFFFF) / 10.0,
                    ((recv_buf["data"]["数据"] >> 16) & 0xFFFF) / 10.0]
        else:
            return [-1, -1]

    # 场景代码-温度
    def getTemperature(self, moduleID):
        """查询温度

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Int: 查询失败返回-1;查询成功返回温度值,单位°.

        """
        recv_buf = self.getTemperatureHumidity(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[0]
        else:
            return -1

    # 场景代码-湿度
    def getHumidity(self, moduleID):
        """查询湿度

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Int: 查询失败返回-1;查询成功返回湿度值,单位%.

        """
        recv_buf = self.getTemperatureHumidity(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[1]
        else:
            return -1

    ################### 以下是执行器状态查询 #####################

    def isFanOpen(self, moduleID):
        """获取风扇状态.

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Boolean: False:查询失败或未开启;True: 已开启.

        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x0048, 0x01, 0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] == 1:
                return True
            else:
                return False
        else:
            return False

    def isRGBLightOpen(self, moduleID):
        """获取灯光状态.

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            Boolean: False:查询失败或未开启;True: 已开启.

        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x009e, 0x03, 0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] != 0:
                return True
            else:
                return False
        else:
            return False

    def currentRGBLight(self, moduleID):
        """查询RGB灯状态

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            List: 查询失败返回[-1,-1,-1];查询成功返回[status1,status2,status3]具体含义如下.
            status1: 红色值，范围(0~255).
            status2: 绿色值，范围(0~255).
            status2: 蓝色值，范围(0~255).

        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x009e, 0x03, 0)
        if recv_buf is not None:
            return [((recv_buf["data"]["数据"] >> 32) & 0xFFFF),
                    ((recv_buf["data"]["数据"] >> 16) & 0xFFFF),
                    ((recv_buf["data"]["数据"]) & 0xFFFF)]
        else:
            return [-1, -1, -1]

    def getRGBRed(self, moduleID):
        """查询RGB灯的红色值.

        Args:
            moduleID (int): 硬件接口号. 

        Returns:
            Int: 查询失败返回-1;查询成功返回RGB灯的红色值.

        """
        recv_buf = self.currentRGBLight(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1 and recv_buf[2] != -1:
            return recv_buf[0]
        else:
            return -1

    def getRGBGreen(self, moduleID):
        """查询RGB灯的绿色值.

        Args:
            moduleID (int): 硬件接口号. 

        Returns:
            Int: 查询失败返回-1;查询成功返回RGB灯的绿色值.

        """
        recv_buf = self.currentRGBLight(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1 and recv_buf[2] != -1:
            return recv_buf[1]
        else:
            return -1

    def getRGBBlue(self, moduleID):
        """查询RGB灯的蓝色值.

        Args:
            moduleID (int): 硬件接口号. 

        Returns:
            Int: 查询失败返回-1;查询成功返回RGB灯的蓝色值.

        """
        recv_buf = self.currentRGBLight(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1 and recv_buf[2] != -1:
            return recv_buf[2]
        else:
            return -1

    def audioPlayerCurrentPlayed(self, moduleID):
        """查询蜂鸣器状态

        Args:
            moduleID (int): 硬件接口号.

        Returns:
            List: 查询失败返回[-1,-1];查询成功返回[songID,songVolume]具体含义如下.
            songID (int): 歌曲编号:范围(1~5). Defaults to 1.
            songVolume (int): 音量:范围(0~100). Defaults to 100.

        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x0096, 0x02, 0)
        if recv_buf is not None:
            return [((recv_buf["data"]["数据"] >> 16) & 0xFFFF),
                    ((recv_buf["data"]["数据"]) & 0xFFFF)]
        else:
            return [-1, -1]

    def audioPlayerCurrentPlayedSong(self, moduleID):
        """查询蜂鸣器播放的歌曲编号.

        Args:
            moduleID (int): 硬件接口号. 

        Returns:
            Int: 查询失败返回-1;查询成功返回蜂鸣器播放的歌曲编号.

        """
        recv_buf = self.audioPlayerCurrentPlayed(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[0]
        else:
            return -1

    def audioPlayerCurrentPlayedVolumn(self, moduleID):
        """查询蜂鸣器的音量.

        Args:
            moduleID (int): 硬件接口号. 

        Returns:
            Int: 查询失败返回-1;查询成功返回蜂鸣器的音量.

        """
        recv_buf = self.audioPlayerCurrentPlayed(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[1]
        else:
            return -1
