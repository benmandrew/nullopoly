import unittest
from unittest.mock import Mock, patch

import cards
import game
from tests import utils


class TestGameStart(unittest.TestCase):
    def test_players_start_with_five_cards(self) -> None:
        mock_window = Mock()
        deck: list[cards.Card] = [cards.MoneyCard(1) for _ in range(15)]
        g = game.Game(["Alice", "Bob", "Charlie"], deck, mock_window)
        g.start()
        for player in g.players:
            self.assertEqual(len(player.hand), 5)


class TestPayments(unittest.TestCase):
    def setUp(self) -> None:
        mock_window = Mock()
        self.g = game.Game(["TestPlayer"], [], mock_window, starting_cards=0)
        self.g.start()
        self.player = self.g.get_player("TestPlayer")
        self.player.add_to_bank(cards.MoneyCard(5))
        self.player.add_to_bank(
            cards.ActionCard("DummyAction", 3, cards.ActionType.PASS_GO),
        )
        self.player.add_property(
            cards.PropertyCard("Property1", 2, cards.PropertyColour.RED),
        )
        self.player.add_property(
            cards.PropertyCard("Property2", 2, cards.PropertyColour.RED),
        )

    def test_get_payment_1(self) -> None:
        with patch.object(self.g.win, "get_number_input", side_effect=[]):
            money, properties = self.g.get_payment(self.player, 5)
            charged_cards = utils.strip_and_join(
                cards.fmt_cards_side_by_side(money + properties),
            )
            self.assertMultiLineEqual(
                charged_cards,
                utils.format_expect(
                    """
                1.
                ┌───────┐
                │ Money │
                │       │
                │ £5    │
                └───────┘
            """,
                ),
            )
            self.assertEqual(self.player.total_bank_value(), 3)
            self.assertEqual(len(self.player.properties_to_list()), 2)

    def test_get_payment_2(self) -> None:
        with patch.object(self.g.win, "get_number_input", side_effect=[1]):
            money, properties = self.g.get_payment(self.player, 10)
            charged_cards = utils.strip_and_join(
                cards.fmt_cards_side_by_side(money + properties),
            )
            self.assertMultiLineEqual(
                charged_cards,
                utils.format_expect(
                    """
                1.       2.         3.
                ┌───────┐┌─────────┐┌───────────┐
                │ Money ││ Pass Go ││ Property1 │
                │       ││         ││ Red       │
                │ £5    ││ £3      ││ £2        │
                └───────┘└─────────┘└───────────┘
            """,
                ),
            )
            self.assertEqual(self.player.total_bank_value(), 0)
            self.assertEqual(len(self.player.properties_to_list()), 1)

    def test_get_payment_3(self) -> None:
        with patch.object(self.g.win, "get_number_input", side_effect=[1, 1]):
            money, properties = self.g.get_payment(self.player, 20)
            charged_cards = utils.strip_and_join(
                cards.fmt_cards_side_by_side(money + properties),
            )
            self.assertMultiLineEqual(
                charged_cards,
                utils.format_expect(
                    """
                    1.       2.         3.           4.
                    ┌───────┐┌─────────┐┌───────────┐┌───────────┐
                    │ Money ││ Pass Go ││ Property1 ││ Property2 │
                    │       ││         ││ Red       ││ Red       │
                    │ £5    ││ £3      ││ £2        ││ £2        │
                    └───────┘└─────────┘└───────────┘└───────────┘
                """,
                ),
            )
            self.assertEqual(self.player.total_bank_value(), 0)
            self.assertEqual(len(self.player.properties_to_list()), 0)


class TestGameWinCondition(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_window = Mock()
        self.g = game.Game(["P1", "P2"], [], self.mock_window, starting_cards=0)
        self.g.start()
        self.p1 = self.g.get_player("P1")
        self.p2 = self.g.get_player("P2")

    def test_no_player_has_won(self) -> None:
        self.assertFalse(self.g.check_win())

    def test_player_has_won(self) -> None:
        # Complete three sets for P1
        for _ in range(2):
            self.p1.add_property(
                cards.PropertyCard("Brown", 1, cards.PropertyColour.BROWN),
            )
        for _ in range(3):
            self.p1.add_property(
                cards.PropertyCard("Red", 1, cards.PropertyColour.RED),
            )
        for _ in range(2):
            self.p1.add_property(
                cards.PropertyCard(
                    "Dark Blue",
                    1,
                    cards.PropertyColour.DARK_BLUE,
                ),
            )
        self.assertTrue(self.g.check_win())


if __name__ == "__main__":
    unittest.main()
