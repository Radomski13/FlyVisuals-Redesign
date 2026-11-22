#!/usr/bin/env python3
"""Add <lastmod> to sitemap.xml. A page's date changes only when its HTML changes.
Dates are kept in launch/sitemap-dates.json in the redesign repo."""
import sys, os, re, json, hashlib, datetime
OUT, DATES = sys.argv[1], sys.argv[2]
today = sys.argv[3] if len(sys.argv) > 3 else datetime.date.today().isoformat()
db = json.load(open(DATES)) if os.path.exists(DATES) else {}
sm = open(os.path.join(OUT, 'sitemap.xml')).read()
def page_hash(u):
    p = os.path.join(OUT, u.lstrip('/'), 'index.html')
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16] if os.path.exists(p) else None
changed = 0
def add(m):
    global changed
    loc = m.group(1); u = re.sub(r'^https?://[^/]+', '', loc) or '/'
    h = page_hash(u); e = db.get(u)
    if h and (not e or e['h'] != h):
        db[u] = {'h': h, 'd': today}; changed += 1
    d = db.get(u, {}).get('d', today)
    return '<url><loc>%s</loc><lastmod>%s</lastmod></url>' % (loc, d)
sm = re.sub(r'<url><loc>([^<]+)</loc>(?:<lastmod>[^<]*</lastmod>)?</url>', add, sm)
open(os.path.join(OUT, 'sitemap.xml'), 'w').write(sm)
json.dump(db, open(DATES, 'w'), indent=0, sort_keys=True)
print('sitemap lastmod: %d pages, %d new or changed' % (len(re.findall('<loc>', sm)), changed))
