import unittest

import cards
import game
import player
from interaction import ai, dummy


class TestAIInteraction(unittest.TestCase):
    def setUp(self) -> None:
        player.Player.global_index = 0
        self.ai = ai.AIInteraction(me_idx=0)
        self.p1 = player.Player("AI", self.ai)
        self.p2 = player.Player("Human", dummy.DummyInteraction())
        self.g = game.Game([self.p1, self.p2], [])
        self.ai.set_game_instance(self.g)

    def test_choose_card_in_hand_prefers_high_value(self) -> None:
        # Give AI a hand with two cards of different values
        card1 = cards.MoneyCard(1)
        card2 = cards.MoneyCard(5)
        self.p1.hand = [card1, card2]
        chosen = self.ai.choose_card_in_hand(self.p1)
        self.assertEqual(chosen, card2)

    def test_choose_property_target_prefers_high_value(self) -> None:
        # Give p2 two properties, AI should pick the higher value
        prop1 = cards.PropertyCard("Cheap", 1, cards.PropertyColour.RED)
        prop2 = cards.PropertyCard("Expensive", 5, cards.PropertyColour.RED)
        self.p2.add_property(prop1)
        self.p2.add_property(prop2)
        chosen = self.ai.choose_property_target(self.p2)
        self.assertEqual(chosen, prop2)

    def test_choose_rent_colour_and_amount_picks_highest(self) -> None:
        # AI owns 1 Dark Blue (£3) and 2 Green (£4) properties
        darkblue = cards.PropertyCard(
            "Park Lane",
            4,
            cards.PropertyColour.DARK_BLUE,
        )
        green1 = cards.PropertyCard("Green1", 2, cards.PropertyColour.GREEN)
        green2 = cards.PropertyCard("Green2", 2, cards.PropertyColour.GREEN)
        self.p1.add_property(darkblue)
        self.p1.add_property(green1)
        self.p1.add_property(green2)
        rent_card = cards.ActionCard(
            "Rent Green/Dark Blue",
            1,
            cards.ActionType.RENT_GREEN_DARK_BLUE,
        )
        # Get the rent options as the AI would see them
        owned = self.p1.owned_colours_with_rents(
            cards.RENT_CARD_COLOURS[rent_card.action],
        )
        # Should pick Green (2 cards = £4) over Dark Blue (1 card = £3)
        colour, amount = self.ai.choose_rent_colour_and_amount(owned)
        self.assertEqual(colour, cards.PropertyColour.GREEN)
        self.assertEqual(amount, 4)

        # Now remove one green so Dark Blue is best
        self.p1.properties[cards.PropertyColour.GREEN].remove(green2)
        owned = self.p1.owned_colours_with_rents(
            cards.RENT_CARD_COLOURS[rent_card.action],
        )
        # Should pick Dark Blue (1 card = £3) over Green (1 card = £2)
        colour, amount = self.ai.choose_rent_colour_and_amount(owned)
        self.assertEqual(colour, cards.PropertyColour.DARK_BLUE)
        self.assertEqual(amount, 3)

    def test_game_state_value(self) -> None:
        # AI has 2 money cards and 1 property, Human has 1 property
        self.p1.hand = []
        self.p1.bank = [cards.MoneyCard(2), cards.MoneyCard(3)]
        prop1 = cards.PropertyCard("Blue", 4, cards.PropertyColour.DARK_BLUE)
        self.p1.add_property(prop1)
        prop2 = cards.PropertyCard("Red", 1, cards.PropertyColour.RED)
        self.p2.add_property(prop2)
        # The value is:
        # AI (bank 5 + property 4) - Human (property 1) + len(hand)
        expected = (5 + 4) - 1 + 0
        assert self.ai.planner is not None, "AI planner should be set"
        value = self.ai.planner.game_state_value(self.g, self.p1)
        self.assertEqual(value, expected)


if __name__ == "__main__":
    unittest.main()
