# Twitter AI Trend Tracker — Build Context for Claude Code

> Paste this file into Claude Code at the start of your session. It contains the full project brief, architecture, and feature spec. Claude Code should read this before writing a single line of code.

---

## 1. What We're Building

A **local web app** (Python + Streamlit) called **"AI Radar"** — a Twitter/X trend tracker that monitors AI news as it breaks on Twitter, categorises it, and surfaces the top trending topics before they reach YouTube.

This is built as a portfolio piece and live demo for a job application at **Klapital** (AI Content Specialist role). The job posting explicitly mentions "KI-Radar on Dauerbetrieb" (AI radar running 24/7) as a key requirement. This tool is the literal answer to that.

The deliverable is:
- A **GitHub repository** with clean code and a good README
- A **locally runnable Streamlit app** that can be demoed on screen (for a video recording)
- Looks and feels like a real internal tool — not a toy

---

## 2. Why It Exists (Context for Framing & README)

AI news breaks on Twitter/X first — from researchers, founders, OpenAI/Anthropic announcements, and viral threads. YouTube channels (like the one Klapital is building) always lag by 1–7 days. A tool that catches trending AI tweets in real time, before they hit mainstream coverage, gives a content team first-mover advantage on video topics.

This directly maps to the Klapital content workflow:
1. **AI Radar surfaces a trending tweet** (e.g. a new model release getting 10k retweets in 3 hours)
2. **Content team evaluates it** — is it worth a video?
3. **Script research begins** while competitors haven't even noticed yet

---

## 3. Tech Stack

- **Language:** Python 3.11+
- **UI:** Streamlit (runs locally with `streamlit run app.py`, looks like a real dashboard)
- **Data source:** Twitter/X API v2 via `tweepy` (free Basic tier, or fallback to mock data)
- **Storage:** SQLite (lightweight, no setup needed, persists between runs)
- **Categorisation:** Rule-based keyword matching + optional OpenAI/Claude API call for smart tagging
- **Scheduling:** `schedule` Python library (runs refresh in background every 30 min)
- **Export:** Markdown daily digest + optional email via SMTP

### Dependencies (requirements.txt)
```
streamlit>=1.32.0
tweepy>=4.14.0
pandas>=2.0.0
plotly>=5.0.0
schedule>=1.2.0
python-dotenv>=1.0.0
sqlite3  # built-in
requests>=2.31.0
```

---

## 4. Twitter API Setup

### Option A: With Twitter API (recommended for production demo)
1. Go to developer.twitter.com → create a free account
2. Create a Project + App → get Bearer Token
3. Free Basic tier: 500k tweet reads/month, recent search (last 7 days)
4. Store in `.env` file: `TWITTER_BEARER_TOKEN=xxx`

### Option B: Mock Data Mode (for offline demo / video)
- If no Bearer Token is present in `.env`, the app runs in **mock mode**
- Mock data is realistic — pre-loaded with 30–50 sample AI tweets from the accounts listed below
- The UI looks identical — suitable for a demo video
- Mock mode shows a yellow banner: "Running in demo mode — connect Twitter API for live data"

---

## 5. Accounts & Hashtags to Monitor

### Key AI Twitter Accounts (by handle, no @ needed in API)
```python
ACCOUNTS = [
    "sama",           # Sam Altman (OpenAI CEO)
    "AnthropicAI",    # Anthropic official
    "OpenAI",         # OpenAI official
    "GoogleDeepMind", # DeepMind official
    "ylecun",         # Yann LeCun (Meta AI)
    "karpathy",       # Andrej Karpathy
    "emollick",       # Ethan Mollick (Wharton, AI adoption)
    "DrJimFan",       # Jim Fan (NVIDIA)
    "_akhaliq",       # AK — posts every new HuggingFace paper
    "mistralai",      # Mistral AI official
    "huggingface",    # HuggingFace official
    "gdb",            # Greg Brockman (OpenAI)
    "fchollet",       # François Chollet (Keras, ARC benchmark)
    "rohanpaul_ai",   # AI news aggregator
    "scaling01",      # Scaling laws / research
    "alexalbert__",   # Alex Albert (Anthropic, Claude)
]
```

### Hashtags & Keywords
```python
KEYWORDS = [
    "#AI", "#LLM", "#GenAI", "#AINews",
    "model release", "open source model",
    "beats GPT-4", "new benchmark", "context window",
    "Claude", "GPT", "Gemini", "Llama", "Mistral",
    "multimodal", "agents", "reasoning model",
    "AI agent", "fine-tuning", "RLHF",
]
```

---

## 6. Categorisation System

Each tweet gets auto-tagged with one of these categories:

| Category | Emoji | Trigger keywords |
|---|---|---|
| Model Release | 🚀 | "new model", "release", "launch", "introducing", "available now", "open source", "weights" |
| New Tool / Product | 🛠️ | "API", "feature", "update", "plugin", "integration", "app", "tool" |
| Research Paper | 📄 | "paper", "arxiv", "benchmark", "we show", "our research", "study" |
| Funding / Business | 💰 | "funding", "raised", "valuation", "Series", "billion", "acquisition" |
| Viral Debate | 🔥 | "hot take", "unpopular opinion", "thread", "disagree", "I think", "actually" |
| Benchmark / Numbers | 📊 | "%", "score", "beats", "outperforms", "SOTA", "state of the art", "vs GPT" |

---

## 7. "Trend Score" Algorithm

The app ranks tweets by **engagement velocity**, not raw likes. This catches things that are blowing up *right now* rather than old tweets with accumulated likes.

```
trend_score = (likes + retweets * 3 + replies * 2) / hours_since_posted
```

Tweets posted in the last 6 hours with rapid engagement get surfaced first. This is the core value of the tool — it catches things before they plateau.

---

## 8. App UI — Screens & Layout

### Main Dashboard (`app.py`)

**Header:**
- App name: **AI Radar** 
- Subtitle: "AI news on Twitter — before it lands on YouTube"
- Last updated timestamp + Refresh button
- Demo mode badge (if no API key)

**Left sidebar filters:**
- Time range: Last 2h / 6h / 24h / 7 days
- Category filter: All / Model Release / Tool / Paper / Funding / Debate / Benchmark
- Min engagement threshold slider (e.g. min 100 interactions)
- Account filter: All accounts / specific account

**Main content — Top Trending (ranked by trend score):**
- Card for each tweet showing:
  - Account name + handle + profile pic (or placeholder)
  - Tweet text (truncated at 280 chars)
  - Category badge (emoji + label)
  - Trend score + raw metrics (❤️ likes, 🔁 retweets, 💬 replies)
  - Posted time (e.g. "3 hours ago")
  - Link to original tweet
  - One-click "Save as content idea" button (saves to SQLite ideas list)

**Right panel — Saved Content Ideas:**
- List of tweets the user starred as potential video topics
- Export button → exports to `content_ideas.md`

**Bottom section — Trend Graph:**
- Plotly line chart showing tweet volume per hour (last 24h)
- Colour-coded by category
- Helps visualise when topics are spiking

### Second tab: Daily Digest
- Auto-generated markdown summary of the top 5 tweets of the day
- Format: "🚀 **[Model Release]** Anthropic released Claude 4 — 14.2k interactions in 3 hours. [Link]"
- Copy to clipboard button
- Export as `.md` file button

### Third tab: Settings
- Twitter API key input (saves to `.env`)
- Account list editor (add/remove accounts)
- Keyword list editor
- Refresh interval setting (15 / 30 / 60 min)
- Test connection button

---

## 9. File Structure

```
ai-radar/
├── app.py                  # Main Streamlit app
├── tracker.py              # Twitter API fetching logic
├── categoriser.py          # Tweet categorisation
├── database.py             # SQLite operations
├── mock_data.py            # Realistic mock tweets for demo mode
├── digest.py               # Daily digest generation
├── scheduler.py            # Background refresh scheduler
├── requirements.txt
├── .env.example            # Template: TWITTER_BEARER_TOKEN=your_token_here
├── .gitignore              # Ignores .env and the SQLite DB
└── README.md               # Setup instructions + screenshots
```

---

## 10. README Content (key sections)

The README should include:
1. **What it does** — 2 sentences, sharp
2. **Why it exists** — the YouTube lag problem
3. **Setup** — 5 steps max: clone → pip install → add API key → run
4. **Screenshots** (add after building)
5. **How the trend score works** — explain the velocity formula
6. **Roadmap** (optional, looks professional): Slack integration, email digests, Claude-powered summaries

---

## 11. Mock Data Spec (for demo mode)

Pre-populate `mock_data.py` with 40+ realistic tweets covering all categories. Examples:

```python
MOCK_TWEETS = [
    {
        "id": "1001",
        "author": "AnthropicAI",
        "text": "Introducing Claude 4 — our most capable model yet. Available now via API. 200k context window, improved reasoning, and new tool use capabilities. Try it today: anthropic.com/claude",
        "likes": 8420,
        "retweets": 3100,
        "replies": 890,
        "posted_at": "2026-04-11T08:30:00Z",
        "url": "https://twitter.com/AnthropicAI/status/1001",
        "category": "model_release"
    },
    {
        "id": "1002", 
        "author": "karpathy",
        "text": "the best way to understand transformers is still to implement one from scratch. nothing has changed here. all the blog posts in the world don't substitute for writing the code.",
        "likes": 12300,
        "retweets": 2800,
        "replies": 440,
        "posted_at": "2026-04-11T06:15:00Z",
        "url": "https://twitter.com/karpathy/status/1002",
        "category": "viral_debate"
    },
    # ... add 38 more covering all categories, spread across past 24h
]
```

Spread the mock tweets across the last 24 hours with varied engagement levels so the trend graph looks realistic.

---

## 12. Video Demo Script (what to show on screen)

When recording the demo for Klapital:

1. **Open terminal** → `streamlit run app.py` → app opens in browser
2. **Show main dashboard** — cards with real-looking AI tweets, categories, trend scores
3. **Use the time filter** — switch from 24h to 6h → fewer, more recent items appear
4. **Click a category filter** — show only "Model Release" tweets
5. **Star a tweet** as a content idea → it appears in the right panel
6. **Switch to Daily Digest tab** → show the auto-generated markdown summary
7. **Export to .md** → show the file
8. **Switch to Settings** → briefly show where you'd add the API key
9. **Close with**: "This is what the Klapital content team would open every morning."

---

## 13. GitHub Repository Setup

- Repo name: `ai-radar` (or `twitter-ai-tracker`)
- Description: "A real-time Twitter/X trend tracker for AI news — surfaces trending topics before they reach YouTube."
- Visibility: **Public**
- Add topics: `ai`, `twitter`, `streamlit`, `trend-tracking`, `content-tools`
- License: MIT
- Pin the repo on GitHub profile

---

## 14. First Prompt for Claude Code

Paste this after loading the context file:

> "Build the AI Radar app described in this context file. Start with the file structure and `app.py`. Use Streamlit. Implement mock mode first (no API key needed) so the app runs out of the box. Then add the real Twitter API integration in `tracker.py`. Make the dashboard look clean and professional — this is a portfolio piece. Follow the UI spec exactly."

---

*Context written: April 2026 | For Klapital AI Content Specialist application*
