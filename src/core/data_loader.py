from __future__ import annotations

import json
import sys

from pathlib import Path
from typing import Any


def get_root() -> Path:

    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parents[2]


def load_json(path: Path | str) -> Any:

    file_path = Path(path)

    if not file_path.is_absolute():
        parts = file_path.parts
        if parts and parts[0] == "data":
            file_path = get_root() / "src" / "resources" / file_path
        else:
            file_path = get_root() / file_path

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)