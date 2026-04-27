"""Core tarot reader: spread selection, card drawing, and Gemini API call."""

from __future__ import annotations
import os
import time
from google import genai
from google.genai import types
from .card_db import draw_cards, ALL_CARDS
from .spread_selector import select_spread
from .prompts import SYSTEM_PROMPT, build_reading_prompt, build_followup_prompt


def _is_retryable(e: Exception) -> bool:
    s = str(e)
    return any(k in s for k in ("503", "UNAVAILABLE"))


def _retry_delay(e: Exception) -> float:
    import re
    m = re.search(r'retry[^\d]*(\d+)', str(e), re.IGNORECASE)
    return float(m.group(1)) + 2 if m else 10.0


def _get_client(api_key: str | None = None) -> genai.Client:
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "Gemini API key not found. Set GEMINI_API_KEY environment variable "
            "or pass api_key to TarotReader."
        )
    return genai.Client(api_key=key)


class TarotReader:
    """
    Main interface for performing tarot readings via Gemini.

    Usage:
        reader = TarotReader(api_key="...")
        result = reader.read("나의 연애운은 어떤가요?")
        print(result.response_text)
    """

    MODELS = [
        "gemini-2.5-flash",
        "gemini-3-flash-preview",
    ]

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.client = _get_client(self._api_key)
        self._active_model = self.MODELS[0]
        self._last_context: str = ""
        self._history: list[dict] = []

    def _config(self) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.9,
            top_p=0.95,
            max_output_tokens=8192,
        )

    def _generate(self, prompt: str) -> str:
        last_err = None
        for attempt in range(2):
            for model in self.MODELS:
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=self._config(),
                    )
                    self._active_model = model
                    return response.text
                except Exception as e:
                    if _is_retryable(e):
                        last_err = e
                        time.sleep(_retry_delay(e))
                        continue
                    raise
        raise RuntimeError(f"서버 과부하로 응답 실패. 잠시 후 다시 시도해주세요. ({last_err})")

    def _stream(self, prompt: str):
        """Yield text chunks — retries on 503."""
        last_err = None
        for attempt in range(2):
            for model in self.MODELS:
                try:
                    got_text = False
                    for chunk in self.client.models.generate_content_stream(
                        model=model,
                        contents=prompt,
                        config=self._config(),
                    ):
                        try:
                            text = chunk.text
                        except Exception:
                            text = None
                        if text:
                            got_text = True
                            yield text
                    if got_text:
                        self._active_model = model
                        return
                    last_err = RuntimeError(f"{model}: 빈 응답")
                except Exception as e:
                    if _is_retryable(e):
                        last_err = e
                        time.sleep(_retry_delay(e))
                        continue
                    raise
        raise RuntimeError(f"서버 과부하로 응답 실패. 잠시 후 다시 시도해주세요. ({last_err})")

    def prepare_reading(self, question: str) -> tuple[dict, list[dict], str]:
        """
        Ask Gemini to pick the spread, draw cards, build prompt.
        Returns (spread, cards, prompt).
        """
        spread = select_spread(question, api_key=self._api_key)
        cards = draw_cards(spread["num_cards"])
        prompt = build_reading_prompt(question, spread, cards)
        return spread, cards, prompt

    def stream_reading(self, question: str):
        """
        Full reading pipeline with streaming.
        Yields (meta, chunk) where meta is sent once at the start (cards info),
        then text chunks follow.
        """
        spread, cards, prompt = self.prepare_reading(question)

        meta = {
            "spread_name": spread["korean_name"],
            "num_cards": spread["num_cards"],
            "positions": spread["positions"],
            "cards": cards,
        }
        yield ("meta", meta)

        full_text = ""
        for chunk in self._stream(prompt):
            full_text += chunk
            yield ("chunk", chunk)

        self._last_context = prompt
        self._history.append({"role": "user", "content": prompt})
        self._history.append({"role": "assistant", "content": full_text})

    def stream_followup(self, question: str):
        """Stream a follow-up response in the context of the last reading."""
        if not self._last_context:
            raise ValueError("No previous reading found. Call stream_reading() first.")
        prompt = build_followup_prompt(question, self._last_context)
        yield from self._stream(prompt)

    def read(self, question: str) -> "ReadingResult":
        """Non-streaming reading (used by CLI)."""
        spread, cards, prompt = self.prepare_reading(question)
        response_text = self._generate(prompt)
        self._last_context = prompt
        self._history.append({"role": "user", "content": prompt})
        self._history.append({"role": "assistant", "content": response_text})
        return ReadingResult(question=question, spread=spread, drawn_cards=cards, response_text=response_text)

    def followup(self, question: str) -> str:
        """Non-streaming follow-up (used by CLI)."""
        if not self._history:
            raise ValueError("No previous reading found. Call read() first.")
        prompt = build_followup_prompt(question, self._last_context)
        return self._generate(prompt)


class ReadingResult:
    def __init__(
        self,
        question: str,
        spread: dict,
        drawn_cards: list[dict],
        response_text: str,
    ):
        self.question = question
        self.spread = spread
        self.drawn_cards = drawn_cards
        self.response_text = response_text

    def __str__(self) -> str:
        lines = [
            f"\n{'='*60}",
            f"질문: {self.question}",
            f"배열: {self.spread['korean_name']} ({self.spread['num_cards']}장)",
            f"{'='*60}",
        ]
        for pos, card in zip(self.spread["positions"], self.drawn_cards):
            orientation = "정방향" if card["orientation"] == "upright" else "역방향"
            lines.append(f"  [{pos['korean_name']}] {card['name']} - {orientation}")
        lines.append(f"\n{self.response_text}")
        lines.append("="*60)
        return "\n".join(lines)
