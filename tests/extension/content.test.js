// Ejecutar con: node tests/extension/content.test.js  (requiere: npm i playwright)
const { chromium } = require('playwright');
const fs = require('fs');
const contentJs = fs.readFileSync(require('path').join(__dirname, '..', '..', 'chrome-extension', 'content.js'), 'utf8');
const LANG = process.env.LANG_UI || 'es';
const messages = JSON.parse(fs.readFileSync(require('path').join(__dirname, '..', '..', 'chrome-extension', '_locales', LANG, 'messages.json'), 'utf8'));
// Imita chrome.i18n.getMessage (placeholders $NAME$ -> $1..$9 -> sustituciones)
const i18nStub = (messages) => {
  window.chrome = { i18n: { getUILanguage: () => 'xx', getMessage: (key, subs = []) => {
    const m = messages[key]; if (!m) return '';
    const text = m.message.replace(/\$([A-Za-z0-9_@]+)\$/g, (_, n) => (m.placeholders && m.placeholders[n.toLowerCase()] || { content: '' }).content);
    return text.replace(/\$([1-9])/g, (_, i) => (subs[i - 1] === undefined ? '' : subs[i - 1]));
  } } };
};
const T = {
  es: { done16: 'Listo: 16 caracteres escritos.', cancelled: 'Cancelado.', stopped: 'Detenido:', focus: 'Detenido: el campo perdió el foco' },
  en: { done16: 'Done: 16 characters typed.', cancelled: 'Cancelled.', stopped: 'Stopped:', focus: 'Stopped: the field lost focus' },
}[LANG];
const html = `<!doctype html><body>
<input id="inp" type="text"><textarea id="ta"></textarea>
<div id="ce" contenteditable="true" style="min-height:40px;border:1px solid"></div>
<input id="pw" type="password"><input id="ro" readonly>
<iframe id="fr" srcdoc="<textarea id='inner'></textarea>"></iframe></body>`;
let fails = 0;
const check = (name, got, want) => { const ok = JSON.stringify(got) === JSON.stringify(want); if (!ok) fails++; console.log(ok ? 'PASS' : 'FAIL', name, ok ? '' : `got=${JSON.stringify(got)} want=${JSON.stringify(want)}`); };
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent(html);
  await page.evaluate(i18nStub, messages);
  await page.evaluate(contentJs);
  const start = (cfg) => page.evaluate((c) => window.__pastescribe.start(c), cfg);
  const wait = () => page.waitForFunction(() => !window.__pastescribe.status().running, null, { timeout: 15000 });
  const status = () => page.evaluate(() => window.__pastescribe.status());

  // input de una línea; \n se convierte en espacio
  await page.focus('#inp');
  await start({ text: 'Hola ñandú 😀\nfin', delayMs: 1, humanize: false }); await wait();
  check('input', await page.inputValue('#inp'), 'Hola ñandú 😀 fin');
  check('input msg', (await status()).message, T.done16);

  // textarea con saltos de línea y eventos input reales
  await page.evaluate(() => { window.__ev = 0; document.getElementById('ta').addEventListener('input', () => window.__ev++); });
  await page.focus('#ta');
  await start({ text: 'línea1\nlínea2', delayMs: 1, humanize: true }); await wait();
  check('textarea', await page.inputValue('#ta'), 'línea1\nlínea2');
  check('textarea input events', await page.evaluate(() => window.__ev), 13);

  // contenteditable
  await page.focus('#ce');
  await start({ text: 'abc\ndef', delayMs: 1 }); await wait();
  check('contenteditable', await page.evaluate(() => document.getElementById('ce').innerText.replace(/\n+/g, '|')), 'abc|def');

  // password
  await page.focus('#pw');
  await start({ text: 's3cr3t', delayMs: 0 }); await wait();
  check('password', await page.inputValue('#pw'), 's3cr3t');

  // iframe del mismo origen
  await page.evaluate(() => document.getElementById('fr').contentDocument.getElementById('inner').focus());
  await start({ text: 'dentro', delayMs: 1 }); await wait();
  check('iframe', await page.evaluate(() => document.getElementById('fr').contentDocument.getElementById('inner').value), 'dentro');

  // esperar campo: sin foco no escribe; al hacer clic empieza
  await page.fill('#inp', '');
  await page.evaluate(() => { document.getElementById('fr').contentDocument.activeElement.blur(); document.activeElement.blur(); });
  await start({ text: 'tarde', delayMs: 1 });
  await page.waitForTimeout(500);
  check('waiting phase', (await status()).phase, 'waiting');
  check('nothing typed yet', await page.inputValue('#inp'), '');
  await page.click('#inp'); await wait();
  check('typed after click', await page.inputValue('#inp'), 'tarde');

  // campo de solo lectura no cuenta como destino -> sigue esperando; Esc cancela
  await page.focus('#ro');
  await start({ text: 'x', delayMs: 1 });
  await page.waitForTimeout(400);
  check('readonly waits', (await status()).phase, 'waiting');
  await page.keyboard.press('Escape'); await wait();
  check('esc cancels wait', (await status()).message, T.cancelled);

  // Esc durante la escritura
  await page.fill('#ta', ''); await page.focus('#ta');
  await start({ text: 'x'.repeat(200), delayMs: 30 });
  await page.waitForTimeout(300);
  await page.keyboard.press('Escape'); await wait();
  const st = await status();
  const v = await page.inputValue('#ta');
  check('esc stops typing', st.message.startsWith(T.stopped) && v.length > 0 && v.length < 200, true);
  check('esc not typed into field', v.includes('\u001b'), false);

  // pérdida de foco
  await page.fill('#ta', ''); await page.focus('#ta');
  await start({ text: 'y'.repeat(200), delayMs: 20 });
  await page.waitForTimeout(200);
  await page.focus('#inp');
  await wait();
  check('focus lost msg', (await status()).message.startsWith(T.focus), true);

  // velocidad 0: no debe escribir de golpe y Esc debe poder detenerla
  await page.fill('#ta', ''); await page.focus('#ta');
  await start({ text: 'x'.repeat(3000), delayMs: 0 });
  await page.waitForTimeout(150);
  await page.keyboard.press('Escape'); await wait();
  check('delay 0 stoppable by Esc', (await page.inputValue('#ta')).length < 3000, true);

  // doble inicio y texto vacío
  await page.focus('#ta');
  const r1 = await start({ text: 'z'.repeat(100), delayMs: 20 });
  const r2 = await start({ text: 'otro', delayMs: 0 });
  check('double start rejected', [r1.ok, r2.ok], [true, false]);
  await page.evaluate(() => window.__pastescribe.stop()); await wait();
  check('empty text', (await start({ text: '', delayMs: 0 })).ok, false);

  // inyectar dos veces no rompe el estado
  await page.evaluate(contentJs);
  check('idempotent', typeof await page.evaluate(() => typeof window.__pastescribe.start), 'string');

  await browser.close();
  console.log(fails ? `${fails} FAILED` : 'ALL PASSED');
  process.exit(fails ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
