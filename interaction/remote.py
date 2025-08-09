from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING

from interaction import interaction

if TYPE_CHECKING:
    import socket

    import cards
    import player


class RemoteInteraction(interaction.Interaction):
    """Interaction class for remote player using a network connection."""

    def __init__(
        self,
        sock: socket.socket,
    ) -> None:
        self.sock: socket.socket = sock
        name_and_index = self.sock.recv(1024).decode("utf-8").split("/", 1)
        self.name = name_and_index[0]
        self.index = uuid.UUID(hex=name_and_index[1])

    def close_connection(self) -> None:
        """Closes the connection to the remote player."""
        if self.sock:
            self.sock.close()
        if self.sock is not None:
            self.sock.close()
            del self.sock

    def choose_card_in_hand(self, p: player.Player) -> cards.Card:
        assert self.sock is not None, "There is no active connection"
        self.sock.sendall(b"choose_card_in_hand/")
        data = self.sock.recv(1024)
        i = int.from_bytes(data, "big")
        assert 1 <= i <= len(p.hand), "Invalid card index"
        return p.hand[i - 1]

    def choose_full_set_target(
        self,
        target: player.Player,
    ) -> player.PropertySet:
        assert self.sock is not None, "There is no active connection"
        full_sets = [
            prop for prop in target.properties.values() if prop.is_complete()
        ]
        self.sock.sendall(b"choose_full_set_target/")
        data = self.sock.recv(1024)
        i = int.from_bytes(data, "big")
        assert 1 <= i <= len(full_sets), "Invalid full set index"
        return full_sets[i - 1]

    def choose_property_target(
        self,
        target: player.Player,
        without_full_sets: bool = False,
    ) -> cards.PropertyCard:
        assert self.sock is not None, "There is no active connection"
        properties = target.properties_to_list(without_full_sets)
        self.sock.sendall(b"choose_property_target/")
        data = self.sock.recv(1024)
        i = int.from_bytes(data, "big")
        assert 1 <= i <= len(properties), "Invalid property index"
        return properties[i - 1]

    def choose_property_source(
        self,
        me: player.Player,
        without_full_sets: bool = False,
    ) -> cards.PropertyCard:
        assert self.sock is not None, "There is no active connection"
        properties = me.properties_to_list(without_full_sets)
        self.sock.sendall(b"choose_property_source/")
        data = self.sock.recv(1024)
        i = int.from_bytes(data, "big")
        assert 1 <= i <= len(properties), "Invalid property index"
        return properties[i - 1]

    def choose_player_target(
        self,
        players: list[player.Player],
    ) -> player.Player:
        assert self.sock is not None, "There is no active connection"
        self.sock.sendall(b"choose_player_target/")
        data = self.sock.recv(1024)
        i = int.from_bytes(data, "big")
        assert 1 <= i <= len(players), "Invalid player index"
        return players[i - 1]

    def choose_action_usage(self) -> int:
        assert self.sock is not None, "There is no active connection"
        self.sock.sendall(b"choose_action_usage/")
        data = self.sock.recv(1024)
        i = int.from_bytes(data, "big")
        assert 1 <= i <= 2, "Invalid action usage choice"
        return i

    def choose_rent_colour_and_amount(
        self,
        owned_colours_with_rents: list[tuple[cards.PropertyColour, int]],
    ) -> tuple[cards.PropertyColour, int]:
        assert self.sock is not None, "There is no active connection"
        self.sock.sendall(b"choose_rent_colour_and_amount/")
        data = self.sock.recv(1024)
        i = int.from_bytes(data, "big")
        assert (
            1 <= i <= len(owned_colours_with_rents)
        ), "Invalid rent/colour index"
        return owned_colours_with_rents[i - 1]

    def log(self, message: str) -> None:
        assert self.sock is not None, "There is no active connection"
        self.sock.sendall(b"log/")
        self.sock.sendall(message.encode("utf-8"))
        self.sock.sendall(b"/")

    def notify_draw_my_turn(
        self,
        current_player: player.Player,
        players: list[player.Player],
        n_cards_played: int,
    ) -> None:
        assert self.sock is not None, "There is no active connection"
        visible_players = [p.to_json() for p in players if p != self]
        data = {
            "current_player": current_player.to_json(),
            "players": visible_players,
            "n_cards_played": n_cards_played,
        }
        self.sock.sendall(b"notify_draw_my_turn/")
        self.sock.sendall(json.dumps(data).encode("utf-8"))
        self.sock.sendall(b"/")

    def notify_draw_other_turn(self, players: list[player.Player]) -> None:
        assert self.sock is not None, "There is no active connection"
        visible_players = [p.to_json() for p in players if p != self]
        data = {
            "players": visible_players,
        }
        self.sock.sendall(b"notify_draw_other_turn/")
        self.sock.sendall(json.dumps(data).encode("utf-8"))
        self.sock.sendall(b"/")

    def notify_turn_over(self, _next_player_name: str) -> None:
        assert self.sock is not None, "There is no active connection"
        self.sock.sendall(b"notify_turn_over/")

    def notify_game_over(self) -> None:
        assert self.sock is not None, "There is no active connection"
        self.sock.sendall(b"notify_game_over/")
