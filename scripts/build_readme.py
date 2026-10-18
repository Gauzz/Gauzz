"""Rebuild the Work section of README.md from work.yml.

Each run shows the next WORK_SHOW projects (default 5) from work.yml, moving
along by that many every run (GITHUB_RUN_NUMBER) and wrapping round at the end.
Run locally with `python scripts/build_readme.py` (needs `pip install pyyaml`).
"""
import os
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
WORK = ROOT / "work.yml"
START, END = "<!-- work starts -->", "<!-- work ends -->"


def render(entries):
    lines = []
    for i, e in enumerate(entries or [], 1):
        name = str(e.get("name", "")).strip()
        desc = str(e.get("description", "")).strip()
        if not name or not desc:
            sys.exit(f"work.yml entry {i} needs both a name and a description")
        link = str(e.get("link", "") or "").strip()
        title = f"[{name}]({link})" if link else name
        lines.append(f"- **{title}.** {desc}")
    return "\n".join(lines)


def main():
    readme = README.read_text(encoding="utf-8")
    if START not in readme or END not in readme:
        sys.exit(f"README.md is missing the {START} / {END} markers")
    entries = yaml.safe_load(WORK.read_text(encoding="utf-8")) or []
    if entries:
        run = int(os.environ.get("GITHUB_RUN_NUMBER", "0"))
        show = min(int(os.environ.get("WORK_SHOW", "5")), len(entries))
        start = (run * show) % len(entries)
        entries = [entries[(start + i) % len(entries)] for i in range(show)]
    block = f"{START}\n{render(entries)}\n{END}"
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, readme, flags=re.S)
    if new != readme:
        README.write_text(new, encoding="utf-8")
        print("README.md updated")
    else:
        print("README.md already up to date")


if __name__ == "__main__":
    main()
