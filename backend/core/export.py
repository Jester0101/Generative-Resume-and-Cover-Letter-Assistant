from __future__ import annotations

import json
import os
import zipfile
from typing import Any, Dict


def export_json(obj: Dict[str, Any], path: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return path


def export_markdown(final_output: Dict[str, Any], out_dir: str) -> Dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)

    bullets = final_output.get("generation", {}).get("resume_bullets", [])
    cover = final_output.get("generation", {}).get("cover_letter", {}).get("text", "")

    resume_md = []
    resume_md.append("# Tailored Resume Bullets\n")
    for b in bullets:
        txt = str(b.get("text", "")).strip()
        if txt:
            resume_md.append(f"- {txt}")
    resume_path = os.path.join(out_dir, "resume.md")
    with open(resume_path, "w", encoding="utf-8") as f:
        f.write("\n".join(resume_md).strip() + "\n")

    cover_md = []
    cover_md.append("# Cover Letter\n")
    cover_md.append(str(cover).strip())
    cover_path = os.path.join(out_dir, "cover_letter.md")
    with open(cover_path, "w", encoding="utf-8") as f:
        f.write("\n".join(cover_md).strip() + "\n")

    return {"resume_md": resume_path, "cover_md": cover_path}


def export_zip(folder: str, zip_path: str) -> str:
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(folder):
            for fn in files:
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, folder)
                z.write(full, arcname=rel)
    return zip_path
