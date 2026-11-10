"""
Step 2: builds index.html from private/portfolio_categorized.csv.
The output contains only title, category, post link and thumbnail.
No timestamps, no CSV, no Instagram "liked_by" links.
Usage:  python3 build.py
"""
import csv, hashlib, html, pathlib, re

SRC = pathlib.Path('private/portfolio_categorized.csv')
OUT = pathlib.Path('index.html')

def clean_url(u):
    return re.sub(r'liked_by/?$', '', u).rstrip('/') + '/'

def yt_id(u):
    m = re.search(r'(?:v=|shorts/|youtu\.be/)([\w-]{11})', u)
    return m.group(1) if m else None

rows = list(csv.DictReader(SRC.open(encoding='utf-8')))
sections = {}
for r in rows:
    sections.setdefault(r['category'], {}).setdefault(r['group'], []).append(r)

def card(r):
    t = html.escape(r['title'])
    p = r['platform']
    vid = yt_id(r['url']) if p == 'YouTube' else None
    if vid:
        short = ' short' if '/shorts/' in r['url'] else ''
        thumb = r['thumb'] or f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg'
        media = (f'<button class="play" data-vid="{vid}" style="background-image:url({html.escape(thumb)})" '
                 f'aria-label="Play: {t}"><span>&#9654;</span></button>')
        link = ''
    else:
        short = ''
        local = pathlib.Path('images') / (hashlib.md5(r['url'].encode()).hexdigest() + '.jpg')
        src = local.as_posix() if local.exists() else ''
        bg = f' style="background-image:url({src})"' if src else ''
        media = f'<div class="thumb"{bg}></div>'
        link = f'<a class="open" href="{html.escape(clean_url(r["url"]))}" target="_blank" rel="noopener">Open on {html.escape(p)} &rarr;</a>'
    return (f'<article class="card{short}" data-platform="{p}">{media}'
            f'<div class="info"><h3>{t}</h3><span class="meta">{html.escape(p)}</span>{link}</div></article>')

body = []
for cat, groups in sections.items():
    body.append(f'<section data-cat="{html.escape(cat)}"><h2>{html.escape(cat)}</h2>')
    for g, items in groups.items():
        if g:
            body.append(f'<h4>{html.escape(g)}</h4>')
        body.append('<div class="grid">' + ''.join(card(r) for r in items) + '</div>')
    body.append('</section>')

platforms = sorted({r['platform'] for r in rows})
pbtns = '<button data-p="all" class="on">All platforms</button>' + ''.join(
    f'<button data-p="{p}">{p}</button>' for p in platforms)
cbtns = '<button data-c="all" class="on">All</button>' + ''.join(
    f'<button data-c="{html.escape(c)}">{html.escape(c)}</button>' for c in sections)

page = f'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Portfolio</title>
<style>
:root{{color-scheme:light dark;--bg:#fafafa;--fg:#111;--mut:#666;--card:#fff;--line:#e5e5e5}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111;--fg:#eee;--mut:#999;--card:#1c1c1c;--line:#2a2a2a}}}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:system-ui,sans-serif;background:var(--bg);color:var(--fg)}}
header,main{{max-width:1200px;margin:auto;padding:16px}}
h1{{margin:8px 0 12px;font-size:1.6rem}}
.filters{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}}
.filters button{{border:1px solid var(--line);background:var(--card);color:var(--fg);padding:6px 12px;border-radius:20px;cursor:pointer;font:inherit;font-size:.9rem}}
.filters button.on{{background:var(--fg);color:var(--bg)}}
section h2{{font-size:1.25rem;margin:28px 0 4px;border-bottom:1px solid var(--line);padding-bottom:6px}}
section h4{{margin:16px 0 8px;color:var(--mut);font-weight:600}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;display:flex;flex-direction:column}}
.play,.thumb{{position:relative;width:100%;aspect-ratio:16/9;border:0;padding:0;background:#222 center/cover no-repeat;cursor:pointer}}
.card.short .play{{aspect-ratio:9/16}}
.play span{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:2.4rem;color:#fff;text-shadow:0 2px 8px #000;background:rgba(0,0,0,.15)}}
.play iframe{{position:absolute;inset:0;width:100%;height:100%;border:0}}
.info{{padding:10px}}
h3{{font-size:.92rem;margin:0 0 4px;line-height:1.3;font-weight:600}}
.meta{{font-size:.75rem;color:var(--mut)}}
.open{{display:inline-block;margin-top:6px;font-size:.82rem;color:var(--fg)}}
.hidden{{display:none!important}}
</style></head><body>
<header>
  <h1>Portfolio</h1>
  <div class="filters" id="cats">{cbtns}</div>
  <div class="filters" id="plats">{pbtns}</div>
</header>
<main id="main">
{chr(10).join(body)}
</main>
<script>
const cats=document.querySelectorAll('#cats button'), plats=document.querySelectorAll('#plats button');
let cat='all', plat='all';
function apply(){{
  document.querySelectorAll('section').forEach(s=>{{
    s.classList.toggle('hidden', cat!=='all' && s.dataset.cat!==cat);
    s.querySelectorAll('.card').forEach(c=>c.classList.toggle('hidden', plat!=='all' && c.dataset.platform!==plat));
  }});
}}
cats.forEach(b=>b.onclick=()=>{{cat=b.dataset.c;cats.forEach(x=>x.classList.toggle('on',x===b));apply();}});
plats.forEach(b=>b.onclick=()=>{{plat=b.dataset.p;plats.forEach(x=>x.classList.toggle('on',x===b));apply();}});
/* YouTube: thumbnail first, player loads on click (keeps the page light) */
document.addEventListener('click',e=>{{
  const b=e.target.closest('button.play'); if(!b||b.querySelector('iframe'))return;
  const f=document.createElement('iframe');
  f.src='https://www.youtube-nocookie.com/embed/'+b.dataset.vid+'?autoplay=1';
  f.allow='autoplay; encrypted-media; picture-in-picture'; f.allowFullscreen=true;
  b.innerHTML=''; b.appendChild(f);
}});
</script></body></html>'''
OUT.write_text(page, encoding='utf-8')
print('Wrote', OUT, f'({len(rows)} items, {len(sections)} categories)')
