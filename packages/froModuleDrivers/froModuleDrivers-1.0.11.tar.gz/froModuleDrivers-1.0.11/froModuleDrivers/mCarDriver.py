# -*- encoding=utf-8 -*-

from .baseDriver import BaseDriver
from .protocolHandler import *
from . import LOGGER
import time

tarVersion = "V20210909"

VersionDetail = "当前版本:" + tarVersion + """
---------------------------版本更新信息----------------------------

可调用方法的API文档请访问:http://www.chuangfeigu.com:9900/web/#/64?page_id=1189

V20210909:
1.使用新的框架来实现旧的api

V20220627:
1.添加API说明

------------------------------------------------------------------
"""


class CarDict():
    car_status = {
        "车速": -1,
        "设定车速": -1,
        "卡号": -1,
        "电压": -1,
        "轨道": -1,
        "模式": -1,
        "充电状态": -1,
        "电压": -1,
        "测距距离": -1,
        "前探头状态": -1,
        "后探头状态": -1,
    }
    infr_dict = {0: "黑色", 1: "白色"}
    charge_dict = {1: "未充电", 2: "充满", 3: "充电中"}


class MCarDriver(BaseDriver, CarDict):
    def __init__(self, host="localhost", port=4001):
        super().__init__(host, port)
        self.addProtocol(K210ProtocolHandler())
        self.addProtocol(K12ProtocolHandler())
        self.__max_led_num = 18  # 车载彩灯个数
        self.__max_speed = 50  # 车速上限
        self.wait_time = 1

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

    # 直接发送指令的原始数据帧
    def sendRawDataRightAway(self, hex_array):
        if hex_array is None:
            return
        self.connector.sendData(self.getClientId(),
                                bytes(bytearray(hex_array)),
                                prior=False)

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

    def cnvHexArrayToHex(self, hex_array=None, scale=16):
        if hex_array is None:
            return 0
        hex_len = len(hex_array)
        result = 0
        for i in range(hex_len):
            result = result << scale
            result |= hex_array[i]
        return result

    def cnvHexToHexArray(self, hex_value=None, scale=16):
        if hex_value is None or isinstance(hex_value,
                                           int) is False or hex_value < 0:
            return []
        result = []
        while True:
            if hex_value == 0:
                break
            result.insert(0, hex_value & (2**(scale) - 1))
            hex_value = hex_value >> scale
        return result

    ########################## 以下是小车通用控制方法 ############################

    def getFirmwareVersion(self):
        """查询固件版本

        Returns:
            Boolean: False 查询失败
            List:[major,minor,modify]
        """
        recv_buf = self.queryOrder(self.wait_time, "查询固件版本")
        if recv_buf is not None:
            return [((recv_buf["data"]["版本号"] >> 16) & 0xFF),
                    ((recv_buf["data"]["版本号"] >> 8) & 0xFF),
                    (recv_buf["data"]["版本号"] & 0xFF)]
        else:
            return False

    def startCar(self):
        """启动小车/小车前进
        """
        self.excuteOrderRightAway("前进/启动")

    def stopCar(self):
        """小车停止
        """
        self.excuteOrderRightAway("停车")

    def turnLeftOrigin(self):
        """小车原地左转

         Note:
            自动模式下,小车会向左转一个小角度，然后探头会进入找黑色模式，找到黑色即可停止，然后恢复到正常循迹模式
        
        """
        self.excuteOrderRightAway("原地左转")

    def turnRightOrigin(self):
        """小车原地右转

         Note:
            自动模式下,小车会向右转一个小角度，然后探头会进入找黑色模式，找到黑色即可停止，然后恢复到正常循迹模式
        
        """
        self.excuteOrderRightAway("原地右转")

    def setCarAutoMode(self):
        """设置为自动模式
        """
        self.excuteOrderRightAway("自动模式")

    def setCarManualMode(self):
        """设置为手动模式
        """
        self.excuteOrderRightAway("手动模式")

    def setCarSingleWheelControlMode(self):
        """设置为单轮控制模式
        """
        self.excuteOrderRightAway("单个轮子控制模式")

    def setCarSpeed(self, tarSpeed=25):
        """设置车速

        Args:
            tarSpeed (int, optional): 车速，范围是（10~50）. Defaults to 25.

        Returns:
            Boolean: 设置失败返回False
        """
        if tarSpeed < 10 or tarSpeed > 50:
            LOGGER.logger.error("fun setCarSpeed：设置的车速必须在10~50")
            return False
        self.excuteOrderRightAway("设置速度", int(tarSpeed) & 0xFF)

    def refreshStatusForced(self):
        """强制刷新小车信息

        Returns:
            dict: 详见 car_status
            Boolean: 失败返回False
        """
        recv_buf = self.queryOrder(self.wait_time, "读寄存器-底层板", 0x0001, 14)
        if recv_buf is not None:
            self.car_status["设定车速"] = recv_buf["data"]["寄存器数据"] & 0xFFFF  # 14
            # self.car_status["自动模式下控制"] = (
            #     recv_buf["data"]["寄存器数据"] >> 16) & 0xFFFF  # 13
            self.car_status["模式"] = (
                recv_buf["data"]["寄存器数据"] >> 32) & 0xFFFF  # 12
            # self.car_status["模式"] = (
            #     recv_buf["data"]["寄存器数据"] >> 48) & 0xFFFF  # 11
            # self.car_status["设定车速"] = (
            #     recv_buf["data"]["寄存器数据"] >> 64) & 0xFFFF # 10
            self.car_status["后探头状态"] = (
                recv_buf["data"]["寄存器数据"] >> 80) & 0xFFFF  # 9
            self.car_status["前探头状态"] = (
                recv_buf["data"]["寄存器数据"] >> 96) & 0xFFFF  # 8
            self.car_status["测距距离"] = (
                recv_buf["data"]["寄存器数据"] >> 112) & 0xFFFF  # 7
            # self.car_status["电池功率"] = (
            #     recv_buf["data"]["寄存器数据"] >> 128) & 0xFFFF # 6
            self.car_status["电量"] = (
                recv_buf["data"]["寄存器数据"] >> 144) & 0xFFFF  # 5
            self.car_status["电压"] = (
                (recv_buf["data"]["寄存器数据"] >> 160) & 0xFFFF) / 100.0  # 4
            self.car_status["充电状态"] = (
                recv_buf["data"]["寄存器数据"] >> 176) & 0xFFFF  # 3
            self.car_status["小车速度"] = (
                recv_buf["data"]["寄存器数据"] >> 192) & 0xFFFF  # 2
            self.car_status["卡号"] = (
                recv_buf["data"]["寄存器数据"] >> 208) & 0xFFFF  # 1
            return self.car_status
        else:
            return False

    def refreshStatus(self):
        """刷新小车缓存信息

        Returns:
            dict: 详见 car_status
            Boolean: 失败返回False
        """
        recv_buf = self.queryOrder(self.wait_time, "读寄存器-缓冲区", 0x0001, 14)
        if recv_buf is not None:
            self.car_status["设定车速"] = recv_buf["data"]["寄存器数据"] & 0xFFFF  # 14
            # self.car_status["自动模式下控制"] = (
            #     recv_buf["data"]["寄存器数据"] >> 16) & 0xFFFF  # 13
            self.car_status["模式"] = (
                recv_buf["data"]["寄存器数据"] >> 32) & 0xFFFF  # 12
            # self.car_status["模式"] = (
            #     recv_buf["data"]["寄存器数据"] >> 48) & 0xFFFF  # 11
            # self.car_status["设定车速"] = (
            #     recv_buf["data"]["寄存器数据"] >> 64) & 0xFFFF # 10
            self.car_status["后探头状态"] = (
                recv_buf["data"]["寄存器数据"] >> 80) & 0xFFFF  # 9
            self.car_status["前探头状态"] = (
                recv_buf["data"]["寄存器数据"] >> 96) & 0xFFFF  # 8
            self.car_status["测距距离"] = (
                recv_buf["data"]["寄存器数据"] >> 112) & 0xFFFF  # 7
            # self.car_status["电池功率"] = (
            #     recv_buf["data"]["寄存器数据"] >> 128) & 0xFFFF # 6
            self.car_status["电量"] = (
                recv_buf["data"]["寄存器数据"] >> 144) & 0xFFFF  # 5
            self.car_status["电压"] = (
                (recv_buf["data"]["寄存器数据"] >> 160) & 0xFFFF) / 100.0  # 4
            self.car_status["充电状态"] = (
                recv_buf["data"]["寄存器数据"] >> 176) & 0xFFFF  # 3
            self.car_status["小车速度"] = (
                recv_buf["data"]["寄存器数据"] >> 192) & 0xFFFF  # 2
            self.car_status["卡号"] = (
                recv_buf["data"]["寄存器数据"] >> 208) & 0xFFFF  # 1
            return self.car_status
        else:
            return False

    def getCarStatus(self):
        """获取小车信息，车速、卡号、电压、轨道、模式
        红色小车可以使用refreshStatus()替换该命令

        Returns:
            dict: 详见car_status
            Boolean: 失败返回False
        """
        recv_buf = self.queryOrder(self.wait_time, "查询小车状态")
        if recv_buf is not None:
            self.car_status["车速"] = recv_buf["data"]["车速"]
            self.car_status["卡号"] = ((recv_buf["data"]["卡号H"] & 0xFF) << 8) | (
                recv_buf["data"]["卡号L"] & 0xFF)
            self.car_status["电压"] = recv_buf["data"]["电压"] / 100.0
            self.car_status["轨道"] = recv_buf["data"]["轨道"]
            self.car_status["模式"] = recv_buf["data"]["模式"]
            return self.car_status
        else:
            return False

    def getDistance(self):
        """获取测距距离

        Returns:
            int: 测距距离
            Boolean: 失败返回False
        """
        recv_buf = self.queryOrder(self.wait_time, "查询距离")
        if recv_buf is not None:
            self.car_status["测距距离"] = ((recv_buf["data"]["距离H"] & 0xFF) <<
                                       8) | (recv_buf["data"]["距离L"] & 0xFF)
            return self.car_status["测距距离"]
        else:
            return False

    def playCarSpeech(self, speech="你好"):
        """播放语音

        Args:
            speech (str, optional): 待播放的语音字符串. Defaults to "你好".
        """
        speech_data = speech.encode('gbk')
        speech_synthesis_buf = []
        if len(speech_data) > 55:
            LOGGER.logger.error("语音超出限定长度:55")
        else:
            # 1、打印帧头和功能码
            HEAD = [0xA0, 0x02, 0xFC]
            for index in range(len(HEAD)):
                speech_synthesis_buf.append(HEAD[index])
            # 2、打印语音编码长度
            speech_synthesis_buf.append(len(speech_data))
            # 3、打印编码类型
            speech_synthesis_buf.append(0x01)
            # 4、打印语音编码
            for index in range(len(speech_data)):
                speech_synthesis_buf.append(speech_data[index])
            # 5、打印帧尾
            TAIL = [0x0D, 0x0A]
            for index in range(len(TAIL)):
                speech_synthesis_buf.append(TAIL[index])
        # print(speech_synthesis_buf)
        # print(bytearray(speech_synthesis_buf))
        self.sendRawDataRightAway(speech_synthesis_buf)

    def playCarSpeechInside(self, speech_num=1):
        """播放内置语音

        Args:
            speech_num (int, optional): 内置语音编号(1~30). Defaults to 1.

        Returns:
            Boolean: 参数错误返回False
        """
        if speech_num < 0 or speech_num > 30:
            LOGGER.logger.warning("没有编号为{speech_num}的语音")
            return False
        self.excuteOrderRightAway("播放内置语音", int(speech_num) & 0xFF)

    def setLanternMode(self, mode_num=0):
        """设置灯光模式

        Args:
            mode_num (int, optional): 灯光模式(0~8、0xff),0xff为特殊模式. Defaults to 0.

        Returns:
            Boolean: 参数错误返回False
        """
        if mode_num != 0xFF:
            if mode_num < 0 or mode_num > 20:
                LOGGER.logger.warning("没有编号为{mode_num}的灯光模式")
                return False
        self.excuteOrderRightAway("设置灯光模式", int(mode_num) & 0xFF)

    def setLantern(self, colors):
        """设置自定义颜色

        Parameters
        ----------
        colors : list[int]
            由int型组成的列表，索引号为0的int数据控制第一个的LED，
            索引号为1的int数据控制第二行的LED，以此类推。

            int数据中的bit7-bit0: 蓝色亮度；
            bit15-bit8: 绿色亮度；
            bit23-bit16: 红色亮度；

            亮度范围: 0-255

        Examples
        --------
        >>> car.setLanternMode(0xFF) # 设置为自定义模式
        >>> # 设置前4盏灯的颜色，分别是白色，红色，蓝色和绿色
        >>> colors = [0xffffff,0xff0000,0x00ff00,0x0000ff]
        >>> car.setLantern(colors) # 设置车灯颜色，只有在自定义模式下才有效
        """
        if len(colors) > self.__max_led_num:
            colors = colors[:self.__max_led_num]
        elif len(colors) < self.__max_led_num:
            colors += [0] * (self.__max_led_num - len(colors))

        color_value = self.cnvHexArrayToHex(colors, 24)
        self.excuteOrderRightAway("设置灯光", color_value)

    def getInfrStatus(self):
        """获取小车探头状态信息

        Returns:
            Boolean: 获取失败
            List[int]:0位是前探头状态，1位是后探头状态，按二进制bit解析后四位。0: "黑色", 1: "白色"
        """
        recv_buf = self.queryOrder(self.wait_time, "查询探头状态")
        if recv_buf is not None:
            return [recv_buf["data"]["前探头状态"], recv_buf["data"]["后探头状态"]]
        else:
            return False

    def setCarExpandPWM(self,
                        period=20000000,
                        pulse1=500000,
                        pulse2=500000,
                        pulse3=500000,
                        pulse4=500000):
        """设置脉冲输出

        Args:
            period (int, optional): 周期，范围（0~0xFFFFFFFF）. Defaults to 20000000.
            pulse1 (int, optional): 1号脉冲宽度，范围（0~0xFFFFFFFF）. Defaults to 500000.
            pulse2 (int, optional): 2号脉冲宽度，范围（0~0xFFFFFFFF）. Defaults to 500000.
            pulse3 (int, optional): 3号脉冲宽度，范围（0~0xFFFFFFFF）. Defaults to 500000.
            pulse4 (int, optional): 4号脉冲宽度，范围（0~0xFFFFFFFF）. Defaults to 500000.

        Returns:
            Boolean: 参数错误返回False
        """
        if isinstance(period, int) is False or isinstance(
                pulse1, int) is False or isinstance(
                    pulse2, int) is False or isinstance(
                        pulse3, int) is False or isinstance(pulse4,
                                                            int) is False:
            LOGGER.logger.error("fun setCarExpandPWM parameter must be int!")
            return False
        self.excuteOrderRightAway("设置脉冲输出",
                                  int(period) & 0xFFFFFFFF,
                                  int(pulse1) & 0xFFFFFFFF,
                                  int(pulse2) & 0xFFFFFFFF,
                                  int(pulse3) & 0xFFFFFFFF,
                                  int(pulse4) & 0xFFFFFFFF)

    def setCarExpandPWMSingle(self, ch=1, period=20000000, pulse=500000):
        """设置单个脉冲输出

        Args:
            ch (int, optional): 通道（1~4）. Defaults to 1.
            period (int, optional): 周期，范围（0~0xFFFFFFFF）. Defaults to 20000000.
            pulse (int, optional): 脉冲宽度，范围（0~0xFFFFFFFF）. Defaults to 500000.
        
        Returns:
            Boolean: 参数错误返回False
        """
        if isinstance(ch, int) is False or isinstance(
                period, int) is False or isinstance(pulse, int) is False:
            LOGGER.logger.error(
                f"fun setCarExpandPWMSingle parameter must be int!")
            return False
        if ch <= 0 or ch > 4:
            LOGGER.logger.error(f"fun setCarExpandPWMSingle ch range(1~4)")
            return False
        self.excuteOrderRightAway("设置脉冲输出-单个",
                                  int(ch) & 0xFF,
                                  int(period) & 0xFFFFFFFF,
                                  int(pulse) & 0xFFFFFFFF)

    ########################## 以下是小车自动模式下的控制方法 ############################

    def parkPoint(self, tarPoint=0):
        """定点停车

        Args:
            tarPoint (int, optional): 停车卡号（1~0xFFFF）. Defaults to 0.

        Returns:
            Boolean: 参数错误返回False
        """
        if isinstance(tarPoint, int) is False:
            LOGGER.logger.error("fun parkPoint parameter must be int!")
            return False
        self.excuteOrderRightAway("定点停车", 1, int(tarPoint) & 0xFFFF)

    def setTurnCard(self, left_card=None, right_card=None):
        """设置转向点

        Args:
            left_card (list[int], optional): 左转点，最多设置19个，设置0个为None. Defaults to None.
            right_card (list[int], optional): 右转点，最多设置19个，设置0个为None. Defaults to None.

        Returns:
            Boolean: 参数错误返回False
        Examples
        --------
        >>> car.setTurnCard([0x0001],[0x0002,0x0003]) # 设置1个左转点，2个右转点
        >>> car.setTurnCard([],[0x0002]) # 设置0个左转点，1个右转点
        """
        # 校验左转参数
        if left_card is None:
            left_num = 0
            left_card_h = 0
            left_card_l = 0
        else:
            if isinstance(left_card, int) is True:
                left_num = 1
                card_value = left_card
            elif isinstance(left_card, list) is True:
                left_num = len(left_card)
                card_value = self.cnvHexArrayToHex(left_card)
            else:
                LOGGER.logger.error(
                    "fun setTurnCard parameter: left_card must be list!")
                return False
            left_card_h = card_value >> (left_num * 8)
            left_card_l = card_value & (2**(left_num * 8) - 1)

        # 校验右转参数
        if right_card is None:
            right_num = 0
            right_card_h = 0
            right_card_l = 0
        else:
            if isinstance(right_card, int) is True:
                right_num = 1
                card_value = right_card
            elif isinstance(right_card, list) is True:
                right_num = len(right_card)
                card_value = self.cnvHexArrayToHex(right_card)
            else:
                LOGGER.logger.error(
                    "fun setTurnCard parameter: right_card must be list!")
                return False
            right_card_h = card_value >> (right_num * 8)
            right_card_l = card_value & (2**(right_num * 8) - 1)
        # 发送命令
        self.excuteOrderRightAway("转向点设置", left_num, left_card_h, left_card_l,
                                  right_num, right_card_h, right_card_l)

    def setTurnLeftCard(self, left_card=None):
        """设置左转点

        Args:
            left_card (List[int], optional): 左转点，最多设置19个，设置0个为None. Defaults to None.

        Returns:
            Boolean: 参数错误返回False
        Examples
        --------
        >>> car.setTurnLeftCard([0x0001,0x0002]) # 设置2个左转点，卡号是0x0001和0x0002
        >>> car.setTurnLeftCard([]) # 清除左转点
        """
        # 校验左转参数
        if left_card is None:
            left_num = 0
            left_card_h = 0
            left_card_l = 0
        else:
            if isinstance(left_card, int) is True:
                left_num = 1
                card_value = left_card
            elif isinstance(left_card, list) is True:
                left_num = len(left_card)
                card_value = self.cnvHexArrayToHex(left_card)
            else:
                LOGGER.logger.error(
                    "fun setTurnCard parameter: left_card must be list!")
                return False
            left_card_h = card_value >> (left_num * 8)
            left_card_l = card_value & (2**(left_num * 8) - 1)
        # 发送命令
        self.excuteOrderRightAway("设置左转点", left_num, left_card_h, left_card_l)

    def setTurnRightCard(self, right_card=None):
        """设置右转点

        Args:
            right_card (List[int], optional): 右转点，最多设置19个，设置0个为None. Defaults to None.

        Returns:
            Boolean: 参数错误返回False
        Examples
        --------
        >>> car.setTurnRightCard([0x0001,0x0002]) # 设置2个右转点，卡号是0x0001和0x0002
        >>> car.setTurnRightCard([]) # 清除右转点
        """
        # 校验右转参数
        if right_card is None:
            right_num = 0
            right_card_h = 0
            right_card_l = 0
        else:
            if isinstance(right_card, int) is True:
                right_num = 1
                card_value = right_card
            elif isinstance(right_card, list) is True:
                right_num = len(right_card)
                card_value = self.cnvHexArrayToHex(right_card)
            else:
                LOGGER.logger.error(
                    "fun setTurnCard parameter: right_card must be list!")
                return False
            right_card_h = card_value >> (right_num * 8)
            right_card_l = card_value & (2**(right_num * 8) - 1)
        self.excuteOrderRightAway("设置右转点", right_num, right_card_h,
                                  right_card_l)

    def getTurnLeftCard(self):
        """获取左转点

        Returns:
            List[int]: 左转点列表
            Boolean: 参数错误返回False
        """
        recv_buf = self.queryOrder(self.wait_time, "查询左转点")
        if recv_buf is not None:
            return self.cnvHexToHexArray(recv_buf["data"]["卡号H"] <<
                                         (recv_buf["data"]["左转点数量"] * 8)
                                         | (recv_buf["data"]["卡号L"]))
        else:
            return False

    def getTurnRightCard(self):
        """获取右转点

        Returns:
            List[int]: 右转点列表
            Boolean: 参数错误返回False
        """
        recv_buf = self.queryOrder(self.wait_time, "查询右转点")
        if recv_buf is not None:
            return self.cnvHexToHexArray(recv_buf["data"]["卡号H"] <<
                                         (recv_buf["data"]["右转点数量"] * 8)
                                         | (recv_buf["data"]["卡号L"]))
        else:
            return False

    def inPark1(self):
        """进入1号停车场。需要在交通沙盘的特定轨道上实现。
        """
        self.excuteOrderRightAway("进停车场1")

    def inPark2(self):
        """进入2号停车场。需要在交通沙盘的特定轨道上实现。
        """
        self.excuteOrderRightAway("进停车场2")

    def outPark(self):
        """出停车场。需要在交通沙盘的特定轨道上实现。
        """
        self.excuteOrderRightAway("出停车场")

    def inCharge1(self):
        """进入1号充电桩。需要在交通沙盘的特定轨道上实现。
        """
        self.excuteOrderRightAway("进充电桩1")

    def inCharge2(self):
        """进入2号充电桩。需要在交通沙盘的特定轨道上实现。
        """
        self.excuteOrderRightAway("进充电桩2")

    def outCharge(self):
        """出充电桩。需要在交通沙盘的特定轨道上实现。
        """
        self.excuteOrderRightAway("出充电桩")

    ########################## 以下是小车手动模式下的控制方法 ############################

    def backCar(self):
        """小车倒车
        """
        self.excuteOrderRightAway("倒车")

    def leftTurn(self):
        """小车左转
        """
        self.excuteOrderRightAway("左转")

    def rightTurn(self):
        """小车右转
        """
        self.excuteOrderRightAway("右转")


########################## 以下是小车单轮控制模式下的控制方法 ############################

    def ctrlCarByWheel(self, left_front_speed, right_front_speed,
                       left_back_speed, right_back_speed):
        """单轮控制

        Args:
            left_front_speed (int): 左前轮速度（-50~50）
            right_front_speed (int): 右前轮速度（-50~50）
            left_back_speed (int): 左后轮速度（-50~50）
            right_back_speed (int): 右后轮速度（-50~50）

        Returns:
            Boolean: 参数错误返回False
        """
        # 入参校验
        if left_front_speed < (
                0 - self.__max_speed) or left_front_speed > self.__max_speed:
            LOGGER.logger.error(
                f"fun ctrlCarByWheel parameter: " +
                f"Speed must be set in the interval " +
                f"[{(0 - self.__max_speed)} ~ {self.__max_speed}]!")
            return False
        if right_front_speed < (
                0 - self.__max_speed) or right_front_speed > self.__max_speed:
            LOGGER.logger.error(
                f"fun ctrlCarByWheel parameter: " +
                f"Speed must be set in the interval " +
                f"[{(0 - self.__max_speed)} ~ {self.__max_speed}]!")
            return False
        if left_back_speed < (
                0 - self.__max_speed) or left_back_speed > self.__max_speed:
            LOGGER.logger.error(
                f"fun ctrlCarByWheel parameter: " +
                f"Speed must be set in the interval " +
                f"[{(0 - self.__max_speed)} ~ {self.__max_speed}]!")
            return False
        if right_back_speed < (
                0 - self.__max_speed) or right_back_speed > self.__max_speed:
            LOGGER.logger.error(
                f"fun ctrlCarByWheel parameter: " +
                f"Speed must be set in the interval " +
                f"[{(0 - self.__max_speed)} ~ {self.__max_speed}]!")
            return False
        # 组装数据帧
        wheel_direction = 0
        if left_front_speed < 0:
            wheel_direction |= 1
        wheel_direction = (wheel_direction << 1)
        if right_front_speed < 0:
            wheel_direction |= 1
        wheel_direction = (wheel_direction << 1)
        if left_back_speed < 0:
            wheel_direction |= 1
        wheel_direction = (wheel_direction << 1)
        if right_back_speed < 0:
            wheel_direction |= 1
        self.excuteOrderRightAway("单个轮子控制", wheel_direction,
                                  abs(left_front_speed),
                                  abs(right_front_speed), abs(left_back_speed),
                                  abs(right_back_speed))

    # 接力出版社之后添加

    def setServoAngle(self, ch=1, angle=0):
        if ch not in range(1, 5):
            LOGGER.logger.error(f'ch:{ch} 范围应是:(1~4)')
            return False
        if angle not in range(0, 181):
            LOGGER.logger.error(f'angle:{angle} 范围是:(0~180)')
            return False
        self.setCarExpandPWMSingle(int(ch), 20000000,
                                   int(2000000 * angle / 180 + 500000))

    def openServo(self, ch=1):
        if ch not in range(1, 5):
            LOGGER.logger.error(f'ch:{ch} 范围应是:(1~4)')
            return False
        self.setServoAngle(ch, 80)

    def closeServo(self, ch=1):
        if ch not in range(1, 5):
            LOGGER.logger.error(f'ch:{ch} 范围应是:(1~4)')
            return False
        self.setServoAngle(ch, 0)

    def getCarStatus(self):
        if self.refreshStatus() is False:
            return False
        if self.car_status["车速"] <= 0:
            return False
        else:
            return True

    def getCardNum(self):
        if self.refreshStatus() is False:
            return False
        return self.car_status["卡号"]

    def getCarMode(self):
        if self.refreshStatus() is False:
            return False
        return self.car_status["模式"]
