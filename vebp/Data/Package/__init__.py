from vebp.Data import VebpData


class Package(VebpData):
    FILENAME = "vebp-package.json"

    PROP_DICT = {
        "name": {
            "generate": True,
            "default": "$cwd"
        },
        "venv": {
            "generate": True,
            "default": ".venv"
        },
        "scripts": {}
    }