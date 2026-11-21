"""DESI Infinity System - Disease Database Connector (v6.2.0).

Abstract connector interface for external biomedical databases (MONDO, HPO,
ClinVar, NCBI Taxonomy, etc.). Provides a local cache, query log, and
explicit "data not available" signalling instead of fabricating results.
Concrete adapters must implement `fetch()`; the base class enforces contract.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)


class ConnectorError(Exception):
    """Base connector error."""


class ConnectorNotConfiguredError(ConnectorError):
    """Raised when no fetch backend is configured."""


class DataNotAvailableError(ConnectorError):
    """Raised when the upstream database has no record for the query."""


@dataclass
class QueryRecord:
    source: str
    query: str
    status: str  # "ok" | "not_found" | "error" | "cached"
    duration_ms: float
    result: Optional[Any] = None
    error: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)


class DiseaseDatabaseConnector:
    """Generic connector with pluggable fetcher and cache."""

    def __init__(self, source_name: str, cache_enabled: bool = True) -> None:
        if not source_name or not isinstance(source_name, str):
            raise ConnectorError("source_name must be a non-empty string")
        self.source_name = source_name
        self.cache_enabled = cache_enabled
        self._fetcher: Optional[Callable[[str], Dict[str, Any]]] = None
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._log: List[QueryRecord] = []

    def configure(self, fetcher: Callable[[str], Dict[str, Any]]) -> None:
        if not callable(fetcher):
            raise ConnectorError("fetcher must be callable")
        self._fetcher = fetcher

    def _run_fetch(self, query: str) -> Dict[str, Any]:
        if self._fetcher is None:
            raise ConnectorNotConfiguredError(
                f"connector {self.source_name!r} has no fetcher configured")
        result = self._fetcher(query)
        if result is None:
            raise DataNotAvailableError(f"no record for {query!r} in {self.source_name}")
        if not isinstance(result, dict):
            raise ConnectorError("fetcher must return a dict")
        return result

    def fetch(self, query: str) -> Dict[str, Any]:
        if not query or not isinstance(query, str):
            raise ConnectorError("query must be a non-empty string")
        start = time.perf_counter()
        if self.cache_enabled and query in self._cache:
            self._log.append(QueryRecord(self.source_name, query, "cached",
                                         (time.perf_counter() - start) * 1000.0,
                                         self._cache[query]))
            return dict(self._cache[query])
        try:
            result = self._run_fetch(query)
            if self.cache_enabled:
                self._cache[query] = result
            self._log.append(QueryRecord(self.source_name, query, "ok",
                                         (time.perf_counter() - start) * 1000.0, result))
            return result
        except DataNotAvailableError:
            self._log.append(QueryRecord(self.source_name, query, "not_found",
                                         (time.perf_counter() - start) * 1000.0))
            raise
        except ConnectorError:
            raise
        except Exception as exc:
            self._log.append(QueryRecord(self.source_name, query, "error",
                                         (time.perf_counter() - start) * 1000.0,
                                         error=str(exc)))
            raise ConnectorError(f"fetch failed for {query!r}: {exc}") from exc

    def clear_cache(self) -> None:
        self._cache.clear()

    def log(self) -> List[QueryRecord]:
        return list(self._log)

    def stats(self) -> Dict[str, Any]:
        statuses: Dict[str, int] = {}
        for rec in self._log:
            statuses[rec.status] = statuses.get(rec.status, 0) + 1
        return {
            "version": VERSION,
            "source": self.source_name,
            "cache_size": len(self._cache),
            "queries": len(self._log),
            "statuses": statuses,
        }


def self_test() -> bool:
    connector = DiseaseDatabaseConnector("mock-db")
    with __import__("contextlib").suppress(ConnectorNotConfiguredError):
        connector.fetch("X")
    connector.configure(lambda q: {"id": q, "name": "mock"} if q != "missing" else None)
    assert connector.fetch("MONDO:0005148")["name"] == "mock"
    connector.fetch("MONDO:0005148")  # cached
    try:
        connector.fetch("missing")
        raise AssertionError("expected DataNotAvailableError")
    except DataNotAvailableError:
        pass
    assert connector.stats()["statuses"].get("cached") == 1
    print("008 disease_database_connector: OK")
    return True


if __name__ == "__main__":
    self_test()
