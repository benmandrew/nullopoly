import itertools

import cards


class PropertySet:
    def __init__(self, colour: cards.PropertyColour, required_count: int):
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


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: list[cards.Card] = []
        self.properties: dict[cards.PropertyColour, PropertySet] = (
            self.empty_property_sets()
        )
        self.bank: list[cards.MoneyCard | cards.ActionCard] = []

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
        self, without_full_sets: bool = False
    ) -> list[cards.PropertyCard]:
        result = []
        for property_set in self.properties.values():
            if without_full_sets and property_set.is_complete():
                continue
            result.extend(property_set.cards)
        return result

    def get_card_in_hand(self, i: int) -> cards.Card:
        """
        Get a card from the player's hand by index.
        """
        assert 0 <= i < len(self.hand), "Index out of range for hand"
        return self.hand[i]

    def remove_card_from_hand(self, card: cards.Card) -> None:
        """
        Remove a card from the player's hand.
        """
        assert card in self.hand, "Card not found in hand"
        self.hand.remove(card)

    def add_payment(self, payment: list[cards.Card]) -> None:
        for card in payment:
            if isinstance(card, cards.PropertyCard):
                self.add_property(card)
            elif isinstance(card, (cards.MoneyCard, cards.ActionCard)):
                self.add_to_bank(card)
            else:
                raise ValueError(f"Unknown card type: {type(card)}")

    def remove_property(self, card: cards.PropertyCard) -> None:
        self.properties[card.colour].remove(card)

    def charge_money_payment(
        self, amount: int
    ) -> tuple[list[cards.MoneyCard | cards.ActionCard], int]:
        """
        Find the optimal set of cards to minimize overpayment.
        """
        bank_cards = list(self.bank)
        n = len(bank_cards)
        best_combo = None
        best_total = None
        for r in range(0, n):
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
        """
        Returns True if the player has at least three complete property sets.
        """
        complete_sets = sum(
            1 for prop_set in self.properties.values() if prop_set.is_complete()
        )
        return complete_sets >= 3

    def has_complete_property_set(self) -> bool:
        """
        Returns True if the player has at least one complete property set.
        """
        return any(
            prop_set.is_complete() for prop_set in self.properties.values()
        )

    def n_properties(self, without_full_sets: bool = False) -> int:
        """
        Returns the total number of properties the player has.
        """
        if without_full_sets:
            return sum(
                len(prop_set.cards)
                for prop_set in self.properties.values()
                if not prop_set.is_complete()
            )
        return sum(len(prop_set.cards) for prop_set in self.properties.values())

    def has_properties(self, without_full_sets: bool = False) -> bool:
        """
        Returns True if the player has any properties.
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
