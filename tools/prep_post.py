#!/usr/bin/env python3
"""Turn an experiment notebook into a blog post for the Quarto site.

Usage:
    python tools/prep_post.py experiments/2026-10-graphrag-vs-rag \
        --title "Does GraphRAG beat vector RAG on multi-hop questions?" \
        --categories rag llm evaluation

What it does (safe to re-run; it updates rather than duplicates):
  1. Adds or updates a raw YAML cell at the top of notebook.ipynb with
     title, description, date, categories and an optional thumbnail.
  2. Adds an "Open in Colab" badge right after it.

The description defaults to the notebook's "TL;DR:" line, and the date
defaults to the YYYY-MM prefix of the folder name. Uses only the
standard library, so no install is needed.
"""
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

# Edit these once; or pass --user / --repo each time.
GITHUB_USER = "CJosh88"
GITHUB_REPO = "ai-portfolio"

FRONT_MATTER_TAG = "quarto-front-matter"
BADGE_TAG = "colab-badge"


def yaml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)  # JSON strings are valid YAML


def find_tldr(nb: dict) -> str | None:
    for cell in nb["cells"]:
        if cell["cell_type"] != "markdown":
            continue
        text = "".join(cell["source"])
        m = re.search(r"TL;DR:?\**\s*(.+)", text)
        if m and "TODO" not in m.group(1):
            return m.group(1).strip().strip("*").strip()
    return None


def date_from_folder(folder: Path) -> str:
    m = re.match(r"(\d{4})-(\d{2})(?:-(\d{2}))?", folder.name)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3) or '01'}"
    return dt.date.today().isoformat()


def has_tag(cell: dict, tag: str) -> bool:
    return tag in cell.get("metadata", {}).get("tags", [])


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("folder", type=Path, help="experiment folder containing notebook.ipynb")
    p.add_argument("--title", required=True)
    p.add_argument("--description", help="one-line summary (default: the notebook's TL;DR line)")
    p.add_argument("--date", help="YYYY-MM-DD (default: from folder name)")
    p.add_argument("--categories", nargs="*", default=[], help="tags, e.g. rag llm evaluation")
    p.add_argument("--image", help="thumbnail path relative to the folder, e.g. figures/results.png")
    p.add_argument("--draft", action="store_true", help="hide from the published listing")
    p.add_argument("--user", default=GITHUB_USER)
    p.add_argument("--repo", default=GITHUB_REPO)
    args = p.parse_args()

    nb_path = args.folder / "notebook.ipynb"
    if not nb_path.exists():
        sys.exit(f"Not found: {nb_path}")
    nb = json.loads(nb_path.read_text(encoding="utf-8"))

    description = args.description or find_tldr(nb)
    if not description:
        print("warning: no --description and no filled-in TL;DR line; the listing will show no summary.")

    image = args.image
    if not image:  # pick the first saved chart if there is one
        figs = sorted((args.folder / "figures").glob("*.png"))
        if figs:
            image = figs[0].relative_to(args.folder).as_posix()

    lines = ["---", f"title: {yaml_str(args.title)}"]
    if description:
        lines.append(f"description: {yaml_str(description)}")
    lines.append(f"date: {args.date or date_from_folder(args.folder)}")
    if args.categories:
        lines.append("categories: [" + ", ".join(yaml_str(c) for c in args.categories) + "]")
    if image:
        lines.append(f"image: {yaml_str(image)}")
    if args.draft:
        lines.append("draft: true")
    lines.append("---")
    front = {
        "cell_type": "raw",
        "metadata": {"tags": [FRONT_MATTER_TAG]},
        "source": "\n".join(lines),
    }

    nb_rel = nb_path.as_posix().split("experiments/", 1)[-1]
    colab = f"https://colab.research.google.com/github/{args.user}/{args.repo}/blob/main/experiments/{nb_rel}"
    badge = {
        "cell_type": "markdown",
        "metadata": {"tags": [BADGE_TAG]},
        "source": f"[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)]({colab})",
    }

    cells = [c for c in nb["cells"] if not (has_tag(c, FRONT_MATTER_TAG) or has_tag(c, BADGE_TAG))]

    # The title now lives in the front matter; drop the notebook's leading
    # "# Title" line so the page doesn't show it twice.
    if cells and cells[0]["cell_type"] == "markdown":
        src = "".join(cells[0]["source"])
        new = re.sub(r"\A\s*# [^\n]*\n*", "", src)
        if new != src:
            cells[0]["source"] = new
            if not new.strip():
                cells = cells[1:]

    nb["cells"] = [front, badge] + cells
    nb_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Updated {nb_path}")
    print("\n".join(lines))
    if args.user == "YOUR-GITHUB-USERNAME":
        print("note: set GITHUB_USER at the top of this script so the Colab link works.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
