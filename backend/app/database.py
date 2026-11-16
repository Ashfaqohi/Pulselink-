from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterator


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL DEFAULT 'development-only'
);
CREATE TABLE IF NOT EXISTS urls (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    original_url TEXT NOT NULL,
    short_code TEXT NOT NULL UNIQUE COLLATE NOCASE,
    created_at TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS click_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url_id TEXT NOT NULL REFERENCES urls(id),
    clicked_at TEXT NOT NULL,
    response_status INTEGER NOT NULL,
    response_time_ms INTEGER NOT NULL CHECK (response_time_ms >= 0)
);
CREATE INDEX IF NOT EXISTS idx_urls_user_created ON urls(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_clicks_url_created ON click_events(url_id, clicked_at DESC);
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(str(db_path), check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize(db_path: str | Path) -> None:
    if str(db_path) != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as connection:
        connection.executescript(SCHEMA)


def get_connection(db_path: str | Path) -> Iterator[sqlite3.Connection]:
    connection = connect(db_path)
    try:
        yield connection
    finally:
        connection.close()
