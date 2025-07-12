import argparse


class CommandHelp:
    @staticmethod
    def handle(parser: argparse.ArgumentParser):
        parser.print_help()