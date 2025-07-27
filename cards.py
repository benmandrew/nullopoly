from abc import ABC, abstractmethod
from enum import Enum


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

    @abstractmethod
    def pretty(self) -> str:
        pass


class PropertyColour(Enum):
    BROWN = "brown"
    LIGHT_BLUE = "light blue"
    PINK = "pink"
    ORANGE = "orange"
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    DARK_BLUE = "dark blue"
    RAILROAD = "railroad"
    UTILITY = "utility"

    def pretty(self) -> str:
        return self.name.replace("_", " ").title()


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


RENT_CARD_COLOURS = {
    ActionType.RENT_BROWN_LIGHT_BLUE: [
        PropertyColour.BROWN,
        PropertyColour.LIGHT_BLUE,
    ],
    ActionType.RENT_PINK_ORANGE: [PropertyColour.PINK, PropertyColour.ORANGE],
    ActionType.RENT_RED_YELLOW: [PropertyColour.RED, PropertyColour.YELLOW],
    ActionType.RENT_GREEN_DARK_BLUE: [
        PropertyColour.GREEN,
        PropertyColour.DARK_BLUE,
    ],
    ActionType.RENT_RAILROAD_UTILITY: [
        PropertyColour.RAILROAD,
        PropertyColour.UTILITY,
    ],
    ActionType.RENT_WILD: list(PropertyColour),
}


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

    def pretty(self) -> str:
        colour_str = self._colour.name.replace("_", " ").title()
        lines = [self._name, colour_str, f"£{self._value}"]
        width = max(len(line) for line in lines) + 4
        top = f"┌{'─' * (width - 2)}┐"
        bottom = f"└{'─' * (width - 2)}┘"
        content = "\n".join(f"│ {line:<{width - 4}} │" for line in lines)
        return f"{top}\n{content}\n{bottom}"

    def __str__(self) -> str:
        return f"Property({self._name}, £{self._value}, {self._colour})"

    def __repr__(self) -> str:
        return f"Property({self._name}, £{self._value}, {self._colour})"


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

    def pretty(self) -> str:
        action_str = self._action.name.replace("_", " ").title()
        lines = [action_str, "", f"£{self._value}"]
        width = max(len(line) for line in lines) + 4
        top = f"┌{'─' * (width - 2)}┐"
        bottom = f"└{'─' * (width - 2)}┘"
        content = "\n".join(f"│ {line:<{width - 4}} │" for line in lines)
        return f"{top}\n{content}\n{bottom}"

    def __str__(self) -> str:
        return f"Action({self._name}, £{self._value})"

    def __repr__(self) -> str:
        return self.__str__()


class MoneyCard(Card):
    def __init__(self, value: int):
        self._value = value

    def name(self) -> str:
        return f"${self._value}M"

    def value(self) -> int:
        return self._value

    def card_type(self) -> str:
        return "money"

    def pretty(self) -> str:
        lines = ["Money", "", f"£{self._value}"]
        width = max(len(line) for line in lines) + 4
        top = f"┌{'─' * (width - 2)}┐"
        bottom = f"└{'─' * (width - 2)}┘"
        content = "\n".join(f"│ {line:<{width - 4}} │" for line in lines)
        return f"{top}\n{content}\n{bottom}"

    def __str__(self) -> str:
        return f"Money(£{self._value})"

    def __repr__(self) -> str:
        return f"Money(£{self._value})"


def fmt_cards_side_by_side(cards: list[Card]) -> list[str]:
    card_lines = [card.pretty().split("\n") for card in cards]
    for i, c in enumerate(card_lines):
        c.insert(0, f"{i + 1}.")
    max_height = max(len(lines) for lines in card_lines)
    for i, lines in enumerate(card_lines):
        card_width = max(len(line) for line in lines)
        # Pad each line to visible card width
        card_lines[i] = [
            line + " " * (card_width - len(line)) for line in lines
        ]
        while len(card_lines[i]) < max_height:
            card_lines[i].append(" " * card_width)
    return [
        "".join(card_lines[i][line_idx] for i in range(len(cards)))
        for line_idx in range(max_height)
    ]
