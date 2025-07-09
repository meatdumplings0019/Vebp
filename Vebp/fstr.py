from Vebp.Libs.String import get_fs
from Vebp.Libs.File.path import MPath_



def format_string(string):
    if not isinstance(string, str):
        return string

    return get_fs(string, {
        "cwd": MPath_.cwd.name,
    })