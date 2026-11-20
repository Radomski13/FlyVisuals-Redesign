import json,os,re,sys,html
OUT=sys.argv[1]; d=json.load(open(os.path.join(OUT,'..','ssr.json'))); DOMAIN='https://flyvisualsfl.com'
SRC='/home/claude/flyvisuals-redesign/'
D=json.loads(re.search(r'var D = (\{.*?\});\n',open(SRC+'ShopProduct.dc.html').read()).group(1))
import csv
U2F={r['Production URL']:r['Design page'] for r in csv.DictReader(open(SRC+'launch/url-plan.csv'))}
BYF={v['file']:v for v in D.values()}
n=0
for u,v in d.items():
    if not v: continue
    p=os.path.join(OUT,u.strip('/'),'index.html'); s=open(p,encoding='utf-8').read()
    s=re.sub(r'<style id="fv-ssr-css">.*?</style>|<div id="fv-ssr">.*?<!--/fv-ssr--></div>(?:<script>new MutationObserver.*?</script>)?','',s,flags=re.S)
    block='<style id="fv-ssr-css">%s</style><div id="fv-ssr">%s<!--/fv-ssr--></div><script>new MutationObserver(function(m,o){var r=document.getElementById("dc-root");if(r&&r.children.length){var s=document.getElementById("fv-ssr");if(s)s.remove();o.disconnect();}}).observe(document.documentElement,{childList:true,subtree:true});</script>'%(v['css'],v['html'])
    s=s.replace('<x-dc>',block+'<x-dc>',1)
    slug=u.strip('/').split('/')[-1]; sc=[]
    x=BYF.get(U2F.get(u)) or D.get(slug)
    if u.startswith('/products/') and x:
        m=re.search(r'<meta name="description" content="([^"]*)"',s)
        img=re.search(r'<img[^>]*src="/?(images/(?!fly-visuals-logo)[^"]+)"',v['html'])
        o={"@context":"https://schema.org","@type":"Product","name":x['n'],"description":html.unescape(m.group(1)) if m else x.get('d',''),"brand":{"@type":"Brand","name":"Fly Visuals"},
           "offers":{"@type":"AggregateOffer","lowPrice":"%.2f"%x['f'],"priceCurrency":"USD","availability":"https://schema.org/InStock","url":DOMAIN+u}}
        if img: o["image"]=DOMAIN+'/'+img.group(1)
        sc.append(o)
        sc.append({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":DOMAIN+"/"},{"@type":"ListItem","position":2,"name":"Shop","item":DOMAIN+"/products/"},{"@type":"ListItem","position":3,"name":x['n'],"item":DOMAIN+u}]})
    s=re.sub(r'<script type="application/ld\+json" data-fv-ssr>.*?</script>','',s,flags=re.S)
    if sc: s=s.replace('</head>',''.join('<script type="application/ld+json" data-fv-ssr>%s</script>'%json.dumps(o,ensure_ascii=False) for o in sc)+'</head>',1)
    open(p,'w',encoding='utf-8').write(s); n+=1
print('ssr inserted',n)
