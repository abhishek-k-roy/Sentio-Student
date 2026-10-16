import streamlit as st

from sentio import emotion_model as em, privacy, ui

ui.setup("About and Privacy", "🔒")
st.title("About & Privacy")
st.write(privacy.DISCLAIMER)
st.markdown(privacy.TRACKING_EXPLANATION)

st.subheader("How it works")
st.markdown(
    "1. **Emotion analysis (AI):** a fine-tuned DistilBERT text classifier, if configured, gives an uncertain best guess about your words.\n"
    "2. **Reset plan (rules, not AI):** curated suggestions picked by simple rules from what *you* tell us. The emotion label isn't used.\n"
    "3. **Patterns (analytics, not AI):** averages and charts from your own saved check-ins.\n"
    "4. **Safety:** if your text suggests danger or self-harm, we skip the model and tips and point you to people who can help. "
    "This keyword screen is limited and can miss things."
)
classifier, reason = ui.get_classifier()
st.subheader("Model status")
st.write("✅ Emotion model loaded." if classifier else f"⚠️ Emotion analysis unavailable: {reason}")
st.caption(f"Set the {em.ENV_VAR} environment variable to the folder containing your saved model. No model accuracy is claimed here.")
