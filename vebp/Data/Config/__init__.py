from typing import Any

from vebp.Data import VebpData


class Config(VebpData):
    FILENAME = "vebp-config.json"

    PROP_DICT = {
        "autoRun": {},
        "plugins": {
            "value": {
                "src": {},
                "add": {}
            }
        },
    }

    @staticmethod
    def default() -> dict[str, Any]:
        return {
            "autoRun": True,
            "plugins": {
                "src": "plugins",
                "add": {}
            }
        }

