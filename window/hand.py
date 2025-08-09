from __future__ import annotations

import curses
from typing import TYPE_CHECKING

import cards
from window import common

if TYPE_CHECKING:
    import queue

    import player

CARD_HEIGHT = 5


class Hand:

    def __init__(
        self,
        stdscr: curses.window,
        height: int,
        width: int,
        y: int,
        x: int,
    ) -> None:
        self.win = stdscr.subwin(height, width, y, x)

    def clear(self) -> None:
        self.win.clear()
        self.win.border(0, 0, 0, 0, 0, 0, 0, 0)

    def draw(
        self,
        p: player.Player,
        hand_len: int,
        played_card_idx: int,
    ) -> None:
        self.clear()
        self.win.addstr(1, 2, f"It's {p.name}'s turn", curses.A_BOLD)
        x = 2
        for i, card in enumerate(p.hand):
            self.win.addstr(2, x, f"{i + 1}.")
            x = self.draw_card(card, 3, x)
        self.win.addstr(
            9,
            2,
            f"{3 - played_card_idx} cards left to play this turn.",
        )
        self.win.addstr(
            10,
            2,
            f"Choose a card to play (1-{hand_len}): ",
        )
        self.win.refresh()

    def draw_card(self, card: cards.Card, y: int, x: int) -> int:
        """Draws a card in the hand window at the specified position.
        Returns the new x position after drawing the card.
        """
        if isinstance(card, cards.ActionCard):
            return self.draw_action_card(card, y, x)
        if isinstance(card, cards.PropertyCard):
            return self.draw_property_card(card, y, x)
        if isinstance(card, cards.MoneyCard):
            return self.draw_money_card(card, y, x)
        msg = f"Unknown card type: {type(card)}"
        raise TypeError(msg)

    def draw_box(self, y: int, x: int, height: int, width: int) -> None:
        self.win.addch(y, x, curses.ACS_ULCORNER)
        self.win.hline(y, x + 1, curses.ACS_HLINE, width - 2)
        self.win.addch(y, x + width - 1, curses.ACS_URCORNER)
        self.win.vline(y + 1, x, curses.ACS_VLINE, height - 2)
        self.win.vline(y + 1, x + width - 1, curses.ACS_VLINE, height - 2)
        self.win.addch(y + height - 1, x, curses.ACS_LLCORNER)
        self.win.hline(y + height - 1, x + 1, curses.ACS_HLINE, width - 2)
        self.win.addch(y + height - 1, x + width - 1, curses.ACS_LRCORNER)

    def draw_rent_wild_content(
        self,
        y: int,
        x: int,
        card: cards.ActionCard,
    ) -> None:
        assert (
            card.action == cards.ActionType.RENT_WILD
        ), "Action type must be rent wild"
        self.win.addstr(y, x, "Rent")
        self.win.addstr(
            y + 1,
            x,
            "W",
            curses.color_pair(common.COLOUR_MAP[cards.PropertyColour.RED]),
        )
        self.win.addstr(
            y + 1,
            x + 1,
            "i",
            curses.color_pair(common.COLOUR_MAP[cards.PropertyColour.GREEN]),
        )
        self.win.addstr(
            y + 1,
            x + 2,
            "l",
            curses.color_pair(common.COLOUR_MAP[cards.PropertyColour.YELLOW]),
        )
        self.win.addstr(
            y + 1,
            x + 3,
            "d",
            curses.color_pair(
                common.COLOUR_MAP[cards.PropertyColour.LIGHT_BLUE],
            ),
        )
        self.win.addstr(y + 2, x, f"£{card.value}")

    def draw_rent_content(self, y: int, x: int, card: cards.ActionCard) -> None:
        assert (
            card.action in cards.RENT_CARD_COLOURS
        ), "Action type must be rent"
        if card.action == cards.ActionType.RENT_WILD:
            self.draw_rent_wild_content(y, x, card)
            return
        colours = cards.RENT_CARD_COLOURS[card.action]
        assert len(colours) == 2, "Rent action must have two colours"
        self.win.addstr(y, x, "Rent")
        first = colours[0].pretty()
        self.win.addstr(
            y + 1,
            x,
            f"{first}",
            curses.color_pair(common.COLOUR_MAP[colours[0]]),
        )
        self.win.addstr(
            y + 1,
            x + len(first) + 1,
            f"{colours[1].pretty()}",
            curses.color_pair(common.COLOUR_MAP[colours[1]]),
        )
        self.win.addstr(y + 2, x, f"£{card.value}")

    def draw_action_card(self, card: cards.ActionCard, y: int, x: int) -> int:
        """Draws an action card in the hand window at the specified position.
        Returns the new x position after drawing the card.
        """
        action_str = card.action.pretty()
        if cards.is_rent_action(card.action):
            rent, colours = action_str.split(" ", 1)
            lines = [rent, colours, f"£{card.value}"]
        else:
            lines = [action_str, "", f"£{card.value}"]
        width = max(len(line) for line in lines) + 4
        self.draw_box(y, x, CARD_HEIGHT, width)
        if cards.is_rent_action(card.action):
            self.draw_rent_content(y + 1, x + 2, card)
        else:
            self.win.addstr(y + 1, x + 2, action_str)
            self.win.addstr(y + 3, x + 2, f"£{card.value}")
        return x + width + 1

    def draw_property_card(
        self,
        card: cards.PropertyCard,
        y: int,
        x: int,
    ) -> int:
        """Draws a property card in the hand window at the specified position.
        Returns the new x position after drawing the card.
        """
        colour_str = card.colour.pretty()
        lines = [card.name, colour_str, f"£{card.value}"]
        width = max(len(line) for line in lines) + 4
        self.draw_box(y, x, CARD_HEIGHT, width)
        self.win.addstr(y + 1, x + 2, card.name)
        self.win.addstr(
            y + 2,
            x + 2,
            colour_str,
            curses.color_pair(common.COLOUR_MAP[card.colour]),
        )
        self.win.addstr(y + 3, x + 2, f"£{card.value}")
        return x + width + 1

    def draw_money_card(self, card: cards.MoneyCard, y: int, x: int) -> int:
        """Draws a money card in the hand window at the specified position.
        Returns the new x position after drawing the card.
        """
        lines = ["Money", f"£{card.value}"]
        width = max(len(line) for line in lines) + 4
        self.draw_box(y, x, CARD_HEIGHT, width)
        self.win.addstr(y + 1, x + 2, "Money")
        self.win.addstr(y + 3, x + 2, f"£{card.value}")
        return x + width + 1

    def draw_action_dialog(self) -> None:
        self.clear()
        self.win.addstr(2, 2, "Choose an option:")
        self.win.addstr(3, 2, "1. Play action")
        self.win.addstr(4, 2, "2. Add to bank")
        self.win.refresh()

    def draw_target_player_dialog(
        self,
        players: list[player.Player],
        exclude: player.Player | None = None,
    ) -> None:
        self.clear()
        self.win.addstr(2, 2, "Choose a player to target:")
        idx = 0
        for p in players:
            if p == exclude:
                continue
            self.win.addstr(3 + idx, 2, f"{idx + 1}. {p.name}")
            idx += 1
        self.win.refresh()

    def draw_target_property_dialog(
        self,
        target: player.Player,
        without_full_sets: bool = False,
    ) -> None:
        self.clear()
        self.win.addstr(2, 2, f"Choose a property from {target.name}:")
        properties = target.properties_to_list(
            without_full_sets=without_full_sets,
        )
        for i, prop in enumerate(properties):
            prop_name = f"{prop.name} ({prop.colour.pretty()}) (£{prop.value})"
            self.win.addstr(3 + i, 2, f"{i + 1}. {prop_name}")
        self.win.refresh()

    def draw_target_full_set_dialog(self, target: player.Player) -> None:
        self.clear()
        self.win.addstr(2, 2, f"Choose a full property set from {target.name}:")
        full_sets = [
            colour
            for colour, properties in target.properties.items()
            if properties.is_complete()
        ]
        for idx, colour in enumerate(full_sets):
            self.win.addstr(
                3 + idx,
                2,
                f"{idx + 1}. {colour.pretty()}",
            )
        self.win.refresh()

    def draw_rent_colour_choice(
        self,
        colours: list[tuple[cards.PropertyColour, int]],
    ) -> None:
        self.clear()
        self.win.addstr(2, 2, "Choose a colour to charge rent on:")
        for idx, (colour, rent) in enumerate(colours):
            self.win.addstr(
                3 + idx,
                2,
                f"{idx + 1}. {colour.pretty()} (£{rent})",
            )
        self.win.refresh()

    def turn_over(
        self,
        input_queue: queue.Queue[str],
        next_player_name: str,
    ) -> None:
        self.clear()
        self.win.addstr(2, 2, f"Next player: {next_player_name}", curses.A_BOLD)
        self.win.addstr(3, 2, "Press Enter to start turn.")
        self.win.refresh()
        while True:
            key = input_queue.get()
            if common.is_enter_key(key):
                break

    def game_over(self, input_queue: queue.Queue[str]) -> None:
        self.clear()
        self.win.addstr(1, 2, "Game over!")
        self.win.addstr(2, 2, "Press Enter to close.")
        self.win.refresh()
        while True:
            key = input_queue.get()
            if common.is_enter_key(key):
                break
