import re


def get_fs(s: str, context: dict) -> str:
    """
    解析自定义 f 字符串格式：
    - $name 替换为字典中的值
    - $$ 转义为单个 $
    - 未识别的占位符保留原样

    Args:
        s: 包含占位符的原始字符串
        context: 包含占位符键值对的字典

    Returns:
        解析后的字符串
    """
    # 正则匹配：$$ 或 $ + 合法标识符 (字母/下划线开头)
    pattern = r'(\$\$)|(\$[a-zA-Z_][a-zA-Z0-9_]*)'

    def replace(match):
        # 处理 $$ 转义情况
        if match.group(1):
            return '$'

        # 提取占位符名称 (去掉开头的$)
        placeholder = match.group(2)[1:]

        # 替换已知占位符，未知保留原样
        return str(context.get(placeholder, match.group(2)))

    return re.sub(pattern, replace, s)