import cards


class PropertySet:
    def __init__(self, colour: cards.PropertyColour, required_count: int):
        self.colour = colour
        self.required_count = required_count
        self.cards: list[cards.PropertyCard] = []

    def add(self, card_obj: cards.PropertyCard) -> None:
        assert (
            card_obj.colour() == self.colour
        ), f"Card colour {card_obj.colour()} does not match set colour {self.colour}"
        self.cards.append(card_obj)

    def remove(self, card_obj: cards.PropertyCard) -> None:
        assert card_obj in self.cards, "Card not found in the property set"
        assert (
            card_obj.colour() == self.colour
        ), f"Card colour {card_obj.colour()} does not match set colour {self.colour}"
        self.cards.remove(card_obj)

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

    def add_to_hand(self, card_obj: cards.Card) -> None:
        self.hand.append(card_obj)

    def add_property(self, property_card: cards.PropertyCard) -> None:
        self.properties[property_card.colour()].add(property_card)

    def add_to_bank(self, card_obj: cards.MoneyCard | cards.ActionCard) -> None:
        self.bank.append(card_obj)

    def total_bank_value(self) -> int:
        return sum(card_obj.value() for card_obj in self.bank)

    def properties_to_list(self) -> list[cards.PropertyCard]:
        return [
            card_obj
            for property_set in self.properties.values()
            for card_obj in property_set.cards
        ]

    def remove_card_from_hand(self, i: int) -> cards.Card:
        assert 0 <= i < len(self.hand), "Index out of range for hand"
        return self.hand.pop(i)

    def add_payment(self, payment: list[cards.Card]) -> None:
        for card in payment:
            if isinstance(card, cards.PropertyCard):
                self.add_property(card)
            elif isinstance(card, (cards.MoneyCard, cards.ActionCard)):
                self.add_to_bank(card)
            else:
                raise ValueError(f"Unknown card type: {type(card)}")

    def charge_properties(self, amount: int) -> list[cards.PropertyCard]:
        assert amount > 0, "Charge amount must be positive"
        charged_properties = self.properties_to_list()
        self.properties = self.empty_property_sets()
        return charged_properties

    def charge_payment(
        self, amount: int
    ) -> tuple[
        list[cards.MoneyCard | cards.ActionCard], list[cards.PropertyCard]
    ]:
        assert amount > 0, "Charge amount must be positive"
        charged_cards = []
        remaining = amount
        for card_obj in self.bank:
            if remaining <= 0:
                break
            if isinstance(card_obj, (cards.MoneyCard, cards.ActionCard)):
                if card_obj.value() <= remaining:
                    remaining -= card_obj.value()
                    charged_cards.append(card_obj)
                    self.bank.remove(card_obj)
        charged_properties = (
            self.charge_properties(remaining) if remaining > 0 else []
        )
        return charged_cards, charged_properties

    def fmt_visible_state(self) -> list[str]:
        lines = [f"Player: {self.name}", "Properties:"]
        for colour, prop_set in self.properties.items():
            if not prop_set.cards:
                continue
            cards_str = ", ".join(
                card_obj.name() for card_obj in prop_set.cards
            )
            lines.append(f"  {colour.name.title():<15}: {cards_str}")
        bank_str = ", ".join(f"£{card_obj.value()}" for card_obj in self.bank)
        lines.append(f"Bank (£{self.total_bank_value()}): {bank_str}")
        return lines

    def fmt_hand(self) -> list[str]:
        lines = ["Hand:"]
        lines.extend(cards.fmt_cards_side_by_side(self.hand))
        return lines
