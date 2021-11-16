#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import logging
import logging.handlers


class Logger(logging.Logger):
    """
    日志类
    """
    LOG_FILENAME = '/opt/ClashV/clash-v.log'

    LOG_FMT = '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'

    level_relations = {
        """
        日志级别关系映射
        """
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'fatal': logging.CRITICAL
    }

    def __init__(self, name='root', filename=LOG_FILENAME, level='info', mode='a', back_num=5, fmt=LOG_FMT):
        """
           初始化日志配置
           filename: 指定生成文件名
           level:  日志级别
           mode:    输入模式
           back_num: 能留几个日志文件
           fmt: 日志输出格式
        """
        if not os.path.isdir(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        # 初始化日志
        super(Logger, self).__init__(name)
        # 设置日志级别
        self.setLevel(self.level_relations.get(level))
        # 设置日志格式
        formatter = logging.Formatter(fmt)
        # 控制台上输出
        console_handler = logging.StreamHandler()
        # 设置屏幕上显示的格式
        console_handler.setFormatter(formatter)
        # 把对象加到logger里
        self.addHandler(console_handler)
        # 往文件里写入
        # 指定间隔时间自动生成文件的处理器
        file_handler = logging.handlers.RotatingFileHandler(filename, mode, maxBytes=10485760, backupCount=back_num, encoding="utf-8")
        # 设置文件里写入的格式
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)
