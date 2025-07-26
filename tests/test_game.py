import unittest
from unittest.mock import Mock, patch

import cards
import game


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
            cards.PropertyCard("TestProperty", 2, cards.PropertyColour.RED)
        )
        self.player.add_property(
            cards.PropertyCard("TestProperty", 2, cards.PropertyColour.RED)
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
            self.assertEqual(len(money), 2)
            self.assertEqual(len(properties), 2)
            self.assertEqual(self.player.total_bank_value(), 0)
            self.assertEqual(len(self.player.properties_to_list()), 0)


if __name__ == "__main__":
    unittest.main()
