/* Run with PLAYWRIGHT_MODULE pointing to an installed Playwright package if needed. */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

(async () => {
  const root = path.resolve(__dirname, '..');
  const out = path.join(root, 'dist/git-en-preview');
  fs.mkdirSync(out, { recursive: true });
  for (const file of fs.readdirSync(out)) {
    if (/^(\d\d-.*\.png|contact-\d\.jpg|key-pages\.jpg)$/.test(file)) fs.unlinkSync(path.join(out, file));
  }
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true
  });
  const context = await browser.newContext({ viewport: { width: 1600, height: 900 }, offline: true });
  const page = await context.newPage();
  const errors = [], network = [], slides = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => { if (/^https?:/.test(request.url())) network.push(request.url()); });
  await page.goto(pathToFileURL(path.join(root, 'dist/git-en.html')).href);
  await page.waitForFunction(() => !!window.slideshow);
  await page.evaluate(() => document.fonts.ready);
  const count = await page.evaluate(() => slideshow.getSlideCount());
  const names = await page.evaluate(() => slideshow.getSlides().map(s => ({ name: s.properties.name, continued: s.properties.continued, count: s.properties.count })));
  for (let n = 1; n <= count; n++) {
    await page.evaluate(n => slideshow.gotoSlide(n), n);
    await page.waitForTimeout(35);
    const slide = await page.locator('.remark-visible .remark-slide-content').evaluate((s, n) => {
      const bounds = s.closest('.remark-slide-scaler').getBoundingClientRect();
      const scale = bounds.width / 1210;
      const issues = [];
      for (const e of s.querySelectorAll('h1,h2,h3,p,li,table,pre,img,.pr-head,.diff,.review-flow,.remark-code-line')) {
        const r = e.getBoundingClientRect();
        const text = e.textContent.trim().slice(0, 100) || e.getAttribute('alt');
        if (r.right > bounds.right + 2 || r.bottom > bounds.bottom - 76 * scale || r.left < bounds.left - 2) issues.push({ text, kind: 'outside-safe-area' });
        if (e.clientWidth && e.scrollWidth > e.clientWidth + 2) issues.push({ text, kind: 'horizontal-overflow' });
      }
      return {
        n, title: s.querySelector('h1')?.textContent, issues,
        overflow: s.scrollHeight > 682 || s.offsetHeight > 682,
        logo: getComputedStyle(s).backgroundImage.includes('data:image/png'),
        brokenImages: [...s.querySelectorAll('img')].filter(i => !i.complete || !i.naturalWidth).map(i => i.alt)
      };
    }, n);
    slides.push(slide);
    const name = names[n - 1].name || `state-${n}`;
    await page.screenshot({ path: path.join(out, `${String(n).padStart(2,'0')}-${name}.png`) });
  }
  await page.evaluate(() => slideshow.gotoSlide(1));
  await page.keyboard.press('ArrowRight');
  const keyboardNext = await page.evaluate(() => slideshow.getCurrentSlideIndex() === 1);
  await page.keyboard.press('ArrowLeft');
  const keyboardPrevious = await page.evaluate(() => slideshow.getCurrentSlideIndex() === 0);
  await page.keyboard.press('p');
  const presenter = await page.locator('body').evaluate(b => b.classList.contains('remark-presenter-mode'));
  await page.keyboard.press('p');
  await page.keyboard.press('?');
  const help = await page.locator('.remark-help').isVisible();
  await page.keyboard.press('Escape');
  const reveals = [];
  for (let i = 0; i < names.length; i++) {
    if (names[i].continued !== 'true') continue;
    await page.evaluate(n => slideshow.gotoSlide(n), i);
    await page.keyboard.press('ArrowRight');
    reveals.push({ state: i + 1, works: await page.evaluate(i => slideshow.getCurrentSlideIndex() === i && !!document.querySelector('.remark-visible .answer'), i) });
  }
  const sizes = [];
  for (const [width, height] of [[1280,720],[1920,1080],[1440,900]]) {
    await page.setViewportSize({ width, height });
    await page.evaluate(() => window.dispatchEvent(new Event('resize')));
    await page.waitForTimeout(250);
    await page.evaluate(() => slideshow.gotoSlide(8));
    const bounds = await page.locator('.remark-visible .remark-slide-content').boundingBox();
    sizes.push({ width, height, bounds, fits: bounds.x >= -1 && bounds.y >= -1 && bounds.x + bounds.width <= width + 1 && bounds.y + bounds.height <= height + 1 });
  }
  const contentChecks = await page.evaluate(() => ({
    columnsAlignLeft: [...document.querySelectorAll('.remark-slide-content .right')].every(e => getComputedStyle(e).textAlign === 'left'),
    placeholdersVisible: document.querySelector('.command-reference').textContent.includes('git add <file>') && document.querySelector('.command-reference').textContent.includes('git branch <name>'),
    originalFonts: getComputedStyle(document.querySelector('.remark-slide-content')).fontFamily.includes('Droid Serif'),
    originalLogo: [...document.querySelectorAll('.remark-slide-content')].every(s => getComputedStyle(s).backgroundImage.includes('data:image/png'))
  }));
  await page.pdf({ path: path.join(out, 'print-proof.pdf'), preferCSSPageSize: true, printBackground: true });
  const svgPage = await context.newPage();
  const diagrams = [];
  for (const file of fs.readdirSync(path.join(root, 'images/git-course')).filter(f => f.endsWith('.svg'))) {
    await svgPage.goto(pathToFileURL(path.join(root, 'images/git-course', file)).href);
    const issues = await svgPage.evaluate(() => {
      const view = document.documentElement.viewBox.baseVal;
      const labels = [...document.querySelectorAll('text')].filter(e => e.textContent.trim()).map(e => ({ text: e.textContent, box: e.getBBox() }));
      const issues = [];
      for (let i = 0; i < labels.length; i++) {
        const a = labels[i].box;
        if (a.x < 0 || a.y < 0 || a.x + a.width > view.width + 1 || a.y + a.height > view.height + 1) issues.push({ kind: 'outside', text: labels[i].text });
        for (let j = i + 1; j < labels.length; j++) {
          const b = labels[j].box;
          if (Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x) > 1 && Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y) > 1) issues.push({ kind: 'overlap', a: labels[i].text, b: labels[j].text });
        }
      }
      return issues;
    });
    diagrams.push({ file, issues });
  }
  const report = { browser: browser.version(), count, names, slides, errors, network, keyboardNext, keyboardPrevious, presenter, help, reveals, sizes, contentChecks, diagrams };
  fs.writeFileSync(path.join(out,'qa-report.json'), JSON.stringify(report,null,2));
  const escape = text => text.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;');
  let logical = 0, currentName = '', previews = '';
  names.forEach((slide, i) => {
    if (slide.continued !== 'true') { logical++; currentName = slide.name; }
    if (names[i + 1]?.continued === 'true') return;
    const file = `${String(i + 1).padStart(2, '0')}-${slide.name || `state-${i + 1}`}.png`;
    previews += `<article><a href="${file}"><img loading="lazy" src="${file}" alt="${escape(slides[i].title)}"></a><p><span>${String(logical).padStart(2,'0')} ${escape(slides[i].title)}</span><a href="../git-en.html#${currentName}">Open slide</a></p></article>`;
  });
  fs.writeFileSync(path.join(out, 'index.html'), `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Git &amp; GitHub slide previews</title><style>body{font:16px/1.5 Georgia,serif;color:#1a1a1a;background:white;margin:0;padding:40px}header,main{max-width:1500px;margin:auto}h1{font-size:36px}a{color:#2640c0}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:24px;margin-top:32px}article{border:1px solid #ddd;overflow:hidden}img{display:block;width:100%;aspect-ratio:16/9}article p{display:flex;justify-content:space-between;gap:16px;margin:16px;font-size:14px}article p a{white-space:nowrap}</style><header><h1>Git &amp; GitHub</h1><p>${logical} teaching slides. Previews show completed answer reveals.</p><p><a href="../git-en.html">Play the workshop</a> · <a href="print-proof.pdf">Printable handout</a></p></header><main>${previews}</main></html>`);
  console.log(JSON.stringify({ count, issues: slides.filter(s=>s.issues.length || s.overflow || s.brokenImages.length), errors, network, keyboardNext, keyboardPrevious, presenter, help, reveals, sizes, contentChecks, diagramIssues: diagrams.filter(d=>d.issues.length) },null,2));
  await browser.close();
  if (errors.length || network.length || slides.some(s => s.issues.length || s.overflow || s.brokenImages.length) || !keyboardNext || !keyboardPrevious || !presenter || !help || reveals.some(r=>!r.works) || sizes.some(s=>!s.fits) || Object.values(contentChecks).some(v=>!v) || diagrams.some(d=>d.issues.length)) process.exitCode = 1;
})().catch(error=>{ console.error(error); process.exitCode=1; });
