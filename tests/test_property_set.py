import unittest

import cards
import player


class TestPropertySet(unittest.TestCase):
    def test_add_and_remove(self):
        prop_set = player.PropertySet(cards.PropertyColour.BROWN, 2)
        prop_card = cards.PropertyCard(
            "Old Kent Road", 1, cards.PropertyColour.BROWN
        )
        prop_set.add(prop_card)
        self.assertEqual(prop_set.count(), 1)
        prop_set.remove(prop_card)
        self.assertEqual(prop_set.count(), 0)

    def test_is_complete(self):
        prop_set = player.PropertySet(cards.PropertyColour.BROWN, 2)
        prop_card1 = cards.PropertyCard(
            "Old Kent Road", 1, cards.PropertyColour.BROWN
        )
        prop_card2 = cards.PropertyCard(
            "Whitechapel Road", 1, cards.PropertyColour.BROWN
        )
        prop_set.add(prop_card1)
        prop_set.add(prop_card2)
        self.assertTrue(prop_set.is_complete())


if __name__ == "__main__":
    unittest.main()
