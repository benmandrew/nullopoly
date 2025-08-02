import cards
import player
from interaction import interaction


class DummyInteraction(interaction.Interaction):
    def choose_card_in_hand(self, p: player.Player) -> cards.Card:
        raise NotImplementedError

    def choose_full_set_target(
        self,
        target: player.Player,
    ) -> player.PropertySet:
        raise NotImplementedError

    def choose_property_source(
        self,
        me: player.Player,
        without_full_sets: bool = False,
    ) -> cards.PropertyCard:
        properties = me.properties_to_list(
            without_full_sets=without_full_sets,
        )
        assert properties, "No properties available to choose from"
        return min(properties, key=lambda prop: prop.value)

    def choose_property_target(
        self,
        target: player.Player,
        without_full_sets: bool = False,
    ) -> cards.PropertyCard:
        properties = target.properties_to_list(
            without_full_sets=without_full_sets,
        )
        assert properties, "No properties available to choose from"
        return max(properties, key=lambda prop: prop.value)

    def choose_player_target(
        self,
        players: list[player.Player],
    ) -> player.Player:
        raise NotImplementedError

    def choose_action_usage(self) -> int:
        raise NotImplementedError

    def choose_rent_colour_and_amount(
        self,
        owned_colours_with_rents: list[tuple[cards.PropertyColour, int]],
    ) -> tuple[cards.PropertyColour, int]:
        raise NotImplementedError

    def log(self, message: str) -> None:
        pass

    def notify_draw_my_turn(
        self,
        current_player: player.Player,
        players: list[player.Player],
        n_cards_played: int,
    ) -> None:
        raise NotImplementedError

    def notify_draw_other_turn(self, players: list[player.Player]) -> None:
        raise NotImplementedError

    def notify_turn_over(self, next_player_name: str) -> None:
        raise NotImplementedError

    def notify_game_over(self) -> None:
        raise NotImplementedError
