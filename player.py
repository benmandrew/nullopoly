import card


class PropertySet:
    def __init__(self, colour: card.PropertyColour, required_count: int):
        self.colour = colour
        self.required_count = required_count
        self.cards: list[card.PropertyCard] = []

    def add(self, card_obj: card.PropertyCard) -> None:
        assert (
            card_obj.colour() == self.colour
        ), f"Card colour {card_obj.colour()} does not match set colour {self.colour}"
        self.cards.append(card_obj)

    def remove(self, card_obj: card.PropertyCard) -> None:
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
        return card.PROPERTY_RENTS[self.colour][len(self.cards) - 1]


class PlayerState:
    def __init__(self, name: str):
        self.name = name
        self.hand: list[card.Card] = []
        self.properties: dict[card.PropertyColour, PropertySet] = (
            self.empty_property_sets()
        )
        self.bank: list[card.MoneyCard | card.ActionCard] = []

    @classmethod
    def empty_property_sets(cls) -> dict[card.PropertyColour, PropertySet]:
        required_counts = {
            card.PropertyColour.BROWN: 2,
            card.PropertyColour.LIGHT_BLUE: 3,
            card.PropertyColour.PINK: 3,
            card.PropertyColour.ORANGE: 3,
            card.PropertyColour.RED: 3,
            card.PropertyColour.YELLOW: 3,
            card.PropertyColour.GREEN: 3,
            card.PropertyColour.DARK_BLUE: 2,
            card.PropertyColour.RAILROAD: 4,
            card.PropertyColour.UTILITY: 2,
        }
        return {
            colour: PropertySet(colour, count)
            for colour, count in required_counts.items()
        }

    def add_to_hand(self, card_obj: card.Card) -> None:
        self.hand.append(card_obj)

    def add_property(self, property_card: card.PropertyCard) -> None:
        self.properties[property_card.colour()].add(property_card)

    def add_to_bank(self, card_obj: card.MoneyCard | card.ActionCard) -> None:
        self.bank.append(card_obj)

    def total_bank_value(self) -> int:
        return sum(card_obj.value() for card_obj in self.bank)

    def properties_to_list(self) -> list[card.PropertyCard]:
        return [
            card_obj
            for property_set in self.properties.values()
            for card_obj in property_set.cards
        ]

    def play_card_from_hand(self, i: int) -> None:
        assert 0 <= i < len(self.hand), "Index out of range for hand"
        card_obj = self.hand.pop(i)
        if isinstance(card_obj, card.PropertyCard):
            self.add_property(card_obj)
        elif isinstance(card_obj, card.MoneyCard):
            self.add_to_bank(card_obj)
        elif isinstance(card_obj, card.ActionCard):
            choice = input(
                "Choose an option:\n1. Play action\n2. Add to bank\n"
            )
            if choice == "1":
                raise NotImplementedError("Action card play not implemented")
            if choice == "2":
                self.add_to_bank(card_obj)
            else:
                raise ValueError("Invalid choice for action card")
        else:
            raise ValueError(f"Unknown card type: {type(card_obj)}")

    def add_payment(self, cards: list[card.Card]) -> None:
        for card_obj in cards:
            if isinstance(card_obj, card.PropertyCard):
                self.add_property(card_obj)
            elif isinstance(card_obj, (card.MoneyCard, card.ActionCard)):
                self.add_to_bank(card_obj)
            else:
                raise ValueError(f"Unknown card type: {type(card_obj)}")

    def charge_properties(self, amount: int) -> list[card.PropertyCard]:
        assert amount > 0, "Charge amount must be positive"
        charged_properties = self.properties_to_list()
        self.properties = self.empty_property_sets()
        return charged_properties

    def charge_payment(
        self, amount: int
    ) -> tuple[list[card.MoneyCard | card.ActionCard], list[card.PropertyCard]]:
        assert amount > 0, "Charge amount must be positive"
        charged_cards = []
        remaining = amount
        for card_obj in self.bank:
            if remaining <= 0:
                break
            if isinstance(card_obj, (card.MoneyCard, card.ActionCard)):
                if card_obj.value() <= remaining:
                    remaining -= card_obj.value()
                    charged_cards.append(card_obj)
                    self.bank.remove(card_obj)
        charged_properties = (
            self.charge_properties(remaining) if remaining > 0 else []
        )
        return charged_cards, charged_properties

    def fmt_state(self) -> str:
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
        lines.append("Hand:")
        lines.append(card.fmt_cards_side_by_side(self.hand))
        lines.append("-" * 40)
        return "\n".join(lines)
