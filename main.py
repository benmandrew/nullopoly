from game import GameState


def main():
    # game = GameState(["Alice", "Bob", "Charlie"], "deck.json")
    game = GameState(["Alice"], "deck.json")
    game.start()

    while True:
        current_player = game.current_player()
        game.deal_to_player(current_player, 2)
        for i in range(3):
            print(current_player.fmt_state())
            print(f"{3 - i} cards left to play this turn.")
            choice = int(
                input(
                    f"Which card do you want to play? (1-{len(current_player.hand)})\n"
                )
            )
            assert 1 <= choice <= len(current_player.hand), "Invalid choice"
            current_player.play_card_from_hand(int(choice) - 1)
            if len(current_player.hand) == 0:
                game.deal_from_empty(current_player)
        game.end_turn()


if __name__ == "__main__":
    main()
