import sys


class CommandExit:
    @staticmethod
    def handle() -> None:
        sys.exit(0)