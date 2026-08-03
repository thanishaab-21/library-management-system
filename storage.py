"""
storage.py
-----------
Handles all persistence for the Library Management System using plain JSON
files. This keeps the project dependency-free (no external database needed)
while still giving the app real, durable storage between runs.

All file I/O is wrapped in try/except so a missing file, corrupted JSON, or
permissions problem never crashes the whole application -- it raises a
StorageError instead, which main.py can catch and report cleanly.
"""

import json
import os

from exceptions import StorageError

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

BOOKS_FILE = os.path.join(DATA_DIR, "books.json")
MEMBERS_FILE = os.path.join(DATA_DIR, "members.json")
ISSUES_FILE = os.path.join(DATA_DIR, "issues.json")
COUNTERS_FILE = os.path.join(DATA_DIR, "counters.json")


def _ensure_data_dir():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except OSError as exc:
        raise StorageError(f"Could not create data directory: {exc}")


def load_json(filepath, default):
    """Load JSON data from a file, returning `default` if the file is
    missing. Raises StorageError if the file exists but is corrupted or
    unreadable."""
    _ensure_data_dir()
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return default
            return json.loads(content)
    except json.JSONDecodeError as exc:
        raise StorageError(
            f"Data file '{os.path.basename(filepath)}' is corrupted: {exc}"
        )
    except OSError as exc:
        raise StorageError(
            f"Could not read data file '{os.path.basename(filepath)}': {exc}"
        )


def save_json(filepath, data):
    """Atomically save `data` as JSON to `filepath`.

    Writes to a temporary file first and then renames it, so that a crash
    or power loss mid-write never leaves a half-written / corrupted data
    file behind.
    """
    _ensure_data_dir()
    tmp_path = filepath + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, filepath)
    except OSError as exc:
        raise StorageError(
            f"Could not write data file '{os.path.basename(filepath)}': {exc}"
        )


def load_counters():
    return load_json(COUNTERS_FILE, {"book_id": 0, "member_id": 0, "record_id": 0})


def save_counters(counters):
    save_json(COUNTERS_FILE, counters)


def next_id(counter_key):
    """Return the next auto-increment integer ID for the given entity type
    ('book_id', 'member_id', or 'record_id'), persisting the updated
    counter immediately so IDs are never reused across runs."""
    counters = load_counters()
    counters[counter_key] = counters.get(counter_key, 0) + 1
    save_counters(counters)
    return counters[counter_key]
