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

    def test_game_state_static_value(self) -> None:
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

    def test_sly_deal_prefers_high_value(self) -> None:
        # Give p2 two properties, AI should pick the higher value
        prop1 = cards.PropertyCard("Cheap", 1, cards.PropertyColour.RED)
        prop2 = cards.PropertyCard("Expensive", 5, cards.PropertyColour.RED)
        self.p2.add_property(prop1)
        self.p2.add_property(prop2)
        assert self.ai.planner is not None
        plan = self.ai.planner.choose_plan(
            [
                cards.ActionCard(
                    "Sly Deal",
                    2,
                    cards.ActionType.SLY_DEAL,
                ),
            ],
        )
        assert isinstance(
            plan,
            ai.SlyDealPlan,
        ), "Plan should be an instance of SlyDealPlan"
        self.assertEqual(plan.target_property, prop2)

    def test_game_state_forced_deal_value(self) -> None:
        ai_swap = cards.PropertyCard("Cheap", 1, cards.PropertyColour.RED)
        ai_keep = cards.PropertyCard("Expensive", 5, cards.PropertyColour.BROWN)
        opp_swap = cards.PropertyCard(
            "Expensive",
            5,
            cards.PropertyColour.GREEN,
        )
        opp_keep = cards.PropertyCard(
            "Cheap",
            1,
            cards.PropertyColour.LIGHT_BLUE,
        )
        self.p1.add_property(ai_swap)
        self.p1.add_property(ai_keep)
        self.p2.add_property(opp_swap)
        self.p2.add_property(opp_keep)
        forced_deal = cards.ActionCard(
            "Forced Deal",
            3,
            cards.ActionType.FORCED_DEAL,
        )
        # Set up the planner and generate plans
        assert self.ai.planner is not None
        all_plans = self.ai.planner.generate_plans(forced_deal)
        valuations = [
            self.ai.planner.plan_value_if_played(plan) for plan in all_plans
        ]
        self.assertListEqual(valuations, [-8, 0, 0, 8])

    def test_forced_deal_ai_prefers_high_for_low(self) -> None:
        ai_swap = cards.PropertyCard("Cheap", 1, cards.PropertyColour.RED)
        ai_keep = cards.PropertyCard("Expensive", 5, cards.PropertyColour.BROWN)
        opp_swap = cards.PropertyCard(
            "Expensive",
            5,
            cards.PropertyColour.GREEN,
        )
        opp_keep = cards.PropertyCard(
            "Cheap",
            1,
            cards.PropertyColour.LIGHT_BLUE,
        )
        self.p1.add_property(ai_swap)
        self.p1.add_property(ai_keep)
        self.p2.add_property(opp_swap)
        self.p2.add_property(opp_keep)
        forced_deal = cards.ActionCard(
            "Forced Deal",
            3,
            cards.ActionType.FORCED_DEAL,
        )
        assert self.ai.planner is not None
        plan = self.ai.planner.choose_plan([forced_deal])
        assert isinstance(
            plan,
            ai.ForcedDealPlan,
        ), "Plan should be an instance of ForcedDealPlan"
        self.assertEqual(plan.source_property, ai_swap)
        self.assertEqual(plan.target_property, opp_swap)


if __name__ == "__main__":
    unittest.main()
