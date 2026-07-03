from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass(frozen=True)
class DetectorIndex:
    asset_types: set[str] = field(default_factory=set)

    def has_detector(self, asset_type_name: str) -> bool:
        return asset_type_name in self.asset_types


# Detector syntax support is related to the thesis detector language work:
# https://github.com/isakhertin/MasterThesis_DetectorsLang


_ASSET_DECLARATION_RE = re.compile(r"^\s*(?:abstract\s+)?asset\s+([A-Za-z_]\w*)\b")
_DETECTOR_RE = re.compile(r"!\s*[A-Za-z_]\w*\s*\(")


def load_detector_index(lang_file_path: str) -> DetectorIndex:
    if Path(lang_file_path).suffix.lower() != ".mal":
        return DetectorIndex()

    return parse_detector_index_from_mal(
        Path(lang_file_path).read_text(encoding="utf-8")
    )


def parse_detector_index_from_mal(mal_source: str) -> DetectorIndex:
    current_asset_name: str | None = None
    asset_depth = 0
    waiting_for_asset_body = False
    asset_types: set[str] = set()

    for raw_line in mal_source.splitlines():
        line = raw_line.split("//", maxsplit=1)[0]
        if not line.strip():
            continue

        asset_match = _ASSET_DECLARATION_RE.match(line)
        if asset_match is not None:
            current_asset_name = asset_match.group(1)
            asset_depth = 0
            waiting_for_asset_body = True

        if current_asset_name is not None and _DETECTOR_RE.search(line):
            asset_types.add(current_asset_name)

        opened = line.count("{")
        closed = line.count("}")
        if current_asset_name is not None:
            asset_depth += opened - closed
            if waiting_for_asset_body and opened > 0:
                waiting_for_asset_body = False
            if not waiting_for_asset_body and asset_depth <= 0:
                current_asset_name = None
                asset_depth = 0

    return DetectorIndex(asset_types=asset_types)
