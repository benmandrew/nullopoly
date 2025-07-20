from game import GameState
from card import print_cards_side_by_side


def main():
    game = GameState(["Alice", "Bob", "Charlie"], "deck.json")
    game.start()
    # for player in game.players:
    #     print(f"{player.state_string()}")

    cards = [game.draw_card() for _ in range(5)]
    print(print_cards_side_by_side(cards))


if __name__ == "__main__":
    main()
