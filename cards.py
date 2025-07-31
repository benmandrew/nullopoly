from enum import Enum


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

    def pretty(self) -> str:
        return self.name.replace("_", " ").title()


RENT_CARD_COLOURS: dict[ActionType, list[PropertyColour]] = {
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


def is_rent_action(action: ActionType) -> bool:
    return action in RENT_CARD_COLOURS


type Card = "ActionCard | PropertyCard | MoneyCard"


class PropertyCard:
    def __init__(self, name: str, value: int, colour: PropertyColour) -> None:
        self.name = name
        self.value = value
        self.colour = colour

    def pretty(self) -> str:
        colour_str = self.colour.name.replace("_", " ").title()
        lines = [self.name, colour_str, f"£{self.value}"]
        width = max(len(line) for line in lines) + 4
        top = f"┌{'─' * (width - 2)}┐"
        bottom = f"└{'─' * (width - 2)}┘"
        content = "\n".join(f"│ {line:<{width - 4}} │" for line in lines)
        return f"{top}\n{content}\n{bottom}"

    def __str__(self) -> str:
        return f"Property({self.name}, £{self.value}, {self.colour})"

    def __repr__(self) -> str:
        return f"Property({self.name}, £{self.value}, {self.colour})"


class ActionCard:
    def __init__(self, name: str, value: int, action: ActionType) -> None:
        self.name = name
        self.value = value
        self.action = action

    def pretty(self) -> str:
        action_str = self.action.pretty()
        if is_rent_action(self.action):
            rent, colours = action_str.split(" ", 1)
            lines = [rent, colours, f"£{self.value}"]
        else:
            lines = [action_str, "", f"£{self.value}"]
        width = max(len(line) for line in lines) + 4
        top = f"┌{'─' * (width - 2)}┐"
        bottom = f"└{'─' * (width - 2)}┘"
        content = "\n".join(f"│ {line:<{width - 4}} │" for line in lines)
        return f"{top}\n{content}\n{bottom}"

    def __str__(self) -> str:
        return f"Action({self.name}, £{self.value})"

    def __repr__(self) -> str:
        return self.__str__()


class MoneyCard:
    def __init__(self, value: int) -> None:
        self.value = value

    def pretty(self) -> str:
        lines = ["Money", "", f"£{self.value}"]
        width = max(len(line) for line in lines) + 4
        top = f"┌{'─' * (width - 2)}┐"
        bottom = f"└{'─' * (width - 2)}┘"
        content = "\n".join(f"│ {line:<{width - 4}} │" for line in lines)
        return f"{top}\n{content}\n{bottom}"

    def __str__(self) -> str:
        return f"Money(£{self.value})"

    def __repr__(self) -> str:
        return f"Money(£{self.value})"


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
