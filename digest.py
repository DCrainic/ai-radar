"""
Tages-Digest-Generator für ONEFRAME KI-Radar.
Gibt einen deutschen Markdown-Bericht der Top-N-Tweets aus.
"""

from __future__ import annotations

from datetime import datetime, timezone

from categoriser import get_meta

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni",
          "Juli", "August", "September", "Oktober", "November", "Dezember"]


def _datum_de() -> str:
    now = datetime.now(timezone.utc)
    return f"{WOCHENTAGE[now.weekday()]}, {now.day}. {MONATE[now.month - 1]} {now.year}"


def _engagement_label(tweet: dict) -> str:
    total = tweet.get("likes", 0) + tweet.get("retweets", 0) + tweet.get("replies", 0)
    if total >= 1000:
        return f"{total / 1000:.1f}k Interaktionen"
    return f"{total} Interaktionen"


def _zeitstempel(posted_at_raw: str) -> str:
    try:
        posted_at = datetime.fromisoformat(posted_at_raw.replace("Z", "+00:00"))
        diff = datetime.now(timezone.utc) - posted_at
        stunden = int(diff.total_seconds() // 3600)
        if stunden < 1:
            return "vor weniger als 1 Stunde"
        if stunden == 1:
            return "vor 1 Stunde"
        if stunden < 24:
            return f"vor {stunden} Stunden"
        tage = stunden // 24
        return f"vor {tage} Tag{'en' if tage > 1 else ''}"
    except (ValueError, TypeError):
        return ""


def generate_digest(tweets: list[dict], top_n: int = 5) -> str:
    """Gibt einen deutschen Markdown-Digest zurück."""
    lines: list[str] = [
        "# ONEFRAME · KI-Radar — Tages-Digest",
        f"*{_datum_de()}*",
        "",
        "---",
        "",
        f"### Top {min(top_n, len(tweets))} Trends des Tages",
        "",
    ]

    for i, tweet in enumerate(tweets[:top_n], start=1):
        meta = get_meta(tweet.get("category", "viral_debate"))
        emoji = meta["emoji"]
        label = meta["label"]
        author = tweet.get("author", "unbekannt")
        text = tweet.get("text", "")
        url = tweet.get("url", "#")
        engagement = _engagement_label(tweet)
        zeitstempel = _zeitstempel(tweet.get("posted_at", ""))
        score = tweet.get("trend_score", 0)

        display_text = text if len(text) <= 200 else text[:197] + "…"

        lines += [
            f"**{i}. {emoji} [{label}]** @{author} — {zeitstempel}",
            f"> {display_text}",
            "",
            f"📈 Trend-Score: **{score:.0f}** · {engagement} · [Auf X ansehen]({url})",
            "",
            "---",
            "",
        ]

    if not tweets:
        lines += [
            "_Keine Tweets im gewählten Zeitraum gefunden._",
            "",
            "---",
            "",
        ]

    lines += [
        f"*Erstellt von ONEFRAME KI-Radar · {datetime.now(timezone.utc).strftime('%H:%M UTC')} · "
        f"Built by Dominique Crainic*",
    ]

    return "\n".join(lines)
