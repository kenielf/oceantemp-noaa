# <!--- Imports --->
from os import getenv
from sys import exit, platform, stderr, stdout
from typing import NoReturn

from colorama import Fore, just_fix_windows_console

# <!--- Constants --->
# NOTE: Since this program requires outputting color to the terminal, we try
# to make the colors available on Windows with colorama. However, I do not
# guarantee that this will work since I do not have access to a machine
# running Windows.
if platform.startswith("win") or platform.startswith("cygwin"):
    just_fix_windows_console()


# Enable debug messages with environment variables
DEBUG: bool = True if getenv("DEBUG") == "1" else False


# <!--- Functions --->
def set_debug(enabled: bool) -> None:
    """
    Enables/disables debug messages for the whole application
    """
    global DEBUG
    # Intentionally overwrite global variable
    DEBUG = enabled  # pyright: ignore[reportConstantRedefinition]


def write_message(
    contents: str,
    label: str = "",
    label_color: str | None = None,
    use_stderr: bool = False,
) -> None:
    """
    Writes a message to stdout or stderr.

    Optionally, the message can be decorated by using the label and label_color
    variables.
    """
    print(
        f"[{label_color}{label}{Fore.RESET}] " if label else "",
        contents,
        sep="",
        file=stderr if use_stderr else stdout,
    )


# Log order: DEBUG -> INFO -> WARN -> ERROR
def debug(message: str, force: bool = False) -> None:
    """
    Wrapper for 'write_message()' to be used for debug messages.
    """
    if DEBUG or force:
        write_message(message, label="DEBUG", label_color=Fore.CYAN)


def info(message: str) -> None:
    """
    Wrapper for 'write_message()' to be used for info messages.
    """
    write_message(message, label="INFO", label_color=Fore.BLUE)


def warn(message: str) -> None:
    """
    Wrapper for 'write_message()' to be used for warning messages.
    """
    write_message(message, label="WARNING", label_color=Fore.YELLOW, use_stderr=True)


def error(message: str) -> None:
    """
    Wrapper for 'write_message()' to be used for error messages.
    """
    write_message(message, label="ERROR", label_color=Fore.RED, use_stderr=True)


def fatal_error(message: str, exit_code: int = 1) -> NoReturn:
    """
    Wrapper for 'error()' with explicit fatal exits
    This function exists mostly due to pyright sheganigans...
    """
    error(message)
    exit(exit_code)
