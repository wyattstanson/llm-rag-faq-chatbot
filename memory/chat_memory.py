import sqlite3
import json
import uuid
import os
from datetime import datetime
from config.settings import SQLITE_DB_PATH

os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)


def get_conn():
    conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            mode TEXT DEFAULT 'general',
            pinned INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT,
            role TEXT,
            content TEXT,
            sources TEXT,
            created_at TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)
    conn.commit()

    conv_cols = [r[1] for r in conn.execute("PRAGMA table_info(conversations)").fetchall()]
    msg_cols  = [r[1] for r in conn.execute("PRAGMA table_info(messages)").fetchall()]

    if "mode" not in conv_cols:
        conn.execute("ALTER TABLE conversations ADD COLUMN mode TEXT DEFAULT 'general'")
        conn.execute("UPDATE conversations SET mode = 'general' WHERE mode IS NULL")
    if "pinned" not in conv_cols:
        conn.execute("ALTER TABLE conversations ADD COLUMN pinned INTEGER DEFAULT 0")
        conn.execute("UPDATE conversations SET pinned = 0 WHERE pinned IS NULL")
    if "sources" not in msg_cols:
        conn.execute("ALTER TABLE messages ADD COLUMN sources TEXT DEFAULT '[]'")
        conn.execute("UPDATE messages SET sources = '[]' WHERE sources IS NULL")

    conn.commit()
    conn.close()


def _safe(d, key, default):
    v = d.get(key)
    return v if v is not None else default


def _conv(row):
    d = dict(row)
    d["mode"]   = _safe(d, "mode",   "general")
    d["pinned"] = int(_safe(d, "pinned", 0))
    return d


def create_conversation(title="New Chat", mode="general"):
    conn = get_conn()
    cid  = str(uuid.uuid4())
    now  = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO conversations (id, title, mode, pinned, created_at, updated_at) VALUES (?, ?, ?, 0, ?, ?)",
        (cid, title, mode, now, now)
    )
    conn.commit()
    conn.close()
    return cid


def get_conversations():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM conversations ORDER BY pinned DESC, updated_at DESC"
    ).fetchall()
    conn.close()
    return [_conv(r) for r in rows]


def get_conversation(cid):
    conn = get_conn()
    row  = conn.execute("SELECT * FROM conversations WHERE id=?", (cid,)).fetchone()
    conn.close()
    return _conv(row) if row else None


def update_conversation_title(cid, title):
    conn = get_conn()
    conn.execute(
        "UPDATE conversations SET title=?, updated_at=? WHERE id=?",
        (title, datetime.utcnow().isoformat(), cid)
    )
    conn.commit()
    conn.close()


def toggle_pin(cid):
    conn  = get_conn()
    row   = conn.execute("SELECT pinned FROM conversations WHERE id=?", (cid,)).fetchone()
    if row:
        new_val = 0 if int(row["pinned"] or 0) else 1
        conn.execute("UPDATE conversations SET pinned=? WHERE id=?", (new_val, cid))
        conn.commit()
    conn.close()


def delete_conversation(cid):
    conn = get_conn()
    conn.execute("DELETE FROM messages WHERE conversation_id=?", (cid,))
    conn.execute("DELETE FROM conversations WHERE id=?", (cid,))
    conn.commit()
    conn.close()


def add_message(conversation_id, role, content, sources=None):
    conn = get_conn()
    mid  = str(uuid.uuid4())
    now  = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO messages (id, conversation_id, role, content, sources, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (mid, conversation_id, role, content, json.dumps(sources or []), now)
    )
    conn.execute("UPDATE conversations SET updated_at=? WHERE id=?", (now, conversation_id))
    conn.commit()
    conn.close()
    return mid


def get_messages(conversation_id, limit=None):
    conn  = get_conn()
    query = "SELECT * FROM messages WHERE conversation_id=? ORDER BY created_at ASC"
    if limit:
        query += f" LIMIT {limit}"
    rows = conn.execute(query, (conversation_id,)).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["sources"] = json.loads(d.get("sources") or "[]")
        result.append(d)
    return result


def get_recent_messages_for_llm(conversation_id, max_messages=20):
    msgs   = get_messages(conversation_id)
    recent = msgs[-max_messages:] if len(msgs) > max_messages else msgs
    return [{"role": m["role"], "content": m["content"]} for m in recent]


init_db()