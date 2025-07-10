from colorama import Fore

from Vebp.Command.Builder import CommandBuild
from Vebp.Command.Clean import CommandClean
from Vebp.Command.Cwd import CommandCwd
from Vebp.Command.Dev import CommandDev
from Vebp.Command.Exit import CommandExit
from Vebp.Command.Init import CommandInit
from Vebp.Command.Pack import CommandPack
from Vebp.Command.Package import CommandPackage
from Vebp.Command.Plugin import CommandPlugin


class CommandMatch:
    @staticmethod
    def handle(parsed_args) -> None:
        command = getattr(parsed_args, "command", None)

        # noinspection PyUnreachableCode
        match command:
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
            case "cwd":
                CommandCwd.handle()
            case others:
                print(f"{Fore.RED}{others} dont have.")