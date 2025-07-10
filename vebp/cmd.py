import sys

from colorama import Fore, Style

from vebp.Libs.Args import ArgsUtil
from vebp.Command.Create import CommandCreate
from vebp.Command.matches import CommandMatch
from vebp.version import __version__
from vebp.base import VebpBase


class CMD(VebpBase):
    def __init__(self) -> None:
        super().__init__()
        self.parser = CommandCreate.create()

    def run(self) -> None:
        print(f"Vebp {__version__}")
        print('Type "help", "copyright", "credits" or "license" for more information.')
        print()

        while True:
            try:
                print(f"{Fore.MAGENTA}>>> ", end="")
                print(Style.RESET_ALL, end="")
                file = input()
                print(Style.RESET_ALL, end="")
                CommandMatch.handle(ArgsUtil.parse_input_args(file, self.parser))
            except Exception as e:
                print(Style.RESET_ALL, end="")
                print(f"{Fore.RED}{e}")