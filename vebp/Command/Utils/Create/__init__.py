﻿import argparse

from vebp.Command import Command
from vebp.Command.Utils.Add import CommandAdd
from vebp.Command.Commands.Version import CommandVersion

class CommandUtilsCreate:
    @staticmethod
    def create() -> argparse.ArgumentParser:
        parser = Command(
            description='🚀 vebp - 增强的 PyInstaller 打包工具',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''示例:
              🔨 vebp build MyProject --src app.py
              🔨 vebp build MyApp -s app.py -i app.ico -c
              🔨 vebp build ProjectX -s main.py -d
              🔨 vebp build Game -s app.py --asset "images;resources" --asset "sfx;resources"
              🔨 vebp build App -s app.py --in_asset "config.json;settings"
              🔨 vebp build App -s app.py --in_asset "templates;ui" --asset "README.md"
              🔨 vebp build  # 使用 vebp-build.json 中的配置
              📦 vebp package # 显示 package 配置
            ''',
            add_help=False,

        )

        parser.add_argument('--help', '-h', action='help',
                            help='ℹ️ 显示帮助信息', default=argparse.SUPPRESS)
        parser.add_argument('--version', '-v', action='version',
                            help='ℹ️ 显示版本信息', version=CommandVersion.get_value())

        subparsers = parser.add_subparsers(
            title='📋 可用命令',
            dest='command',
            help='👉 选择要执行的操作'
        )

        CommandAdd.add_build_command(subparsers)
        CommandAdd.add_init_command(subparsers)
        CommandAdd.add_package_command(subparsers)
        CommandAdd.add_pack_command(subparsers)
        CommandAdd.add_dev_command(subparsers)
        CommandAdd.add_plugin_command(subparsers)
        CommandAdd.add_exit_command(subparsers)
        CommandAdd.add_clean_command(subparsers)
        CommandAdd.add_cwd_command(subparsers)
        CommandAdd.add_help_command(subparsers)
        CommandAdd.add_version_command(subparsers)
        CommandAdd.add_create_command(subparsers)

        return parser