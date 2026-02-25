#!/usr/bin/env python3
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT_ROOT = ROOT / "Q_权力的游戏_中英对照word"
DOCS_ROOT = ROOT / "docs"

SEASON_RE = re.compile(r"Game\.Of\.Thrones\.(S\d{2})")
EP_RE = re.compile(r"Game\.Of\.Thrones\.(S\d{2}E\d{2})_eng_cn\.docx")


def run_pandoc(src: Path, dst: Path, title: str) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    # Convert docx to GitHub-flavored markdown to preserve tables.
    cmd = [
        "pandoc",
        "-f",
        "docx",
        "-t",
        "gfm",
        "--wrap=none",
        "-o",
        str(dst),
        str(src),
    ]
    subprocess.run(cmd, check=True)
    # Prepend a title header to make pages consistent.
    body = dst.read_text(encoding="utf-8")
    dst.write_text(f"# {title}\n\n{body}", encoding="utf-8")


def season_sort_key(season_code: str) -> int:
    return int(season_code[1:])


def episode_sort_key(ep_code: str) -> int:
    # S01E02 -> 102
    return int(ep_code[1:3]) * 100 + int(ep_code[4:6])


def build_nav(seasons):
    lines = [
        "site_name: Game of Thrones Scripts",
        "theme: readthedocs",
        "nav:",
        "  - Home: index.md",
    ]
    for season_code, episodes in seasons:
        season_dir = f"season-{season_code[1:]}"
        lines.append(f"  - Season {season_code[1:]}:")
        lines.append(f"      - Index: {season_dir}/index.md")
        for ep_code in episodes:
            ep_num = ep_code[4:6]
            lines.append(
                f"      - Episode {ep_num}: {season_dir}/episode-{ep_num}.md"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    if not INPUT_ROOT.exists():
        raise SystemExit(f"Input root not found: {INPUT_ROOT}")

    DOCS_ROOT.mkdir(parents=True, exist_ok=True)

    seasons = []

    for season_dir in sorted(INPUT_ROOT.iterdir()):
        if not season_dir.is_dir():
            continue
        m = SEASON_RE.fullmatch(season_dir.name)
        if not m:
            continue
        season_code = m.group(1)  # S01

        episodes = []
        for docx in sorted(season_dir.glob("*.docx")):
            m_ep = EP_RE.fullmatch(docx.name)
            if not m_ep:
                continue
            ep_code = m_ep.group(1)  # S01E01
            episodes.append(ep_code)

        episodes.sort(key=episode_sort_key)
        seasons.append((season_code, episodes))

        season_out_dir = DOCS_ROOT / f"season-{season_code[1:]}"
        for ep_code in episodes:
            ep_num = ep_code[4:6]
            src = season_dir / f"Game.Of.Thrones.{ep_code}_eng_cn.docx"
            dst = season_out_dir / f"episode-{ep_num}.md"
            title = f"{ep_code}"
            run_pandoc(src, dst, title)

        # Season index
        season_index = season_out_dir / "index.md"
        season_lines = [f"# Season {season_code[1:]}", ""]
        for ep_code in episodes:
            ep_num = ep_code[4:6]
            season_lines.append(f"- [Episode {ep_num}](episode-{ep_num}.md)")
        season_lines.append("")
        season_index.write_text("\n".join(season_lines), encoding="utf-8")

    seasons.sort(key=lambda s: season_sort_key(s[0]))

    # Root index
    root_lines = ["# Game of Thrones Scripts", "", "## Seasons", ""]
    for season_code, _ in seasons:
        season_dir = f"season-{season_code[1:]}"
        root_lines.append(
            f"- [Season {season_code[1:]}]({season_dir}/index.md)"
        )
    root_lines.append("")
    (DOCS_ROOT / "index.md").write_text("\n".join(root_lines), encoding="utf-8")

    # mkdocs.yml
    mkdocs = build_nav(seasons)
    (ROOT / "mkdocs.yml").write_text(mkdocs, encoding="utf-8")

    print("Site build files generated.")


if __name__ == "__main__":
    main()
