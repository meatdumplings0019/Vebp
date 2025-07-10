from vebp.Libs.File.path import MPath_


class CommandCwd:
    @staticmethod
    def handle():
        print(f"{MPath_.cwd}")
        print()