import csv, json, os, re, shutil, subprocess, html, sys
SRC='/home/claude/flyvisuals-redesign/'; OUT='/home/claude/flyvisuals-live/'; RAW='/tmp/claude-0/-home-claude/a8013e0b-8655-5c58-81c7-1543d506ab10/scratchpad/build/raw/'
DOMAIN='https://flyvisualsfl.com'; STAGING = '--prod' not in sys.argv
plan=[r for r in csv.DictReader(open(SRC+'launch/url-plan.csv'))]
URL={r['Design page']:r['Production URL'] for r in plan}
URL['Classic.dc.html']='/'; URL['index.html']='/'; URL['BlogPost.dc.html']='/blog/'
RUNTIME=lambda f: f.startswith('Shop') or f=='Gallery.dc.html'
if '--skip-render' not in sys.argv:
    shutil.rmtree(RAW,ignore_errors=True); os.makedirs(RAW)
    items=[]
    for i,r in enumerate(plan):
        f=r['Design page']; f2='index.html' if f=='Classic.dc.html' else f
        items.append({'id':str(i),'file':f2,'mode':'runtime-meta' if RUNTIME(f) and f!='Shop.dc.html' and f!='Gallery.dc.html' else ('skip' if RUNTIME(f) else 'static')})
    items.append({'id':'thanks','file':'Quote.dc.html','mode':'thanks'})
    json.dump([x for x in items if x['mode']!='skip'],open(RAW+'plan.json','w'))
    PS='/tmp/claude-0/-home-claude/a8013e0b-8655-5c58-81c7-1543d506ab10/scratchpad/build/psrc/'
    shutil.rmtree(PS,ignore_errors=True); shutil.copytree(SRC,PS,ignore=shutil.ignore_patterns('.git'))
    for t in ['Product','Option','City','Industry','Process']:
        fp=PS+t+'.dc.html'; x=open(fp).read(); assert 'var open = self.state.open === i;' in x; open(fp,'w').write(x.replace('var open = self.state.open === i;','var open = true;'))
    srv=subprocess.Popen(['python3','-m','http.server','8766'],cwd=PS,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    import time; time.sleep(1)
    try: subprocess.run(['node','prerender.js',RAW+'plan.json',RAW],check=True,env=dict(os.environ,PR_BASE='http://localhost:8766/'))
    finally: srv.kill()
shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT)
shutil.copytree(SRC+'_blob',OUT+'_blob'); shutil.copy(SRC+'support.js',OUT+'support.js'); shutil.copy('site.js',OUT+'site.js')
unknown=set()
def mapurl(m):
    f=m.group(2)
    if f in URL: return m.group(1)+URL[f]+m.group(3)
    unknown.add(f); return m.group(0)
def fixlinks(s):
    s=re.sub(r'(["\'])(?:\./)?([A-Za-z0-9-]+\.dc\.html)(#[^"\']*)?(?=["\'])',lambda m:m.group(1)+(URL.get(m.group(2)) or (unknown.add(m.group(2)) or m.group(2)))+(m.group(3) or ''),s)
    s=re.sub(r'(["\(]|&quot;)(?:\./)?_blob/',r'\1/_blob/',s)
    if 'ALT' not in globals(): globals()['ALT']=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'photo_alt.json')))
    def _alt(m):
        tag=m.group(0); mm=re.search(r'/_blob/([0-9a-f]{32})',tag)
        if not mm or mm.group(1) not in ALT: return tag
        alt=ALT[mm.group(1)].replace('&','&amp;').replace('"','&quot;')
        return re.sub(r'\salt="[^"]*"',' alt="%s"'%alt,tag) if ' alt="' in tag else tag[:-1]+' alt="%s">'%alt
    s=re.sub(r'<img\b[^>]*>',_alt,s)
    s=re.sub(r'href=(["\'])(?:\./)?index\.html\1',r'href=\1/\1',s)
    return s
def schema_home():
    return {"@context":"https://schema.org","@type":"LocalBusiness","@id":DOMAIN+"/#port-richey","name":"Fly Visuals","url":DOMAIN+"/","telephone":"+1-727-494-6162","email":"flyvisualsfl@gmail.com",
            "address":{"@type":"PostalAddress","streetAddress":"8132 Cormel St","addressLocality":"Port Richey","addressRegion":"FL","postalCode":"34668","addressCountry":"US"},
            "openingHours":"Mo-Fr 09:00-17:00","areaServed":["Pasco County, FL","Pinellas County, FL","Hillsborough County, FL","Hernando County, FL"],"priceRange":"$$"}
def finish_static(h,url,extra_head=''):
    h=re.sub(r'<script src="[^"]*support\.js"></script>','',h)
    h=re.sub(r'<script type="text/x-dc"[^>]*>.*?</script>','',h,flags=re.S)
    h=re.sub(r' data-dc-tpl="\d+"','',h)
    h=fixlinks(h)
    can='<link rel="canonical" href="%s%s">'%(DOMAIN,url)
    h=h.replace('</head>',can+extra_head+'<script src="/site.js" defer></script></head>',1)
    return h
written=[]
def write(url,h):
    d=OUT+url.strip('/'); os.makedirs(d,exist_ok=True); open((d+'/' if url!='/' else OUT)+'index.html','w').write(h); written.append(url)
for i,r in enumerate(plan):
    f=r['Design page']; url=r['Production URL']
    if RUNTIME(f):
        s=open(SRC+f).read()
        s=s.replace('<script src="./support.js"></script>','<base href="/"><script src="/support.js"></script>')
        if f.startswith('Shop-'):
            meta=json.load(open(RAW+str(i)+'.json'))
            t=html.escape(meta['h1']); d=html.escape(meta['d'][:300])
            if 'SHOPD' not in globals():
                globals()['SHOPD']={v['file']:v for v in json.loads(re.search(r'var D = (\{.*?\});\n',open(SRC+'ShopProduct.dc.html').read()).group(1)).values()}
            sp=SHOPD.get(f); pr=(' | From $%.2f'%sp['f']) if sp else ''
            s=re.sub(r'<title>.*?</title>','<title>Order %s Online%s | Fly Visuals</title>\n<meta name="description" content="%s">'%(t,pr,d),s,1)
        s=fixlinks(s)
        s=s.replace('</head>','<link rel="canonical" href="%s%s"></head>'%(DOMAIN,url),1)
        write(url,s); continue
    h=re.sub(r' data-dc-tpl="\d+"','',open(RAW+str(i)+'.html').read())
    extra=''
    if f in ('Classic.dc.html','City-Port-Richey.dc.html'):
        extra='<script type="application/ld+json">%s</script>'%json.dumps(schema_home())
    if f=='Blog.dc.html':
        h=re.sub(r'<div role="group" aria-label="Filter[^"]*"[^>]*>.*?</div>','',h,count=1,flags=re.S)
    if f=='Quote.dc.html':
        h=h.replace('<form style=','<form name="quote" method="POST" action="/thanks/" data-netlify="true" netlify-honeypot="bot-field" style=',1)
        h=h.replace('<form name="quote"','<form name="quote"',1)
        h=re.sub(r'(<form name="quote"[^>]*>)',r'\1<input type="hidden" name="form-name" value="quote"><p hidden><label>Leave this empty <input name="bot-field"></label></p><input type="hidden" name="services" value="" data-on="font: inherit; font-weight: 600; font-size: 14px; padding: 10px 16px; min-height: 44px; border-radius: 999px; cursor: pointer; border: 1px solid #111111; background: #111111; color: #FFFFFF" data-off="font: inherit; font-weight: 600; font-size: 14px; padding: 10px 16px; min-height: 44px; border-radius: 999px; cursor: pointer; border: 1px solid #BEBEBE; background: #FFFFFF; color: #111111">',h,1)
        for a,nm,req in [('autocomplete="name"','name',' required'),('autocomplete="tel"','phone',''),('autocomplete="email"','email','')]:
            h=h.replace('<input type="%s" %s'%({'name':'text','phone':'tel','email':'email'}[nm],a),'<input name="%s"%s type="%s" %s'%(nm,req,{'name':'text','phone':'tel','email':'email'}[nm],a),1)
        h=h.replace('<textarea rows="3"','<textarea name="details" rows="3"',1)
        h=re.sub(r'<button type="button" aria-pressed="false"',r'<button type="button" data-fv-chip aria-pressed="false"',h)
        h=re.sub(r'<button type="button"([^>]*)>Get My Free Quote</button>',r'<button type="submit"\1>Get My Free Quote</button>',h,1)
        assert 'name="phone"' in h and 'type="submit"' in h and 'data-fv-chip' in h
    write(url,finish_static(h,url,extra))
# thanks page
h=open(RAW+'thanks.html').read()
h=re.sub(r'<button type="button"[^>]*>Send another request</button>','<a href="/" style="font-family: \'Montserrat\', sans-serif; font-weight: 700; color: #111111">Back to home →</a>',h)
h=h.replace('<title>','<meta name="robots" content="noindex"><title>',1)
write('/thanks/',finish_static(h,'/thanks/'))
# components needed by runtime pages
for c in ['Header','Footer','ShopProduct']:
    open(OUT+c+'.dc.html','w').write(fixlinks(open(SRC+c+'.dc.html').read()))
# 404
h=open(OUT+'index.html').read()
four=re.sub(r'<title>.*?</title>','<title>Page not found | Fly Visuals</title><meta name="robots" content="noindex">',h,1)
open(OUT+'404.html','w').write(four)
# redirects
red=['# old site → new site (301)']+[l.rstrip() for l in open(SRC+'launch/_redirects') if l.strip() and not l.startswith('#')]
red+=['# design file names → clean URLs']+['/%s  %s  301'%(f,u) for f,u in URL.items() if f.endswith('.dc.html') and f not in ('Header.dc.html','Footer.dc.html','ShopProduct.dc.html')]
open(OUT+'_redirects','w').write('\n'.join(red)+'\n')
hd=open(SRC+'_headers').read()
if STAGING: hd='/*\n  X-Robots-Tag: noindex\n'+hd
open(OUT+'_headers','w').write(hd)
open(OUT+'robots.txt','w').write(('User-agent: *\nDisallow: /\n' if STAGING else 'User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n'%DOMAIN))
sm=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']+['<url><loc>%s%s</loc></url>'%(DOMAIN,u) for u in sorted(set(written)) if u!='/thanks/']+['</urlset>']
open(OUT+'sitemap.xml','w').write('\n'.join(sm))
print('pages',len(written),'unknown links',sorted(unknown))
