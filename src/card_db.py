import json
import random
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent / "data"

with open(_DATA_DIR / "cards.json", encoding="utf-8") as f:
    _CARD_DATA = json.load(f)

with open(_DATA_DIR / "spreads.json", encoding="utf-8") as f:
    _SPREAD_DATA = json.load(f)


def _flatten_cards() -> list[dict]:
    cards = list(_CARD_DATA["major_arcana"])
    for suit_data in _CARD_DATA["minor_arcana"].values():
        cards.extend(suit_data["cards"])
    return cards


ALL_CARDS: list[dict] = _flatten_cards()
ALL_SPREADS: list[dict] = _SPREAD_DATA["spreads"]


def get_spread(spread_id: str) -> dict | None:
    return next((s for s in ALL_SPREADS if s["id"] == spread_id), None)


def draw_cards(n: int) -> list[dict]:
    """Draw n unique random cards, each with a random orientation."""
    chosen = random.sample(ALL_CARDS, n)
    return [
        {**card, "orientation": random.choice(["upright", "reversed"])}
        for card in chosen
    ]


def card_meaning(card: dict) -> dict:
    """Return the relevant meaning dict (upright or reversed)."""
    return card[card["orientation"]]


def format_drawn_card(card: dict, position: dict) -> str:
    orientation_kr = "정방향" if card["orientation"] == "upright" else "역방향"
    meaning = card_meaning(card)
    keywords = ", ".join(card["keywords"][:4])
    return (
        f"[{position['korean_name']} / {position['name']}]\n"
        f"카드: {card['name']} ({orientation_kr})\n"
        f"키워드: {keywords}\n"
        f"의미: {meaning['general']}"
    )
