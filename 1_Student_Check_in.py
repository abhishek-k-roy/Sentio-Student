import streamlit as st

from sentio import database as db, emotion_model as em, privacy, safety, suggestions as sg, ui

ui.setup("Student Check-in", "📝")
S = st.session_state
tracking = db.tracking_enabled()

st.title("Student Check-in")
st.caption(("Tracking is ON: this check-in will be saved locally. " if tracking else
            "Tracking is OFF: nothing from this check-in is saved. ") + "You can change this on the Patterns page.")

with st.form("checkin"):
    text = st.text_area("How are you feeling, and what's going on? (optional)", height=120,
                        placeholder="Write as much or as little as you like.")
    concern = st.selectbox("What's the main thing weighing on you?", sg.CONCERNS)
    stress = st.slider("How stressed do you feel right now? (1 = calm, 10 = very stressed)", 1, 10, 5)
    minutes = st.select_slider("How much time do you have?", options=sg.TIME_OPTIONS, value=30,
                               format_func=lambda m: f"{m} min" if m < 60 else f"{m // 60} h")
    workload = st.radio("How does your workload feel?", sg.WORKLOADS, index=1, horizontal=True)
    with st.expander("Optional questions (skip freely)"):
        energy = st.selectbox("Energy today", ["Skip", "Low", "Medium", "High"])
        sleep = st.selectbox("Sleep last night", ["Skip", "Under 6 hours", "6 hours or more"])
    save_text = st.checkbox("Also save the text I wrote (otherwise only the numbers/choices are saved)",
                            disabled=not tracking)
    go = st.form_submit_button("Get my reset plan", type="primary")

if go:
    S.pop("chosen", None); S.pop("feedback", None); S.pop("checkin_id", None)
    if safety.is_crisis_text(text):
        S.result = {"crisis": True}  # nothing is analysed or saved
    else:
        classifier, reason = ui.get_classifier()
        emotion = em.analyze(text, classifier, reason)
        plan = sg.select_suggestions(concern, stress, minutes, workload)
        if tracking:
            S.checkin_id = db.add_checkin(
                stress, concern, workload, minutes,
                None if energy == "Skip" else energy, None if sleep == "Skip" else sleep,
                text.strip() if (save_text and text.strip()) else None)
        S.result = {"crisis": False, "emotion": emotion, "plan": plan}

R = S.get("result")
if R and R["crisis"]:
    st.warning(safety.CRISIS_MESSAGE)
elif R:
    e = R["emotion"]
    st.subheader("1 · What the text analysis picked up")
    if e.status == "ok":
        st.info(f"The model's best guess for your words is **{e.label}** (model score {e.confidence:.0%}). "
                "That's an uncertain signal from a statistical model, not a fact about you. You know how you feel better than it does.")
    elif e.status == "unclear":
        st.info(f"The model wasn't confident (best guess: {e.label}, score {e.confidence:.0%}). Treat this as unclear.")
    else:
        st.info(f"Emotion analysis not shown: {e.message}")

    st.subheader("2 · Your reset plan")
    st.caption("Chosen from what you told us (concern, stress, time, workload), not from the emotion label. Pick any, or none.")
    for s in R["plan"]:
        with st.container(border=True):
            st.markdown(f"**{s['title']}** · ~{s['minutes']} min")
            st.write(s["body"])
            if st.button("I'll try this", key=f"try_{s['id']}"):
                S.chosen = s["id"]
                if S.get("checkin_id"):
                    db.set_suggestion(S.checkin_id, s["id"])
    if S.get("chosen"):
        st.subheader("3 · Was that helpful?")
        choice = st.radio("Tell us after you've tried it", ["Yes", "Somewhat", "Not really"], index=None, horizontal=True)
        if choice:
            S.feedback = {"Yes": 2, "Somewhat": 1, "Not really": 0}[choice]
            if S.get("checkin_id"):
                db.set_helpful(S.checkin_id, S.feedback)
            st.success("Thanks. " + ("Saved locally." if S.get("checkin_id") else "Not saved, since tracking is off."))
    st.caption("If things feel heavy or keep building up, talking to a counsellor or someone you trust is a good next step.")
