const { chromium, devices } = require('playwright'); const fs=require('fs');
const ROOT='/home/claude/flyvisuals-live'; const B='http://localhost:8790';
const urls=fs.readFileSync(ROOT+'/sitemap.xml','utf8').match(/<loc>[^<]+<\/loc>/g).map(x=>x.replace(/<\/?loc>/g,'').replace('https://flyvisualsfl.com',''));
const exists=u=>{u=u.split('#')[0].split('?')[0]; if(!u.startsWith('/'))return true; if(u==='/')return true; return fs.existsSync(ROOT+u+(u.endsWith('/')?'index.html':''))||fs.existsSync(ROOT+u);};
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:1440,height:900}});
const errs=[];const broken={};let i=0;
const work=async(list)=>{const p=await ctx.newPage();p.on('pageerror',e=>errs.push(p.url()+' '+e.message));
for(const u of list){await p.goto(B+u,{waitUntil:'networkidle'});await p.waitForTimeout(150);
 const links=await p.evaluate(()=>[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')));
 for(const l of links){ if(/^(https?:|tel:|mailto:|#)/.test(l))continue; if(!exists(l)){(broken[l]=broken[l]||[]).push(u);} }
 const h1=await p.locator('h1').count(); if(!h1) errs.push(u+' NO H1'); i++;}
await p.close();};
const k=6;await Promise.all(Array.from({length:k},(_,j)=>work(urls.filter((_,n)=>n%k===j))));
console.log('checked',i,'errors',errs.length);console.log(errs.slice(0,8).join('\n'));
console.log('broken',Object.keys(broken).length);for(const [l,ps] of Object.entries(broken).slice(0,15))console.log(l,'<-',ps.length,ps[0]);
await b.close();})();
