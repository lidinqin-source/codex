from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


class StepLogger:
    def __init__(self, log_dir: Path, quiet: bool = True, timezone: str = "Asia/Shanghai") -> None:
        self.log_dir = log_dir
        self.quiet = quiet
        self.timezone = timezone
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.events_path = self.log_dir / "runner_events.jsonl"

    def now(self) -> str:
        return datetime.now(ZoneInfo(self.timezone)).isoformat(timespec="seconds")

    def event(self, step: str, status: str, **metadata: Any) -> None:
        payload = {
            "timestamp": self.now(),
            "step": step,
            "status": status,
            "metadata": metadata,
        }
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        if not self.quiet:
            print(f"{step}: {status}")
