"""
Rule-based tweet categorisation using keyword matching.
Each tweet gets exactly one category label.
"""

from __future__ import annotations

CATEGORY_RULES: list[tuple[str, list[str]]] = [
    # Higher-priority rules first
    (
        "benchmark_numbers",
        [
            "%", "score", "beats", "outperforms", "sota", "state of the art",
            "vs gpt", "vs claude", "vs gemini", "benchmark", "leaderboard",
            "accuracy", "eval", "results:", "achieves", "surpasses",
        ],
    ),
    (
        "model_release",
        [
            "new model", "release", "launch", "introducing", "available now",
            "open source", "weights", "open-weight", "open weight",
            "we're releasing", "we are releasing", "releasing today",
            "out now", "dropping", "shipping",
        ],
    ),
    (
        "research_paper",
        [
            "paper", "arxiv", "we show", "our research", "study", "findings",
            "we propose", "we introduce", "we demonstrate", "empirically",
            "experiments show", "ablation", "dataset",
        ],
    ),
    (
        "funding_business",
        [
            "funding", "raised", "valuation", "series a", "series b", "series c",
            "billion", "million", "acquisition", "acqui-hire", "ipo", "revenue",
            "arr", "investment", "investor", "venture",
        ],
    ),
    (
        "tool_product",
        [
            "api", "feature", "update", "plugin", "integration", "app", "tool",
            "product", "platform", "service", "launching", "now available",
            "deploy", "endpoint", "sdk", "open-source",
        ],
    ),
    (
        "viral_debate",
        [
            "hot take", "unpopular opinion", "thread", "disagree", "i think",
            "actually", "controversial", "change my mind", "fight me",
            "overrated", "underrated", "debate", "wrong about",
        ],
    ),
]

CATEGORY_META: dict[str, dict] = {
    "model_release":      {"emoji": "🚀", "label": "Modell-Release",      "color": "#1D4ED8", "bg": "#EFF6FF"},
    "tool_product":       {"emoji": "🛠️", "label": "Neues Tool / Produkt","color": "#166534", "bg": "#F0FDF4"},
    "research_paper":     {"emoji": "📄", "label": "Forschungspapier",     "color": "#713F12", "bg": "#FEF9C3"},
    "funding_business":   {"emoji": "💰", "label": "Finanzierung / News",  "color": "#9A3412", "bg": "#FFF7ED"},
    "viral_debate":       {"emoji": "🔥", "label": "Virale Debatte",       "color": "#BE123C", "bg": "#FFF1F2"},
    "benchmark_numbers":  {"emoji": "📊", "label": "Benchmark / Zahlen",   "color": "#5B21B6", "bg": "#F5F3FF"},
}

DEFAULT_CATEGORY = "viral_debate"


def categorise(text: str) -> str:
    """Return the best-matching category key for a tweet's text."""
    lower = text.lower()
    for category, keywords in CATEGORY_RULES:
        if any(kw in lower for kw in keywords):
            return category
    return DEFAULT_CATEGORY


def get_meta(category: str) -> dict:
    """Return display metadata (emoji, label, colors) for a category."""
    return CATEGORY_META.get(category, CATEGORY_META[DEFAULT_CATEGORY])


def all_categories() -> list[dict]:
    """Return all categories with their display metadata, for filter UIs."""
    return [
        {"key": k, **v}
        for k, v in CATEGORY_META.items()
    ]
