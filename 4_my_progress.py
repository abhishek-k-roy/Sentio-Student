"""My progress — has stress actually moved since starting Sentio?

Self-contained: the analytics, the styling, and the page all live here.
The only external touch-point is ``sentio.database`` (for reading check-ins)
and ``sentio.ui.setup`` (for the shared theme).
"""

import sqlite3

import numpy as np
import pandas as pd
import streamlit as st

from sentio import database, ui


# ============================================================================
# PAGE SETUP
# ============================================================================
ui.setup("My progress", "📈")


# ============================================================================
# PAGE-SPECIFIC STYLING
# ============================================================================
st.markdown(
    """
    <style>
    .sentio-impact-row {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin-bottom: .4rem;
    }
    .sentio-impact {
        flex: 1 1 220px;
        border-radius: 20px;
        padding: 1.15rem 1.3rem 1.25rem;
        border: 1px solid var(--s-line);
        background: linear-gradient(180deg, #FFFFFF 0%, #FCFCFF 100%);
        box-shadow: 0 1px 2px rgba(30,42,71,.04),
                    0 14px 30px -24px rgba(30,42,71,.4);
    }
    .sentio-impact--before {
        background: linear-gradient(160deg, #FDF2E9 0%, #FCF8F3 100%);
        border-color: #F2DFCC;
    }
    .sentio-impact--after {
        background: linear-gradient(160deg, #E4F5EF 0%, #F2FAF7 100%);
        border-color: #CFEAE1;
    }
    .sentio-impact-label {
        font-size: .71rem;
        font-weight: 700;
        letter-spacing: .14em;
        text-transform: uppercase;
        color: var(--s-muted);
    }
    .sentio-impact-value {
        font-family: 'Instrument Serif', Georgia, serif;
        font-size: 2.5rem;
        line-height: 1.05;
        color: var(--s-ink);
        margin: .3rem 0 .15rem 0;
    }
    .sentio-impact-sub {
        font-size: .82rem;
        color: var(--s-muted);
        line-height: 1.5;
    }
    .sentio-delta {
        display: inline-flex;
        align-items: center;
        gap: .3rem;
        border-radius: 999px;
        padding: .3rem .75rem;
        font-size: .8rem;
        font-weight: 700;
        margin-top: .5rem;
    }
    .sentio-delta--down { background: #DFF3EE; color: #1F6B5E; }
    .sentio-delta--up   { background: #FBE7E1; color: #A64C36; }
    .sentio-delta--flat { background: #E8EAFB; color: #3B4AB8; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# ANALYTICS
# ============================================================================
_STRESS_KEYS = ("stress_score", "stress_level", "stress", "score", "rating", "level")
_TIME_KEYS = ("created_at", "timestamp", "logged_at", "datetime", "created", "date", "ts")
_CONCERN_KEYS = ("concern", "concern_label", "category", "topic", "label")
_RESET_KEYS = ("suggestion_id", "suggestion", "reset_id", "reset", "chosen_suggestion")
_ACCEPTED_KEYS = ("accepted", "suggestion_accepted", "reset_accepted", "is_accepted", "chose_reset")

_EMPTY = pd.DataFrame(columns=["ts", "stress", "concern", "reset", "accepted"])


def _pick(columns, candidates):
    lookup = {str(c).strip().lower(): c for c in columns}
    for cand in candidates:
        if cand in lookup:
            return lookup[cand]
    return None


def _read_rows(user_id=None):
    """Load saved check-ins from Sentio's SQLite database."""
    try:
        return database.list_checkins()
    except Exception as exc:
        st.error(f"Could not load saved check-ins: {exc}")
        return []

def _read_sql():
    conn = None
    for name in ("get_connection", "connect", "get_conn", "connection"):
        obj = getattr(database, name, None)
        if callable(obj):
            try:
                conn = obj()
                break
            except Exception:
                conn = None
        elif obj is not None and hasattr(obj, "execute"):
            conn = obj
            break

    if conn is None:
        for name in ("DB_PATH", "DB_FILE", "DATABASE_PATH", "DATABASE", "DB"):
            path = getattr(database, name, None)
            if isinstance(path, (str, bytes)):
                try:
                    conn = sqlite3.connect(path)
                except Exception:
                    conn = None
                break

    if conn is None:
        return []

    for table in ("check_ins", "checkins", "check_in", "entries"):
        try:
            cur = conn.execute(f"SELECT * FROM {table}")
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        except Exception:
            continue
    return []


def _normalise(rows):
    if rows is None:
        return _EMPTY.copy()

    if isinstance(rows, pd.DataFrame):
        df = rows.copy()
    else:
        records = []
        for row in rows:
            if isinstance(row, dict):
                records.append(dict(row))
            elif hasattr(row, "keys"):
                records.append({k: row[k] for k in row.keys()})
            else:
                records.append(dict(row))
        df = pd.DataFrame(records)

    if df.empty:
        return _EMPTY.copy()

    stress_col = _pick(df.columns, _STRESS_KEYS)
    if stress_col is None:
        return _EMPTY.copy()

    out = pd.DataFrame()
    out["stress"] = pd.to_numeric(df[stress_col], errors="coerce")

    time_col = _pick(df.columns, _TIME_KEYS)
    out["ts"] = pd.to_datetime(df[time_col], errors="coerce") if time_col else pd.NaT

    concern_col = _pick(df.columns, _CONCERN_KEYS)
    out["concern"] = df[concern_col].astype(str) if concern_col else None

    reset_col = _pick(df.columns, _RESET_KEYS)
    out["reset"] = df[reset_col].astype(str) if reset_col else None

    accepted_col = _pick(df.columns, _ACCEPTED_KEYS)
    if accepted_col is not None:
        out["accepted"] = df[accepted_col].fillna(False).astype(bool)
    elif reset_col is not None:
        out["accepted"] = df[reset_col].notna()
    else:
        out["accepted"] = False

    out = out.dropna(subset=["stress"]).reset_index(drop=True)
    out = out.sort_values("ts", na_position="last").reset_index(drop=True)
    return out


class ImpactReport:
    """Plain container for everything the page needs to render."""

    def __init__(self):
        self.n = 0
        self.days = 0
        self.baseline = 0.0
        self.current = 0.0
        self.change = 0.0
        self.pct_change = 0.0
        self.best = 0.0
        self.worst = 0.0
        self.slope = 0.0
        self.direction = "gathering"
        self.headline = ""
        self.detail = ""
        self.scale = 10.0
        self.series = pd.DataFrame()
        self.resets = pd.DataFrame()
        self.top_helper = None


def _labels(ts_series):
    dates = [
        pd.Timestamp(t).strftime("%d %b") if pd.notna(t) else None
        for t in ts_series
    ]
    if any(x is None for x in dates) or len(set(dates)) != len(dates):
        out = []
        for i, t in enumerate(ts_series):
            if pd.notna(t):
                out.append(pd.Timestamp(t).strftime("%d %b · %H:%M"))
            else:
                out.append(f"Check-in {i + 1}")
        return out
    return dates


def _reset_effects(d):
    """Stress at the check-in where a reset was accepted vs the next check-in."""
    cols = ["reset", "before", "after", "delta"]
    if d.empty or "accepted" not in d:
        return pd.DataFrame(columns=cols)

    flags = d["accepted"].fillna(False).astype(bool).to_numpy()
    rows = []
    for i in range(len(d) - 1):
        if not flags[i]:
            continue
        name = d.at[i, "reset"]
        if not name or str(name).lower() in ("none", "nan", ""):
            name = "Your reset"
        rows.append({
            "reset": str(name),
            "before": float(d.at[i, "stress"]),
            "after": float(d.at[i + 1, "stress"]),
        })

    out = pd.DataFrame(rows, columns=["reset", "before", "after"])
    if not out.empty:
        out["delta"] = out["after"] - out["before"]
    return out


def _narrative(r):
    if r.n < 2:
        return (
            "One check-in so far",
            "Log another check-in and Sentio will start showing how your stress is moving.",
        )

    if r.direction == "improving":
        head = f"Your stress is down {abs(r.pct_change):.0f}% since you started."
        detail = (
            f"Across {r.n} check-ins your average moved from {r.baseline:.1f} to "
            f"{r.current:.1f}, and the trend line is still pointing down."
        )
    elif r.direction == "rising":
        head = "Your stress has been climbing recently."
        detail = (
            "That is worth paying attention to. A reset, a proper break, or talking "
            "to someone you trust are all reasonable next steps."
        )
    elif r.direction == "steady":
        head = "Your stress has been holding fairly steady."
        detail = (
            f"You have logged {r.n} check-ins and your average is sitting around "
            f"{r.current:.1f}. Steady is not failure — it is a baseline to build on."
        )
    else:
        head = "You are starting to build a picture."
        detail = "A few more check-ins and a clearer trend will appear here."

    return head, detail


def analyse(df, window=3):
    report = ImpactReport()
    if df is None or df.empty or "stress" not in df:
        return report

    d = df.dropna(subset=["stress"]).sort_values("ts", na_position="last").reset_index(drop=True)
    n = len(d)
    report.n = n
    if n == 0:
        return report

    scores = d["stress"].to_numpy(dtype=float)
    report.scale = 100.0 if float(np.nanmax(scores)) > 10 else 10.0
    report.best = float(np.nanmin(scores))
    report.worst = float(np.nanmax(scores))

    if d["ts"].notna().any():
        try:
            report.days = max(1, int((d["ts"].max() - d["ts"].min()).days))
        except Exception:
            report.days = 1

    k = 1 if n < 4 else min(window, max(1, n // 3))
    report.baseline = float(scores[:k].mean())
    report.current = float(scores[-k:].mean())
    report.change = report.current - report.baseline
    report.pct_change = (report.change / report.baseline * 100.0) if report.baseline else 0.0

    idx = np.arange(n, dtype=float)
    if n >= 2:
        slope, intercept = np.polyfit(idx, scores, 1)
        report.slope = float(slope)
        trend = intercept + slope * idx
    else:
        trend = scores

    mean = float(np.nanmean(scores)) or 1.0
    rel = report.slope / mean
    if n < 3:
        report.direction = "gathering"
    elif rel <= -0.015:
        report.direction = "improving"
    elif rel >= 0.015:
        report.direction = "rising"
    else:
        report.direction = "steady"

    report.series = pd.DataFrame({
        "label": _labels(d["ts"]),
        "Stress": scores,
        "Trend": trend,
        "Start line": report.baseline,
    })

    report.resets = _reset_effects(d)
    if not report.resets.empty:
        by_reset = report.resets.groupby("reset")["delta"].mean().sort_values()
        if not by_reset.empty:
            report.top_helper = str(by_reset.index[0])

    report.headline, report.detail = _narrative(report)
    return report


# ============================================================================
# PAGE HEADER
# ============================================================================
st.markdown('<div class="sentio-section-label">Your progress</div>', unsafe_allow_html=True)
st.markdown('<div class="sentio-h2">Has Sentio made a difference?</div>', unsafe_allow_html=True)
st.markdown(
    '<p class="sentio-lead">This page compares where your stress started with where it is '
    'now, and shows whether the resets you chose actually helped.</p>',
    unsafe_allow_html=True,
)
st.write("")


# ============================================================================
# LOAD + ANALYSE
# ============================================================================
with st.spinner("Reading your check-ins…"):
    history = _normalise(_read_rows())
report = analyse(history)


# ============================================================================
# EMPTY STATE
# ============================================================================
if report.n < 2:
    st.markdown(
        """
        <div class="sentio-note">
            <div class="sentio-note-icon">🌱</div>
            <strong>Not enough check-ins yet.</strong>
            <p>Progress needs at least two check-ins before a pattern can appear.
            Once you have a few, this page will show how your stress has moved over time.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    st.page_link(
        "pages/1_Student_Check_in.py",
        label="Start a check-in →",
        use_container_width=True,
    )
    st.stop()


scale = report.scale
unit = f"/{scale:.0f}"


# ============================================================================
# BEFORE / NOW
# ============================================================================
delta = report.change
if delta < -0.05:
    pill_class, arrow, word = "sentio-delta--down", "↓", "lower than where you started"
elif delta > 0.05:
    pill_class, arrow, word = "sentio-delta--up", "↑", "higher than where you started"
else:
    pill_class, arrow, word = "sentio-delta--flat", "→", "about the same as where you started"

st.markdown(
    f"""
    <div class="sentio-impact-row">
        <div class="sentio-impact sentio-impact--before">
            <div class="sentio-impact-label">Before Sentio</div>
            <div class="sentio-impact-value">{report.baseline:.1f}<span style="font-size:1rem;color:#8A96B0;">{unit}</span></div>
            <div class="sentio-impact-sub">Average of your earliest check-ins</div>
        </div>
        <div class="sentio-impact sentio-impact--after">
            <div class="sentio-impact-label">Now</div>
            <div class="sentio-impact-value">{report.current:.1f}<span style="font-size:1rem;color:#8A96B0;">{unit}</span></div>
            <div class="sentio-impact-sub">Average of your most recent check-ins</div>
            <span class="sentio-delta {pill_class}">{arrow} {abs(report.pct_change):.0f}% {word}</span>
        </div>
        <div class="sentio-impact">
            <div class="sentio-impact-label">Check-ins logged</div>
            <div class="sentio-impact-value">{report.n}</div>
            <div class="sentio-impact-sub">over {report.days} day{'s' if report.days != 1 else ''}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
st.markdown(f"**{report.headline}**")
st.markdown(f'<p class="sentio-lead">{report.detail}</p>', unsafe_allow_html=True)
st.write("")
st.write("")


# ============================================================================
# TREND CHART
# ============================================================================
st.markdown('<div class="sentio-section-label">Stress over time</div>', unsafe_allow_html=True)
st.markdown('<div class="sentio-h2">Your check-in history</div>', unsafe_allow_html=True)
st.write("")

st.line_chart(
    report.series,
    x="label",
    y=["Stress", "Trend", "Start line"],
    color=["#4C5FD5", "#E8945A", "#C3C9E0"],
    height=330,
)

st.caption(
    "**Stress** is what you reported. **Trend** is a straight line fitted through your "
    "check-ins — it shows the overall direction. **Start line** is where you began, so you "
    "can see how far you have moved from it."
)

st.write("")
st.write("")


# ============================================================================
# DID THE RESETS HELP?
# ============================================================================
st.markdown('<div class="sentio-section-label">Did the resets help?</div>', unsafe_allow_html=True)
st.markdown('<div class="sentio-h2">What happened after you chose a reset</div>', unsafe_allow_html=True)
st.write("")

resets = report.resets

if resets.empty:
    st.markdown(
        """
        <div class="sentio-note">
            <div class="sentio-note-icon">🧭</div>
            <strong>No reset comparisons yet.</strong>
            <p>When you accept a reset suggestion during a check-in, Sentio will compare your
            stress then against your next check-in and show the difference here.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    avg_delta = resets["delta"].mean()
    helped = int((resets["delta"] < 0).sum())
    total = len(resets)

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.metric("Resets chosen", total)
    with c2:
        st.metric("Followed by a drop", f"{helped}/{total}")
    with c3:
        st.metric(
            "Average change",
            f"{avg_delta:+.1f}",
            delta=f"{avg_delta:+.1f} {unit.strip('/')}",
            delta_color="inverse",
        )

    st.write("")

    grouped = (
        resets.groupby("reset", as_index=False)[["before", "after"]]
        .mean()
        .rename(columns={"before": "Before reset", "after": "After reset"})
    )
    st.bar_chart(
        grouped,
        x="reset",
        y=["Before reset", "After reset"],
        color=["#E8945A", "#2E9E8F"],
        height=300,
    )

    if report.top_helper:
        st.markdown(
            f"""
            <div class="sentio-note">
                <div class="sentio-note-icon">✨</div>
                <strong>Most helpful for you so far: {report.top_helper}</strong>
                <p>Across your check-ins, stress tended to fall the most after this reset.
                You might want to keep it in your toolkit.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")
st.write("")


# ============================================================================
# READING THIS PAGE
# ============================================================================
st.markdown('<div class="sentio-section-label">Reading this page</div>', unsafe_allow_html=True)
st.write("")

n1, n2 = st.columns(2, gap="medium")
with n1:
    st.markdown(
        """
        <div class="sentio-card">
            <div class="sentio-icon sentio-icon--teal">📉</div>
            <h3>A downward line is progress</h3>
            <p>Stress rarely drops in a straight line. What matters is the overall direction
            across several check-ins, not any single day.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with n2:
    st.markdown(
        """
        <div class="sentio-card">
            <div class="sentio-icon sentio-icon--peach">🔎</div>
            <h3>This is a mirror, not a diagnosis</h3>
            <p>These numbers reflect what you reported and when you reported it. They are a
            prompt for reflection — not a clinical measure of your well-being.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
st.markdown(
    '<div class="sentio-footer">Sentio · Progress is measured in small steps.</div>',
    unsafe_allow_html=True,
)