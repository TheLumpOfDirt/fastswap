#!/usr/bin/env python3

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# List of anime girl images (objects with source and colors)
ANIME_GIRLS = [
    {"source": "image0.png", "colors": ["#cb7a6b", "#eeeeee", "#cb7a6b"]},
    {"source": "image1.png", "colors": ["#ccc3ff", "#eeeeee", "#ccc3ff"]}
]

def swap_filename(src: str) -> str:
    p = Path(src).expanduser()
    current = p.name
    for idx, entry in enumerate(ANIME_GIRLS):
        if entry.get("source") == current:
            next_entry = ANIME_GIRLS[(idx + 1) % len(ANIME_GIRLS)]
            next_source = next_entry.get("source")
            return str(p.with_name(next_source))
    return src

def find_anime_entry_for_filename(filename: str) -> Dict[str, Any]:
    """Return the ANIME_GIRLS entry matching filename, or None."""
    for entry in ANIME_GIRLS:
        if entry.get("source") == Path(filename).name:
            return entry
    return None

def apply_category_colors(modules: List[Any], colors: List[str]) -> None:
    """
    Apply colors to modules grouped by 'custom' separators.
    Each group between separators receives one color from colors in order.
    Only modules that are dicts and have a 'keyColor' field will be updated.
    """
    if not colors:
        return

    # Find indices of separator modules (type == "custom")
    sep_indices = [i for i, m in enumerate(modules) if isinstance(m, dict) and m.get("type") == "custom"]

    # If there are no separators, treat the whole modules list as a single category
    if not sep_indices:
        groups = [(0, len(modules))]
    else:
        groups = []
        # For each separator, the category starts at the separator index + 1
        for i, sep_idx in enumerate(sep_indices):
            start = sep_idx + 1
            # end is next separator index, or end of modules
            end = sep_indices[i + 1] if i + 1 < len(sep_indices) else len(modules)
            groups.append((start, end))

    # Apply colors to groups in order; if fewer colors than groups, cycle colors
    for i, (start, end) in enumerate(groups):
        color = colors[i % len(colors)]
        for j in range(start, end):
            mod = modules[j]
            if isinstance(mod, dict) and "keyColor" in mod:
                mod["keyColor"] = color

def main():
    cfg = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("config.jsonc")
    if not cfg.exists():
        print(f"Config file not found: {cfg}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Rotate logo filename if present
    logo = data.get("logo")
    if isinstance(logo, dict) and isinstance(logo.get("source"), str):
        old_source = logo["source"]
        new_source = swap_filename(old_source)
        logo["source"] = new_source
    else:
        print("No logo.source string found in config.", file=sys.stderr)
        sys.exit(1)

    # Determine colors for the currently selected image
    current_entry = find_anime_entry_for_filename(Path(logo["source"]).name)
    if not current_entry:
        # If the current logo isn't in ANIME_GIRLS, default to first entry's colors
        current_entry = ANIME_GIRLS[0] if ANIME_GIRLS else None

    colors = current_entry.get("colors", []) if current_entry else []

    # Apply colors to modules grouped by 'custom' separators
    modules = data.get("modules")
    if isinstance(modules, list):
        apply_category_colors(modules, colors)
    else:
        print("No modules list found in config.", file=sys.stderr)
        sys.exit(1)

    # Write back the updated config
    cfg.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Updated config: swapped logo to {logo['source']} and applied colors {colors} in {cfg}")

if __name__ == "__main__":
    main()
