import unittest
import cards
import game


class DummyCard(cards.Card):
    def name(self) -> str:
        return "Dummy"

    def value(self) -> int:
        return 1

    def card_type(self) -> str:
        return "dummy"


class TestGame(unittest.TestCase):
    def test_players_start_with_five_cards(self):
        # Fill the deck with enough dummy cards
        deck = [DummyCard() for _ in range(15)]
        g = game.Game(["Alice", "Bob", "Charlie"], deck)
        g.start()
        for player in g.players:
            self.assertEqual(len(player.hand), 5)


if __name__ == "__main__":
    unittest.main()
