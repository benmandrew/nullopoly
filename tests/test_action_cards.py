import unittest
from typing import cast
from unittest.mock import Mock, patch

import cards
import game
import player
from tests import utils
from window import common


class TestActionCards(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_interaction = Mock()
        players = [
            player.Player(name, self.mock_interaction)
            for name in ["P1", "P2", "P3"]
        ]
        self.g = game.Game(
            players,
            [],
            starting_cards=0,
        )
        self.g.start()
        self.p1 = self.g.get_player_by_name("P1")
        self.p2 = self.g.get_player_by_name("P2")
        self.p3 = self.g.get_player_by_name("P3")

    def test_debt_collector(self) -> None:
        action_card = cards.ActionCard(
            "Debt Collector",
            3,
            cards.ActionType.DEBT_COLLECTOR,
        )
        self.p2.add_to_bank(cards.MoneyCard(3))
        self.p2.add_to_bank(cards.MoneyCard(3))
        self.p2.add_to_bank(cards.MoneyCard(1))
        with patch.object(
            self.mock_interaction,
            "choose_player_target",
            return_value=self.p2,
        ):
            self.g.play_action_card(action_card, self.p1)
        self.assertEqual(self.p1.total_bank_value(), 6)
        self.assertEqual(self.p2.total_bank_value(), 1)

    def test_birthday(self) -> None:
        action_card = cards.ActionCard(
            "Birthday",
            2,
            cards.ActionType.ITS_MY_BIRTHDAY,
        )
        self.p1.add_to_bank(cards.MoneyCard(5))
        self.p2.add_to_bank(cards.MoneyCard(10))
        self.p2.add_to_bank(cards.MoneyCard(1))
        self.p2.add_property(
            cards.PropertyCard("Prop1", 2, cards.PropertyColour.RED),
        )
        property2 = cards.PropertyCard("Prop2", 2, cards.PropertyColour.RED)
        self.p3.add_property(property2)
        with patch.object(
            self.mock_interaction,
            "choose_property_source",
            return_value=property2,
        ):
            self.g.play_action_card(action_card, self.p1)
            self.assertEqual(self.p2.total_bank_value(), 1)
            self.assertEqual(self.p3.total_bank_value(), 0)
            properties: list[cards.Card] = cast(
                "list[cards.Card]",
                self.p1.properties_to_list(),
            )
            result = utils.strip_and_join(
                cards.fmt_cards_side_by_side(properties),
            )
            self.assertMultiLineEqual(
                result,
                utils.format_expect(
                    """
                    1.
                    ┌───────┐
                    │ Prop2 │
                    │ Red   │
                    │ £2    │
                    └───────┘
                """,
                ),
            )

    def test_pass_go(self) -> None:
        self.g.deck.extend([cards.MoneyCard(1), cards.MoneyCard(2)])
        action_card = cards.ActionCard("Pass Go", 1, cards.ActionType.PASS_GO)
        self.p1.add_to_hand(
            cards.ActionCard("Action", 3, cards.ActionType.PASS_GO),
        )
        self.g.play_action_card(action_card, self.p1)
        self.assertEqual(len(self.p1.hand), 3)


class TestRentCards(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_interaction = Mock()
        players = [
            player.Player(name, self.mock_interaction)
            for name in ["P1", "P2", "P3"]
        ]
        self.g = game.Game(
            players,
            [],
            starting_cards=0,
        )
        self.g.start()
        self.p1 = self.g.get_player_by_name("P1")
        self.p2 = self.g.get_player_by_name("P2")
        self.p3 = self.g.get_player_by_name("P3")
        # Give P1 properties in two colours
        self.p1.add_property(
            cards.PropertyCard("Brown1", 1, cards.PropertyColour.BROWN),
        )
        self.p1.add_property(
            cards.PropertyCard(
                "LightBlue1",
                1,
                cards.PropertyColour.LIGHT_BLUE,
            ),
        )
        self.p1.add_property(
            cards.PropertyCard(
                "LightBlue2",
                1,
                cards.PropertyColour.LIGHT_BLUE,
            ),
        )
        # Give P2 and P3 some money
        self.p2.add_to_bank(cards.MoneyCard(1))
        self.p2.add_to_bank(cards.MoneyCard(2))
        self.p3.add_to_bank(cards.MoneyCard(1))
        self.p3.add_to_bank(cards.MoneyCard(2))

    def test_rent_brown_light_blue_brown(self) -> None:
        rent_card = cards.ActionCard(
            "Rent Brown/Light Blue",
            1,
            cards.ActionType.RENT_BROWN_LIGHT_BLUE,
        )
        with patch.object(
            self.mock_interaction,
            "choose_rent_colour_and_amount",
            return_value=(
                cards.PropertyColour.BROWN,
                cards.PROPERTY_RENTS[cards.PropertyColour.BROWN][0],
            ),
        ):
            self.g.play_rent_card(rent_card, self.p1)
        # Brown rent for 1 property is 1
        self.assertEqual(self.p1.total_bank_value(), 2)
        self.assertEqual(self.p2.total_bank_value(), 2)
        self.assertEqual(self.p3.total_bank_value(), 2)

    def test_rent_brown_light_blue_light_blue(self) -> None:
        rent_card = cards.ActionCard(
            "Rent Brown/Light Blue",
            1,
            cards.ActionType.RENT_BROWN_LIGHT_BLUE,
        )
        with patch.object(
            self.mock_interaction,
            "choose_rent_colour_and_amount",
            return_value=(
                cards.PropertyColour.LIGHT_BLUE,
                cards.PROPERTY_RENTS[cards.PropertyColour.LIGHT_BLUE][1],
            ),
        ):
            self.g.play_rent_card(rent_card, self.p1)
        # Light Blue rent for 2 properties is 2
        self.assertEqual(self.p1.total_bank_value(), 4)
        self.assertEqual(self.p2.total_bank_value(), 1)
        self.assertEqual(self.p3.total_bank_value(), 1)

    def test_rent_green_dark_blue(self) -> None:
        self.p1.add_property(
            cards.PropertyCard("DarkBlue1", 1, cards.PropertyColour.DARK_BLUE),
        )
        self.p2.add_to_bank(cards.MoneyCard(2))
        rent_card = cards.ActionCard(
            "Rent Green/Dark Blue",
            1,
            cards.ActionType.RENT_GREEN_DARK_BLUE,
        )
        with patch.object(
            self.mock_interaction,
            "choose_rent_colour_and_amount",
            return_value=(
                cards.PropertyColour.DARK_BLUE,
                cards.PROPERTY_RENTS[cards.PropertyColour.DARK_BLUE][0],
            ),
        ):
            self.g.play_rent_card(rent_card, self.p1)
        # Dark Blue rent for 1 property is 3
        self.assertEqual(self.p1.total_bank_value(), 6)
        self.assertEqual(self.p2.total_bank_value(), 2)
        self.assertEqual(self.p3.total_bank_value(), 0)

    def test_rent_wild(self) -> None:
        self.p1.add_property(
            cards.PropertyCard("Green1", 1, cards.PropertyColour.GREEN),
        )
        self.p2.add_to_bank(cards.MoneyCard(2))
        rent_card = cards.ActionCard("Rent Wild", 1, cards.ActionType.RENT_WILD)
        with patch.object(
            self.mock_interaction,
            "choose_rent_colour_and_amount",
            return_value=(
                cards.PropertyColour.GREEN,
                cards.PROPERTY_RENTS[cards.PropertyColour.GREEN][0],
            ),
        ), patch.object(
            self.mock_interaction,
            "choose_player_target",
            return_value=self.p2,
        ):
            self.g.play_rent_card(rent_card, self.p1)
        # Green rent for 1 property is 2, target is P2
        self.assertEqual(self.p1.total_bank_value(), 2)
        self.assertEqual(self.p2.total_bank_value(), 3)
        self.assertEqual(self.p3.total_bank_value(), 3)


class TestDealBreaker(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_interaction = Mock()
        players = [
            player.Player(name, self.mock_interaction) for name in ["P1", "P2"]
        ]
        self.g = game.Game(players, [], starting_cards=0)
        self.g.start()
        self.p1 = self.g.get_player_by_name("P1")
        self.p2 = self.g.get_player_by_name("P2")
        for _ in range(2):
            self.p2.add_property(
                cards.PropertyCard("Brown", 1, cards.PropertyColour.BROWN),
            )
        for _ in range(3):
            self.p2.add_property(
                cards.PropertyCard("Yellow", 1, cards.PropertyColour.YELLOW),
            )

    def test_deal_breaker(self) -> None:
        with patch.object(
            self.mock_interaction,
            "choose_player_target",
            return_value=self.p2,
        ), patch.object(
            self.mock_interaction,
            "choose_full_set_target",
            return_value=self.p2.properties[cards.PropertyColour.BROWN],
        ):
            self.g.play_deal_breaker(self.p1)
        self.assertEqual(
            len(self.p1.properties[cards.PropertyColour.BROWN].cards),
            2,
        )
        self.assertEqual(
            len(self.p2.properties[cards.PropertyColour.BROWN].cards),
            0,
        )
        self.assertEqual(
            len(self.p1.properties[cards.PropertyColour.YELLOW].cards),
            0,
        )
        self.assertEqual(
            len(self.p2.properties[cards.PropertyColour.YELLOW].cards),
            3,
        )
        with patch.object(
            self.mock_interaction,
            "choose_player_target",
            return_value=self.p1,
        ), patch.object(
            self.mock_interaction,
            "choose_full_set_target",
            return_value=self.p1.properties[cards.PropertyColour.BROWN],
        ):
            self.g.play_deal_breaker(self.p2)
        self.assertEqual(
            len(self.p1.properties[cards.PropertyColour.BROWN].cards),
            0,
        )
        self.assertEqual(
            len(self.p2.properties[cards.PropertyColour.BROWN].cards),
            2,
        )
        self.assertEqual(
            len(self.p1.properties[cards.PropertyColour.YELLOW].cards),
            0,
        )
        self.assertEqual(
            len(self.p2.properties[cards.PropertyColour.YELLOW].cards),
            3,
        )

    def test_forced_deal_no_properties(self) -> None:
        self.p2.properties = self.p2.empty_property_sets()
        with patch.object(
            self.mock_interaction,
            "choose_player_target",
            return_value=self.p2,
        ), self.assertRaises(common.InvalidChoiceError):
            self.g.play_deal_breaker(self.p1)


class TestSlyDeal(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_interaction = Mock()
        players = [
            player.Player(name, self.mock_interaction) for name in ["P1", "P2"]
        ]
        self.g = game.Game(players, [], starting_cards=0)
        self.g.start()
        self.p1 = self.g.get_player_by_name("P1")
        self.p2 = self.g.get_player_by_name("P2")
        self.p2.add_property(
            cards.PropertyCard("Red", 1, cards.PropertyColour.RED),
        )

    def test_sly_deal(self) -> None:
        with patch.object(
            self.mock_interaction,
            "choose_player_target",
            return_value=self.p2,
        ), patch.object(
            self.mock_interaction,
            "choose_property_target",
            return_value=self.p2.properties[cards.PropertyColour.RED].cards[0],
        ):
            self.g.play_sly_deal(self.p1)
        self.assertEqual(
            len(self.p1.properties[cards.PropertyColour.RED].cards),
            1,
        )
        self.assertEqual(
            len(self.p2.properties[cards.PropertyColour.RED].cards),
            0,
        )

    def test_forced_deal_no_properties(self) -> None:
        self.p2.properties = self.p2.empty_property_sets()
        with patch.object(
            self.mock_interaction,
            "choose_player_target",
            return_value=self.p2,
        ), self.assertRaises(common.InvalidChoiceError):
            self.g.play_sly_deal(self.p1)


class TestForcedDeal(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_interaction = Mock()
        players = [
            player.Player(name, self.mock_interaction) for name in ["P1", "P2"]
        ]
        self.g = game.Game(players, [], starting_cards=0)
        self.g.start()
        self.p1 = self.g.get_player_by_name("P1")
        self.p2 = self.g.get_player_by_name("P2")
        self.p1.add_property(
            cards.PropertyCard("Red", 1, cards.PropertyColour.RED),
        )
        self.p2.add_property(
            cards.PropertyCard("Yellow", 1, cards.PropertyColour.YELLOW),
        )

    def test_forced_deal(self) -> None:
        with patch.object(
            self.mock_interaction,
            "choose_player_target",
            return_value=self.p2,
        ), patch.object(
            self.mock_interaction,
            "choose_property_target",
            return_value=self.p2.properties[cards.PropertyColour.YELLOW].cards[
                0
            ],
        ), patch.object(
            self.mock_interaction,
            "choose_property_source",
            return_value=self.p1.properties[cards.PropertyColour.RED].cards[0],
        ):
            self.g.play_forced_deal(self.p1)
        self.assertEqual(
            len(self.p1.properties[cards.PropertyColour.RED].cards),
            0,
        )
        self.assertEqual(
            len(self.p2.properties[cards.PropertyColour.RED].cards),
            1,
        )
        self.assertEqual(
            len(self.p2.properties[cards.PropertyColour.YELLOW].cards),
            0,
        )
        self.assertEqual(
            len(self.p1.properties[cards.PropertyColour.YELLOW].cards),
            1,
        )

    def test_forced_deal_target_no_properties(self) -> None:
        self.p2.properties = self.p2.empty_property_sets()
        with patch.object(
            self.mock_interaction,
            "choose_player_target",
            return_value=self.p2,
        ), self.assertRaises(common.InvalidChoiceError):
            self.g.play_forced_deal(self.p1)

    def test_forced_deal_source_no_properties(self) -> None:
        self.p1.properties = self.p1.empty_property_sets()
        with self.assertRaises(common.InvalidChoiceError):
            self.g.play_forced_deal(self.p1)
