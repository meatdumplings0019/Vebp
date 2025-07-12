from colorama import Fore, Style

from vebp.Command.Utils.Create import CommandUtilsCreate
from vebp.Command.Commands.matches import CommandMatch
from vebp.base import VebpBase
from vebp.version import __version__


class CMD(VebpBase):
    def __init__(self) -> None:
        super().__init__()
        self.parser = CommandUtilsCreate.create()

    def run(self) -> None:
        print(f"Vebp {__version__}")
        print('Type "help", "version", "copyright", "credits" or "license" for more information.')
        print()

        while True:
            try:
                print(f"{Fore.MAGENTA}>>> ", end="")
                print(Style.RESET_ALL, end="")
                file = input()
                print(Style.RESET_ALL, end="")
                CommandMatch.handle(self.parser, 1, file)
            except Exception as e:
                print(Style.RESET_ALL, end="")
                print(f"{Fore.RED}{e}")