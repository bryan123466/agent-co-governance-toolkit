"""Durable local records and a nonblocking operating-system mutation guard."""
from __future__ import annotations

from contextlib import contextmanager, closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
import threading


class GovernanceError(Exception):
    def __init__(self, code, message, details=None):
        super().__init__(message)
        self.code, self.message, self.details = code, message, details


def now():
    return datetime.now(timezone.utc).isoformat()


def _linked(path):
    try:
        return path.is_symlink() or bool(getattr(path.lstat(), 'st_file_attributes', 0) & 0x400)
    except FileNotFoundError:
        return False


class Store:
    def __init__(self, project, create=False):
        raw_root = Path(project).expanduser().absolute()
        if any(_linked(p) for p in (raw_root, *raw_root.parents)):
            raise GovernanceError('UNSAFE_METADATA', 'The project location cannot traverse symbolic links or junctions.')
        self.root = raw_root.resolve()
        self.directory = self.root / '.agct'
        self.path = self.directory / 'state.sqlite3'
        self._mutex = threading.RLock()
        self._depth = 0
        self._lock_handle = None
        if _linked(self.directory):
            raise GovernanceError('UNSAFE_METADATA', 'Governance metadata cannot be a symbolic link.')
        if create:
            self.root.mkdir(parents=True, exist_ok=True)
            self.directory.mkdir(exist_ok=True)
            with self.guard():
                if _linked(self.path):
                    raise GovernanceError('UNSAFE_METADATA', 'The state database cannot be a symbolic link.')
                with closing(sqlite3.connect(self.path, timeout=0)) as db:
                    db.execute('PRAGMA journal_mode=WAL')
                    db.execute('PRAGMA synchronous=FULL')
                    db.executescript('''
                        CREATE TABLE IF NOT EXISTS records (
                            collection TEXT NOT NULL, key TEXT NOT NULL,
                            value TEXT NOT NULL, PRIMARY KEY(collection,key));
                        CREATE TABLE IF NOT EXISTS events (
                            sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                            created_at TEXT NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL);
                    ''')
        elif not self.path.is_file():
            raise GovernanceError('NOT_INITIALIZED', 'Initialize this project before using governance.')
        if _linked(self.path):
            raise GovernanceError('UNSAFE_METADATA', 'The state database cannot be a symbolic link.')

    @contextmanager
    def _connect(self):
        if _linked(self.directory) or _linked(self.path):
            raise GovernanceError('UNSAFE_METADATA', 'Metadata changed to a symbolic link or junction.')
        connection = sqlite3.connect(self.path.as_uri() + '?mode=rw', uri=True, timeout=0)
        try:
            connection.execute('PRAGMA synchronous=FULL')
            with connection:
                yield connection
        finally:
            connection.close()

    @contextmanager
    def guard(self):
        if not self._mutex.acquire(blocking=False):
            raise GovernanceError('BUSY', 'Another operation is changing this project; retry after it completes.')
        acquired = False
        try:
            if self._depth == 0:
                lock_path = self.directory / 'mutation.lock'
                if _linked(self.directory) or _linked(lock_path):
                    raise GovernanceError('UNSAFE_METADATA', 'The mutation guard cannot be a symbolic link.')
                self._lock_handle = open(lock_path, 'a+b')
                self._lock_handle.seek(0, os.SEEK_END)
                if self._lock_handle.tell() == 0:
                    self._lock_handle.write(b'0')
                    self._lock_handle.flush()
                self._lock_handle.seek(0)
                try:
                    if os.name == 'nt':
                        import msvcrt
                        msvcrt.locking(self._lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(self._lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except (OSError, BlockingIOError) as exc:
                    self._lock_handle.close()
                    self._lock_handle = None
                    raise GovernanceError('BUSY', 'Another process holds the project mutation guard.') from exc
            self._depth += 1
            acquired = True
            yield self
        finally:
            if acquired:
                self._depth -= 1
                if self._depth == 0 and self._lock_handle is not None:
                    try:
                        self._lock_handle.seek(0)
                        if os.name == 'nt':
                            import msvcrt
                            msvcrt.locking(self._lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
                        else:
                            import fcntl
                            fcntl.flock(self._lock_handle, fcntl.LOCK_UN)
                    finally:
                        self._lock_handle.close()
                        self._lock_handle = None
            self._mutex.release()

    def get(self, collection, key, default=None):
        with self._connect() as db:
            row = db.execute('SELECT value FROM records WHERE collection=? AND key=?', (collection, key)).fetchone()
        return json.loads(row[0]) if row else default

    def put(self, collection, key, value):
        serialized = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
        with self.guard(), self._connect() as db:
            db.execute('INSERT INTO records(collection,key,value) VALUES(?,?,?) '
                       'ON CONFLICT(collection,key) DO UPDATE SET value=excluded.value',
                       (collection, key, serialized))
        return value

    def list(self, collection):
        with self._connect() as db:
            rows = db.execute('SELECT value FROM records WHERE collection=? ORDER BY key', (collection,)).fetchall()
        return [json.loads(row[0]) for row in rows]

    def event(self, kind, payload):
        with self.guard(), self._connect() as db:
            cursor = db.execute('INSERT INTO events(created_at,kind,payload) VALUES(?,?,?)',
                                (now(), kind, json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False)))
            return cursor.lastrowid

    def events(self):
        with self._connect() as db:
            rows = db.execute('SELECT sequence,created_at,kind,payload FROM events ORDER BY sequence').fetchall()
        return [dict(sequence=r[0], created_at=r[1], kind=r[2], payload=json.loads(r[3])) for r in rows]
