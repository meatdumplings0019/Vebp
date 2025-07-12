import json
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Optional

from vebp.Data.Package import Package
from vebp.Libs.File import FileStream, FolderStream
from vebp.Libs.File.path import MPath_
from vebp.Libs.venvs import get_venv_python


class PluginBuilder:
    """插件构建器，专门用于将插件目录打包为 ZIP 格式"""

    def __init__(self, plugin_dir: str) -> None:
        """
        初始化插件构建器

        :param plugin_dir: 插件目录路径
        """
        self.plugin_path = Path(plugin_dir).resolve()
        if not self.plugin_path.exists():
            raise FileNotFoundError(f"🔴 插件目录不存在: {plugin_dir}")
        if not self.plugin_path.is_dir():
            raise ValueError(f"🔴 插件路径必须是目录: {plugin_dir}")

        # 获取插件元数据
        self.meta = self._load_plugin_meta()
        self.plugin_name = self.meta["namespace"]

        # 设置输出目录
        self.output_dir = MPath_.cwd / "vebp-build"
        FolderStream(self.output_dir).create()

        print(f"🔍 找到插件: {self.plugin_name}")
        print(f"📂 插件目录: {self.plugin_path}")
        print(f"📦 输出目录: {self.output_dir}")

    def _load_plugin_meta(self) -> dict:
        """加载插件元数据文件"""
        meta_file_path = self.plugin_path / "vebp-plugin.json"
        meta_file = FileStream(meta_file_path)

        if not meta_file.exists:
            raise FileNotFoundError(f"🔴 插件元数据文件 vebp-plugin.json 不存在")

        try:
            return meta_file.read_json()
        except json.JSONDecodeError:
            raise ValueError("🔴 vebp-plugin.json 格式错误")

    def validate(self) -> bool:
        """验证插件结构是否完整"""
        # 检查必要文件
        required_files = ["vebp-plugin.json", "main.py"]
        plugin_folder = FolderStream(self.plugin_path)
        dir_info = plugin_folder.walk()

        if dir_info is None:
            raise FileNotFoundError(f"🔴 无法访问插件目录: {self.plugin_path}")

        for file in required_files:
            if not any(f.name == file for f in dir_info.files):
                raise FileNotFoundError(f"🔴 插件缺少必要文件: {file}")

        # 验证元数据字段
        required_fields = ["namespace", "author"]
        for field in required_fields:
            if field not in self.meta:
                raise ValueError(f"🔴 vebp-plugin.json 缺少字段: {field}")

        return True

    def _resolve_dependencies(self) -> dict[str, Path]:
        """解析插件依赖，返回依赖包名到安装路径的映射"""
        # 1. 检查是否有 requirements.txt
        req_file = self.plugin_path / "requirements.txt"
        if not req_file.exists():
            print("📝 未找到 requirements.txt，跳过依赖解析")
            return {}

        # 2. 读取依赖列表
        dependencies = []
        with open(req_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "vebp" not in line.lower():
                    dependencies.append(line.split("==")[0].strip())

        if not dependencies:
            print("📝 未找到有效依赖")
            return {}

        print(f"🔍 发现依赖: {', '.join(dependencies)}")

        # 3. 获取当前环境的 site-packages 路径
        site_packages = self._get_site_packages_path()
        if not site_packages:
            print("⚠️ 无法定位 site-packages 目录")
            return {}

        # 4. 收集依赖包路径
        dep_map = {}
        for dep in dependencies:
            dep_path = self._find_dependency_path(site_packages, dep)
            if dep_path:
                dep_map[dep] = dep_path
                print(f"  ✅ 定位依赖: {dep} -> {dep_path}")
            else:
                print(f"  ⚠️ 未找到依赖: {dep}")

        return dep_map

    def _get_site_packages_path(self) -> Optional[Path]:
        """获取当前环境的 site-packages 路径"""
        try:
            # 使用 Python 命令获取 site-packages 路径
            result = subprocess.run(
                [get_venv_python(Package(self.plugin_path / Package.FILENAME).get("venv", ".venv")), "-c", "import site; print(site.getsitepackages()[1])"],
                capture_output=True,
                text=True,
                check=True
            )
            return Path(result.stdout.strip())
        except Exception as e:
            print(f"⚠️ 获取 site-packages 失败: {str(e)}")
            return None

    @staticmethod
    def _find_dependency_path(site_packages: Path, package_name: str) -> Optional[Path]:
        """在 site-packages 中查找依赖包路径"""
        # 尝试直接匹配包名目录
        package_dir = site_packages / package_name
        if package_dir.exists() and package_dir.is_dir():
            return package_dir

        # 尝试匹配带下划线的包名（如 PyYAML -> _yaml）
        underscore_name = f"_{package_name.replace('-', '_')}"
        underscore_dir = site_packages / underscore_name
        if underscore_dir.exists() and underscore_dir.is_dir():
            return underscore_dir

        # 尝试匹配 dist-info 获取真实包名
        for item in site_packages.iterdir():
            if item.name.startswith(f"{package_name}-") and item.name.endswith(".dist-info"):
                # 从 dist-info 获取真实包名
                top_level = item / "top_level.txt"
                if top_level.exists():
                    with open(top_level, "r") as f:
                        real_name = f.readline().strip()
                    real_dir = site_packages / real_name
                    if real_dir.exists():
                        return real_dir
                    # 尝试带下划线版本
                    underscore_real = site_packages / f"_{real_name}"
                    if underscore_real.exists():
                        return underscore_real

        return None

    @staticmethod
    def _copy_dependencies(target_dir: Path, dep_map: dict[str, Path]):
        """复制依赖到 dependencies 文件夹"""
        deps_dir = target_dir / "dependencies"
        FolderStream(deps_dir).create()

        for package_name, source_path in dep_map.items():
            # 复制整个包目录
            dest_path = deps_dir / package_name
            shutil.copytree(
                source_path,
                dest_path,
                ignore=shutil.ignore_patterns(
                    '__pycache__', '*.pyc', '*.pyo', '*.pyd', '*.egg-info'
                )
            )
            print(f"  📦 复制依赖: {package_name}")

    def _copy_plugin_files(self, target_dir: Path):
        """复制插件文件到目标目录，排除不需要的文件"""
        print(f"📦 准备插件文件...")

        # 使用 FolderStream 遍历插件目录
        plugin_folder = FolderStream(self.plugin_path)
        self._copy_folder_contents(plugin_folder, target_dir)

    def _copy_folder_contents(self, source_folder: FolderStream, target_dir: Path):
        """递归复制文件夹内容"""
        dir_info = source_folder.walk()
        if dir_info is None:
            return

        # 处理当前目录的文件
        for file in dir_info.files:
            file_path = Path(file.path)
            if self._should_exclude(file_path):
                continue

            # 计算相对路径和目标路径
            rel_path = file_path.relative_to(self.plugin_path)
            dest_path = target_dir / rel_path

            # 确保目标目录存在
            FolderStream(dest_path.parent).create()

            # 复制文件
            FileStream.copy(str(file_path), str(dest_path))
            print(f"  ➕ 添加: {rel_path}")

        # 递归处理子目录
        for sub_folder in dir_info.folders:
            folder_path = Path(sub_folder.path)
            if self._should_exclude(folder_path):
                continue

            # 复制子目录内容
            self._copy_folder_contents(sub_folder, target_dir)

    def _create_zip_archive(self, source_dir: Path, zip_path: Path):
        """从源目录创建 ZIP 文件"""
        print(f"📦 创建 ZIP 包: {zip_path.name}")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 使用 FolderStream 遍历源目录
            source_folder = FolderStream(source_dir)
            self._add_folder_to_zip(source_folder, zipf, source_dir)

    def _add_folder_to_zip(self, folder: FolderStream, zipf: zipfile.ZipFile, base_dir: Path):
        """递归添加文件夹内容到 ZIP"""
        dir_info = folder.walk()
        if dir_info is None:
            return

        # 添加文件
        for file in dir_info.files:
            file_path = Path(file.path)
            rel_path = file_path.relative_to(base_dir)
            zipf.write(str(file_path), str(rel_path))

        # 递归添加子目录
        for sub_folder in dir_info.folders:
            self._add_folder_to_zip(sub_folder, zipf, base_dir)

    def _should_exclude(self, path: Path) -> bool:
        """判断是否应该排除文件/目录"""
        # 排除隐藏文件和目录
        if any(part.startswith('.') and part != '.' and part != '..'
               for part in path.parts):
            return True

        # 排除特定文件类型
        exclude_extensions = ['.pyc', '.pyo', '.pyd', '.log', '.tmp', '.bak']
        if path.suffix.lower() in exclude_extensions:
            return True

        # 排除特定目录
        exclude_dirs = ['__pycache__', '.git', '.idea', '.vscode', 'node_modules', 'dist', 'build']
        if any(dir_name in path.parts for dir_name in exclude_dirs):
            return True

        # 排除构建输出目录自身
        if self.output_dir in path.parents:
            return True

        # 排除 macOS 的 DS_Store 文件
        if path.name == '.DS_Store':
            return True

        return False

    def build(self) -> Optional[Path]:
        """构建插件 ZIP 包"""
        self.validate()

        # 创建临时构建目录
        temp_build_dir = self.output_dir / f"_{self.plugin_name}_temp"
        FolderStream(temp_build_dir).create()

        try:
            print(f"🔧 开始构建插件: {self.plugin_name}")

            dep_map = self._resolve_dependencies()
            if dep_map:
                self._copy_dependencies(temp_build_dir, dep_map)

            # 复制文件到临时目录
            self._copy_plugin_files(temp_build_dir)

            # 创建 ZIP 文件
            zip_filename = f"{self.plugin_name}.zip"
            zip_path = self.output_dir / zip_filename
            self._create_zip_archive(temp_build_dir, zip_path)

            print(f"✅ 插件构建完成: {zip_path}")
            return zip_path
        finally:
            # 清理临时目录
            shutil.rmtree(temp_build_dir, ignore_errors=True)