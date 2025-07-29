import curses
from typing import Callable

import cards


def int_range_validator(v_min: int, v_max: int) -> Callable[[str], bool]:
    """
    Returns a validation function that checks if a key is a digit
    and within the specified range (inclusive).
    """

    def validator(key: str) -> bool:
        return key.isdigit() and v_min <= int(key) <= v_max

    return validator


def is_enter_key(key: str) -> bool:
    """
    Returns True if the key is an Enter key (either '\n' or '\r').
    """
    return key in ("\n", "\r", chr(10), chr(13))


def init_colours() -> None:
    assert curses.has_colors(), "Terminal does not support colours"
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.BROWN],
        curses.COLOR_WHITE,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.LIGHT_BLUE],
        curses.COLOR_CYAN,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.PINK],
        curses.COLOR_MAGENTA,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.ORANGE],
        curses.COLOR_WHITE,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.RED],
        curses.COLOR_RED,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.YELLOW],
        curses.COLOR_YELLOW,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.GREEN],
        curses.COLOR_GREEN,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.DARK_BLUE],
        curses.COLOR_BLUE,
        curses.COLOR_BLACK,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.RAILROAD],
        curses.COLOR_BLACK,
        curses.COLOR_WHITE,
    )
    curses.init_pair(
        COLOUR_MAP[cards.PropertyColour.UTILITY],
        curses.COLOR_BLACK,
        curses.COLOR_YELLOW,
    )


class InvalidChoiceError(Exception):
    """
    Raised when the option taken is invalid.
    """


COLOUR_MAP = {
    cards.PropertyColour.BROWN: 1,
    cards.PropertyColour.LIGHT_BLUE: 2,
    cards.PropertyColour.PINK: 3,
    cards.PropertyColour.ORANGE: 4,
    cards.PropertyColour.RED: 5,
    cards.PropertyColour.YELLOW: 6,
    cards.PropertyColour.GREEN: 7,
    cards.PropertyColour.DARK_BLUE: 8,
    cards.PropertyColour.RAILROAD: 9,
    cards.PropertyColour.UTILITY: 10,
}
