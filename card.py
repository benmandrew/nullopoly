from enum import Enum
from abc import ABC, abstractmethod
import re


class Card(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def value(self) -> int:
        pass

    @abstractmethod
    def card_type(self) -> str:
        pass


class PropertyColour(Enum):
    BROWN = "brown"
    LIGHT_BLUE = "light_blue"
    PINK = "pink"
    ORANGE = "orange"
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    DARK_BLUE = "dark_blue"
    RAILROAD = "railroad"
    UTILITY = "utility"


PROPERTY_RENTS: dict[PropertyColour, list[int]] = {
    PropertyColour.BROWN: [1, 2],
    PropertyColour.LIGHT_BLUE: [1, 2, 3],
    PropertyColour.PINK: [1, 2, 4],
    PropertyColour.ORANGE: [1, 3, 5],
    PropertyColour.RED: [2, 3, 6],
    PropertyColour.YELLOW: [2, 4, 6],
    PropertyColour.GREEN: [2, 4, 7],
    PropertyColour.DARK_BLUE: [3, 8],
    PropertyColour.RAILROAD: [1, 2, 3, 4],
    PropertyColour.UTILITY: [1, 2],
}


class ActionType(Enum):
    DEAL_BREAKER = "deal_breaker"
    JUST_SAY_NO = "just_say_no"
    SLY_DEAL = "sly_deal"
    FORCED_DEAL = "forced_deal"
    DEBT_COLLECTOR = "debt_collector"
    ITS_MY_BIRTHDAY = "its_my_birthday"
    RENT_WILD = "rent_wild"
    RENT_BROWN_LIGHT_BLUE = "rent_brown_light_blue"
    RENT_PINK_ORANGE = "rent_pink_orange"
    RENT_RED_YELLOW = "rent_red_yellow"
    RENT_GREEN_DARK_BLUE = "rent_green_dark_blue"
    RENT_RAILROAD_UTILITY = "rent_railroad_utility"
    PASS_GO = "pass_go"


class PropertyCard(Card):
    def __init__(self, name: str, value: int, colour: PropertyColour):
        self._name = name
        self._value = value
        self._colour = colour

    def name(self) -> str:
        return self._name

    def value(self) -> int:
        return self._value

    def card_type(self) -> str:
        return "property"

    def colour(self) -> PropertyColour:
        return self._colour

    def __str__(self) -> str:
        colour_str = self._colour.name.replace("_", " ").title()
        lines = [self._name, colour_str, f"£{self._value}"]
        width = max(len(line) for line in lines) + 4
        top = f"┌{'─' * (width - 2)}┐"
        bottom = f"└{'─' * (width - 2)}┘"
        content = "\n".join(f"│ {line:<{width-4}} │" for line in lines)
        return f"{top}\n{content}\n{bottom}"


class ActionCard(Card):
    def __init__(self, name: str, value: int, action: ActionType):
        self._name = name
        self._value = value
        self._action = action

    def name(self) -> str:
        return self._name

    def value(self) -> int:
        return self._value

    def card_type(self) -> str:
        return "action"

    def action(self) -> ActionType:
        return self._action

    def colour_rent_wild(self, parts: list[str]) -> str:
        # Rainbow colours for "Wild"
        rainbow = [
            "\033[31m",  # Red
            "\033[33m",  # Yellow
            "\033[32m",  # Green
            "\033[36m",  # Cyan
            "\033[34m",  # Blue
            "\033[35m",  # Magenta
        ]
        wild_text = "Wild"
        coloured_wild = (
            "".join(
                f"{rainbow[i % len(rainbow)]}{c}"
                for i, c in enumerate(wild_text)
            )
            + RESET_COLOUR
            + ACTION_COLOUR
        )
        return f"{parts[0]} {coloured_wild}"

    def colour_rent_names(self, action_str: str) -> str:
        # Example input: "Rent Brown Light Blue" or "Rent Wild"
        parts = action_str.split()
        assert len(parts) >= 2, "Rent string must have at least two parts"
        if "Wild" in parts:
            return self.colour_rent_wild(parts)
        # Otherwise, colour property names as before
        property_names = []
        i = 1
        while i < len(parts):
            if i + 1 < len(parts):
                two_word = f"{parts[i]} {parts[i+1]}"
                if two_word in {"Light Blue", "Dark Blue"}:
                    property_names.append(two_word)
                    i += 2
                    continue
            property_names.append(parts[i])
            i += 1
        coloured = "/".join(
            colour_property_name(name) for name in property_names
        )
        return f"{parts[0]} {coloured}"

    def __str__(self) -> str:
        action_str = self._action.name.replace("_", " ").title()
        if self._action.name.startswith("RENT_"):
            action_str = self.colour_rent_names(action_str)
        lines = [action_str, f"£{self._value}"]
        width = max(len(strip_ansi(line)) for line in lines) + 4
        top = f"┌{'─' * (width - 2)}┐"
        bottom = f"└{'─' * (width - 2)}┘"
        content = "\n".join(f"│ {line:<{width-4}} │" for line in lines)
        return f"{top}\n{content}\n{bottom}"


class MoneyCard(Card):
    def __init__(self, value: int):
        self._value = value

    def name(self) -> str:
        return f"${self._value}M"

    def value(self) -> int:
        return self._value

    def card_type(self) -> str:
        return "money"

    def __str__(self) -> str:
        lines = ["Money", f"£{self._value}"]
        width = max(len(line) for line in lines) + 4
        top = f"┌{'─' * (width - 2)}┐"
        bottom = f"└{'─' * (width - 2)}┘"
        content = "\n".join(f"│ {line:<{width-4}} │" for line in lines)
        return f"{top}\n{content}\n{bottom}"


# ANSI colour codes for property colours
PROPERTY_COLOUR_CODES = {
    PropertyColour.BROWN: "\033[38;5;94m",  # Dark brown
    PropertyColour.LIGHT_BLUE: "\033[38;5;117m",  # Light blue
    PropertyColour.PINK: "\033[38;5;205m",  # Pink
    PropertyColour.ORANGE: "\033[38;5;208m",  # Orange
    PropertyColour.RED: "\033[31m",  # Red
    PropertyColour.YELLOW: "\033[33m",  # Yellow
    PropertyColour.GREEN: "\033[32m",  # Green
    PropertyColour.DARK_BLUE: "\033[34m",  # Blue
    PropertyColour.RAILROAD: "\033[38;5;240m",  # Grey
    PropertyColour.UTILITY: "\033[37m",  # White
}

ACTION_COLOUR = "\033[32m"  # Green for action cards
MONEY_COLOUR = "\033[93m"  # Bright yellow for money cards
RESET_COLOUR = "\033[0m"


def colour_card_str(card: Card) -> str:
    card_lines = str(card).split("\n")
    if isinstance(card, PropertyCard):
        colour_code = PROPERTY_COLOUR_CODES.get(card.colour())
        return "\n".join(
            f"{colour_code}{line}{RESET_COLOUR}" for line in card_lines
        )
    if isinstance(card, ActionCard):
        return "\n".join(
            f"{ACTION_COLOUR}{line}{RESET_COLOUR}" for line in card_lines
        )
    if isinstance(card, MoneyCard):
        return "\n".join(
            f"{MONEY_COLOUR}{line}{RESET_COLOUR}" for line in card_lines
        )
    return str(card)


def strip_ansi(s: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", s)


def fmt_cards_side_by_side(cards: list[Card]) -> str:
    card_lines = [colour_card_str(card).split("\n") for card in cards]
    max_height = max(len(lines) for lines in card_lines)
    for i, lines in enumerate(card_lines):
        # Calculate visible width, ignoring ANSI codes
        card_width = max(len(strip_ansi(line)) for line in lines)
        # Pad each line to visible card width
        card_lines[i] = [
            line + " " * (card_width - len(strip_ansi(line))) for line in lines
        ]
        while len(card_lines[i]) < max_height:
            card_lines[i].append(" " * card_width)
    output_lines = [
        "".join(card_lines[i][line_idx] for i in range(len(cards)))
        for line_idx in range(max_height)
    ]
    return "\n".join(output_lines)


def colour_property_name(name: str) -> str:
    # Map colour names to PropertyColour
    name_map = {
        "Brown": PropertyColour.BROWN,
        "Light Blue": PropertyColour.LIGHT_BLUE,
        "Pink": PropertyColour.PINK,
        "Orange": PropertyColour.ORANGE,
        "Red": PropertyColour.RED,
        "Yellow": PropertyColour.YELLOW,
        "Green": PropertyColour.GREEN,
        "Dark Blue": PropertyColour.DARK_BLUE,
        "Railroad": PropertyColour.RAILROAD,
        "Utility": PropertyColour.UTILITY,
    }
    colour = name_map.get(name)
    if colour:
        return f"{RESET_COLOUR}{PROPERTY_COLOUR_CODES[colour]}{name}{RESET_COLOUR}{ACTION_COLOUR}"
    return name
