import re
import curses
from collections.abc import Callable


def strip_ansi(s: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", s)


def get_number_input(
    stdscr: curses.window, validation: Callable[[str], bool]
) -> int:
    while True:
        key = stdscr.getkey()
        if validation(key):
            return int(key)
        stdscr.addstr("Invalid input. Try again.  ")
        stdscr.refresh()
