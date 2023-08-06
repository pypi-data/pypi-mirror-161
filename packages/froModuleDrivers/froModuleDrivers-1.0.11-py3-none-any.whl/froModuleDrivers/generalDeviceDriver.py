# -*- encoding=utf-8 -*-

from operator import truediv
from .baseDriver import BaseDriver
from .protocolHandler import *
from . import LOGGER
import time

tarVersion = "V20220718"

VersionDetail = "当前版本:" + tarVersion + """
---------------------------版本更新信息----------------------------

可调用方法的API文档请访问:http://www.chuangfeigu.com:9900/web/#/50?page_id=947

V20220411:
1. 添加了基础的传感器获取与设备控制方法。

V20220415:
1. 添加了控制指令的返回校验功能(默认关闭)。
2. 添加了直接打开/关闭5V输出接口的方法。
3. 添加了更为详细的API说明和使用示例。

V20220718:
1. 修复了语音识别编码字典(voiceEncodeV3)与硬件返回不匹配的BUG。

V20220802:
1. 添加了3个语音识别接口的控制方法:
    def clearCachedSpeech(self, moduleID=2):
    def setCachedSpeech(self, moduleID=2, speechNum=0):
    def recognizeSpeechAndClearCache(self, moduleID=2):

------------------------------------------------------------------
"""


class GeneralDeviceDict():
    last_speech = 0xFF
    voiceEncodeV3 = {
        0: "未识别到语音",
        223: "再见",
        1: "小飞同学",
        2: "打开灯光",
        3: "关闭灯光",
        28: "娱乐模式",
        29: "学习模式",
        49: "打开窗帘",
        52: "关闭窗帘",
        73: "打开彩灯",
        74: "关闭彩灯",
        83: "红色模式",
        84: "绿色模式",
        85: "蓝色模式",
        86: "彩色模式",
        87: "流水灯模式",
        90: "打开警报",
        91: "关闭警报",
        121: "你好",
        122: "打开门",
        123: "关闭门",
        124: "打开风扇",
        125: "关闭风扇",
        126: "音量增",
        127: "我回来了",
        128: "我出去了",
        141: "开始",
        142: "结束",
        143: "前进",
        144: "后退",
        145: "左转",
        146: "右转",
    }
    colorEncode = {
        0: "无",
        1: "红色",
        2: "黄色",
        4: "粉色",
        8: "白色",
        16: "黑色",
        32: "绿色",
        64: "深蓝色",
        128: "蓝色",
    }


class GeneralDeviceDriver(BaseDriver, GeneralDeviceDict):

    def __init__(self, host="localhost", port=4001):
        super().__init__(host, port)
        self.addProtocol(K12ProtocolHandler())
        self.wait_time = 0.5
        self.send_time = 0
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

    # 等待返回值，指令返回状态
    def excuteOrder(self, *args):
        argList = list(args)
        timeout = argList.pop(0)
        orderName = argList.pop(0)
        data = self.parseOrder(orderName, *argList)
        if data is None:
            return False
        if timeout == 0:
            self.connector.sendData(self.getClientId(), data, prior=False)
            return True
        else:
            self.connector.waitResponse(self.getClientId(), orderName)
            self.connector.sendData(self.getClientId(), data, prior=False)
            time.sleep(timeout)
            res_data = self.connector.getResponse(self.getClientId(),
                                                  orderName)
            if res_data is None:
                return False
            if data[0] == res_data["data"]["主/从机号"] and data[1] == res_data[
                    "data"]["指令号"] and (data[2] * 256 + data[3]) == res_data[
                        "data"]["设备号"] and data[6] == res_data["data"]["数据长度"]:
                return True

    # 直接发送指令的原始数据帧
    def sendRawDataRightAway(self, hex_array):
        if hex_array is None:
            return
        self.connector.sendData(self.getClientId(),
                                bytes(bytearray(hex_array)),
                                prior=False)

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

    def setWaitTime(self, wait_recv_time=0.5):
        """设置查询指令的响应等待时间.

        Note:
            该参数为全局变量.影响查询类方法的执行速度和成功率.
            一般情况下,响应等待时间越久,执行速度越慢,成功率越高.
            应根据实际的网络状况来谨慎配置.
            不建议设置到0.2以下.

        Args:
            wait_recv_time (float, optional): 等待时间,单位:秒. Defaults to 0.5.

        """
        if wait_recv_time < 0:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        self.wait_time = wait_recv_time

    def setSendTime(self, send_recv_time=0):
        """设置设置类指令的响应等待时间.
        Note:
            该参数为全局变量.影响调用excuteOrder()方法的查询响应速度和成功率.
            一般情况下,响应等待时间越久,查询响应速度越慢,成功率越高.
            应根据实际的网络状况来谨慎配置.
            通常不需要校验设置指令成功与否的情况下把该位设置为0即可.
            不建议设置到0.2以下.

        Args:
            send_recv_time (float, optional): 等待时间,单位:秒. Defaults to 0.

        """
        if send_recv_time < 0:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        self.send_time = send_recv_time

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

    ########################## 以下是传感器状态获取方法 ############################

    def recognizeSpeech(self, moduleID=2):
        """语音识别.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 2.

        Returns:
            Int: 查询失败返回-1;查询成功返回识别到的语音编码.语音编码可参考字典voiceEncodeV3.

        Examples:
            >>>print(driver.recognizeSpeech(2))
            2
        """
        if isinstance(moduleID, int) is False:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x00b8, 0x01, 0)
        if recv_buf is not None:
            current_speech = recv_buf["data"]["数据"]
            if current_speech in self.voiceEncodeV3:
                return current_speech
        return -1

    def recognizeNewSpeech(self, moduleID=2):
        """识别新语句

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 2.

        Returns:
            Int: 查询失败或查询的语句未改变返回-1;查询到新语句返回识别到的语音编码.语音编码可参考字典voiceEncodeV3.

        Examples:
            >>>print(driver.recognizeNewSpeech(2))
            2
        """
        recv_buf = self.recognizeSpeech(moduleID)
        if recv_buf is not False and recv_buf != self.last_speech:
            self.last_speech = recv_buf
            return self.last_speech
        return -1

    def setCachedSpeech(self, moduleID=2, speechNum=0):
        """设置语音识别缓存语句编号

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 2.
            speechNum (int, optional): 待设置的语句编号. Defaults to 0.

        Returns:
            Boolean: False:参数校验失败/设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功.

        Examples:
            # 设置2号接口语音识别缓存的编号为0.
            >>>driver.setCachedSpeech(2, 0)
        """
        if speechNum > 0xFF:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        return self.excuteOrder(self.send_time, "10号写指令", int(moduleID),
                                0x00B8, 0x01, 0x02,
                                ((int(speechNum) & 0xFFFF)), 0)

    def clearCachedSpeech(self, moduleID=2):
        """设置语音识别缓存的语句编号为0

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 2.

        Returns:
            Boolean: False:参数校验失败/设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功.

        Examples:
            # 设置2号接口语音识别缓存的编号为0.
            >>>driver.clearCachedSpeech(2)
        """
        return self.setCachedSpeech(moduleID)

    def recognizeSpeechAndClearCache(self, moduleID=2):
        """语音识别然后清除缓存

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 2.

        Returns:
            Int: 查询失败返回-1;查询成功返回识别到的语音编码.语音编码可参考字典voiceEncodeV3.

        Examples:
            >>>print(driver.recognizeSpeechAndClearCache(2))
            2
        """
        speech_num_cache = self.recognizeSpeech(moduleID)
        if speech_num_cache != -1 and speech_num_cache != 0:
            self.clearCachedSpeech(moduleID)
        return speech_num_cache

    def checkSmoke(self, moduleID=7):
        """获取烟雾状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 7.

        Returns:
            Int: 查询失败返回-1;查询成功返回烟雾值.

        Examples:
            >>>print(driver.checkSmoke(7))
            2
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x0034, 0x01, 0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"]
        else:
            return -1

    def getTemperatureHumidity(self, moduleID=15):
        """查询温湿度

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 15.

        Returns:
            List: 查询失败返回[-1,-1];查询成功返回[Temperature,Humidity]具体含义如下.
            Temperature: 温度,单位°.
            Humidity: 湿度,单位%.

        Examples:
            >>>print(driver.getTemperatureHumidity(15))
            [29, 48]
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x0014, 0x02, 0)
        if recv_buf is not None:
            return [((recv_buf["data"]["数据"]) & 0xFFFF) / 10.0,
                    ((recv_buf["data"]["数据"] >> 16) & 0xFFFF) / 10.0]
        else:
            return [-1, -1]

    def getTemperature(self, moduleID=15):
        """查询温度

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 15.

        Returns:
            Int: 查询失败返回-1;查询成功返回温度值,单位°.

        Examples:
            >>>print(driver.getTemperature(15))
            29
        """
        recv_buf = self.getTemperatureHumidity(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[0]
        else:
            return -1

    def getHumidity(self, moduleID=15):
        """查询湿度

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 15.

        Returns:
            Int: 查询失败返回-1;查询成功返回湿度值,单位%.

        Examples:
            >>>print(driver.getHumidity(15))
            48
        """
        recv_buf = self.getTemperatureHumidity(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[1]
        else:
            return -1

    def getLightIntensity(self, moduleID=16):
        """查询光照值

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 16.

        Returns:
            Int: 查询失败返回-1;查询成功返回光照值,单位Lux.

        Examples:
            >>>print(driver.getLightIntensity(16))
            213
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x0101, 0x01, 0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"]
        else:
            return -1

    def getDistanceByUltrasound(self, moduleID=8):
        """查询超声波测量的距离

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 8.

        Returns:
            Int或Float: 查询失败或者超出量程返回-1;查询成功返回距离值,单位cm.

        Examples:
            >>>print(driver.getDistanceByUltrasound(8))
            15.6
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x0046, 0x01, 0)
        if recv_buf is not None and recv_buf["data"]["数据"] != 0xFFFF:
            return recv_buf["data"]["数据"] / 10
        else:
            return -1

    def getTriggerStatus(self, moduleID=4):
        """查询触发器状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 4.

        Returns:
            List: 查询失败返回[-1,-1];查询成功返回[status1,status2]具体含义如下.
            status1: 触发器接口第一位的状态,[1-高电平;0-低电平].
            status2: 触发器接口第二位的状态,[1-高电平;0-低电平].

        Examples:
            >>>print(driver.getTriggerStatus(4))
            [1,0]
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x0105, 0x02, 0)
        if recv_buf is not None:
            return [(recv_buf["data"]["数据"] >> 16) & 0xFFFF,
                    (recv_buf["data"]["数据"]) & 0xFFFF]
        else:
            return [-1, -1]

    def getTriggerStatus1(self, moduleID=4):
        """获取触发器1位状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 4.

        Returns:
            Int: 查询失败返回-1;查询成功返回触发器接口第一位的状态,[1-高电平;0-低电平].

        Examples:
            >>>print(driver.getTriggerStatus1(4))
            1
        """
        recv_buf = self.getTriggerStatus(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[0]
        else:
            return -1

    def getTriggerStatus2(self, moduleID=4):
        """获取触发器2位状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 4.

        Returns:
            Int: 查询失败返回-1;查询成功返回触发器接口第二位的状态,[1-高电平;0-低电平].

        Examples:
            >>>print(driver.getTriggerStatus2(4))
            0
        """
        recv_buf = self.getTriggerStatus(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[1]
        else:
            return -1

    def getColorDetectStatus(self, moduleID=9):
        """获取颜色识别状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 9.

        Returns:
            List: 查询失败返回[-1,-1,-1,-1];查询成功返回[R,G,B,Color]具体含义如下.
            R: 颜色识别传感器识别到的颜色的R值.
            G: 颜色识别传感器识别到的颜色的G值.
            B: 颜色识别传感器识别到的颜色的B值.
            Color: 颜色识别传感器识别到的颜色值,可对照字典colorEncode解析.

        Examples:
            >>>print(driver.getColorDetectStatus(9))
            [255,79,79,1]
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x00C5, 0x04, 0)
        if recv_buf is not None:
            return [(recv_buf["data"]["数据"] >> 48) & 0xFFFF,
                    (recv_buf["data"]["数据"] >> 32) & 0xFFFF,
                    (recv_buf["data"]["数据"] >> 16) & 0xFFFF,
                    (recv_buf["data"]["数据"]) & 0xFFFF]
        else:
            return [-1, -1, -1, -1]

    def getColorDetectValueRGB(self, moduleID=9):
        """获取颜色识别RGB值

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 9.

        Returns:
            List: 查询失败返回[-1,-1,-1];查询成功返回[R,G,B]具体含义如下.
            R: 颜色识别传感器识别到的颜色的R值.
            G: 颜色识别传感器识别到的颜色的G值.
            B: 颜色识别传感器识别到的颜色的B值.

        Examples:
            >>>print(driver.getColorDetectValueRGB(9))
            [255,79,79]
        """
        recv_buf = self.getColorDetectStatus(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1 and recv_buf[2] != -1:
            return [recv_buf[0], recv_buf[1], recv_buf[2]]
        else:
            return [-1, -1, -1]

    def getColorDetectValueR(self, moduleID=9):
        """获取颜色识别R值

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 9.

        Returns:
            Int: 查询失败返回-1;查询成功返回颜色识别传感器识别到的颜色的R值.

        Examples:
            >>>print(driver.getColorDetectValueR(9))
            255
        """
        recv_buf = self.getColorDetectStatus(moduleID)
        if recv_buf[0] != -1:
            return recv_buf[0]
        else:
            return -1

    def getColorDetectValueG(self, moduleID=9):
        """获取颜色识别G值

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 9.

        Returns:
            Int: 查询失败返回-1;查询成功返回颜色识别传感器识别到的颜色的G值.

        Examples:
            >>>print(driver.getColorDetectValueG(9))
            79
        """
        recv_buf = self.getColorDetectStatus(moduleID)
        if recv_buf[1] != -1:
            return recv_buf[1]
        else:
            return -1

    def getColorDetectValueB(self, moduleID=9):
        """获取颜色识别B值

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 9.

        Returns:
            Int: 查询失败返回-1;查询成功返回颜色识别传感器识别到的颜色的B值.

        Examples:
            >>>print(driver.getColorDetectValueB(9))
            79
        """
        recv_buf = self.getColorDetectStatus(moduleID)
        if recv_buf[2] != -1:
            return recv_buf[2]
        else:
            return -1

    # 颜色数值转换
    def rgb888torgb565(self, n888Color):
        RGB888_RED = 0x00ff0000
        RGB888_GREEN = 0x0000ff00
        RGB888_BLUE = 0x000000ff

        n565Color = 0
        cRed = (n888Color & RGB888_RED) >> 19
        cGreen = (n888Color & RGB888_GREEN) >> 10
        cBlue = (n888Color & RGB888_BLUE) >> 3
        n565Color = (cRed << 11) + (cGreen << 5) + (cBlue << 0)
        return n565Color

    def getColorDetectValueRGB565(self, moduleID=9):
        """获取颜色识别RGB565值
        """
        recv_buf = self.getColorDetectStatus(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1 and recv_buf[2] != -1:
            rbg888 = (recv_buf[0] << 16) + (recv_buf[1] << 8) + recv_buf[2]
            return self.rgb888torgb565(rbg888)
        else:
            return -1

    def getColorDetectColor(self, moduleID=9):
        """获取颜色识别传感器识别的部分颜色.

        Note:
            识别到的颜色存在误差，仅供参考.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 9.

        Returns:
            Int: 查询失败返回-1;查询成功返回颜色识别传感器识别到的颜色值,可对照字典colorEncode解析.

        Examples:
            >>>print(driver.getColorDetectColor(9))
            1
        """
        recv_buf = self.getColorDetectStatus(moduleID)
        if recv_buf[3] != -1:
            if recv_buf[3] in self.colorEncode:
                return recv_buf[3]
            else:
                return -1
        else:
            return -1

    ########################## 以下是设备控制控制方法 ############################
    def playSpeech(self, moduleID=1, speech="你好"):
        """语音合成,播放语音.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 1.
            speech (str, optional): 要播放的语音字符串,只能为gbk编码的汉字字符串. Defaults to "你好".

        Examples:
            # 控制1号接口语音合成,播放"你好小飞同学".
            >>>driver.playSpeech(1, "你好小飞同学")
        """
        if isinstance(moduleID, int) is False or isinstance(speech,
                                                            str) is False:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        VOICE = speech.encode('gbk')
        OUT = []  # 指令存储
        OUT.append(moduleID)  # 主机号
        OUT.append(0x10)  # 写功能码
        OUT.append(0x01)
        OUT.append(0x04)  # 地址位
        # 以下组装数据段
        if len(VOICE) > 50:
            print("语音超出限定长度:55")
        else:
            # 1、计算地址长度（GBK编码）
            if len(VOICE) % 2 == 0:
                addr_len = len(VOICE) / 2
            else:
                addr_len = len(VOICE) / 2 + 1
            addr_len += 3
            OUT.append((int(addr_len) >> 8) & 0xFF)
            OUT.append(int(addr_len) & 0xFF)  # 地址长度
            OUT.append(int(addr_len) * 2)  # 占位数据长度
            # 2、功能码
            OUT.append(0x00)
            OUT.append(0x01)
            # 3、语音编码长度
            OUT.append(0x00)
            if len(VOICE) % 2 == 0:
                OUT.append(len(VOICE))
            else:
                OUT.append(len(VOICE) + 1)
            # 4、编码类型
            OUT.append(0x00)
            OUT.append(0x01)
            # 5、打印语音编码
            for index in range(len(VOICE)):
                OUT.append(VOICE[index])
            if len(VOICE) % 2 != 0:
                OUT.append(0x00)
            # 6、添加crc16校验
            crc16_obj = CRC16()
            OUT = crc16_obj.create_array(OUT)
            # 7、打印结果
            # for index in range(len(OUT)):
            #     print("%02X"%(OUT[index]),end=" ")
            # print("")
            LOGGER.print_hex(OUT, "语音合成编码:")
            self.sendRawDataRightAway(OUT)
            time.sleep(self.wait_time)

    def setPulseOutput(self, moduleID=5, period=20000000, pulse=500000):
        """脉冲输出.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 5.
            period (int, optional): 周期，范围(1~4294967295). Defaults to 20000000.
            pulse (int, optional): 脉冲宽度，范围(0~4294967295). Defaults to 500000.

        Returns:
            Boolean: False:参数校验失败/设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功

        Examples:
            # 控制5号接口脉冲,输出周期20000000ms,高电平时间500000ms.
            >>>driver.setPulseOutput(5, 20000000, 500000)
        """
        if period > 0xFFFFFFFF or period < 1 or pulse < 0 or pulse > 0xFFFFFFFF or period < pulse:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        return self.excuteOrder(self.send_time, "10号写指令", int(moduleID),
                                0x0102, 0x05, 0x0A, ((0x0001) << 64) |
                                ((int(period) & 0xFFFFFFFF) << 32) |
                                (int(pulse) & 0xFFFFFFFF), 0)

    def getPulseOutput(self, moduleID=5):
        """获取脉冲输出状态.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 5.

        Returns:
            List: 失败返回[-1,-1];读出成功返回[period,pulse].具体含义如下.
            period: 周期,单位ms.
            pulse: 脉冲宽度,单位ms.

        Examples:
            >>>print(driver.getPulseOutput(5, 20000000, 500000))
            [20000000,500000]
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x0102, 0x05, 0)
        if recv_buf is not None:
            return [(recv_buf["data"]["数据"] >> 32) & 0x00FFFFFFFF,
                    recv_buf["data"]["数据"] & 0x00FFFFFFFF]
        else:
            return [-1, -1]

    def setServoAngle(self, moduleID=5, angle=0):
        """设置SG90舵机角度.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 5.
            angle (int, optional): 舵机角度,范围(0~180). Defaults to 0.

        Returns:
            Boolean: False:参数校验失败/设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功.

        Examples:
            # 控制5号接口脉冲,控制SG90舵机到90°.
            >>>driver.setServoAngle(5, 90)
        """
        if angle > 180:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        return self.excuteOrder(self.send_time, "10号写指令", int(moduleID),
                                0x0102, 0x02, 0x04,
                                ((0x0002) << 16) | ((int(angle) & 0xFFFF)), 0)

    def getServoAngle(self, moduleID=5):
        """脉冲控制--获取SG90舵机角度.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 5.

        Returns:
            Int: 失败返回-1;成功返回舵机角度,单位°.

        Examples:
            >>>print(driver.getServoAngle(5))
            90
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x0102, 0x02, 0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"] & 0x00FF
        else:
            return -1

    def setOutput5V(self, moduleID=10, status=0):
        """IO控制-控制输出

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 10.
            status (int, optional): 输出状态:[0-关闭;1-打开]. Defaults to 0.

        Returns:
            Boolean: False:参数校验失败/设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功.

        Examples:
            # 控制10号接口5V输出,控制电平为高.
            >>>driver.setOutput5V(10, 1)
        """
        if status > 1:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        return self.excuteOrder(self.send_time, "10号写指令", int(moduleID),
                                0x0103, 0x01, 0x02, ((int(status) & 0xFFFF)),
                                0)

    def openOutput5V(self, moduleID=10):
        """打开指定接口的5V输出.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 10.

        Returns:
            Boolean: False:设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功

        Examples:
            # 控制10号接口5V输出,控制电平为高.
            >>>driver.openOutput5V(10)
        """
        return self.setOutput5V(moduleID, 1)

    def closeOutput5V(self, moduleID=10):
        """关闭指定接口的5V输出.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 10.

        Returns:
            Boolean: False:设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功.

        Examples:
            # 控制10号接口5V输出,控制电平为低.
            >>>driver.closeOutput5V(10).30
        """
        return self.setOutput5V(moduleID, 0)

    def getOutput5V(self, moduleID=10):
        """IO控制-获取输出状态

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 10.

        Returns:
            Int: 失败返回-1;成功返回输出端口的状态:[0-关闭;1-打开]

        Examples:
            >>>print(driver.getOutput5V(10))
            1
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x0103, 0x01, 0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"] & 0x00FF
        else:
            return -1

    def setMotor5V(self,
                   moduleID=13,
                   status=0,
                   speed=0,
                   countdown=0,
                   countdown_enable=0):
        """控制直流电机状态、转速、延时关闭

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 13.
            status (int, optional): 电机的状态:[0-关闭;1-正转;2-反转;3-刹车]. Defaults to 0.
            speed (int, optional): 速度:范围(0~100). Defaults to 0.
            countdown (int, optional): 延时关闭:范围(0~65535). Defaults to 0.
            countdown_enable (int, optional): 延时关闭功能使能:[0-关闭;1-打开]. Defaults to 0.

        Returns:
            Boolean: False:参数校验失败/设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功.

        Examples:
            # 控制13号接口5V电机,控制电机以100%速度转动2秒.
            >>>driver.setMotor5V(13, 1, 100, 2, 1)
        """
        if status > 3 or speed > 100 or countdown > 0xFFFF:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        return self.excuteOrder(
            self.send_time, "10号写指令", int(moduleID), 0x0106, 0x04, 0x08,
            ((int(status) & 0xFFFF) << 48) | ((int(speed) & 0xFFFF) << 32) |
            ((int(countdown) & 0xFFFF) << 16) |
            ((int(countdown_enable) & 0xFFFF)), 0)

    def getMotor5VAllStatus(self, moduleID=13):
        """获取直流电机状态、转速、延时关闭信息.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 13.

        Returns:
            List:读取失败返回[-1, -1, -1, -1];读取成功返回[status,speed,countdown,countdown_enable]具体含义如下.
            status (int): 电机的状态:[0-关闭;1-正转;2-反转;3-刹车].
            speed (int): 速度:范围(0~100). 
            countdown (int): 延时关闭:范围(0~65535). 
            countdown_enable (int): 延时关闭功能使能:[0-关闭;1-打开]. 

        Examples:
            >>>print(driver.getMotor5VAllStatus(13))
            [1,100,2,1]
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x0106, 0x04, 0)
        if recv_buf is not None:
            return [(recv_buf["data"]["数据"] >> 48) & 0x00FFFF,
                    (recv_buf["data"]["数据"] >> 32) & 0x00FFFF,
                    (recv_buf["data"]["数据"] >> 16) & 0x00FFFF,
                    recv_buf["data"]["数据"] & 0x00FFFF]
        else:
            return [-1, -1, -1, -1]

    def getMotor5V(self, moduleID=13):
        """获取直流电机状态、转速.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 13.

        Returns:
            List: 失败返回[-1,-1];读取成功返回[status,speed],具体含义如下.
            status (int): 电机的状态:[0-关闭;1-正转;2-反转;3-刹车].
            speed (int): 速度:范围(0~100). 

        Examples:
            >>>print(driver.getMotor5V(13))
            [1,100]
        """
        recv_buf = self.getMotor5VAllStatus(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return [recv_buf[0], recv_buf[1]]
        else:
            return [-1, -1]

    def getMotorStatus(self, moduleID=13):
        """获取直流电机状态.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 13.

        Returns:
            Int: 失败返回-1;读取成功返回电机的状态:[0-关闭;1-正转;2-反转;3-刹车].

        Examples:
            >>>print(driver.getMotorStatus(13))
            1
        """
        recv_buf = self.getMotor5V(moduleID)
        if recv_buf[0] != -1:
            return recv_buf[0]
        else:
            return -1

    def getMotorSpeed(self, moduleID=13):
        """获取直流电机速度.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 13.

        Returns:
            Int: 失败返回-1;读取成功返回电机的设定速度.

        Examples:
            >>>print(driver.getMotorSpeed(13))
            100
        """
        recv_buf = self.getMotor5V(moduleID)
        if recv_buf[1] != -1:
            return recv_buf[1]
        else:
            return -1

    def setMotorClockwise(self, moduleID=13, speed=0):
        """控制直流电机正转的速度.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 13.
            speed (int, optional): 速度:范围(0~100). Defaults to 0.

        Returns:
            Boolean: False:参数校验失败/设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功.

        Examples:
            # 控制13号接口5V电机,控制电机以100%速度正转.
            >>>driver.setMotorClockwise(13, 100)
        """
        if speed > 100:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        return self.setMotor5V(moduleID, 1, speed, 0, 0)

    def setMotorClockwiseTime(self, moduleID=13, speed=0, countdown=0):
        """控制直流电机正转一段时间.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 13.
            speed (int, optional): 速度:范围(0~100). Defaults to 0.
            countdown (float|int, optional): 时间(0~600),单位s. Defaults to 0.

        Returns:
            Boolean: False:参数校验失败/设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功.

        Examples:
            # 控制13号接口5V电机,控制电机以100%速度正转2秒.
            >>>driver.setMotorClockwiseTime(13, 100, 2)
        """
        if speed > 100 or countdown > 600 or countdown < 0:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        return self.setMotor5V(moduleID, 1, speed,
                               int(round(countdown, 2) * 100), 1)

    def setMotorCounterclockwise(self, moduleID=13, speed=0):
        """控制直流电机反转的速度.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 13.
            speed (int, optional): 速度:范围(0~100). Defaults to 0.

        Returns:
            Boolean: False:参数校验失败/设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功.

        Examples:
            # 控制13号接口5V电机,控制电机以100%速度反转.
            >>>driver.setMotorCounterclockwise(13, 100)
        """
        if speed > 100:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        return self.setMotor5V(moduleID, 2, speed, 0, 0)

    def setMotorCounterclockwiseTime(self, moduleID=13, speed=0, countdown=0):
        """控制直流电机反转一段时间.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 13.
            speed (int, optional): 速度:范围(0~100). Defaults to 0.
            countdown (float|int, optional): 时间(0~600),单位s. Defaults to 0.

        Returns:
            Boolean: False:参数校验失败/设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功.

        Examples:
            # 控制13号接口5V电机,控制电机以100%速度反转2秒.
            >>>driver.setMotorCounterclockwiseTime(13, 100, 2)
        """
        if speed > 100 or countdown > 600 or countdown < 0:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        return self.setMotor5V(moduleID, 2, speed,
                               int(round(countdown, 2) * 100), 1)

    def setMotorBrakes(self, moduleID=13):
        """控制直流电机刹车.

        Note:
            这是一种特殊的状态,它能以电机最大的力矩锁住电机,既不正转也不反转.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 13.

        Returns:
            Boolean: False:设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功.

        Examples:
            # 控制13号接口5V电机刹车.
            >>>driver.setMotorBrakes(13)
        """
        return self.setMotor5V(moduleID, 3, 0, 0, 0)

    def setMotorStop(self, moduleID=13):
        """控制直流电机停止.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 13.

        Returns:
            Boolean: False:设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功.

        Examples:
            # 控制13号接口5V电机停止.
            >>>driver.setMotorStop(13)
        """
        return self.setMotor5V(moduleID, 0, 0, 0, 0)

    def setLanternMode(self, moduleID=6, mode=0, led_num=20):
        """设置彩灯模式和数量

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 6.
            mode (int, optional): 模式:范围(0~8、255),[0-关闭;1~7-单色;8-流水灯;255-特殊模式]. Defaults to 0.
            led_num (int, optional): 控制的彩灯数量,mode=255时该参数无效. Defaults to 20.

        Returns:
            Boolean: False:参数校验失败/设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功.

        Examples:
            # 控制6号接口彩灯以模式1亮起20盏灯.
            >>>driver.setLanternMode(6, 1, 20)
        """
        if (mode > 8 and mode != 0xFF) or led_num > 60:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        return self.excuteOrder(
            self.send_time, "10号写指令", int(moduleID), 0x00AE, 0x03, 0x06,
            ((int(0x0001) << 32) | ((int(mode) & 0xFFFF) << 16) |
             ((int(led_num) & 0xFFFF))), 0)

    def getLanternStatus(self, moduleID=6):
        """获取彩灯当前模式和数量

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 6.

        Returns:
            List: 失败返回[-1,-1];读取成功返回[mode,led_num],具体含义如下.
            mode: 模式:[0-关闭;1~7-单色;8-流水灯;255-特殊模式].
            led_num: 控制的彩灯数量,mode=255时该参数无效.

        Examples:
            >>>print(driver.getLanternStatus(6))
            [1,20]
        """
        recv_buf = self.queryOrder(self.wait_time, "03号查询指令", int(moduleID),
                                   0x00AE, 0x03, 0)
        if recv_buf is not None:
            return [(recv_buf["data"]["数据"] >> 16) & 0x00FFFF,
                    recv_buf["data"]["数据"] & 0x00FFFF]
        else:
            return [-1, -1]

    def getLanternMode(self, moduleID=6):
        """获取彩灯模式

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 6.

        Returns:
            Int: 失败返回-1;读取成功返回当前彩灯模式:[0-关闭;1~7-单色;8-流水灯;255-特殊模式].

        Examples:
            >>>print(driver.getLanternMode(6))
            1
        """
        recv_buf = self.getLanternStatus(moduleID)
        if recv_buf[0] != -1:
            return recv_buf[0]
        else:
            return -1

    def getLanternNum(self, moduleID=6):
        """获取彩灯数量

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 6.

        Returns:
            Int: 失败返回-1;读取成功返回当前控制的彩灯数量,mode=255时该参数无效.

        Examples:
            >>>print(driver.getLanternNum(6))
            20
        """
        recv_buf = self.getLanternStatus(moduleID)
        if recv_buf[1] != -1:
            return recv_buf[1]
        else:
            return -1

    def setLanternSpecialMode(self, moduleID=6):
        """控制彩灯进入特殊模式.
        
        Note:
            在该模式下可以配合setLanternByEachLedColor()方法来控制每盏灯的颜色.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 6.

        Returns:
            Boolean: False:设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功.

        Examples:
            # 控制6号接口彩灯进入特殊模式.
            >>>driver.setLanternSpecialMode(6)
        """
        return self.setLanternMode(int(moduleID), 0xFF, 0)

    def setLanternByEachLedColor(self,
                                 moduleID=6,
                                 led_num=3,
                                 led_color=[0xF800, 0x07E0, 0x001F]):
        """单独控制每盏灯的颜色.
        
        Note:
            配合setLanternSpecialMode()方法使用,在mode=255时生效.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 6.
            led_num (int, optional): 控制的灯的数量,范围(0~60). Defaults to 3.
            led_color (list, optional): 每盏灯的颜色列表,颜色格式为RGB565. Defaults to [0xF800, 0x07E0, 0x001F].

        Returns:
            Boolean: False:参数校验失败/设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功

        Examples:
            # 控制6号接口彩灯的前三盏依次亮起红、绿、蓝.
            >>>driver.setLanternSpecialMode(6)
            >>>driver.setLanternByEachLedColor(6, 3, [0xF800, 0x07E0, 0x001F])
        """
        if led_num > 60 or isinstance(
                led_color, list) is False or led_num != len(led_color):
            LOGGER.logger.error(f"Parameter setting error!")
            return False

        order_num = led_num + 2
        order = 0x0002
        order = (int(order) << 16) | (led_num & 0x0FFFF)
        for num in range(led_num):
            order = ((int(order) << 16) | led_color[num])
        return self.excuteOrder(self.send_time, "10号写指令", int(moduleID),
                                0x00AE, order_num, order_num * 2, order, 0)

    def setLanternByLedColor(self, moduleID=6, led_num=3, led_rgb565=0):
        """控制彩灯亮起同一种自定义颜色.
        
        Note:
            配合setLanternSpecialMode()方法使用,在mode=255时生效.

        Args:
            moduleID (int, optional): 硬件接口号. Defaults to 6.
            led_num (int, optional): 控制的灯的数量,范围(0~60). Defaults to 3.
            led_rgb565 (int, optional): 灯的颜色,颜色格式为RGB565. Defaults to 0.

        Returns:
            Boolean: False:参数校验失败/设置返回校验后且未校验成功返回数据;True:设置返回校验后且校验成功

        Examples:
            # 控制6号接口彩灯的前三盏亮起红色.
            >>>driver.setLanternSpecialMode(6)
            >>>driver.setLanternByLedColor(6, 3, 0xF800)
        """
        if led_num > 60 or led_num > 0xFF:
            LOGGER.logger.error(f"Parameter setting error!")
            return False
        color = []
        for num in range(led_num):
            color.append(led_rgb565)
        return self.setLanternByEachLedColor(int(moduleID), int(led_num),
                                             color)
