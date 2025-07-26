import curses
from collections.abc import Callable


class InvalidChoiceError(Exception):
    """
    Raised when the option taken is invalid.
    """


def get_number_input(
    stdscr: curses.window, validation: Callable[[str], bool]
) -> int:
    while True:
        key = stdscr.getkey()
        if validation(key):
            return int(key)
        stdscr.addstr("Invalid input. Try again.  ")
        stdscr.refresh()
