import random

from player import PlayerState
from card import Card
import parse_deck


class GameState:
    def __init__(self, player_names: list[str], deck: str | list[Card]):
        self.players: list[PlayerState] = [
            PlayerState(name) for name in player_names
        ]
        if isinstance(deck, str):
            self.deck: list[Card] = parse_deck.from_json(deck)
        else:
            assert isinstance(
                deck, list
            ), "Deck must be a string or a list of Card objects"
            assert all(
                isinstance(card, Card) for card in deck
            ), "All items in deck must be Card objects"
            self.deck = deck
        self.current_player_index: int = 0
        self.current_turn: int = 0
        self.game_over: bool = False
        self.discard_pile: list[Card] = []

    def start(self) -> None:
        random.shuffle(self.deck)
        for player in self.players:
            self.deal_from_empty(player)

    def deal_from_empty(self, player: PlayerState) -> None:
        assert len(player.hand) == 0, "Player hand is not empty"
        self.deal_to_player(player, 5)

    def deal_to_player(self, player: PlayerState, count: int) -> None:
        assert count > 0, "Count must be positive"
        for _ in range(count):
            player.add_to_hand(self.draw_card())

    def next_player(self) -> PlayerState:
        self.current_player_index = (self.current_player_index + 1) % len(
            self.players
        )
        return self.players[self.current_player_index]

    def current_player(self) -> PlayerState:
        return self.players[self.current_player_index]

    def end_turn(self) -> None:
        self.current_turn += 1
        self.next_player()

    def get_player(self, name: str) -> PlayerState | None:
        for player in self.players:
            if player.name == name:
                return player
        return None

    def add_card_to_deck(self, card: Card) -> None:
        self.deck.append(card)

    def draw_card(self) -> Card:
        if not self.deck:
            self.deck = self.discard_pile
            self.discard_pile = []
            if not self.deck:
                raise RuntimeError("No cards left to draw.")
            random.shuffle(self.deck)
        return self.deck.pop()

    def discard_card(self, card: Card) -> None:
        self.discard_pile.append(card)
