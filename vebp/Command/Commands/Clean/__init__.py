from vebp.Builder.Builder import Builder


class CommandClean:
    @staticmethod
    def handle():
        Builder.clean()