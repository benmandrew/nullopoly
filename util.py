import re


def strip_ansi(s: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", s)
