import json

from card import (
    Card,
    PropertyCard,
    ActionCard,
    MoneyCard,
    PropertyColour,
    ActionType,
)


def parse_action_card(card_data: dict, idx: int) -> ActionCard:
    for field in ["name", "value", "action"]:
        if field not in card_data:
            raise ValueError(
                f"Missing '{field}' in action card at index {idx}."
            )
    try:
        action = ActionType[card_data["action"].upper()]
    except KeyError as exc:
        raise ValueError(
            f"Invalid action type '{card_data['action']}' at index {idx}."
        ) from exc
    return ActionCard(
        card_data["name"],
        card_data["value"],
        action,
    )


def parse_property_card(card_data: dict, idx: int) -> PropertyCard:
    for field in ["name", "value", "colour"]:
        if field not in card_data:
            raise ValueError(
                f"Missing '{field}' in property card at index {idx}."
            )
    try:
        colour = PropertyColour[card_data["colour"].upper()]
    except KeyError as exc:
        raise ValueError(
            f"Invalid property colour '{card_data['colour']}' at index {idx}."
        ) from exc
    return PropertyCard(
        card_data["name"],
        card_data["value"],
        colour,
    )


def parse_money_card(card_data: dict, idx: int) -> MoneyCard:
    if "value" not in card_data:
        raise ValueError(f"Missing 'value' in money card at index {idx}.")
    return MoneyCard(card_data["value"])


def from_json(filepath: str) -> list[Card]:
    with open(filepath, "rt", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON format: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Deck JSON must be a dictionary with card type keys.")
    deck: list[Card] = []
    property_cards = data.get("property", [])
    if not isinstance(property_cards, list):
        raise ValueError("'property' must be a list.")
    for idx, card_data in enumerate(property_cards):
        if not isinstance(card_data, dict):
            raise ValueError(
                f"Property card at index {idx} is not a JSON object."
            )
        deck.append(parse_property_card(card_data, idx))
    action_cards = data.get("action", [])
    if not isinstance(action_cards, list):
        raise ValueError("'action' must be a list.")
    for idx, card_data in enumerate(action_cards):
        if not isinstance(card_data, dict):
            raise ValueError(
                f"Action card at index {idx} is not a JSON object."
            )
        deck.append(parse_action_card(card_data, idx))
    money_cards = data.get("money", [])
    if not isinstance(money_cards, list):
        raise ValueError("'money' must be a list.")
    for idx, card_data in enumerate(money_cards):
        if not isinstance(card_data, dict):
            raise ValueError(f"Money card at index {idx} is not a JSON object.")
        deck.append(parse_money_card(card_data, idx))
    return deck
