# Game of Thrones Scripts (EN/CN)

Bilingual (English/Chinese) Game of Thrones scripts organized by season and episode.

## Site

This project publishes a static site via GitHub Pages with one page per season and episode.

Local preview:

```bash
pip install mkdocs
python3 scripts/build_site.py
mkdocs serve
```

Deploy (CI):

```bash
git push origin main
```

## Structure

- `Q_权力的游戏_中英对照word/` source docx files
- `docs/` generated markdown pages
- `scripts/build_site.py` build script
- `mkdocs.yml` site config

## License

MIT
