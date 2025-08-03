from __future__ import annotations

import argparse
import curses
import json
import signal
import socket
import sys
from dataclasses import dataclass
from types import FrameType
from typing import Any

import cards
import game
import player
from interaction import dummy, local


class ClientNamespace(argparse.Namespace):
    name: str  # Name of the player
    host: str
    port: int


def get_parser_args() -> ClientNamespace:
    parser = argparse.ArgumentParser(
        description="Run a client instance of Nullopoly.",
        epilog="Example usage: python client.py --name Ben --host 127.0.0.1 --port 12345",  # noqa: E501, pylint: disable=line-too-long
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Name of the player",
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
    return parser.parse_args(namespace=ClientNamespace())


class BlockReceiver:
    """A class to receive blocks of data separated by slashes."""

    def __init__(self, conn: socket.socket) -> None:
        self.conn = conn
        self.buffer = b""

    def receive_opt(self) -> str | None:
        while b"/" not in self.buffer:
            chunk = self.conn.recv(4096)
            if not chunk:
                return None
            self.buffer += chunk
        block, self.buffer = self.buffer.split(b"/", 1)
        return block.decode("utf-8")

    def receive(self) -> str:
        data = self.receive_opt()
        assert data is not None, "No data received"
        return data


DUMMY = dummy.DummyInteraction()


def game_from_json(data: dict[str, Any]) -> game.Game:
    players = [player.Player.from_json(p, DUMMY) for p in data["players"]]
    return game.Game(players, deck=[])


def choose_card_in_hand(
    c: ClientState,
    inter: local.LocalInteraction,
    s: socket.socket,
) -> ClientState:
    card = inter.choose_card_in_hand(c.me)
    if isinstance(card, cards.ActionCard) and cards.is_rent_action(
        card.action,
    ):
        c.colour_options = cards.RENT_CARD_COLOURS[card.action]
    s.sendall(int.to_bytes(c.me.hand.index(card) + 1, 1, "big"))
    return c


def choose_full_set_target(
    c: ClientState,
    inter: local.LocalInteraction,
    s: socket.socket,
) -> None:
    assert c.target is not None, "Target player is not set"
    full_sets = [
        prop for prop in c.target.properties.values() if prop.is_complete()
    ]
    full_set = inter.choose_full_set_target(c.target)
    s.sendall(int.to_bytes(full_sets.index(full_set) + 1, 1, "big"))


def choose_property_target(
    c: ClientState,
    inter: local.LocalInteraction,
    s: socket.socket,
) -> None:
    assert c.target is not None, "Target player is not set"
    prop = inter.choose_property_target(c.target)
    properties = c.target.properties_to_list()
    s.sendall(int.to_bytes(properties.index(prop) + 1, 1, "big"))


def choose_property_source(
    c: ClientState,
    inter: local.LocalInteraction,
    s: socket.socket,
) -> None:
    prop = inter.choose_property_source(c.me)
    properties = c.me.properties_to_list()
    s.sendall(int.to_bytes(properties.index(prop) + 1, 1, "big"))


def choose_player_target(
    c: ClientState,
    inter: local.LocalInteraction,
    s: socket.socket,
) -> ClientState:
    excluded_players = [p for p in c.g.players if p != c.me]
    c.target = inter.choose_player_target(excluded_players)
    s.sendall(
        int.to_bytes(excluded_players.index(c.target) + 1, 1, "big"),
    )
    return c


def choose_rent_colour_and_amount(
    c: ClientState,
    inter: local.LocalInteraction,
    s: socket.socket,
) -> None:
    assert c.colour_options, "No colour options available"
    owned_colours_with_rents = c.me.owned_colours_with_rents(
        c.colour_options,
    )
    colour_choice = inter.choose_rent_colour_and_amount(
        owned_colours_with_rents,
    )
    s.sendall(
        int.to_bytes(
            owned_colours_with_rents.index(colour_choice) + 1,
            1,
            "big",
        ),
    )


def notify_draw_my_turn(
    inter: local.LocalInteraction,
    block_receiver: BlockReceiver,
) -> game.Game:
    data_dict = json.loads(block_receiver.receive())
    n_players = len(data_dict["players"])
    if n_players != inter.win.n_players:
        inter.win.update_n_players(n_players)
    current_player = player.Player.from_json(
        data_dict["current_player"],
        DUMMY,
    )
    inter.notify_draw_my_turn(
        current_player=current_player,
        players=[
            player.Player.from_json(p, DUMMY) for p in data_dict["players"]
        ],
        n_cards_played=int(data_dict["n_cards_played"]),
    )
    return game_from_json(data_dict)


def notify_draw_other_turn(
    inter: local.LocalInteraction,
    block_receiver: BlockReceiver,
) -> game.Game:
    data = block_receiver.receive()
    assert data is not None, "No data received"
    data_dict = json.loads(data)
    n_players = len(data_dict["players"])
    if n_players != inter.win.n_players:
        inter.win.update_n_players(n_players)
    inter.notify_draw_other_turn(
        players=[
            player.Player.from_json(p, DUMMY) for p in data_dict["players"]
        ],
    )
    return game_from_json(data_dict)


@dataclass
class ClientState:
    g: game.Game
    me: player.Player
    target: player.Player | None
    colour_options: list[cards.PropertyColour]


def game_loop(
    c: ClientState,
    inter: local.LocalInteraction,
    block_receiver: BlockReceiver,
    s: socket.socket,
) -> ClientState:
    data = block_receiver.receive_opt()
    if data is None:
        return c
    if data == "notify_draw_my_turn":
        c.g = notify_draw_my_turn(inter, block_receiver)
        c.me = c.g.current_player()
    elif data == "notify_draw_other_turn":
        c.g = notify_draw_other_turn(inter, block_receiver)
    elif data == "choose_card_in_hand":
        c = choose_card_in_hand(c, inter, s)
    elif data == "choose_full_set_target":
        choose_full_set_target(c, inter, s)
    elif data == "choose_property_target":
        choose_property_target(c, inter, s)
    elif data == "choose_property_source":
        choose_property_source(c, inter, s)
    elif data == "choose_player_target":
        c = choose_player_target(c, inter, s)
    elif data == "choose_action_usage":
        choice = inter.choose_action_usage()
        s.sendall(int.to_bytes(choice, 1, "big"))
    elif data == "choose_rent_colour_and_amount":
        choose_rent_colour_and_amount(c, inter, s)
    elif data == "log":
        message = block_receiver.receive()
        inter.log(message)
    return c


def run_game(stdscr: curses.window, args: ClientNamespace) -> None:
    g: game.Game = game.Game(
        [],
        deck=[],
    )
    me: player.Player = player.Player(
        args.name,
        DUMMY,
    )
    inter = local.LocalInteraction(stdscr, n_players=1)
    target: player.Player | None = None
    colour_options: list[cards.PropertyColour] = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((args.host, args.port))
        block_receiver = BlockReceiver(s)
        s.sendall(str(me.index).encode("utf-8"))
        c = ClientState(
            g,
            me,
            target,
            colour_options,
        )
        while True:
            c = game_loop(
                c,
                inter,
                block_receiver,
                s,
            )


def curses_exit() -> None:
    curses.curs_set(1)  # Show the cursor again
    curses.endwin()


def curses_main(stdscr: curses.window) -> None:
    args = get_parser_args()
    curses.start_color()
    curses.curs_set(0)  # Hide the cursor
    try:
        run_game(stdscr, args)
    except Exception:
        curses_exit()
        raise


def signal_handler(_sig: int, _frame: FrameType | None) -> None:
    curses_exit()
    sys.exit(0)


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        get_parser_args()
    else:
        signal.signal(signal.SIGINT, signal_handler)
        curses.wrapper(curses_main)
