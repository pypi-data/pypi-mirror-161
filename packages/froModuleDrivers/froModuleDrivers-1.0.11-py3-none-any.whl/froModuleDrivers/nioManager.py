# -*- encoding=utf-8 -*-

from .baseDriver import BaseDriver

from .nioConnector import NioConnector
from . import LOGGER
import threading


class NioManager(NioConnector):
    def __init__(self, *args):
        super().__init__()
        self.drivers = {}
        for arg in args:
            if isinstance(arg, BaseDriver):
                self.binDriver(arg)

    def onDataReceived(self, clientId, data):
        LOGGER.logger.debug("onDataReceivedCustom:[%s]" % data.hex())
        if clientId not in self.drivers:
            return None

        driver = self.drivers[clientId]
        return driver.handleResult(data)

    def binDriver(self, driver):
        clientId = driver.bindConnector(self)
        self.drivers[clientId] = driver

    def run(self):
        LOGGER.logger.info("ready to loop")
        # th = threading.Thread(target=self.loop)
        th = threading.Thread(target=self.loop, daemon=True)
        th.start()
