import argparse
import shlex


class ArgsUtil:
    @staticmethod
    def parse_input_args(input_str, parser: argparse.ArgumentParser):
        try:
            if not input_str.strip():
                return parser.parse_args([])

            tokens = shlex.split(input_str)
            return parser.parse_args(tokens)

        except SystemExit:
            return None
        except Exception as e:
            print(f"参数解析错误: {str(e)}")
            return None