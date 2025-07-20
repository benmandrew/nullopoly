import unittest
import card
from player import PropertySet


class TestPropertySet(unittest.TestCase):
    def test_add_and_remove(self):
        prop_set = PropertySet(card.PropertyColour.BROWN, 2)
        prop_card = card.PropertyCard(
            "Old Kent Road", 1, card.PropertyColour.BROWN
        )
        prop_set.add(prop_card)
        self.assertEqual(prop_set.count(), 1)
        prop_set.remove(prop_card)
        self.assertEqual(prop_set.count(), 0)

    def test_is_complete(self):
        prop_set = PropertySet(card.PropertyColour.BROWN, 2)
        prop_card1 = card.PropertyCard(
            "Old Kent Road", 1, card.PropertyColour.BROWN
        )
        prop_card2 = card.PropertyCard(
            "Whitechapel Road", 1, card.PropertyColour.BROWN
        )
        prop_set.add(prop_card1)
        prop_set.add(prop_card2)
        self.assertTrue(prop_set.is_complete())


if __name__ == "__main__":
    unittest.main()
