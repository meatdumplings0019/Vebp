from argparse import ArgumentParser

from colorama import Fore, Style


class Command(ArgumentParser):
    def error(self, message):
        print(f"{Fore.RED}{message}{Style.RESET_ALL}")