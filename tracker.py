"""
Twitter/X data fetcher.
Falls back to realistic mock data when no Bearer Token is configured.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from categoriser import categorise
from mock_data import get_mock_tweets

load_dotenv()

# Accounts and keywords from the spec
ACCOUNTS: list[str] = [
    "sama", "AnthropicAI", "OpenAI", "GoogleDeepMind", "ylecun",
    "karpathy", "emollick", "DrJimFan", "_akhaliq", "mistralai",
    "huggingface", "gdb", "fchollet", "rohanpaul_ai", "scaling01",
    "alexalbert__",
]

KEYWORDS: list[str] = [
    "#AI", "#LLM", "#GenAI", "#AINews",
    "model release", "open source model",
    "beats GPT-4", "new benchmark", "context window",
    "Claude", "GPT", "Gemini", "Llama", "Mistral",
    "multimodal", "agents", "reasoning model",
    "AI agent", "fine-tuning", "RLHF",
]


def _trend_score(tweet: dict) -> float:
    """Engagement velocity: (likes + retweets*3 + replies*2) / hours_since_posted."""
    likes = tweet.get("likes", 0)
    retweets = tweet.get("retweets", 0)
    replies = tweet.get("replies", 0)
    engagement = likes + retweets * 3 + replies * 2

    posted_at_raw = tweet.get("posted_at", "")
    try:
        if isinstance(posted_at_raw, str):
            posted_at = datetime.fromisoformat(posted_at_raw.replace("Z", "+00:00"))
        else:
            posted_at = posted_at_raw
        hours_ago = max((datetime.now(timezone.utc) - posted_at).total_seconds() / 3600, 0.1)
    except (ValueError, TypeError):
        hours_ago = 1.0

    return round(engagement / hours_ago, 1)


class TwitterTracker:
    """Fetches and preprocesses tweets. Uses mock data when no API key is set."""

    def __init__(self):
        self.bearer_token: str | None = os.getenv("TWITTER_BEARER_TOKEN")
        self.mock_mode: bool = not bool(self.bearer_token)

    # ── Public API ────────────────────────────────────────────────────────

    def fetch(self) -> list[dict]:
        """Return processed tweets ready for storage."""
        if self.mock_mode:
            return self._fetch_mock()
        return self._fetch_live()

    # ── Internal ──────────────────────────────────────────────────────────

    def _fetch_mock(self) -> list[dict]:
        tweets = get_mock_tweets()
        return [self._enrich(t) for t in tweets]

    def _fetch_live(self) -> list[dict]:
        try:
            import tweepy  # type: ignore
        except ImportError:
            raise RuntimeError(
                "tweepy is not installed. Run: pip install tweepy"
            )

        client = tweepy.Client(bearer_token=self.bearer_token, wait_on_rate_limit=True)
        results: list[dict] = []

        # Build search query: monitored accounts OR keywords
        account_query = " OR ".join(f"from:{a}" for a in ACCOUNTS)
        keyword_query = " OR ".join(f'"{kw}"' for kw in KEYWORDS[:10])
        query = f"({account_query}) ({keyword_query}) -is:retweet lang:en"

        try:
            response = client.search_recent_tweets(
                query=query,
                max_results=100,
                tweet_fields=["created_at", "public_metrics", "author_id", "text"],
                user_fields=["username"],
                expansions=["author_id"],
            )

            if not response.data:
                return []

            user_map = {u.id: u.username for u in (response.includes.get("users") or [])}

            for tweet in response.data:
                metrics = tweet.public_metrics or {}
                author = user_map.get(tweet.author_id, str(tweet.author_id))
                raw = {
                    "id": str(tweet.id),
                    "author": author,
                    "text": tweet.text,
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0),
                    "posted_at": tweet.created_at.isoformat() if tweet.created_at else datetime.now(timezone.utc).isoformat(),
                    "url": f"https://twitter.com/{author}/status/{tweet.id}",
                    "category": None,
                }
                results.append(self._enrich(raw))

        except tweepy.TweepyException as exc:
            raise RuntimeError(f"Twitter API error: {exc}") from exc

        return results

    def _enrich(self, tweet: dict) -> dict:
        """Add category and trend_score to a raw tweet dict."""
        if not tweet.get("category"):
            tweet["category"] = categorise(tweet["text"])
        tweet["trend_score"] = _trend_score(tweet)
        return tweet
