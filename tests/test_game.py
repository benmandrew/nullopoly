import unittest
from unittest.mock import Mock, patch

import cards
import game
import player
from tests import utils


class TestGameStart(unittest.TestCase):
    def test_players_start_with_five_cards(self) -> None:
        deck: list[cards.Card] = [cards.MoneyCard(1) for _ in range(15)]
        mock_interaction = Mock()
        players = [
            player.Player(name, mock_interaction)
            for name in ["Alice", "Bob", "Charlie"]
        ]
        g = game.Game(players, deck)
        g.start()
        for p in g.players:
            self.assertEqual(len(p.hand), 5)


class TestPayments(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_interaction = Mock()
        players = [
            player.Player(name, self.mock_interaction)
            for name in ["TestPlayer"]
        ]
        self.g = game.Game(players, [], starting_cards=0)
        self.g.start()
        self.player = self.g.get_player_by_name("TestPlayer")
        self.player.add_to_bank(cards.MoneyCard(5))
        self.player.add_to_bank(
            cards.ActionCard("DummyAction", 3, cards.ActionType.PASS_GO),
        )
        self.property1 = cards.PropertyCard(
            "Property1",
            2,
            cards.PropertyColour.RED,
        )
        self.property2 = cards.PropertyCard(
            "Property2",
            2,
            cards.PropertyColour.RED,
        )
        self.player.add_property(self.property1)
        self.player.add_property(self.property2)

    def test_get_payment_1(self) -> None:
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
        with patch.object(
            self.mock_interaction,
            "choose_property_source",
            side_effect=[self.property1],
        ):
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
        with patch.object(
            self.mock_interaction,
            "choose_property_source",
            side_effect=[self.property1, self.property2],
        ):
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
        self.mock_interaction = Mock()
        players = [
            player.Player(name, self.mock_interaction) for name in ["P1", "P2"]
        ]
        self.g = game.Game(players, [], starting_cards=0)
        self.g.start()
        self.p1 = self.g.get_player_by_name("P1")
        self.p2 = self.g.get_player_by_name("P2")

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
