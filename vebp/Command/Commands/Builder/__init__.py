import sys
from pathlib import Path
from vebp.Builder.Builder import Builder


class CommandBuild:
    @staticmethod
    def handle(args) -> None:
        try:
            builder = Builder.from_package()

            if not builder:
                print("🔍 未找到配置文件，创建新构建器...")
                builder = Builder()

            name = getattr(args, 'name', None)
            if name:
                print(f"📛 设置项目名称: {name}")
                builder._name = name

            src = getattr(args, 'src', None)
            if src:
                print(f"📜 设置脚本路径: {src}")
                builder.set_script(src)

            icon = getattr(args, 'icon', None)
            if icon:
                print(f"🖼️ 设置图标: {icon}")
                builder._icon = Path(icon)

            console = getattr(args, 'console', False)
            if console:
                print("🖥️ 显示控制台: 是")
                builder.set_console(True)

            one_dir = getattr(args, 'onedir', False)
            if one_dir:
                print("📁 打包模式: 目录模式")
                builder.set_onefile(False)
            elif builder.onefile is None:
                print("📦 打包模式: 单文件模式")
                builder.set_onefile(True)

            assets = getattr(args, 'asset', [])
            if assets:
                print("📦 处理外部资源...")
                assets_by_target = {}

                for asset_spec in assets:
                    parts = asset_spec.split(';', 1)
                    source = parts[0].strip()
                    target = parts[1].strip() if len(parts) > 1 else ""

                    assets_by_target.setdefault(target, []).append(source)

                for target, sources in assets_by_target.items():
                    print(f"  ➕ 添加资源: {sources} -> {target}")
                    builder.add_assets(sources, target)

            in_assets = getattr(args, 'in_asset', [])
            if in_assets:
                print("📦 处理内部资源...")
                in_assets_by_target = {}

                for in_asset_spec in in_assets:
                    parts = in_asset_spec.split(';', 1)
                    source = parts[0].strip()
                    target = parts[1].strip() if len(parts) > 1 else ""

                    in_assets_by_target.setdefault(target, []).append(source)

                for target, sources in in_assets_by_target.items():
                    print(f"  ➕ 添加内部资源: {sources} -> {target}")
                    builder.add_in_assets(sources, target)

            print("🔨 开始构建...")
            success = builder.build()
        except Exception as e:
            print(f"\n❌ 构建错误: {str(e)}", file=sys.stderr)
            sys.exit(2)

        if success:
            print("✅ 构建成功!")
            sys.exit(0)
        else:
            print("\n❌ 操作失败! 请检查错误信息", file=sys.stderr)
            sys.exit(1)