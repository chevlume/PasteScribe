// Genera las capturas y la imagen promocional de la Chrome Web Store en store-assets/.
// Usa el código real de la extensión (content.js y popup). Requiere: npm i playwright
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const ext = path.join(root, 'chrome-extension');
const LANG = process.env.LANG_UI || 'es';   // es | en
const out = path.join(root, 'store-assets', LANG);
const messages = JSON.parse(fs.readFileSync(path.join(ext, '_locales', LANG, 'messages.json'), 'utf8'));
const COPY = {
  es: { sample: 'Hola, quisiera pedir información sobre el curso de otoño.\nMe interesan los horarios de tarde y el precio de la matrícula.\nGracias de antemano por vuestra respuesta.',
        school: 'Academia Ejemplo', title: 'Solicitud de información', name: 'Nombre', person: 'Laura Martínez', msg: 'Mensaje', ph: 'Escribe tu mensaje…', send: 'Enviar',
        h1: 'Escribe tu texto letra por letra', s1: 'Haz clic en el campo de texto de la página', s2: 'Abre PasteScribe, pega el texto y elige la velocidad',
        s3: 'Pulsa «Escribir». Esc lo detiene al instante', small: 'Solo actúa en la pestaña activa. No envía datos a ningún servidor.', tile: 'Escribe tu texto pegado letra por letra', html: 'es' },
  en: { sample: 'Hello, I would like some information about the autumn course.\nI am interested in the afternoon schedule and the enrollment fee.\nThank you in advance for your reply.',
        school: 'Example Academy', title: 'Information request', name: 'Name', person: 'Laura Martin', msg: 'Message', ph: 'Write your message…', send: 'Send',
        h1: 'Type your text letter by letter', s1: 'Click the text field on the page', s2: 'Open PasteScribe, paste your text and pick the speed',
        s3: 'Press “Type”. Esc stops it instantly', small: 'Only works on the active tab. Sends no data to any server.', tile: 'Types your pasted text letter by letter', html: 'en' },
}[LANG];
// Imita chrome.i18n.getMessage con las traducciones reales de la extensión.
const i18nStub = ({ messages, lang }) => {
  window.chrome = window.chrome || {};
  window.chrome.i18n = { getUILanguage: () => lang, getMessage: (key, subs = []) => {
    const m = messages[key]; if (!m) return '';
    const text = m.message.replace(/\$([A-Za-z0-9_@]+)\$/g, (_, n) => (m.placeholders && m.placeholders[n.toLowerCase()] || { content: '' }).content);
    return text.replace(/\$([1-9])/g, (_, i) => (subs[i - 1] === undefined ? '' : subs[i - 1]));
  } };
};
fs.mkdirSync(out, { recursive: true });
const contentJs = fs.readFileSync(path.join(ext, 'content.js'), 'utf8');

const SAMPLE = COPY.sample;

const formPage = `<!doctype html><html lang="${COPY.html}"><meta charset="utf-8"><style>
body{margin:0;font:16px system-ui,"Segoe UI",sans-serif;background:#eef2f7;color:#1f2937}
header{background:#1e3a8a;color:#fff;padding:18px 40px;font-size:20px;font-weight:600}
main{max-width:640px;margin:48px auto 0 90px;background:#fff;border-radius:12px;padding:32px 36px;box-shadow:0 6px 24px rgba(15,23,42,.12)}
h1{margin:0 0 20px;font-size:22px} label{display:block;margin:16px 0 6px;font-weight:600;font-size:14px}
input,textarea{width:100%;box-sizing:border-box;padding:10px 12px;font:inherit;border:1px solid #cbd5e1;border-radius:8px}
textarea{height:210px;resize:none} textarea:focus,input:focus{outline:2px solid #2563eb;border-color:#2563eb}
button{margin-top:20px;padding:10px 22px;border:0;border-radius:8px;background:#2563eb;color:#fff;font:inherit;font-weight:600}
</style><header>${COPY.school}</header><main><h1>${COPY.title}</h1>
<label>${COPY.name}</label><input value="${COPY.person}" readonly>
<label>${COPY.msg}</label><textarea id="msg" placeholder="${COPY.ph}"></textarea>
<button>${COPY.send}</button></main></html>`;

// Simula chrome.* para renderizar el popup real sin instalarlo (solo para la captura).
const allMessages = Object.fromEntries(['en', 'es'].map((l) =>
  [l, JSON.parse(fs.readFileSync(path.join(ext, '_locales', l, 'messages.json'), 'utf8'))]));
const chromeStub = (text, delay) => `
  window.fetch = async (url) => ({ ok: true, json: async () => (${JSON.stringify(allMessages)})[/_locales\\/(\\w+)\\//.exec(url)[1]] });
  window.chrome = Object.assign(window.chrome || {}, { runtime: { getURL: (p) => p }, tabs: { query: async () => [{ id: 1 }] },
    scripting: { executeScript: async (o) => [{ result: o.func ? { running: false, phase: 'idle', typed: 0, total: 0, message: '' } : undefined }] },
    storage: { local: { get: async (d) => ({ ...d, delay: ${delay}, humanize: true, lang: ${JSON.stringify(LANG)} }), set: async () => {} },
               session: { get: async (d) => ({ ...d, text: ${JSON.stringify(text)} }), set: async () => {} } } });`;

(async () => {
  const browser = await chromium.launch();

  // 1) Popup real (alta resolución) para componer
  const popupCtx = await browser.newContext({ viewport: { width: 340, height: 600 }, deviceScaleFactor: 2 });
  const popup = await popupCtx.newPage();
  await popup.addInitScript(chromeStub(SAMPLE, 60));
  await popup.goto('file://' + path.join(ext, 'popup', 'popup.html'));
  await popup.waitForSelector('body.ready');
  await popup.waitForTimeout(200);
  const popupBox = await popup.evaluate(() => ({ h: Math.ceil(document.body.getBoundingClientRect().height) }));
  const popupPng = await popup.screenshot({ clip: { x: 0, y: 0, width: 340, height: popupBox.h } });

  // 2) Página con el formulario escribiéndose de verdad (content.js real)
  const pageCtx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await pageCtx.newPage();
  await page.setContent(formPage);
  await page.evaluate(i18nStub, { messages, lang: LANG });
  await page.evaluate(contentJs);
  await page.focus('#msg');
  await page.evaluate((t) => window.__pastescribe.start({ text: t, delayMs: 25, humanize: false }), SAMPLE);
  await page.waitForFunction(() => window.__pastescribe.status().typed >= 95, null, { timeout: 20000 });
  const pagePng = await page.screenshot();
  await page.evaluate(() => window.__pastescribe.stop());

  // 3) Captura 1: la página escribiéndose de verdad (el popup se cierra al empezar, así que no aparece)
  const b64 = (b) => 'data:image/png;base64,' + b.toString('base64');
  const compose = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const c = await compose.newPage();
  await c.setContent(`<style>body{margin:0;width:1280px;height:800px;position:relative;overflow:hidden;font-family:system-ui,"Segoe UI",sans-serif}
    .bg{position:absolute;inset:0;width:1280px;height:800px}
    .popup{position:absolute;right:48px;top:96px;width:340px;border-radius:10px;box-shadow:0 12px 40px rgba(0,0,0,.35),0 0 0 1px rgba(0,0,0,.12)}
    .cap{position:absolute;left:0;right:0;top:0;height:0}</style>
    <img class="bg" src="${b64(pagePng)}">`);
  await c.waitForTimeout(200);
  await c.screenshot({ path: path.join(out, 'screenshot-1-escribiendo.png') });

  // 4) Captura 2: popup ampliado con los tres pasos
  const s2 = await compose.newPage();
  await s2.setContent(`<style>body{margin:0;width:1280px;height:800px;display:flex;align-items:center;justify-content:center;gap:70px;
    background:linear-gradient(135deg,#1e3a8a,#2563eb);font-family:system-ui,"Segoe UI",sans-serif;color:#fff}
    img{width:476px;border-radius:14px;box-shadow:0 20px 60px rgba(0,0,0,.45)}
    ol{margin:0;padding:0;list-style:none;max-width:520px} h1{font-size:40px;line-height:1.15;margin:0 0 34px}
    li{display:flex;gap:16px;align-items:flex-start;font-size:22px;line-height:1.35;margin-bottom:22px}
    li b{flex:none;width:38px;height:38px;border-radius:50%;background:#fff;color:#1e3a8a;display:flex;align-items:center;justify-content:center;font-size:20px}
    small{display:block;margin-top:30px;font-size:17px;opacity:.85}</style>
    <img src="${b64(popupPng)}"><div><h1>${COPY.h1}</h1><ol>
    <li><b>1</b><span>${COPY.s1}</span></li>
    <li><b>2</b><span>${COPY.s2}</span></li>
    <li><b>3</b><span>${COPY.s3}</span></li></ol>
    <small>${COPY.small}</small></div>`);
  await s2.waitForTimeout(200);
  await s2.screenshot({ path: path.join(out, 'screenshot-2-pasos.png') });

  // 5) Mosaico promocional 440x280
  const tileCtx = await browser.newContext({ viewport: { width: 440, height: 280 } });
  const t = await tileCtx.newPage();
  const icon = fs.readFileSync(path.join(ext, 'icons', 'icon-128.png'));
  await t.setContent(`<style>body{margin:0;width:440px;height:280px;display:flex;flex-direction:column;align-items:center;justify-content:center;
    background:linear-gradient(135deg,#1e3a8a,#2563eb);font-family:system-ui,"Segoe UI",sans-serif;color:#fff;text-align:center}
    img{width:96px;height:96px} h1{margin:14px 0 6px;font-size:36px} p{margin:0;font-size:17px;opacity:.9;padding:0 24px}</style>
    <img src="${b64(icon)}"><h1>PasteScribe</h1><p>${COPY.tile}</p>`);
  await t.waitForTimeout(200);
  await t.screenshot({ path: path.join(out, 'promo-tile-440x280.png') });

  await browser.close();
  console.log('OK ->', out);
})().catch((e) => { console.error(e); process.exit(1); });
