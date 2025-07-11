import argparse

from vebp.Command.Builder import CommandBuild
from vebp.Command.Clean import CommandClean
from vebp.Command.Cwd import CommandCwd
from vebp.Command.Dev import CommandDev
from vebp.Command.Exit import CommandExit
from vebp.Command.Help import CommandHelp
from vebp.Command.Init import CommandInit
from vebp.Command.Pack import CommandPack
from vebp.Command.Package import CommandPackage
from vebp.Command.Plugin import CommandPlugin
from vebp.Command.Version import CommandVersion
from vebp.Libs.Args import ArgsUtil


class CommandMatch:
    @staticmethod
    def handle(parser, _type=0, _input: str="") -> None:
        # noinspection PyUnreachableCode
        match _type:
            case 0:
                parsed_args = parser.parse_args()
            case 1:
                parsed_args = ArgsUtil.parse_input_args(_input, parser)
            case other:
                raise argparse.ArgumentTypeError(other)
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
            case "help":
                CommandHelp.handle(parser)
            case "version":
                CommandVersion.handle()