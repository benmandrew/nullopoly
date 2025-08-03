import json
import logging.config
import pathlib

import game
import player
from interaction import ai, dummy, remote
from window import common

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    config_file = pathlib.Path("log_config.json")
    with config_file.open(encoding="utf-8") as f:
        config = json.load(f)
    logging.config.dictConfig(config)


HOST = "127.0.0.1"
PORT = 12345


def game_loop(g: game.Game) -> game.Game:
    current_player = g.current_player()
    g.deal_to_player(current_player, 2)
    n_cards_played = 0
    while n_cards_played < 3:
        g.draw(n_cards_played)
        try:
            c = g.choose_card_in_hand(current_player)
            g.play_card(c, current_player)
        except common.InvalidChoiceError:
            continue
        n_cards_played += 1
        current_player.remove_card_from_hand(c)
        if not current_player.hand:
            g.deal_from_empty(current_player)
        if g.check_win():
            raise game.WonError
    g.draw(n_cards_played)
    return g


def set_ai_game_instances(players: list[player.Player], g: game.Game) -> None:
    for p in players:
        if isinstance(p.inter, ai.AIInteraction):
            p.inter.set_game_instance(g)


def set_remote_player_indexes(players: list[player.Player]) -> None:
    for p in players:
        if isinstance(p.inter, remote.RemoteInteraction):
            assert p.inter.index is not None, "Remote player index must be set"
            p.index = p.inter.index


def create_ai_player(name: str) -> player.Player:
    p = player.Player(
        name,
        dummy.DummyInteraction(),
    )
    inter = ai.AIInteraction(p.index)
    p.inter = inter
    return p


def main() -> None:
    setup_logging()
    players = [
        player.Player(
            "Ben",
            remote.RemoteInteraction(
                host=HOST,
                port=PORT,
            ),
        ),
        create_ai_player("AI"),
    ]
    g = game.Game(players, deck="deck.json", create_logger=True)
    set_ai_game_instances(players, g)
    g.start()
    while True:
        try:
            g = game_loop(g)
        except game.WonError:
            break
        g.end_turn()


if __name__ == "__main__":
    main()
