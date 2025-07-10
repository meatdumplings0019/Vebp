import platform
from pathlib import Path
from typing import Optional, Union

from vebp.Libs.File import FolderStream
from vebp.Libs.File.path import MPath_
from vebp.base import VebpBase


class BaseBuilder(VebpBase):
    """基础构建器类，提供项目构建的基本功能"""

    def __init__(self, name: Optional[str] = None, base_path: str = ".") -> None:
        """
        初始化基础构建器

        :param name: 项目名称
        :param base_path: 基础路径
        """
        super().__init__()
        self._name = name
        self._base_path = Path(base_path)
        self._venv = ".venv"
        self._script_path = None
        self._project_dir = None

        FolderStream(self.base_output_dir).create()

    @property
    def name(self) -> str:
        """获取项目名称"""
        return self._name

    @property
    def project_dir(self) -> Path:
        """获取项目目录"""
        return self._project_dir

    @property
    def venv(self) -> str:
        """获取虚拟环境路径"""
        return self._venv

    @venv.setter
    def venv(self, value: str) -> None:
        """设置虚拟环境路径"""
        self._venv = value

    @property
    def script_path(self) -> Path:
        """获取脚本路径"""
        return self._script_path

    @property
    def base_output_dir(self) -> Path:
        return MPath_.cwd / "vebp-build"

    def set_script(self, script_path: str) -> "BaseBuilder":
        """
        设置脚本路径

        :param script_path: 脚本路径
        :return: 自身实例
        """
        if script_path:
            self._script_path = self._base_path / Path(script_path)
        return self

    def _validate(self) -> None:
        """验证构建器配置"""
        if not self.name:
            raise ValueError("项目名称是必需的")

    def _get_venv_python(self) -> Optional[Union[str, Path]]:
        venv_dir = MPath_.cwd / Path(self.venv)

        if not venv_dir.exists():
            return None

        if platform.system() == "Windows":
            python_path = venv_dir / "Scripts" / "python.exe"
        else:
            python_path = venv_dir / "bin" / "python"

        if python_path.exists():
            return python_path
        return "python.exe"

    def build(self) -> None:
        """执行构建过程（由子类实现）"""
        pass