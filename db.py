"""
db.py – SQLite helpers for TrashLock.

Schemas:
  1. users:
     (id INTEGER PK, name TEXT, pin_hash TEXT, pin_salt TEXT, embedding TEXT)
     - Embeddings are stored as JSON strings (512-d list of floats).
     - PINs are stored as SHA-256(salt + pin) hex digests.
     - No photos are ever written to disk.

  2. test_logs:
     (id INTEGER PK, test_case TEXT, expected TEXT, actual TEXT, status TEXT, created_at TEXT)
     - Tracks experimental verification scenarios (Pass/Fail).
"""

import sqlite3
import hashlib
import json
import os
import secrets
from datetime import datetime

# ---------------------------------------------------------------------------
# Database path – lives next to app.py so it's easy to find / inspect / reset.
# ---------------------------------------------------------------------------
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")


def _connect():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


# ---------------------------------------------------------------------------
# Initialise
# ---------------------------------------------------------------------------
def init_db():
    """Create the users and test_logs tables if they don't exist yet."""
    try:
        con = _connect()
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT    NOT NULL,
                pin_hash  TEXT    NOT NULL,
                pin_salt  TEXT    NOT NULL,
                embedding TEXT    NOT NULL
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS test_logs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                test_case  TEXT    NOT NULL,
                expected   TEXT    NOT NULL,
                actual     TEXT    NOT NULL,
                status     TEXT    NOT NULL,
                created_at TEXT    NOT NULL
            )
            """
        )
        con.commit()
        con.close()
    except sqlite3.Error as err:
        raise RuntimeError(f"Database initialization error: {err}")


# ---------------------------------------------------------------------------
# PIN hashing helpers
# ---------------------------------------------------------------------------
def _hash_pin(pin: str, salt: str) -> str:
    """Hash a PIN with the given salt using SHA-256."""
    return hashlib.sha256((salt + pin).encode()).hexdigest()


def verify_pin(pin: str, stored_hash: str, stored_salt: str) -> bool:
    """Return True if the PIN matches the stored hash."""
    return _hash_pin(pin, stored_salt) == stored_hash


# ---------------------------------------------------------------------------
# User CRUD operations
# ---------------------------------------------------------------------------
def user_exists(name: str) -> bool:
    """Check if a user with the given name (case-insensitive) already exists."""
    con = _connect()
    row = con.execute(
        "SELECT 1 FROM users WHERE LOWER(TRIM(name)) = LOWER(TRIM(?)) LIMIT 1",
        (name,)
    ).fetchone()
    con.close()
    return row is not None


def save_user(name: str, pin: str, embedding):
    """
    Insert a new user.
    - `name`: display name
    - `pin`: raw PIN string (will be salted + hashed before storage)
    - `embedding`: 512-d vector or list of floats (the averaged face template)
    """
    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()

    salt = secrets.token_hex(16)  # 32-char random salt
    pin_hash = _hash_pin(pin, salt)
    emb_json = json.dumps(embedding)

    con = _connect()
    try:
        con.execute(
            "INSERT INTO users (name, pin_hash, pin_salt, embedding) VALUES (?, ?, ?, ?)",
            (name.strip(), pin_hash, salt, emb_json),
        )
        con.commit()
    finally:
        con.close()


def load_users() -> list[dict]:
    """
    Return every user as a dict with keys:
        id, name, pin_hash, pin_salt, embedding (list[float])
    """
    con = _connect()
    try:
        rows = con.execute(
            "SELECT id, name, pin_hash, pin_salt, embedding FROM users ORDER BY id ASC"
        ).fetchall()
    finally:
        con.close()

    users = []
    for row in rows:
        users.append(
            {
                "id": row[0],
                "name": row[1],
                "pin_hash": row[2],
                "pin_salt": row[3],
                "embedding": json.loads(row[4]),
            }
        )
    return users


def delete_user(user_id: int):
    """Delete a single user by their primary-key id."""
    con = _connect()
    try:
        con.execute("DELETE FROM users WHERE id = ?", (user_id,))
        con.commit()
    finally:
        con.close()


def delete_all_users():
    """Wipe every row from the users table (handy for demo resets)."""
    con = _connect()
    try:
        con.execute("DELETE FROM users")
        con.commit()
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Test Log CRUD operations
# ---------------------------------------------------------------------------
def save_test_log(test_case: str, expected: str, actual: str, status: str):
    """
    Insert a new verification test result into the test_logs table.
    - `test_case`: scenario description (e.g., 'Enrolled user, front desk lighting')
    - `expected`: expected outcome ('Access granted' or 'Access denied')
    - `actual`: actual outcome (e.g., 'Access granted (0.214)')
    - `status`: 'Pass' or 'Fail'
    """
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    con = _connect()
    try:
        con.execute(
            "INSERT INTO test_logs (test_case, expected, actual, status, created_at) VALUES (?, ?, ?, ?, ?)",
            (test_case.strip(), expected.strip(), actual.strip(), status.strip(), created_at),
        )
        con.commit()
    finally:
        con.close()


def load_test_logs() -> list[dict]:
    """Return all test log rows ordered by id ascending."""
    con = _connect()
    try:
        rows = con.execute(
            "SELECT id, test_case, expected, actual, status, created_at FROM test_logs ORDER BY id ASC"
        ).fetchall()
    finally:
        con.close()

    logs = []
    for row in rows:
        logs.append(
            {
                "id": row[0],
                "test_case": row[1],
                "expected": row[2],
                "actual": row[3],
                "status": row[4],
                "created_at": row[5],
            }
        )
    return logs


def delete_test_log(log_id: int):
    """Delete a single test log row by id."""
    con = _connect()
    try:
        con.execute("DELETE FROM test_logs WHERE id = ?", (log_id,))
        con.commit()
    finally:
        con.close()


def clear_test_logs():
    """Clear all test log entries."""
    con = _connect()
    try:
        con.execute("DELETE FROM test_logs")
        con.commit()
    finally:
        con.close()
