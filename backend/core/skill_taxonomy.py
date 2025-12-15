from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set

import yaml

from .preprocess import normalize_text


@dataclass
class SkillEntry:
    canonical: str
    aliases: Set[str]
    related: Set[str]


class SkillTaxonomy:
    def __init__(self, entries: Dict[str, SkillEntry]):
        self.entries = entries
        self.alias_to_canonical: Dict[str, str] = {}
        for canon, entry in entries.items():
            self.alias_to_canonical[normalize_text(canon)] = canon
            for a in entry.aliases:
                self.alias_to_canonical[normalize_text(a)] = canon

    @classmethod
    def from_yaml(cls, path: str) -> "SkillTaxonomy":
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        entries: Dict[str, SkillEntry] = {}
        for canon, obj in raw.items():
            canon_norm = normalize_text(str(canon))
            aliases = set(normalize_text(x) for x in (obj.get("aliases") or []))
            related = set(normalize_text(x) for x in (obj.get("related") or []))
            entries[canon_norm] = SkillEntry(canonical=canon_norm, aliases=aliases, related=related)
        return cls(entries)

    def canonicalize(self, skill_or_alias: str) -> str | None:
        key = normalize_text(skill_or_alias)
        return self.alias_to_canonical.get(key)

    def is_known_skill(self, skill: str) -> bool:
        key = normalize_text(skill)
        return key in self.entries or key in self.alias_to_canonical

    def all_canonicals(self) -> List[str]:
        return sorted(self.entries.keys())

    def extract_skills(self, text: str) -> Set[str]:
        t = normalize_text(text)
        found: Set[str] = set()
        padded = f" {t} "
        for alias_norm, canon in self.alias_to_canonical.items():
            if not alias_norm:
                continue
            if f" {alias_norm} " in padded:
                found.add(canon)
        return found
