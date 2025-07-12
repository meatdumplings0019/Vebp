class CommandMapper:
    _builtin_mappings = {
        "run": "python"
    }

    _plugin_mappings = {}

    @classmethod
    def register_mapping(cls, command, replacement):
        cls._plugin_mappings[command] = replacement

    @classmethod
    def resolve_command(cls, command_str):
        parts = command_str.strip().split()
        if not parts:
            return command_str

        command_head = parts[0]
        resolved = cls._plugin_mappings.get(
            command_head,
            cls._builtin_mappings.get(command_head, command_head)
        )

        return [resolved] + parts[1:]

    @classmethod
    def get_available_commands(cls):
        """📋 获取所有可用命令映射"""
        return {
            **cls._builtin_mappings,
            **cls._plugin_mappings
        }