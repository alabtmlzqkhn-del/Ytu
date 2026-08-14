import os
import sqlite3
import threading
import time


class LocalDB:
    def __init__(self, path="jack.db"):
        self.path = os.getenv("LOCAL_DB_PATH", path)
        self.lock = threading.RLock()

        folder = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(folder, exist_ok=True)

        self.conn = sqlite3.connect(
            self.path,
            check_same_thread=False
        )

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS data (
                key TEXT PRIMARY KEY,
                value BLOB,
                expires REAL
            )
        """)

        self.conn.commit()

    def _cleanup(self):
        now = time.time()
        self.conn.execute(
            "DELETE FROM data WHERE expires IS NOT NULL AND expires <= ?",
            (now,)
        )
        self.conn.commit()

    def set(self, key, value, ex=None):
        with self.lock:
            expires = time.time() + ex if ex else None

            self.conn.execute("""
                INSERT INTO data (key, value, expires)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    expires = excluded.expires
            """, (str(key), str(value), expires))

            self.conn.commit()
            return True

    def get(self, key):
        with self.lock:
            self._cleanup()

            cursor = self.conn.execute(
                "SELECT value FROM data WHERE key = ?",
                (str(key),)
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return row[0]

    def delete(self, key):
        with self.lock:
            self.conn.execute(
                "DELETE FROM data WHERE key = ?",
                (str(key),)
            )
            self.conn.commit()
            return True

    def exists(self, key):
        return self.get(key) is not None

    def setex(self, key, seconds, value):
        return self.set(key, value, ex=seconds)

    def expire(self, key, seconds):
        with self.lock:
            if not self.exists(key):
                return False

            self.conn.execute(
                "UPDATE data SET expires = ? WHERE key = ?",
                (time.time() + seconds, str(key))
            )

            self.conn.commit()
            return True

    def incr(self, key, amount=1):
        with self.lock:
            current = self.get(key)

            try:
                current = int(current or 0)
            except Exception:
                current = 0

            current += amount
            self.set(key, current)

            return current

    def decr(self, key, amount=1):
        return self.incr(key, -amount)

    def close(self):
        with self.lock:
            try:
                self.conn.close()
            except Exception:
                pass


r = LocalDB("jack.db")
