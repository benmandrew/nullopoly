import unittest

import utils

import cards


class TestDrawCardsSideBySide(unittest.TestCase):
    def test_draw_cards(self) -> None:
        deck: list[cards.Card] = [
            cards.PropertyCard("Park Lane", 4, cards.PropertyColour.DARK_BLUE),
            cards.ActionCard("Deal Breaker", 5, cards.ActionType.DEAL_BREAKER),
            cards.MoneyCard(5),
        ]
        output = utils.strip_and_join(cards.fmt_cards_side_by_side(deck))
        self.assertMultiLineEqual(
            output,
            utils.format_expect(
                """
            1.           2.              3.
            ┌───────────┐┌──────────────┐┌───────┐
            │ Park Lane ││ Deal Breaker ││ Money │
            │ Dark Blue ││              ││       │
            │ £4        ││ £5           ││ £5    │
            └───────────┘└──────────────┘└───────┘
        """
            ),
        )

    def test_draw_rent_wild_and_rent_card(self) -> None:
        rent_wild = cards.ActionCard("Rent Wild", 3, cards.ActionType.RENT_WILD)
        rent = cards.ActionCard(
            "Rent Green/Dark Blue", 7, cards.ActionType.RENT_GREEN_DARK_BLUE
        )
        deck: list[cards.Card] = [rent_wild, rent]
        output = utils.strip_and_join(cards.fmt_cards_side_by_side(deck))
        self.assertMultiLineEqual(
            output,
            utils.format_expect(
                """
            1.      2.
            ┌──────┐┌─────────────────┐
            │ Rent ││ Rent            │
            │ Wild ││ Green Dark Blue │
            │ £3   ││ £7              │
            └──────┘└─────────────────┘
        """
            ),
        )


if __name__ == "__main__":
    unittest.main()
