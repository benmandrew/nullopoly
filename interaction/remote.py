from __future__ import annotations

import json
import socket
import uuid
from typing import TYPE_CHECKING

import cards
from interaction import interaction

if TYPE_CHECKING:
    import player


class RemoteInteraction(interaction.Interaction):
    """Interaction class for remote player using a network connection."""

    def __init__(
        self,
        host: str,
        port: int,
    ) -> None:
        self.host = host
        self.port = port
        self.sock: socket.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        self.conn: socket.socket
        self.index: uuid.UUID
        self.conn, self.index = self.open_connection()

    def open_connection(self) -> tuple[socket.socket, uuid.UUID]:
        """Opens a connection to the remote player."""
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        conn, _ = self.sock.accept()
        index = conn.recv(1024).decode("utf-8")
        return conn, uuid.UUID(hex=index)

    def close_connection(self) -> None:
        """Closes the connection to the remote player."""
        if self.sock:
            self.sock.close()
        if self.conn is not None:
            self.conn.close()
            del self.conn

    def choose_card_in_hand(self, p: player.Player) -> cards.Card:
        assert self.conn is not None, "There is no active connection"
        self.conn.sendall(b"choose_card_in_hand/")
        data = self.conn.recv(1024)
        i = int.from_bytes(data, "big")
        assert 1 <= i <= len(p.hand), "Invalid card index"
        return p.hand[i - 1]

    def choose_full_set_target(
        self,
        target: player.Player,
    ) -> player.PropertySet:
        assert self.conn is not None, "There is no active connection"
        full_sets = [
            prop for prop in target.properties.values() if prop.is_complete()
        ]
        self.conn.sendall(b"choose_full_set_target/")
        data = self.conn.recv(1024)
        i = int.from_bytes(data, "big")
        assert 1 <= i <= len(full_sets), "Invalid full set index"
        return full_sets[i - 1]

    def choose_property_target(
        self,
        target: player.Player,
        without_full_sets: bool = False,
    ) -> cards.PropertyCard:
        assert self.conn is not None, "There is no active connection"
        properties = target.properties_to_list(without_full_sets)
        self.conn.sendall(b"choose_property_target/")
        data = self.conn.recv(1024)
        i = int.from_bytes(data, "big")
        assert 1 <= i <= len(properties), "Invalid property index"
        return properties[i - 1]

    def choose_property_source(
        self,
        me: player.Player,
        without_full_sets: bool = False,
    ) -> cards.PropertyCard:
        assert self.conn is not None, "There is no active connection"
        properties = me.properties_to_list(without_full_sets)
        self.conn.sendall(b"choose_property_source/")
        data = self.conn.recv(1024)
        i = int.from_bytes(data, "big")
        assert 1 <= i <= len(properties), "Invalid property index"
        return properties[i - 1]

    def choose_player_target(
        self,
        players: list[player.Player],
    ) -> player.Player:
        assert self.conn is not None, "There is no active connection"
        self.conn.sendall(b"choose_player_target/")
        data = self.conn.recv(1024)
        i = int.from_bytes(data, "big")
        assert 1 <= i <= len(players), "Invalid player index"
        return players[i - 1]

    def choose_action_usage(self) -> int:
        assert self.conn is not None, "There is no active connection"
        self.conn.sendall(b"choose_action_usage/")
        data = self.conn.recv(1024)
        i = int.from_bytes(data, "big")
        assert 1 <= i <= 2, "Invalid action usage choice"
        return i

    def choose_rent_colour_and_amount(
        self,
        owned_colours_with_rents: list[tuple[cards.PropertyColour, int]],
    ) -> tuple[cards.PropertyColour, int]:
        assert self.conn is not None, "There is no active connection"
        self.conn.sendall(b"choose_rent_colour_and_amount/")
        data = self.conn.recv(1024)
        i = int.from_bytes(data, "big")
        assert (
            1 <= i <= len(owned_colours_with_rents)
        ), "Invalid rent/colour index"
        return owned_colours_with_rents[i - 1]

    def log(self, message: str) -> None:
        assert self.conn is not None, "There is no active connection"
        self.conn.sendall(b"log/")
        self.conn.sendall(message.encode("utf-8"))
        self.conn.sendall(b"/")

    def notify_draw_my_turn(
        self,
        current_player: player.Player,
        players: list[player.Player],
        n_cards_played: int,
    ) -> None:
        assert self.conn is not None, "There is no active connection"
        visible_players = [p.to_json() for p in players if p != self]
        data = {
            "current_player": current_player.to_json(),
            "players": visible_players,
            "n_cards_played": n_cards_played,
        }
        self.conn.sendall(b"notify_draw_my_turn/")
        self.conn.sendall(json.dumps(data).encode("utf-8"))
        self.conn.sendall(b"/")

    def notify_draw_other_turn(self, players: list[player.Player]) -> None:
        assert self.conn is not None, "There is no active connection"
        visible_players = [p.to_json() for p in players if p != self]
        data = {
            "players": visible_players,
        }
        self.conn.sendall(b"notify_draw_other_turn/")
        self.conn.sendall(json.dumps(data).encode("utf-8"))
        self.conn.sendall(b"/")

    def notify_turn_over(self, _next_player_name: str) -> None:
        assert self.conn is not None, "There is no active connection"
        self.conn.sendall(b"notify_turn_over/")

    def notify_game_over(self) -> None:
        assert self.conn is not None, "There is no active connection"
        self.conn.sendall(b"notify_game_over/")
