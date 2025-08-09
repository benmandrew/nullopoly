import unittest
from unittest.mock import Mock

import cards
import player


class TestChargeMoneyPayment(unittest.TestCase):
    def setUp(self) -> None:
        mock_interaction = Mock()
        self.p = player.Player("Test", mock_interaction)

    def test_exact_payment(self) -> None:
        self.p.add_to_bank(cards.MoneyCard(5))
        paid, remaining = self.p.charge_money_payment(5)
        self.assertEqual(sum(c.value for c in paid), 5)
        self.assertEqual(remaining, 0)
        self.assertEqual(len(self.p.bank), 0)

    def test_overpayment_minimized(self) -> None:
        self.p.add_to_bank(cards.MoneyCard(2))
        self.p.add_to_bank(cards.MoneyCard(3))
        self.p.add_to_bank(cards.MoneyCard(5))
        paid, remaining = self.p.charge_money_payment(4)
        # Should pay 5 (not 2+3=5, but 5 is the only single card >=4)
        self.assertEqual(sum(c.value for c in paid), 5)
        self.assertEqual(remaining, 0)
        self.assertEqual(len(self.p.bank), 2)

    def test_multiple_cards(self) -> None:
        self.p.add_to_bank(cards.MoneyCard(1))
        self.p.add_to_bank(cards.MoneyCard(2))
        self.p.add_to_bank(cards.MoneyCard(2))
        paid, remaining = self.p.charge_money_payment(3)
        self.assertEqual(sum(c.value for c in paid), 3)
        self.assertEqual(remaining, 0)
        self.assertEqual(len(self.p.bank), 1)

    def test_insufficient_funds(self) -> None:
        self.p.add_to_bank(cards.MoneyCard(2))
        self.p.add_to_bank(cards.MoneyCard(1))
        paid, remaining = self.p.charge_money_payment(10)
        self.assertEqual(sum(c.value for c in paid), 3)
        self.assertEqual(remaining, 7)
        self.assertEqual(len(self.p.bank), 0)

    def test_action_card_in_bank(self) -> None:
        self.p.add_to_bank(cards.MoneyCard(2))
        self.p.add_to_bank(cards.ActionCard("A", 3, cards.ActionType.PASS_GO))
        paid, remaining = self.p.charge_money_payment(3)
        self.assertEqual(sum(c.value for c in paid), 3)
        self.assertEqual(remaining, 0)
        self.assertEqual(len(self.p.bank), 1)


if __name__ == "__main__":
    unittest.main()
