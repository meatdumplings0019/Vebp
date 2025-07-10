from vebp.Command.Builder import CommandBuild
from vebp.Command.Clean import CommandClean
from vebp.Command.Cwd import CommandCwd
from vebp.Command.Dev import CommandDev
from vebp.Command.Exit import CommandExit
from vebp.Command.Init import CommandInit
from vebp.Command.Pack import CommandPack
from vebp.Command.Package import CommandPackage
from vebp.Command.Plugin import CommandPlugin


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