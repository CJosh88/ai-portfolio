# ML Experiments

Small, reproducible experiments with new ML/AI releases, published as a blog at
**https://CJosh88.github.io/ai-portfolio**.

## Layout

```
_quarto.yml                 site config (title, navbar, theme)
index.qmd                   home page: auto-lists every experiment, newest first
about.qmd                   about page
styles.css
experiments/
  _metadata.yml             defaults for every post (author, no re-execution)
  2026-10-<slug>/
    notebook.ipynb          the post itself
    README.md               GitHub-only notes (not rendered on the site)
    requirements.txt        pinned versions
    figures/                saved charts (first one becomes the thumbnail)
tools/prep_post.py          adds title/date/tags + Colab badge to a notebook
.github/workflows/publish.yml   builds and deploys on every push to main
```

## One-time setup (about 10 minutes)

1. **Fill in the placeholders.** Search the repo for `YOUR-LINKEDIN`,
   `Your Name` and `you@example.com`, and replace them. They appear in `_quarto.yml`, `about.qmd`,
   `experiments/_metadata.yml`. (The GitHub username is already set to `CJosh88`.)
2. **Create a public GitHub repo** called `ai-portfolio` and push this folder to `main`.
3. **Turn on Pages:** repo *Settings → Pages → Build and deployment → Source: GitHub Actions*.
4. Open the *Actions* tab. The *Publish site* run takes about a minute. When it's green,
   your site is live at the URL above.
5. **Delete the example post** (`experiments/2026-10-example-tokenizer-speed/`) once your first real experiment is in.

Optional: to use a site at `https://CJosh88.github.io` with no `/ai-portfolio` suffix,
name the repo `CJosh88.github.io` instead and update `site-url` in `_quarto.yml`.
For a custom domain, add it under *Settings → Pages → Custom domain*.

## Publishing a new experiment

1. Run the notebook top to bottom, so its outputs are saved in the `.ipynb`. The site shows the
   saved outputs and never re-runs anything, so GPU and API-key experiments work fine.
2. Fill in the `TL;DR:` line in the first markdown cell. It becomes the summary on the home page.
3. Add the front matter:
   ```bash
   python tools/prep_post.py experiments/2026-10-my-slug \
       --title "Does X beat Y on Z?" --categories llm rag evaluation
   ```
   Add `--draft` to keep a post off the listing while you work on it.
4. Preview locally (optional; needs [Quarto](https://quarto.org/docs/get-started/)):
   `quarto preview`
5. Commit and push. The site rebuilds automatically.

## Troubleshooting

- **A post shows no outputs:** the notebook was saved without running it. Run all cells, save, push again.
- **The Action fails at "deploy":** check that Pages *Source* is set to *GitHub Actions* (step 3 above).
- **Huge notebook / slow page:** clear noisy cell outputs (long training logs) before saving.
  Keep charts, tables and a few examples.
