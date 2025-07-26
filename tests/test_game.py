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

    def test_charge_payment_1(self):
        with patch("util.get_number_input", side_effect=[]):
            money, properties = self.g.charge_payment(self.player, 5)
            self.assertEqual(len(money), 1)
            self.assertEqual(len(properties), 0)
            self.assertEqual(self.player.total_bank_value(), 3)
            self.assertEqual(len(self.player.properties_to_list()), 2)

    def test_charge_payment_2(self):
        with patch("util.get_number_input", side_effect=[1]):
            money, properties = self.g.charge_payment(self.player, 10)
            self.assertEqual(len(money), 2)
            self.assertEqual(len(properties), 1)
            self.assertEqual(self.player.total_bank_value(), 0)
            self.assertEqual(len(self.player.properties_to_list()), 1)

    def test_charge_payment_3(self):
        with patch("util.get_number_input", side_effect=[1, 1]):
            money, properties = self.g.charge_payment(self.player, 20)
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

    # def test_debt_collector(self):
    #     action_card = cards.ActionCard(
    #         "Debt Collector", 3, cards.ActionType.DEBT_COLLECTOR
    #     )
    #     with patch.object(
    #         self.g, "choose_player_target", return_value=self.p2
    #     ), patch("util.get_number_input", return_value=1):
    #         self.g.play_action_card(action_card, self.p1)
    #     self.assertEqual(self.p2.total_bank_value(), 5)

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
        with patch("util.get_number_input", return_value=1):
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


if __name__ == "__main__":
    unittest.main()
