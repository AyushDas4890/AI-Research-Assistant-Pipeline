// Drive the local app.py (replay stubs) through one research run and screenshot each real UI state.
// Run from the project root while `streamlit run capture_app/app.py` serves :8501.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(path.join(process.cwd(), 'package.json'));
const { chromium } = require('playwright');

const OUT = 'assets/cap';
const TOPIC = 'Future of AI coding agents and multimodal models';
const STEP_MS = Number(process.env.CAPTURE_STEP_MS || 4000);
fs.rmSync('capture_app/.saved_session', { force: true });
fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2 });
const page = await ctx.newPage();
const rects = {};
const rectOf = async (sel) => page.locator(sel).first().boundingBox().catch(() => null);
const shot = async (name, sels = {}) => {
  await page.screenshot({ path: `${OUT}/${name}.png` });
  rects[name] = {};
  for (const [k, s] of Object.entries(sels)) rects[name][k] = await rectOf(s);
  console.log('shot', name);
};
const SEL = {
  input: 'input[aria-label="Research topic"]',
  button: 'button:has-text("Run Research")',
  status: '[data-testid="stExpander"]',
  code: '[data-testid="stCode"]',
  title: 'h1',
};

await page.goto('http://localhost:8501/', { waitUntil: 'domcontentloaded' });
await page.waitForSelector(SEL.input, { timeout: 60000 });
await page.waitForTimeout(2500);
await shot('s00_idle', { input: SEL.input, button: SEL.button, title: SEL.title });

await page.click(SEL.input);
await page.waitForTimeout(400);
await shot('s01_focus', { input: SEL.input, button: SEL.button });
await page.keyboard.type(TOPIC, { delay: 20 });
await page.keyboard.press('Enter');
await page.waitForTimeout(1500);
await page.mouse.move(1200, 700);
await page.waitForTimeout(500);
await shot('s02_typed', { input: SEL.input, button: SEL.button });
await page.hover(SEL.button);
await page.waitForTimeout(500);
await shot('s03_hover', { input: SEL.input, button: SEL.button });

await page.click(SEL.button);
await page.mouse.move(1200, 900);
await page.waitForTimeout(1500);
await shot('s04_run_start', { status: SEL.status, code: SEL.code });
// one shot in the middle of every replayed node (8 updates, STEP_MS apart)
for (let i = 0; i < 8; i++) {
  await page.waitForTimeout(STEP_MS);
  await shot(`s${String(5 + i).padStart(2, '0')}_step${i + 1}`, { status: SEL.status, code: SEL.code });
}
await page.waitForTimeout(3000);
await shot('s13_done_top', { status: SEL.status });
await page.screenshot({ path: `${OUT}/s14_done_full.png`, fullPage: true });
console.log('shot s14_done_full');
// expand the agent log
const log = page.locator('[data-testid="stExpander"] summary:has-text("Agent log")');
if (await log.count()) { await log.click(); await page.waitForTimeout(800); }
await shot('s15_log_open', { status: SEL.status });
await page.screenshot({ path: `${OUT}/s16_log_full.png`, fullPage: true });
// memory: a fresh page load lists the saved session in the sidebar; clicking it reloads the report
await page.goto('http://localhost:8501/', { waitUntil: 'domcontentloaded' });
await page.waitForSelector(SEL.input, { timeout: 60000 });
await page.waitForTimeout(2500);
const sess = 'button:has-text("Future of AI coding agents")';
await shot('s17_memory', { session: sess, sidebar: '[data-testid="stSidebar"]' });
await page.hover(sess); await page.waitForTimeout(400);
await shot('s18_memory_hover', { session: sess });
await page.click(sess); await page.waitForTimeout(2000);
await shot('s19_memory_loaded', { session: sess });
fs.writeFileSync(`${OUT}/rects.json`, JSON.stringify(rects, null, 2));
await browser.close();
