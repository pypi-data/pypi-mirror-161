# -*- encoding=utf-8 -*-

ProtocolDefine = {
    # protocolName: {
    #     "request":{
    #         orderName:{
    #             "cmd": bytes[]
    #             "args": [
    #                 {
    #                     "argName": nameStr,
    #                     "index": 3,
    #                     "length": 1
    #                 }
    #                 ...
    #             ]
    #         }
    #     },
    #     "responsePattern": rb'\xa0\x0b([\s\S]+)\x0d\x0a',
    #     "response": {
    #         orderCode: {
    #         orderName: nameStr,
    #         dataDefine: [
    #             {
    #                 fieldName: nameStr,
    #                 length: int
    #             },
    #             '''
    #         ]
    #     }
    # }
    "K210": {
        "request": {
            "查询固件版本": {
                "cmd": b"\xA0\x02\xD1\x0D\x0A",
                "args": []
            },
            "转向点设置": {
                "cmd":
                b"\xA0\x02\xC5\x00\x00\x00\x00\x00\x00\x0D\x0A",
                "args": [
                    {
                        "argName": "左转数量",
                        "index": 3,
                        "length": 1
                    },
                    {
                        "argName": "左转卡位高位",
                        "index": 4,
                        "length": "左转数量"
                    },
                    {
                        "argName": "左转卡位低位",
                        "index": 5,
                        "length": "左转数量"
                    },
                    {
                        "argName": "右转数量",
                        "index": 6,
                        "length": 1
                    },
                    {
                        "argName": "右转卡位高位",
                        "index": 7,
                        "length": "右转数量"
                    },
                    {
                        "argName": "右转卡位低位",
                        "index": 8,
                        "length": "右转数量"
                    },
                ]
            },
            "设置左转点": {
                "cmd":
                b"\xA0\x02\xB1\x00\x00\x00\x0D\x0A",
                "args": [
                    {
                        "argName": "左转数量",
                        "index": 3,
                        "length": 1
                    },
                    {
                        "argName": "左转卡位高位",
                        "index": 4,
                        "length": "左转数量"
                    },
                    {
                        "argName": "左转卡位低位",
                        "index": 5,
                        "length": "左转数量"
                    },
                ]
            },
            "设置右转点": {
                "cmd":
                b"\xA0\x02\xB2\x00\x00\x00\x0D\x0A",
                "args": [
                    {
                        "argName": "右转数量",
                        "index": 3,
                        "length": 1
                    },
                    {
                        "argName": "右转卡位高位",
                        "index": 4,
                        "length": "右转数量"
                    },
                    {
                        "argName": "右转卡位低位",
                        "index": 5,
                        "length": "右转数量"
                    },
                ]
            },
            "读寄存器-缓冲区": {
                "cmd":
                b"\xA0\x02\xF2\x00\x00\x00\x00\x0D\x0A",
                "args": [
                    {
                        "argName": "起始寄存器地址",
                        "index": 3,
                        "length": 2
                    },
                    {
                        "argName": "寄存器长度",
                        "index": 5,
                        "length": 2
                    },
                ]
            },
            "读寄存器-底层板": {
                "cmd":
                b"\xA0\x02\xF3\x00\x00\x00\x00\x0D\x0A",
                "args": [
                    {
                        "argName": "起始寄存器地址",
                        "index": 3,
                        "length": 2
                    },
                    {
                        "argName": "寄存器长度",
                        "index": 5,
                        "length": 2
                    },
                ]
            },
            "写寄存器": {
                # A0 02	F1	X1 X2	X3 X4	X5	XN …	0D 0A 不定长的数据占一位
                "cmd":
                b"\xA0\x02\xF1\x00\x00\x00\x00\x00\x00\x0D\x0A",
                "args": [
                    {
                        "argName": "起始寄存器地址",
                        "index": 3,
                        "length": 2
                    },
                    {
                        "argName": "寄存器长度",
                        "index": 5,
                        "length": 2
                    },
                    {
                        "argName": "数据长度",
                        "index": 7,
                        "length": 1
                    },
                    {
                        "argName": "写数据",
                        "index": 8,
                        "length": "数据长度"
                    },
                ]
            },
            "前进/启动": {
                "cmd": b"\xA0\x02\x01\x0D\x0A",
                "args": []
            },
            "停车": {
                "cmd": b"\xA0\x02\x02\x0D\x0A",
                "args": []
            },
            "自动模式": {
                "cmd": b"\xA0\x02\x06\x0D\x0A",
                "args": []
            },
            "手动模式": {
                "cmd": b"\xA0\x02\x07\x0D\x0A",
                "args": []
            },
            "单个轮子控制模式": {
                "cmd": b"\xA0\x02\x11\x0D\x0A",
                "args": []
            },
            "设置速度": {
                "cmd": b"\xA0\x02\x08\00\x0D\x0A",
                "args": [
                    {
                        "argName": "速度",
                        "index": 3,
                        "length": 1
                    },
                ]
            },
            "查询小车状态": {
                "cmd": b"\xA0\x02\xD2\x0D\x0A",
                "args": []
            },
            "查询距离": {
                "cmd": b"\xA0\x02\xD3\x0D\x0A",
                "args": []
            },
            "播放内置语音": {
                "cmd": b"\xA0\x02\xC6\00\x0D\x0A",
                "args": [
                    {
                        "argName": "语音编号",
                        "index": 3,
                        "length": 1
                    },
                ]
            },
            "设置灯光模式": {
                "cmd": b"\xA0\x02\x21\00\x0D\x0A",
                "args": [
                    {
                        "argName": "灯光模式编号",
                        "index": 3,
                        "length": 1
                    },
                ]
            },
            "设置灯光": {
                "cmd":
                b"\xA0\x02\x22\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\x0D\x0A",
                "args": [
                    {
                        "argName": "18盏灯光RGB值",
                        "index": 3,
                        "length": 54
                    },
                ]
            },
            "查询探头状态": {
                "cmd": b"\xA0\x02\xC9\x0D\x0A",
                "args": []
            },
            "设置脉冲输出": {
                "cmd":
                b"\xA0\x02\x23\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\x0D\x0A",
                "args": [
                    {
                        "argName": "周期",
                        "index": 3,
                        "length": 4
                    },
                    {
                        "argName": "1号脉冲",
                        "index": 7,
                        "length": 4
                    },
                    {
                        "argName": "2号脉冲",
                        "index": 11,
                        "length": 4
                    },
                    {
                        "argName": "3号脉冲",
                        "index": 15,
                        "length": 4
                    },
                    {
                        "argName": "4号脉冲",
                        "index": 19,
                        "length": 4
                    },
                ]
            },
            "设置脉冲输出-单个": {
                "cmd":
                b"\xA0\x02\x24\00\00\00\00\00\00\00\00\00\x0D\x0A",
                "args": [
                    {
                        "argName": "通道",
                        "index": 3,
                        "length": 1
                    },
                    {
                        "argName": "周期",
                        "index": 4,
                        "length": 4
                    },
                    {
                        "argName": "脉冲",
                        "index": 8,
                        "length": 4
                    },
                ]
            },
            "定点停车": {
                "cmd":
                b"\xA0\x02\xC4\00\00\00\x0D\x0A",
                "args": [
                    {
                        "argName": "停车开关",
                        "index": 3,
                        "length": 1
                    },
                    {
                        "argName": "卡号",
                        "index": 4,
                        "length": 2
                    },
                ]
            },
            "查询左转点": {
                "cmd": b"\xA0\x02\xC7\x0D\x0A",
                "args": []
            },
            "查询右转点": {
                "cmd": b"\xA0\x02\xC8\x0D\x0A",
                "args": []
            },
            "进停车场1": {
                "cmd": b"\xA0\x02\xA1\x0D\x0A",
                "args": []
            },
            "进停车场2": {
                "cmd": b"\xA0\x02\xA2\x0D\x0A",
                "args": []
            },
            "出停车场": {
                "cmd": b"\xA0\x02\xA3\x0D\x0A",
                "args": []
            },
            "进充电桩1": {
                "cmd": b"\xA0\x02\xA4\x0D\x0A",
                "args": []
            },
            "进充电桩2": {
                "cmd": b"\xA0\x02\xA5\x0D\x0A",
                "args": []
            },
            "出充电桩": {
                "cmd": b"\xA0\x02\xA6\x0D\x0A",
                "args": []
            },
            "倒车": {
                "cmd": b"\xA0\x02\x03\x0D\x0A",
                "args": []
            },
            "左转": {
                "cmd": b"\xA0\x02\x04\x0D\x0A",
                "args": []
            },
            "右转": {
                "cmd": b"\xA0\x02\x05\x0D\x0A",
                "args": []
            },
            "原地左转": {
                "cmd": b"\xA0\x02\x09\x0D\x0A",
                "args": []
            },
            "原地右转": {
                "cmd": b"\xA0\x02\x0A\x0D\x0A",
                "args": []
            },
            "单个轮子控制": {
                "cmd":
                b"\xA0\x02\x12\x00\x00\x00\x00\x00\x0D\x0A",
                "args": [
                    {
                        "argName": "轮胎状态",
                        "index": 3,
                        "length": 1
                    },
                    {
                        "argName": "左前轮速度",
                        "index": 4,
                        "length": 1
                    },
                    {
                        "argName": "右前轮速度",
                        "index": 5,
                        "length": 1
                    },
                    {
                        "argName": "左后轮速度",
                        "index": 6,
                        "length": 1
                    },
                    {
                        "argName": "右后轮速度",
                        "index": 7,
                        "length": 1
                    },
                ]
            },
        },
        "responsePattern": rb'\xa0\x0b([\s\S]+)\x0d\x0a',
        "response": {
            0xD1: {
                "orderName": "查询固件版本",
                "dataDefine": [
                    {
                        "fieldName": "版本号",
                        "length": 3
                    },
                ]
            },
            0xF2: {
                "orderName":
                "读寄存器-缓冲区",
                "dataDefine": [
                    {
                        "fieldName": "起始寄存器地址",
                        "length": 2
                    },
                    {
                        "fieldName": "寄存器长度",
                        "length": 2
                    },
                    {
                        "fieldName": "寄存器数据长度",
                        "length": 1
                    },
                    {
                        "fieldName": "寄存器数据",
                        "length":
                        "寄存器数据长度"  # 若是变量，则之前必然出现过，否则逻辑上就无法解析。因此这里用fieldName字符串表示变量
                    }
                ]
            },
            0xF3: {
                "orderName":
                "读寄存器-底层板",
                "dataDefine": [
                    {
                        "fieldName": "起始寄存器地址",
                        "length": 2
                    },
                    {
                        "fieldName": "寄存器长度",
                        "length": 2
                    },
                    {
                        "fieldName": "寄存器数据长度",
                        "length": 1
                    },
                    {
                        "fieldName": "寄存器数据",
                        "length":
                        "寄存器数据长度"  # 若是变量，则之前必然出现过，否则逻辑上就无法解析。因此这里用fieldName字符串表示变量
                    }
                ]
            },
            0xF1: {
                "orderName":
                "写寄存器",
                "dataDefine": [
                    {
                        "fieldName": "起始寄存器地址",
                        "length": 2
                    },
                    {
                        "fieldName": "寄存器长度",
                        "length": 2
                    },
                    {
                        "fieldName": "寄存器数据长度",
                        "length": 1
                    },
                    {
                        "fieldName": "寄存器数据",
                        "length":
                        "寄存器数据长度"  # 若是变量，则之前必然出现过，否则逻辑上就无法解析。因此这里用fieldName字符串表示变量
                    }
                ]
            },
            0x01: {
                "orderName": "前进/启动",
                "dataDefine": []
            },
            0x02: {
                "orderName": "停车",
                "dataDefine": []
            },
            0x06: {
                "orderName": "自动模式",
                "dataDefine": []
            },
            0x07: {
                "orderName": "手动模式",
                "dataDefine": []
            },
            0x11: {
                "orderName": "单个轮子控制模式",
                "dataDefine": []
            },
            0x08: {
                "orderName": "设置速度",
                "dataDefine": [
                    {
                        "fieldName": "速度",
                        "length": 1
                    },
                ]
            },
            0xD2: {
                "orderName":
                "查询小车状态",
                "dataDefine": [
                    {
                        "fieldName": "B1",
                        "length": 1
                    },
                    {
                        "fieldName": "车速",
                        "length": 1
                    },
                    {
                        "fieldName": "B2",
                        "length": 1
                    },
                    {
                        "fieldName": "卡号H",
                        "length": 1
                    },
                    {
                        "fieldName": "B3",
                        "length": 1
                    },
                    {
                        "fieldName": "卡号L",
                        "length": 1
                    },
                    {
                        "fieldName": "B4",
                        "length": 1
                    },
                    {
                        "fieldName": "电压",
                        "length": 1
                    },
                    {
                        "fieldName": "B5",
                        "length": 1
                    },
                    {
                        "fieldName": "轨道",
                        "length": 1
                    },
                    {
                        "fieldName": "B6",
                        "length": 1
                    },
                    {
                        "fieldName": "模式",
                        "length": 1
                    },
                ]
            },
            0xD3: {
                "orderName":
                "查询距离",
                "dataDefine": [
                    {
                        "fieldName": "B1",
                        "length": 1
                    },
                    {
                        "fieldName": "距离H",
                        "length": 1
                    },
                    {
                        "fieldName": "B2",
                        "length": 1
                    },
                    {
                        "fieldName": "距离L",
                        "length": 1
                    },
                ]
            },
            0xC5: {
                "orderName":
                "转向点设置",
                "dataDefine": [
                    {
                        "fieldName": "左转数量",
                        "length": 1
                    },
                    {
                        "fieldName": "左转卡位高位",
                        "length": "左转数量"
                    },
                    {
                        "fieldName": "左转卡位低位",
                        "length": "左转数量"
                    },
                    {
                        "fieldName": "右转数量",
                        "length": 1
                    },
                    {
                        "fieldName": "右转卡位高位",
                        "length": "右转数量"
                    },
                    {
                        "fieldName": "右转卡位低位",
                        "length": "右转数量"
                    },
                ]
            },
            0xB1: {
                "orderName":
                "设置左转点",
                "dataDefine": [
                    {
                        "fieldName": "左转数量",
                        "length": 1
                    },
                    {
                        "fieldName": "左转卡位高位",
                        "length": "左转数量"
                    },
                    {
                        "fieldName": "左转卡位低位",
                        "length": "左转数量"
                    },
                ]
            },
            0xB2: {
                "orderName":
                "设置右转点",
                "dataDefine": [
                    {
                        "fieldName": "右转数量",
                        "length": 1
                    },
                    {
                        "fieldName": "右转卡位高位",
                        "length": "右转数量"
                    },
                    {
                        "fieldName": "右转卡位低位",
                        "length": "右转数量"
                    },
                ]
            },
            0xC6: {
                "orderName": "播放内置语音",
                "dataDefine": [
                    {
                        "fieldName": "语音编号",
                        "length": 1
                    },
                ]
            },
            0x21: {
                "orderName": "设置灯光模式",
                "dataDefine": [
                    {
                        "fieldName": "灯光模式编号",
                        "length": 1
                    },
                ]
            },
            0x22: {
                "orderName": "设置灯光",
                "dataDefine": [
                    {
                        "fieldName": "18盏灯光RGB值",
                        "length": 54
                    },
                ]
            },
            0xC9: {
                "orderName":
                "查询探头状态",
                "dataDefine": [
                    {
                        "fieldName": "前探头状态",
                        "length": 1
                    },
                    {
                        "fieldName": "后探头状态",
                        "length": 1
                    },
                ]
            },
            0x23: {
                "orderName":
                "设置脉冲输出",
                "dataDefine": [
                    {
                        "fieldName": "周期",
                        "length": 4
                    },
                    {
                        "fieldName": "1号脉冲",
                        "length": 4
                    },
                    {
                        "fieldName": "2号脉冲",
                        "length": 4
                    },
                    {
                        "fieldName": "3号脉冲",
                        "length": 4
                    },
                    {
                        "fieldName": "4号脉冲",
                        "length": 4
                    },
                ]
            },
            0x24: {
                "orderName":
                "设置脉冲输出-单个",
                "dataDefine": [
                    {
                        "fieldName": "通道",
                        "length": 1
                    },
                    {
                        "fieldName": "周期",
                        "length": 4
                    },
                    {
                        "fieldName": "脉冲",
                        "length": 4
                    },
                ]
            },
            0xC4: {
                "orderName":
                "定点停车",
                "dataDefine": [
                    {
                        "fieldName": "停车开关",
                        "length": 1
                    },
                    {
                        "fieldName": "卡号",
                        "length": 2
                    },
                ]
            },
            0xC7: {
                "orderName":
                "查询左转点",
                "dataDefine": [
                    {
                        "fieldName": "左转点数量",
                        "length": 1
                    },
                    {
                        "fieldName": "卡号H",
                        "length": "左转点数量"
                    },
                    {
                        "fieldName": "卡号L",
                        "length": "左转点数量"
                    },
                ]
            },
            0xC8: {
                "orderName":
                "查询右转点",
                "dataDefine": [
                    {
                        "fieldName": "右转点数量",
                        "length": 1
                    },
                    {
                        "fieldName": "卡号H",
                        "length": "右转点数量"
                    },
                    {
                        "fieldName": "卡号L",
                        "length": "右转点数量"
                    },
                ]
            },
            0xA1: {
                "orderName": "进停车场1",
                "dataDefine": []
            },
            0xA2: {
                "orderName": "进停车场2",
                "dataDefine": []
            },
            0xA3: {
                "orderName": "出停车场",
                "dataDefine": []
            },
            0xA4: {
                "orderName": "进充电桩1",
                "dataDefine": []
            },
            0xA5: {
                "orderName": "进充电桩2",
                "dataDefine": []
            },
            0xA6: {
                "orderName": "出充电桩",
                "dataDefine": []
            },
            0x03: {
                "orderName": "倒车",
                "dataDefine": []
            },
            0x04: {
                "orderName": "左转",
                "dataDefine": []
            },
            0x05: {
                "orderName": "右转",
                "dataDefine": []
            },
            0x09: {
                "orderName": "原地左转",
                "dataDefine": []
            },
            0x0A: {
                "orderName": "原地右转",
                "dataDefine": []
            },
            0x12: {
                "orderName":
                "单个轮子控制",
                "dataDefine": [
                    {
                        "fieldName": "轮胎状态",
                        "length": 1
                    },
                    {
                        "fieldName": "左前轮速度",
                        "length": 1
                    },
                    {
                        "fieldName": "右前轮速度",
                        "length": 1
                    },
                    {
                        "fieldName": "左后轮速度",
                        "length": 1
                    },
                    {
                        "fieldName": "右后轮速度",
                        "length": 1
                    },
                ]
            },
        }
    },
    "K12": {
        "request": {
            "03号查询指令": {
                "cmd":
                b"\x00\x03\x00\x00\x00\x00\x00\x00",
                "args": [
                    {
                        "argName": "主/从机号",
                        "index": 0,
                        "length": 1
                    },
                    {
                        "argName": "地址位",
                        "index": 2,
                        "length": 2
                    },
                    {
                        "argName": "地址长度",
                        "index": 4,
                        "length": 2
                    },
                    {
                        "argName": "CRC校验",
                        "index": 6,
                        "length": 2
                    },
                ]
            },
            "10号写指令": {
                "cmd":
                b"\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00",
                "args": [
                    {
                        "argName": "主/从机号",
                        "index": 0,
                        "length": 1
                    },
                    {
                        "argName": "地址位",
                        "index": 2,
                        "length": 2
                    },
                    {
                        "argName": "地址长度",
                        "index": 4,
                        "length": 2
                    },
                    {
                        "argName": "数据长度",
                        "index": 6,
                        "length": 1
                    },
                    {
                        "argName": "数据",
                        "index": 7,
                        "length": "数据长度"
                    },
                    {
                        "argName": "CRC校验",
                        "index": 8,
                        "length": 2
                    },
                ]
            }
        },
        "responsePattern": rb'([\s\S][\x03\x10\x83\x90][\s\S]+)',
        "response": {
            0x03: {
                "orderName":
                "03号查询指令",
                "dataDefine": [
                    {
                        "fieldName": "主机号",
                        "length": 1
                    },
                    {
                        "fieldName": "指令号",
                        "length": 1
                    },
                    {
                        "fieldName": "设备号",
                        "length": 2
                    },
                    {
                        "fieldName": "数据长度",
                        "length": 1
                    },
                    {
                        "fieldName": "数据",
                        "length": "数据长度"
                    },
                    {
                        "fieldName": "CRC校验",
                        "length": 2
                    },
                ]
            },
            0x10: {
                "orderName":
                "10号写指令",
                "dataDefine": [
                    {
                        "fieldName": "主/从机号",
                        "length": 1
                    },
                    {
                        "fieldName": "指令号",
                        "length": 1
                    },
                    {
                        "fieldName": "设备号",
                        "length": 2
                    },
                    {
                        "fieldName": "地址长度",
                        "length": 2
                    },
                    {
                        "fieldName": "数据长度",
                        "length": 1
                    },
                    {
                        "fieldName": "数据",
                        "length": "数据长度"
                    },
                    {
                        "fieldName": "CRC校验",
                        "length": 2
                    },
                ]
            },
            0x83: {
                "orderName":
                "03号错误指令",
                "dataDefine": [
                    {
                        "fieldName": "主/从机号",
                        "length": 1
                    },
                    {
                        "fieldName": "指令号",
                        "length": 1
                    },
                    {
                        "fieldName": "错误码",
                        "length": 1
                    },
                    {
                        "fieldName": "CRC校验",
                        "length": 2
                    },
                ]
            },
            0x90: {
                "orderName":
                "10号错误指令",
                "dataDefine": [
                    {
                        "fieldName": "主/从机号",
                        "length": 1
                    },
                    {
                        "fieldName": "指令号",
                        "length": 1
                    },
                    {
                        "fieldName": "错误码",
                        "length": 1
                    },
                    {
                        "fieldName": "CRC校验",
                        "length": 2
                    },
                ]
            }
        }
    }
}