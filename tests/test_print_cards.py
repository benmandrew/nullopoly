import unittest
import card
import util


class TestPrintCardsSideBySide(unittest.TestCase):
    def test_print_five_cards(self):
        cards = [
            card.PropertyCard("Park Lane", 4, card.PropertyColour.DARK_BLUE),
            card.ActionCard("Deal Breaker", 5, card.ActionType.DEAL_BREAKER),
            card.MoneyCard(5),
        ]
        output = "\n".join(card.fmt_cards_side_by_side(cards))
        # The expected output will contain ANSI codes and box drawing characters.
        # For a robust test, strip ANSI codes and compare the visible layout.
        visible_output = util.strip_ansi(output)
        expected = (
            "1.           2.              3.       \n"
            "┌───────────┐┌──────────────┐┌───────┐\n"
            "│ Park Lane ││ Deal Breaker ││ Money │\n"
            "│ Dark Blue ││              ││       │\n"
            "│ £4        ││ £5           ││ £5    │\n"
            "└───────────┘└──────────────┘└───────┘"
        )
        self.assertMultiLineEqual(visible_output.strip(), expected.strip())


if __name__ == "__main__":
    unittest.main()
