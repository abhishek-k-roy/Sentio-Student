"""Rule-based, curated Student Reset Plan.

Suggestions depend ONLY on what the student reported (concern, stress, time, workload).
The emotion model's label is deliberately NOT an input: it can't tell us what a student needs.
Edit LIBRARY to change content; edit select_suggestions() to change the rules.
"""
from __future__ import annotations

ANY = "any"
CONCERNS = ["Academic pressure", "Assignment overload", "Exam stress", "Poor sleep",
            "Trouble concentrating", "Feeling lonely or isolated", "Something else"]
WORKLOADS = ["Light", "Manageable", "Heavy"]
TIME_OPTIONS = [5, 15, 30, 60, 120]

# kind: calm | action | connect
LIBRARY = [
    {"id": "box_breath", "title": "A 2-minute breathing pause", "minutes": 5, "kind": "calm", "concerns": [ANY],
     "body": "Breathe in for 4 counts, hold for 4, out for 4, hold for 4. Repeat for about two minutes. Longer exhales help many people settle."},
    {"id": "senses_check", "title": "5-4-3-2-1 grounding", "minutes": 5, "kind": "calm",
     "concerns": ["Trouble concentrating", "Exam stress", "Academic pressure"],
     "body": "Name 5 things you see, 4 you can feel, 3 you hear, 2 you smell, 1 you taste. It's a way to bring attention back to the present."},
    {"id": "walk", "title": "A 10-minute walk, phone away", "minutes": 15, "kind": "calm",
     "concerns": ["Trouble concentrating", "Poor sleep", "Academic pressure", "Something else"],
     "body": "Step outside or walk a corridor. No goal, no podcast on study. Then return to your desk with one task in mind."},
    {"id": "brain_dump", "title": "Brain-dump, then pick one", "minutes": 15, "kind": "action",
     "concerns": ["Assignment overload", "Academic pressure", "Exam stress", "Trouble concentrating"],
     "body": "Write every pending task on paper for 5 minutes. Circle the single item with the nearest deadline. That's your only job for the next block."},
    {"id": "split_assignment", "title": "Split one assignment into 3 small steps", "minutes": 15, "kind": "action",
     "concerns": ["Assignment overload", "Academic pressure"],
     "body": "Pick one assignment. Write three steps that each take under 30 minutes (e.g. outline, first draft of one section, references). Do only step one."},
    {"id": "pomodoro", "title": "One 25-minute focus block", "minutes": 30, "kind": "action",
     "concerns": ["Exam stress", "Trouble concentrating", "Assignment overload", "Academic pressure"],
     "body": "Choose one topic or task. Silence notifications, work for 25 minutes, then take a 5-minute break. Decide afterwards whether to do another."},
    {"id": "exam_priority", "title": "Rank your exam topics by marks and weakness", "minutes": 30, "kind": "action",
     "concerns": ["Exam stress", "Academic pressure"],
     "body": "List topics for tomorrow. Mark each as high/low weight and strong/weak. Start with high-weight and weak; leave low-weight and strong for last."},
    {"id": "study_plan", "title": "Build a short study plan with breaks", "minutes": 120, "kind": "action",
     "concerns": ["Exam stress", "Assignment overload", "Academic pressure", "Trouble concentrating"],
     "body": "Split your time into 25-40 minute blocks, one topic each, with a 5-10 minute break between them. Leave the last 15 minutes as a buffer."},
    {"id": "wind_down", "title": "A 20-minute wind-down routine", "minutes": 30, "kind": "calm", "concerns": ["Poor sleep"],
     "body": "Dim lights, put the phone out of reach, and do something low-effort: stretching, a shower, or reading something non-academic."},
    {"id": "write_worry", "title": "Park tomorrow's worries on paper", "minutes": 15, "kind": "action", "concerns": ["Poor sleep", "Exam stress"],
     "body": "Write what's on your mind and one small next step for each item. Closing the notebook is a way of telling yourself it's handled for tonight."},
    {"id": "reach_out", "title": "Message or call someone you trust", "minutes": 15, "kind": "connect",
     "concerns": ["Feeling lonely or isolated", "Academic pressure", "Exam stress", "Something else"],
     "body": "A friend, family member, or classmate. You don't have to explain everything: \"Can we talk for ten minutes?\" is enough."},
    {"id": "campus_support", "title": "Consider your college counsellor or mentor", "minutes": 60, "kind": "connect", "concerns": [ANY],
     "body": "If this stress keeps coming back or feels hard to manage alone, a counsellor, mentor, or teacher you trust can help. Sentio Student can't replace them."},
    {"id": "journal", "title": "Three lines of journaling", "minutes": 5, "kind": "calm", "concerns": [ANY],
     "body": "Write: what I'm feeling, what's in my control today, one thing I'll do next. That's all."},
]


def select_suggestions(concern: str, stress: int, minutes: int, workload: str = "Manageable", limit: int = 3) -> list[dict]:
    """Return up to `limit` suggestions for the student's stated context."""
    fits = [s for s in LIBRARY if s["minutes"] <= minutes and (ANY in s["concerns"] or concern in s["concerns"])]
    # Specific matches before generic ones; keep library order within a tier.
    fits.sort(key=lambda s: ANY in s["concerns"])
    high_stress = stress >= 8
    heavy = workload == "Heavy"
    lonely = concern == "Feeling lonely or isolated"

    def first(kind):
        return next((s for s in fits if s["kind"] == kind and s not in chosen), None)

    chosen: list[dict] = []
    order = ["connect", "calm", "action"] if (high_stress or lonely) else (["action", "calm", "connect"] if heavy else ["calm", "action", "connect"])
    for kind in order:
        pick = first(kind)
        if pick:
            chosen.append(pick)
    for s in fits:  # fill any remaining slots
        if len(chosen) >= limit:
            break
        if s not in chosen:
            chosen.append(s)
    return chosen[:limit]
