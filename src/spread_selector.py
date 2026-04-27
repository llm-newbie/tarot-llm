"""
Simple rule-based spread selector.
Picks one of three 3-card spreads based on question keywords.
Optimized: No API call needed, so it conserves daily quota.
"""

from __future__ import annotations
from .card_db import ALL_SPREADS


def select_spread(question: str, api_key: str | None = None) -> dict:
    """Select a 3-card spread based on the question content."""
    q = question.lower()

    # 예/아니오 계열
    yes_no_signals = ["할까", "할지", "해야", "되나요", "될까요", "맞나요",
                      "괜찮을까", "가능할까", "should i", "will i", "is it"]
    if any(s in q for s in yes_no_signals):
        return _get("yes_no")

    # 상황/행동/결과 계열 (고민, 결정)
    situation_signals = ["고민", "선택", "결정", "어떻게", "방법", "해결",
                         "문제", "갈등", "방향", "어떡", "decide", "choice", "how to"]
    if any(s in q for s in situation_signals):
        return _get("three_card_situation")

    # 나머지는 과거/현재/미래
    return _get("three_card_ppf")


def _get(spread_id: str) -> dict:
    return next(
        (s for s in ALL_SPREADS if s["id"] == spread_id),
        next(s for s in ALL_SPREADS if s["id"] == "three_card_ppf"),
    )


def list_spreads() -> list[dict]:
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "korean_name": s["korean_name"],
            "num_cards": s["num_cards"],
            "best_for": s["best_for"],
        }
        for s in ALL_SPREADS
        if s["id"] in ("three_card_ppf", "three_card_situation", "yes_no")
    ]
