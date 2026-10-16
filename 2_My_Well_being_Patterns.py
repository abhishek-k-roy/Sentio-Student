import plotly.express as px
import streamlit as st

from sentio import database as db, patterns, privacy, ui

ui.setup("My Well-being Patterns", "📈")
st.title("My Well-being Patterns")

if not db.tracking_enabled():
    st.markdown(privacy.TRACKING_EXPLANATION)
    if st.button("I understand. Turn tracking on", type="primary"):
        db.set_tracking(True)
        st.rerun()
    st.stop()

st.success("Tracking is on. " + privacy.STORED_NOTE)
rows = db.list_checkins()
df = patterns.to_frame(rows)

if df.empty:
    st.info("No saved check-ins yet. Complete a check-in and it will show up here.")
else:
    fig = px.line(df, x="created_at", y="stress", markers=True, range_y=[0, 10],
                  labels={"created_at": "Check-in", "stress": "Self-reported stress (1-10)"})
    st.plotly_chart(fig, use_container_width=True)
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.bar(df.groupby("concern")["stress"].mean().reset_index(), x="concern", y="stress",
                           title="Average stress by concern", range_y=[0, 10]), use_container_width=True)
    c2.plotly_chart(px.bar(df.groupby("workload")["stress"].mean().reset_index(), x="workload", y="stress",
                           title="Average stress by workload", range_y=[0, 10]), use_container_width=True)

    st.subheader("Things you might reflect on")
    notes = patterns.cautious_insights(df)
    if notes:
        for n in notes:
            st.write("• " + n)
    else:
        st.caption(f"Not enough data yet. Reflection prompts appear after at least {patterns.MIN_CHECKINS} check-ins "
                   "and only when there's a visible difference. These are patterns in your own entries, not causes or diagnoses.")

    st.subheader("Your saved entries")
    show = df.drop(columns=["id"]).rename(columns={"created_at": "when"})
    st.dataframe(show, use_container_width=True)
    pick = st.selectbox("Delete one entry", [None] + [r["id"] for r in rows],
                        format_func=lambda i: "Choose..." if i is None else next(f"#{r['id']} · {r['created_at']}" for r in rows if r["id"] == i))
    if pick is not None and st.button("Delete this entry"):
        db.delete_checkin(pick)
        st.rerun()

st.divider()
col_a, col_b = st.columns(2)
if col_a.button("Delete all my saved entries"):
    db.delete_all()
    st.rerun()
if col_b.button("Turn tracking off"):
    db.set_tracking(False)
    st.rerun()
st.caption("Turning tracking off stops new saving; use 'Delete all' to remove existing entries.")
