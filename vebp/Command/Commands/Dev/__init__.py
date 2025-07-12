import subprocess
import sys
from vebp.Libs.File.path import MPath_
from vebp.Data.Package import Package
from vebp.Command.Commands.Dev.mapper import CommandMapper


class CommandDev:
    @staticmethod
    def handle(args) -> None:
        try:
            # 尝试加载package配置
            package = Package(MPath_.cwd / Package.FILENAME)
            scripts = package.get("scripts", {})

            script_name = args.script
            if script_name not in scripts:
                print(f"❌ 错误: 未找到脚本 '{script_name}'", file=sys.stderr)

                # 显示可用脚本和命令映射
                print(f"📋 可用脚本: {', '.join(scripts.keys())}")
                print("\n📋 可用命令映射:")
                for cmd, replacement in CommandMapper.get_available_commands().items():
                    print(f"  ➡️ {cmd} -> {replacement}")

                sys.exit(1)

            command_str = scripts[script_name]
            print(f"🚀 执行脚本: {script_name}")

            # 解析命令映射
            resolved_command = CommandMapper.resolve_command(command_str)

            print(f"📜 命令: {' '.join(resolved_command)}")

            print("")

            # 执行脚本命令
            result = subprocess.run(
                resolved_command,
                shell=True,
                cwd=MPath_.cwd
            )

            sys.exit(result.returncode)

        except FileNotFoundError:
            print(f"❌ 错误: 未找到 {Package.FILENAME} 文件", file=sys.stderr)
            print("👉 请先运行 'vebp init' 创建配置文件")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 执行错误: {str(e)}", file=sys.stderr)
            sys.exit(1)