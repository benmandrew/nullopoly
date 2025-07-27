import unittest

import cards


class TestDrawCardsSideBySide(unittest.TestCase):
    def test_draw_five_cards(self):
        deck = [
            cards.PropertyCard("Park Lane", 4, cards.PropertyColour.DARK_BLUE),
            cards.ActionCard("Deal Breaker", 5, cards.ActionType.DEAL_BREAKER),
            cards.MoneyCard(5),
        ]
        output = "\n".join(cards.fmt_cards_side_by_side(deck))
        expected = (
            "1.           2.              3.       \n"
            "┌───────────┐┌──────────────┐┌───────┐\n"
            "│ Park Lane ││ Deal Breaker ││ Money │\n"
            "│ Dark Blue ││              ││       │\n"
            "│ £4        ││ £5           ││ £5    │\n"
            "└───────────┘└──────────────┘└───────┘"
        )
        self.assertMultiLineEqual(output.strip(), expected.strip())


if __name__ == "__main__":
    unittest.main()
