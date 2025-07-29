import textwrap


def format_expect(s: str) -> str:
    return textwrap.dedent(s).strip("\n")


def strip_and_join(lines: list[str]) -> str:
    return "\n".join(line.strip() for line in lines).strip("\n")
