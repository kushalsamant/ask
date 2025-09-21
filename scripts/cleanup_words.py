#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {'.py', '.md', '.env', '.csv', '.txt'}
IMAGE_DIR = REPO_ROOT / 'images'

# Banned words (case-insensitive regex)
BANNED_PATTERNS = [
    re.compile(r"?", re.IGNORECASE),
    re.compile(r"ure", re.IGNORECASE),
    re.compile(r"ural", re.IGNORECASE),
]

# Simple normalization: collapse double hyphens repeatedly
NORMALIZE_DASHES = re.compile(r"-+")


def remove_banned_words(text: str) -> str:
    updated = text
    for pat in BANNED_PATTERNS:
        updated = pat.sub('', updated)
    # Normalize multiple dashes
    while NORMALIZE_DASHES.search(updated):
        updated = NORMALIZE_DASHES.sub('-', updated)
    return updated


def iter_text_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for p in root.rglob('*'):
        if p.is_file() and p.suffix.lower() in TEXT_EXTENSIONS:
            files.append(p)
    return files


def update_text_files(files: List[Path]) -> int:
    changed = 0
    for f in files:
        try:
            original = f.read_text(encoding='utf-8')
        except Exception:
            # Skip unreadable files
            continue
        updated = remove_banned_words(original)
        if updated != original:
            f.write_text(updated, encoding='utf-8')
            changed += 1
    return changed


def rename_images_and_collect_mappings(image_dir: Path) -> List[Tuple[str, str]]:
    mappings: List[Tuple[str, str]] = []
    if not image_dir.exists():
        return mappings
    for p in image_dir.rglob('*'):
        if not p.is_file():
            continue
        name_lower = p.name.lower()
        if any(word in name_lower for word in ['ure', '', 'ural']):
            new_name = p.name
            new_name = re.sub(r'ure', '', new_name, flags=re.IGNORECASE)
            new_name = re.sub(r'?', '', new_name, flags=re.IGNORECASE)
            new_name = re.sub(r'ural', '', new_name, flags=re.IGNORECASE)
            while '-' in new_name:
                new_name = new_name.replace('-', '-')
            new_path = p.with_name(new_name)
            if new_path.name != p.name:
                # If destination exists, try to avoid collision by appending a suffix index
                if new_path.exists():
                    stem = new_path.stem
                    suffix = new_path.suffix
                    idx = 1
                    candidate = new_path.with_name(f"{stem}-{idx}{suffix}")
                    while candidate.exists():
                        idx += 1
                        candidate = new_path.with_name(f"{stem}-{idx}{suffix}")
                    new_path = candidate
                p.rename(new_path)
                mappings.append((p.name, new_path.name))
    return mappings


def apply_filename_mappings_in_text(files: List[Path], mappings: List[Tuple[str, str]]) -> int:
    if not mappings:
        return 0
    changed = 0
    for f in files:
        try:
            original = f.read_text(encoding='utf-8')
        except Exception:
            continue
        updated = original
        for old, new in mappings:
            if old in updated:
                updated = updated.replace(old, new)
        if updated != original:
            # Also re-run normalization for any accidental double dashes introduced
            updated = remove_banned_words(updated)
            f.write_text(updated, encoding='utf-8')
            changed += 1
    return changed


def main() -> int:
    print(f"Running cleanup in: {REPO_ROOT}")
    text_files = iter_text_files(REPO_ROOT)

    t1 = update_text_files(text_files)
    print(f"Updated text files (banned word removal): {t1}")

    mappings = rename_images_and_collect_mappings(IMAGE_DIR)
    if mappings:
        print("Renamed images:")
        for old, new in mappings:
            print(f" - {old} -> {new}")
    else:
        print("No images required renaming.")

    t2 = apply_filename_mappings_in_text(text_files, mappings)
    print(f"Updated text files (filename reference updates): {t2}")

    # Final verification summary
    remaining = 0
    check_patterns = [re.compile(r"?", re.IGNORECASE), re.compile(r"ure", re.IGNORECASE), re.compile(r"ural", re.IGNORECASE)]
    for f in text_files:
        try:
            content = f.read_text(encoding='utf-8')
        except Exception:
            continue
        if any(p.search(content) for p in check_patterns):
            remaining += 1
    print(f"Text files still containing banned words: {remaining}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
