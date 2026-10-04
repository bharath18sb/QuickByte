"""
Quickbyte - Database layer
SQLite connection management + schema initialisation.
All queries elsewhere use parameterised statements (SQL-injection safe).
"""
import sqlite3
import os
from flask import g, current_app

# database.db lives next to this file (project root).
# Override with QUICKBYTE_DB (used by the smoke test to isolate its data).
DB_PATH = os.environ.get("QUICKBYTE_DB") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "database.db"
)


def get_db():
    """Return a per-request SQLite connection (stored on flask.g)."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row          # rows behave like dicts
        g.db.execute("PRAGMA foreign_keys = ON") # enforce FK constraints
    return g.db


def close_db(exception=None):
    """Close the connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ---------------------------------------------------------------------------
# Small query helpers -> keep route code short and always parameterised
# ---------------------------------------------------------------------------
def query(sql, args=(), one=False):
    cur = get_db().execute(sql, args)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute(sql, args=()):
    """Run INSERT/UPDATE/DELETE, commit, and return lastrowid."""
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    email         TEXT    UNIQUE NOT NULL,
    password_hash TEXT    NOT NULL,
    is_admin      INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS categories (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT    UNIQUE NOT NULL,
    icon  TEXT,
    image TEXT
);

CREATE TABLE IF NOT EXISTS restaurants (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    cuisine       TEXT,
    rating        REAL    DEFAULT 4.0,
    delivery_time TEXT,
    image         TEXT,
    description   TEXT,
    active        INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS food_items (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER NOT NULL,
    category_id   INTEGER,
    name          TEXT    NOT NULL,
    description   TEXT,
    price         REAL    NOT NULL,
    image         TEXT,
    is_veg        INTEGER DEFAULT 1,
    popular       INTEGER DEFAULT 0,
    active        INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id)   REFERENCES categories(id)  ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS addresses (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    full_name  TEXT,
    phone      TEXT,
    address    TEXT,
    city       TEXT,
    postal_code TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS orders (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    full_name     TEXT,
    phone         TEXT,
    address       TEXT,
    city          TEXT,
    postal_code   TEXT,
    payment_method TEXT,
    subtotal      REAL,
    delivery_fee  REAL,
    total         REAL,
    status        TEXT    NOT NULL DEFAULT 'PLACED',
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS order_items (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id  INTEGER NOT NULL,
    food_id   INTEGER,
    food_name TEXT,
    price     REAL,
    quantity  INTEGER,
    FOREIGN KEY (order_id) REFERENCES orders(id)     ON DELETE CASCADE,
    FOREIGN KEY (food_id)  REFERENCES food_items(id) ON DELETE SET NULL
);
"""


def init_db():
    """Create all tables if they do not yet exist."""
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()


def init_app(app):
    """Register close_db on app teardown."""
    app.teardown_appcontext(close_db)
