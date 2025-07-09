from Vebp.Data.Config import Config

_global_config_manager = None


def get_config() -> Config:
    """
    获取全局插件管理器实例

    此函数返回一个全局唯一的插件管理器实例，适用于整个应用。
    如果尚未初始化，会创建一个新的实例。

    用法示例:
        pm = get_config_manager()
        pm.load_configs("configs/")

    :return: 全局插件管理器实例
    """
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = Config(Config.FILENAME)
    return _global_config_manager


def reset_config():
    """
    重置全局插件管理器

    主要用于测试环境或需要重新初始化插件的场景
    在正常运行时通常不需要调用此函数
    """
    global _global_config_manager
    _global_config_manager = None