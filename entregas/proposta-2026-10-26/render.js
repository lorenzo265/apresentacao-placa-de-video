// Renderiza um HTML em PDF A4 com rodapé numerado, usando o Chromium do Playwright.
// Uso: node render.js entrada.html saida.pdf "texto do rodapé"
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const [, , input, output, footer = ''] = process.argv;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(input), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  await page.pdf({
    path: output,
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate:
      '<div style="width:100%;font-family:Arial,Helvetica,sans-serif;font-size:9pt;color:#000;' +
      'padding:0 18mm;display:flex;justify-content:space-between;">' +
      `<span>${esc(footer)}</span>` +
      '<span>Página <span class="pageNumber"></span> de <span class="totalPages"></span></span></div>',
    margin: { top: '16mm', bottom: '18mm', left: '18mm', right: '18mm' },
  });
  await browser.close();
})();
