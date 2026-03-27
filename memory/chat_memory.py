

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class ChatMemory:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)
            conn.commit()

   
    def new_conversation(self, title: str = "New conversation") -> str:
        cid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO conversations (id, title, created_at, updated_at) "
                "VALUES (?, ?, ?, ?)",
                (cid, title, now, now)
            )
            conn.commit()
        return cid

    def update_title(self, conv_id: str, title: str):
        with self._conn() as conn:
            conn.execute(
                "UPDATE conversations SET title=?, updated_at=? WHERE id=?",
                (title, datetime.utcnow().isoformat(), conv_id)
            )
            conn.commit()

    def list_conversations(self) -> List[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM conversations ORDER BY updated_at DESC LIMIT 50"
            ).fetchall()
        return [dict(r) for r in rows]

    def delete_conversation(self, conv_id: str):
        with self._conn() as conn:
            conn.execute("DELETE FROM messages WHERE conversation_id=?", (conv_id,))
            conn.execute("DELETE FROM conversations WHERE id=?", (conv_id,))
            conn.commit()

    

    def save_message(
        self,
        conv_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None
    ):
        now = datetime.utcnow().isoformat()
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, metadata, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (conv_id, role, content, json.dumps(metadata or {}), now)
            )
            conn.execute(
                "UPDATE conversations SET updated_at=? WHERE id=?",
                (now, conv_id)
            )
            conn.commit()

    def load_messages(self, conv_id: str) -> List[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT role, content, metadata FROM messages "
                "WHERE conversation_id=? ORDER BY id ASC",
                (conv_id,)
            ).fetchall()
        result = []
        for row in rows:
            meta = json.loads(row["metadata"] or "{}")
            result.append({
                "role": row["role"],
                "content": row["content"],
                "sources": meta.get("sources", []),
            })
        return result

    def get_recent_messages(self, conv_id: str, n: int = 10) -> List[dict]:
        msgs = self.load_messages(conv_id)
        return msgs[-n * 2:]  