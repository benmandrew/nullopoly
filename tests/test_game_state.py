import unittest
import card
from game import GameState


class DummyCard(card.Card):
    def name(self) -> str:
        return "Dummy"

    def value(self) -> int:
        return 1

    def card_type(self) -> str:
        return "dummy"


class TestGameState(unittest.TestCase):
    def test_players_start_with_five_cards(self):
        player_names = ["Alice", "Bob", "Charlie"]
        # Fill the deck with enough dummy cards
        deck = [DummyCard() for _ in range(15)]
        game_state = GameState(player_names, deck)
        game_state.start()
        for player in game_state.players:
            self.assertEqual(len(player.hand), 5)


if __name__ == "__main__":
    unittest.main()
