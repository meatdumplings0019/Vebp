import sys
from pathlib import Path
from typing import Dict, Any, Optional

from vebp.Libs.File import FolderStream, FileStream
from vebp.Libs.File.modulelib import ModuleLoader
from vebp.Libs.File.zip import ZipContent
from vebp.Data.PluginConfig import PluginConfig
from vebp.Data.globals import get_config
from vebp.Plugin import Plugin


class PluginManager:
    def __init__(self):
        """
        插件管理器初始化
        """
        # 插件存储字典: {namespace: PluginConfig 实例}
        self.plugins: Dict[str, Plugin] = {}
        # 记录插件包名到路径的映射
        self.package_paths: Dict[str, str] = {}

    def load_plugins(self):
        """
        加载指定目录下的所有插件
        """
        plugin_dir = get_config().get("plugins", "plugins", "src")

        f = FolderStream(plugin_dir).create()

        for fs in f.walk().files:
            self.load_plugin(fs.path)

        for ff in f.walk().folders:
            self.load_plugin(ff.path)

    def load_plugin(self, plugin_name: str | Path):
        try:
            plugin = Path(str(plugin_name))

            if FileStream(plugin).suffix == ".zip":
                with ZipContent(plugin) as zipf:
                    self._load_single_plugin(zipf)

            if plugin.is_dir():
                self._load_single_plugin(plugin)

        except Exception as e:
            print(f"🔥 解析失败[{plugin_name}]: {str(e)}]")

    def _load_single_plugin(self, plugin_path: Path):
        """
        加载单个插件

        :param plugin_path: 插件路径
        """
        plugin_dir = Path(plugin_path)

        meta = PluginConfig(plugin_dir / PluginConfig.FILENAME)

        namespace = meta.get("namespace", None)
        author = meta.get("author", "null")

        if not namespace:
            return

        if namespace in self.plugins:
            return

        package_name = f"plugin_{namespace}"

        if package_name in sys.modules:
            return

        with ModuleLoader(plugin_dir, package_name, "main.py") as module:
            main_module = module

        # 4. 创建并存储 PluginConfig 实例
        plugin = Plugin(
            namespace=namespace,
            author=author,
            module=main_module,
            package_name=package_name,
            meta=meta.file
        )
        self.plugins[namespace] = plugin
        self.package_paths[package_name] = str(plugin_dir)

        print(f"✅ 插件加载成功: {namespace} by {author}")

    def run_hook(self, namespace: str, hook_name: str, *args, **kwargs) -> Any:
        """
        执行指定插件的钩子函数

        :param namespace: 插件命名空间
        :param hook_name: 钩子名称（不需要带 _hook 后缀）
        :param args: 传递给钩子函数的参数
        :param kwargs: 传递给钩子函数的关键字参数
        :return: 钩子函数的返回值
        """
        if namespace in self.plugins:
            return self.plugins[namespace].run_hook(hook_name, *args, **kwargs)

        print(f"插件未加载: {namespace}")
        return None

    def run_hook_all(self, hook_name: str, *args, **kwargs) -> list[Any]:
        if not self.plugins: return []

        return [n.run_hook(hook_name, *args, **kwargs) for n in self.plugins.values()]

    def get_plugin(self, namespace: str) -> Optional[Plugin]:
        """
        获取插件实例

        :param namespace: 插件命名空间
        :return: PluginConfig 实例或 None
        """
        return self.plugins.get(namespace)

    def list_plugins(self) -> list[str]:
        """
        列出所有已加载插件的命名空间

        :return: 插件命名空间列表
        """
        return list(self.plugins.keys())

    def unload_plugin(self, namespace: str):
        """
        卸载指定插件

        :param namespace: 插件命名空间
        """
        if namespace in self.plugins:
            plugin = self.plugins[namespace]
            package_name = plugin.package_name

            # 清理所有相关模块
            to_remove = [name for name in sys.modules
                         if name == package_name or name.startswith(f"{package_name}.")]

            for module_name in to_remove:
                del sys.modules[module_name]

            # 清理插件记录
            del self.plugins[namespace]
            if package_name in self.package_paths:
                del self.package_paths[package_name]

            print(f"✅ 插件已卸载: {namespace}")
        else:
            print(f"⚠️ 插件未加载: {namespace}")

    def enable(self, namespace: str):
        self.get_plugin(namespace).enable()

    def disable(self, namespace: str):
        self.get_plugin(namespace).disable()