from __future__ import annotations

import itertools
from copy import deepcopy
from dataclasses import dataclass

import cards
import game
import player
from interaction import interaction


@dataclass(frozen=True)
class Plan:
    pass


@dataclass(frozen=True)
class PropertyPlan(Plan):
    """Plan to play a property card."""

    card: cards.PropertyCard


@dataclass(frozen=True)
class MoneyPlan(Plan):
    """Plan to play a money card."""

    card: cards.MoneyCard


@dataclass(frozen=True)
class ActionPlan(Plan):
    """Base class for action plans."""

    card: cards.ActionCard


@dataclass(frozen=True)
class GeneralActionPlan(ActionPlan):
    """Plan to play a general action card."""


@dataclass(frozen=True)
class GeneralRentPlan(GeneralActionPlan):
    """Plan to play a general rent action card."""

    colour: cards.PropertyColour
    rent_amount: int


@dataclass(frozen=True)
class TargetedActionPlan(ActionPlan):
    """Plan to play an action card targeted to a single player."""

    target: player.Player


@dataclass(frozen=True)
class WildRentPlan(TargetedActionPlan):
    """Plan to play a Wild Rent action card."""

    colour: cards.PropertyColour
    rent_amount: int


@dataclass(frozen=True)
class SlyDealPlan(TargetedActionPlan):
    """Plan to play a Sly Deal action card."""

    target_property: cards.PropertyCard


@dataclass(frozen=True)
class ForcedDealPlan(TargetedActionPlan):
    """Plan to play a Forced Deal action card."""

    target_property: cards.PropertyCard
    source_property: cards.PropertyCard


@dataclass(frozen=True)
class DealBreakerPlan(TargetedActionPlan):
    """Plan to play a Deal Breaker action card."""

    target_set: player.PropertySet


class Planner:
    """Planner class to generate plans for AI interactions."""

    def __init__(self, g: game.Game, p: player.Player) -> None:
        self.g = g  # Reference to the game instance for decision making
        self.p = p  # Reference to the player for whom plans are generated

        self.plan: Plan | None = None  # Current plan

    def choose_plan(self, hand: list[cards.Card]) -> None:
        # AI chooses the best plan based on the current hand
        all_plans = [self.generate_plans(card) for card in hand]
        assert all_plans, "No plans generated from hand"
        self.plan = max(
            list(itertools.chain(*all_plans)),
            key=self.plan_value_if_played,
        )

    def game_state_value(self, g: game.Game, me: player.Player) -> int:
        """Calculate a simple value for the game state."""
        value = 0
        for p in g.players:
            v = p.total_bank_value() + sum(
                card.value for card in p.properties_to_list()
            )
            if p == me:
                value += v
            else:
                value -= v
        return value + len(me.hand)

    def generate_rent_plans(
        self,
        card: cards.ActionCard,
        other_players: list[player.Player],
    ) -> list[Plan]:
        """Generate plans for rent actions."""
        assert cards.is_rent_action(
            card.action,
        ), f"Not a rent card: {card.action}"
        owned_colours_with_rents = self.p.owned_colours_with_rents(
            cards.RENT_CARD_COLOURS[card.action],
        )
        if not owned_colours_with_rents:
            return []
        if card.action == cards.ActionType.RENT_WILD:
            return [
                WildRentPlan(card, target, colour, rent_amount)
                for colour, rent_amount in owned_colours_with_rents
                for target in other_players
            ]
        return [
            GeneralRentPlan(card, colour, rent_amount)
            for colour, rent_amount in owned_colours_with_rents
        ]

    def generate_action_plans(self, card: cards.ActionCard) -> list[Plan]:
        other_players = [p for p in self.g.players if p != self.p]
        if card.action in (
            cards.ActionType.PASS_GO,
            cards.ActionType.ITS_MY_BIRTHDAY,
        ):
            return [GeneralActionPlan(card)]
        if cards.is_rent_action(card.action):
            return self.generate_rent_plans(card, other_players)
        if card.action == cards.ActionType.SLY_DEAL:
            return [
                SlyDealPlan(card, target, target_property)
                for target in other_players
                for target_property in target.properties_to_list()
            ]
        if card.action == cards.ActionType.FORCED_DEAL:
            return [
                ForcedDealPlan(card, target, target_property, source_property)
                for target in other_players
                for target_property in target.properties_to_list()
                for source_property in self.p.properties_to_list()
                if source_property.colour != target_property.colour
            ]
        if card.action == cards.ActionType.DEAL_BREAKER:
            return [
                DealBreakerPlan(card, target, target_set)
                for target in other_players
                for target_set in target.properties.values()
                if target_set.is_complete()
            ]
        msg = f"Unknown action card type: {card.action}"
        raise TypeError(
            msg,
        )

    def generate_plans(self, card: cards.Card) -> list[Plan]:
        """Generate all possible plans for the given card."""
        if isinstance(card, cards.PropertyCard):
            return [PropertyPlan(card)]
        if isinstance(card, cards.MoneyCard):
            return [MoneyPlan(card)]
        if isinstance(card, cards.ActionCard):
            return self.generate_action_plans(card)
        msg = f"Unknown card type: {type(card)}"
        raise TypeError(
            msg,
        )

    def plan_value_if_played(self, plan: Plan) -> int:
        """Compute the value of the game state if the given plan is played."""
        g_copy = deepcopy(self.g)
        p = g_copy.get_player_by_idx(self.p.index)
        if isinstance(plan, (PropertyPlan, MoneyPlan, ActionPlan)):
            g_copy.play_card(plan.card, p)
        return self.game_state_value(g_copy, p)


class AIInteraction(interaction.Interaction):
    """Interaction class for AI player making decisions automatically."""

    def __init__(self, me_idx: int) -> None:
        self.me_idx = me_idx  # index of the AI player

        self.planner: Planner | None = None

    def set_game_instance(self, g: game.Game) -> None:
        """Set the game instance for the AI interaction."""
        self.planner = Planner(g, g.get_player_by_idx(self.me_idx))

    def choose_card_in_hand(self, p: player.Player) -> cards.Card:
        assert (
            self.planner is not None
        ), "Planner and game instance not set for AI interaction"
        self.planner.choose_plan(p.hand)
        if isinstance(self.planner.plan, PropertyPlan):
            return self.planner.plan.card
        if isinstance(self.planner.plan, MoneyPlan):
            return self.planner.plan.card
        if isinstance(self.planner.plan, ActionPlan):
            return self.planner.plan.card
        msg = "No valid plan found for the AI to play."
        raise ValueError(msg)

    def choose_full_set_target(
        self,
        target: player.Player,
    ) -> player.PropertySet:
        # AI logic to choose a full set
        for prop_set in target.properties.values():
            if prop_set.is_complete():
                return prop_set
        return next(iter(target.properties.values()))

    def choose_property_target(
        self,
        target: player.Player,
        without_full_sets: bool = False,
    ) -> cards.PropertyCard:
        # AI logic to choose a property
        properties = target.properties_to_list(
            without_full_sets=without_full_sets,
        )
        assert properties, "No properties available to choose from"
        return max(properties, key=lambda prop: prop.value)

    def choose_player_target(
        self,
        players: list[player.Player],
    ) -> player.Player:
        # AI logic to choose a player
        return players[0]

    def choose_action_usage(self) -> int:
        # AI logic to decide how to use an action card
        return 1

    def choose_rent_colour_and_amount(
        self,
        owned_colours_with_rents: list[tuple[cards.PropertyColour, int]],
    ) -> tuple[cards.PropertyColour, int]:
        # AI logic to choose a colour and amount for rent
        if owned_colours_with_rents:
            return owned_colours_with_rents[0]
        return (cards.PropertyColour.RED, 0)

    def log(self, message: str) -> None:
        # AI does not log messages
        pass

    def notify_draw_my_turn(
        self,
        current_player: player.Player,
        players: list[player.Player],
        n_cards_played: int,
    ) -> None:
        # AI does not need to handle drawing
        pass

    def notify_draw_other_turn(self, players: list[player.Player]) -> None:
        # AI does not need to handle drawing
        pass

    def notify_turn_over(
        self,
        next_player_name: str,
    ) -> None:
        # AI does not need to handle turn-over
        pass

    def notify_game_over(
        self,
    ) -> None:
        # AI does not need to handle game-over
        pass
