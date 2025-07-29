import random
from typing import cast

import cards
import parse_deck
import player
import window


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
        self.win.turn_over(self.current_player().name)

    def get_player(self, name: str) -> player.Player | None:
        for p in self.players:
            if p.name == name:
                return p
        return None

    def add_card_to_deck(self, card: cards.Card) -> None:
        self.deck.append(card)

    def draw(self, n_cards_played: int) -> None:
        """
        Draw the current game state.
        """
        self.win.draw(self.current_player(), self.players, n_cards_played)

    def draw_card(self) -> cards.Card:
        """Draw a card from the deck."""
        if not self.deck:
            self.deck = self.discard_pile
            self.discard_pile = []
            if not self.deck:
                raise RuntimeError("No cards left to draw.")
            random.shuffle(self.deck)
        return self.deck.pop()

    def discard_card(self, card: cards.Card) -> None:
        self.discard_pile.append(card)

    def play_deal_breaker(self, p: player.Player) -> None:
        target = self.choose_player_target(exclude=p)
        if not target.has_complete_property_set():
            self.win.draw_log(f"{target.name} has no complete sets to take!")
            raise window.InvalidChoiceError()
        property_set = self.choose_full_set_target(target)
        for card in list(property_set.cards):
            p.add_property(card)
            target.remove_property(card)
        self.win.draw_log(
            f"{p.name} stole the {property_set.colour.pretty()} set from {target.name}!"  # noqa: E501 pylint: disable=line-too-long
        )

    def play_sly_deal(self, p: player.Player) -> None:
        target = self.choose_player_target(exclude=p)
        if not target.has_properties(without_full_sets=True):
            self.win.draw_log(f"{target.name} has no properties to take!")
            raise window.InvalidChoiceError()
        self.win.hand.draw_target_property_dialog(
            target, without_full_sets=True
        )
        property_card = self.choose_property_target(
            target, without_full_sets=True
        )
        p.add_property(property_card)
        target.remove_property(property_card)
        self.win.draw_log(
            f"{p.name} took {property_card.name} from {target.name}"
        )

    def play_forced_deal(self, p: player.Player) -> None:
        if not p.has_properties(without_full_sets=True):
            self.win.draw_log(f"{p.name} has no properties to swap!")
            raise window.InvalidChoiceError()
        target = self.choose_player_target(exclude=p)
        if not target.has_properties(without_full_sets=True):
            self.win.draw_log(f"{target.name} has no properties to swap!")
            raise window.InvalidChoiceError()
        target_card = self.choose_property_target(
            target, without_full_sets=True
        )
        source_card = self.choose_property_target(p)
        p.add_property(target_card)
        target.remove_property(target_card)
        target.add_property(source_card)
        p.remove_property(source_card)
        self.win.draw_log(
            f"{p.name} forced {target.name} to swap {target_card.name} with {source_card.name}"  # noqa: E501 pylint: disable=line-too-long
        )

    def get_rent_amount(self, card: cards.ActionCard, p: player.Player) -> int:
        assert (
            card.action in cards.RENT_CARD_COLOURS
        ), f"Not a rent card: {card.action}"
        colour_options = cards.RENT_CARD_COLOURS[card.action]
        owned_colours_with_rents = []
        for c in colour_options:
            if p.properties[c].cards:
                owned_colours_with_rents.append((c, p.properties[c].rent()))
        if not owned_colours_with_rents:
            self.win.draw_log(
                "You do not own any properties of the required colours"
            )
            raise window.InvalidChoiceError()
        if len(owned_colours_with_rents) == 1:
            return owned_colours_with_rents[0][1]

        self.win.hand.draw_rent_colour_choice(owned_colours_with_rents)
        choice = self.win.get_number_input(1, len(owned_colours_with_rents))
        return owned_colours_with_rents[choice - 1][1]

    def play_rent_card(self, card: cards.ActionCard, p: player.Player) -> None:
        rent_amount = self.get_rent_amount(card, p)
        if card.action is cards.ActionType.RENT_WILD:
            target = self.choose_player_target(exclude=p)
            self.transfer_payment(target, p, rent_amount)
            self.win.draw_log(
                f"{p.name} charged {target.name} £{rent_amount} in rent"
            )
        else:
            for target in self.players:
                if target != p:
                    self.transfer_payment(target, p, rent_amount)
            self.win.draw_log(
                f"{p.name} charged everybody £{rent_amount} in rent"
            )

    def play_birthday_card(self, p: player.Player) -> None:
        for target in self.players:
            if target != p:
                self.transfer_payment(target, p, 2)
        self.win.draw_log(
            f"{p.name} collected £2 from each player for their birthday"
        )

    def play_debt_collector_card(self, p: player.Player) -> None:
        target = self.choose_player_target(exclude=p)
        self.win.draw_log(f"{p.name} collected £5 debt from {target.name}")
        self.transfer_payment(target, p, 5)

    def play_pass_go(self, p: player.Player) -> None:
        self.win.draw_log(f"{p.name} passed GO and picked up two cards")
        self.deal_to_player(p, 2)

    def play_action_card(
        self, card: cards.ActionCard, p: player.Player
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
            raise NotImplementedError(
                f"Action card type '{card.action}' not implemented"
            )
        self.discard_card(card)

    def play_card(self, card: cards.Card, p: player.Player) -> None:
        if isinstance(card, cards.PropertyCard):
            p.add_property(card)
        elif isinstance(card, cards.MoneyCard):
            p.add_to_bank(card)
        elif isinstance(card, cards.ActionCard):
            self.win.hand.draw_action_dialog()
            choice = self.win.get_number_input(1, 2)
            if choice == 1:
                self.play_action_card(card, p)
            elif choice == 2:
                p.add_to_bank(card)
            else:
                raise ValueError("Invalid choice for action card")
        else:
            raise ValueError(f"Unknown card type: {type(card)}")

    def choose_player_target(
        self, exclude: player.Player | None = None
    ) -> player.Player:
        without_exclude = [p for p in self.players if p != exclude]
        if len(without_exclude) == 1:
            return without_exclude[0]
        self.win.hand.draw_target_player_dialog(self.players, exclude)
        choice = self.win.get_number_input(1, len(without_exclude))
        return without_exclude[choice - 1]

    def choose_property_target(
        self, target: player.Player, without_full_sets: bool = False
    ) -> cards.PropertyCard:
        self.win.hand.draw_target_property_dialog(
            target, without_full_sets=without_full_sets
        )
        choice = self.win.get_number_input(
            1, target.n_properties(without_full_sets=without_full_sets)
        )
        return target.properties_to_list(without_full_sets=without_full_sets)[
            choice - 1
        ]

    def choose_full_set_target(
        self, target: player.Player
    ) -> player.PropertySet:
        full_sets: list[player.PropertySet] = []
        for prop in target.properties.values():
            if prop.is_complete():
                full_sets.append(prop)
        if not full_sets:
            raise window.InvalidChoiceError(
                "Target player does not have a full set of properties"
            )
        self.win.hand.draw_target_full_set_dialog(target)
        choice = self.win.get_number_input(1, len(full_sets))
        return full_sets[choice - 1]

    def get_payment(
        self, p: player.Player, amount: int
    ) -> tuple[
        list[cards.MoneyCard | cards.ActionCard], list[cards.PropertyCard]
    ]:
        charged_cards, remaining = p.charge_money_payment(amount)
        charged_properties = self.charge_properties(p, remaining)
        return charged_cards, charged_properties

    def transfer_payment(
        self, from_player: player.Player, to_player: player.Player, amount: int
    ) -> None:
        money, properties = self.get_payment(from_player, amount)
        to_player.add_payment(cast(list[cards.Card], money + properties))

    def charge_properties(
        self, p: player.Player, amount: int
    ) -> list[cards.PropertyCard]:
        charged_properties = []
        while amount > 0 and p.properties_to_list():
            property_card = self.choose_property_target(p)
            p.remove_property(property_card)
            amount -= property_card.value
            charged_properties.append(property_card)
        return charged_properties

    def get_card_choice(self, p: player.Player) -> cards.Card:
        choice = self.win.get_number_input(1, len(p.hand))
        return p.get_card_in_hand(choice - 1)

    def check_win(self) -> bool:
        """
        Check if any player has won the game.
        """
        has_won = [p for p in self.players if p.has_won()]
        if not has_won:
            return False
        if len(has_won) == 1:
            winner = has_won[0]
            self.win.hand.draw_action_dialog()
            self.win.draw_log(f"{winner.name} has won the game!")
            self.win.refresh()
            return True
        winner_names = ", ".join(p.name for p in has_won)
        self.win.draw_log(f"{winner_names} have drawn!")
        return True
