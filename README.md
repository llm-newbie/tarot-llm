# TarotLLM

An AI tarot reading web app built with Google Gemini API and prompt engineering.
Enter a question, draw 3 cards, and receive an in-depth streaming interpretation based on a full 78-card dataset.

## Features

- **Full 78-card dataset** — 22 Major Arcana + 56 Minor Arcana, with upright and reversed meanings
- **Automatic spread selection** — Chooses the best 3-card spread (Past/Present/Future, Situation/Action/Outcome, or Yes/No) based on the question type
- **Structured 5-step interpretation** — Individual cards → Card interactions → Overall reading → Cautions → Core message
- **Real-time streaming output** — Interpretation text appears as it is generated
- **Follow-up questions** — Ask additional questions within the same reading context
- **Korean & English support** — Handles questions in both languages

## Installation

```bash
git clone https://github.com/llm-newbie/tarot-llm
cd tarot-llm
pip install -r requirements.txt
```

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/) and sign in with your Google account
2. Click **"Get API key"** in the left menu
3. Click **"Create API key"** and copy the generated key (`AIza...`)
4. Available on the free plan immediately — no credit card required

> Never upload your API key to a public repository.

## Running the App

### Windows

```bat
run.bat
```

### macOS / Linux

```bash
streamlit run app.py
```

Once the browser opens at `http://localhost:8501`, enter your API key in the sidebar and start asking questions.

## How to Use

1. Paste your Gemini API key into the **Gemini API Key** field in the sidebar
2. Type your question or concern in the chat input at the bottom
3. The app automatically selects the most suitable 3-card spread, draws cards, and streams the interpretation
4. Ask follow-up questions within the same reading ("Tell me more", "Why is that?", etc.)

## Project Structure

```
tarot-llm/
├── data/
│   ├── cards.json          # Full 78-card dataset (upright/reversed meanings across 5 contexts)
│   └── spreads.json        # Spread definitions
├── src/
│   ├── card_db.py          # Card loading and random draw
│   ├── spread_selector.py  # Keyword-based automatic spread selection
│   ├── prompts.py          # Prompt templates
│   └── tarot_reader.py     # Core reading logic + streaming
├── app.py                  # Streamlit web UI
├── run.bat                 # Windows launcher
└── requirements.txt
```

## Tech Stack

- **LLM**: Google Gemini 2.5 Flash (`google-genai` SDK)
- **UI**: Streamlit (real-time streaming chat)
- **Data**: Hand-built 78-card tarot JSON dataset
- **Spread selection**: Keyword rule-based (no API call)
- **Model settings**: temperature=0.9, top_p=0.95, max_output_tokens=8192

## Notes

- Free tier limit: **20 requests per day** for Gemini 2.5 Flash
- On 503 errors (server overload), the app automatically retries before showing an error message
- The daily limit resets at UTC midnight (9:00 AM KST)
"# tarot-llm" 
