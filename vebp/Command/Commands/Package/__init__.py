class CommandPackage:
    @staticmethod
    def handle() -> None:
        print("📦 显示 package 配置详情...\n")

        print("📋 说明:")
        print("- 👉 使用 'vebp init' 创建配置文件")
        print("- 📝 编辑 vebp-package.json 添加自定义脚本到 'scripts' 部分")
        print("- 🚀 使用 'vebp dev <脚本名>' 执行自定义脚本")
        print("- 🔨 使用 'vebp build' 构建应用程序")