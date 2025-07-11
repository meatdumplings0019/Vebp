from vebp.version import __version__

class CommandVersion:
    @staticmethod
    def handle():
        print(CommandVersion.get_value())

    @staticmethod
    def get_value():
        return f"Vebp {__version__}"