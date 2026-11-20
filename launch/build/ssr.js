// snapshot runtime-rendered pages so crawlers get real HTML before JS runs
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const OUT=process.argv[2], BASE=process.argv[3]||'http://localhost:8790';
(async()=>{const urls=[];
 for(const d of fs.readdirSync(path.join(OUT,'products'),{withFileTypes:true})) if(d.isDirectory()) urls.push('/products/'+d.name+'/');
 urls.push('/products/','/gallery/');
 const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:1280,height:900}});const res={};
 for(const u of urls){const p=await ctx.newPage();
  await p.goto(BASE+u,{waitUntil:'networkidle'});await p.waitForTimeout(500);
  res[u]=await p.evaluate(()=>{const r=document.getElementById('dc-root');if(!r)return null;const c=r.cloneNode(true);
    c.querySelectorAll('script,style[data-dc]').forEach(e=>e.remove());
    c.querySelectorAll('[data-dc-tpl]').forEach(e=>e.removeAttribute('data-dc-tpl'));
    c.querySelectorAll('img').forEach(i=>{if(!i.getAttribute('src')||i.getAttribute('src').includes('{{'))i.remove();});
    const css=[...document.head.querySelectorAll('style')].map(s=>s.textContent).join('\n');
    return {css,html:c.innerHTML};});
  await p.close();}
 fs.writeFileSync(path.join(OUT,'..','ssr.json'),JSON.stringify(res));await b.close();console.log('ssr',Object.keys(res).length);})();
