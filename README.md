# Portfolio

A simple static portfolio site (GitHub Pages).

## Updating the site
1. Put your updated CSV at `private/portfolio_categorized.csv` (this folder is git-ignored).
2. `python3 download_images.py` downloads Facebook/Instagram thumbnails into `images/`.
3. `python3 build.py` regenerates `index.html`.
4. Commit and push `index.html` and `images/`.

## Publishing
Settings > Pages > Deploy from a branch > `main` / `(root)`.
Site: https://YOUR-USERNAME.github.io/REPO-NAME/
