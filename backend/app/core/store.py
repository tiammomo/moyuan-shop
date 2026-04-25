from dataclasses import dataclass, field
from threading import Lock
from typing import Any


@dataclass
class InMemoryStore:
    assets: dict[str, dict[str, Any]] = field(default_factory=dict)
    tasks: dict[str, dict[str, Any]] = field(default_factory=dict)
    results: dict[str, dict[str, Any]] = field(default_factory=dict)
    task_results: dict[str, list[str]] = field(default_factory=dict)
    lock: Lock = field(default_factory=Lock)


store = InMemoryStore()
