import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import pandas as pd
import pytest
from sentio import database as db, emotion_model as em, patterns, safety, suggestions as sg


@pytest.fixture
def dbp(tmp_path):
    p = tmp_path / "t.db"; db.init_db(p); return p


# --- database ---
def test_tracking_default_off_and_toggle(dbp):
    assert db.tracking_enabled(dbp) is False
    db.set_tracking(True, dbp); assert db.tracking_enabled(dbp)
    db.set_tracking(False, dbp); assert not db.tracking_enabled(dbp)

def test_add_update_delete(dbp):
    i = db.add_checkin(7, "Exam stress", "Heavy", 30, path=dbp)
    db.set_suggestion(i, "pomodoro", dbp); db.set_helpful(i, 2, dbp)
    row = db.list_checkins(dbp)[0]
    assert row["suggestion_id"] == "pomodoro" and row["helpful"] == 2 and row["note_text"] is None
    db.delete_checkin(i, dbp); assert db.list_checkins(dbp) == []

def test_delete_all_and_constraints(dbp):
    for _ in range(3): db.add_checkin(5, "x", "Light", path=dbp)
    db.delete_all(dbp); assert db.list_checkins(dbp) == []
    with pytest.raises(Exception): db.add_checkin(11, "x", "Light", path=dbp)

def test_sql_injection_text_is_stored_literally(dbp):
    db.add_checkin(3, "x'); DROP TABLE checkins;--", "Light", path=dbp)
    assert len(db.list_checkins(dbp)) == 1


# --- suggestions ---
def test_respects_time_and_limit():
    out = sg.select_suggestions("Exam stress", 5, 5)
    assert 0 < len(out) <= 3 and all(s["minutes"] <= 5 for s in out)

def test_deterministic():
    a = sg.select_suggestions("Assignment overload", 6, 60, "Heavy")
    assert a == sg.select_suggestions("Assignment overload", 6, 60, "Heavy")

def test_high_stress_includes_human_support():
    out = sg.select_suggestions("Academic pressure", 9, 60)
    assert any(s["kind"] == "connect" for s in out)

def test_concern_relevance():
    out = sg.select_suggestions("Poor sleep", 5, 30)
    assert any("Poor sleep" in s["concerns"] for s in out)

def test_library_ids_unique():
    ids = [s["id"] for s in sg.LIBRARY]; assert len(ids) == len(set(ids))


# --- emotion model adapter ---
def test_missing_model_not_configured(monkeypatch):
    monkeypatch.delenv(em.ENV_VAR, raising=False)
    with pytest.raises(em.ModelUnavailable): em.load_classifier()

def test_missing_dir_and_missing_config(tmp_path):
    with pytest.raises(em.ModelUnavailable): em.load_classifier(str(tmp_path / "nope"))
    with pytest.raises(em.ModelUnavailable): em.load_classifier(str(tmp_path))  # no config.json

def test_unavailable_result_is_labeled():
    r = em.analyze("I am tired", None, "no model"); assert r.status == "unavailable" and r.label is None

def test_no_text():
    assert em.analyze("   ", lambda t: []).status == "no_text"

def test_ok_unclear_error():
    ok = lambda t: [[{"label": "sadness", "score": 0.8}, {"label": "joy", "score": 0.2}]]
    r = em.analyze("x", ok); assert (r.status, r.label) == ("ok", "sadness")
    low = lambda t: [[{"label": "fear", "score": 0.3}, {"label": "joy", "score": 0.3}]]
    assert em.analyze("x", low).status == "unclear"
    def boom(t): raise RuntimeError("bad")
    assert em.analyze("x", boom).status == "error"


# --- safety ---
@pytest.mark.parametrize("t", ["I want to die", "i don\u2019t want to live anymore", "thinking of suicide", "I might hurt myself"])
def test_crisis_detected(t): assert safety.is_crisis_text(t)

@pytest.mark.parametrize("t", ["I have two exams tomorrow and cannot concentrate", "this exam is killing me", ""])
def test_benign_not_flagged(t): assert not safety.is_crisis_text(t)


# --- patterns ---
def _df(rows): return patterns.to_frame([{"created_at": f"2026-10-0{i+1}T10:00:00+00:00", "sleep": None, **r} for i, r in enumerate(rows)])

def test_no_insight_with_little_data():
    assert patterns.cautious_insights(_df([{"stress": 8, "concern": "a", "workload": "Heavy"}])) == []

def test_workload_insight_is_associative():
    rows = [{"stress": 9, "concern": "a", "workload": "Heavy"}] * 3 + [{"stress": 3, "concern": "b", "workload": "Light"}] * 3
    notes = patterns.cautious_insights(_df(rows))
    assert any("workload felt heavy" in n for n in notes) and not any("because" in n.lower() or "cause" in n.lower().replace("not causes", "") for n in notes)
