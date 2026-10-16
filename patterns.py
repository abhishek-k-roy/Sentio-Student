"""Plain pandas analytics for the personal patterns page. This is analytics, not machine learning."""
from __future__ import annotations

import pandas as pd

MIN_CHECKINS = 5
MIN_GROUP = 2
MIN_DIFFERENCE = 1.0


def to_frame(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    return df


def cautious_insights(df: pd.DataFrame) -> list[str]:
    """Return reflection prompts only when there is enough data. Associations, never causes."""
    if df.empty or len(df) < MIN_CHECKINS:
        return []
    notes: list[str] = []
    heavy = df[df["workload"] == "Heavy"]["stress"]
    rest = df[df["workload"] != "Heavy"]["stress"]
    if len(heavy) >= MIN_GROUP and len(rest) >= MIN_GROUP and heavy.mean() - rest.mean() >= MIN_DIFFERENCE:
        notes.append(f"In your check-ins, stress was higher when your workload felt heavy (average {heavy.mean():.1f} vs {rest.mean():.1f}). "
                     "This is only an association in a small sample. Would planning your tasks ahead help?")
    by_concern = df.groupby("concern")["stress"].agg(["mean", "count"])
    by_concern = by_concern[by_concern["count"] >= MIN_GROUP]
    if not by_concern.empty and df["stress"].mean() + MIN_DIFFERENCE <= by_concern["mean"].max():
        top = by_concern["mean"].idxmax()
        notes.append(f"Check-ins about \"{top}\" had your highest average stress ({by_concern.loc[top, 'mean']:.1f}). "
                     "Is there a small step you could take on that before it builds up?")
    slept = df[df["sleep"].notna()]
    if len(slept) >= MIN_CHECKINS:
        low = slept[slept["sleep"] == "Under 6 hours"]["stress"]
        ok = slept[slept["sleep"] != "Under 6 hours"]["stress"]
        if len(low) >= MIN_GROUP and len(ok) >= MIN_GROUP and low.mean() - ok.mean() >= MIN_DIFFERENCE:
            notes.append("On days you reported under 6 hours of sleep, your stress ratings were higher. Worth noticing, though many things can be going on.")
    return notes
