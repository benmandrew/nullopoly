from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import cards

if TYPE_CHECKING:
    import player


class Interaction(ABC):
    """Base class for player interactions."""

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def choose_card_in_hand(self, p: "player.Player") -> cards.Card:
        """Choose a card from the player's hand."""

    @abstractmethod
    def choose_full_set_target(
        self,
        target: "player.Player",
    ) -> "player.PropertySet":
        """Choose a full property set from the target player's properties."""

    @abstractmethod
    def choose_property_target(
        self,
        target: "player.Player",
        without_full_sets: bool = False,
    ) -> cards.PropertyCard:
        """Choose a property card from the target player's hand."""

    @abstractmethod
    def choose_player_target(
        self,
        players: list["player.Player"],
    ) -> "player.Player":
        """Choose a target player from the list of players."""

    @abstractmethod
    def choose_action_usage(self) -> int:
        """Choose how to use an action card.
        1 for playing the action, 2 for adding to bank.
        """

    @abstractmethod
    def choose_rent_colour_and_amount(
        self,
        owned_colours_with_rents: list[tuple[cards.PropertyColour, int]],
    ) -> tuple[cards.PropertyColour, int]:
        """Choose the colour and amount of rent to charge."""

    @abstractmethod
    def log(self, message: str) -> None:
        """Log a message to the player."""

    @abstractmethod
    def notify_draw_my_turn(
        self,
        current_player: "player.Player",
        players: list["player.Player"],
        n_cards_played: int,
    ) -> None:
        """Notify the player that they should draw the window for their turn."""

    @abstractmethod
    def notify_draw_other_turn(self, players: list["player.Player"]) -> None:
        """Notify the player that they should draw the window
        for another player's turn.
        """

    @abstractmethod
    def notify_turn_over(self, next_player_name: str) -> None:
        """Notify the player that their turn is over."""

    @abstractmethod
    def notify_game_over(self) -> None:
        """Notify the player that the game is over."""
