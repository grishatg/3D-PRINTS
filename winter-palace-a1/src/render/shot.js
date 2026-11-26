// node shot.js <dir> <scene1> <scene2> ...   ->  <dir>/<scene>.png
// Files are handed to the page straight from disk (request interception), so no web server is needed.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const TYPES = { '.html': 'text/html', '.js': 'application/javascript', '.json': 'application/json', '.bin': 'application/octet-stream' };
(async () => {
  const dir = path.resolve(process.argv[2]);
  const names = process.argv.slice(3);
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader'] });
  for (const n of names) {
    const sc = JSON.parse(fs.readFileSync(path.join(dir, n + '.json'), 'utf8'));
    const p = await b.newPage({ viewport: { width: sc.w || 1600, height: sc.h || 1200 }, deviceScaleFactor: 1 });
    p.on('console', m => { if (m.type() === 'error') console.log('console:', m.text()); });
    await p.route('**/*', route => {
      const u = new URL(route.request().url());
      const f = path.join(dir, path.basename(u.pathname));
      if (!fs.existsSync(f)) return route.fulfill({ status: 404, body: 'missing' });
      route.fulfill({ status: 200, contentType: TYPES[path.extname(f)] || 'application/octet-stream', body: fs.readFileSync(f) });
    });
    await p.goto(`http://render.local/view.html?s=${n}.json`);
    await p.waitForFunction(() => document.title === 'done' || document.title.startsWith('err'), null, { timeout: 300000 });
    const t = await p.title();
    if (t !== 'done') console.log(n, t);
    await p.screenshot({ path: path.join(dir, n + '.png') });
    await p.close();
    console.log('shot', n);
  }
  await b.close();
})();
