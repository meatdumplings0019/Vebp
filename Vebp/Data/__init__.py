from typing import Any

from Vebp.Libs.File import FileStream
from Vebp.Libs.File.path import MPath_
from Vebp.fstr import format_string


class VebpData:
    FILENAME = "vebp-config.json"

    PROP_DICT = {}

    def __init__(self, path) -> None:
        self.file = self._read(path)

    def _read(self, path) -> dict[str, Any]:
        f = FileStream(path)
        if not f.is_name(self.FILENAME):
            raise FileNotFoundError(f"File {path} not found")

        try:
            return f.read_json()
        except FileNotFoundError:
            return self.default()

    @classmethod
    def generate_default(cls) -> dict:
        generate = {}

        for k, v in cls.PROP_DICT.items():
            if v.get("generate", False):
                generate[k] = format_string(v["default"])

        return generate

    @classmethod
    def create(cls, path, overwrite=False) -> bool:
        file_path = FileStream(MPath_.cwd / path / cls.FILENAME)

        if file_path.exists and not overwrite:
            print(f"{cls.FILENAME} 已存在。使用 --force 覆盖。")
            return False

        file_path.create()
        config = cls.generate_default()
        file_path.write_json(config)

        print(f"成功创建 {cls.FILENAME}!")

        return True

    def get(self, key, default=None, *keys) -> Any:
        try:
            if not keys:
                return self.file.get(key, default)

            value = self.file.get(key, {})

            for k in keys[1:-1]:
                value = value.get(k, {})

            return value.get(keys[-1], default)
        except Exception as e:
            print(f"🔥{e}")
            return None

    @staticmethod
    def default() -> dict[str, Any]:
        return {}