#!/usr/bin/env python3
"""A miniature data pipeline framework for demonstrating Python syntax.

This module implements a lightweight ETL (Extract, Transform, Load) pipeline
with pluggable stages, validators, and async batch processing.
"""

from __future__ import annotations

import asyncio
import json
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Generator, TypeVar

# -- Constants ---------------------------------------------------------------

MAX_BATCH_SIZE = 1_000
DEFAULT_TIMEOUT = 30.0
VERSION = "0.4.2"
HEX_MASK = 0xFF
EPSILON = 1e-9
VALID_STATES = frozenset({"pending", "running", "done", "failed"})
_REGISTRY: dict[str, type] = {}


# -- Exceptions --------------------------------------------------------------

class PipelineError(Exception):
    """Base exception for all pipeline failures."""


class ValidationError(PipelineError):
    """Raised when a record fails validation."""

    def __init__(self, field_name: str, value: Any, reason: str = "invalid") -> None:
        self.field_name = field_name
        self.value = value
        super().__init__(f"{field_name}={value!r}: {reason}")


class StageTimeoutError(PipelineError):
    """Raised when a stage exceeds its time budget."""


# -- Decorators --------------------------------------------------------------

T = TypeVar("T")


def register(name: str) -> Callable:
    """Class decorator that registers a stage in the global registry."""
    def decorator(cls: type[T]) -> type[T]:
        _REGISTRY[name] = cls
        return cls
    return decorator


def retry(max_attempts: int = 3, *, backoff: float = 0.1):
    """Retry a function on failure with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    last_error = exc
                    wait = backoff * (2 ** attempt)
                    await asyncio.sleep(wait)
            raise PipelineError("retries exhausted") from last_error
        return wrapper
    return decorator


# -- Data models -------------------------------------------------------------

@dataclass
class Record:
    """A single data record flowing through the pipeline."""
    id: int
    payload: dict[str, Any]
    tags: list[str] = field(default_factory=list)
    timestamp: float = 0.0
    _processed: bool = field(default=False, repr=False)

    @property
    def is_processed(self) -> bool:
        return self._processed

    def mark_done(self) -> None:
        self._processed = True
        self.timestamp = datetime.now().timestamp()

    def __str__(self) -> str:
        status = "done" if self._processed else "pending"
        return f"Record(#{self.id}, {status}, tags={self.tags})"


# -- Abstract base & concrete stages ----------------------------------------

class Stage(ABC):
    """Base class for all pipeline stages."""

    @abstractmethod
    def process(self, record: Record) -> Record | None:
        ...

    @classmethod
    def from_config(cls, config: dict) -> Stage:
        kind = config.get("type", "")
        stage_cls = _REGISTRY.get(kind)
        if stage_cls is None:
            raise ValueError(f"Unknown stage type: {kind!r}")
        return stage_cls(**config.get("params", {}))


@register("filter")
class FilterStage(Stage):
    """Drops records that don't match a pattern."""

    def __init__(self, key: str, pattern: str = r".*") -> None:
        self.key = key
        self._regex = re.compile(pattern)

    def process(self, record: Record) -> Record | None:
        value = record.payload.get(self.key, "")
        if not isinstance(value, str) or not self._regex.search(value):
            return None  # drop
        return record


@register("transform")
class TransformStage(Stage):
    """Applies transformations to record payloads."""

    OPERATIONS = {"upper", "lower", "strip", "title"}

    def __init__(self, operations: list[str] | None = None) -> None:
        self.ops = operations or ["strip"]

    def process(self, record: Record) -> Record:
        for key, val in record.payload.items():
            if not isinstance(val, str):
                continue
            for op in self.ops:
                if op in self.OPERATIONS:
                    val = getattr(val, op)()
            record.payload[key] = val
        return record

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()


# -- Pipeline engine ---------------------------------------------------------

class Pipeline:
    """Orchestrates data flow through a sequence of stages."""

    def __init__(self, name: str = "default") -> None:
        self.name = name
        self._stages: list[Stage] = []
        self._stats: dict[str, int] = defaultdict(int)
        self._hooks: dict[str, list[Callable]] = {}

    def add_stage(self, stage: Stage) -> Pipeline:
        self._stages.append(stage)
        return self  # fluent interface

    def on(self, event: str, callback: Callable) -> None:
        self._hooks.setdefault(event, []).append(callback)

    def _emit(self, event: str, data: Any = None) -> None:
        for hook in self._hooks.get(event, []):
            hook(data)

    def run(self, records: list[Record]) -> Generator[Record, None, None]:
        """Process records through all stages, yielding survivors."""
        self._emit("start", {"count": len(records)})

        for record in records:
            result: Record | None = record
            for stage in self._stages:
                if result is None:
                    break
                result = stage.process(result)

            if result is not None:
                result.mark_done()
                self._stats["passed"] += 1
                yield result
            else:
                self._stats["dropped"] += 1

        self._emit("end", dict(self._stats))

    @retry(max_attempts=3, backoff=0.05)
    async def run_async(self, records: list[Record]) -> list[Record]:
        """Async batch runner with chunked processing."""
        results = []
        # walrus operator + chunked iteration
        offset = 0
        while (chunk := records[offset:offset + MAX_BATCH_SIZE]):
            batch = [r for r in self.run(chunk)]
            results.extend(batch)
            offset += MAX_BATCH_SIZE
            await asyncio.sleep(0)  # yield control
        return results

    def summary(self) -> str:
        total = self._stats["passed"] + self._stats["dropped"]
        pct = (self._stats["passed"] / total * 100) if total > 0 else 0.0
        return f"Pipeline '{self.name}': {self._stats['passed']}/{total} passed ({pct:.1f}%)"


# -- Validators (closures & higher-order functions) --------------------------

def make_validator(rules: dict[str, Callable[[Any], bool]]) -> Callable:
    """Factory that returns a validator closure over the given rules."""
    required_keys = list(rules.keys())

    def validate(record: Record) -> bool:
        nonlocal required_keys
        for key in required_keys:
            value = record.payload.get(key)
            if value is None or not rules[key](value):
                raise ValidationError(key, value)
        return True

    return validate


# -- Utility functions -------------------------------------------------------

def parse_config(raw: str) -> dict[str, Any]:
    """Parse a JSON config string with some escape sequences."""
    # Handle common escapes: tabs, newlines, backslashes
    cleaned = raw.replace("\t", " ").replace("\r\n", "\n")
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise PipelineError(f"Bad config: {exc}") from exc


def describe_records(records: list[Record]) -> str:
    """Build a multiline summary using f-strings and comprehensions."""
    lines = [f"  #{r.id}: {r.payload!r}" for r in records if not r.is_processed]
    header = f"Pending records ({len(lines)}):\n"
    return header + "\n".join(lines) if lines else "All records processed."


def merge_payloads(*records: Record) -> dict[str, Any]:
    """Merge payloads using unpacking, handling duplicates with last-wins."""
    merged: dict[str, Any] = {}
    for rec in records:
        merged = {**merged, **rec.payload}
    return merged


def tag_statistics(records: list[Record]) -> dict[str, int]:
    """Count tag frequencies using a dict comprehension over grouped data."""
    all_tags = [tag for rec in records for tag in rec.tags]
    return {tag: count for tag, count in
            ((t, all_tags.count(t)) for t in set(all_tags))}


# -- Demo / main ------------------------------------------------------------

async def main() -> None:
    """Run a demo pipeline to exercise the framework."""
    # Build sample records
    raw_data = [
        {"name": "  Alice  ", "email": "alice@example.com", "score": 95},
        {"name": "Bob", "email": "bob@test", "score": 42},
        {"name": "  Charlie ", "email": "charlie@example.com", "score": 78},
        {"name": "diana", "email": "skip-this", "score": 110},
    ]

    records = [
        Record(id=i, payload=dict(d), tags=["batch-1" if i < 2 else "batch-2"])
        for i, d in enumerate(raw_data)
    ]

    # Configure pipeline
    pipe = Pipeline(name="demo")
    pipe.add_stage(FilterStage(key="email", pattern=r"@\w+\.\w+"))
    pipe.add_stage(TransformStage(operations=["strip", "title"]))
    pipe.on("end", lambda stats: print(f"  Finished: {stats}"))

    # Validate before processing
    is_valid = make_validator({
        "name": lambda v: isinstance(v, str) and len(v) > 0,
        "score": lambda v: isinstance(v, (int, float)) and 0 <= v <= 100,
    })

    valid_records = []
    for rec in records:
        try:
            is_valid(rec)
            valid_records.append(rec)
        except ValidationError as err:
            print(f"  Skipped record #{rec.id}: {err}")

    # Run async pipeline
    results = await pipe.run_async(valid_records)

    # Print results
    print(f"\n{pipe.summary()}")
    print(describe_records(records))
    print(f"Tag stats: {tag_statistics(records)}")

    # Quick comprehension & ternary demo
    scores = {r.payload.get("name", "?"): r.payload.get("score", 0) for r in results}
    best = max(scores, key=scores.get) if scores else None
    print(f"Top scorer: {best}" if best is not None else "No results")

    # Generator expression for memory-efficient aggregation
    total = sum(r.payload.get("score", 0) for r in results)
    avg = total / len(results) if len(results) > 0 else 0
    print(f"Average score: {avg:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
