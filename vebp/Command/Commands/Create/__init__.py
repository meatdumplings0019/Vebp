class CommandCreate:
    @staticmethod
    def handle(args):
        name = getattr(args, 'name', None)

        if not name:
            return