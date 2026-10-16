import streamlit as st

from sentio import ui

ui.setup("Home")


# ============================================================
# HERO
# ============================================================
st.markdown(
    """
    <section class="sentio-hero">
        <span class="sentio-orb sentio-orb--a"></span>
        <span class="sentio-orb sentio-orb--b"></span>
        <span class="sentio-orb sentio-orb--c"></span>
        <div class="sentio-hero-inner">
            <div class="sentio-eyebrow">A little space for you</div>
            <h1>Understand your state.<br>Take one small step forward.</h1>
            <p class="sentio-hero-copy">
                College life can feel like a lot sometimes. Sentio gives you a calm
                place to check in, reflect on what is on your mind, and choose a
                manageable next step — at your own pace.
            </p>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.write("")
left, right = st.columns([1.45, 1], gap="large")

# ============================================================
# LEFT COLUMN — Choose your path
# ============================================================
with left:
    st.markdown(
        '<div class="sentio-section-label">Start where you are</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sentio-h2">What would help you right now?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sentio-lead">You don\'t need to have everything figured out. '
        'Choose the space that feels useful today.</p>',
        unsafe_allow_html=True,
    )
    st.write("")

    # --- Student check-in ---
    with st.container(border=True):
        st.markdown(
            """
            <div class="sentio-choice">
                <div class="sentio-icon">📝</div>
                <div>
                    <div class="sentio-choice-title">Student check-in</div>
                    <div class="sentio-choice-copy">Put your thoughts into words and explore possible study-related concerns.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "pages/1_Student_Check_in.py",
            label="Start a check-in →",
            use_container_width=True,
        )

    st.write("")

    # --- My well-being patterns ---
    with st.container(border=True):
        st.markdown(
            """
            <div class="sentio-choice">
                <div class="sentio-icon sentio-icon--teal">🌿</div>
                <div>
                    <div class="sentio-choice-title">My well-being patterns</div>
                    <div class="sentio-choice-copy">Review your own tracked patterns, when tracking is enabled.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "pages/2_My_Well_being_Patterns.py",
            label="View my patterns →",
            use_container_width=True,
        )

    st.write("")

    # --- About & privacy ---
    with st.container(border=True):
        st.markdown(
            """
            <div class="sentio-choice">
                <div class="sentio-icon sentio-icon--peach">🔒</div>
                <div>
                    <div class="sentio-choice-title">About &amp; privacy</div>
                    <div class="sentio-choice-copy">Understand how Sentio works and how your information is handled.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(
            "pages/3_About_and_Privacy.py",
            label="Explore privacy →",
            use_container_width=True,
        )

# ============================================================
# RIGHT COLUMN — Reminder + What Sentio can help with
# ============================================================
with right:
    st.markdown(
        '<div class="sentio-section-label">A gentle reminder</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="sentio-note">
            <div class="sentio-note-icon">☁️</div>
            <strong>You don't have to solve everything today.</strong>
            <p>Small steps count. Take a breath, name what is on your mind, and focus on one thing you can do next.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.markdown(
        '<div class="sentio-section-label">What Sentio can help with</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    st.markdown(
        """
        <div class="sentio-card">
            <div class="sentio-icon">🧭</div>
            <h3>Reflect without judgement</h3>
            <p>Use your own words to explore study pressure, deadlines, workload, and other concerns that may be affecting your day.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    st.markdown(
        """
        <div class="sentio-card">
            <div class="sentio-icon sentio-icon--teal">🌱</div>
            <h3>Choose one small next step</h3>
            <p>Explore curated reset suggestions. You stay in control of what feels right for you.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# BUILT FOR THOUGHTFUL CHECK-INS
# ============================================================
st.write("")
st.markdown(
    '<div class="sentio-section-label">Built for thoughtful check-ins</div>',
    unsafe_allow_html=True,
)
st.write("")

f1, f2, f3 = st.columns(3, gap="medium")
with f1:
    st.markdown(
        """
        <div class="sentio-card">
            <div class="sentio-icon">💬</div>
            <h3>Your words, your context</h3>
            <p>Share as much or as little as you feel comfortable sharing.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with f2:
    st.markdown(
        """
        <div class="sentio-card">
            <div class="sentio-icon sentio-icon--teal">✨</div>
            <h3>Support, not judgement</h3>
            <p>Text analysis highlights possible concern categories; it does not diagnose stress.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with f3:
    st.markdown(
        """
        <div class="sentio-card">
            <div class="sentio-icon sentio-icon--peach">🛡️</div>
            <h3>Privacy matters</h3>
            <p>Explore the privacy page to understand the app's current data practices.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# AVAILABLE IN THIS VERSION
# ============================================================
st.write("")
st.markdown(
    '<div class="sentio-section-label">Available in this version</div>',
    unsafe_allow_html=True,
)
st.write("")

m1, m2 = st.columns(2, gap="medium")
with m1:
    st.markdown(
        """
        <div class="sentio-card">
            <div class="sentio-icon">✅</div>
            <h3>What you can use today</h3>
            <p>• Check-ins with your own context, including concerns, stress, time, and workload.<br>
            • Curated, rule-based reset suggestions you can accept or ignore.<br>
            • Optional local tracking, charts, and deletion controls.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        """
        <div class="sentio-card">
            <div class="sentio-icon sentio-icon--peach">🗺️</div>
            <h3>Still on the roadmap</h3>
            <p>Audio emotion analysis, AI-written summaries, and Campus Pulse are planned ideas, not features available in this version.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# FOOTER
# ============================================================
st.write("")
st.markdown(
    '<div class="sentio-footer">Sentio · A small pause can be a meaningful step.</div>',
    unsafe_allow_html=True,
)