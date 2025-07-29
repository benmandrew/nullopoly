import textwrap
import unittest
from unittest.mock import Mock, patch

import cards
import game


def format_expect(s: str) -> str:
    return textwrap.dedent(s).strip("\n")


def strip_and_join(lines: list[str]) -> str:
    return "\n".join(line.strip() for line in lines).strip("\n")


class TestGameStart(unittest.TestCase):
    def test_players_start_with_five_cards(self):
        mock_window = Mock()
        deck = [cards.MoneyCard(1) for _ in range(15)]
        g = game.Game(["Alice", "Bob", "Charlie"], deck, mock_window)
        g.start()
        for player in g.players:
            self.assertEqual(len(player.hand), 5)


class TestPayments(unittest.TestCase):
    def setUp(self):
        mock_window = Mock()
        self.g = game.Game(["TestPlayer"], [], mock_window, starting_cards=0)
        self.g.start()
        self.player = self.g.get_player("TestPlayer")
        self.player.add_to_bank(cards.MoneyCard(5))
        self.player.add_to_bank(
            cards.ActionCard("DummyAction", 3, cards.ActionType.PASS_GO)
        )
        self.player.add_property(
            cards.PropertyCard("Property1", 2, cards.PropertyColour.RED)
        )
        self.player.add_property(
            cards.PropertyCard("Property2", 2, cards.PropertyColour.RED)
        )

    def test_get_payment_1(self):
        with patch.object(self.g.win, "get_number_input", side_effect=[]):
            money, properties = self.g.get_payment(self.player, 5)
            charged_cards = strip_and_join(
                cards.fmt_cards_side_by_side(money + properties)
            )
            self.assertMultiLineEqual(
                charged_cards,
                format_expect(
                    """
                1.
                ┌───────┐
                │ Money │
                │       │
                │ £5    │
                └───────┘
            """
                ),
            )
            self.assertEqual(self.player.total_bank_value(), 3)
            self.assertEqual(len(self.player.properties_to_list()), 2)

    def test_get_payment_2(self):
        with patch.object(self.g.win, "get_number_input", side_effect=[1]):
            money, properties = self.g.get_payment(self.player, 10)
            charged_cards = strip_and_join(
                cards.fmt_cards_side_by_side(money + properties)
            )
            self.assertMultiLineEqual(
                charged_cards,
                format_expect(
                    """
                1.       2.         3.
                ┌───────┐┌─────────┐┌───────────┐
                │ Money ││ Pass Go ││ Property1 │
                │       ││         ││ Red       │
                │ £5    ││ £3      ││ £2        │
                └───────┘└─────────┘└───────────┘
            """
                ),
            )
            self.assertEqual(self.player.total_bank_value(), 0)
            self.assertEqual(len(self.player.properties_to_list()), 1)

    def test_get_payment_3(self):
        with patch.object(self.g.win, "get_number_input", side_effect=[1, 1]):
            money, properties = self.g.get_payment(self.player, 20)
            charged_cards = strip_and_join(
                cards.fmt_cards_side_by_side(money + properties)
            )
            self.assertMultiLineEqual(
                charged_cards,
                format_expect(
                    """
                    1.       2.         3.           4.
                    ┌───────┐┌─────────┐┌───────────┐┌───────────┐
                    │ Money ││ Pass Go ││ Property1 ││ Property2 │
                    │       ││         ││ Red       ││ Red       │
                    │ £5    ││ £3      ││ £2        ││ £2        │
                    └───────┘└─────────┘└───────────┘└───────────┘
                """
                ),
            )
            self.assertEqual(self.player.total_bank_value(), 0)
            self.assertEqual(len(self.player.properties_to_list()), 0)


class TestActionCards(unittest.TestCase):
    def setUp(self):
        self.mock_window = Mock()
        self.g = game.Game(
            ["P1", "P2", "P3"], [], self.mock_window, starting_cards=0
        )
        self.g.start()
        self.p1 = self.g.get_player("P1")
        self.p2 = self.g.get_player("P2")
        self.p3 = self.g.get_player("P3")

    def test_debt_collector(self):
        action_card = cards.ActionCard(
            "Debt Collector", 3, cards.ActionType.DEBT_COLLECTOR
        )
        self.p2.add_to_bank(cards.MoneyCard(3))
        self.p2.add_to_bank(cards.MoneyCard(3))
        self.p2.add_to_bank(cards.MoneyCard(1))
        with patch.object(
            self.g, "choose_player_target", return_value=self.p2
        ), patch.object(self.g.win, "get_number_input", return_value=1):
            self.g.play_action_card(action_card, self.p1)
        self.assertEqual(self.p1.total_bank_value(), 6)
        self.assertEqual(self.p2.total_bank_value(), 1)

    def test_birthday(self):
        action_card = cards.ActionCard(
            "Birthday", 2, cards.ActionType.ITS_MY_BIRTHDAY
        )
        self.p1.add_to_bank(cards.MoneyCard(5))
        self.p2.add_to_bank(cards.MoneyCard(10))
        self.p2.add_to_bank(cards.MoneyCard(1))
        self.p2.add_property(
            cards.PropertyCard("Prop", 2, cards.PropertyColour.RED)
        )
        self.p3.add_property(
            cards.PropertyCard("Prop", 2, cards.PropertyColour.RED)
        )
        with patch.object(self.g.win, "get_number_input", return_value=1):
            self.g.play_action_card(action_card, self.p1)
            self.assertEqual(self.p2.total_bank_value(), 1)
            self.assertEqual(self.p3.total_bank_value(), 0)
            result = strip_and_join(
                cards.fmt_cards_side_by_side(self.p1.properties_to_list())
            )
            self.assertMultiLineEqual(
                result,
                format_expect(
                    """
                    1.
                    ┌──────┐
                    │ Prop │
                    │ Red  │
                    │ £2   │
                    └──────┘
                """
                ),
            )

    def test_pass_go(self):
        self.g.deck.extend([cards.MoneyCard(1), cards.MoneyCard(2)])
        action_card = cards.ActionCard("Pass Go", 1, cards.ActionType.PASS_GO)
        self.p1.add_to_hand(
            cards.ActionCard("Action", 3, cards.ActionType.PASS_GO)
        )
        self.g.play_action_card(action_card, self.p1)
        self.assertEqual(len(self.p1.hand), 3)


class TestRentCards(unittest.TestCase):
    def setUp(self):
        self.mock_window = Mock()
        self.g = game.Game(
            ["P1", "P2", "P3"], [], self.mock_window, starting_cards=0
        )
        self.g.start()
        self.p1 = self.g.get_player("P1")
        self.p2 = self.g.get_player("P2")
        self.p3 = self.g.get_player("P3")
        # Give P1 properties in two colours
        self.p1.add_property(
            cards.PropertyCard("Brown1", 1, cards.PropertyColour.BROWN)
        )
        self.p1.add_property(
            cards.PropertyCard("LightBlue1", 1, cards.PropertyColour.LIGHT_BLUE)
        )
        self.p1.add_property(
            cards.PropertyCard("LightBlue2", 1, cards.PropertyColour.LIGHT_BLUE)
        )
        # Give P2 and P3 some money
        self.p2.add_to_bank(cards.MoneyCard(1))
        self.p2.add_to_bank(cards.MoneyCard(2))
        self.p3.add_to_bank(cards.MoneyCard(1))
        self.p3.add_to_bank(cards.MoneyCard(2))

    def test_rent_brown_light_blue_brown(self):
        rent_card = cards.ActionCard(
            "Rent Brown/Light Blue", 1, cards.ActionType.RENT_BROWN_LIGHT_BLUE
        )
        # Patch rent colour choice to select BROWN (index 1)
        with patch.object(self.g.win, "get_number_input", return_value=1):
            self.g.play_rent_card(rent_card, self.p1)
        # Brown rent for 1 property is 1
        self.assertEqual(self.p1.total_bank_value(), 2)
        self.assertEqual(self.p2.total_bank_value(), 2)
        self.assertEqual(self.p3.total_bank_value(), 2)

    def test_rent_brown_light_blue_light_blue(self):
        rent_card = cards.ActionCard(
            "Rent Brown/Light Blue", 1, cards.ActionType.RENT_BROWN_LIGHT_BLUE
        )
        # Patch rent colour choice to select LIGHT_BLUE (index 2)
        with patch.object(self.g.win, "get_number_input", return_value=2):
            self.g.play_rent_card(rent_card, self.p1)
        # Light Blue rent for 2 properties is 2
        self.assertEqual(self.p1.total_bank_value(), 4)
        self.assertEqual(self.p2.total_bank_value(), 1)
        self.assertEqual(self.p3.total_bank_value(), 1)

    def test_rent_green_dark_blue(self):
        # Give P1 a dark blue property
        self.p1.add_property(
            cards.PropertyCard("DarkBlue1", 1, cards.PropertyColour.DARK_BLUE)
        )
        self.p2.add_to_bank(cards.MoneyCard(2))
        rent_card = cards.ActionCard(
            "Rent Green/Dark Blue", 1, cards.ActionType.RENT_GREEN_DARK_BLUE
        )
        # Patch rent colour choice to select DARK BLUE (index 1)
        with patch.object(self.g.win, "get_number_input", return_value=2):
            self.g.play_rent_card(rent_card, self.p1)
        # Dark Blue rent for 1 property is 3
        self.assertEqual(self.p1.total_bank_value(), 6)
        self.assertEqual(self.p2.total_bank_value(), 2)
        self.assertEqual(self.p3.total_bank_value(), 0)

    def test_rent_wild(self):
        # Give P1 a green property
        self.p1.add_property(
            cards.PropertyCard("Green1", 1, cards.PropertyColour.GREEN)
        )
        self.p2.add_to_bank(cards.MoneyCard(2))
        rent_card = cards.ActionCard("Rent Wild", 1, cards.ActionType.RENT_WILD)
        with patch.object(self.g.win, "get_number_input", side_effect=[2, 1]):
            self.g.play_rent_card(rent_card, self.p1)
        # Green rent for 1 property is 2
        self.assertEqual(self.p1.total_bank_value(), 2)
        self.assertEqual(self.p2.total_bank_value(), 3)
        self.assertEqual(self.p3.total_bank_value(), 3)


class TestGameWinCondition(unittest.TestCase):
    def setUp(self):
        self.mock_window = Mock()
        self.g = game.Game(["P1", "P2"], [], self.mock_window, starting_cards=0)
        self.g.start()
        self.p1 = self.g.get_player("P1")
        self.p2 = self.g.get_player("P2")

    def test_no_player_has_won(self):
        self.assertFalse(self.g.check_win())

    def test_player_has_won(self):
        # Complete three sets for P1
        for _ in range(2):
            self.p1.add_property(
                cards.PropertyCard("Brown", 1, cards.PropertyColour.BROWN)
            )
        for _ in range(3):
            self.p1.add_property(
                cards.PropertyCard("Red", 1, cards.PropertyColour.RED)
            )
        for _ in range(2):
            self.p1.add_property(
                cards.PropertyCard(
                    "Dark Blue", 1, cards.PropertyColour.DARK_BLUE
                )
            )
        self.assertTrue(self.g.check_win())


class TestDealBreaker(unittest.TestCase):
    def setUp(self):
        self.mock_window = Mock()
        self.g = game.Game(["P1", "P2"], [], self.mock_window, starting_cards=0)
        self.g.start()
        self.p1 = self.g.get_player("P1")
        self.p2 = self.g.get_player("P2")
        for _ in range(2):
            self.p2.add_property(
                cards.PropertyCard("Brown", 1, cards.PropertyColour.BROWN)
            )
        for _ in range(3):
            self.p2.add_property(
                cards.PropertyCard("Yellow", 1, cards.PropertyColour.YELLOW)
            )

    def test_deal_breaker(self):
        with patch.object(
            self.g, "choose_player_target", return_value=self.p2
        ), patch.object(
            self.g,
            "choose_full_set_target",
            return_value=self.p2.properties[cards.PropertyColour.BROWN],
        ):
            self.g.play_deal_breaker(self.p1)
        self.assertEqual(
            len(self.p1.properties[cards.PropertyColour.BROWN].cards), 2
        )
        self.assertEqual(
            len(self.p2.properties[cards.PropertyColour.BROWN].cards), 0
        )
        self.assertEqual(
            len(self.p1.properties[cards.PropertyColour.YELLOW].cards), 0
        )
        self.assertEqual(
            len(self.p2.properties[cards.PropertyColour.YELLOW].cards), 3
        )
        with patch.object(
            self.g, "choose_player_target", return_value=self.p1
        ), patch.object(
            self.g,
            "choose_full_set_target",
            return_value=self.p1.properties[cards.PropertyColour.BROWN],
        ):
            self.g.play_deal_breaker(self.p2)
        self.assertEqual(
            len(self.p1.properties[cards.PropertyColour.BROWN].cards), 0
        )
        self.assertEqual(
            len(self.p2.properties[cards.PropertyColour.BROWN].cards), 2
        )
        self.assertEqual(
            len(self.p1.properties[cards.PropertyColour.YELLOW].cards), 0
        )
        self.assertEqual(
            len(self.p2.properties[cards.PropertyColour.YELLOW].cards), 3
        )

    def test_forced_deal_no_properties(self):
        self.p2.properties = self.p2.empty_property_sets()
        with patch.object(
            self.g, "choose_player_target", return_value=self.p2
        ), self.assertRaises(game.window.InvalidChoiceError):
            self.g.play_deal_breaker(self.p1)


class TestSlyDeal(unittest.TestCase):
    def setUp(self):
        self.mock_window = Mock()
        self.g = game.Game(["P1", "P2"], [], self.mock_window, starting_cards=0)
        self.g.start()
        self.p1 = self.g.get_player("P1")
        self.p2 = self.g.get_player("P2")
        self.p2.add_property(
            cards.PropertyCard("Red", 1, cards.PropertyColour.RED)
        )

    def test_sly_deal(self):
        with patch.object(
            self.g, "choose_player_target", return_value=self.p2
        ), patch.object(
            self.g,
            "choose_property_target",
            return_value=self.p2.properties[cards.PropertyColour.RED].cards[0],
        ):
            self.g.play_sly_deal(self.p1)
        self.assertEqual(
            len(self.p1.properties[cards.PropertyColour.RED].cards), 1
        )
        self.assertEqual(
            len(self.p2.properties[cards.PropertyColour.RED].cards), 0
        )

    def test_forced_deal_no_properties(self):
        self.p2.properties = self.p2.empty_property_sets()
        with patch.object(
            self.g, "choose_player_target", return_value=self.p2
        ), self.assertRaises(game.window.InvalidChoiceError):
            self.g.play_sly_deal(self.p1)


class TestForcedDeal(unittest.TestCase):
    def setUp(self):
        self.mock_window = Mock()
        self.g = game.Game(["P1", "P2"], [], self.mock_window, starting_cards=0)
        self.g.start()
        self.p1 = self.g.get_player("P1")
        self.p2 = self.g.get_player("P2")
        self.p1.add_property(
            cards.PropertyCard("Red", 1, cards.PropertyColour.RED)
        )
        self.p2.add_property(
            cards.PropertyCard("Yellow", 1, cards.PropertyColour.YELLOW)
        )

    def test_forced_deal(self):
        with patch.object(
            self.g, "choose_player_target", return_value=self.p2
        ), patch.object(
            self.g,
            "choose_property_target",
            side_effect=[
                self.p2.properties[cards.PropertyColour.YELLOW].cards[0],
                self.p1.properties[cards.PropertyColour.RED].cards[0],
            ],
        ):
            self.g.play_forced_deal(self.p1)
        self.assertEqual(
            len(self.p1.properties[cards.PropertyColour.RED].cards), 0
        )
        self.assertEqual(
            len(self.p2.properties[cards.PropertyColour.RED].cards), 1
        )
        self.assertEqual(
            len(self.p2.properties[cards.PropertyColour.YELLOW].cards), 0
        )
        self.assertEqual(
            len(self.p1.properties[cards.PropertyColour.YELLOW].cards), 1
        )

    def test_forced_deal_target_no_properties(self):
        self.p2.properties = self.p2.empty_property_sets()
        with patch.object(
            self.g, "choose_player_target", return_value=self.p2
        ), self.assertRaises(game.window.InvalidChoiceError):
            self.g.play_forced_deal(self.p1)

    def test_forced_deal_source_no_properties(self):
        self.p1.properties = self.p1.empty_property_sets()
        with self.assertRaises(game.window.InvalidChoiceError):
            self.g.play_forced_deal(self.p1)


if __name__ == "__main__":
    unittest.main()
