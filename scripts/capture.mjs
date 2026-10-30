#!/usr/bin/env node
/** Capture viewport screenshots and console errors at mobile/tablet/desktop sizes. */
import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

function getArgs(argv) {
  const args = { url: null, out: 'artifacts/screenshots', fullPage: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--url') args.url = argv[++i];
    else if (argv[i] === '--out') args.out = argv[++i];
    else if (argv[i] === '--full-page') args.fullPage = true;
    else throw new Error(`Unknown option: ${argv[i]}`);
  }
  if (!args.url) throw new Error('Usage: node scripts/capture.mjs --url http://localhost:3000 [--out artifacts/screenshots] [--full-page]');
  return args;
}

const sizes = {
  mobile: { width: 390, height: 844 },
  tablet: { width: 820, height: 1180 },
  desktop: { width: 1440, height: 900 }
};
const args = getArgs(process.argv.slice(2));
await fs.mkdir(args.out, { recursive: true });
const browser = await chromium.launch({ headless: true });
const evidence = [];
let failed = false;
try {
  for (const [name, size] of Object.entries(sizes)) {
    const context = await browser.newContext({ viewport: size, deviceScaleFactor: 1, reducedMotion: 'reduce' });
    const page = await context.newPage();
    const runtimeErrors = [];
    page.on('pageerror', (error) => runtimeErrors.push(error.message));
    page.on('console', (message) => { if (message.type() === 'error') runtimeErrors.push(message.text()); });
    try {
      const response = await page.goto(args.url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.evaluate(() => document.fonts.ready);
      await page.waitForLoadState('load', { timeout: 15000 }).catch(() => {});
      // Avoid frozen text caret / motion without altering CSS layout.
      await page.addStyleTag({ content: '*, *::before, *::after { animation-duration: 0s !important; transition-duration: 0s !important; caret-color: transparent !important; }' });
      await page.screenshot({ path: path.join(args.out, `${name}.png`), fullPage: args.fullPage, animations: 'disabled' });
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
      const record = { name, viewport: size, dpr: 1, status: response?.status() ?? null, screenshot: `${name}.png`, horizontalOverflow: overflow, runtimeErrors };
      evidence.push(record);
      if ((response && !response.ok()) || overflow || runtimeErrors.length) failed = true;
      console.log(JSON.stringify(record));
    } catch (error) {
      failed = true;
      evidence.push({ name, viewport: size, error: String(error) });
      console.error(name, error);
    } finally {
      await context.close();
    }
  }
} finally {
  await browser.close();
}
await fs.writeFile(path.join(args.out, 'capture-report.json'), JSON.stringify({ url: args.url, captures: evidence }, null, 2) + '\n');
if (failed) process.exitCode = 1;
