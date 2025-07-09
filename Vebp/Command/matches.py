import sys

from Vebp.Command.Builder import CommandBuild
from Vebp.Command.Clean import CommandClean
from Vebp.Command.Dev import CommandDev
from Vebp.Command.Exit import CommandExit
from Vebp.Command.Init import CommandInit
from Vebp.Command.Pack import CommandPack
from Vebp.Command.Package import CommandPackage
from Vebp.Command.Plugin import CommandPlugin


class CommandMatch:
    @staticmethod
    def handle(parsed_args) -> None:
        # noinspection PyUnreachableCode
        match parsed_args.command:
            case 'build':
                CommandBuild.handle(parsed_args)
            case 'init':
                CommandInit.handle(parsed_args)
            case 'package':
                CommandPackage.handle()
            case 'pack':
                CommandPack.handle()
            case 'dev':
                CommandDev.handle(parsed_args)
            case 'plugin':
                CommandPlugin.handle(parsed_args)
            case 'exit':
                CommandExit.handle()
            case "clean":
                CommandClean.handle()
            case others:
                print(f"{others} dont have.", file=sys.stderr)