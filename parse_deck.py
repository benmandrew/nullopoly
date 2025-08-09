import json
import pathlib
from typing import Any

import cards


def parse_action_card(card_data: dict[str, Any], idx: int) -> cards.ActionCard:
    for field in ["name", "value", "action"]:
        if field not in card_data:
            msg = f"Missing '{field}' in action card at index {idx}."
            raise ValueError(msg)
    try:
        action = cards.ActionType[card_data["action"].upper()]
    except KeyError as exc:
        msg = f"Invalid action type '{card_data['action']}' at index {idx}."
        raise TypeError(msg) from exc
    return cards.ActionCard(
        card_data["name"],
        card_data["value"],
        action,
    )


def parse_property_card(
    card_data: dict[str, Any],
    idx: int,
) -> cards.PropertyCard:
    for field in ["name", "value", "colour"]:
        if field not in card_data:
            msg = f"Missing '{field}' in property card at index {idx}."
            raise ValueError(msg)
    try:
        colour = cards.PropertyColour[card_data["colour"].upper()]
    except KeyError as exc:
        msg = f"Invalid property colour '{card_data['colour']}' at index {idx}."
        raise ValueError(msg) from exc
    return cards.PropertyCard(
        card_data["name"],
        card_data["value"],
        colour,
    )


def parse_money_card(card_data: dict[str, Any], idx: int) -> cards.MoneyCard:
    if "value" not in card_data:
        msg = f"Missing 'value' in money card at index {idx}."
        raise ValueError(msg)
    return cards.MoneyCard(card_data["value"])


def parse_actions(data: dict[str, Any]) -> list[cards.Card]:
    deck: list[cards.Card] = []
    action_cards = data.get("action", [])
    if not isinstance(action_cards, list):
        msg = "'action' must be a list."
        raise TypeError(msg)
    for idx, card_data in enumerate(action_cards):
        if not isinstance(card_data, dict):
            msg = f"Action card at index {idx} is not a JSON object."
            raise TypeError(msg)
        deck.append(parse_action_card(card_data, idx))
    return deck


def parse_properties(data: dict[str, Any]) -> list[cards.Card]:
    deck: list[cards.Card] = []
    property_cards = data.get("property", [])
    if not isinstance(property_cards, list):
        msg = "'property' must be a list."
        raise TypeError(msg)
    for idx, card_data in enumerate(property_cards):
        if not isinstance(card_data, dict):
            msg = f"Property card at index {idx} is not a JSON object."
            raise TypeError(msg)
        deck.append(parse_property_card(card_data, idx))
    return deck


def parse_money(data: dict[str, Any]) -> list[cards.Card]:
    deck: list[cards.Card] = []
    money_cards = data.get("money", [])
    if not isinstance(money_cards, list):
        msg = "'money' must be a list."
        raise TypeError(msg)
    for idx, card_data in enumerate(money_cards):
        if not isinstance(card_data, dict):
            msg = f"Money card at index {idx} is not a JSON object."
            raise TypeError(msg)
        deck.append(parse_money_card(card_data, idx))
    return deck


def from_json(filepath: pathlib.Path) -> list[cards.Card]:
    if not filepath.is_file():
        msg = f"Deck file '{filepath}' does not exist."
        raise FileNotFoundError(msg)
    with filepath.open(encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as exc:
            msg = f"Invalid JSON format: {exc}"
            raise ValueError(msg) from exc
    if not isinstance(data, dict):
        msg = "Deck JSON must be a dictionary with card type keys."
        raise TypeError(msg)
    return parse_properties(data) + parse_actions(data) + parse_money(data)
