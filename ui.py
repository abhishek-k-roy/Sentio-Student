"""Shared Streamlit UI helpers for Sentio Student."""
import streamlit as st

from sentio import database, emotion_model, privacy


@st.cache_resource(show_spinner="Loading emotion model...")
def get_classifier():
    """Load the classifier once per server process.

    Returns (classifier_or_None, reason_if_unavailable).
    """
    try:
        return emotion_model.load_classifier(), ""
    except emotion_model.ModelUnavailable as exc:
        return None, str(exc)


def _apply_theme():
    """Apply Sentio's shared calming design system."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Instrument+Serif:ital@0;1&display=swap');

        :root {
            --s-ink: #1E2A47;
            --s-ink-soft: #3D4C6B;
            --s-muted: #6C7A96;
            --s-indigo: #4C5FD5;
            --s-indigo-deep: #3B4AB8;
            --s-indigo-tint: #E8EAFB;
            --s-teal: #2E9E8F;
            --s-teal-tint: #DFF3EE;
            --s-peach: #E8945A;
            --s-peach-tint: #FCEDE1;
            --s-line: #E4E3F1;
            --s-surface: #FFFFFF;
        }

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', ui-sans-serif, system-ui, -apple-system,
                         BlinkMacSystemFont, "Segoe UI", sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        .stApp {
            background:
                radial-gradient(1100px 640px at 6% -10%, rgba(150,166,255,.30), transparent 62%),
                radial-gradient(980px 580px at 100% 2%, rgba(122,214,196,.26), transparent 60%),
                radial-gradient(900px 700px at 52% 112%, rgba(255,196,150,.22), transparent 62%),
                linear-gradient(168deg, #F7F5FC 0%, #F2F4FC 46%, #F0F7F5 100%);
            background-attachment: fixed;
            color: var(--s-ink);
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1180px;
            padding-top: 1.4rem;
            padding-bottom: 3rem;
        }

        /* -------- Typography -------- */
        h1, h2, h3, h4 {
            color: var(--s-ink) !important;
            letter-spacing: -0.02em;
        }
        h1 {
            font-family: 'Instrument Serif', Georgia, 'Times New Roman', serif !important;
            font-weight: 400 !important;
            line-height: 1.1 !important;
        }
        h2, h3, h4 {
            font-weight: 700 !important;
        }

        p, li, label, [data-testid="stCaptionContainer"] {
            color: var(--s-ink-soft);
        }

        [data-testid="stCaptionContainer"] {
            font-size: .78rem !important;
            color: var(--s-muted) !important;
        }

        /* -------- Sidebar -------- */
        [data-testid="stSidebar"] {
            background: rgba(255,255,255,.72);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-right: 1px solid var(--s-line);
        }
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.2rem;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: var(--s-muted);
        }
        [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
            border-radius: 12px;
            margin: .18rem 0;
            transition: background 160ms ease, color 160ms ease;
        }
        [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
            background: var(--s-indigo-tint);
            color: var(--s-indigo-deep);
        }

        /* -------- Buttons -------- */
        div.stButton > button {
            border-radius: 13px;
            font-weight: 650;
            transition: transform 170ms ease, box-shadow 170ms ease,
                        background 170ms ease, border-color 170ms ease;
        }
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--s-indigo) 0%, var(--s-indigo-deep) 100%);
            border: 1px solid var(--s-indigo-deep);
            color: #FFFFFF;
        }
        div.stButton > button[kind="primary"]:hover {
            box-shadow: 0 12px 24px -14px rgba(76,95,213,.9);
            transform: translateY(-1px);
        }
        div.stButton > button[kind="secondary"] {
            background: #FFFFFF;
            border: 1px solid var(--s-line);
            color: var(--s-ink);
        }
        div.stButton > button[kind="secondary"]:hover {
            border-color: #C9D0EE;
            background: #F8F9FE;
        }

        /* -------- Page links (main area) -------- */
        [data-testid="stPageLink"] a {
            background: linear-gradient(135deg, #F1F3FE 0%, #EEF5FD 100%);
            border: 1px solid #DEE4F8;
            color: var(--s-indigo-deep) !important;
            padding: .58rem .95rem;
            border-radius: 13px;
            font-weight: 650;
            display: flex !important;
            justify-content: center;
            align-items: center;
            gap: .4rem;
            text-decoration: none;
            transition: transform 170ms ease, box-shadow 170ms ease,
                        background 170ms ease, border-color 170ms ease;
        }
        [data-testid="stPageLink"] a:hover {
            background: linear-gradient(135deg, #E7EAFB 0%, #E4F0FB 100%);
            border-color: #C5CEF2;
            transform: translateY(-1px);
            box-shadow: 0 10px 20px -16px rgba(76,95,213,.9);
            color: var(--s-indigo-deep) !important;
        }
        [data-testid="stPageLink"] a p,
        [data-testid="stPageLink"] a span {
            color: inherit !important;
            font-weight: inherit !important;
        }

        /* -------- Inputs -------- */
        [data-testid="stTextArea"] textarea,
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            border-radius: 12px;
            border-color: var(--s-line);
            background: #FFFFFF;
        }
        [data-testid="stTextArea"] textarea:focus,
        [data-testid="stTextInput"] input:focus {
            border-color: var(--s-indigo);
            box-shadow: 0 0 0 3px rgba(76,95,213,.12);
        }

        /* -------- Metrics -------- */
        [data-testid="stMetric"] {
            background: linear-gradient(180deg, #FFFFFF 0%, #FCFCFF 100%);
            border: 1px solid var(--s-line);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 1px 2px rgba(30,42,71,.04),
                        0 12px 26px -22px rgba(30,42,71,.4);
        }

        /* -------- Alerts -------- */
        [data-testid="stAlert"] {
            border-radius: 14px;
        }

        hr {
            border-color: var(--s-line);
        }

        /* -------- Bordered container = card -------- */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(180deg, #FFFFFF 0%, #FCFCFF 100%) !important;
            border: 1px solid var(--s-line) !important;
            border-radius: 22px !important;
            padding: 1.2rem 1.3rem !important;
            box-shadow: 0 1px 2px rgba(30,42,71,.04),
                        0 14px 30px -24px rgba(30,42,71,.4) !important;
            transition: transform 200ms ease, box-shadow 200ms ease, border-color 200ms ease;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-2px);
            border-color: #CFD5F1 !important;
            box-shadow: 0 2px 6px rgba(30,42,71,.05),
                        0 26px 46px -28px rgba(30,42,71,.45) !important;
        }

        /* ============================================================
           HERO
           ============================================================ */
        .sentio-eyebrow {
            display: inline-block;
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .16em;
            text-transform: uppercase;
            color: #2E7D6B;
            background: rgba(255,255,255,.72);
            border: 1px solid rgba(46,158,143,.24);
            border-radius: 999px;
            padding: .34rem .8rem;
            margin-bottom: 1.1rem;
            backdrop-filter: blur(6px);
        }

        .sentio-hero {
            position: relative;
            overflow: hidden;
            border-radius: 28px;
            padding: clamp(1.8rem, 4.2vw, 3.2rem);
            background: linear-gradient(125deg, #E9E9FC 0%, #E4EFFB 38%, #E1F4EF 68%, #FAEFE4 100%);
            border: 1px solid rgba(255,255,255,.85);
            box-shadow: 0 30px 70px -45px rgba(30,42,71,.85),
                        inset 0 1px 0 rgba(255,255,255,.9);
            min-height: 300px;
            display: flex;
            align-items: center;
        }

        .sentio-orb {
            position: absolute;
            border-radius: 50%;
            filter: blur(46px);
            opacity: .55;
            pointer-events: none;
        }
        .sentio-orb--a { width: 260px; height: 260px; background: #B9C6FF; top: -90px; right: -40px; }
        .sentio-orb--b { width: 220px; height: 220px; background: #A8E6D6; bottom: -100px; left: 38%; }
        .sentio-orb--c { width: 180px; height: 180px; background: #F8D3AF; bottom: -60px; right: 12%; opacity: .45; }

        .sentio-hero-inner {
            position: relative;
            z-index: 1;
            max-width: 680px;
        }

        .sentio-hero h1 {
            font-family: 'Instrument Serif', Georgia, 'Times New Roman', serif !important;
            font-weight: 400 !important;
            font-size: clamp(2.2rem, 4.4vw, 3.6rem) !important;
            line-height: 1.08 !important;
            letter-spacing: -0.02em !important;
            color: #1B2743 !important;
            margin: 0 0 1rem 0 !important;
        }

        .sentio-hero-copy {
            color: #4A5D7A;
            font-size: 1.05rem;
            line-height: 1.75;
            max-width: 600px;
            margin: 0;
        }

        /* ============================================================
           SECTION LABEL + HEADINGS
           ============================================================ */
        .sentio-section-label {
            font-size: .73rem;
            font-weight: 700;
            letter-spacing: .14em;
            text-transform: uppercase;
            color: #7A88A6;
            margin-bottom: .5rem;
        }

        .sentio-h2 {
            font-size: 1.4rem;
            font-weight: 700;
            letter-spacing: -.02em;
            color: var(--s-ink);
            margin: .4rem 0 .6rem 0;
            line-height: 1.25;
        }

        .sentio-lead {
            color: var(--s-ink-soft);
            font-size: .94rem;
            line-height: 1.65;
            margin: 0;
        }

        /* ============================================================
           CHOICE CARD (icon + title + copy + page_link)
           ============================================================ */
        .sentio-icon {
            width: 44px;
            height: 44px;
            border-radius: 14px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            line-height: 1;
            background: linear-gradient(145deg, #EEF0FE, #E2E7FB);
            box-shadow: inset 0 0 0 1px rgba(255,255,255,.85),
                        0 6px 14px -10px rgba(76,95,213,.75);
            flex-shrink: 0;
        }
        .sentio-icon--teal {
            background: linear-gradient(145deg, #E7F6F1, #D6EEE7);
            box-shadow: inset 0 0 0 1px rgba(255,255,255,.85),
                        0 6px 14px -10px rgba(46,158,143,.75);
        }
        .sentio-icon--peach {
            background: linear-gradient(145deg, #FDF0E5, #FAE3D0);
            box-shadow: inset 0 0 0 1px rgba(255,255,255,.85),
                        0 6px 14px -10px rgba(232,148,90,.75);
        }

        .sentio-choice {
            display: flex;
            gap: .95rem;
            align-items: center;
            margin-bottom: 1rem;
        }
        .sentio-choice-title {
            font-weight: 700;
            color: var(--s-ink);
            font-size: 1rem;
            letter-spacing: -.015em;
            margin-bottom: .15rem;
        }
        .sentio-choice-copy {
            color: var(--s-muted);
            font-size: .86rem;
            line-height: 1.5;
            margin: 0;
        }

        /* ============================================================
           PLAIN CARD (icon + h3 + p, used on right column & feature grids)
           ============================================================ */
        .sentio-card {
            background: linear-gradient(180deg, #FFFFFF 0%, #FCFCFF 100%);
            border: 1px solid var(--s-line);
            border-radius: 20px;
            padding: 1.3rem 1.35rem 1.4rem;
            box-shadow: 0 1px 2px rgba(30,42,71,.04),
                        0 14px 30px -24px rgba(30,42,71,.4);
            transition: transform 200ms ease, box-shadow 200ms ease, border-color 200ms ease;
            height: 100%;
        }
        .sentio-card:hover {
            transform: translateY(-2px);
            border-color: #CFD5F1;
            box-shadow: 0 2px 6px rgba(30,42,71,.05),
                        0 26px 46px -28px rgba(30,42,71,.45);
        }
        .sentio-card h3 {
            font-size: 1.02rem;
            font-weight: 700;
            margin: .9rem 0 .45rem 0;
            color: var(--s-ink);
            letter-spacing: -.015em;
        }
        .sentio-card p {
            color: var(--s-muted);
            font-size: .9rem;
            line-height: 1.65;
            margin: 0;
        }

        /* ============================================================
           GENTLE REMINDER NOTE
           ============================================================ */
        .sentio-note {
            border-radius: 20px;
            padding: 1.4rem 1.5rem;
            background: linear-gradient(135deg, #E4F5EF 0%, #E9F6F2 55%, #F1F8F5 100%);
            border: 1px solid #CFEAE1;
            box-shadow: 0 14px 34px -26px rgba(46,158,143,.9);
            color: #1F4B41;
        }
        .sentio-note-icon {
            font-size: 1.45rem;
            margin-bottom: .7rem;
        }
        .sentio-note strong {
            display: block;
            color: #1A4038;
            font-size: .98rem;
            letter-spacing: -.01em;
            margin-bottom: .4rem;
        }
        .sentio-note p {
            color: #3A6357;
            font-size: .9rem;
            line-height: 1.65;
            margin: 0;
        }

        /* ============================================================
           FOOTER
           ============================================================ */
        .sentio-footer {
            color: var(--s-muted);
            text-align: center;
            font-size: .83rem;
            padding-top: 2.5rem;
            letter-spacing: -.01em;
        }

        /* ============================================================
           RESPONSIVE
           ============================================================ */
        @media (max-width: 760px) {
            [data-testid="stMainBlockContainer"] {
                padding-top: 1rem;
            }
            .sentio-hero {
                border-radius: 20px;
                padding: 1.4rem;
                min-height: auto;
            }
            .sentio-h2 {
                font-size: 1.25rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def setup(title: str, icon: str = "🌱"):
    """Set page defaults, initialize storage, and apply shared styling."""
    st.set_page_config(
        page_title=f"{title} · Sentio Student",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _apply_theme()
    database.init_db()
    st.caption(privacy.DISCLAIMER)