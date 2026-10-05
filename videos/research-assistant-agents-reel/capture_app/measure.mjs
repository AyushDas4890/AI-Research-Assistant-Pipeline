// Replays the same run as states.mjs and records element geometry (CSS px, viewport 1600x1000) for the film's crops.
// Also takes s20_done_tall.png: the finished page with a taller viewport, so the report below the fold is captured
// (Streamlit scrolls inside its main section, so a fullPage screenshot stops at the viewport).
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(path.join(process.cwd(), 'package.json'));
const { chromium } = require('playwright');

const OUT = 'assets/cap';
const TOPIC = 'Future of AI coding agents and multimodal models';
const STEP_MS = Number(process.env.CAPTURE_STEP_MS || 4000);
fs.rmSync('capture_app/.saved_session', { force: true });

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2 });
const page = await ctx.newPage();
const geo = {};
const measure = async (name) => {
  geo[name] = await page.evaluate(() => {
    const r = (el) => { if (!el) return null; const b = el.getBoundingClientRect(); return { x: b.x, y: b.y, w: b.width, h: b.height }; };
    const lines = (el) => {
      if (!el) return [];
      const rg = document.createRange(); rg.selectNodeContents(el);
      return [...rg.getClientRects()].filter((b) => b.width > 2).map((b) => ({ x: b.x, y: b.y, w: b.width, h: b.height }));
    };
    const main = document.querySelector('[data-testid="stMain"]') || document.querySelector('section.main');
    const side = document.querySelector('[data-testid="stSidebar"]');
    const mainCode = main && main.querySelector('[data-testid="stCode"] code');
    const sideCode = side && side.querySelector('[data-testid="stCode"] code');
    const byText = (root, sel, t) => root && [...root.querySelectorAll(sel)].find((e) => e.innerText && e.innerText.includes(t));
    const caption = byText(main, '[data-testid="stCaptionContainer"]', 'Total run time');
    const status = byText(main, '[data-testid="stExpander"]', 'Research complete') || byText(main, '[data-testid="stExpander"]', '—') || byText(main, '[data-testid="stExpander"]', 'Running');
    return {
      h1: r(main && main.querySelector('h1')), h1text: r(main && main.querySelector('h1 span') || main && main.querySelector('h1')),
      caption: r(byText(main, 'p', 'Multi-Agent Pipeline')),
      label: r(byText(main, 'label', 'Research topic')), input: r(main && main.querySelector('input')),
      button: r(byText(main, 'button', 'Run Research')), status: r(status),
      logBlock: r(mainCode && mainCode.closest('[data-testid="stCode"]')), logLines: lines(mainCode),
      runTime: r(caption),
      reportH1: r(main && [...main.querySelectorAll('h1')][1]), reportH2: r(main && main.querySelector('h2')),
      sideCode: r(sideCode), sideLines: lines(sideCode),
      pastSessions: r(byText(side, 'h3', 'Past Sessions')), session: r(byText(side, 'button', 'Future of AI')),
      noPast: r(byText(side, 'p', 'No past research')),
      typed: (() => { const i = main && main.querySelector('input'); if (!i || !i.value) return null;
        const c = document.createElement('canvas').getContext('2d'); const cs = getComputedStyle(i);
        c.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
        return { value: i.value, textWidth: c.measureText(i.value).width, paddingLeft: parseFloat(cs.paddingLeft), font: c.font }; })(),
    };
  });
  console.log('measured', name);
};

await page.goto('http://localhost:8501/', { waitUntil: 'domcontentloaded' });
await page.waitForSelector('input[aria-label="Research topic"]', { timeout: 60000 });
await page.waitForTimeout(2500);
await measure('idle');
await page.click('input[aria-label="Research topic"]');
await page.keyboard.type(TOPIC, { delay: 10 });
await page.keyboard.press('Enter');
await page.waitForTimeout(1500);
await measure('typed');
await page.click('button:has-text("Run Research")');
await page.waitForTimeout(1500);
await measure('run_start');
for (let i = 0; i < 8; i++) { await page.waitForTimeout(STEP_MS); await measure(`step${i + 1}`); }
await page.waitForTimeout(3000);
await measure('done');
await page.setViewportSize({ width: 1600, height: 2600 });
await page.waitForTimeout(1500);
await page.screenshot({ path: `${OUT}/s20_done_tall.png` });
await measure('done_tall');
await page.setViewportSize({ width: 1600, height: 1000 });
await page.goto('http://localhost:8501/', { waitUntil: 'domcontentloaded' });
await page.waitForSelector('input[aria-label="Research topic"]', { timeout: 60000 });
await page.waitForTimeout(2500);
await measure('memory');
await page.click('button:has-text("Future of AI")');
await page.waitForTimeout(2000);
await measure('memory_loaded');
fs.writeFileSync(`${OUT}/geometry.json`, JSON.stringify(geo, null, 1));
await browser.close();
