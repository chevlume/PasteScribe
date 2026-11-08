// Types into a real Draft.js editor (X's post box is one) through the extension's content script.
// Run: cd tests/extension/draft && npm install && npm test
const { chromium } = require('playwright');
const esbuild = require('esbuild');
const fs = require('fs');
const os = require('os');
const path = require('path');

const root = path.join(__dirname, '..', '..', '..', 'chrome-extension');
const contentJs = fs.readFileSync(process.env.CONTENT_JS || path.join(root, 'content.js'), 'utf8');
const messages = JSON.parse(fs.readFileSync(path.join(root, '_locales', 'en', 'messages.json'), 'utf8'));

const out = fs.mkdtempSync(path.join(os.tmpdir(), 'draft-test-'));
esbuild.buildSync({ entryPoints: [path.join(__dirname, 'app.js')], bundle: true, outfile: path.join(out, 'bundle.js'),
  define: { 'process.env.NODE_ENV': '"development"', global: 'window' }, logLevel: 'error' });
fs.writeFileSync(path.join(out, 'index.html'), '<!doctype html><meta charset=utf-8><div id=root></div><script src=bundle.js></script>');

const TEXT = 'Este es un texto de prueba, árbol ñandú.\nSegunda línea con 😀 y emoji.';
let failures = 0;
const check = (name, got, want) => { const ok = JSON.stringify(got) === JSON.stringify(want); if (!ok) failures++; console.log(ok ? 'PASS' : 'FAIL', name, ok ? '' : `got=${JSON.stringify(got)}`); };

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('file://' + path.join(out, 'index.html'));
  await page.waitForSelector('.public-DraftEditor-content');
  await page.click('.public-DraftEditor-content');
  await page.evaluate(contentJs);
  await page.evaluate((a) => window.__pastescribe.start(a), { text: TEXT, delayMs: 10, humanize: false, messages });
  await page.waitForFunction(() => !window.__pastescribe.status().running, null, { timeout: 30000 });
  check('draft editor text', await page.evaluate(() => window.__getText()), TEXT);
  check('final message', await page.evaluate(() => window.__pastescribe.status().message), `Done: ${Array.from(TEXT).length} characters typed.`);
  check('no page errors', errors, []);

  // typing again after existing content (editor not empty)
  await page.evaluate((a) => window.__pastescribe.start(a), { text: ' MAS', delayMs: 10, humanize: false, messages });
  await page.waitForFunction(() => !window.__pastescribe.status().running, null, { timeout: 30000 });
  check('appends to existing content', await page.evaluate(() => window.__getText()), TEXT + ' MAS');

  await browser.close();
  console.log(failures ? `${failures} FAILED` : 'ALL PASSED');
  process.exit(failures ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
