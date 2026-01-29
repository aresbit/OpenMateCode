#!/usr/bin/env python3
"""Local Memory System for MateCode - SQLite-based long-term memory"""

import os
import json
import sqlite3
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Configuration
MEMORY_DIR = os.path.expanduser("~/.matecode")
MEMORY_DB = os.path.join(MEMORY_DIR, "memory.db")


class LocalMemory:
    """Local SQLite-based memory storage with FTS5 search."""

    def __init__(self, db_path: str = MEMORY_DB):
        self.db_path = db_path
        self._ensure_dir()
        self._init_db()

    def _ensure_dir(self):
        """Ensure memory directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _init_db(self):
        """Initialize SQLite database with FTS5."""
        conn = sqlite3.connect(self.db_path)
        try:
            # Main memories table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    message_type TEXT DEFAULT 'conversation'
                )
            """)

            # FTS5 virtual table for full-text search
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_search
                USING fts5(content, content_rowid=rowid)
            """)

            # Index for faster user queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id
                ON memories(user_id)
            """)

            conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()

    def _generate_id(self, user_id: str, content: str) -> str:
        """Generate unique ID for memory entry."""
        data = f"{user_id}:{content}:{datetime.now().isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()

    def add(self, user_id: str, content: str, metadata: Optional[Dict] = None,
            message_type: str = "conversation") -> bool:
        """
        Add a memory entry.

        Args:
            user_id: User identifier (e.g., telegram chat_id)
            content: Memory content to store
            metadata: Optional metadata dictionary
            message_type: Type of message (conversation, note, etc.)

        Returns:
            True if successful, False otherwise
        """
        if not content or not content.strip():
            return False

        # Clean and truncate content if needed
        content = content.strip()[:10000]  # Max 10k chars

        memory_id = self._generate_id(user_id, content)
        metadata_json = json.dumps(metadata) if metadata else None

        conn = sqlite3.connect(self.db_path)
        try:
            # Insert into main table
            conn.execute(
                """INSERT OR REPLACE INTO memories
                   (id, user_id, content, timestamp, metadata, message_type)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (memory_id, user_id, content, datetime.now(), metadata_json, message_type)
            )

            # Insert/update FTS index
            conn.execute(
                """INSERT OR REPLACE INTO memory_search(rowid, content)
                   VALUES ((SELECT rowid FROM memories WHERE id = ?), ?)""",
                (memory_id, content)
            )

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding memory: {e}")
            return False
        finally:
            conn.close()

    def search(self, user_id: str, query: str, limit: int = 5) -> List[Dict]:
        """
        Search memories using FTS5.

        Args:
            user_id: User identifier
            query: Search query
            limit: Maximum results to return

        Returns:
            List of memory entries sorted by relevance
        """
        if not query or not query.strip():
            return []

        # Sanitize query for FTS5
        query = self._sanitize_query(query)
        if not query:
            return []

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """SELECT m.id, m.content, m.timestamp, m.metadata,
                          rank as relevance
                   FROM memories m
                   JOIN memory_search s ON m.rowid = s.rowid
                   WHERE m.user_id = ? AND memory_search MATCH ?
                   ORDER BY rank
                   LIMIT ?""",
                (user_id, query, limit)
            )

            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "content": row[1],
                    "timestamp": row[2],
                    "metadata": json.loads(row[3]) if row[3] else None,
                    "relevance": row[4]
                })
            return results
        except sqlite3.Error as e:
            print(f"Error searching memories: {e}")
            return []
        finally:
            conn.close()

    def get_recent(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent memories without search."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """SELECT id, content, timestamp, metadata
                   FROM memories
                   WHERE user_id = ?
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (user_id, limit)
            )

            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "content": row[1],
                    "timestamp": row[2],
                    "metadata": json.loads(row[3]) if row[3] else None
                })
            return results
        except sqlite3.Error as e:
            print(f"Error getting recent memories: {e}")
            return []
        finally:
            conn.close()

    def delete(self, user_id: str, memory_id: str) -> bool:
        """Delete a specific memory by ID."""
        conn = sqlite3.connect(self.db_path)
        try:
            # Get rowid before deleting
            cursor = conn.execute(
                "SELECT rowid FROM memories WHERE id = ? AND user_id = ?",
                (memory_id, user_id)
            )
            row = cursor.fetchone()
            if not row:
                return False

            rowid = row[0]

            # Delete from main table
            conn.execute(
                "DELETE FROM memories WHERE id = ? AND user_id = ?",
                (memory_id, user_id)
            )

            # Delete from FTS index
            conn.execute(
                "DELETE FROM memory_search WHERE rowid = ?",
                (rowid,)
            )

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting memory: {e}")
            return False
        finally:
            conn.close()

    def delete_by_query(self, user_id: str, query: str) -> int:
        """
        Delete memories matching a query.

        Returns:
            Number of deleted memories
        """
        # Find matching memories first
        matches = self.search(user_id, query, limit=100)
        count = 0
        for mem in matches:
            if self.delete(user_id, mem["id"]):
                count += 1
        return count

    def clear_all(self, user_id: str) -> bool:
        """Clear all memories for a user."""
        conn = sqlite3.connect(self.db_path)
        try:
            # Get all rowids to delete from FTS
            cursor = conn.execute(
                "SELECT rowid FROM memories WHERE user_id = ?",
                (user_id,)
            )
            rowids = [row[0] for row in cursor.fetchall()]

            # Delete from main table
            conn.execute(
                "DELETE FROM memories WHERE user_id = ?",
                (user_id,)
            )

            # Delete from FTS index
            for rowid in rowids:
                conn.execute(
                    "DELETE FROM memory_search WHERE rowid = ?",
                    (rowid,)
                )

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error clearing memories: {e}")
            return False
        finally:
            conn.close()

    def get_stats(self, user_id: str) -> Dict:
        """Get memory statistics for a user."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "SELECT COUNT(*), MAX(timestamp), MIN(timestamp) FROM memories WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return {
                "count": row[0] or 0,
                "newest": row[1],
                "oldest": row[2]
            }
        except sqlite3.Error as e:
            print(f"Error getting stats: {e}")
            return {"count": 0, "newest": None, "oldest": None}
        finally:
            conn.close()

    def _sanitize_query(self, query: str) -> str:
        """Sanitize query string for FTS5."""
        # Remove FTS5 special characters that could cause syntax errors
        # Keep only alphanumeric, spaces, and basic punctuation
        query = re.sub(r'[^\w\s\-_.]', ' ', query)

        # Split into words and make each word a prefix match
        words = query.split()
        if not words:
            return ""

        # Join with AND for better relevance
        return " AND ".join(f"{word}*" for word in words if len(word) >= 2)

    def format_for_prompt(self, memories: List[Dict], max_chars: int = 2000) -> str:
        """
        Format memories for injection into Claude prompt.

        Args:
            memories: List of memory dictionaries
            max_chars: Maximum characters to return

        Returns:
            Formatted context string
        """
        if not memories:
            return ""

        lines = ["【历史记忆】", ""]
        current_len = len("【历史记忆】\n\n")

        for mem in memories:
            content = mem["content"].replace("\n", " ")
            line = f"• {content}"

            if current_len + len(line) + 1 > max_chars:
                break

            lines.append(line)
            current_len += len(line) + 1

        return "\n".join(lines)


# Singleton instance
_memory_instance: Optional[LocalMemory] = None


def get_memory() -> LocalMemory:
    """Get or create singleton memory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = LocalMemory()
    return _memory_instance


if __name__ == "__main__":
    # Simple test
    mem = LocalMemory()

    # Test add
    mem.add("user_123", "Python is a great programming language")
    mem.add("user_123", "I prefer using SQLite for local storage")
    mem.add("user_123", "Machine learning is fascinating")

    # Test search
    print("Search 'python':")
    for r in mem.search("user_123", "python"):
        print(f"  - {r['content']}")

    print("\nSearch 'storage':")
    for r in mem.search("user_123", "storage"):
        print(f"  - {r['content']}")

    # Test stats
    print(f"\nStats: {mem.get_stats('user_123')}")
