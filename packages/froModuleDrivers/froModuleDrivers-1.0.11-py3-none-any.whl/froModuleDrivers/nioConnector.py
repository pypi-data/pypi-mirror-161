# -*- encoding=utf-8 -*-
import select
import socket
import time
from . import LOGGER


class NioConnector(object):
    IDLE = 0
    RUNNING = 1
    SHUTDOWN_WAITING = 2
    SHUTDOWN = 3

    def __init__(self):
        super().__init__()
        self.status = self.IDLE
        self.socketRegistry = {}  # sk:netAddr
        self.sockets = []
        self.messageQueues = {}  # netAddr:[queuePriority, queueSecondary]

        self.results = {}  # netAddr:{orderName:doHandleResult}

        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
        # LOGGER.logger.basicConfig(level=LOGGER.logger.ERROR, format=LOG_FORMAT)

    def doConnect(self, netAddr):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client.setblocking(0)
        try:
            client.connect(netAddr)
        except Exception as e:
            LOGGER.logger.debug(e)
        return client

    def onDataReceived(self, clientId, data):
        LOGGER.logger.debug("onDataReceved:[%s]" % data.hex())
        return None

    def sendData(self, netAddr, data, prior=False):
        if self.status != self.RUNNING:
            LOGGER.logger.debug("cannot sendData on status[%d]" % self.status)
            return

        LOGGER.logger.debug("sendData:[%s]" % data.hex())
        if netAddr in self.messageQueues:
            msgQueue = self.messageQueues[netAddr][0] if prior else \
                self.messageQueues[netAddr][1]
            msgQueue.append(data)

    def registConnection(self, netAddr):
        client = self.doConnect(netAddr)
        self.sockets.append(client)
        self.socketRegistry[client] = netAddr
        self.messageQueues[netAddr] = [[], []]
        self.results[netAddr] = {}
        # 返回clientId。将netAddr用作clientId。
        return netAddr

    def modifyInner(self, oldSk):
        if oldSk in self.sockets:
            self.sockets.remove(oldSk)

        if oldSk in self.socketRegistry:
            netAddr = self.socketRegistry.pop(oldSk)
            newSk = self.doConnect(netAddr)
            self.sockets.append(newSk)
            self.socketRegistry[newSk] = netAddr

    def waitResponse(self, clientId, orderName):
        self.results[clientId][orderName] = None

    def getResponse(self, clientId, orderName):
        if orderName in self.results[clientId]:
            return self.results[clientId].pop(orderName)
        else:
            return None

    def shutdown(self):
        self.status = self.SHUTDOWN

    def shutdownGracefully(self):
        self.status = self.SHUTDOWN_WAITING
        time.sleep(1)

    def sendAllMessage(self, writable):
        LOGGER.logger.debug("sendAllMessage")
        for s in writable:
            if s in self.socketRegistry:
                netAddr = self.socketRegistry[s]
                if netAddr in self.messageQueues:
                    queuePriority = self.messageQueues[netAddr][0]
                    queueSecondary = self.messageQueues[netAddr][1]
                    while len(queuePriority) > 0:
                        data = queuePriority.pop(0)
                        s.send(data)
                        LOGGER.logger.debug("doSendDataP:%s" % data.hex())
                    while len(queueSecondary) > 0:
                        data = queueSecondary.pop(0)
                        LOGGER.logger.debug("doSendDataS:%s" % data.hex())
                        s.send(data)

    def loop(self):
        self.status = self.RUNNING
        while self.status in [self.RUNNING, self.SHUTDOWN_WAITING]:
            # unlikely to happen
            if len(self.sockets) == 0:
                raise Exception("未注册连接")

            readable, writable, exceptional = select.select(
                self.sockets, self.sockets, self.sockets, 2)

            if self.status == self.SHUTDOWN_WAITING:
                try:
                    self.sendAllMessage(writable)
                except Exception:
                    pass
                self.status = self.SHUTDOWN
                break

            # handle dataReceved
            for s in readable:
                data = s.recv(1024)
                # reconnect
                if not data:
                    s.close()
                    LOGGER.logger.debug("socket closed %s" % s)
                    self.modifyInner(s)
                    break
                if s in self.socketRegistry:
                    result = self.onDataReceived(self.socketRegistry[s], data)
                    if result is not None and "orderName" in result:
                        orderName = result["orderName"]
                        self.results[
                            self.socketRegistry[s]][orderName] = result

            # wirte data
            for s in writable:
                if s in self.socketRegistry:
                    netAddr = self.socketRegistry[s]
                    if netAddr in self.messageQueues:
                        queuePriority = self.messageQueues[netAddr][0]
                        queueSecondary = self.messageQueues[netAddr][1]
                        if len(queuePriority) > 0:
                            data = queuePriority.pop(0)
                            s.send(data)
                            LOGGER.logger.debug("doSendDataP:%s" % data.hex())
                        elif len(queueSecondary) > 0:
                            data = queueSecondary.pop(0)
                            LOGGER.logger.debug("doSendDataS:%s" % data.hex())
                            s.send(data)

            # handle exception, just reconnect
            for s in exceptional:
                s.close()
                self.modifyInner(s)

        # close all sockets on exit
        for s in self.sockets:
            s.close()
        LOGGER.logger.debug("loop ends")
