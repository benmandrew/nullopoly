import curses

import cards
import player
from interaction import interaction
from window import common, window


class LocalInteraction(interaction.Interaction):
    """Interaction class for local player using the UI."""

    def __init__(self, stdscr: curses.window, n_players: int) -> None:
        self.win = window.Window(stdscr, n_players)

    def update_n_players(self, n_players: int) -> None:
        """Update the number of players in the interaction."""
        self.win.update_n_players(n_players)

    def choose_card_in_hand(self, p: player.Player) -> cards.Card:
        choice = self.win.get_number_input(1, len(p.hand))
        return p.get_card_in_hand(choice - 1)

    def choose_full_set_target(
        self,
        target: player.Player,
    ) -> player.PropertySet:
        full_sets = [
            prop for prop in target.properties.values() if prop.is_complete()
        ]
        if not full_sets:
            msg = "Target player does not have a full set of properties"
            raise common.InvalidChoiceError(msg)
        self.win.hand.draw_target_full_set_dialog(target)
        choice = self.win.get_number_input(1, len(full_sets))
        return full_sets[choice - 1]

    def choose_property_target(
        self,
        target: player.Player,
        without_full_sets: bool = False,
    ) -> cards.PropertyCard:
        properties = target.properties_to_list(without_full_sets)
        if not properties:
            msg = "Target player has no properties to choose from"
            raise common.InvalidChoiceError(msg)
        self.win.hand.draw_target_property_dialog(
            target,
            without_full_sets=True,
        )
        choice = self.win.get_number_input(1, len(properties))
        return properties[choice - 1]

    def choose_property_source(
        self,
        me: player.Player,
        without_full_sets: bool = False,
    ) -> cards.PropertyCard:
        return self.choose_property_target(
            target=me,
            without_full_sets=without_full_sets,
        )

    def choose_player_target(
        self,
        players: list[player.Player],
    ) -> player.Player:
        if len(players) == 0:
            msg = "No players available to choose from"
            raise common.InvalidChoiceError(
                msg,
            )
        if len(players) == 1:
            return players[0]
        self.win.hand.draw_target_player_dialog(players)
        choice = self.win.get_number_input(1, len(players))
        return players[choice - 1]

    def choose_action_usage(self) -> int:
        """Choose how to use an action card.
        1 for playing the action, 2 for adding to bank.
        """
        self.win.hand.draw_action_dialog()
        return self.win.get_number_input(1, 2)

    def choose_rent_colour_and_amount(
        self,
        owned_colours_with_rents: list[tuple[cards.PropertyColour, int]],
    ) -> tuple[cards.PropertyColour, int]:
        """Choose the amount of rent to charge."""
        self.win.hand.draw_rent_colour_choice(owned_colours_with_rents)
        choice = self.win.get_number_input(1, len(owned_colours_with_rents))
        return owned_colours_with_rents[choice - 1]

    def log(self, message: str) -> None:
        """Log a message to the game window."""
        self.win.draw_log(message)

    def notify_draw_my_turn(
        self,
        current_player: player.Player,
        players: list[player.Player],
        n_cards_played: int,
    ) -> None:
        """Notify the player that they should draw the window for their turn."""
        self.win.draw_my_turn(current_player, players, n_cards_played)

    def notify_draw_other_turn(self, players: list[player.Player]) -> None:
        """Notify the player that they should draw the window
        for another player's turn.
        """
        self.win.draw_other_turn(players)

    def notify_turn_over(self, next_player_name: str) -> None:
        """Notify the player that their turn is over."""
        self.win.turn_over(next_player_name)

    def notify_game_over(self) -> None:
        """Notify the player that the game is over."""
        self.win.game_over()
        self.win.refresh()
