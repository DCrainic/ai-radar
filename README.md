# 📡 AI Radar

> AI news on Twitter — before it lands on YouTube.

A real-time Twitter/X trend tracker that monitors AI news as it breaks, categorises it automatically, and surfaces the top trending topics **before** competitors even notice.

---

## What it does

AI Radar watches a curated list of researchers, labs, and accounts on Twitter/X. It scores every tweet by **engagement velocity** (not raw likes), so you see what's blowing up *right now* — not what was popular yesterday.

Connect it to a Twitter API key for live data, or run it in **demo mode** (no key needed) to explore the full UI with realistic mock tweets.

---

## Why it exists

AI news breaks on Twitter first — from model releases to benchmark drops to viral debates. YouTube channels always lag by 1–7 days. A team that catches a trend in hour one, while competitors are still scrolling, has a massive first-mover advantage on video topics.

**The workflow AI Radar enables:**
1. Open the dashboard → see what's trending right now
2. Filter by category (Model Release, Research Paper, etc.)
3. Star the best ideas → they go into your saved list
4. Export a daily digest → paste into your morning planning doc
5. Start scripting while the topic is still early

---

## Setup

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/ai-radar.git
cd ai-radar

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Add your Twitter Bearer Token
cp .env.example .env
# Edit .env and paste your TWITTER_BEARER_TOKEN

# 4. Run
streamlit run app.py
```

The app opens at `http://localhost:8501`. No API key? It runs in demo mode automatically.

### Getting a free Twitter API key

1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Create a free account → New Project → New App
3. Copy the **Bearer Token** from the "Keys and Tokens" tab
4. Paste it in `.env` or the Settings tab inside the app

Free Basic tier: **500,000 tweet reads/month** — plenty for daily monitoring.

---

## How the trend score works

```
trend_score = (likes + retweets × 3 + replies × 2) / hours_since_posted
```

Retweets are weighted 3× (signal of spread) and replies 2× (signal of discussion). Dividing by age means a tweet with 500 interactions in 30 minutes scores higher than one with 2,000 interactions over 3 days.

This catches things while they're still in the growth phase — the core value of the tool.

---

## Features

| Feature | Description |
|---|---|
| **Live feed** | Twitter API v2, filtered to top AI accounts + keywords |
| **Demo mode** | 40+ realistic mock tweets, runs without any API key |
| **Auto-categorisation** | Model Release / Tool / Paper / Funding / Debate / Benchmark |
| **Trend scoring** | Engagement velocity, not raw likes |
| **Sidebar filters** | Time range, category, min engagement, account |
| **Saved ideas** | Star tweets as content ideas, export to `.md` |
| **Daily digest** | Auto-generated markdown summary of the top 5 tweets |
| **Trend graph** | Plotly chart — tweet volume by hour, colour-coded by category |
| **Settings tab** | Add API key, edit account/keyword lists, set refresh interval |
| **Background refresh** | Auto-fetches new tweets every 30 min (configurable) |

---

## File structure

```
ai-radar/
├── app.py           # Main Streamlit app (dashboard, digest, settings)
├── tracker.py       # Twitter API fetching + mock fallback
├── categoriser.py   # Rule-based tweet categorisation
├── database.py      # SQLite — tweets, ideas, settings
├── mock_data.py     # 40+ realistic demo tweets
├── digest.py        # Daily digest markdown generator
├── scheduler.py     # Background auto-refresh thread
├── requirements.txt
├── .env.example     # Copy → .env, add Bearer Token
└── .gitignore
```

---

## Roadmap

- [ ] Slack integration — post daily digest automatically
- [ ] Email digest via SMTP
- [ ] Claude-powered summaries ("why does this tweet matter?")
- [ ] Thread unrolling (fetch full Twitter threads, not just the first tweet)
- [ ] Topic clustering across multiple tweets on the same story
- [ ] Keyword alerts — push notification when a high-score tweet matches a keyword

---

## License

MIT — use it, fork it, build on it.
