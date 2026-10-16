"""Safety screening for check-in text.

This is a deliberately conservative, keyword-based screen. It is NOT a clinical
risk assessment: it will miss indirect phrasing and can flag benign text. When it
triggers, the app skips the emotion model and ordinary tips and shows a calm
message pointing the student to a trusted person and local emergency/crisis support.
"""
import re

_PATTERNS = [
    r"\bkill (myself|my self)\b", r"\bsuicid(e|al)\b", r"\bend (my|it all|my own) life\b",
    r"\bwant(ed)? to die\b", r"\bdon'?t want to (live|be alive|be here)\b",
    r"\b(hurt|harm|cut|cutting) (myself|my self)\b", r"\bself[- ]?harm\b",
    r"\bbetter off dead\b", r"\bno reason to live\b", r"\btake my own life\b",
    r"\boverdose\b", r"\bnot worth living\b",
]
_RE = re.compile("|".join(_PATTERNS), re.IGNORECASE)

CRISIS_MESSAGE = (
    "It sounds like you may be going through something very hard, and your safety matters more "
    "than any study plan. Sentio Student isn't able to help in an emergency, and its suggestions "
    "aren't right for this moment.\n\n"
    "- If you might act on these thoughts or are in immediate danger, contact your local emergency "
    "number now.\n"
    "- Reach out to someone you trust right away: a friend, family member, hostel warden, or a "
    "college counsellor. You don't have to explain everything; \"I'm not okay and I need company\" is enough.\n"
    "- Contact a local crisis line or mental-health service in your area. (Sentio Student doesn't "
    "list numbers because they vary by country; your college or a local health service can give you a reliable one.)"
)


def normalize(text: str) -> str:
    return (text or "").replace("\u2019", "'").replace("\u2018", "'")


def is_crisis_text(text: str) -> bool:
    """True if the text contains phrases suggesting self-harm or immediate danger."""
    return bool(_RE.search(normalize(text)))
