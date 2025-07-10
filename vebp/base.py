from vebp.Data.globals import get_config
from vebp.Plugin.globals import get_plugin_manager


class VebpBase:
    def __init__(self):
        get_plugin_manager().load_plugins()

        p_lst = get_config().get("plugins", [], "add")
        if p_lst:
            for p in p_lst:
                get_plugin_manager().load_plugin(p)