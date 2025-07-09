from Vebp.Data import VebpData


class BuildConfig(VebpData):
    FILENAME = "vebp-build.json"

    PROP_DICT = {
        "main": {
            "generate": True,
            "default": "run.py"
        },
        "console": {
            "generate": True,
            "default": False,
        },
        "icon": {},
        "onefile": {},
        "assets": {},
        "in_assets": {},
        "sub_project": {},
        "exclude_modules": {},
    }