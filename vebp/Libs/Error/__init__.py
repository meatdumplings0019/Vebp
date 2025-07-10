import traceback


def get_traceback(e: Exception):
    return traceback.extract_tb(e.__traceback__)[-1]