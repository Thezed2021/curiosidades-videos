// Renderiza os quadros 3D de um vídeo com three.js no Chromium (Playwright) — sem internet.
// Uso (o engine chama sozinho): node render3d.js <timeline.json> <cena3d.js> <saida_dir> [frames=all|1,2,3] [capa]
const http = require('http'), fs = require('fs'), path = require('path');
const { chromium } = require('playwright');

const [, , tlPath, scenePath, outDir, framesArg = 'all', capaArg = ''] = process.argv;
const KIT = __dirname, WORK = path.dirname(path.resolve(scenePath));
const tl = JSON.parse(fs.readFileSync(tlPath, 'utf8'));
fs.mkdirSync(outDir, { recursive: true });

const html = `<!doctype html><html><body style="margin:0;background:#000">
<script type="importmap">{"imports":{"three":"/kit/three.module.min.js"}}</script>
<script type="module">
import * as L from '/kit/lib3d.js';
import * as S from '/work/${path.basename(scenePath)}';
const THREE = L.THREE, W = ${tl.W}, H = ${tl.H};
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H); renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap; renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(35, W / H, 0.1, 200);
const TL = ${JSON.stringify(tl)};
const api = { THREE, L, scene, camera, renderer, TL };
await S.setup(api);
window.renderFrame = (fi, name) => {
  const gt = fi / TL.fps; let b = TL.blocks[TL.blocks.length - 1];
  for (const x of TL.blocks) if (gt >= x.start && gt < x.end) { b = x; break; }
  if (name) b = { name, start: 0, end: 1, marks: [0] };
  const t = gt - b.start, d = b.end - b.start;
  const ctx = { name: b.name, t, d, gt, k: Math.min(1, t / d), mark: (i) => b.marks[Math.min(i, b.marks.length - 1)] };
  S.update(api, ctx);
  renderer.render(scene, camera);
  return true;
};
window.__ready = true;
</script></body></html>`;

const server = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split('?')[0]);
  let f = null;
  if (u === '/' || u === '/index.html') { res.writeHead(200, { 'Content-Type': 'text/html' }); return res.end(html); }
  if (u.startsWith('/kit/')) f = path.join(KIT, u.slice(5));
  if (u.startsWith('/work/')) f = path.join(WORK, u.slice(6));
  if (!f || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': f.endsWith('.js') ? 'text/javascript' : 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
});

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const port = server.address().port;
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: tl.W, height: tl.H } });
  page.on('console', m => { if (m.type() === 'error') console.error('[3d]', m.text()); });
  page.on('pageerror', e => { console.error('[3d] erro na cena:', e.message); process.exitCode = 2; });
  await page.goto(`http://127.0.0.1:${port}/`);
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 60000 });
  let frames = framesArg === 'all' ? [...Array(tl.nframes).keys()] : framesArg.split(',').filter(Boolean).map(Number);
  const fname = (fi) => path.join(outDir, String(fi).padStart(5, '0') + '.jpg');
  if (framesArg === 'all') frames = frames.filter(fi => !fs.existsSync(fname(fi)));  // retomável
  const maxS = Number(process.env.RENDER3D_MAX_S || 0), t0 = Date.now();
  console.log(`   3d: ${frames.length} quadros a renderizar` + (maxS ? ` (limite ${maxS}s nesta rodada)` : ''));
  for (let i = 0; i < frames.length; i++) {
    const fi = frames[i];
    await page.evaluate((fi) => window.renderFrame(fi), fi);
    const tmp = fname(fi) + '.part.jpg';
    await page.screenshot({ path: tmp, type: 'jpeg', quality: 92 });
    fs.renameSync(tmp, fname(fi));
    if (i % 100 === 0) console.log(`   3d ${i}/${frames.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
    if (maxS && (Date.now() - t0) / 1000 > maxS) { console.log(`   3d PARCIAL: parei no limite de tempo; rode de novo para continuar`); break; }
  }
  if (capaArg) {
    await page.evaluate(() => window.renderFrame(0, 'capa'));
    await page.screenshot({ path: path.join(outDir, 'capa.jpg'), type: 'jpeg', quality: 92 });
  }
  console.log(`   3d fim da rodada:  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  await browser.close(); server.close();
})().catch(e => { console.error(e); process.exit(1); });
