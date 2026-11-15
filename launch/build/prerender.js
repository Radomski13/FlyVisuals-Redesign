// usage: node prerender.js plan.json outdir
const { chromium } = require('playwright'); const fs = require('fs');
const plan = JSON.parse(fs.readFileSync(process.argv[2])); const out = process.argv[3];
const BASE = process.env.PR_BASE || 'http://localhost:8765/';
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const errs = []; let n = 0;
  const work = async (items) => {
    const p = await ctx.newPage(); p.on('pageerror', e => errs.push(p.url() + ' ' + e.message));
    for (const it of items) {
      await p.goto(BASE + it.file, { waitUntil: 'networkidle' }); await p.waitForTimeout(350);
      if (it.mode === 'runtime-meta') {
        const meta = await p.evaluate(() => { const h = document.querySelector('h1'); let d = ''; if (h) { let el = h.parentElement.querySelector('p'); if (el) d = el.innerText; } return { h1: h ? h.innerText : '', d }; });
        fs.writeFileSync(out + '/' + it.id + '.json', JSON.stringify(meta)); n++; continue;
      }
      if (it.mode === 'thanks') { await p.getByRole('button', { name: /Get My Free Quote/ }).click(); await p.waitForTimeout(300); }
      // expand every FAQ-style toggle
      for (let i = 0; i < 80; i++) {
        const did = await p.evaluate(() => { const btn = [...document.querySelectorAll('button[aria-expanded="false"]')].find(x => !x.classList.contains('fv-burger')); if (!btn) return false; btn.click(); return true; });
        if (!did) break; await p.waitForTimeout(40);
      }
      await p.evaluate(() => { document.querySelectorAll('button[aria-expanded="true"]').forEach(x => { if (!x.classList.contains('fv-burger')) x.setAttribute('data-fv-faq', ''); }); });
      // open mobile menu so it is in the DOM, then tag it
      const hasBurger = await p.evaluate(() => { const bb = document.querySelector('.fv-burger'); if (!bb) return false; bb.setAttribute('data-fv-closed-icon', bb.innerHTML); bb.click(); return true; });
      if (hasBurger) { await p.waitForTimeout(150); await p.evaluate(() => { const bb = document.querySelector('.fv-burger'); bb.setAttribute('data-fv-open-icon', bb.innerHTML); const nav = document.querySelector('nav[aria-label="Mobile"]'); if (nav) nav.setAttribute('data-fv-menu', ''); }); }
      const html = await p.evaluate(() => '<!doctype html>\n' + document.documentElement.outerHTML);
      fs.writeFileSync(out + '/' + it.id + '.html', html); n++;
    }
    await p.close();
  };
  const k = 6, chunks = Array.from({ length: k }, (_, i) => plan.filter((_, j) => j % k === i));
  await Promise.all(chunks.map(work));
  console.log('rendered', n, 'errors', errs.length); if (errs.length) console.log(errs.slice(0, 5).join('\n'));
  await b.close();
})();
