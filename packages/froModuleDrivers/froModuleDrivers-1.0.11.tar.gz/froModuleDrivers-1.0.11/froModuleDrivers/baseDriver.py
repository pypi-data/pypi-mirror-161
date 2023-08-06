# -*- encoding=utf-8 -*-
from . import LOGGER


class BaseDriver(object):
    def __init__(self, host="localhost", port=4001):
        self.host = str(host)
        self.port = int(port)
        self.supportProtocols = []
        self.connector = None

    def setNetAddr(self, host="localhost", port=4001):
        self.host = str(host)
        self.port = int(port)

    def addProtocol(self, protocol, index=None):
        if index is None:
            self.supportProtocols.append(protocol)
        else:
            self.supportProtocols.insert(index, protocol)

    def bindConnector(self, connector):
        self.connector = connector
        clientId = connector.registConnection((self.host, self.port))
        return clientId

    def doHandleResult(self, result):
        """
        此处result为按协议定义的字段解析过的dict
        驱动可根据具体设备进行自定义 状态信息维护、状态查询结果返回等操作。
        包装返回值，使其包含"orderName", 并被查询指令接收
        :param result: protocolhandler解析过的dict, 可能为None
                       默认结构为{"orderName": nameStr, "data": dataMap}
                       其中nameStr, dataMap均遵守protocol的定义
        :return:result: 驱动自定义包装返回值，主要返回给驱动函数调用方。
                        里面需包含"orderName"字段，建议规范成{"orderName": nameStr, "data": dataMap}结构。
                boolean: True 表示收到的数据处理完成
                         False 表示收到的数据处理失败，交给其他protocol解析

        """
        # dont block here
        LOGGER.logger.debug("handle result:%s" % result)
        return result, False

    def handleResult(self, data):
        for handler in self.supportProtocols:
            if handler.canHandle(data):
                result = handler.parseResponse(data)
                resp, finished = self.doHandleResult(result)
                if finished:
                    return resp

    def parseOrder(self, orderName, *args):
        LOGGER.logger.debug("parse order:%s" % orderName)
        for handler in self.supportProtocols:
            if handler.haveOrder(orderName):
                result = handler.parseCmd(orderName, *args)
                if result is not None:
                    return result
        LOGGER.logger.debug("cannot parse order:%s" % orderName)
        return None

    def getClientId(self):
        return self.host, self.port
