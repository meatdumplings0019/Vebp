import os
import sys
import inspect

from pathlib import Path


class MPath:
    @property
    def cwd(self) -> Path:
        """
        获取当前工作目录（命令行路径）

        返回:
            Path: 当前工作目录的绝对路径
        """
        return Path.cwd()
    @property
    def scriptDir(self) -> Path:
        """
        获取当前执行脚本所在的目录

        返回:
            Path: 当前脚本所在目录的绝对路径
        """
        return Path(os.path.dirname(os.path.abspath(sys.argv[0])))

    @property
    def callerDir(self) -> Path:
        """
        获取调用者所在的目录（在模块中使用时获取导入模块的位置）

        返回:
            Path: 调用者所在目录的绝对路径
        """
        # 获取调用栈中上一帧的信息
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        if module and hasattr(module, '__file__'):
            return Path(os.path.dirname(os.path.abspath(module.__file__)))
        return Path(self.scriptDir)

    @staticmethod
    def get() -> Path:
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath("")

        return Path(base_path)

    @staticmethod
    def change_directory(path) -> None:
        """
        改变当前工作目录

        参数:
            path (str): 目标路径
        """
        os.chdir(path)

    @staticmethod
    def resolve_relative_path(relative_path, base_path=None) -> Path:
        """
        解析相对路径为绝对路径

        参数:
            relative_path (str): 相对路径
            base_path (str, optional): 基础路径，默认为当前工作目录

        返回:
            Path: 绝对路径
        """
        base = base_path or MPath_.cwd
        return Path(os.path.abspath(str(os.path.join(base, relative_path))))

    @property
    def homeDir(self) -> Path:
        """
        获取用户主目录

        返回:
            str: 用户主目录路径
        """
        return Path(os.path.expanduser("~"))

    @staticmethod
    def is_absolute_path(path) -> bool:
        """
        检查路径是否为绝对路径

        参数:
            path (str): 要检查的路径

        返回:
            bool: 如果是绝对路径返回True，否则False
        """
        return os.path.isabs(path)

    @staticmethod
    def get_path_components(path) -> tuple[str, ...]:
        """
        分解路径为各个组成部分

        返回:
            tuple: (目录名, 基本文件名, 扩展名)
        """
        dir_name = os.path.dirname(path)
        base_name = os.path.basename(path)
        file_name, ext = os.path.splitext(base_name)
        return dir_name, file_name, ext

MPath_ = MPath()