# 02 – Architektúra

## 1. Prehľad

Kalkulačka je statická webová stránka bez servera. Celý výpočet beží v prehliadači.
Aplikácia je rozdelená na malé moduly s jednou zodpovednosťou. Závislosti smerujú iba jedným smerom:
UI → aplikačná vrstva → doména, vstupy a formátovanie.
Prehliadač (DOM) používajú iba dva moduly (M8, M9). Ostatné moduly sú čisté funkcie, ktoré sa dajú
testovať v Node.js bez prehliadača.

## 2. Technológie

| Oblasť | Voľba | Dôvod |
|--------|-------|-------|
| Jazyk | JavaScript (ES2022), natívne ES moduly | Žiadny build krok, 0 závislostí za behu. |
| UI | Čisté HTML + CSS + DOM API, bez frameworku | Formulár s 3 vstupmi a 3 výstupmi framework nepotrebuje. |
| Testy | Vstavaný test runner Node.js (`node --test`, Node ≥ 20) | 0 závislostí, testuje čisté moduly priamo. |
| Spustenie | Ľubovoľný statický server, napr. `python -m http.server` | ES moduly sa nenačítajú cez `file://`. |

## 3. Nefunkčné požiadavky

Tieto požiadavky dopĺňajú `01-functional.md` a vyplývajú z rozhodnutí v tejto architektúre.

| ID | Požiadavka |
|----|------------|
| NFR-01 | Výsledky (alebo chybové správy) sa zobrazia do 100 ms po zmene ľubovoľného vstupu. |
| NFR-02 | Aplikácia nemá žiadne závislosti za behu (0 balíkov z npm, 0 načítaní z CDN). |
| NFR-03 | Všetky moduly okrem M8 a M9 sa dajú spustiť v Node.js bez DOM (0 odkazov na `window`/`document`). |
| NFR-04 | Každý vstup má priradený `<label>`. Neplatný vstup má `aria-invalid="true"` a jeho chybová správa je s ním prepojená cez `aria-describedby`. |

## 4. Štruktúra projektu

```
index.html                 statický markup: formulár s 3 vstupmi, blok výsledkov
styles.css
package.json               iba "type": "module" a skript "test": "node --test"
src/
  main.js                  M9 – vstupný bod, prepojenie modulov
  app/calculator.js        M7 – orchestrácia jedného výpočtu
  domain/mortgage.js       M3 – výpočet splátky a súm
  domain/rounding.js       M4 – zaokrúhľovanie polovica nahor
  input/parse.js           M1 – prevod textu na číslo
  input/validate.js        M2 – hranice a validácia vstupov
  format/money.js          M5 – slovenský formát sumy v €
  ui/messages.js           M6 – texty chybových správ
  ui/view.js               M8 – čítanie formulára a vykreslenie
tests/
  input/parse.test.js, input/validate.test.js, domain/mortgage.test.js,
  domain/rounding.test.js, format/money.test.js, ui/messages.test.js,
  app/calculator.test.js   (zrkadlí `src/`, každý test uvádza ID požiadavky)
```

## 5. Závislosti modulov

```
M9 main.js ──► M8 ui/view.js
     └──────► M7 app/calculator.js ──► M2 input/validate.js ──► M1 input/parse.js
                                   ──► M3 domain/mortgage.js
                                   ──► M5 format/money.js ──► M4 domain/rounding.js
                                   ──► M6 ui/messages.js ──► M2 (LIMITS)
```

Pravidlá:
- Doména (M3, M4) nezávisí od ničoho iného.
- Nič okrem M9 neimportuje M8.
- Cyklické závislosti nie sú povolené.

## 6. Moduly

### M1 `src/input/parse.js` – prevod textu na číslo
- **Zodpovednosť:** prevedie surový text zo vstupného poľa na číslo podľa pravidiel z časti 3 v `01-functional.md`.
  - Orezá medzery na začiatku a na konci.
  - Odstráni medzery medzi číslicami (`150 000` → `150000`).
  - Ako desatinný oddeľovač akceptuje `,` aj `.`.
  - Vráti aj počet desatinných miest, aby M2 mohol overiť krok.
  - Prijme iba tvar `-?číslice[,|.číslice]`. Napríklad `1e3`, `0x10` alebo `1,2,3` vráti ako `'nan'`.
- **Rozhranie:**
  ```js
  parseNumber(raw: string)
    → { ok: true, value: number, decimals: number }
    | { ok: false, reason: 'empty' | 'nan' }
  ```
- **Implementuje:** IN-01, IN-02, IN-03 (pravidlá zápisu čísla), FR-05 (podmienky „je prázdny“ a „nie je číslo“).

### M2 `src/input/validate.js` – hranice a validácia
- **Zodpovednosť:**
  - Je jediným miestom, kde sú hranice vstupov.
  - Pre každé pole overí podmienky v tomto poradí: prázdne → nie je číslo → mimo rozsahu → priveľa desatinných miest.
  - Validuje všetky tri polia naraz, aby sa zobrazili všetky chyby, nielen prvá (FR-05, príklad 3).
- **Rozhranie:**
  ```js
  LIMITS = {
    amount: { min: 1000, max: 1000000, decimals: 2 },   // IN-01
    rate:   { min: 0,    max: 20,      decimals: 2 },   // IN-02
    years:  { min: 1,    max: 30,      decimals: 0 },   // IN-03
  }
  validateInputs(raw: { amount: string, rate: string, years: string })
    → { valid: true,  values: { amount: number, rate: number, years: number } }
    | { valid: false, errors: { [field]: 'empty' | 'nan' | 'range' | 'step' } }
  ```
- **Implementuje:** IN-01, IN-02, IN-03, FR-05 (zistenie neplatného vstupu).

### M3 `src/domain/mortgage.js` – výpočet
- **Zodpovednosť:**
  - Vypočíta mesačnú splátku, celkovú sumu a celkový úrok z platných čísel.
  - Pre sadzbu > 0 použije anuitný vzorec, pre sadzbu = 0 jednoduché delenie.
  - Nič nezaokrúhľuje.
  - Predpokladá platné vstupy, validácia patrí M2.
- **Rozhranie:**
  ```js
  calculateMortgage({ principal: number, annualRatePct: number, years: number })
    → { monthlyPayment: number, totalPaid: number, totalInterest: number }
  // i = annualRatePct / 100 / 12, n = years * 12
  // monthlyPayment = i > 0 ? P·i / (1 − (1 + i)^−n) : P / n
  // totalPaid = monthlyPayment · n, totalInterest = totalPaid − P   (všetko nezaokrúhlené)
  ```
- **Implementuje:** FR-01, FR-02, FR-03, DR-01, DR-02, DR-03 (žiadne zaokrúhľovanie medzivýsledkov).

### M4 `src/domain/rounding.js` – zaokrúhľovanie
- **Zodpovednosť:**
  - Zaokrúhli číslo na daný počet desatinných miest matematicky (polovica nahor).
  - Musí byť odolný voči chybám binárnej aritmetiky: `1.005` → `1.01`, nie `1.00`. Rieši sa posunom exponentu cez reťazec (`Number(value + 'e2')`), nie násobením `value * 100`.
  - Hodnoty s |value| < 1e-6 vráti ako `0`. Pri sadzbe 0 % môže byť `M × n − P` napr. `±1.8e-12`, nie presne 0. Overené: pri 961 kombináciách P a doby splácania. Bez tohto pravidla by posun exponentu dal `NaN` (`"1.8e-12e2"`), prípadne by sa zobrazilo `-0,00 €` namiesto `0,00 €` (FR-03).
  - Nikdy nevráti `-0`.
- **Rozhranie:**
  ```js
  roundHalfUp(value: number, decimals = 2) → number
  ```
- **Implementuje:** DR-03.

### M5 `src/format/money.js` – formát sumy
- **Zodpovednosť:**
  - Naformátuje sumu v slovenskom formáte: medzera ako oddeľovač tisícov, desatinná čiarka, presne 2 desatinné miesta a ` €` za číslom.
  - Pred formátovaním zaokrúhli cez M4.
  - Formátuje sa ručne, nie cez `Intl.NumberFormat`. Ten pre `sk-SK` vkladá nezalomiteľné medzery (U+00A0 / U+202F) a výstup by sa nezhodoval s FR-04.
  - Zalomenie riadku vo výsledku zabráni CSS (`white-space: nowrap`).
- **Rozhranie:**
  ```js
  formatMoney(value: number) → string           // 6015667.2705 → "6 015 667,27 €"
  formatNumber(value: number, decimals) → string // 1000000, 0 → "1 000" (pre texty chýb v M6)
  ```
- **Implementuje:** FR-04, DR-03 (zaokrúhlenie zobrazených výsledkov).

### M6 `src/ui/messages.js` – chybové správy
- **Zodpovednosť:**
  - Zostaví slovenskú chybovú správu s povoleným rozsahom z `LIMITS` (M2) a `formatNumber` (M5).
  - Pre všetky typy chýb jedného poľa vráti tú istú správu, lebo FR-05 vyžaduje iba povolený rozsah.
  - Texty sú na jednom mieste, aby sa dali skontrolovať oproti FR-05.
- **Rozhranie:**
  ```js
  errorMessage(field: 'amount' | 'rate' | 'years', code) → string
  // amount → „Výška úveru musí byť od 1 000 do 1 000 000 €.“
  // rate   → „Ročná úroková sadzba musí byť od 0 do 20 %.“
  // years  → „Doba splácania musí byť od 1 do 30 rokov.“
  ```
- **Implementuje:** FR-05 (obsah chybovej správy).

### M7 `src/app/calculator.js` – orchestrácia
- **Zodpovednosť:**
  - Spracuje jeden výpočet od surových textov po hotové reťazce: validácia → výpočet → formátovanie.
  - Ak je niektorý vstup neplatný, nevráti žiadne výsledky.
  - Nepoužíva DOM, takže celý tok FR-01 až FR-05 sa dá otestovať v Node.js na referenčných príkladoch z DR-04.
- **Rozhranie:**
  ```js
  runCalculation(raw: { amount: string, rate: string, years: string })
    → { status: 'ok',      results: { monthly: string, total: string, interest: string } }
    | { status: 'invalid', errors:  { [field]: string } }   // texty z M6
  ```
- **Implementuje:** FR-01, FR-02, FR-03, FR-04, FR-05 (end-to-end), DR-04 (akceptačné testy).

### M8 `src/ui/view.js` – zobrazenie
- **Zodpovednosť:**
  - Prečíta hodnoty z formulára ako surové texty, bez `valueAsNumber`. Polia sú `type="text"` s `inputmode="decimal"`, aby prehliadač neodmietal čiarku.
  - Pri stave `ok` zobrazí tri výsledky a odstráni chyby.
  - Pri stave `invalid` skryje celý blok výsledkov, pri každom neplatnom poli zobrazí správu a nastaví `aria-invalid` a `aria-describedby`.
  - Pri každej udalosti `input` zavolá spätné volanie.
- **Rozhranie:**
  ```js
  readForm(root: HTMLElement) → { amount: string, rate: string, years: string }
  render(root: HTMLElement, result: ReturnType<typeof runCalculation>) → void
  bind(root: HTMLElement, onChange: () => void) → void
  ```
- **Implementuje:** FR-05 (žiadne výsledky pri chybe), OQ-01, NFR-01, NFR-04.

### M9 `src/main.js` + `index.html` + `styles.css` – vstupný bod
- **Zodpovednosť:**
  - Pri načítaní stránky prepojí moduly a vykoná prvý výpočet.
  - `index.html` obsahuje formulár s tromi vstupmi a ich `<label>`, blok výsledkov a prvky pre chybové správy.
  - Polia sú predvyplnené referenčným príkladom 100 000 / 4 / 30, aby sa výsledok zobrazil hneď a prázdny formulár nezobrazil po načítaní tri chyby.
- **Rozhranie:**
  ```js
  const update = () => render(root, runCalculation(readForm(root)));
  bind(root, update);
  update();
  ```
- **Implementuje:** OQ-01, NFR-01, NFR-04 (markup).

## 7. Tok dát

```
používateľ píše → udalosť `input` (M8.bind)
  → readForm: { amount: "150 000", rate: "3,5", years: "25" }   (surové texty)
  → runCalculation (M7)
      → validateInputs (M2) → parseNumber (M1) pre každé pole
      → neplatné?  → errorMessage (M6) → { status: 'invalid', errors }
      → platné     → calculateMortgage (M3, nezaokrúhlené)
                   → formatMoney (M5 → M4 zaokrúhlenie) → { status: 'ok', results }
  → render (M8): výsledky, alebo chyby a skrytie výsledkov
```

Surové texty sa na čísla prevádzajú iba v M1. Zaokrúhľuje sa iba v M5 (cez M4), tesne pred zobrazením.

## 8. Rozhodnutia a kompromisy

| # | Rozhodnutie | Dôvod / kompromis |
|---|-------------|-------------------|
| AD-01 | **OQ-01: výsledky sa prepočítajú pri každej zmene vstupu** (udalosť `input`), bez tlačidla „Vypočítať“. | Výpočet je jeden vzorec O(1), trvá rádovo mikrosekundy, takže NFR-01 (≤ 100 ms) je splnená aj bez debounce. Kompromis: počas písania (napr. `99` pri výške úveru) sa na chvíľu zobrazí chyba rozsahu. Je to prijateľné, lebo správa hneď hovorí povolený rozsah. |
| AD-02 | Validuje sa pôvodný text, nie hodnota typu float. | Počet desatinných miest sa z floatu nedá spoľahlivo zistiť. `100,005` musí byť neplatné (IN-01). |
| AD-03 | Vstupy sú `type="text"`, nie `type="number"`. | `type="number"` v niektorých prehliadačoch odmieta čiarku alebo medzery a `value` vráti prázdny reťazec. Porušilo by to pravidlá IN-01 až IN-03. |
| AD-04 | Vlastné formátovanie sumy namiesto `Intl.NumberFormat`. | Presná zhoda s FR-04 (obyčajná medzera) a rovnaký výstup v Node.js aj v prehliadači. |
| AD-05 | Hranice vstupov sú iba v M2 (`LIMITS`) a texty chýb sa z nich generujú. | Zmena hranice v jednom mieste zmení validáciu aj správu. |
| AD-06 | Doména a orchestrácia sú bez DOM (NFR-03). | FR-01 až FR-05 a DR-04 sa dajú overiť rýchlymi testami v Node.js, testy v prehliadači sú potrebné iba pre M8. |
| AD-07 | Žiadny framework ani build (NFR-02). | V1 má 3 vstupy a 3 výstupy. Kompromis: stránku treba spúšťať cez statický server, nie dvojklikom na súbor. |

## 9. Matica sledovateľnosti

| Požiadavka | Moduly |
|------------|--------|
| FR-01 Mesačná splátka | M3, M7 |
| FR-02 Celková zaplatená suma | M3, M7 |
| FR-03 Celkový zaplatený úrok | M3, M7 |
| FR-04 Formát peňažných súm | M5, M7 |
| FR-05 Neplatný vstup | M1, M2, M6, M7, M8 |
| IN-01 Výška úveru | M1, M2 |
| IN-02 Ročná úroková sadzba | M1, M2 |
| IN-03 Doba splácania | M1, M2 |
| DR-01 Anuitný vzorec | M3 |
| DR-02 Sadzba 0 % | M3 |
| DR-03 Zaokrúhľovanie | M3, M4, M5 |
| DR-04 Referenčné príklady | M7 (akceptačné testy) |
| OQ-01 Kedy prepočítať | M8, M9 (AD-01) |
| NFR-01 Odozva ≤ 100 ms | M8, M9 |
| NFR-02 0 závislostí | celý projekt |
| NFR-03 Čisté moduly bez DOM | M1–M7 |
| NFR-04 Prístupnosť formulára | M8, M9 |
