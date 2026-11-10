"""
Step 1 (run on YOUR computer, once): downloads Facebook/Instagram thumbnails
into images/ so the site doesn't depend on expiring Meta links.
Usage:  python3 download_images.py
Needs:  Python 3 only (no installs).
"""
import csv, hashlib, pathlib, urllib.request

SRC = pathlib.Path('private/portfolio_categorized.csv')
OUT = pathlib.Path('images')
OUT.mkdir(exist_ok=True)

ok = failed = 0
with SRC.open(encoding='utf-8') as f:
    for r in csv.DictReader(f):
        if r['platform'] == 'YouTube' or not r['thumb']:
            continue
        name = hashlib.md5(r['url'].encode()).hexdigest() + '.jpg'
        dest = OUT / name
        if dest.exists():
            continue
        try:
            req = urllib.request.Request(r['thumb'], headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as resp, dest.open('wb') as out:
                out.write(resp.read())
            ok += 1
        except Exception as e:
            failed += 1
            print('FAILED:', r['url'], e)
print(f'Downloaded {ok}, failed {failed}. Links that fail have probably expired.')
