from __future__ import annotations

import copy
import itertools
import uuid
from typing import Any, cast

import cards
from interaction import dummy, interaction


class PropertySet:
    def __init__(
        self,
        colour: cards.PropertyColour,
        required_count: int,
    ) -> None:
        self.colour = colour
        self.required_count = required_count
        self.cards: list[cards.PropertyCard] = []

    def add(self, card: cards.PropertyCard) -> None:
        assert card.colour == self.colour, (
            f"Card colour {card.colour} does not match set colour"
            f" {self.colour}"
        )
        self.cards.append(card)

    def remove(self, card: cards.PropertyCard) -> None:
        assert card in self.cards, "Card not found in the property set"
        assert card.colour == self.colour, (
            f"Card colour {card.colour} does not match set colour"
            f" {self.colour}"
        )
        self.cards.remove(card)

    def is_complete(self) -> bool:
        return len(self.cards) >= self.required_count

    def count(self) -> int:
        return len(self.cards)

    def rent(self) -> int:
        if self.count() == 0:
            return 0
        return cards.PROPERTY_RENTS[self.colour][len(self.cards) - 1]

    def to_json(self) -> dict[str, Any]:
        return {
            "colour": self.colour.name,
            "required_count": self.required_count,
            "cards": [card.to_json() for card in self.cards],
        }

    @staticmethod
    def from_json(data: dict[str, Any]) -> PropertySet:
        colour = cards.PropertyColour[data["colour"]]
        required_count = data["required_count"]
        prop_set = PropertySet(colour, required_count)
        for card_data in data["cards"]:
            card = cards.PropertyCard.from_json(card_data)
            prop_set.add(card)
        return prop_set


class Player:

    def __init__(self, name: str, inter: interaction.Interaction) -> None:
        self.index = uuid.uuid4()
        self.name = name
        self.inter = inter
        self.hand: list[cards.Card] = []
        self.properties: dict[cards.PropertyColour, PropertySet] = (
            self.empty_property_sets()
        )
        self.bank: list[cards.MoneyCard | cards.ActionCard] = []

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return False
        return self.index == other.index

    def __hash__(self) -> int:
        return hash(self.index)

    @classmethod
    def empty_property_sets(cls) -> dict[cards.PropertyColour, PropertySet]:
        required_counts = {
            cards.PropertyColour.BROWN: 2,
            cards.PropertyColour.LIGHT_BLUE: 3,
            cards.PropertyColour.PINK: 3,
            cards.PropertyColour.ORANGE: 3,
            cards.PropertyColour.RED: 3,
            cards.PropertyColour.YELLOW: 3,
            cards.PropertyColour.GREEN: 3,
            cards.PropertyColour.DARK_BLUE: 2,
            cards.PropertyColour.RAILROAD: 4,
            cards.PropertyColour.UTILITY: 2,
        }
        return {
            colour: PropertySet(colour, count)
            for colour, count in required_counts.items()
        }

    def add_to_hand(self, card: cards.Card) -> None:
        self.hand.append(card)

    def add_property(self, property_card: cards.PropertyCard) -> None:
        self.properties[property_card.colour].add(property_card)

    def add_to_bank(self, card: cards.MoneyCard | cards.ActionCard) -> None:
        self.bank.append(card)

    def total_bank_value(self) -> int:
        return sum(card.value for card in self.bank)

    def properties_to_list(
        self,
        without_full_sets: bool = False,
    ) -> list[cards.PropertyCard]:
        result = []
        for property_set in self.properties.values():
            if without_full_sets and property_set.is_complete():
                continue
            result.extend(property_set.cards)
        return result

    def owned_colours_with_rents(
        self,
        colour_options: list[cards.PropertyColour],
    ) -> list[tuple[cards.PropertyColour, int]]:
        return [
            (c, self.properties[c].rent())
            for c in colour_options
            if self.properties[c].cards
        ]

    def get_card_in_hand(self, i: int) -> cards.Card:
        """Get a card from the player's hand by index."""
        assert 0 <= i < len(self.hand), "Index out of range for hand"
        return self.hand[i]

    def remove_card_from_hand(self, card: cards.Card) -> None:
        """Remove a card from the player's hand."""
        assert card in self.hand, "Card not found in hand"
        self.hand.remove(card)

    def add_payment(self, payment: list[cards.Card]) -> None:
        for card in payment:
            if isinstance(card, cards.PropertyCard):
                self.add_property(card)
            elif isinstance(card, (cards.MoneyCard, cards.ActionCard)):
                self.add_to_bank(card)
            else:
                msg = f"Unknown card type: {type(card)}"
                raise TypeError(msg)

    def remove_property(self, card: cards.PropertyCard) -> None:
        self.properties[card.colour].remove(card)

    def charge_money_payment(
        self,
        amount: int,
    ) -> tuple[list[cards.MoneyCard | cards.ActionCard], int]:
        """Find the optimal set of cards to minimize overpayment."""
        bank_cards = list(self.bank)
        n = len(bank_cards)
        best_combo = None
        best_total = None
        for r in range(n):
            for combo in itertools.combinations(bank_cards, r + 1):
                total = sum(card.value for card in combo)
                if total >= amount and (
                    best_total is None or total < best_total
                ):
                    best_total = total
                    best_combo = combo
        if best_combo is not None:
            for card in best_combo:
                self.bank.remove(card)
            return list(best_combo), 0
        total = sum(card.value for card in bank_cards)
        self.bank.clear()
        return bank_cards, max(0, amount - total)

    def has_won(self) -> bool:
        """Returns True if the player has at least three complete property
        sets.
        """
        complete_sets = sum(
            1 for prop_set in self.properties.values() if prop_set.is_complete()
        )
        return complete_sets >= 3

    def has_complete_property_set(self) -> bool:
        """Returns True if the player has at least one complete property set."""
        return any(
            prop_set.is_complete() for prop_set in self.properties.values()
        )

    def n_properties(self, without_full_sets: bool = False) -> int:
        """Returns the total number of properties the player has."""
        if without_full_sets:
            return sum(
                len(prop_set.cards)
                for prop_set in self.properties.values()
                if not prop_set.is_complete()
            )
        return sum(len(prop_set.cards) for prop_set in self.properties.values())

    def has_properties(self, without_full_sets: bool = False) -> bool:
        """Returns True if the player has any properties.
        If `without_full_sets` is True, it only counts properties
        that are not part of a complete set.
        """
        if without_full_sets:
            return any(
                len(prop_set.cards) > 0 and not prop_set.is_complete()
                for prop_set in self.properties.values()
            )
        return any(
            len(prop_set.cards) > 0 for prop_set in self.properties.values()
        )

    def fmt_hand(self) -> list[str]:
        return cards.fmt_cards_side_by_side(self.hand)

    def choose_player_target(
        self,
        players: list[Player],
    ) -> Player:
        """Choose a player from the list of players, excluding self."""
        players = [p for p in players if p != self]
        return self.inter.choose_player_target(players)

    def copy_visible(self) -> Player:
        """Create a copy of the player with only visible attributes."""
        new_player = Player(self.name, dummy.DummyInteraction())
        new_player.index = self.index
        new_player.hand = []
        new_player.properties = copy.deepcopy(self.properties)
        new_player.bank = list(self.bank)
        return new_player

    def to_json(self) -> dict[str, Any]:
        return {
            "index": str(self.index),
            "name": self.name,
            "hand": [card.to_json() for card in self.hand],
            "properties": {
                colour.name: prop_set.to_json()
                for colour, prop_set in self.properties.items()
            },
            "bank": [card.to_json() for card in self.bank],
        }

    @staticmethod
    def from_json(
        data: dict[str, Any],
        inter: interaction.Interaction,
    ) -> Player:
        player = Player(data["name"], inter)
        player.index = data["index"]
        player.hand = [cards.from_json(card_data) for card_data in data["hand"]]
        player.properties = {
            cards.PropertyColour[colour]: PropertySet.from_json(prop_set_data)
            for colour, prop_set_data in data["properties"].items()
        }
        player.bank = [
            cast(
                "cards.MoneyCard | cards.ActionCard",
                cards.from_json(card_data),
            )
            for card_data in data["bank"]
        ]
        return player
