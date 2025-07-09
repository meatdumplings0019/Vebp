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
                print("🔨 开始构建项目...")
                CommandBuild.handle(parsed_args)
            case 'init':
                print("🛠️ 初始化项目...")
                CommandInit.handle(parsed_args)
            case 'package':
                print("📦 显示包配置...")
                CommandPackage.handle()
            case 'pack':
                print("📦 打包项目...")
                CommandPack.handle()
            case 'dev':
                print("🚀 运行开发脚本...")
                CommandDev.handle(parsed_args)
            case 'plugin':
                print("🧩 插件工具...")
                CommandPlugin.handle(parsed_args)
            case 'exit':
                CommandExit.handle()
            case "clean":
                CommandClean.handle()
            case others:
                print(f"{others} dont have.", file=sys.stderr)