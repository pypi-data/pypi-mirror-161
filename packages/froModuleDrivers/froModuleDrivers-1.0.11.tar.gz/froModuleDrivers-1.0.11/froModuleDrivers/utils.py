# -*- coding: utf-8 -*-

import logging


class Logger(object):
    """[通用打印信息类] 

    Args:
        object ([type]): [description]
    """
    def __init__(self, *args, **kwargs):
        # self.logger = logging.getLogger(args[0])
        self.logger = logging.getLogger(self.__class__.__name__)
        # self.logger = logging.getLogger("root")

    def create_logger(self, name='console', level='error', record_format=None):
        """开启log模式

        Args:
            name (str, optional): 输出格式. Defaults to 'console'.
            level (str, optional): 输出等级. Defaults to 'debug'.
            record_format (格式化字符串), optional): 格式化字符串. Defaults to None.

        Returns:
            logger: 句柄
        """
        if record_format is None:
            record_format = '[%(levelname)5s] %(asctime)15s [%(filename)18s %(lineno)3s] %(funcName)10s : %(message)s'

        level = level.upper()
        if level not in [
                'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        ]:
            raise ValueError(f'Unknow logging level: {level}')

        self.logger.setLevel(eval('logging.' + level))
        formatter = logging.Formatter(record_format)
        if name == 'console':
            ch = logging.StreamHandler()
        elif name == 'dummy':
            ch = logging.NullHandler()
        elif name[-4:] == '.log':
            ch = logging.FileHandler(name, encoding='utf-8')
        else:
            raise Exception(f"Unknown handler: {name}")
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        return self.logger

    def set_lvl(self, level='debug'):
        """设置调试等级

        Args:
            level (str, optional): 输出等级. Defaults to 'debug'.

        Raises:
            ValueError: 不存在的调试等级
        """
        level = level.upper()
        if level not in [
                'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        ]:
            raise ValueError(f'Unknow logging level: {level}')

        self.logger.setLevel(eval('logging.' + level))

    def print_hex(self,
                  bytes,
                  title="[DEF.]",
                  base=2,
                  modifier_font=" 0x",
                  modifier_behind=""):
        """打印HEX数组

        Args:
            bytes (List): HEX数组
            title (str, optional): 标题. Defaults to "[DEF.]".
            base (int, optional): 宽度. Defaults to 8.
            modifier_font (str, optional): 每个元素的前缀. Defaults to " 0x".
            modifier_behind (str, optional): 每个元素的后缀. Defaults to "".
        """
        s = title
        if base == 4:
            for i in bytes:
                s += modifier_font
                s += f'{i:04X}'
                s += modifier_behind
        else:
            for i in bytes:
                s += modifier_font
                s += f'{i:02X}'
                s += modifier_behind
        self.logger.debug(s)

    def turn_to_hex(self,
                    bytes,
                    title="[DEF.]",
                    base=2,
                    modifier_font=" 0x",
                    modifier_behind=""):
        """转换为16进制列表

        Args:
            bytes (List): HEX数组
            title (str, optional): 标题. Defaults to "[DEF.]".
            base (int, optional): 宽度. Defaults to 8.
            modifier_font (str, optional): 每个元素的前缀. Defaults to " 0x".
            modifier_behind (str, optional): 每个元素的后缀. Defaults to "".

        Return:
            list:16进制列表
        """
        s = title
        if base == 4:
            for i in bytes:
                s += modifier_font
                s += f'{i:04X}'
                s += modifier_behind
        else:
            for i in bytes:
                s += modifier_font
                s += f'{i:02X}'
                s += modifier_behind
        return s
