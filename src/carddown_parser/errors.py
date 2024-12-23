import sys
import traceback
from .config.config import ENABLE_DEBUG


def show_exception_msg(e: Exception):
    print(type(e).__name__ + ": " + str(e))


def show_warning_msg(msg: str):
    print("Warning: " + msg)


def debug_print(*msg: str):
    if ENABLE_DEBUG:
        print(*msg)


def try_read_file(filepath: str, error_msg: str = None, exit=True) -> str:
    try:
        try:
            with open(filepath, 'r') as file:
                data = file.read()
                return data
        except UnicodeDecodeError as e:
            with open(filepath, 'r', encoding="windows-1252") as file:
                data = file.read()
                return data

    except OSError as e:
        if not error_msg:
            error_msg = f"Error: the file '{filepath}' doesn't exist"
        print(error_msg)
        if ENABLE_DEBUG:
            print(f"{type(e)}, {e}")
            traceback.print_exc()
        if exit:
            sys.exit()

    except Exception as e:
        print(f"Error: Something went wrong opening the file '{filepath}':")
        print(f"{type(e)}, {e}")
        if ENABLE_DEBUG:
            print(f"{type(e)}, {e}")
            traceback.print_exc()
        if exit:
            sys.exit()


class MarkdownSyntaxError(Exception):
    pass


class CardSyntaxError(Exception):
    pass
