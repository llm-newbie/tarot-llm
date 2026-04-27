# -*- coding: utf-8 -*-
"""Prompt templates for the Tarot LLM."""

SYSTEM_PROMPT = """당신은 깊은 통찰력과 솔직함을 갖춘 타로 리더입니다.
타로는 현실을 있는 그대로 비추는 거울입니다 — 아름다운 면도, 직면해야 할 면도 함께 보여줍니다.

## 해석 순서 (반드시 이 순서를 따를 것)

**1단계 — 개별 카드 해석**
각 카드를 포지션 맥락에 맞게 독립적으로 해석합니다.
카드의 상징, 에너지, 정/역방향 의미를 구체적으로 풀어냅니다.

**2단계 — 카드 간 상호작용 분석**
카드들이 서로 어떻게 대화하는지 읽어냅니다.
- 에너지가 강화되는 조합인지, 긴장을 만드는 조합인지
- 흐름이 이어지는지, 단절되는지
- 반복되는 수트·원소·숫자가 있다면 그 패턴이 무엇을 말하는지
이 상호작용 분석이 리딩의 핵심입니다. 충분한 깊이로 다룰 것.

**3단계 — 전체 해석 틀 도출**
1·2단계를 바탕으로 이 배열 전체가 말하는 하나의 큰 이야기를 도출합니다.
이 해석 틀 안에서 질문자의 상황을 유연하게 풀어나갑니다.

## 균형의 원칙

타로는 좋은 말만 하지 않습니다. **솔직함이 진짜 도움입니다.**
- 긍정적인 에너지와 가능성은 명확히 제시합니다
- **조심해야 할 부분, 리스크, 놓치고 있는 것도 직접적으로 말합니다**
- 어려운 카드를 억지로 긍정적으로 포장하지 않습니다
- 단, 두려움을 조장하지 않고 "알고 대비하면 달라진다"는 관점을 유지합니다
- 역방향 카드는 막힌 에너지 또는 그림자 측면으로 솔직하게 다룹니다

## 응답 형식

- 마크다운을 활용해 구조를 명확히 합니다
- 각 카드 해석 → 카드 간 상호작용 → 전체 해석 → 조심할 점 → 핵심 메시지 순으로 작성합니다
- **조심할 점** 섹션은 생략하지 말 것 — 리딩에서 가장 중요한 경고 신호를 담습니다
- 마지막 핵심 메시지는 한 줄로, 솔직하고 힘 있게 마무리합니다
- 한국어로 대화합니다 (질문이 영어라면 영어로 답변)"""


def build_reading_prompt(
    question: str,
    spread: dict,
    drawn_cards: list[dict],
) -> str:
    """
    Build the user-turn prompt for the tarot reading.

    Args:
        question: The user's question
        spread: The selected spread dict from spreads.json
        drawn_cards: List of drawn card dicts (already including 'orientation')
    """
    spread_info = (
        f"**배열**: {spread['korean_name']} ({spread['name']}) — "
        f"카드 {spread['num_cards']}장\n"
        f"**배열 설명**: {spread['description']}\n"
    )

    cards_block = []
    for i, (position, card) in enumerate(zip(spread["positions"], drawn_cards), 1):
        orientation_kr = "정방향" if card["orientation"] == "upright" else "역방향"
        meaning = card[card["orientation"]]
        keywords = ", ".join(card["keywords"][:5])

        card_text = (
            f"### 카드 {i}: [{position['korean_name']}] {position['name']}\n"
            f"- **카드명**: {card['name']} ({orientation_kr})\n"
            f"- **원형/상징**: {card.get('archetype', card.get('suit_theme', ''))}\n"
            f"- **키워드**: {keywords}\n"
            f"- **포지션 의미**: {position['description']}\n"
            f"- **카드 일반 의미**: {meaning['general']}\n"
        )

        # Add context-specific meaning if available
        question_lower = question.lower()
        context_keys = []
        if any(w in question_lower for w in ["사랑", "연애", "관계", "love", "relationship", "partner"]):
            context_keys.append("love")
        if any(w in question_lower for w in ["직업", "일", "커리어", "career", "work", "job"]):
            context_keys.append("career")
        if any(w in question_lower for w in ["돈", "재정", "money", "finance", "financial"]):
            context_keys.append("finance")
        if any(w in question_lower for w in ["건강", "몸", "health", "wellness"]):
            context_keys.append("health")

        for ctx_key in context_keys[:1]:  # Use the most relevant context
            if ctx_key in meaning:
                card_text += f"- **{ctx_key.capitalize()} 맥락**: {meaning[ctx_key]}\n"

        cards_block.append(card_text)

    cards_section = "\n".join(cards_block)

    prompt = f"""다음 타로 리딩을 진행해주세요.

## 질문자의 질문
"{question}"

## 선택된 배열
{spread_info}

## 뽑힌 카드들

{cards_section}

---

위 카드들을 바탕으로 다음 순서로 리딩을 진행하세요.

## 리딩 구성

**① 카드 해석** — 각 카드를 포지션 맥락에 맞게 해석합니다

**② 카드 간 상호작용** — 카드들이 서로 만들어내는 긴장·흐름·패턴을 분석합니다.
에너지가 충돌하는 조합, 강화되는 조합, 반복 수트/원소가 있다면 반드시 짚어주세요.

**③ 전체 해석** — 이 배열 전체가 말하는 하나의 큰 이야기를 도출하고, 그 틀 안에서 질문자의 상황을 풀어줍니다.

**④ 조심할 점** — 이 리딩에서 발견되는 경고 신호, 리스크, 놓치고 있는 부분을 솔직하게 짚어줍니다. 억지로 긍정적으로 포장하지 마세요.

**⑤ 핵심 메시지** — 한 줄로, 솔직하고 힘 있게 마무리합니다."""

    return prompt


def build_followup_prompt(followup_question: str, previous_context: str) -> str:
    return f"""이전 리딩 컨텍스트:
{previous_context}

후속 질문: {followup_question}

이전 리딩의 맥락을 유지하면서 후속 질문에 답변해주세요."""
