from __future__ import annotations

import random
from typing import cast

import cards
import parse_deck
import player
from window import common


class WonError(Exception):
    """Raised when a player has won the game."""


class Game:
    def __init__(
        self,
        players: list[player.Player],
        deck: str | list[cards.Card],
        starting_cards: int = 5,
    ) -> None:
        self.players = players
        if isinstance(deck, str):
            self.deck: list[cards.Card] = parse_deck.from_json(deck)
        else:
            self.deck = deck
        self.starting_cards = starting_cards
        self.current_player_index: int = 0
        self.current_turn: int = 0
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
            self.players,
        )
        return self.players[self.current_player_index]

    def current_player(self) -> player.Player:
        return self.players[self.current_player_index]

    def end_turn(self) -> None:
        self.current_turn += 1
        finished_player = self.current_player()
        self.next_player()
        finished_player.inter.notify_turn_over(self.current_player().name)

    def get_player_by_name(self, name: str) -> player.Player:
        for p in self.players:
            if p.name == name:
                return p
        msg = f"Player '{name}' not found"
        raise ValueError(msg)

    def get_player_by_idx(self, idx: int) -> player.Player:
        for p in self.players:
            if p.index == idx:
                return p
        msg = f"Player with index {idx} not found"
        raise IndexError(msg)

    def add_card_to_deck(self, card: cards.Card) -> None:
        self.deck.append(card)

    def draw(self, n_cards_played: int) -> None:
        """Draw the current game state."""
        for p in self.players:
            if p == self.current_player():
                p.inter.notify_draw_my_turn(
                    self.current_player(),
                    self.players,
                    n_cards_played,
                )
            else:
                p.inter.notify_draw_other_turn(self.players)

    def draw_card(self) -> cards.Card:
        """Draw a card from the deck."""
        if not self.deck:
            self.deck = self.discard_pile
            self.discard_pile = []
            if not self.deck:
                msg = "No cards left to draw."
                raise RuntimeError(msg)
            random.shuffle(self.deck)
        return self.deck.pop()

    def discard_card(self, card: cards.Card) -> None:
        self.discard_pile.append(card)

    def play_deal_breaker(self, p: player.Player) -> None:
        target = p.choose_player_target(self.players)
        if not target.has_complete_property_set():
            p.inter.log(f"{target.name} has no complete sets to take!")
            raise common.InvalidChoiceError
        property_set = p.inter.choose_full_set_target(target)
        for card in list(property_set.cards):
            p.add_property(card)
            target.remove_property(card)
        self.log_all(
            f"{p.name} stole the {property_set.colour.pretty()} set from {target.name}!",  # noqa: E501 pylint: disable=line-too-long
        )

    def play_sly_deal(self, p: player.Player) -> None:
        target = p.choose_player_target(self.players)
        if not target.has_properties(without_full_sets=True):
            p.inter.log(f"{target.name} has no properties to take!")
            raise common.InvalidChoiceError
        property_card = p.inter.choose_property_target(
            target,
            without_full_sets=True,
        )
        p.add_property(property_card)
        target.remove_property(property_card)
        self.log_all(
            f"{p.name} took {property_card.name} from {target.name}",
        )

    def play_forced_deal(self, p: player.Player) -> None:
        if not p.has_properties(without_full_sets=True):
            p.inter.log(f"{p.name} has no properties to swap!")
            raise common.InvalidChoiceError
        target = p.choose_player_target(self.players)
        if not target.has_properties(without_full_sets=True):
            p.inter.log(f"{target.name} has no properties to swap!")
            raise common.InvalidChoiceError
        target_card = p.inter.choose_property_target(
            target,
            without_full_sets=True,
        )
        source_card = p.inter.choose_property_source(p)
        p.add_property(target_card)
        target.remove_property(target_card)
        target.add_property(source_card)
        p.remove_property(source_card)
        self.log_all(
            f"{p.name} forced {target.name} to swap {target_card.name} with {source_card.name}",  # noqa: E501 pylint: disable=line-too-long
        )

    def get_rent_colour_and_amount(
        self,
        card: cards.ActionCard,
        p: player.Player,
    ) -> tuple[cards.PropertyColour, int]:
        assert (
            card.action in cards.RENT_CARD_COLOURS
        ), f"Not a rent card: {card.action}"
        colour_options = cards.RENT_CARD_COLOURS[card.action]
        owned_colours_with_rents = p.owned_colours_with_rents(
            colour_options,
        )
        if not owned_colours_with_rents:
            p.inter.log(
                "You do not own any properties of the required colours",
            )
            raise common.InvalidChoiceError
        if len(owned_colours_with_rents) == 1:
            return owned_colours_with_rents[0]
        return p.inter.choose_rent_colour_and_amount(owned_colours_with_rents)

    def play_rent_card(self, card: cards.ActionCard, p: player.Player) -> None:
        rent_colour, rent_amount = self.get_rent_colour_and_amount(card, p)
        if card.action is cards.ActionType.RENT_WILD:
            target = p.choose_player_target(self.players)
            self.transfer_payment(target, p, rent_amount)
            self.log_all(
                f"{p.name} charged {target.name} £{rent_amount} in "
                f"{rent_colour.pretty()} rent",
            )
        else:
            for target in self.players:
                if target != p:
                    self.transfer_payment(target, p, rent_amount)
            self.log_all(
                f"{p.name} charged everybody £{rent_amount} in "
                f"{rent_colour.pretty()} rent",
            )

    def play_birthday_card(self, p: player.Player) -> None:
        for target in self.players:
            if target != p:
                self.transfer_payment(target, p, 2)
        self.log_all(
            f"{p.name} collected £2 from each player for their birthday",
        )

    def play_debt_collector_card(self, p: player.Player) -> None:
        target = p.choose_player_target(self.players)
        self.log_all(f"{p.name} collected £5 debt from {target.name}")
        self.transfer_payment(target, p, 5)

    def play_pass_go(self, p: player.Player) -> None:
        self.log_all(f"{p.name} passed GO and picked up two cards")
        self.deal_to_player(p, 2)

    def play_action_card(
        self,
        card: cards.ActionCard,
        p: player.Player,
    ) -> None:
        if card.action == cards.ActionType.DEAL_BREAKER:
            self.play_deal_breaker(p)
        elif card.action == cards.ActionType.SLY_DEAL:
            self.play_sly_deal(p)
        elif card.action == cards.ActionType.FORCED_DEAL:
            self.play_forced_deal(p)
        elif card.action in cards.RENT_CARD_COLOURS:
            self.play_rent_card(card, p)
        elif card.action == cards.ActionType.DEBT_COLLECTOR:
            self.play_debt_collector_card(p)
        elif card.action == cards.ActionType.ITS_MY_BIRTHDAY:
            self.play_birthday_card(p)
        elif card.action == cards.ActionType.PASS_GO:
            self.play_pass_go(p)
        else:
            msg = f"Action card type '{card.action}' not implemented"
            raise NotImplementedError(
                msg,
            )
        self.discard_card(card)

    def play_card(self, card: cards.Card, p: player.Player) -> None:
        if isinstance(card, cards.PropertyCard):
            p.add_property(card)
        elif isinstance(card, cards.MoneyCard):
            p.add_to_bank(card)
        elif isinstance(card, cards.ActionCard):
            # choice = self.choose_action_usage()
            choice = self.players[
                self.current_player_index
            ].inter.choose_action_usage()
            if choice == 1:
                self.play_action_card(card, p)
            elif choice == 2:
                p.add_to_bank(card)
            else:
                msg = "Invalid choice for action card"
                raise ValueError(msg)
        else:
            msg = f"Unknown card type: {type(card)}"
            raise TypeError(msg)

    def get_payment(
        self,
        p: player.Player,
        amount: int,
    ) -> tuple[
        list[cards.MoneyCard | cards.ActionCard],
        list[cards.PropertyCard],
    ]:
        charged_cards, remaining = p.charge_money_payment(amount)
        charged_properties = self.charge_properties(p, remaining)
        return charged_cards, charged_properties

    def transfer_payment(
        self,
        from_player: player.Player,
        to_player: player.Player,
        amount: int,
    ) -> None:
        money, properties = self.get_payment(from_player, amount)
        to_player.add_payment(cast("list[cards.Card]", money + properties))

    def charge_properties(
        self,
        p: player.Player,
        amount: int,
    ) -> list[cards.PropertyCard]:
        charged_properties = []
        while amount > 0 and p.properties_to_list():
            property_card = p.inter.choose_property_source(p)
            p.remove_property(property_card)
            amount -= property_card.value
            charged_properties.append(property_card)
        return charged_properties

    def check_win(self) -> bool:
        """Check if any player has won the game."""
        has_won = [p for p in self.players if p.has_won()]
        if not has_won:
            return False
        if len(has_won) == 1:
            winner = has_won[0]
            self.notify_game_over(f"{winner.name} has won the game!")
            return True
        winner_names = ", ".join(p.name for p in has_won)
        self.notify_game_over(f"{winner_names} have drawn!")
        return True

    def log_all(self, message: str) -> None:
        """Log a message to all players."""
        for p in self.players:
            p.inter.log(message)

    def notify_game_over(self, message: str) -> None:
        """Notify all players that the game is over."""
        for p in self.players:
            p.inter.notify_game_over()
        self.log_all(message)

    def choose_card_in_hand(self, p: player.Player) -> cards.Card:
        """Choose a card from the player's hand."""
        return p.inter.choose_card_in_hand(p)
