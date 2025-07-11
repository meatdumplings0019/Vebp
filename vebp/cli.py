import sys

from vebp.Command.matches import CommandMatch
from vebp.base import VebpBase
from vebp.Command.Create import CommandCreate
from vebp.cmd import CMD


class CLI(VebpBase):
    def __init__(self) -> None:
        super().__init__()
        self.parser = CommandCreate.create()

    def run(self, args=None) -> None:
        if len(sys.argv) == 1:
            cmd = CMD()
            cmd.run()
            sys.exit(0)

        CommandMatch.handle(self.parser)