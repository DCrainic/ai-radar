"""
KI-Radar — ONEFRAME Content Studio
Streamlit-App für KI-Trend-Tracking auf X/Twitter
Starten: streamlit run app.py
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from categoriser import all_categories, get_meta
from database import Database
from digest import generate_digest
from scheduler import start as start_scheduler
from tracker import ACCOUNTS, YOUTUBE_CREATORS, RESEARCH_ACCOUNTS, TwitterTracker

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="KI-Radar · ONEFRAME",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Markenfarben ──────────────────────────────────────────────────────────────
BRAND   = "#FF4500"   # ONEFRAME orange-red
BRAND_D = "#CC3700"   # darker variant for hover

# ── Global CSS ────────────────────────────────────────────────────────────────

st.markdown(
    f"""
    <style>
    /* ── Layout ── */
    .block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; }}

    /* ── ONEFRAME Sidebar-Header ── */
    .of-brand {{
        background: {BRAND};
        border-radius: 10px;
        padding: 13px 16px 11px;
        margin-bottom: 20px;
    }}
    .of-brand-name {{
        color: #fff;
        font-size: 20px;
        font-weight: 900;
        letter-spacing: 3px;
        line-height: 1;
    }}
    .of-brand-sub {{
        color: rgba(255,255,255,.75);
        font-size: 11px;
        margin-top: 3px;
        letter-spacing: .5px;
    }}

    /* ── Tweet-Karten ── */
    .tweet-card {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 18px 12px;
        margin-bottom: 10px;
        box-shadow: 0 1px 4px rgba(0,0,0,.06);
        transition: box-shadow .15s ease;
    }}
    .tweet-card:hover {{ box-shadow: 0 4px 14px rgba(0,0,0,.10); }}

    /* ── Kategorie-Badges ── */
    .badge {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 100px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .4px;
        text-transform: uppercase;
    }}
    .badge-youtube_signal    {{ background:#FEF2F2; color:#B91C1C; }}
    .badge-model_release     {{ background:#EFF6FF; color:#1D4ED8; }}
    .badge-tool_product      {{ background:#F0FDF4; color:#166534; }}
    .badge-research_paper    {{ background:#FEF9C3; color:#713F12; }}
    .badge-funding_business  {{ background:#FFF7ED; color:#9A3412; }}
    .badge-viral_debate      {{ background:#FFF1F2; color:#BE123C; }}
    .badge-benchmark_numbers {{ background:#F5F3FF; color:#5B21B6; }}

    /* ── Trend-Score-Pill (Markenfarbe) ── */
    .score-pill {{
        display: inline-block;
        background: {BRAND};
        color: #fff;
        border-radius: 100px;
        padding: 2px 10px;
        font-size: 12px;
        font-weight: 700;
    }}

    /* ── Autor / Handle ── */
    .author {{ font-weight: 700; font-size: 15px; color: #0f172a; }}
    .handle {{ font-size: 13px; color: #64748b; }}

    /* ── Tweet-Text ── */
    .tweet-text {{
        font-size: 14px;
        line-height: 1.55;
        color: #1e293b;
        margin: 8px 0 10px;
    }}

    /* ── Metriken ── */
    .metrics {{ font-size: 13px; color: #64748b; }}

    /* ── YouTube-Signal-Karte ── */
    .yt-signal-card {{
        background: #fff5f5;
        border: 1.5px solid #fca5a5;
        border-radius: 12px;
        padding: 16px 18px 14px;
        margin-bottom: 12px;
        box-shadow: 0 1px 4px rgba(185,28,28,.08);
    }}
    .yt-signal-card:hover {{ box-shadow: 0 4px 14px rgba(185,28,28,.15); }}

    /* ── Adaptions-Karte ── */
    .adaptation-card {{
        background: #f0fdf4;
        border: 1px solid #86efac;
        border-radius: 8px;
        padding: 12px 14px;
        margin-top: 10px;
        font-size: 13px;
        line-height: 1.6;
    }}
    .adaptation-row {{
        display: flex;
        gap: 8px;
        margin-bottom: 5px;
    }}
    .adaptation-label {{
        font-weight: 700;
        color: #15803d;
        min-width: 130px;
        flex-shrink: 0;
    }}
    .adaptation-value {{
        color: #1e293b;
    }}

    /* ── Tier-Badge ── */
    .tier-badge-1 {{
        display: inline-block;
        background: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #fca5a5;
        border-radius: 100px;
        padding: 1px 8px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: .5px;
        text-transform: uppercase;
        margin-right: 6px;
    }}
    .tier-badge-2 {{
        display: inline-block;
        background: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #93c5fd;
        border-radius: 100px;
        padding: 1px 8px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: .5px;
        text-transform: uppercase;
        margin-right: 6px;
    }}

    /* ── Ideen-Karte ── */
    .idea-card {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 8px;
        font-size: 13px;
    }}

    /* ── Demo-Banner ── */
    .demo-banner {{
        background: #fefce8;
        border: 1px solid #fde68a;
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 13px;
        color: #92400e;
        margin-bottom: 1rem;
    }}

    /* ── App-Titel ── */
    .app-title {{
        font-size: 28px;
        font-weight: 900;
        color: #0f172a;
        letter-spacing: -0.5px;
        line-height: 1.1;
        margin-bottom: 2px;
    }}
    .app-subtitle {{
        font-size: 14px;
        color: #64748b;
        margin-top: 0;
    }}
    .brand-tag {{
        color: {BRAND};
        font-weight: 800;
    }}

    /* ── Credit-Footer ── */
    .credit {{
        font-size: 11px;
        color: #94a3b8;
        line-height: 1.6;
        margin-top: 8px;
    }}

    /* ── Abschnitts-Überschriften ── */
    h3 {{ font-size: 16px !important; font-weight: 700 !important; }}

    /* ── Streamlit-Chrome ausblenden ── */
    #MainMenu                        {{ visibility: hidden; }}
    footer                           {{ visibility: hidden; }}
    .stDeployButton                  {{ display: none !important; }}
    /* Deliberately NOT hiding the header — it contains the sidebar reopen button */
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Hilfsfunktionen ───────────────────────────────────────────────────────────

ZEITRAUM_OPTIONEN: dict[str, int] = {
    "Letzte 2 Stunden":  2,
    "Letzte 6 Stunden":  6,
    "Letzte 24 Stunden": 24,
    "Letzte 7 Tage":     168,
}

KATEGORIE_OPTIONEN: dict[str, str] = {
    "Alle Kategorien": "all",
    **{f"{m['emoji']} {m['label']}": k for k, m in {c["key"]: c for c in all_categories()}.items()},
}


def _fmt_num(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def _vor(raw: str) -> str:
    """Gibt 'vor Xh' etc. auf Deutsch zurück."""
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        secs = int((datetime.now(timezone.utc) - dt).total_seconds())
        if secs < 60:
            return f"vor {secs}s"
        if secs < 3600:
            return f"vor {secs // 60}m"
        if secs < 86400:
            return f"vor {secs // 3600}h"
        return f"vor {secs // 86400}d"
    except (ValueError, TypeError):
        return ""


# ── Initialisierung (einmal pro Session) ─────────────────────────────────────

@st.cache_resource
def _init():
    db = Database()
    tracker = TwitterTracker()
    if db.tweet_count() == 0:
        db.upsert_tweets(tracker.fetch())

    def _refresh():
        db.upsert_tweets(tracker.fetch())

    start_scheduler(_refresh, interval_minutes=30)
    return db, tracker


db, tracker = _init()

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now(timezone.utc)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    # ONEFRAME Markenkopf
    st.markdown(
        """
        <div class="of-brand">
            <div class="of-brand-name">ONEFRAME</div>
            <div class="of-brand-sub">KI-Radar · Content Studio</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Filter")

    zeitraum_label = st.selectbox("Zeitraum", list(ZEITRAUM_OPTIONEN.keys()), index=2)
    stunden = ZEITRAUM_OPTIONEN[zeitraum_label]

    kat_label = st.selectbox("Kategorie", list(KATEGORIE_OPTIONEN.keys()))
    kat_key = KATEGORIE_OPTIONEN[kat_label]

    min_eng = st.slider("Mindest-Engagement", min_value=0, max_value=5000, value=100, step=50)

    account_liste = db.get_setting("accounts", ACCOUNTS)

    # Build display list with tier labels
    tier_options = (
        ["Alle"]
        + [f"📹 {a}" for a in YOUTUBE_CREATORS if a in account_liste]
        + [f"🔬 {a}" for a in RESEARCH_ACCOUNTS if a in account_liste]
    )
    account_filter_raw = st.selectbox("Account", tier_options)
    # Strip the tier emoji prefix (format is "EMOJI handle" — split on first space)
    account_filter = account_filter_raw.split(" ", 1)[-1] if " " in account_filter_raw else account_filter_raw

    st.markdown("---")
    st.markdown(
        f"<span style='font-size:12px;color:#94a3b8'>Zuletzt aktualisiert: "
        f"{st.session_state.last_refresh.strftime('%H:%M UTC')}</span>",
        unsafe_allow_html=True,
    )

    # Credits
    st.markdown(
        """
        <div style="margin-top:24px">
            <div class="credit">
                Built by <strong>Dominique Crainic</strong><br>
                ONEFRAME Content Studio
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Haupt-Tabs ────────────────────────────────────────────────────────────────

tab_dashboard, tab_digest, tab_einstellungen = st.tabs(
    ["📊 Dashboard", "📋 Tages-Digest", "⚙️ Einstellungen"]
)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

with tab_dashboard:

    # Kopfzeile
    hcol1, hcol2 = st.columns([5, 1])
    with hcol1:
        st.markdown(
            "<div class='app-title'>📡 KI-Radar"
            "<span class='brand-tag'> · ONEFRAME</span></div>"
            "<p class='app-subtitle'>"
            "📹 <strong>Tier 1:</strong> AI-YouTuber-Signale &nbsp;|&nbsp; "
            "🔬 <strong>Tier 2:</strong> Forschungs-Accounts &nbsp;—&nbsp; "
            "KI-Trends erkennen, bevor sie auf YouTube landen</p>",
            unsafe_allow_html=True,
        )
    with hcol2:
        st.markdown("<div style='margin-top:26px'></div>", unsafe_allow_html=True)
        if st.button("🔄 Aktualisieren", use_container_width=True):
            with st.spinner("Neue Tweets werden geladen…"):
                db.upsert_tweets(tracker.fetch())
                st.session_state.last_refresh = datetime.now(timezone.utc)
            st.rerun()

    # Demo-Modus-Banner — check env directly so it reflects the current state
    if not os.getenv("TWITTER_BEARER_TOKEN"):
        st.markdown(
            "<div class='demo-banner'>⚠️ <strong>Demo-Modus</strong> — "
            "läuft mit realistischen Beispiel-Daten. Füge deinen Twitter Bearer Token "
            "unter <strong>Einstellungen</strong> hinzu, um Live-Daten zu erhalten.</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Gefilterte Tweets laden
    account_arg = None if account_filter == "Alle" else account_filter
    tweets = db.get_tweets(
        hours=stunden,
        category=kat_key,
        min_engagement=min_eng,
        account=account_arg,
    )

    # Aufteilen nach Tier
    from tracker import YOUTUBE_CREATORS as _YT_CREATORS
    yt_signals = [t for t in tweets if t.get("category") == "youtube_signal"]
    other_tweets = [t for t in tweets if t.get("category") != "youtube_signal"]

    # ── Tier 1: YouTube Früh-Signale ─────────────────────────────────────────
    if yt_signals and (kat_key == "all" or kat_key == "youtube_signal"):
        st.markdown(f"### 📹 YouTube Früh-Signale ({len(yt_signals)})")
        st.caption("Diese Creator kündigen Themen zuerst auf X an — Frühwarnsignal, was bald auf YouTube landet.")

        for tweet in yt_signals:
            vor = _vor(tweet.get("posted_at", ""))
            score = tweet.get("trend_score", 0)
            text = tweet.get("text", "")
            adaptation = tweet.get("adaptation", {})

            # Signal Card
            adapt_html = ""
            if adaptation:
                adapt_html = f"""
                <div class="adaptation-card">
                    <div style="font-weight:700;color:#15803d;margin-bottom:8px;font-size:12px;text-transform:uppercase;letter-spacing:.5px">🎬 Adaptionsvorschlag für deinen Kanal</div>
                    <div class="adaptation-row"><span class="adaptation-label">🇺🇸 Original-Format</span><span class="adaptation-value">{adaptation.get('original_format','–')}</span></div>
                    <div class="adaptation-row"><span class="adaptation-label">🇩🇪 Deutscher Titel</span><span class="adaptation-value">{adaptation.get('german_title','–')}</span></div>
                    <div class="adaptation-row"><span class="adaptation-label">🎯 Zielgruppe</span><span class="adaptation-value">{adaptation.get('audience_fit','–')}</span></div>
                    <div class="adaptation-row"><span class="adaptation-label">🪝 Hook-Idee</span><span class="adaptation-value"><em>{adaptation.get('hook','–')}</em></span></div>
                    <div class="adaptation-row"><span class="adaptation-label">🖼️ Thumbnail</span><span class="adaptation-value">{adaptation.get('thumbnail','–')}</span></div>
                    <div class="adaptation-row"><span class="adaptation-label">📋 Videostruktur</span><span class="adaptation-value">{adaptation.get('struktur','–')}</span></div>
                </div>
                """

            st.markdown(
                f"""
                <div class="yt-signal-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                        <span><span class="tier-badge-1">Tier 1 · YouTuber</span>
                        <span class="badge badge-youtube_signal">📹 YouTube Signal</span></span>
                        <span class="handle">{vor}</span>
                    </div>
                    <div class="author">@{tweet['author']}</div>
                    <div class="tweet-text">{text}</div>
                    <div class="metrics">
                        ❤️ {_fmt_num(tweet.get('likes', 0))}&nbsp;&nbsp;
                        🔁 {_fmt_num(tweet.get('retweets', 0))}&nbsp;&nbsp;
                        💬 {_fmt_num(tweet.get('replies', 0))}&nbsp;&nbsp;&nbsp;
                        <span class="score-pill">⚡ {score:.0f}</span>
                    </div>
                    {adapt_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

            btn1, btn2 = st.columns(2)
            with btn1:
                st.link_button("🔗 Tweet ansehen", tweet.get("url", "#"), use_container_width=True)
            with btn2:
                gespeichert = db.is_idea(tweet["id"])
                label = "✅ Gespeichert" if gespeichert else "🎬 Als Video-Idee"
                if st.button(label, key=f"save_{tweet['id']}", use_container_width=True, disabled=gespeichert):
                    db.save_idea(tweet["id"])
                    st.rerun()

            st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)

        st.markdown("---")

    # Zweispaltiges Layout: Tweets | Video-Ideen
    col_tweets, col_ideen = st.columns([2, 1], gap="large")

    with col_tweets:
        display_tweets = other_tweets if (kat_key == "all" or kat_key != "youtube_signal") else []
        st.markdown(f"### 🔥 Top Trends — Forschung & Industrie ({len(display_tweets)} Tweets)")

        if not display_tweets and not yt_signals:
            st.info("Keine Tweets gefunden. Zeitraum erweitern oder Mindest-Engagement verringern.")
        elif not display_tweets and kat_key != "youtube_signal":
            st.caption("Alle Treffer sind YouTube-Signale (oben angezeigt).")
        else:
            for tweet in display_tweets:
                meta = get_meta(tweet["category"])
                vor = _vor(tweet.get("posted_at", ""))
                score = tweet.get("trend_score", 0)
                text = tweet.get("text", "")

                st.markdown(
                    f"""
                    <div class="tweet-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                            <span><span class="tier-badge-2">Tier 2 · Research</span>
                            <span class="badge badge-{tweet['category']}">{meta['emoji']} {meta['label']}</span></span>
                            <span class="handle">{vor}</span>
                        </div>
                        <div class="author">@{tweet['author']}</div>
                        <div class="tweet-text">{text}</div>
                        <div class="metrics">
                            ❤️ {_fmt_num(tweet.get('likes', 0))}&nbsp;&nbsp;
                            🔁 {_fmt_num(tweet.get('retweets', 0))}&nbsp;&nbsp;
                            💬 {_fmt_num(tweet.get('replies', 0))}&nbsp;&nbsp;&nbsp;
                            <span class="score-pill">⚡ {score:.0f}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                btn1, btn2 = st.columns(2)
                with btn1:
                    st.link_button(
                        "🔗 Tweet ansehen",
                        tweet.get("url", "#"),
                        use_container_width=True,
                    )
                with btn2:
                    gespeichert = db.is_idea(tweet["id"])
                    label = "✅ Gespeichert" if gespeichert else "🎬 Als Video-Idee"
                    if st.button(label, key=f"save_{tweet['id']}", use_container_width=True, disabled=gespeichert):
                        db.save_idea(tweet["id"])
                        st.rerun()

                st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)

    with col_ideen:
        st.markdown("### 🎬 Video-Ideen")

        ideen = db.get_ideas()

        if not ideen:
            st.markdown(
                "<p style='color:#94a3b8;font-size:13px'>Noch keine Ideen gespeichert.<br>"
                "Klicke auf <strong>🎬 Als Video-Idee</strong> bei einem Tweet.</p>",
                unsafe_allow_html=True,
            )
        else:
            for idee in ideen:
                meta = get_meta(idee["category"])
                st.markdown(
                    f"""
                    <div class="idea-card">
                        <div style="display:flex;justify-content:space-between">
                            <span class="badge badge-{idee['category']}">{meta['emoji']} {meta['label']}</span>
                            <span class="handle">@{idee['author']}</span>
                        </div>
                        <p style="margin:6px 0 4px;font-size:13px;color:#1e293b">
                            {idee['text'][:140]}{'…' if len(idee['text']) > 140 else ''}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                rm_col, link_col = st.columns(2)
                with rm_col:
                    if st.button("🗑️ Entfernen", key=f"rm_{idee['id']}", use_container_width=True):
                        db.remove_idea(idee["id"])
                        st.rerun()
                with link_col:
                    st.link_button("🔗 Ansehen", idee.get("url", "#"), use_container_width=True)

            st.markdown("---")
            content = generate_digest(ideen, top_n=len(ideen))
            st.download_button(
                label="📥 Ideen exportieren (.md)",
                data=content,
                file_name="oneframe_video_ideen.md",
                mime="text/markdown",
                use_container_width=True,
            )

    # ── Trend-Grafik ──────────────────────────────────────────────────────────

    st.markdown("---")
    st.markdown("### 📈 Tweet-Volumen (letzte 24 Stunden)")

    volume_data = db.get_hourly_volume(hours=24)

    if volume_data:
        df = pd.DataFrame(volume_data)
        df["hour"] = pd.to_datetime(df["hour"])
        df["category_label"] = df["category"].apply(
            lambda c: f"{get_meta(c)['emoji']} {get_meta(c)['label']}"
        )
        farben = {
            f"{get_meta(k)['emoji']} {get_meta(k)['label']}": get_meta(k)["color"]
            for k in ["model_release", "tool_product", "research_paper",
                      "funding_business", "viral_debate", "benchmark_numbers"]
        }
        fig = px.line(
            df,
            x="hour",
            y="count",
            color="category_label",
            color_discrete_map=farben,
            labels={"hour": "", "count": "Tweets", "category_label": "Kategorie"},
            template="plotly_white",
        )
        fig.update_traces(mode="lines+markers", line_width=2, marker_size=5)
        fig.update_layout(
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("Die Trend-Grafik füllt sich mit der Zeit, sobald mehr Tweets gesammelt werden.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — TAGES-DIGEST
# ═══════════════════════════════════════════════════════════════════════════════

with tab_digest:
    st.markdown("## 📋 Tages-Digest")
    st.markdown(
        "<p style='color:#64748b;font-size:14px'>"
        "Tägliche Zusammenfassung: YouTube Früh-Signale mit Adaptionsvorschlag + Top-Trends. "
        "Direkt in Notion, Slack oder dein Morgen-Briefing kopieren.</p>",
        unsafe_allow_html=True,
    )

    top_tweets = db.get_tweets(hours=24, limit=20)
    digest_md = generate_digest(top_tweets, top_n=5)

    st.markdown("---")
    st.markdown(digest_md)
    st.markdown("---")

    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.download_button(
            label="⬇️ Als .md exportieren",
            data=digest_md,
            file_name=f"oneframe_digest_{datetime.now().strftime('%Y-%m-%d')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with dcol2:
        st.code(digest_md, language="markdown")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — EINSTELLUNGEN
# ═══════════════════════════════════════════════════════════════════════════════

with tab_einstellungen:
    st.markdown("## ⚙️ Einstellungen")

    # ── API-Schlüssel ─────────────────────────────────────────────────────────

    st.markdown("### 🔑 Twitter / X API")
    current_token = os.getenv("TWITTER_BEARER_TOKEN", "")
    token_display = ("●" * 20 + current_token[-6:]) if current_token else ""

    new_token = st.text_input(
        "Bearer Token",
        value=token_display if current_token else "",
        type="password",
        placeholder="Bearer Token hier einfügen…",
        help="Kostenlos erhältlich auf developer.twitter.com",
    )

    if st.button("💾 API-Schlüssel speichern"):
        if new_token and not new_token.startswith("●"):
            # 1. Persist to .env
            env_path = os.path.join(os.path.dirname(__file__), ".env")
            existing: list[str] = []
            if os.path.exists(env_path):
                with open(env_path) as f:
                    existing = [l for l in f.readlines() if not l.startswith("TWITTER_BEARER_TOKEN")]
            existing.append(f"TWITTER_BEARER_TOKEN={new_token}\n")
            with open(env_path, "w") as f:
                f.writelines(existing)
            # 2. Activate immediately in the running process
            os.environ["TWITTER_BEARER_TOKEN"] = new_token
            # 3. Clear cached tracker so it reinitialises with the new token
            st.cache_resource.clear()
            st.success("✅ API-Schlüssel gespeichert — Live-Modus wird aktiviert…")
            st.rerun()
        else:
            st.warning("Bitte einen gültigen Token eingeben (nicht den maskierten Platzhalter).")

    if os.getenv("TWITTER_BEARER_TOKEN"):
        st.markdown(
            "<span style='color:#16a34a;font-size:13px'>✅ Bearer Token erkannt — Live-Modus aktiv</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<span style='color:#d97706;font-size:13px'>⚠️ Kein Bearer Token — Demo-Modus aktiv</span>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Account-Liste ─────────────────────────────────────────────────────────

    st.markdown("### 👤 Überwachte Accounts")

    ecol1, ecol2 = st.columns(2)
    with ecol1:
        st.markdown("**📹 Tier 1 — AI-YouTuber (Früh-Signale)**")
        st.caption("Kündigen Themen auf X an, bevor Videos live gehen")
        yt_text = st.text_area(
            "YouTuber-Handles (ohne @)",
            value="\n".join(db.get_setting("youtube_creators", YOUTUBE_CREATORS)),
            height=160,
            key="yt_accounts",
        )
    with ecol2:
        st.markdown("**🔬 Tier 2 — Forschung & Industrie**")
        st.caption("AI-Labore, Forscher und Industrie-Experten")
        research_text = st.text_area(
            "Forschungs-Handles (ohne @)",
            value="\n".join(db.get_setting("research_accounts", RESEARCH_ACCOUNTS)),
            height=160,
            key="research_accounts",
        )

    if st.button("💾 Accounts speichern"):
        yt_updated = [a.strip().lstrip("@") for a in yt_text.splitlines() if a.strip()]
        research_updated = [a.strip().lstrip("@") for a in research_text.splitlines() if a.strip()]
        db.set_setting("youtube_creators", yt_updated)
        db.set_setting("research_accounts", research_updated)
        db.set_setting("accounts", yt_updated + research_updated)
        st.success(f"✅ {len(yt_updated)} YouTuber + {len(research_updated)} Forschungs-Accounts gespeichert.")

    st.markdown("---")

    # ── Keywords ──────────────────────────────────────────────────────────────

    st.markdown("### 🔍 Keywords & Hashtags")
    from tracker import KEYWORDS as DEFAULT_KEYWORDS  # noqa: E402
    current_keywords = db.get_setting("keywords", DEFAULT_KEYWORDS)
    keywords_text = st.text_area(
        "Ein Keyword pro Zeile",
        value="\n".join(current_keywords),
        height=200,
        help="Werden für die Filterung relevanter Tweets in der Live-API-Abfrage verwendet.",
    )
    if st.button("💾 Keywords speichern"):
        updated_kw = [k.strip() for k in keywords_text.splitlines() if k.strip()]
        db.set_setting("keywords", updated_kw)
        st.success(f"{len(updated_kw)} Keywords gespeichert.")

    st.markdown("---")

    # ── Aktualisierungsintervall ───────────────────────────────────────────────

    st.markdown("### ⏱️ Automatisches Aktualisierungsintervall")
    interval_opts = {15: "Alle 15 Minuten", 30: "Alle 30 Minuten", 60: "Jede Stunde"}
    current_interval = db.get_setting("refresh_interval", 30)
    selected_interval = st.selectbox(
        "Intervall",
        options=list(interval_opts.keys()),
        format_func=lambda x: interval_opts[x],
        index=list(interval_opts.keys()).index(current_interval) if current_interval in interval_opts else 1,
    )
    if st.button("💾 Intervall speichern"):
        db.set_setting("refresh_interval", selected_interval)
        st.success("Intervall gespeichert. App neu starten, um die Änderung zu übernehmen.")

    st.markdown("---")

    # ── Verbindungstest ───────────────────────────────────────────────────────

    st.markdown("### 🧪 Verbindungstest")
    if st.button("▶️ Twitter API testen"):
        if not current_token:
            st.error("Kein Bearer Token konfiguriert. Bitte zuerst oben hinzufügen.")
        else:
            with st.spinner("Verbindung wird getestet…"):
                try:
                    import tweepy  # type: ignore
                    client = tweepy.Client(bearer_token=current_token)
                    resp = client.search_recent_tweets(query="AI lang:en", max_results=10)
                    count = len(resp.data) if resp.data else 0
                    st.success(f"✅ Verbindung erfolgreich! {count} Test-Tweets abgerufen.")
                except Exception as exc:
                    st.error(f"❌ Verbindung fehlgeschlagen: {exc}")
