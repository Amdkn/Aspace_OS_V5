#!/usr/bin/env python3
"""
01_Forkable/FKB07_Money_Maker/01_Trading/aspace_trading_copilot_foundation.py
Organe canonique K5 Trading (`CORPS` · Famille `F-CORPS-05`) — Fondation A'Space OS V5.

Porte 1:1 sans perte le cœur fonctionnel et le corpus SQLite FTS5 de `M074`
(`tradingview-indicator-search-mcp-server`) sous veto humain S0 lecture seule (`ADR-07`),
raccordé au bus L0 (`EventJournal`, `R10Ledger`, `consign_measured_l0_evidence`) de
`fondation-13-1` (`aspace_foundation_kernel.py`), sans aucune auto-certification.
"""

from __future__ import annotations

import copy
import json
import math
import os
import pathlib
import re
import sqlite3
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence
from urllib.parse import quote, urlencode

_HERE = Path(__file__).resolve()
WORKSPACE_ROOT = _HERE.parents[3]
_CORE_DIR = WORKSPACE_ROOT / "01_Forkable" / "FKB00_Runtime" / "00_A0_Core"
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from aspace_foundation_kernel import (  # noqa: E402
    ContractViolation,
    consign_measured_l0_evidence,
)

TV_ORIGIN = "https://www.tradingview.com"
FACADE_ORIGIN = "https://pine-facade.tradingview.com"
ACCESS_OPEN = 1
READ_ONLY_VETO_S0 = True

DEFAULT_TRADINGVIEW_CONFIG: Dict[str, Any] = {
    "minDelayMs": 1500,
    "maxDelayMs": 4500,
    "breakEvery": 25,
    "breakMinMs": 20_000,
    "breakMaxMs": 60_000,
    "dailyBudget": 2000,
    "maxRetries": 4,
    "backoffBaseMs": 2000,
    "backoffMaxMs": 60_000,
    "breakerThreshold": 3,
    "breakerCooldownMs": 15 * 60 * 1000,
    "requestTimeoutMs": 30_000,
    "listingTtlMs": 6 * 60 * 60 * 1000,
    "harvestMaxScripts": 200,
    "harvestTimeBudgetMs": 120_000,
    "snippetChars": 300,
    "cookieMaxAgeMs": 12 * 60 * 60 * 1000,
}

_SCRIPT_TYPE_MAP: Dict[str, str] = {
    "indicator": "indicators",
    "indicators": "indicators",
    "strategy": "strategies",
    "strategies": "strategies",
    "library": "libraries",
    "libraries": "libraries",
    "all": "all",
}

_PUB_ID_RE = re.compile(r"(PUB|USER);[0-9a-fA-F]{32}")
_SCRIPT_ID_PART_RE = re.compile(r"^(PUB|USER);[A-Za-z0-9]+$", re.IGNORECASE)
_PINE_VERSION_RE = re.compile(r"^\s*//\s*@version\s*=\s*(\d+)", re.MULTILINE)
_CHART_SLUG_RE = re.compile(r"tradingview\.com/script/([A-Za-z0-9]+)")

_CORPUS_SCHEMA = """
CREATE TABLE IF NOT EXISTS scripts (
  script_id_part TEXT PRIMARY KEY,
  script_id      INTEGER,
  name           TEXT,
  author         TEXT,
  author_id      INTEGER,
  script_type    TEXT,
  script_access  INTEGER,
  open_source    INTEGER,
  version        TEXT,
  likes          INTEGER,
  comments       INTEGER,
  views          INTEGER,
  created_at     TEXT,
  updated_at     TEXT,
  chart_url      TEXT,
  image_url      TEXT,
  symbol         TEXT,
  interval       TEXT,
  is_picked      INTEGER,
  is_hot         INTEGER,
  description    TEXT,
  fetched_at     INTEGER
);
CREATE INDEX IF NOT EXISTS idx_scripts_author ON scripts(author);
CREATE INDEX IF NOT EXISTS idx_scripts_type   ON scripts(script_type);
CREATE INDEX IF NOT EXISTS idx_scripts_likes  ON scripts(likes DESC);

CREATE TABLE IF NOT EXISTS sources (
  script_id_part TEXT NOT NULL,
  version        TEXT NOT NULL,
  source         TEXT,
  pine_version   INTEGER,
  kind           TEXT,
  script_name    TEXT,
  fetched_at     INTEGER,
  PRIMARY KEY (script_id_part, version)
);

CREATE TABLE IF NOT EXISTS searches (
  cache_key  TEXT PRIMARY KEY,
  kind       TEXT,
  params     TEXT,
  total      INTEGER,
  has_more   INTEGER,
  payload    TEXT,
  fetched_at INTEGER
);

CREATE TABLE IF NOT EXISTS harvests (
  id         TEXT PRIMARY KEY,
  spec       TEXT,
  status     TEXT,
  cursor     TEXT,
  scripts_seen   INTEGER DEFAULT 0,
  sources_stored INTEGER DEFAULT 0,
  started_at INTEGER,
  updated_at INTEGER,
  note       TEXT
);

CREATE TABLE IF NOT EXISTS request_log (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  ts      INTEGER,
  day     TEXT,
  host    TEXT,
  path    TEXT,
  status  INTEGER,
  ms      INTEGER,
  outcome TEXT
);
CREATE INDEX IF NOT EXISTS idx_request_log_day ON request_log(day);

CREATE TABLE IF NOT EXISTS cookies (
  host       TEXT PRIMARY KEY,
  jar        TEXT,
  updated_at INTEGER
);

CREATE VIRTUAL TABLE IF NOT EXISTS corpus_fts USING fts5(
  script_id_part UNINDEXED,
  name,
  author,
  description,
  source
);
"""


def _nullish(value: Any, default: Any = None) -> Any:
    """Reproduit l'opérateur JS `??` : seul None bascule sur default."""
    return default if value is None else value


def _now_ms() -> int:
    return int(time.time() * 1000)


# ===========================================================================
# 1. Parseurs purs TradingView (src/parse.js)
# ===========================================================================


def tv_slugify(query: Any) -> str:
    """Convertit une requête thématique en slug TradingView URL-safe."""
    text = str(query if query else "").strip().lower()
    text = re.sub(r"['\u2019]", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def tv_normalize_item(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalise une fiche script (slug-feed ou author-feed) vers le schéma canonique."""
    access = _nullish(raw.get("script_access"), None)
    user = raw.get("user") if isinstance(raw.get("user"), dict) else {}
    image = raw.get("image") if isinstance(raw.get("image"), dict) else {}
    symbol = raw.get("symbol") if isinstance(raw.get("symbol"), dict) else {}
    return {
        "script_id_part": _nullish(raw.get("script_id_part"), None),
        "script_id": _nullish(raw.get("id"), None),
        "name": _nullish(raw.get("name"), None),
        "author": _nullish(user.get("username"), None),
        "author_id": _nullish(user.get("id"), None),
        "script_type": _nullish(raw.get("script_type"), None),
        "script_access": access,
        "open_source": access == ACCESS_OPEN,
        "version": _nullish(raw.get("version"), None),
        "likes": _nullish(raw.get("likes_count"), 0),
        "comments": _nullish(raw.get("comments_count"), 0),
        "views": _nullish(raw.get("views_count"), 0),
        "created_at": _nullish(raw.get("created_at"), None),
        "updated_at": _nullish(raw.get("updated_at"), None),
        "chart_url": _nullish(raw.get("chart_url"), None),
        "image_url": _nullish(image.get("big"), _nullish(raw.get("image_url"), None)),
        "symbol": _nullish(symbol.get("name"), None),
        "interval": _nullish(symbol.get("interval"), None),
        "is_picked": bool(raw.get("is_picked")),
        "is_hot": bool(raw.get("is_hot")),
        "description": _nullish(raw.get("description"), ""),
    }


def tv_parse_slug_feed(payload: Any) -> Dict[str, Any]:
    """Parse `/scripts/<slug>/?component-data-only=1` (data.ideas.data)."""
    data = payload.get("data") if isinstance(payload, dict) else None
    ideas = data.get("ideas") if isinstance(data, dict) else None
    feed = ideas.get("data") if isinstance(ideas, dict) else None
    if not isinstance(feed, dict) or not isinstance(feed.get("items"), list):
        raise ValueError("Unexpected slug-feed shape: data.ideas.data.items missing")
    meta = payload.get("meta") if isinstance(payload, dict) and isinstance(payload.get("meta"), dict) else {}
    return {
        "total": _nullish(feed.get("total"), 0),
        "has_more": bool(feed.get("next")),
        "next_path": _nullish(feed.get("next"), None),
        "heading": _nullish(meta.get("heading"), None),
        "items": [tv_normalize_item(it) for it in feed["items"]],
    }


def tv_parse_author_feed(payload: Any) -> Dict[str, Any]:
    """Parse `/api/v1/scripts/?by=<username>`."""
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise ValueError("Unexpected author-feed shape: results missing")
    results = payload["results"]
    return {
        "total": _nullish(payload.get("count"), len(results)),
        "page_count": _nullish(payload.get("page_count"), 1),
        "has_more": bool(payload.get("next")),
        "next_path": _nullish(payload.get("next"), None),
        "items": [tv_normalize_item(it) for it in results],
    }


def tv_detect_pine_version(source: Any) -> Optional[int]:
    """Extrait la version `//@version=N` d'une source Pine Script."""
    match = _PINE_VERSION_RE.search(source or "")
    return int(match.group(1)) if match else None


def tv_parse_facade(payload: Any, *, script_id_part: Optional[str] = None) -> Dict[str, Any]:
    """Parse la réponse `/pine-facade/get/...` sans confondre un refus `{success:false}` avec du code."""
    if not isinstance(payload, dict) or payload.get("success") is False or not isinstance(payload.get("source"), str):
        reason = payload.get("reason") if isinstance(payload, dict) else None
        return {
            "ok": False,
            "protected": True,
            "reason": _nullish(reason, "No source returned"),
            "script_id_part": _nullish(script_id_part, None),
        }
    extra = payload.get("extra") if isinstance(payload.get("extra"), dict) else {}
    kind = _nullish(extra.get("kind"), None)
    if kind == "strategy":
        script_type = "strategy"
    elif kind == "study":
        script_type = "indicator"
    else:
        script_type = kind
    source = payload["source"]
    return {
        "ok": True,
        "script_id_part": _nullish(script_id_part, None),
        "script_name": _nullish(payload.get("scriptName"), None),
        "version": _nullish(payload.get("version"), _nullish(payload.get("lastVersionMaj"), None)),
        "script_access": _nullish(payload.get("scriptAccess"), None),
        "kind": kind,
        "script_type": script_type,
        "pine_version": tv_detect_pine_version(source),
        "is_price_study": _nullish(extra.get("is_price_study"), None),
        "source": source,
        "source_chars": len(source),
    }


def tv_extract_id_from_chart_url(url: Any) -> Optional[str]:
    """Extrait l'identifiant court d'une URL TradingView `/script/<slug>-.../`."""
    match = _CHART_SLUG_RE.search(str(url if url is not None else ""))
    return match.group(1) if match else None


def _js_slice(text: str, end: int) -> str:
    """Reproduit String.prototype.slice(0, end) en unités UTF-16 comme V8/Node."""
    if end <= 0:
        return ""
    raw = text.encode("utf-16-le")
    if len(raw) <= end * 2:
        return text
    return raw[: end * 2].decode("utf-16-le", errors="replace")


def tv_snippet(text: Any, max_chars: int) -> str:
    """Compacte une description avec ellipse finale si elle dépasse `max_chars` (unités UTF-16)."""
    clean = re.sub(r"\s+", " ", str(text if text else "")).strip()
    if len(clean.encode("utf-16-le")) <= max_chars * 2:
        return clean
    return f"{_js_slice(clean, max_chars).rstrip()}\u2026"


def tv_to_listing(item: Dict[str, Any], snippet_chars: int) -> Dict[str, Any]:
    """Produit la vue synthétique d'un script sans description complète."""
    out: Dict[str, Any] = {}
    for key in ("script_id_part", "name", "author", "script_type"):
        if key in item:
            out[key] = item[key]
    out["open_source"] = bool(item.get("open_source"))
    for key in ("likes", "version", "symbol", "interval", "created_at", "chart_url"):
        if key in item:
            out[key] = item[key]
    out["description_snippet"] = tv_snippet(item.get("description"), snippet_chars)
    return out


# ===========================================================================
# 2. Corpus SQLite + FTS5 local (src/db.js)
# ===========================================================================


def tv_utc_day(ts_ms: Optional[int] = None) -> str:
    """Retourne le jour calendaire UTC `YYYY-MM-DD` pour un timestamp epoch ms."""
    import datetime as dt

    ts_val = _now_ms() if ts_ms is None else ts_ms
    return dt.datetime.fromtimestamp(ts_val / 1000.0, tz=dt.timezone.utc).strftime("%Y-%m-%d")


class TradingViewIndicatorStore:
    """Corpus SQLite + index FTS5 local (zéro ré-exécution réseau sur versions immuables)."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        db_str = str(db_path)
        if db_str != ":memory:":
            Path(db_str).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(db_str)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode = WAL;")
        self.db.execute("PRAGMA busy_timeout = 5000;")
        self.db.executescript(_CORPUS_SCHEMA)
        self.db.commit()

    def close(self) -> None:
        try:
            self.db.close()
        except Exception:
            pass

    @staticmethod
    def _row_to_dict(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
        return dict(row) if row is not None else None

    def upsert_script(self, s: Dict[str, Any], now: Optional[int] = None) -> None:
        ts = _now_ms() if now is None else now
        self.db.execute(
            """
            INSERT INTO scripts (
              script_id_part, script_id, name, author, author_id, script_type,
              script_access, open_source, version, likes, comments, views,
              created_at, updated_at, chart_url, image_url, symbol, interval,
              is_picked, is_hot, description, fetched_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(script_id_part) DO UPDATE SET
              script_id=excluded.script_id, name=excluded.name, author=excluded.author,
              author_id=excluded.author_id, script_type=excluded.script_type,
              script_access=excluded.script_access, open_source=excluded.open_source,
              version=excluded.version, likes=excluded.likes, comments=excluded.comments,
              views=excluded.views, created_at=excluded.created_at,
              updated_at=excluded.updated_at, chart_url=excluded.chart_url,
              image_url=excluded.image_url, symbol=excluded.symbol,
              interval=excluded.interval, is_picked=excluded.is_picked,
              is_hot=excluded.is_hot, description=excluded.description,
              fetched_at=excluded.fetched_at
            """,
            (
                s["script_id_part"],
                s.get("script_id"),
                s.get("name"),
                s.get("author"),
                s.get("author_id"),
                s.get("script_type"),
                s.get("script_access"),
                1 if s.get("open_source") else 0,
                s.get("version"),
                _nullish(s.get("likes"), 0),
                _nullish(s.get("comments"), 0),
                _nullish(s.get("views"), 0),
                s.get("created_at"),
                s.get("updated_at"),
                s.get("chart_url"),
                s.get("image_url"),
                s.get("symbol"),
                s.get("interval"),
                1 if s.get("is_picked") else 0,
                1 if s.get("is_hot") else 0,
                s.get("description"),
                ts,
            ),
        )
        self._reindex(s["script_id_part"])
        self.db.commit()

    def upsert_scripts(self, items: Sequence[Dict[str, Any]], now: Optional[int] = None) -> int:
        ts = _now_ms() if now is None else now
        for item in items:
            self.upsert_script(item, ts)
        return len(items)

    def get_script(self, script_id_part: str) -> Optional[Dict[str, Any]]:
        row = self.db.execute("SELECT * FROM scripts WHERE script_id_part = ?", (script_id_part,)).fetchone()
        return self._row_to_dict(row)

    def mark_protected(self, script_id_part: str, now: Optional[int] = None) -> None:
        ts = _now_ms() if now is None else now
        self.db.execute(
            """
            INSERT INTO scripts (script_id_part, open_source, script_access, fetched_at)
            VALUES (?, 0, 2, ?)
            ON CONFLICT(script_id_part) DO UPDATE SET open_source = 0, script_access = 2
            """,
            (script_id_part, ts),
        )
        self.db.commit()

    def put_source(self, rec: Dict[str, Any], now: Optional[int] = None) -> None:
        ts = _now_ms() if now is None else now
        self.db.execute(
            """
            INSERT INTO sources (script_id_part, version, source, pine_version, kind, script_name, fetched_at)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(script_id_part, version) DO UPDATE SET
              source=excluded.source, pine_version=excluded.pine_version,
              kind=excluded.kind, script_name=excluded.script_name,
              fetched_at=excluded.fetched_at
            """,
            (
                rec["script_id_part"],
                str(rec["version"]),
                rec["source"],
                rec.get("pine_version"),
                rec.get("kind"),
                rec.get("script_name"),
                ts,
            ),
        )
        self._reindex(rec["script_id_part"])
        self.db.commit()

    def get_source(self, script_id_part: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if version is None or version == "last":
            row = self.db.execute(
                "SELECT * FROM sources WHERE script_id_part = ? ORDER BY fetched_at DESC LIMIT 1",
                (script_id_part,),
            ).fetchone()
        else:
            row = self.db.execute(
                "SELECT * FROM sources WHERE script_id_part = ? AND version = ?",
                (script_id_part, str(version)),
            ).fetchone()
        return self._row_to_dict(row)

    def has_source(self, script_id_part: str) -> bool:
        row = self.db.execute("SELECT 1 AS ok FROM sources WHERE script_id_part = ? LIMIT 1", (script_id_part,)).fetchone()
        return row is not None

    def _reindex(self, script_id_part: str) -> None:
        s = self.get_script(script_id_part)
        src = self.get_source(script_id_part)
        if not s and not src:
            return
        self.db.execute("DELETE FROM corpus_fts WHERE script_id_part = ?", (script_id_part,))
        name = _nullish(s.get("name") if s else None, _nullish(src.get("script_name") if src else None, ""))
        author = _nullish(s.get("author") if s else None, "")
        description = _nullish(s.get("description") if s else None, "")
        source_txt = _nullish(src.get("source") if src else None, "")
        self.db.execute(
            "INSERT INTO corpus_fts (script_id_part, name, author, description, source) VALUES (?,?,?,?,?)",
            (script_id_part, name, author, description, source_txt),
        )

    def get_cached_search(self, cache_key: str, ttl_ms: int, now: Optional[int] = None) -> Optional[Dict[str, Any]]:
        ts = _now_ms() if now is None else now
        row = self.db.execute("SELECT * FROM searches WHERE cache_key = ?", (cache_key,)).fetchone()
        if row is None:
            return None
        d = dict(row)
        if ts - d["fetched_at"] > ttl_ms:
            return None
        d["payload"] = json.loads(d["payload"])
        return d

    def put_cached_search(
        self, cache_key: str, kind: str, params: Dict[str, Any], result: Dict[str, Any], now: Optional[int] = None
    ) -> None:
        ts = _now_ms() if now is None else now
        self.db.execute(
            """
            INSERT INTO searches (cache_key, kind, params, total, has_more, payload, fetched_at)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(cache_key) DO UPDATE SET
              total=excluded.total, has_more=excluded.has_more,
              payload=excluded.payload, fetched_at=excluded.fetched_at
            """,
            (
                cache_key,
                kind,
                json.dumps(params, ensure_ascii=False, separators=(",", ":")),
                _nullish(result.get("total"), 0),
                1 if result.get("has_more") else 0,
                json.dumps(result, ensure_ascii=False, separators=(",", ":")),
                ts,
            ),
        )
        self.db.commit()

    def create_harvest(self, harvest_id: str, spec: Dict[str, Any], now: Optional[int] = None) -> Dict[str, Any]:
        ts = _now_ms() if now is None else now
        self.db.execute(
            """
            INSERT INTO harvests (id, spec, status, cursor, scripts_seen, sources_stored, started_at, updated_at)
            VALUES (?,?,?,?,0,0,?,?)
            """,
            (
                harvest_id,
                json.dumps(spec, ensure_ascii=False, separators=(",", ":")),
                "running",
                json.dumps({"page": 1, "pending": []}, separators=(",", ":")),
                ts,
                ts,
            ),
        )
        self.db.commit()
        res = self.get_harvest(harvest_id)
        assert res is not None
        return res

    def get_harvest(self, harvest_id: str) -> Optional[Dict[str, Any]]:
        row = self.db.execute("SELECT * FROM harvests WHERE id = ?", (harvest_id,)).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["spec"] = json.loads(d["spec"])
        d["cursor"] = json.loads(d["cursor"])
        return d

    def update_harvest(self, harvest_id: str, patch: Dict[str, Any], now: Optional[int] = None) -> Dict[str, Any]:
        ts = _now_ms() if now is None else now
        cur = self.get_harvest(harvest_id)
        if cur is None:
            raise ValueError(f"Unknown harvest_id: {harvest_id}")
        nxt = {**cur, **patch}
        self.db.execute(
            """
            UPDATE harvests SET status=?, cursor=?, scripts_seen=?, sources_stored=?, updated_at=?, note=?
            WHERE id=?
            """,
            (
                nxt["status"],
                json.dumps(nxt["cursor"], ensure_ascii=False, separators=(",", ":")),
                nxt["scripts_seen"],
                nxt["sources_stored"],
                ts,
                nxt.get("note"),
                harvest_id,
            ),
        )
        self.db.commit()
        res = self.get_harvest(harvest_id)
        assert res is not None
        return res

    def log_request(
        self,
        *,
        host: str,
        path: str,
        status: Optional[int] = None,
        ms: Optional[int] = None,
        outcome: Optional[str] = None,
        now: Optional[int] = None,
    ) -> None:
        ts = _now_ms() if now is None else now
        self.db.execute(
            "INSERT INTO request_log (ts, day, host, path, status, ms, outcome) VALUES (?,?,?,?,?,?,?)",
            (ts, tv_utc_day(ts), host, path, status, ms, outcome),
        )
        self.db.commit()

    def count_requests_today(self, now: Optional[int] = None) -> int:
        ts = _now_ms() if now is None else now
        row = self.db.execute("SELECT COUNT(*) AS n FROM request_log WHERE day = ?", (tv_utc_day(ts),)).fetchone()
        return int(row["n"]) if row is not None else 0

    def get_cookie_jar(self, host: str, max_age_ms: int, now: Optional[int] = None) -> Optional[str]:
        ts = _now_ms() if now is None else now
        row = self.db.execute("SELECT * FROM cookies WHERE host = ?", (host,)).fetchone()
        if row is None:
            return None
        if ts - row["updated_at"] > max_age_ms:
            return None
        return row["jar"]

    def put_cookie_jar(self, host: str, jar: str, now: Optional[int] = None) -> None:
        ts = _now_ms() if now is None else now
        self.db.execute(
            """
            INSERT INTO cookies (host, jar, updated_at) VALUES (?,?,?)
            ON CONFLICT(host) DO UPDATE SET jar=excluded.jar, updated_at=excluded.updated_at
            """,
            (host, jar, ts),
        )
        self.db.commit()

    def query_corpus(
        self,
        *,
        query: Optional[str] = None,
        source_contains: Optional[str] = None,
        script_type: Optional[str] = None,
        author: Optional[str] = None,
        with_source_only: bool = False,
        min_likes: int = 0,
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        where: List[str] = []
        args: List[Any] = []
        from_clause = "FROM scripts s LEFT JOIN sources src ON src.script_id_part = s.script_id_part"

        if query:
            from_clause += " JOIN corpus_fts ON corpus_fts.script_id_part = s.script_id_part"
            where.append("corpus_fts MATCH ?")
            args.append(query)
        if source_contains:
            where.append("src.source LIKE ?")
            args.append(f"%{source_contains}%")
        if script_type and script_type != "all":
            where.append("s.script_type = ?")
            args.append(script_type)
        if author:
            where.append("LOWER(s.author) = LOWER(?)")
            args.append(author)
        if with_source_only:
            where.append("src.source IS NOT NULL")
        if min_likes > 0:
            where.append("s.likes >= ?")
            args.append(min_likes)

        sql = (
            "SELECT s.*, (src.source IS NOT NULL) AS has_source, LENGTH(src.source) AS source_chars, "
            "src.pine_version AS pine_version "
            + from_clause
            + (f" WHERE {' AND '.join(where)}" if where else "")
            + " ORDER BY s.likes DESC LIMIT ?"
        )
        args.append(limit)
        return [dict(r) for r in self.db.execute(sql, tuple(args)).fetchall()]

    def stats(self, now: Optional[int] = None) -> Dict[str, int]:
        def _count(sql: str) -> int:
            row = self.db.execute(sql).fetchone()
            return int(row["n"]) if row is not None else 0

        return {
            "scripts": _count("SELECT COUNT(*) AS n FROM scripts"),
            "sources": _count("SELECT COUNT(*) AS n FROM sources"),
            "authors": _count("SELECT COUNT(DISTINCT author) AS n FROM scripts"),
            "requests_today": self.count_requests_today(now),
            "requests_total": _count("SELECT COUNT(*) AS n FROM request_log"),
        }


# ===========================================================================
# 3. Pacing séquentiel, Coupe-circuit & Budget quotidien (src/throttle.js)
# ===========================================================================


class CircuitOpenError(RuntimeError):
    def __init__(self, ms_until_reset: int) -> None:
        mins = math.ceil(ms_until_reset / 60000)
        super().__init__(
            "TradingView rate-limit circuit is OPEN. Blocked repeatedly, so all requests are "
            f"paused for another ~{mins} min to avoid an IP ban. Use query_corpus to work "
            "offline against already-cached scripts in the meantime."
        )
        self.retry_after_ms = ms_until_reset


class BudgetExceededError(RuntimeError):
    def __init__(self, budget: int) -> None:
        super().__init__(
            f"Daily request budget of {budget} reached. This is a safety cap against runaway "
            "loops. It resets at 00:00 UTC, or raise IF_DAILY_BUDGET if you genuinely need more."
        )


class TradingViewThrottle:
    """Port 1:1 du limiteur séquentiel + coupe-circuit 429/403 + budget UTC."""

    def __init__(
        self,
        config: Dict[str, Any],
        *,
        now: Optional[Callable[[], int]] = None,
        sleep: Optional[Callable[[int], None]] = None,
        random_fn: Optional[Callable[[], float]] = None,
        count_today: Optional[Callable[[], int]] = None,
    ) -> None:
        import random

        self.config = dict(config)
        self.now = now or _now_ms
        self.sleep = sleep or (lambda ms: time.sleep(max(0.0, ms / 1000.0)))
        self.random_fn = random_fn or random.random
        self.count_today = count_today or (lambda: 0)
        self._has_run = False
        self._last_request_at = 0
        self._since_break = 0
        self._consecutive_blocks = 0
        self._open_until = 0
        self._served = 0

    @property
    def is_open(self) -> bool:
        return self.now() < self._open_until

    def run(self, fn: Callable[[], Any]) -> Any:
        if self.is_open:
            raise CircuitOpenError(self._open_until - self.now())
        if self.count_today() >= self.config["dailyBudget"]:
            raise BudgetExceededError(self.config["dailyBudget"])
        self._wait_turn()
        return fn()

    def _wait_turn(self) -> None:
        gap = self._jitter(self.config["minDelayMs"], self.config["maxDelayMs"])
        elapsed = self.now() - self._last_request_at
        if self._has_run and elapsed < gap:
            self.sleep(gap - elapsed)

        if self.config["breakEvery"] > 0 and self._since_break >= self.config["breakEvery"]:
            self._since_break = 0
            self.sleep(self._jitter(self.config["breakMinMs"], self.config["breakMaxMs"]))

        self._since_break += 1
        self._served += 1
        self._has_run = True
        self._last_request_at = self.now()

    def _jitter(self, min_ms: int, max_ms: int) -> int:
        if max_ms <= min_ms:
            return min_ms
        return int(math.floor(min_ms + self.random_fn() * (max_ms - min_ms) + 0.5))

    def note_blocked(self) -> bool:
        self._consecutive_blocks += 1
        if self._consecutive_blocks >= self.config["breakerThreshold"]:
            self._open_until = self.now() + self.config["breakerCooldownMs"]
            self._consecutive_blocks = 0
            return True
        return False

    def note_ok(self) -> None:
        self._consecutive_blocks = 0

    def status(self) -> Dict[str, Any]:
        return {
            "circuit_open": self.is_open,
            "circuit_reopens_in_ms": (self._open_until - self.now()) if self.is_open else 0,
            "consecutive_blocks": self._consecutive_blocks,
            "requests_this_process": self._served,
            "requests_today": self.count_today(),
            "daily_budget": self.config["dailyBudget"],
            "requests_until_break": max(0, self.config["breakEvery"] - self._since_break),
        }


# ===========================================================================
# 4. Endpoints TradingView & Outils MCP (src/tradingview.js + src/tools.js)
# ===========================================================================


class TradingViewHttpError(RuntimeError):
    def __init__(self, status: int, url: str, body: Any = "") -> None:
        super().__init__(f"HTTP {status} for {url}")
        self.status = status
        self.url = url
        self.body = body


def tv_normalize_script_type(script_type: Any) -> Optional[str]:
    if not script_type:
        return None
    return _SCRIPT_TYPE_MAP.get(str(script_type).lower())


class TradingViewClient:
    """Couche endpoints TradingView : URLs, cache TTL et normalisation."""

    def __init__(self, *, config: Dict[str, Any], http: Any, store: Optional[TradingViewIndicatorStore]) -> None:
        self.config = config
        self.http = http
        self.store = store

    def search_scripts(
        self,
        *,
        query: Optional[str] = None,
        script_type: Optional[str] = None,
        sort: Optional[str] = None,
        page: int = 1,
    ) -> Dict[str, Any]:
        slug = tv_slugify(query) if query else None
        if query and not slug:
            raise ValueError(f'Query "{query}" does not produce a usable topic slug.')
        return self._slug_feed(
            segment=slug,
            page=page,
            script_type=script_type,
            sort=sort,
            kind="search",
            label=slug if slug is not None else "top",
        )

    def editors_picks(
        self, *, script_type: Optional[str] = None, sort: Optional[str] = None, page: int = 1
    ) -> Dict[str, Any]:
        return self._slug_feed(
            segment="editors-picks",
            page=page,
            script_type=script_type,
            sort=sort,
            kind="editors_picks",
            label="editors-picks",
        )

    def _slug_feed(
        self,
        *,
        segment: Optional[str],
        page: int,
        script_type: Optional[str],
        sort: Optional[str],
        kind: str,
        label: str,
    ) -> Dict[str, Any]:
        norm_type = tv_normalize_script_type(script_type)
        if script_type and not norm_type:
            raise ValueError(
                f'Unknown script_type "{script_type}". Use indicators, strategies, libraries or all.'
            )

        parts = ["/scripts"]
        if segment:
            parts.append(segment)
        if page and page > 1:
            parts.append(f"page-{page}")
        pathname = f"{'/'.join(parts)}/"

        params: List[tuple[str, str]] = [("component-data-only", "1")]
        if norm_type:
            params.append(("script_type", norm_type))
        if sort:
            params.append(("sort", sort))
        params.append(("script_access", "open"))

        qs = urlencode(params)
        url = f"{TV_ORIGIN}{pathname}?{qs}"
        cache_key = f"{kind}:{pathname}?{qs}"
        cached = self.store.get_cached_search(cache_key, self.config["listingTtlMs"]) if self.store else None
        if cached:
            return {**cached["payload"], "from_cache": True}

        referer_path = f"/scripts/{segment}/" if segment else "/scripts/"
        try:
            raw_json = self.http.get_json(url, referer=f"{TV_ORIGIN}{referer_path}")
        except TradingViewHttpError as err:
            if err.status == 404:
                raise ValueError(
                    f'No TradingView topic page for "{label}". Topic slugs are hyphenated single '
                    'concepts, for example "trend-following", "scalping", "order-blocks". '
                    "Try a broader or differently worded topic."
                ) from err
            raise

        parsed = tv_parse_slug_feed(raw_json)
        res = self._finalise(parsed, {"page": page, "kind": kind, "label": label, "type": norm_type, "sort": sort})
        if self.store:
            self.store.put_cached_search(cache_key, kind, {"page": page, "type": norm_type, "sort": sort, "label": label}, res)
        return res

    def author_scripts(
        self, *, username: str, query: str = "", page: int = 1, per_page: int = 24
    ) -> Dict[str, Any]:
        if not username:
            raise ValueError("username is required")
        clamped = min(max(per_page, 1), 24)
        qs = urlencode(
            [
                ("page", str(page)),
                ("per_page", str(clamped)),
                ("by", username),
                ("q", "" if query is None else query),
            ]
        )
        url = f"{TV_ORIGIN}/api/v1/scripts/?{qs}"
        cache_key = f"author:{qs}"
        cached = self.store.get_cached_search(cache_key, self.config["listingTtlMs"]) if self.store else None
        if cached:
            return {**cached["payload"], "from_cache": True}

        try:
            raw_json = self.http.get_json(url, referer=f"{TV_ORIGIN}/u/{quote(username, safe='')}/")
        except TradingViewHttpError as err:
            if err.status in (400, 404):
                raise ValueError(
                    f'TradingView rejected the username "{username}". Usernames are case-insensitive '
                    'but must match exactly otherwise, for example "TraderlifestyleYT".'
                ) from err
            raise

        parsed = tv_parse_author_feed(raw_json)
        res = self._finalise(parsed, {"page": page, "kind": "author", "label": username})
        if self.store:
            self.store.put_cached_search(cache_key, "author", {"username": username, "query": query, "page": page}, res)
        return res

    def _finalise(self, parsed: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
        open_items = [i for i in parsed["items"] if i["script_access"] == ACCESS_OPEN]
        filtered = len(parsed["items"]) - len(open_items)
        if self.store:
            self.store.upsert_scripts(open_items)
        return {
            **meta,
            "total": parsed["total"],
            "returned": len(open_items),
            "filtered_protected": filtered,
            "has_more": parsed["has_more"],
            "heading": _nullish(parsed.get("heading"), None),
            "items": open_items,
            "from_cache": False,
        }

    def get_source(
        self, *, script_id_part: str, version: str = "last", force: bool = False
    ) -> Dict[str, Any]:
        if not script_id_part:
            raise ValueError("script_id_part is required")
        if not _SCRIPT_ID_PART_RE.match(script_id_part):
            raise ValueError(
                f'"{script_id_part}" is not a script_id_part. Expected the form "PUB;<hash>", which '
                "every search result carries. A chart URL alone is not enough: pass chart_url "
                "instead and it will be resolved."
            )

        if not force and self.store:
            hit = self.store.get_source(script_id_part, version)
            if hit:
                src_txt = hit.get("source")
                return {
                    "ok": True,
                    "from_cache": True,
                    "script_id_part": script_id_part,
                    "version": hit["version"],
                    "script_name": hit.get("script_name"),
                    "kind": hit.get("kind"),
                    "pine_version": hit.get("pine_version"),
                    "source": src_txt,
                    "source_chars": len(src_txt) if src_txt is not None else 0,
                }

        known = self.store.get_script(script_id_part) if self.store else None
        if known and known.get("open_source") == 0:
            return {
                "ok": False,
                "protected": True,
                "script_id_part": script_id_part,
                "reason": (
                    "Script is closed source (invite-only or protected). TradingView never exposes "
                    "its Pine code, so this cannot be retrieved and will not be retried."
                ),
            }

        url = f"{FACADE_ORIGIN}/pine-facade/get/{quote(script_id_part, safe='')}/{quote(str(version), safe='')}?no_4xx=true"
        try:
            raw_json = self.http.get_json(
                url,
                origin=TV_ORIGIN,
                referer=f"{TV_ORIGIN}/",
                same_site="same-site",
                xhr=False,
            )
        except TradingViewHttpError as err:
            if err.status in (401, 403):
                if self.store:
                    self.store.mark_protected(script_id_part)
                return {
                    "ok": False,
                    "protected": True,
                    "script_id_part": script_id_part,
                    "reason": "TradingView refused the source (closed source or invite-only).",
                }
            if err.status == 404:
                raise ValueError(
                    f'No script found for {script_id_part} at version "{version}". Try version "last".'
                ) from err
            raise

        parsed = tv_parse_facade(raw_json, script_id_part=script_id_part)
        if not parsed["ok"]:
            if self.store:
                self.store.mark_protected(script_id_part)
            return {**parsed, "from_cache": False}

        if self.store:
            self.store.put_source(
                {
                    "script_id_part": script_id_part,
                    "version": parsed["version"] if parsed.get("version") is not None else version,
                    "source": parsed["source"],
                    "pine_version": parsed.get("pine_version"),
                    "kind": parsed.get("kind"),
                    "script_name": parsed.get("script_name"),
                }
            )
        return {**parsed, "from_cache": False}


def create_tradingview_tools(
    *,
    config: Dict[str, Any],
    tv: TradingViewClient,
    store: TradingViewIndicatorStore,
    throttle: TradingViewThrottle,
    http: Any,
    now_ms: Optional[Callable[[], int]] = None,
) -> Dict[str, Callable[..., Dict[str, Any]]]:
    """Construit la table complète des 7 outils MCP TradingView en lecture seule."""
    clock = now_ms or _now_ms

    def _listing(items: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [tv_to_listing(it, config["snippetChars"]) for it in items]

    def _resolve_chart_url(chart_url: str) -> str:
        slug = tv_extract_id_from_chart_url(chart_url)
        if not slug:
            raise ValueError(
                f'Could not read a script id from "{chart_url}". Expected something like '
                "https://www.tradingview.com/script/K0SEi3Ct-Some-Name/"
            )
        row = store.db.execute(
            "SELECT script_id_part FROM scripts WHERE chart_url LIKE ? LIMIT 1",
            (f"%/script/{slug}%",),
        ).fetchone()
        if row and row["script_id_part"]:
            return row["script_id_part"]

        html = http.get_text(f"{TV_ORIGIN}/script/{slug}/")
        matches = [m.group(0) for m in _PUB_ID_RE.finditer(str(html))]
        pub = next((m for m in matches if m.startswith("PUB;")), matches[0] if matches else None)
        if not pub:
            raise ValueError(f"Could not resolve {chart_url} to a script_id_part.")
        return pub

    def search_scripts(
        *,
        query: Optional[str] = None,
        script_type: Optional[str] = None,
        sort: Optional[str] = None,
        page: int = 1,
    ) -> Dict[str, Any]:
        res = tv.search_scripts(query=query, script_type=script_type, sort=sort, page=page)
        out: Dict[str, Any] = {
            "query": query if query is not None else None,
            "topic": res["label"],
            "page": page,
            "total_available": res["total"],
            "returned": res["returned"],
            "has_more": res["has_more"],
            "from_cache": res["from_cache"],
        }
        if res["total"] >= 1000:
            out["note"] = "TradingView caps broad result counts at 1000. Narrow the topic for real coverage."
        out["items"] = _listing(res["items"])
        return out

    def list_editors_picks(
        *, script_type: Optional[str] = None, sort: Optional[str] = None, page: int = 1
    ) -> Dict[str, Any]:
        res = tv.editors_picks(script_type=script_type, sort=sort, page=page)
        return {
            "feed": "editors-picks",
            "page": page,
            "total_available": res["total"],
            "returned": res["returned"],
            "has_more": res["has_more"],
            "from_cache": res["from_cache"],
            "items": _listing(res["items"]),
        }

    def list_author_scripts(*, username: str, query: str = "", page: int = 1) -> Dict[str, Any]:
        res = tv.author_scripts(username=username, query=query, page=page)
        return {
            "author": username,
            "page": page,
            "total_available": res["total"],
            "returned": res["returned"],
            "filtered_protected": res["filtered_protected"],
            "has_more": res["has_more"],
            "from_cache": res["from_cache"],
            "items": _listing(res["items"]),
        }

    def get_script_source(
        *,
        script_id_part: Optional[str] = None,
        chart_url: Optional[str] = None,
        version: str = "last",
        force: bool = False,
    ) -> Dict[str, Any]:
        sid = script_id_part
        if not sid and chart_url:
            sid = _resolve_chart_url(chart_url)
        if not sid:
            raise ValueError("Provide either script_id_part or chart_url.")

        res = tv.get_source(script_id_part=sid, version=version, force=force)
        if not res["ok"]:
            return res

        meta = store.get_script(sid)
        src_txt = res.get("source")
        return {
            "ok": True,
            "script_id_part": sid,
            "name": _nullish(res.get("script_name"), meta.get("name") if meta else None),
            "author": meta.get("author") if meta else None,
            "script_type": _nullish(res.get("script_type"), meta.get("script_type") if meta else None),
            "version": res.get("version"),
            "pine_version": res.get("pine_version"),
            "source_chars": _nullish(res.get("source_chars"), len(src_txt) if src_txt is not None else 0),
            "from_cache": res.get("from_cache"),
            "chart_url": meta.get("chart_url") if meta else None,
            "source": src_txt,
        }

    def harvest_scripts(
        *,
        source: str = "search",
        query: Optional[str] = None,
        username: Optional[str] = None,
        script_type: Optional[str] = None,
        sort: Optional[str] = None,
        max_scripts: int = 100,
        fetch_sources: bool = True,
        time_budget_ms: Optional[int] = None,
        harvest_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        budget = time_budget_ms if time_budget_ms is not None else config["harvestTimeBudgetMs"]
        deadline = clock() + budget
        cap = min(max_scripts, config["harvestMaxScripts"])

        if harvest_id:
            harvest = store.get_harvest(harvest_id)
            if not harvest:
                raise ValueError(f"Unknown harvest_id: {harvest_id}")
            if harvest["status"] == "complete":
                return {
                    "harvest_id": harvest_id,
                    "status": "complete",
                    "note": "Already finished.",
                    "scripts_seen": harvest["scripts_seen"],
                    "sources_stored": harvest["sources_stored"],
                }
        else:
            if source == "author" and not username:
                raise ValueError('source="author" requires a username.')
            spec_init = {
                "source": source,
                "query": query,
                "username": username,
                "script_type": script_type,
                "sort": sort,
                "cap": cap,
                "fetch_sources": fetch_sources,
            }
            harvest = store.create_harvest(uuid.uuid4().hex[:8], spec_init)

        spec = harvest["spec"]
        cursor = harvest["cursor"]
        cursor.setdefault("page", 1)
        cursor.setdefault("seen", [])
        cursor.setdefault("pending", [])
        cursor.setdefault("done_listing", False)

        scripts_seen = _nullish(harvest.get("scripts_seen"), 0)
        sources_stored = _nullish(harvest.get("sources_stored"), 0)
        listing_errors = 0

        while clock() < deadline:
            if not cursor["done_listing"] and len(cursor["seen"]) < spec["cap"]:
                try:
                    if spec["source"] == "author":
                        res = tv.author_scripts(username=spec["username"], page=cursor["page"])
                    elif spec["source"] == "editors_picks":
                        res = tv.editors_picks(
                            script_type=spec.get("script_type"), sort=spec.get("sort"), page=cursor["page"]
                        )
                    else:
                        res = tv.search_scripts(
                            query=spec.get("query"),
                            script_type=spec.get("script_type"),
                            sort=spec.get("sort"),
                            page=cursor["page"],
                        )
                except Exception as err:
                    listing_errors += 1
                    cursor["done_listing"] = True
                    store.update_harvest(
                        harvest["id"],
                        {
                            "cursor": cursor,
                            "scripts_seen": scripts_seen,
                            "sources_stored": sources_stored,
                            "status": "paused",
                            "note": f"Listing stopped: {err}",
                        },
                    )
                    raise

                for item in res["items"]:
                    if len(cursor["seen"]) >= spec["cap"]:
                        break
                    sid = item["script_id_part"]
                    if sid in cursor["seen"]:
                        continue
                    cursor["seen"].append(sid)
                    if spec["fetch_sources"] and not store.has_source(sid):
                        cursor["pending"].append(sid)
                scripts_seen = len(cursor["seen"])
                cursor["page"] += 1
                if not res["has_more"] or len(cursor["seen"]) >= spec["cap"]:
                    cursor["done_listing"] = True

                store.update_harvest(
                    harvest["id"],
                    {
                        "cursor": cursor,
                        "scripts_seen": scripts_seen,
                        "sources_stored": sources_stored,
                        "status": "running",
                    },
                )
                continue

            if spec["fetch_sources"] and cursor["pending"]:
                nxt = cursor["pending"].pop(0)
                try:
                    got = tv.get_source(script_id_part=nxt)
                    if got.get("ok"):
                        sources_stored += 1
                except Exception as err:
                    store.update_harvest(
                        harvest["id"],
                        {
                            "cursor": cursor,
                            "scripts_seen": scripts_seen,
                            "sources_stored": sources_stored,
                            "status": "paused",
                            "note": f"Source fetch stopped: {err}",
                        },
                    )
                    raise

                store.update_harvest(
                    harvest["id"],
                    {
                        "cursor": cursor,
                        "scripts_seen": scripts_seen,
                        "sources_stored": sources_stored,
                        "status": "running",
                    },
                )
                continue

            break

        complete = bool(cursor["done_listing"] and (not spec["fetch_sources"] or len(cursor["pending"]) == 0))
        saved = store.update_harvest(
            harvest["id"],
            {
                "cursor": cursor,
                "scripts_seen": scripts_seen,
                "sources_stored": sources_stored,
                "status": "complete" if complete else "paused",
            },
        )
        preview = [
            {
                "script_id_part": r["script_id_part"],
                "name": r["name"],
                "author": r["author"],
                "script_type": r["script_type"],
                "likes": r["likes"],
                "has_source": bool(r["has_source"]),
            }
            for r in store.query_corpus(limit=20)
            if r["script_id_part"] in cursor["seen"]
        ]
        hid = saved["id"]
        next_step = (
            "Done. Use query_corpus to search everything collected, offline."
            if saved["status"] == "complete"
            else f'Paused on the time budget, not an error. Call harvest_scripts again with harvest_id="{hid}" to continue where it left off.'
        )
        return {
            "harvest_id": hid,
            "status": saved["status"],
            "scripts_seen": scripts_seen,
            "sources_stored": sources_stored,
            "sources_pending": len(cursor["pending"]),
            "listing_errors": listing_errors,
            "next_step": next_step,
            "preview": preview,
        }

    def query_corpus(
        *,
        query: Optional[str] = None,
        source_contains: Optional[str] = None,
        script_type: Optional[str] = None,
        author: Optional[str] = None,
        with_source_only: bool = False,
        min_likes: int = 0,
        limit: int = 25,
        include_source: bool = False,
    ) -> Dict[str, Any]:
        eff_limit = min(limit, 3) if include_source else min(limit, 100)
        rows = store.query_corpus(
            query=query,
            source_contains=source_contains,
            script_type=script_type,
            author=author,
            with_source_only=with_source_only or bool(source_contains),
            min_likes=min_likes,
            limit=eff_limit,
        )
        items_out: List[Dict[str, Any]] = []
        for r in rows:
            desc = r.get("description")
            snip = _js_slice(re.sub(r"\s+", " ", desc), config["snippetChars"]) if desc else ""
            row_obj: Dict[str, Any] = {
                "script_id_part": r["script_id_part"],
                "name": r["name"],
                "author": r["author"],
                "script_type": r["script_type"],
                "likes": r["likes"],
                "symbol": r["symbol"],
                "interval": r["interval"],
                "chart_url": r["chart_url"],
                "pine_version": r["pine_version"],
                "has_source": bool(r["has_source"]),
                "source_chars": _nullish(r.get("source_chars"), 0),
                "description_snippet": snip,
            }
            if include_source and r["has_source"]:
                src_rec = store.get_source(r["script_id_part"])
                row_obj["source"] = src_rec["source"] if src_rec else None
            items_out.append(row_obj)

        return {
            "matched": len(rows),
            "limit_applied": eff_limit,
            "include_source": include_source,
            "note": (
                "include_source caps results at 3 because Pine sources are large."
                if include_source
                else "Set include_source=true (with a small limit) to get full Pine code."
            ),
            "corpus": store.stats(),
            "items": items_out,
        }

    def fetch_status() -> Dict[str, Any]:
        return {
            "throttle": throttle.status(),
            "corpus": store.stats(),
            "pacing": {
                "delay_between_requests_ms": [config["minDelayMs"], config["maxDelayMs"]],
                "long_break_every_n_requests": config["breakEvery"],
                "long_break_ms": [config["breakMinMs"], config["breakMaxMs"]],
                "circuit_breaker_after_consecutive_blocks": config["breakerThreshold"],
                "circuit_cooldown_ms": config["breakerCooldownMs"],
            },
        }

    return {
        "search_scripts": search_scripts,
        "list_editors_picks": list_editors_picks,
        "list_author_scripts": list_author_scripts,
        "get_script_source": get_script_source,
        "harvest_scripts": harvest_scripts,
        "query_corpus": query_corpus,
        "fetch_status": fetch_status,
    }


# ===========================================================================
# 5. Auto-test interne & Reçu R10 mesuré (zéro auto-certification)
# ===========================================================================


def run_trading_copilot_self_test(
    head_sha40: Optional[str] = None,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Vérifie le câblage K5 Trading SQLite/FTS5/Throttle sous veto S0 sans auto-certification."""
    root = repo_root or WORKSPACE_ROOT
    sha = head_sha40 or ("0" * 40)
    if not READ_ONLY_VETO_S0:
        raise ContractViolation("ADR-07", "READ_ONLY_VETO_S0 doit rester True")

    store = TradingViewIndicatorStore(":memory:")
    try:
        store.upsert_script(
            {
                "script_id_part": "PUB;smoke00000000000000000000000001",
                "name": "Supertrend ReadOnly",
                "author": "smoke_author",
                "script_type": "indicator",
                "script_access": ACCESS_OPEN,
                "open_source": True,
                "likes": 10,
                "description": "Smoke read-only indicator",
            }
        )
        store.put_source(
            {
                "script_id_part": "PUB;smoke00000000000000000000000001",
                "version": "1",
                "source": "//@version=5\nindicator('x')\nta.supertrend(3, 10)",
                "pine_version": 5,
            }
        )
        hits = store.query_corpus(source_contains="ta.supertrend")
        assert len(hits) == 1 and tv_detect_pine_version(store.get_source("PUB;smoke00000000000000000000000001")["source"]) == 5
        thr = TradingViewThrottle(DEFAULT_TRADINGVIEW_CONFIG, now=lambda: 0, sleep=lambda _ms: None)
        assert thr.run(lambda: "ok") == "ok" and tv_slugify("Trend Following") == "trend-following"
    finally:
        store.close()

    evt, rec = consign_measured_l0_evidence(
        actor_from="fabricator",
        actor_to="judge",
        dispatch_id="D-TRADING-SMOKE",
        payload="K5 Trading copilot smoke passed (0 source-oracle parities self-claimed)",
        issuer="Kernel K5 (TradingCopilot)",
        mission_prefix="TRADING-SMOKE",
        sha=sha,
        proof=["01_Forkable/FKB07_Money_Maker/01_Trading/aspace_trading_copilot_foundation.py"],
        summary=f"K5 Trading smoke PASS; source_oracle_parity=0 at {sha[:7]}",
        repo_root=root,
    )
    return {
        "organ": "aspace_trading_copilot_foundation",
        "read_only_veto_s0": READ_ONLY_VETO_S0,
        "source_parity_verified": [],
        "l0_seq": evt["seq"],
        "r10_entry_id": rec["entry_id"],
    }


def consign_trading_parity_receipt(
    module_results: Dict[str, Dict[str, Any]],
    head_sha40: str,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Consigne uniquement la parité source-vs-organe réellement mesurée contre l'oracle Node."""
    verified = sorted(
        mid
        for mid, res in module_results.items()
        if res.get("compared_against_source")
        and res.get("cases_compared", 0) > 0
        and res.get("cases_matched") == res.get("cases_compared")
    )
    total_cases = sum(int(res.get("cases_compared", 0)) for res in module_results.values())
    total_matched = sum(int(res.get("cases_matched", 0)) for res in module_results.values())
    evt, rec = consign_measured_l0_evidence(
        actor_from="fabricator",
        actor_to="judge",
        dispatch_id="D-TRADING-PARITY",
        payload=f"K5 Trading differential parity: {verified} ({total_matched}/{total_cases} cases)",
        issuer="Kernel K5 (TradingCopilot)",
        mission_prefix="TRADING-PARITY",
        sha=head_sha40,
        proof=["01_Forkable/FKB07_Money_Maker/01_Trading/aspace_trading_copilot_foundation.py"],
        summary=f"K5 Trading measured parity {total_matched}/{total_cases} across {verified} at {head_sha40[:7]}",
        repo_root=repo_root,
    )
    return {
        "verified_modules": verified,
        "cases_matched": total_matched,
        "cases_compared": total_cases,
        "l0_seq": evt["seq"],
        "r10_entry_id": rec["entry_id"],
    }


if __name__ == "__main__":
    print(json.dumps(run_trading_copilot_self_test(), indent=2, ensure_ascii=False))
