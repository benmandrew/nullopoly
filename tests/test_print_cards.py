import unittest
import card


class TestPrintCardsSideBySide(unittest.TestCase):
    def test_print_five_cards(self):
        cards = [
            card.PropertyCard("Park Lane", 4, card.PropertyColour.DARK_BLUE),
            card.ActionCard("Deal Breaker", 5, card.ActionType.DEAL_BREAKER),
            card.MoneyCard(5),
        ]
        output = card.print_cards_side_by_side(cards)
        # The expected output will contain ANSI codes and box drawing characters.
        # For a robust test, strip ANSI codes and compare the visible layout.
        visible_output = card.strip_ansi(output)
        expected = (
            "┌───────────┐┌──────────────┐┌───────┐\n"
            "│ Park Lane ││ Deal Breaker ││ Money │\n"
            "│ Dark Blue ││ £5           ││ £5    │\n"
            "│ £4        │└──────────────┘└───────┘\n"
            "└───────────┘"
        )
        self.assertMultiLineEqual(visible_output.strip(), expected.strip())


if __name__ == "__main__":
    unittest.main()
