import sqlite3

import aceest_db


def test_init_db_creates_tables_and_admin(tmp_path, monkeypatch):
    db_file = tmp_path / "aceest_fitness.db"
    monkeypatch.setattr(aceest_db, "DB_NAME", str(db_file))

    aceest_db.init_db()

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    assert {"users", "clients", "progress", "workouts", "exercises", "metrics"} <= tables

    cur.execute("SELECT username, role FROM users WHERE username='admin'")
    assert cur.fetchone() == ("admin", "Admin")
    conn.close()


def test_init_db_does_not_duplicate_admin(tmp_path, monkeypatch):
    monkeypatch.setattr(aceest_db, "DB_NAME", str(tmp_path / "aceest_fitness.db"))
    aceest_db.init_db()
    aceest_db.init_db()

    conn = sqlite3.connect(aceest_db.DB_NAME)
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    assert count == 1

