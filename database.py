"""Local SQLite storage. Nothing is saved unless the student opts in to tracking."""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_DB = Path("data") / "sentio.db"


def db_path() -> Path:
    return Path(os.environ.get("SENTIO_DB_PATH", str(DEFAULT_DB)))


@contextmanager
def connect(path: Optional[str | Path] = None):
    p = Path(path) if path else db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(path=None) -> None:
    with connect(path) as c:
        c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        c.execute("""CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            stress INTEGER NOT NULL CHECK (stress BETWEEN 1 AND 10),
            concern TEXT NOT NULL,
            workload TEXT NOT NULL,
            minutes_available INTEGER,
            energy TEXT,
            sleep TEXT,
            suggestion_id TEXT,
            helpful INTEGER CHECK (helpful IN (0, 1, 2)),
            note_text TEXT)""")


def tracking_enabled(path=None) -> bool:
    with connect(path) as c:
        row = c.execute("SELECT value FROM settings WHERE key='tracking_enabled'").fetchone()
    return bool(row and row["value"] == "1")


def set_tracking(enabled: bool, path=None) -> None:
    with connect(path) as c:
        c.execute("INSERT INTO settings(key, value) VALUES('tracking_enabled', ?) "
                  "ON CONFLICT(key) DO UPDATE SET value=excluded.value", ("1" if enabled else "0",))


def add_checkin(stress: int, concern: str, workload: str, minutes_available: Optional[int] = None,
                energy: Optional[str] = None, sleep: Optional[str] = None,
                note_text: Optional[str] = None, path=None) -> int:
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect(path) as c:
        cur = c.execute(
            "INSERT INTO checkins(created_at, stress, concern, workload, minutes_available, energy, sleep, note_text) "
            "VALUES(?,?,?,?,?,?,?,?)", (ts, stress, concern, workload, minutes_available, energy, sleep, note_text))
        return int(cur.lastrowid)


def set_suggestion(checkin_id: int, suggestion_id: str, path=None) -> None:
    with connect(path) as c:
        c.execute("UPDATE checkins SET suggestion_id=? WHERE id=?", (suggestion_id, checkin_id))


def set_helpful(checkin_id: int, helpful: int, path=None) -> None:
    with connect(path) as c:
        c.execute("UPDATE checkins SET helpful=? WHERE id=?", (helpful, checkin_id))


def list_checkins(path=None) -> list[dict]:
    with connect(path) as c:
        return [dict(r) for r in c.execute("SELECT * FROM checkins ORDER BY created_at ASC, id ASC")]


def delete_checkin(checkin_id: int, path=None) -> None:
    with connect(path) as c:
        c.execute("DELETE FROM checkins WHERE id=?", (checkin_id,))


def delete_all(path=None) -> None:
    with connect(path) as c:
        c.execute("DELETE FROM checkins")
