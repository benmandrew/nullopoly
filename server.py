import argparse
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


class ServerNamespace(argparse.Namespace):
    deck: pathlib.Path  # Path to the deck file
    n_ai: int  # Number of AI players
    host: str
    port: int


def get_parser_args() -> ServerNamespace:
    parser = argparse.ArgumentParser(
        description="Run a server instance of Nullopoly.",
        epilog="Example usage: python server.py --n-ai 2 --deck custom_deck.json --host 127.0.0.1 --port 12345",  # noqa: E501, pylint: disable=line-too-long
    )
    parser.add_argument(
        "--deck",
        type=pathlib.Path,
        default=pathlib.Path("deck.json"),
        nargs="?",
        help="Path to the deck file (default: deck.json)",
    )
    parser.add_argument(
        "--n-ai",
        type=int,
        default=1,
        help="Number of AI players (default: 1)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=12345,
        help="Port number (default: 12345)",
    )
    return parser.parse_args(namespace=ServerNamespace())


def main() -> None:
    args = get_parser_args()
    setup_logging()
    players = [
        player.Player(
            "Ben",
            remote.RemoteInteraction(
                host=args.host,
                port=args.port,
            ),
        ),
    ]
    if args.n_ai > 0:
        players.extend(
            create_ai_player(f"AI {i + 1}") for i in range(args.n_ai)
        )
    g = game.Game(players, deck=args.deck, create_logger=True)
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
