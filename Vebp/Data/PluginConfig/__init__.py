from Vebp.Data import VebpData


class PluginConfig(VebpData):
    FILENAME = "vebp-plugin.json"

    PROP_DICT = {
        "namespace": {
            "generate": True,
            "default": "vebp_plugin"
        },
        "author": {
            "generate": True,
            "default": "vebp"
        }
    }