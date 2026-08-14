import sqlite3
import threading
import time
import fnmatch
import json
import os

class LocalDB:
    """Small Redis-compatible subset backed by SQLite. No Redis server required."""
    def __init__(self, path="jack.db", decode_responses=True):
        self.path = path
        self.decode_responses = decode_responses
        self.lock = threading.RLock()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS kv (
                key TEXT PRIMARY KEY,
                kind TEXT NOT NULL DEFAULT 'string',
                value TEXT NOT NULL,
                expires REAL
            )
        """)
        self.conn.commit()

    def _cleanup(self, key=None):
        now = time.time()
        if key is None:
            self.conn.execute("DELETE FROM kv WHERE expires IS NOT NULL AND expires <= ?", (now,))
        else:
            self.conn.execute("DELETE FROM kv WHERE key=? AND expires IS NOT NULL AND expires <= ?", (key, now))
        self.conn.commit()

    def ping(self):
        with self.lock:
            self.conn.execute("SELECT 1").fetchone()
        return True

    def _getrow(self, key):
        self._cleanup(key)
        return self.conn.execute("SELECT kind,value,expires FROM kv WHERE key=?", (str(key),)).fetchone()

    def get(self, key):
        with self.lock:
            row = self._getrow(key)
            return None if row is None or row[0] != "string" else row[1]

    def set(self, key, value, ex=None, **kwargs):
        with self.lock:
            expires = time.time() + ex if ex is not None else None
            self.conn.execute(
                "INSERT INTO kv(key,kind,value,expires) VALUES(?,?,?,?) "
                "ON CONFLICT(key) DO UPDATE SET kind=excluded.kind,value=excluded.value,expires=excluded.expires",
                (str(key), "string", str(value), expires)
            )
            self.conn.commit()
            return True

    def setex(self, key, seconds, value):
        return self.set(key, value, ex=seconds)

    def delete(self, *keys):
        with self.lock:
            qmarks=",".join("?" for _ in keys)
            cur=self.conn.execute(f"DELETE FROM kv WHERE key IN ({qmarks})", tuple(map(str,keys)))
            self.conn.commit()
            return cur.rowcount

    def exists(self, key):
        return self._getrow(key) is not None

    def ttl(self, key):
        with self.lock:
            row=self._getrow(key)
            if row is None: return -2
            if row[2] is None: return -1
            return max(0, int(row[2]-time.time()))

    def _hash(self, key):
        row=self._getrow(key)
        data={}
        if row is not None:
            if row[0] != "hash": raise TypeError("WRONGTYPE")
            try: data=json.loads(row[1])
            except Exception: data={}
        return data

    def hset(self, key, field=None, value=None, mapping=None, **kwargs):
        with self.lock:
            data=self._hash(key)
            if mapping is not None: data.update({str(k):str(v) for k,v in mapping.items()})
            elif field is not None: data[str(field)]=str(value)
            else: data.update({str(k):str(v) for k,v in kwargs.items()})
            self.conn.execute(
                "INSERT INTO kv(key,kind,value,expires) VALUES(?,?,?,NULL) "
                "ON CONFLICT(key) DO UPDATE SET kind='hash',value=excluded.value,expires=NULL",
                (str(key),"hash",json.dumps(data,ensure_ascii=False))
            )
            self.conn.commit()
            return 1

    def hget(self,key,field):
        with self.lock:
            return self._hash(key).get(str(field))

    def hgetall(self,key):
        with self.lock:
            return self._hash(key)

    def hdel(self,key,*fields):
        with self.lock:
            data=self._hash(key)
            n=0
            for f in fields:
                if str(f) in data:
                    del data[str(f)]; n+=1
            self._save_hash(key,data)
            return n

    def hexists(self,key,field):
        return str(field) in self._hash(key)

    def hlen(self,key):
        return len(self._hash(key))

    def _save_hash(self,key,data):
        if not data:
            self.conn.execute("DELETE FROM kv WHERE key=?", (str(key),))
        else:
            self.conn.execute("UPDATE kv SET kind='hash',value=?,expires=NULL WHERE key=?",
                              (json.dumps(data,ensure_ascii=False),str(key)))
        self.conn.commit()

    def _setdata(self,key):
        row=self._getrow(key)
        if row is None: return set()
        if row[0] != "set": raise TypeError("WRONGTYPE")
        try: return set(json.loads(row[1]))
        except Exception: return set()

    def sadd(self,key,*members):
        with self.lock:
            data=self._setdata(key)
            before=len(data)
            data.update(str(x) for x in members)
            self.conn.execute(
                "INSERT INTO kv(key,kind,value,expires) VALUES(?,?,?,NULL) "
                "ON CONFLICT(key) DO UPDATE SET kind='set',value=excluded.value,expires=NULL",
                (str(key),"set",json.dumps(list(data),ensure_ascii=False))
            )
            self.conn.commit()
            return len(data)-before

    def smembers(self,key):
        with self.lock:
            return self._setdata(key)

    def srem(self,key,*members):
        with self.lock:
            data=self._setdata(key); before=len(data)
            for x in members: data.discard(str(x))
            if data:
                self.conn.execute("UPDATE kv SET value=? WHERE key=?",
                                  (json.dumps(list(data),ensure_ascii=False),str(key)))
            else:
                self.conn.execute("DELETE FROM kv WHERE key=?",(str(key),))
            self.conn.commit()
            return before-len(data)

    def sismember(self,key,member):
        return str(member) in self._setdata(key)

    def scard(self,key):
        return len(self._setdata(key))

    def keys(self,pattern="*"):
        with self.lock:
            self._cleanup()
            keys=[r[0] for r in self.conn.execute("SELECT key FROM kv").fetchall()]
            return [k for k in keys if fnmatch.fnmatchcase(k, pattern)]

    def scan_iter(self, match=None, count=None):
        for key in self.keys(match or "*"):
            yield key

# One process-wide database object, matching the source's global `r`.
r = LocalDB(os.getenv("LOCAL_DB_PATH", "jack.db"))
