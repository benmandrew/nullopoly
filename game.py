import random
from typing import cast

import cards
import parse_deck
import player
import util
import window


def _action_input_validation(key: str) -> bool:
    return key.isdigit() and 1 <= int(key) <= 2


class Game:
    def __init__(
        self,
        player_names: list[str],
        deck: str | list[cards.Card],
        win: window.Window,
        starting_cards: int = 5,
    ):
        self.players: list[player.Player] = [
            player.Player(name) for name in player_names
        ]
        if isinstance(deck, str):
            self.deck: list[cards.Card] = parse_deck.from_json(deck)
        else:
            self.deck = deck
        self.starting_cards = starting_cards
        self.win = win
        self.current_player_index: int = 0
        self.current_turn: int = 0
        self.game_over: bool = False
        self.discard_pile: list[cards.Card] = []

    def start(self) -> None:
        random.shuffle(self.deck)
        for p in self.players:
            self.deal_from_empty(p)

    def deal_from_empty(self, p: player.Player) -> None:
        assert len(p.hand) == 0, "Player hand is not empty"
        self.deal_to_player(p, self.starting_cards)

    def deal_to_player(self, p: player.Player, count: int) -> None:
        for _ in range(count):
            p.add_to_hand(self.draw_card())

    def next_player(self) -> player.Player:
        self.current_player_index = (self.current_player_index + 1) % len(
            self.players
        )
        return self.players[self.current_player_index]

    def current_player(self) -> player.Player:
        return self.players[self.current_player_index]

    def end_turn(self) -> None:
        self.current_turn += 1
        self.next_player()

    def get_player(self, name: str) -> player.Player | None:
        for p in self.players:
            if p.name == name:
                return p
        return None

    def add_card_to_deck(self, card: cards.Card) -> None:
        self.deck.append(card)

    def draw_card(self) -> cards.Card:
        if not self.deck:
            self.deck = self.discard_pile
            self.discard_pile = []
            if not self.deck:
                raise RuntimeError("No cards left to draw.")
            random.shuffle(self.deck)
        return self.deck.pop()

    def discard_card(self, card: cards.Card) -> None:
        self.discard_pile.append(card)

    def play_birthday_card(self, p: player.Player) -> None:
        for target in self.players:
            if target != p:
                money, properties = self.charge_payment(target, 2)
                p.add_payment(cast(list[cards.Card], money + properties))

    def play_debt_collector_card(self, p: player.Player) -> None:
        target = self.choose_player_target(exclude=p)
        money, properties = self.charge_payment(target, 5)
        p.add_payment(cast(list[cards.Card], money + properties))

    def play_pass_go(self, p: player.Player) -> None:
        self.deal_to_player(p, 2)

    def play_action_card(
        self, card: cards.ActionCard, p: player.Player
    ) -> None:
        if card.action() == cards.ActionType.DEAL_BREAKER:
            raise NotImplementedError()
        if card.action() == cards.ActionType.SLY_DEAL:
            raise NotImplementedError()
        if card.action() == cards.ActionType.FORCED_DEAL:
            raise NotImplementedError()
        if card.action().name.startswith("RENT"):
            raise NotImplementedError()
        if card.action() == cards.ActionType.DEBT_COLLECTOR:
            self.play_debt_collector_card(p)
        elif card.action() == cards.ActionType.ITS_MY_BIRTHDAY:
            self.play_birthday_card(p)
        elif card.action() == cards.ActionType.PASS_GO:
            self.play_pass_go(p)
        else:
            raise NotImplementedError(
                f"Action card type '{card.action()}' not implemented"
            )
        self.discard_card(card)

    def play_card(self, card: cards.Card, p: player.Player) -> None:
        if isinstance(card, cards.PropertyCard):
            p.add_property(card)
        elif isinstance(card, cards.MoneyCard):
            p.add_to_bank(card)
        elif isinstance(card, cards.ActionCard):
            self.win.print_action_dialog()
            choice = util.get_number_input(
                self.win.stdscr, _action_input_validation
            )
            if choice == 1:
                raise NotImplementedError("Action card play not implemented")
            if choice == 2:
                p.add_to_bank(card)
            else:
                raise ValueError("Invalid choice for action card")
        else:
            raise ValueError(f"Unknown card type: {type(card)}")

    def _player_input_validation(self, key: str) -> bool:
        return key.isdigit() and 1 <= int(key) <= len(self.players) - 1

    def choose_player_target(
        self, exclude: player.Player | None = None
    ) -> player.Player:
        self.win.print_target_player_dialog(self.players, exclude)
        without_exclude = [p for p in self.players if p != exclude]
        choice = util.get_number_input(
            self.win.stdscr, self._player_input_validation
        )
        return without_exclude[choice - 1]

    def choose_property_target(
        self, target: player.Player
    ) -> cards.PropertyCard:
        self.win.print_target_property_dialog(target)
        choice = util.get_number_input(
            self.win.stdscr, target.property_input_validation
        )
        return target.properties_to_list()[choice - 1]

    def charge_payment(
        self, p: player.Player, amount: int
    ) -> tuple[
        list[cards.MoneyCard | cards.ActionCard], list[cards.PropertyCard]
    ]:
        charged_cards, remaining = p.charge_money_payment(amount)
        charged_properties = self.charge_properties(p, remaining)
        return charged_cards, charged_properties

    def charge_properties(
        self, p: player.Player, amount: int
    ) -> list[cards.PropertyCard]:
        charged_properties = []
        while amount > 0 and p.properties_to_list():
            property_card = self.choose_property_target(p)
            p.remove_property(property_card)
            amount -= property_card.value()
            charged_properties.append(property_card)
        return charged_properties
