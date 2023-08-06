# !/usr/bin/env python
# _*_coding: utf-8 _*_
# @Time: 2022/2/14 20:46
# @Author: "John"

from datetime import datetime
from os.path import basename

from mob_tools import logger
from mob_tools._get_frame import get_frame

"""
基于loguru的日志模块
"""


def formatted_mob_msg(msg, level, class_name="", func_name="", line_num="", track_id=""):
    """
    :param msg:         日志内容
    :param level:       日志级别
    :param class_name:  调用模块
    :param line_num:    调用行号
    :param func_name:  调用方法名称
    :param track_id:    trackId
    :return:            格式化后的日志内容
    """
    formatted_level = "{0:>8}".format(f"{level}")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    formatted_msg = f"[{ts} {formatted_level}] {class_name}.{func_name}:{line_num} {msg} {track_id}"
    return formatted_msg


class MobLoguru:
    def __init__(self, deep=1, log_file="", ):
        """
        :param deep:           获取调用者文件名、方法名、行号深度
        :log_file  :           输出日志文件目录
        """
        self._frame = None
        self._msg = ""
        self._level = ""
        self._track_id = ""
        self._deep = deep
        self._p_track_id = ""

        if log_file:
            logger.add(log_file,
                       format="{message}",
                       rotation="200 MB")

    def debug(self, msg):
        self._msg = msg
        self._level = "DEBUG"
        self._frame = get_frame(self._deep)
        return self

    def info(self, msg):
        self._msg = msg
        self._level = "INFO"
        self._frame = get_frame(self._deep)
        return self

    def warning(self, msg):
        self._msg = msg
        self._level = "WARNING"
        self._frame = get_frame(self._deep)
        return self

    def error(self, msg):
        self._msg = msg
        self._level = "ERROR"
        self._frame = get_frame(self._deep)
        return self

    def critical(self, msg):
        self._msg = msg
        self._level = "CRITICAL"
        self._frame = get_frame(self._deep)
        return self

    def p_track_id(self, p_track_id):
        self._p_track_id = p_track_id
        return self

    def track_id(self, track_id=''):
        self._track_id = (self._p_track_id + "-" + track_id) if self._p_track_id else track_id
        self._p_track_id = ""  # 置空p_track_id
        formatted_msg = formatted_mob_msg(
            self._msg,
            self._level,
            basename(self._frame.f_code.co_filename),  # 脚本名称
            self._frame.f_code.co_name,  # 方法名
            str(self._frame.f_lineno),  # 行号
            self._track_id
        )
        logger.log(self._level, formatted_msg)
        return self

    def tracker(self, track_id=''):
        self._track_id = (self._p_track_id + "-" + track_id) if self._p_track_id else track_id
        self._p_track_id = ""  # 置空p_track_id
        formatted_msg = formatted_mob_msg(
            self._msg,
            self._level,
            basename(self._frame.f_code.co_filename),  # 脚本名称
            self._frame.f_code.co_name,  # 方法名
            str(self._frame.f_lineno),  # 行号
            self._track_id
        )
        logger.log(self._level, formatted_msg)
        return self

    def commit(self):
        pass
