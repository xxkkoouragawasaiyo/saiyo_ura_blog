// 使い方: node render.js <出力フォルダ> [ファイル名...]  src/*.html を .canvas の大きさで撮影（1.5倍＝幅1800px）
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const out = process.argv[2];
  const names = process.argv.slice(3).length ? process.argv.slice(3) : fs.readdirSync(__dirname).filter(f => f.endsWith('.html'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1300, height: 1400 }, deviceScaleFactor: 1.5 });
  for (const n of names) {
    await page.goto('file://' + path.join(__dirname, n), { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.locator('.canvas').screenshot({ path: path.join(out, n.replace(/\.html$/, '.png')) });
    console.log('rendered', n);
  }
  await browser.close();
})();
