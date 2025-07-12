from vebp.Libs.File import FolderStream
from vebp.path import initContentPath


def create(path):
    FolderStream(initContentPath).copy_tree(str(path))