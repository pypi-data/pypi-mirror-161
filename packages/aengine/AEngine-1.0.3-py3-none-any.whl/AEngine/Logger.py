from enum import Enum

from AEngine.Debug import Debug
from AEngine.Errors import Error
from AEngine.Files import FileManager
from AEngine.Warning import Warn
from AEngine.defaults import logger_map


class LogType(Enum):
    Error = 0
    Warning = 1
    Debug = 2
    FileLog = 3


class Logger:
    color_map = logger_map

    @classmethod
    def log(cls, message, log_type=LogType.Debug, **kwargs):
        _methods = {
            LogType.Error: lambda x: cls.__log_error(x, kwargs.get('color')),
            LogType.Warning: lambda x: cls.__log_warning(x, kwargs.get('color')),
            LogType.Debug: lambda x: cls.__log_debug(x, kwargs.get('prefix'), kwargs.get('color')),
            LogType.FileLog: lambda x: cls.__log_to_file(x, kwargs.get('filename'))
        }
        _methods[log_type](message)

    @classmethod
    def __log_error(cls, message, color=None):
        if color is None:
            color = cls.color_map.Error
        Error.raise_safely(message, color)

    @classmethod
    def __log_warning(cls, message, color=None):
        if color is None:
            color = cls.color_map.Warning
        Warn.raise_warning(message, color)

    @classmethod
    def __log_debug(cls, message, prefix, color=None):
        if color is None:
            color = cls.color_map.Debug
        Debug.log(message, prefix, color)

    @staticmethod
    def __log_to_file(message, filename=None):
        if filename is None:
            filename = 'logs/log.txt'
        message += '\n'

        if not FileManager.check_instance(filename):
            FileManager.create_file(filename)
            FileManager.add(filename, message)

        else:
            FileManager.add(filename, message)

    @classmethod
    def set_color_map(cls, CMap):
        cls.color_map = CMap
