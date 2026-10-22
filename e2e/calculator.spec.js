// E2E testy frontendu V2 cez prehliadač (krok 11 docs/v2/05-plan.md, 02a-tiers.md 1.7).
// Každý test uvádza ID požiadavky. Backend: STORAGE=memory (playwright.config.js).
const { test, expect } = require('@playwright/test');

const field = (page, name) => page.locator(`[data-field="${name}"]`);
const error = (page, name) => page.locator(`[data-error="${name}"]`);
const result = (page, key) => page.locator(`[data-result="${key}"]`);
const saveButton = (page) => page.locator('[data-action="save"]');
const saveStatus = (page) => page.locator('[data-status="save"]');
const listStatus = (page) => page.locator('[data-status="list"]');
const listRows = (page) => page.locator('[data-list="calculations"] tr');
const isCalculate = (req) => req.method() === 'POST' && new URL(req.url()).pathname === '/api/calculate';

async function open(page) {
  await page.goto('/');
  await expect(result(page, 'monthly')).toHaveText('477,42 €');  // AD-08 V1: predvyplnené hodnoty
}

async function fillExtra(page, month, amount, mode = 'shorter_term') {
  await page.locator(`input[name="mode"][value="${mode}"]`).check();
  await field(page, 'extraMonth').fill(month);
  await field(page, 'extraAmount').fill(amount);
}

// --- FR-01 až FR-05, NFR-V2-01, AD-V2-02, R-V2-04 ---------------------------------------------

test('FR-01: predvyplnené hodnoty → 477,42 €', async ({ page }) => {
  await open(page);
  await expect(result(page, 'total')).toHaveText('171 869,51 €');
  await expect(result(page, 'interest')).toHaveText('71 869,51 €');
  await expect(page.locator('[data-extra-mode]')).toBeHidden();
});

test('FR-05: 2 chyby naraz, výsledky skryté', async ({ page }) => {
  await open(page);
  await field(page, 'rate').fill('');
  await field(page, 'years').fill('2,5');
  await expect(error(page, 'rate')).toHaveText('Ročná úroková sadzba musí byť od 0 do 20 %.');
  await expect(error(page, 'years')).toHaveText('Doba splácania musí byť od 1 do 30 rokov.');
  await expect(page.locator('[data-results]')).toBeHidden();
});

test('NFR-V2-04: aria-invalid a aria-describedby', async ({ page }) => {
  await open(page);
  await field(page, 'amount').fill('999');
  await expect(field(page, 'amount')).toHaveAttribute('aria-invalid', 'true');
  await expect(field(page, 'amount')).toHaveAttribute('aria-describedby', 'amount-error');
  await expect(page.locator('#amount-error')).toHaveText('Výška úveru musí byť od 1 000 do 1 000 000 €.');
  await field(page, 'amount').fill('100 000');
  await expect(field(page, 'amount')).not.toHaveAttribute('aria-invalid', /.*/);
  await expect(field(page, 'amount')).not.toHaveAttribute('aria-describedby', /.*/);
});

test('NFR-V2-01: výsledok do 500 ms po poslednej zmene', async ({ page }) => {
  await open(page);
  const start = Date.now();
  await field(page, 'amount').fill('150 000');
  await expect(result(page, 'monthly')).toHaveText('716,12 €', { timeout: 2000 });
  expect(Date.now() - start).toBeLessThanOrEqual(500);
});

test('AD-V2-02: 6 rýchlych zmien = 1 požiadavka', async ({ page }) => {
  await open(page);
  const requests = [];
  page.on('request', (req) => { if (isCalculate(req)) requests.push(req.postDataJSON()); });
  await field(page, 'amount').fill('');
  await field(page, 'amount').pressSequentially('150000', { delay: 50 });  // 50 ms < 300 ms debounce
  await expect(result(page, 'monthly')).toHaveText('716,12 €');
  await page.waitForTimeout(600);
  expect(requests).toHaveLength(1);
  expect(requests[0].amount).toBe('150000');  // API-R3: surový text
});

test('R-V2-04: staršia odpoveď sa zahodí', async ({ page }) => {
  await open(page);
  await page.route('**/api/calculate', async (route) => {
    if (route.request().postDataJSON().amount === '200 000') await new Promise((r) => setTimeout(r, 1500));
    await route.continue();
  });
  await field(page, 'amount').fill('200 000');
  await page.waitForTimeout(400);                 // požiadavka na 200 000 je odoslaná a čaká 1,5 s
  await field(page, 'amount').fill('300 000');
  await expect(result(page, 'monthly')).toHaveText('1 432,25 €');
  await page.waitForTimeout(1500);                // pomalá odpoveď na 200 000 prišla neskôr
  await expect(result(page, 'monthly')).toHaveText('1 432,25 €');
});

test('API-R7: timeout 5 s → stav unavailable', async ({ page }) => {
  await open(page);
  await page.route('**/api/calculate', async (route) => {
    await new Promise((r) => setTimeout(r, 6000));
    await route.continue().catch(() => {});        // klient už požiadavku zrušil
  });
  const start = Date.now();
  await field(page, 'amount').fill('150 000');
  const banner = page.locator('[data-unavailable]');
  await expect(banner).toBeVisible({ timeout: 7000 });
  expect(Date.now() - start).toBeGreaterThanOrEqual(5000);
  await expect(banner).toContainText('Výpočet je dočasne nedostupný. Skúste to znova.');
  await expect(page.locator('[data-results]')).toBeHidden();
  await expect(saveButton(page)).toBeDisabled();
});

test('OQ-V2-04: Skúsiť znova obnoví výpočet', async ({ page }) => {
  await open(page);
  await page.route('**/api/calculate', (route) => route.abort('failed'));  // chyba siete
  await field(page, 'amount').fill('150 000');
  await expect(page.locator('[data-unavailable]')).toBeVisible();
  await page.unroute('**/api/calculate');
  await page.locator('[data-action="retry"]').click();
  await expect(result(page, 'monthly')).toHaveText('716,12 €');
  await expect(page.locator('[data-unavailable]')).toBeHidden();
});

// --- FR-06 až FR-09 -----------------------------------------------------------------------------

test('FR-06: riadok 1 DR-10 (kratšia doba)', async ({ page }) => {
  await open(page);
  await fillExtra(page, '12', '10 000');
  await expect(result(page, 'extra.payments')).toHaveText('300 mesiacov (o 60 mesiacov menej)');
  await expect(result(page, 'extra.lastPayment')).toHaveText('325,32 €');
  await expect(result(page, 'extra.total')).toHaveText('153 072,49 €');
  await expect(result(page, 'extra.interest')).toHaveText('53 072,49 €');
  await expect(result(page, 'extra.interestSaved')).toHaveText('18 797,02 €');
  await expect(result(page, 'extra.newMonthly')).toBeHidden();
  await expect(result(page, 'monthly')).toHaveText('477,42 €');
});

test('FR-07: riadok 1 DR-10 (nižšia splátka)', async ({ page }) => {
  await open(page);
  await fillExtra(page, '12', '10 000');
  await expect(result(page, 'extra.payments')).toBeVisible();
  await page.locator('input[name="mode"][value="lower_payment"]').check();  // zmena režimu prepočíta
  await expect(result(page, 'extra.newMonthly')).toHaveText('428,82 €');
  await expect(result(page, 'extra.total')).toHaveText('164 957,63 €');
  await expect(result(page, 'extra.interest')).toHaveText('64 957,63 €');
  await expect(result(page, 'extra.interestSaved')).toHaveText('6 911,88 €');
  await expect(result(page, 'extra.payments')).toBeHidden();
  await expect(result(page, 'extra.lastPayment')).toBeHidden();
});

test('FR-09: iba IN-04 vyplnený → správa pri IN-05', async ({ page }) => {
  await open(page);
  await field(page, 'extraMonth').fill('12');
  await expect(error(page, 'extraAmount'))
    .toHaveText('Mimoriadna splátka musí byť od 100 € a menej ako zostatok úveru 98 238,96 €.');
  await expect(error(page, 'extraMonth')).toBeHidden();
  await expect(page.locator('[data-results]')).toBeHidden();
  await field(page, 'extraMonth').fill('');        // obe prázdne = bez mimoriadnej splátky, nie chyba
  await expect(result(page, 'monthly')).toHaveText('477,42 €');
  await expect(error(page, 'extraAmount')).toBeHidden();
});

// --- FR-10, FR-11 -------------------------------------------------------------------------------

test('FR-10: 1 klik = 1 záznam (2 rýchle kliky → 1 uloženie)', async ({ page }) => {
  await open(page);
  await fillExtra(page, '12', '10 000');
  await expect(result(page, 'extra.payments')).toBeVisible();
  await expect(saveButton(page)).toBeEnabled();
  const posts = [];
  page.on('request', (req) => {
    if (req.method() === 'POST' && new URL(req.url()).pathname === '/api/calculations') posts.push(req);
  });
  await saveButton(page).evaluate((button) => { button.click(); button.click(); });
  await expect(saveStatus(page)).toHaveText('Výpočet bol uložený.');
  expect(posts).toHaveLength(1);
  await expect(listRows(page).first().locator('[data-col="extra"]'))
    .toHaveText('10 000,00 € v 12. mesiaci, kratšia doba');   // nový záznam je v zozname prvý
  await expect(listRows(page).first().locator('[data-col="monthly"]')).toHaveText('477,42 €');
});

test('FR-10: tlačidlo neaktívne pri chybe', async ({ page }) => {
  await open(page);
  await expect(saveButton(page)).toBeEnabled();
  await field(page, 'amount').fill('abc');
  await expect(error(page, 'amount')).toBeVisible();
  await expect(saveButton(page)).toBeDisabled();
  await field(page, 'amount').fill('100 000');
  await expect(saveButton(page)).toBeEnabled();
});

test('FR-10: 503 → správa, formulár zostane', async ({ page }) => {
  await open(page);
  await page.route('**/api/calculations', (route) => (route.request().method() === 'POST'
    ? route.fulfill({ status: 503, json: { error: 'storage_unavailable' } })
    : route.continue()));
  await field(page, 'extraMonth').fill('12');
  await field(page, 'extraAmount').fill('10 000');
  await expect(result(page, 'extra.payments')).toBeVisible();
  await saveButton(page).click();
  await expect(saveStatus(page)).toHaveText('Výpočet sa nepodarilo uložiť. Skúste to znova.');
  await expect(field(page, 'amount')).toHaveValue('100 000');
  await expect(field(page, 'extraMonth')).toHaveValue('12');
  await expect(field(page, 'extraAmount')).toHaveValue('10 000');
  await expect(saveButton(page)).toBeEnabled();     // dá sa skúsiť znova
});

test('FR-10: chyba siete pri uložení → správa', async ({ page }) => {
  await open(page);
  await page.route('**/api/calculations', (route) => (route.request().method() === 'POST'
    ? route.abort('failed') : route.continue()));
  await saveButton(page).click();
  await expect(saveStatus(page)).toHaveText('Výpočet sa nepodarilo uložiť. Skúste to znova.');
});

test('FR-11: prázdny zoznam → správa', async ({ page }) => {
  await page.route('**/api/calculations', (route) => route.fulfill({ json: { items: [] } }));
  await open(page);
  await expect(listStatus(page)).toHaveText('Zatiaľ nie sú uložené žiadne výpočty.');
  await expect(page.locator('[data-table]')).toBeHidden();
});

test('FR-11: chyba načítania → správa, kalkulačka funguje ďalej', async ({ page }) => {
  await page.route('**/api/calculations', (route) => route.fulfill({ status: 503, json: { error: 'storage_unavailable' } }));
  await open(page);
  await expect(listStatus(page)).toHaveText('Uložené výpočty sa nepodarilo načítať.');
  await field(page, 'amount').fill('150 000');
  await expect(result(page, 'monthly')).toHaveText('716,12 €');
});

test('FR-11: 25 uložení → 20 riadkov', async ({ page, request }) => {
  const ids = [];
  for (let years = 1; years <= 25; years += 1) {
    const response = await request.post('/api/calculations', {
      data: { amount: '100 000', rate: '4', years: String(years), extra: { month: '', amount: '', mode: 'shorter_term' } },
    });
    expect(response.status()).toBe(201);
    ids.push((await response.json()).id);
  }
  await open(page);
  await expect(listRows(page)).toHaveCount(20);
  const shown = await listRows(page).evaluateAll((rows) => rows.map((row) => row.dataset.id));
  expect(shown).toEqual(ids.slice(-20).reverse());   // od najnovšieho, 5 najstarších chýba
  await expect(listRows(page).first().locator('[data-col="years"]')).toHaveText('25 rokov');
  await expect(listRows(page).first().locator('[data-col="rate"]')).toHaveText('4,00 %');
  await expect(listRows(page).first().locator('[data-col="createdAt"]')).toHaveText(/^\d{1,2}\. \d{1,2}\. \d{4} \d{2}:\d{2}$/);
});
