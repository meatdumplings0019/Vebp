import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Union, Optional

from vebp.Libs.File import FileStream, FolderStream
from vebp.Libs.File.path import MPath_
from vebp.Builder import BaseBuilder
from vebp.Data.BuildConfig import BuildConfig
from vebp.Data.globals import get_config
from vebp.Data.Package import Package


class Builder(BaseBuilder):
    def __init__(self, name=None, icon=None, parent_path=None, sub=None, base_path=".") -> None:
        super().__init__(name, base_path)
        self._icon = Path(icon) if icon else None
        self._console = False
        self._onefile = True
        self._assets: Dict[str, list[Path]] = {}
        self._in_assets: Dict[str, list[Path]] = {}
        self._sub = sub
        self._parent_path = parent_path
        self._exclude_modules = []

        self._auto_run = True

        self.sub_project_src = {}
        self.sub_project_builder = []

    def _get_path(self) -> None:
        if not self._parent_path:
            self._parent_path = self.name

        self._project_dir = self.base_output_dir / self._parent_path

        if self._sub:
            self._project_dir /= self._sub

    @property
    def icon(self) -> Path:
        return self._icon

    @property
    def console(self) -> bool:
        return self._console

    @property
    def onefile(self) -> bool:
        return self._onefile

    @property
    def assets(self) -> Dict[str, list[Path]]:
        return self._assets

    @property
    def in_assets(self) -> Dict[str, list[Path]]:
        return self._in_assets

    @property
    def auto_run(self) -> bool:
        return self._auto_run

    @auto_run.setter
    def auto_run(self, value) -> None:
        self._auto_run = value

    @staticmethod
    def from_package(folder_path = None, sub=None, parent=None, base_path=".") -> Optional["Builder"]:
        if folder_path:
            folder_path = Path(str(folder_path))
            build_config = BuildConfig(folder_path / BuildConfig.FILENAME)
            package_config = Package(folder_path / Package.FILENAME)

        else:
            build_config = BuildConfig(BuildConfig.FILENAME)
            package_config = Package(Package.FILENAME)

        if not build_config or not package_config:
            return None

        builder = Builder(package_config.get('name', None), sub=sub, parent_path=parent, base_path=base_path)
        builder.venv = package_config.get('venv', '.venv')

        builder.set_script(build_config.get('main', None))
        builder.set_console(build_config.get('console', False))

        icon = build_config.get('icon', None)
        if icon:
            builder._icon = Path(icon)

        onefile = build_config.get('onefile', True)
        builder.set_onefile(onefile)

        assets_lst = build_config.get('assets', [])
        if assets_lst:
            for asset in assets_lst:
                builder.add_assets(asset.get("from", []), asset.get("to", "."))

        in_assets_lst = build_config.get('in_assets', [])
        if in_assets_lst:
            for asset in in_assets_lst:
                builder.add_in_assets(asset.get("from", []), asset.get("to", "."))

        sub_pro = build_config.get('sub_project', [])
        if sub_pro:
            for pro in sub_pro:
                builder.add_sub_project(pro.get("path", "sub_project"), pro.get("script", None))
        exclude_modules = build_config.get('exclude_modules', [])
        builder._exclude_modules = exclude_modules

        auto_run = get_config().get('autoRun', True)
        builder.auto_run = auto_run

        return builder

    def set_console(self, console) -> "Builder":
        if console:
            self._console = console
        return self

    def set_onefile(self, onefile) -> "Builder":
        if onefile:
            self._onefile = onefile
        return self

    def add_assets(self, sources: list[Union[str, Path]], target_relative_path: str = "") -> "Builder":
        if not sources:
            return self

        source_paths = [Path(source) for source in sources]

        self.assets.setdefault(target_relative_path, [])

        for source in source_paths:
            source = self._base_path / source
            if not source.exists():
                print(f"警告: 资源源不存在: {source}", file=sys.stderr)
            else:
                self.assets[target_relative_path].append(source)

        return self

    def add_in_assets(self, sources: list[Union[str, Path]], target_relative_path: str = "") -> "Builder":
        if not sources:
            return self

        source_paths = [Path(source) for source in sources]

        self.in_assets.setdefault(target_relative_path, [])

        for source in source_paths:
            source = self._base_path / source
            if not source.exists():
                print(f"警告: 内部资源源不存在: {source}", file=sys.stderr)
            else:
                self.in_assets[target_relative_path].append(source)

        return self

    def add_sub_project(self, key, package_path) -> "Builder":
        if package_path:
            self.sub_project_src[key] = package_path

        return self

    def _validate(self) -> bool:
        super()._validate()

        if not self.script_path or not self.script_path.is_file():
            raise ValueError(f"脚本文件不存在: {self.script_path}")

        if self.icon and not self.icon.is_file():
            raise ValueError(f"图标文件不存在: {self.icon}")

        return True

    def _get_add_data_args(self) -> list[str]:
        add_data_args = []
        separator = ";" if platform.system() == "Windows" else ":"

        for target_relative, sources in self.in_assets.items():
            for source in sources:
                abs_source = source.resolve()

                arg = f"{abs_source}{separator}{Path(target_relative) / source}"
                add_data_args.extend(["--add-data", arg])

        return add_data_args

    def _copy_assets(self) -> bool:
        if not self._assets:
            return True

        print("\n📦 复制外部资源...")
        success = True

        for target_relative, sources in self.assets.items():
            target_path = self._project_dir / target_relative
            target_folder = FolderStream(str(target_path))

            if not target_folder.create():
                print(f"  创建目录失败: {target_path}", file=sys.stderr)
                success = False
                continue

            for source in sources:
                try:
                    source_path = source.resolve()
                    dest_path = target_path / source.name
                    if source.is_dir():
                        print(f"  📁 复制目录: {source} -> {dest_path}")
                        if dest_path.exists:
                            shutil.rmtree(dest_path)

                        FolderStream(str(dest_path)).create()

                        for root, dirs, files in os.walk(source_path):
                            relative_path = Path(root).relative_to(source_path)
                            dest_dir = dest_path / relative_path

                            FolderStream(str(dest_dir)).create()

                            # 复制所有文件
                            for file in files:
                                src_file = Path(root) / file
                                dest_file = dest_dir / file
                                if not FileStream.copy(str(src_file), str(dest_file)):
                                    print(f"    复制文件失败: {src_file} -> {dest_file}", file=sys.stderr)
                                    success = False
                    else:
                        print(f"  📄 复制文件: {source} -> {dest_path}")
                        if not FileStream.copy(str(source_path), str(dest_path)):
                            print(f"    复制文件失败: {source} -> {dest_path}", file=sys.stderr)
                            success = False
                except Exception as e:
                    print(f"  ❌ 复制 {source} 出错: {str(e)}", file=sys.stderr)
                    success = False

        return success

    def _print_result(self, target_path) -> None:
        print(f"\n🎉 项目构建成功!")
        print(f"📂 输出目录: {self._project_dir}")
        print(f"📦 输出文件: {target_path}")
        print(f"📦 单文件打包: {'✅' if self.onefile else '❌'}")
        print(f"🖥️ 显示控制台: {'✅' if self.console else '❌'}")
        print(f"🚀 自动运行: {'✅' if self.auto_run else '❌'}")

    def _copy_exe(self, source_path, target_path) -> bool:
        if self.onefile:
            if FileStream.copy(str(source_path), str(target_path)):
                print(f"  ✅ 已复制可执行文件到: {target_path}")
                return True
            else:
                print(f"  ❌ 复制可执行文件失败: {source_path} -> {target_path}", file=sys.stderr)
                return False
        else:
            print(f"  📁 复制目录: {source_path} -> {target_path}")

            for item in source_path.iterdir():
                dest_item = target_path / item.name
                if item.is_dir():
                    shutil.copytree(item, dest_item, dirs_exist_ok=True)
                    return True
                else:
                    if not FileStream.copy(str(item), str(dest_item)):
                        print(f"    复制文件失败: {item} -> {dest_item}", file=sys.stderr)
                        return False

            return True

    def _start_build(self, cmd) -> None:
        print(f"\n🔨 开始打包项目: {self.name}")
        print(f"📜 脚本路径: {self.script_path}")
        print(f"📦 打包模式: {'单文件 ✅' if self.onefile else '带依赖的目录 📁'}")
        print(f"🖥️ 控制台设置: {'显示 ✅' if self.console else '隐藏 ❌'}")
        print(f"🚀 自动运行: {'✅' if self.auto_run else '❌'}")

        if self.in_assets:
            print("📦 要嵌入的内部资源:")
            for target_relative, sources in self.in_assets.items():
                for source in sources:
                    print(f"  ➡️ {source} -> {target_relative}")

        print("⏳ 打包进行中...")

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            check=True
        )

    def _get_cmd(self, python_path) -> list[str]:
        cmd = [str(python_path), '-m', 'PyInstaller', '--noconfirm']

        if self.onefile:
            cmd.append('--onefile')
        else:
            cmd.append('--onedir')

        if not self.console:
            cmd.append('--noconsole')

        if self.icon:
            cmd.extend(['--icon', str(self.icon.resolve())])

        if self._exclude_modules:
            for module in self._exclude_modules:
                cmd.extend(['--exclude-module', module])

        cmd.extend(self._get_add_data_args())
        cmd.extend(['--name', self.name, str(self.script_path.resolve())])

        return cmd

    @staticmethod
    def _run_executable(exe_path: Path) -> None:
        try:
            if not exe_path.exists():
                print(f"❌ 可执行文件不存在: {exe_path}", file=sys.stderr)
                return

            print(f"🚀 启动程序: {exe_path}")
            if platform.system() == 'Windows':
                subprocess.Popen([str(exe_path)], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([str(exe_path)])
        except Exception as e:
            print(f"运行程序失败: {str(e)}", file=sys.stderr)

    def _compile_sub_project(self) -> None:
        if not self.sub_project_src:
            return

        for key, pro in self.sub_project_src.items():
            self.sub_project_builder.append(self.from_package(pro, key, self._project_dir, pro))

    def _build_sub_project(self) -> None:
        for pro in self.sub_project_builder:
            pro.build()

    def build(self) -> bool:
        super().build()
        self._get_path()

        python_path = self._get_venv_python()

        FolderStream(str(self._project_dir)).create()

        try:
            self._validate()
            self._compile_sub_project()
            self._build_sub_project()
            self._start_build(self._get_cmd(python_path))

            if self.onefile:
                source_path = Path('dist') / f"{self.name}.exe"
                target_path = self._project_dir / f"{self.name}.exe"
            else:
                source_path = Path('dist') / self.name
                target_path = self._project_dir

            copy = self._copy_exe(source_path, target_path)
            self._print_result(target_path)
            assets = self._copy_assets()

            if self.onefile:
                run_path = target_path
            else:
                run_path = target_path / f"{self.name}.exe"

            if not self._sub and self._auto_run:
                print(f"\n🚀 正在启动应用程序...")
                self._run_executable(run_path)

            return copy and assets
        except subprocess.CalledProcessError as e:
            print(f"\n❌ 打包失败! 错误代码: {e.returncode}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"\n❌ {str(e)}", file=sys.stderr)
            return False

    @staticmethod
    def clean():
        try:
            print(f"\n🧹 正在清理构建文件...")
            shutil.rmtree(Builder().base_output_dir, ignore_errors=True)
            shutil.rmtree(MPath_.cwd / "build", ignore_errors=True)
            shutil.rmtree(MPath_.cwd / "dist", ignore_errors=True)
            print(f"✅ 清理成功, 已删除'vebp-build', 'build', 'dist'")
        except Exception as e:
            print(f"\n❌ {str(e)}", file=sys.stderr)

    def __repr__(self):
        return f'<Builder name: {self.name}>'