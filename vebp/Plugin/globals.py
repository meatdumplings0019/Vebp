from vebp.Plugin.Manager import PluginManager

_global_plugin_manager = None


def get_plugin_manager() -> PluginManager:
    """
    获取全局插件管理器实例

    此函数返回一个全局唯一的插件管理器实例，适用于整个应用。
    如果尚未初始化，会创建一个新的实例。

    用法示例:
        pm = get_plugin_manager()
        pm.load_plugins("plugins/")

    :return: 全局插件管理器实例
    """
    global _global_plugin_manager
    if _global_plugin_manager is None:
        _global_plugin_manager = PluginManager()
    return _global_plugin_manager


def reset_plugin_manager():
    """
    重置全局插件管理器

    主要用于测试环境或需要重新初始化插件的场景
    在正常运行时通常不需要调用此函数
    """
    global _global_plugin_manager
    _global_plugin_manager = None