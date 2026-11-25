import json as _j, os as _o
NOINDEX=set(_j.load(open(_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),'noindex.json')))['urls'])
# SEO + performance polish over the built site (run after build.py)
import os,re,json,html,sys
from PIL import Image
OUT=sys.argv[1] if len(sys.argv)>1 else '/home/claude/flyvisuals-live/'
DOMAIN='https://flyvisualsfl.com'
TITLES={'/about/':'About Fly Visuals | Sign & Wrap Shop in Port Richey, FL','/blog/':'Sign & Wrap Tips | Fly Visuals Blog','/contact/':'Request a Free Quote | Fly Visuals',
'/financing/':'Sign & Wrap Financing with Snap | Fly Visuals','/gallery/':'Sign & Wrap Gallery | Fly Visuals Projects','/industries/':'Signs & Wraps by Industry | Fly Visuals',
'/locations/':'Service Area: Pasco, Pinellas & Hillsborough | Fly Visuals','/our-process/':'Our Sign & Wrap Process | Fly Visuals','/products/':'Order Signs, Banners & Stickers Online | Fly Visuals',
'/signs-and-graphics/':'Signs, Wraps & Graphics | All Products | Fly Visuals','/thanks/':'Thanks for Your Request | Fly Visuals','/services/':'Printing, Design & Sign Repair Services | Fly Visuals'}
DESC={'/about/':'Fly Visuals is a local sign and wrap shop in Port Richey, FL. We design, print and install business signs, vehicle wraps and graphics across Tampa Bay.',
'/blog/':'Tips and guides on business signs, vehicle wraps, permits and pricing from the Fly Visuals team in Port Richey, FL.',
'/contact/':'Request a free quote for signs, vehicle wraps, banners or printing. Fly Visuals replies within one business day. Port Richey, FL.',
'/financing/':'Get your sign or wrap now and pay over time with Snap Finance, up to 12 months interest free. Fly Visuals, Port Richey, FL.',
'/gallery/':'See real signs, vehicle wraps, boat wraps and window graphics made by Fly Visuals for businesses across Tampa Bay.',
'/guides/sign-permitting-guide/':'What needs a sign permit in Pasco, Pinellas and Hillsborough County, lit sign rules, and the details for Port Richey and New Port Richey.',
'/guides/vehicle-wraps-complete-guide/':'Vehicle wrap costs, cast vs. calendered vinyl, how long wraps last in Florida, and full vs. partial wraps. A guide from Fly Visuals.',
'/blog/car-wrap-cost/':'What a car wrap costs in Tampa Bay, what changes the price, and our $12 per square foot installed pricing for cars, trucks and vans.',
'/industries/':'Signs, wraps and graphics for contractors, restaurants, retail, medical offices, HOAs, schools, churches and more across Tampa Bay.',
'/locations/':'Fly Visuals serves Pasco, Pinellas, Hernando and Hillsborough from our sign shops in Port Richey and Tampa, including Clearwater and Wesley Chapel.',
'/our-process/':'How a Fly Visuals sign or wrap project works, from free quote and design proof to printing, fabrication and installation.',
'/products/':'Order yard signs, banners, stickers, flags and displays online. Ships across the US or pick up free at our Port Richey, FL shop.',
'/signs-and-graphics/':'Every sign, wrap and graphic we make: business signs, vehicle wraps, banners, window graphics, stickers, trade show displays and more.',
'/thanks/':'Thanks for your quote request. Fly Visuals will reach out within one business day.'}
def fit_title(t,url):
    if url in TITLES: return TITLES[url]
    t=html.unescape(t).strip()
    parts=[p.strip() for p in t.split(' | ')]
    if 'Fly Visuals' not in t:
        if len(parts)==1 and not re.search(r' in [A-Z]',t): parts.append('Tampa Bay Sign & Wrap Shop') if False else None
        parts.append('Fly Visuals')
    def L(p): return len(' | '.join(p))
    if len(parts)==2 and url.count('/')==2 and not url.startswith(('/industries','/locations','/blog','/guides','/products')) and ' in ' not in parts[0] and L([parts[0]+' in Tampa Bay','x'])<=52:
        parts[0]+=' in Tampa Bay'
    while L(parts)>65 and len(parts)>2: parts.pop(-2)
    if L(parts)>65 and parts[-1]=='Fly Visuals': parts.pop()
    if L(parts)>65 and parts[0].startswith('Order ') and parts[0].endswith(' Online'): parts[0]=parts[0][6:-7]
    return ' | '.join(parts)
CITY={'clearwater':'Clearwater','port-richey':'Port Richey','tampa':'Tampa','wesley-chapel':'Wesley Chapel'}
def fit_desc(d,url):
    if url in DESC: return DESC[url]
    d=re.sub(r'\s+',' ',html.unescape(d or '')).strip()
    seg=[x for x in url.split('/') if x]
    if len(seg)==2 and seg[1] in CITY and not url.startswith('/locations') and (len(d)>160 or CITY[seg[1]] not in d):
        d=re.sub(r'\s*Fly Visuals, Port Richey, FL\.$','',d)
        tail=' Serving %s, FL.'%CITY[seg[1]]; room=160-len(tail)
        cut=d[:room]; k=max(cut.rfind('. '),cut.rfind('! '),cut.rfind('? '))
        if len(d)+len(tail)<=160: return d+tail
        return (cut[:k+1] if k>=60 else cut[:cut.rfind(' ')].rstrip(',;:')+'…')+tail
    if len(d)>160:
        cut=d[:160]; k=max(cut.rfind('. '),cut.rfind('! '),cut.rfind('? '))
        d=cut[:k+1] if k>=90 else cut[:cut.rfind(' ')].rstrip(',;:')+'…'
    if len(d)<70 and url.startswith('/products/'):
        d=(d.rstrip('.')+'. ' if d else '')+'Order online with US shipping or free pickup in Port Richey, FL.'
    return d
# 800px copies for srcset
IMG=OUT+'images/'; SMALL={}
for f in os.listdir(IMG):
    if re.search(r'-800\.(jpg|png)$',f) or not f.endswith('.jpg'): continue
    im=Image.open(IMG+f); w,h=im.size
    sm=f[:-4]+'-800.jpg'
    if w>900:
        if not os.path.exists(IMG+sm): im.convert('RGB').resize((800,round(h*800/w)),Image.LANCZOS).save(IMG+sm,quality=78,optimize=True,progressive=True)
        SMALL[f]=(sm,w,h)
    else: SMALL[f]=(None,w,h)
def imgfix(s):
    n=[0]
    def rep(m):
        tag=m.group(0); n[0]+=1
        src=re.search(r'src="/images/([^"]+)"',tag)
        if src and src.group(1) in SMALL:
            sm,w,h=SMALL[src.group(1)]
            if sm and 'srcset' not in tag: tag=tag.replace('<img','<img srcset="/images/%s 800w, /images/%s %dw" sizes="(max-width: 700px) 100vw, 640px"'%(sm,src.group(1),w),1)
            if 'width=' not in tag: tag=tag.replace('<img','<img width="%d" height="%d"'%(w,h),1)
        if n[0]>2 and 'loading=' not in tag: tag=tag.replace('<img','<img loading="lazy" decoding="async"',1)
        return tag
    return re.sub(r'<img\b[^>]*>',rep,s)
def txt(x): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x))).strip()
def schema(s,url):
    out=[]
    nav=re.search(r'<nav aria-label="Breadcrumb"[^>]*>(.*?)</nav>',s,re.S)
    if nav:
        items=[]
        for m in re.finditer(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>|<span[^>]*>((?:(?!<span).)*?)</span>',nav.group(1),re.S):
            if m.group(1): items.append((txt(m.group(2)),DOMAIN+m.group(1) if m.group(1).startswith('/') else m.group(1)))
            elif m.group(3) and txt(m.group(3)) not in ('/',''): items.append((txt(m.group(3)),DOMAIN+url))
        if len(items)>1:
            out.append({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":u} for i,(n,u) in enumerate(items)]})
            if items[1][0] in ('Products','Services'):
                h1=re.search(r'<h1\b[^>]*>(.*?)</h1>',s,re.S)
                if h1: out.append({"@context":"https://schema.org","@type":"Service","name":txt(h1.group(1)),"url":DOMAIN+url,"provider":{"@id":DOMAIN+"/#port-richey"},"areaServed":["Pasco County, FL","Pinellas County, FL","Hillsborough County, FL","Hernando County, FL"]})
    qa=[]
    for m in re.finditer(r'<button[^>]*data-fv-faq[^>]*>(.*?)</button>\s*<p[^>]*>(.*?)</p>',s,re.S):
        q=txt(re.sub(r'<span aria-hidden="true">.*?</span></span>','',m.group(1))); q=re.sub(r'\s*[−+]$','',q)
        qa.append({"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":txt(m.group(2))}})
    if qa: out.append({"@context":"https://schema.org","@type":"FAQPage","mainEntity":qa})
    return ''.join('<script type="application/ld+json" data-fv-seo>%s</script>'%json.dumps(o,ensure_ascii=False) for o in out)

def layoutfix(s):
    # start with mobile menu closed and FAQs (except first) closed, so nothing jumps when site.js runs
    s=re.sub(r'(<nav aria-label="Mobile" data-fv-menu=""[^>]*style="[^"]*?)display: flex;',r'\1display: none;',s,count=1)
    m=re.search(r'<button type="button" class="fv-burger"[^>]*>',s)
    if m:
        tag=m.group(0); ci=re.search(r'data-fv-closed-icon="([^"]*)"',tag)
        new=tag.replace('aria-expanded="true"','aria-expanded="false"').replace('aria-label="Close menu"','aria-label="Open menu"')
        e=s.index(tag)+len(tag); end=s.index('</button>',e)
        s=s[:s.index(tag)]+new+(html.unescape(ci.group(1)) if ci else s[e:end])+s[end:]
    n=[0]
    def faq(m):
        n[0]+=1
        if n[0]==1: return m.group(0)
        b=m.group(1).replace('aria-expanded="true"','aria-expanded="false"').replace('<span class="sc-interp">−</span>','<span class="sc-interp">+</span>')
        return b+m.group(2)+'style="display: none; '+m.group(3)
    s=re.sub(r'(<button[^>]*data-fv-faq[^>]*>.*?</button>)(\s*<p\b[^>]*?)style="([^"]*)"',faq,s,flags=re.S)
    # main landmark
    if '<main' not in s:
        a=s.find('</header></div></div>'); b=s.find('<div class="sc-host" data-sc-name="Footer"')
        if a>0 and b>a:
            a+=len('</header></div></div>'); s=s[:a]+'<main id="main">'+s[a:b]+'</main>'+s[b:]
    # non-blocking fonts
    s=s.replace('<link href="https://fonts.googleapis.com/css2?','<link media="print" onload="this.media=\'all\'" href="https://fonts.googleapis.com/css2?')
    s=s.replace('src="/images/fly-visuals-logo.png"','src="/images/fly-visuals-logo-sm.png" width="243" height="104"')
    return s
stats={'pages':0,'srcset':0}
LG=IMG+'fly-visuals-logo.png'
if os.path.exists(LG):
    im=Image.open(LG); w,h=im.size; im.resize((round(w*104/h),104),Image.LANCZOS).save(IMG+'fly-visuals-logo-sm.png',optimize=True)

for root,_,fs in os.walk(OUT):
    for f in fs:
        if f!='index.html': continue
        p=os.path.join(root,f); url='/'+os.path.relpath(root,OUT).strip('.').strip('/')+'/'; url=url.replace('//','/')
        s=open(p,encoding='utf-8').read(); s0=s; runtime='<x-dc>' in s
        m=re.search(r'<title>(.*?)</title>',s,re.S)
        if m: s=s.replace(m.group(0),'<title>%s</title>'%html.escape(fit_title(m.group(1),url),quote=False),1)
        dm=re.search(r'<meta name="description" content="([^"]*)">',s)
        nd=fit_desc(dm.group(1) if dm else '',url)
        if nd:
            tag='<meta name="description" content="%s">'%html.escape(nd)
            s=s.replace(dm.group(0),tag,1) if dm else s.replace('</title>','</title>'+tag,1)
        if '<link rel="icon"' not in s:
            s=s.replace('</head>','<link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><meta name="theme-color" content="#111111"></head>',1)
        if url in NOINDEX and 'name="robots"' not in s:
            s=s.replace('<title>','<meta name="robots" content="noindex, follow"><title>',1)
        if url=='/order-complete/' and 'noindex' not in s:
            s=s.replace('<title>','<meta name="robots" content="noindex"><title>',1)
        if not runtime:
            s=layoutfix(s)
            s=imgfix(s)
            s=re.sub(r'<script type="application/ld\+json" data-fv-seo>.*?</script>','',s,flags=re.S)
            sc=schema(s,url)
            if sc: s=s.replace('</head>',sc+'</head>',1)
            if 'data-fv-tw' not in s:
                s=re.sub(r'(<table\b)',r'<div data-fv-tw style="overflow-x:auto;-webkit-overflow-scrolling:touch">\1',s); s=s.replace('</table>','</table></div>')
        if s!=s0: open(p,'w',encoding='utf-8').write(s); stats['pages']+=1
print('polished',stats,'small images',sum(1 for v in SMALL.values() if v[0]))
