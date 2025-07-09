from Vebp.Builder.Plugin import PluginBuilder
from Vebp.Plugin.globals import get_plugin_manager


class CommandPlugin:
    @staticmethod
    def handle(args) -> None:
        print("\n🧩 PluginConfig Tool")

        if args.list:
            print("\n📋 已加载插件列表:")
            plugins = get_plugin_manager().list_plugins()

            if not plugins:
                print("  没有加载任何插件")
                return

            for pn in plugins:
                p = get_plugin_manager().get_plugin(pn)
                print(f"  🔌 {p.namespace}: 作者: {p.author} 是否开启:  {'✅' if p.action else '❌'}")
            return

        if args.build:
            if not hasattr(args, "path"):
                print("❌ 错误: 缺少 --path 参数")
                return

            print(f"🔨 构建插件: {args.path}")
            pb = PluginBuilder(args.path)
            pb.build()
            print("✅ 插件构建完成!")
            return

        if args.reload:
            get_plugin_manager().load_plugins()
            print("🧩 加载成功")
            return