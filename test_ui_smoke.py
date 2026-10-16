"""Headless Streamlit smoke tests using streamlit.testing (no browser, no model)."""
import os, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import pytest
from streamlit.testing.v1 import AppTest
from sentio import database as db


@pytest.fixture(autouse=True)
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("SENTIO_DB_PATH", str(tmp_path / "ui.db"))
    monkeypatch.delenv("SENTIO_MODEL_DIR", raising=False)
    monkeypatch.chdir(ROOT)


def run(page):
    at = AppTest.from_file(str(ROOT / page), default_timeout=30).run()
    assert not at.exception, at.exception
    return at


def test_home_and_about_load():
    run("app.py")
    at = run("pages/3_About_and_Privacy.py")
    assert any("unavailable" in w.value for w in at.markdown)

def test_checkin_without_model_shows_unavailable_and_plan():
    at = run("pages/1_Student_Check_in.py")
    at.text_area[0].set_value("Two exams tomorrow and I cannot concentrate")
    at.button[0].click().run()
    assert not at.exception
    assert any("not shown" in i.value for i in at.info)
    assert at.button  # suggestion buttons rendered
    assert db.list_checkins() == []  # tracking off -> nothing stored

def test_crisis_path_skips_plan_and_storage():
    db.init_db(); db.set_tracking(True)
    at = run("pages/1_Student_Check_in.py")
    at.text_area[0].set_value("I want to die")
    at.button[0].click().run()
    assert at.warning and not at.info
    assert db.list_checkins() == []

def test_tracking_opt_in_saves_without_text_by_default():
    at = run("pages/2_My_Well_being_Patterns.py")
    next(b for b in at.button if "Turn tracking on" in b.label).click().run()
    assert db.tracking_enabled()
    at = run("pages/1_Student_Check_in.py")
    at.text_area[0].set_value("private words")
    at.button[0].click().run()
    rows = db.list_checkins()
    assert len(rows) == 1 and rows[0]["note_text"] is None
    run("pages/2_My_Well_being_Patterns.py")
