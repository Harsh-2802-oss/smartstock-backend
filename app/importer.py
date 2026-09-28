"""Loads smartstockdatabase.sql (a pg_dump with COPY blocks) into whichever database is configured,
SQLite or PostgreSQL, and makes sure every store has a login."""
import os
import re
from datetime import datetime
from pathlib import Path

from sqlalchemy import DateTime, Integer, Numeric, text
from sqlalchemy.orm import Session

from . import auth, models
from .database import Base

SQL_FILE = Path(os.getenv("SMARTSTOCK_SQL", Path(__file__).resolve().parent.parent / "database" / "smartstockdatabase.sql"))
ADMIN_PASSWORD = os.getenv("SMARTSTOCK_ADMIN_PASSWORD", "smartstock-demo")
COPY_RE = re.compile(r"^COPY (?:public\.)?(\w+) \(([^)]*)\) FROM stdin;$")
ESCAPES = {"t": "\t", "n": "\n", "r": "\r", "\\": "\\"}


def _unescape(v: str) -> str:
    return re.sub(r"\\(.)", lambda m: ESCAPES.get(m.group(1), m.group(1)), v)


def _timestamp(v: str) -> datetime:
    # Postgres prints 1-6 fractional digits; datetime.fromisoformat on 3.10 only takes 3 or 6.
    m = re.match(r"(\d{4}-\d\d-\d\d)[ T](\d\d:\d\d:\d\d)(?:\.(\d+))?", v)
    micro = int((m.group(3) or "0").ljust(6, "0")[:6])
    return datetime.fromisoformat(f"{m.group(1)}T{m.group(2)}").replace(microsecond=micro)


def _coerce(column, raw: str):
    if raw == r"\N":
        return None
    v = _unescape(raw)
    if isinstance(column.type, Integer):
        return int(v)
    if isinstance(column.type, Numeric):
        return float(v)
    if isinstance(column.type, DateTime):
        return _timestamp(v)
    return v


def parse_dump(path: Path) -> dict:
    tables, current = {}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if current is None:
            m = COPY_RE.match(line)
            if m:
                current = (m.group(1), [c.strip() for c in m.group(2).split(",")])
                tables[current[0]] = []
        elif line == r"\.":
            current = None
        else:
            tables[current[0]].append(dict(zip(current[1], line.split("\t"))))
    return tables


def import_dump(db: Session, path: Path = SQL_FILE) -> dict:
    data, counts = parse_dump(path), {}
    for table in Base.metadata.sorted_tables:  # parents before children
        rows = data.get(table.name)
        if rows:
            db.execute(table.insert(), [{k: _coerce(table.c[k], v) for k, v in r.items() if k in table.c} for r in rows])
            counts[table.name] = len(rows)
    if db.get_bind().dialect.name == "postgresql":  # explicit ids were inserted, so move the sequences past them
        for t in Base.metadata.sorted_tables:
            pk = list(t.primary_key.columns)
            if len(pk) == 1 and isinstance(pk[0].type, Integer):
                c = pk[0].name
                db.execute(text(f"SELECT setval(pg_get_serial_sequence('{t.name}', '{c}'), "
                                f"COALESCE(MAX({c}), 1), MAX({c}) IS NOT NULL) FROM {t.name}"))
    db.commit()
    return counts


def bootstrap(db: Session):
    """First run: import the dump if the database is empty, then give each store without a user a login."""
    if db.query(models.Store).count() == 0 and SQL_FILE.exists():
        print("SmartStock: importing", SQL_FILE.name, import_dump(db))
    for s in db.query(models.Store).all():
        email = (s.email or "").lower()
        if email and not db.query(models.User).filter_by(store_id=s.store_id).first() \
                and not db.query(models.User).filter_by(email=email).first():
            db.add(models.User(store_id=s.store_id, email=email, hashed_password=auth.hash_password(ADMIN_PASSWORD)))
            print(f"SmartStock: created login {email} for '{s.store_name}'")
    db.commit()
