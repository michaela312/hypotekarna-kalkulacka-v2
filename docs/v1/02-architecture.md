# 02 – Architektúra

## Stack

Kalkulačka je statická webová stránka bez servera. Celý výpočet beží v prehliadači.

| Oblasť | Voľba | Dôvod |
|--------|-------|-------|
| Jazyk | JavaScript (ES2022), natívne ES moduly | Žiadny build krok, 0 závislostí za behu (NFR-02). |
| UI | Čisté HTML + CSS + DOM API, bez frameworku | Formulár s 3 vstupmi a 3 výstupmi framework nepotrebuje. |
| Testy | Vstavaný test runner Node.js (`node --test`, Node ≥ 20) | 0 závislostí. Moduly bez DOM sa testujú priamo v Node.js (NFR-03). |
| Spustenie | Ľubovoľný statický server, napr. `python -m http.server` | ES moduly sa nenačítajú cez `file://`. |

Štruktúra projektu:

```
index.html                 M11 – markup formulára a výsledkov
styles.css                 M12 – vzhľad
package.json               iba "type": "module" a skript "test": "node --test"
src/
  main.js                  M10 – vstupný bod, prepojenie modulov
  app/calculator.js        M8  – orchestrácia jedného výpočtu
  domain/mortgage.js       M4  – výpočet splátky a súm
  domain/rounding.js       M5  – zaokrúhľovanie polovica nahor
  input/parse.js           M1  – prevod textu na číslo
  input/limits.js          M2  – hranice vstupov (dáta)
  input/validate.js        M3  – validácia vstupov
  format/money.js          M6  – slovenský formát čísel a súm v €
  text/messages.js         M7  – texty chybových správ
  ui/view.js               M9  – DOM adaptér: čítanie formulára a vykreslenie
tests/                     zrkadlí `src/` pre M1 až M8; každý test uvádza ID požiadavky
```

## Modules

Každý modul má **jednu zodpovednosť**, teda jeden dôvod na zmenu. Ten je uvedený v riadku „Dôvod zmeny“.
Overenie princípu jednej zodpovednosti (SRP) je na konci tejto sekcie.

### M1 `src/input/parse.js` – prevod textu na číslo
- **Zodpovednosť:** prevedie surový text zo vstupného poľa na číslo podľa pravidiel zápisu z časti 3 v `01-functional.md`.
  - Orezá medzery na začiatku a na konci.
  - Odstráni medzery medzi číslicami (`150 000` → `150000`).
  - Ako desatinný oddeľovač akceptuje `,` aj `.`.
  - Vráti aj počet desatinných miest.
  - Prijme iba tvar `-?číslice[,|.číslice]`. Napríklad `1e3`, `0x10` alebo `1,2,3` vráti ako `'nan'`.
  - Nepozná hranice ani polia.
- **Dôvod zmeny:** zmena pravidiel zápisu čísla.
- **Rozhranie:**
  ```js
  parseNumber(raw: string) → ParsedNumber
  ```
- **Implementuje:** IN-01, IN-02, IN-03 (pravidlá zápisu čísla), FR-05 (podmienky „je prázdny“ a „nie je číslo“).

### M2 `src/input/limits.js` – hranice vstupov
- **Zodpovednosť:** je jediným miestom, kde sú hranice a povolený počet desatinných miest každého vstupu. Obsahuje iba dáta, žiadnu logiku.
- **Dôvod zmeny:** zmena tabuľky vstupov v `01-functional.md`.
- **Rozhranie:**
  ```js
  LIMITS: Record<Field, FieldLimits>
  // amount: { min: 1000, max: 1000000, decimals: 2 }   IN-01
  // rate:   { min: 0,    max: 20,      decimals: 2 }   IN-02
  // years:  { min: 1,    max: 30,      decimals: 0 }   IN-03
  ```
- **Implementuje:** IN-01, IN-02, IN-03 (hodnoty hraníc).

### M3 `src/input/validate.js` – validácia vstupov
- **Zodpovednosť:**
  - Pre každé pole overí podmienky v tomto poradí: prázdne → nie je číslo → priveľa desatinných miest → mimo rozsahu. Hranice berie z M2, text parsuje cez M1.
  - Validuje všetky tri polia naraz, aby sa zobrazili všetky chyby, nielen prvá (FR-05, príklad 3).
  - Nevytvára texty správ.
- **Dôvod zmeny:** zmena pravidiel platnosti vstupu (zoznam podmienok v časti 3).
- **Rozhranie:**
  ```js
  validateInputs(raw: RawInput) → ValidationResult
  ```
- **Implementuje:** IN-01, IN-02, IN-03, FR-05 (zistenie neplatného vstupu).

### M4 `src/domain/mortgage.js` – výpočet
- **Zodpovednosť:**
  - Vypočíta mesačnú splátku, celkovú sumu a celkový úrok z platných čísel.
  - Pre sadzbu > 0 použije DR-01, pre sadzbu = 0 použije DR-02.
  - Nič nezaokrúhľuje a nič nevaliduje.
- **Dôvod zmeny:** zmena doménových vzorcov.
- **Rozhranie:**
  ```js
  calculateMortgage(params: LoanParams) → LoanResult
  // i = annualRatePct / 100 / 12, n = years * 12
  // monthlyPayment = i > 0 ? P·i / (1 − (1 + i)^−n) : P / n
  // totalPaid = monthlyPayment · n, totalInterest = totalPaid − P   (všetko nezaokrúhlené)
  ```
- **Implementuje:** FR-01, FR-02, FR-03, DR-01, DR-02, DR-03 (žiadne zaokrúhľovanie medzivýsledkov).

### M5 `src/domain/rounding.js` – zaokrúhľovanie
- **Zodpovednosť:**
  - Zaokrúhli číslo na daný počet desatinných miest matematicky (polovica nahor).
  - Musí byť odolný voči chybám binárnej aritmetiky: `1.005` → `1.01`, nie `1.00`. Rieši sa posunom exponentu cez reťazec (`Number(value + 'e2')`), nie násobením `value * 100`.
  - Hodnoty s |value| < 1e-6 vráti ako `0`. Pri sadzbe 0 % môže byť `M × n − P` napr. `±1.8e-12`, nie presne 0. Overené: pri 961 kombináciách P a doby splácania. Bez tohto pravidla by posun exponentu dal `NaN` (`"1.8e-12e2"`), prípadne by sa zobrazilo `-0,00 €` namiesto `0,00 €` (FR-03).
  - Nikdy nevráti `-0`.
- **Dôvod zmeny:** zmena pravidla zaokrúhľovania (DR-03).
- **Rozhranie:**
  ```js
  roundHalfUp(value: number, decimals = 2) → number
  ```
- **Implementuje:** DR-03.

### M6 `src/format/money.js` – formát čísel a súm
- **Zodpovednosť:**
  - Prevedie číslo na text v slovenskom formáte: medzera ako oddeľovač tisícov, desatinná čiarka, pevný počet desatinných miest.
  - Pri sumách pridá ` €` za číslo. Pred formátovaním zaokrúhli cez M5.
  - Formátuje sa ručne, nie cez `Intl.NumberFormat`. Ten pre `sk-SK` vkladá nezalomiteľné medzery (U+00A0 / U+202F) a výstup by sa nezhodoval s FR-04 (AD-04).
- **Dôvod zmeny:** zmena formátu zobrazenia čísla (FR-04).
- **Rozhranie:**
  ```js
  formatMoney(value: number) → string             // 6015667.2705 → "6 015 667,27 €"
  formatNumber(value: number, decimals) → string  // 1000000, 0 → "1 000"
  ```
- **Implementuje:** FR-04, DR-03 (zaokrúhlenie zobrazených výsledkov).

### M7 `src/text/messages.js` – chybové správy
- **Zodpovednosť:**
  - Zostaví slovenskú chybovú správu s povoleným rozsahom z hraníc (M2) a formátu čísla (M6).
  - Pre všetky kódy chýb jedného poľa vráti tú istú správu, lebo FR-05 vyžaduje iba povolený rozsah.
  - Je bez DOM, preto nie je v `ui/`.
- **Dôvod zmeny:** zmena znenia správ.
- **Rozhranie:**
  ```js
  errorMessage(field: Field, code: ErrorCode) → string
  // amount → „Výška úveru musí byť od 1 000 do 1 000 000 €.“
  // rate   → „Ročná úroková sadzba musí byť od 0 do 20 %.“
  // years  → „Doba splácania musí byť od 1 do 30 rokov.“
  ```
- **Implementuje:** FR-05 (obsah chybovej správy).

### M8 `src/app/calculator.js` – orchestrácia
- **Zodpovednosť:**
  - Riadi jeden výpočet od surových textov po hotové reťazce: M3 → M4 → M6, pri chybe M7.
  - Ak je niektorý vstup neplatný, nevráti žiadne výsledky.
  - Sám nič nepočíta, neformátuje ani nevaliduje, iba volá ostatné moduly v správnom poradí.
- **Dôvod zmeny:** zmena poradia krokov alebo podoby výsledku pre UI.
- **Rozhranie:**
  ```js
  runCalculation(raw: RawInput) → CalculationResult
  ```
- **Implementuje:** FR-01 až FR-05 (end-to-end), DR-04 (akceptačné testy na referenčných príkladoch).

### M9 `src/ui/view.js` – DOM adaptér
- **Zodpovednosť:** prekladá medzi DOM a dátovým modelom. Žiadna logika výpočtu ani validácie.
  - Prečíta hodnoty polí ako surové texty, bez `valueAsNumber`.
  - Pri stave `ok` zobrazí tri výsledky a odstráni chyby.
  - Pri stave `invalid` skryje celý blok výsledkov a pri každom neplatnom poli zobrazí správu a nastaví `aria-invalid` a `aria-describedby`.
  - Pri každej udalosti `input` zavolá spätné volanie.
- **Dôvod zmeny:** zmena štruktúry markupu (M11).
- **Rozhranie:**
  ```js
  readForm(root: HTMLElement) → RawInput
  render(root: HTMLElement, result: CalculationResult) → void
  bind(root: HTMLElement, onChange: () => void) → void
  ```
- **Implementuje:** FR-05 (žiadne výsledky pri chybe), OQ-01, NFR-01, NFR-04.

### M10 `src/main.js` – vstupný bod
- **Zodpovednosť:** pri načítaní stránky prepojí M9 a M8 a vykoná prvý výpočet. Neobsahuje žiadnu inú logiku.
- **Dôvod zmeny:** zmena spôsobu prepojenia modulov.
- **Rozhranie:**
  ```js
  const update = () => render(root, runCalculation(readForm(root)));
  bind(root, update);
  update();
  ```
- **Implementuje:** OQ-01 (AD-01), NFR-01.

### M11 `index.html` – markup
- **Zodpovednosť:**
  - Statická štruktúra stránky: tri polia `type="text"` s `inputmode="decimal"` a `<label>`, prvky pre chybové správy a blok výsledkov.
  - Polia sú predvyplnené referenčným príkladom 100 000 / 4 / 30 (AD-08).
- **Dôvod zmeny:** zmena obsahu alebo štruktúry stránky.
- **Rozhranie:** atribúty `data-field="amount|rate|years"`, `data-error="<field>"`, `data-result="monthly|total|interest"`, ktoré používa M9.
- **Implementuje:** NFR-04 (labely), AD-03.

### M12 `styles.css` – vzhľad
- **Zodpovednosť:** vizuálna podoba stránky vrátane `white-space: nowrap` pre sumy a zvýraznenia neplatného poľa.
- **Dôvod zmeny:** zmena vzhľadu.
- **Rozhranie:** CSS triedy a selektory na atribúty z M11 (napr. `[aria-invalid="true"]`).
- **Implementuje:** FR-04 (suma sa nezalomí na dva riadky).

### Overenie SRP

| Modul | Jeden dôvod zmeny? | Poznámka |
|-------|--------------------|----------|
| M1 | Áno | Iba zápis čísla. Hranice ani polia nepozná. |
| M2 | Áno | **Upravené:** hranice boli predtým v module validácie. M7 ich potreboval iba na texty správ, a preto závisel od celej validácie. Teraz sú samostatné dáta. |
| M3 | Áno | Iba pravidlá platnosti. Texty správ sú v M7. |
| M4 | Áno | Iba vzorce. Nezaokrúhľuje a nevaliduje. |
| M5 | Áno | Ošetrenie hodnôt pod 1e-6 je súčasť zaokrúhlenia (rovnaký dôvod zmeny, DR-03), nie samostatná zodpovednosť. |
| M6 | Áno | `formatMoney` a `formatNumber` sa menia spolu (rovnaký formát FR-04). `formatMoney` je `formatNumber(v, 2) + " €"`. |
| M7 | Áno | **Upravené:** presunuté z `ui/` do `text/`, lebo nepoužíva DOM. Názov priečinka zodpovedá NFR-03. |
| M8 | Áno | Iba koordinácia, žiadny vlastný výpočet. |
| M9 | Áno | Čítanie aj vykreslenie sa menia z toho istého dôvodu (markup M11). Rozdelením na dva moduly by vznikli dva súbory závislé od tej istej štruktúry HTML. |
| M10 | Áno | **Upravené:** predtým bol jeden modul spolu s markupom a štýlmi (3 dôvody zmeny). Teraz je to iba prepojenie modulov. |
| M11 | Áno | **Upravené:** oddelené od M10 a M12. |
| M12 | Áno | **Upravené:** oddelené od M10 a M11. |

### Matica sledovateľnosti

| Požiadavka | Moduly |
|------------|--------|
| FR-01 Mesačná splátka | M4, M8 |
| FR-02 Celková zaplatená suma | M4, M8 |
| FR-03 Celkový zaplatený úrok | M4, M5, M8 |
| FR-04 Formát peňažných súm | M6, M8, M12 |
| FR-05 Neplatný vstup | M1, M3, M7, M8, M9 |
| IN-01 Výška úveru | M1, M2, M3 |
| IN-02 Ročná úroková sadzba | M1, M2, M3 |
| IN-03 Doba splácania | M1, M2, M3 |
| DR-01 Anuitný vzorec | M4 |
| DR-02 Sadzba 0 % | M4 |
| DR-03 Zaokrúhľovanie | M4, M5, M6 |
| DR-04 Referenčné príklady | M8 (akceptačné testy) |
| OQ-01 Kedy prepočítať | M9, M10 (AD-01) |
| NFR-01 Odozva ≤ 100 ms | M9, M10 |
| NFR-02 0 závislostí | celý projekt |
| NFR-03 Moduly bez DOM | M1–M8 |
| NFR-04 Prístupnosť formulára | M9, M11 |

## Dependency Direction

```
M10 main.js ──► M9 ui/view.js
     └───────► M8 app/calculator.js ──► M3 input/validate.js ──► M1 input/parse.js
                                    │                        └─► M2 input/limits.js
                                    ├─► M4 domain/mortgage.js
                                    ├─► M6 format/money.js ──► M5 domain/rounding.js
                                    └─► M7 text/messages.js ──► M2 input/limits.js
                                                            └─► M6 format/money.js
M11 index.html ──► M10 (<script type="module">), M12 (<link>)
M9 ──► M11 (iba cez data-* atribúty, nie import)
```

Pravidlá:
1. Závislosti smerujú iba zhora nadol: vstupný bod → UI → aplikácia → vstupy, doména, formát, texty.
2. Doména (M4, M5) a dáta (M2) neimportujú žiadny iný modul.
3. DOM používa iba M9 a M10. M1 až M8 nesmú odkazovať na `window` ani `document` (NFR-03).
4. M9 neimportuje M8. `CalculationResult` dostane ako argument od M10, ktorý ako jediný volá výpočet.
5. Cyklické závislosti nie sú povolené.
6. Dodržanie pravidiel 2 a 3 overí v implementácii jednoduchý test, ktorý prehľadá importy a výskyty `document`/`window` v `src/`.

## Data Model

Typy sú opísané v notácii JSDoc/TypeScript iba kvôli dokumentácii. Kód je čistý JavaScript.

```ts
type Field = 'amount' | 'rate' | 'years';

// Surové texty z formulára – jediný vstup do systému (M9 → M8)
type RawInput = { amount: string; rate: string; years: string };

// Výstup M1
type ParsedNumber =
  | { ok: true;  value: number; decimals: number }
  | { ok: false; reason: 'empty' | 'nan' };

// M2: hranice jedného poľa (IN-01 až IN-03)
type FieldLimits = { min: number; max: number; decimals: number };

// Výstup M3
type ErrorCode = 'empty' | 'nan' | 'step' | 'range';
type ValidationResult =
  | { valid: true;  values: { amount: number; rate: number; years: number } }
  | { valid: false; errors: Partial<Record<Field, ErrorCode>> };

// Vstup a výstup M4 (nezaokrúhlené, DR-03)
type LoanParams = { principal: number; annualRatePct: number; years: number };
type LoanResult = { monthlyPayment: number; totalPaid: number; totalInterest: number };

// Výstup M8 → vstup M9
type CalculationResult =
  | { status: 'ok';      results: { monthly: string; total: string; interest: string } }
  | { status: 'invalid'; errors: Partial<Record<Field, string>> };
```

Tok dát:

```
udalosť `input` → M9.readForm → RawInput { amount: "150 000", rate: "3,5", years: "25" }
  → M8.runCalculation
      → M3.validateInputs (M1 + M2) → ValidationResult
          invalid → M7.errorMessage pre každé pole → CalculationResult { status: 'invalid' }
          valid   → LoanParams → M4.calculateMortgage → LoanResult (nezaokrúhlené)
                  → M6.formatMoney (M5) → CalculationResult { status: 'ok' }
  → M9.render
```

Invarianty:
- Text sa na číslo prevádza iba v M1. Žiadny iný modul neparsuje vstup.
- Zaokrúhľuje sa iba v M6 (cez M5), tesne pred zobrazením. `LoanResult` je vždy nezaokrúhlený (DR-03).
- `status: 'invalid'` nikdy neobsahuje výsledky a `status: 'ok'` nikdy neobsahuje chyby (FR-05).
- Jednotky: `rate` / `annualRatePct` je v % p. a. (nie desatinný zlomok), `years` je celé číslo rokov, sumy sú v EUR.
- Aplikácia nemá žiadny trvalý stav. Stav je iba v poliach formulára a každý výpočet vychádza z nich.

## Extension Points & Decisions

### Body rozšírenia

Ako by sa do tejto architektúry pridali funkcie, ktoré sú vo V1 mimo rozsahu (časť 5 v `01-functional.md`):

| Rozšírenie | Kde sa zapojí | Čo sa nemení |
|------------|---------------|--------------|
| Nový vstup (poplatky, cena nehnuteľnosti / LTV) | Záznam v M2, text v M7, pole v M11, kľúč v `RawInput` | M1, M5, M6 |
| Splátkový kalendár | Nový doménový modul `domain/schedule.js` so vstupom `LoanParams`. M8 rozšíri `results`, M9 dostane vykreslenie tabuľky | M4, M1–M3 |
| Grafy | Nový UI modul `ui/chart.js` nad dátami kalendára | Doména, vstupy |
| Prepínanie jazyka | M7 dostane parameter jazyka (slovník textov) | Všetko okrem M7 a M11 |
| Iná mena | M6 dostane parameter meny | Doména, vstupy |
| Uloženie / zdieľanie výpočtu | Nový modul, ktorý serializuje `RawInput` (napr. do URL). Vstupom M10 je potom `RawInput` z URL namiesto predvyplnených hodnôt | M1–M8 |

### Nefunkčné požiadavky

Tieto požiadavky dopĺňajú `01-functional.md` a vyplývajú z rozhodnutí nižšie.

| ID | Požiadavka |
|----|------------|
| NFR-01 | Výsledky alebo chybové správy sa zobrazia do 100 ms po zmene ľubovoľného vstupu. |
| NFR-02 | Aplikácia nemá žiadne závislosti za behu (0 balíkov z npm, 0 načítaní z CDN). |
| NFR-03 | Moduly M1 až M8 sa dajú spustiť v Node.js bez DOM (0 odkazov na `window`/`document`). |
| NFR-04 | Každý vstup má priradený `<label>`. Neplatný vstup má `aria-invalid="true"` a chybová správa je s ním prepojená cez `aria-describedby`. |

### Rozhodnutia

| # | Rozhodnutie | Dôvod / kompromis |
|---|-------------|-------------------|
| AD-01 | **OQ-01: výsledky sa prepočítajú pri každej zmene vstupu** (udalosť `input`), bez tlačidla „Vypočítať“. | Výpočet je jeden vzorec O(1), trvá rádovo mikrosekundy, takže NFR-01 (≤ 100 ms) je splnená aj bez debounce. Kompromis: počas písania (napr. `99` pri výške úveru) sa na chvíľu zobrazí chyba rozsahu. Je to prijateľné, lebo správa hneď hovorí povolený rozsah. |
| AD-02 | Validuje sa pôvodný text, nie hodnota typu float. | Počet desatinných miest sa z floatu nedá spoľahlivo zistiť. `100,005` musí byť neplatné (IN-01). |
| AD-03 | Vstupy sú `type="text"`, nie `type="number"`. | `type="number"` v niektorých prehliadačoch odmieta čiarku alebo medzery a `value` vráti prázdny reťazec. Porušilo by to pravidlá IN-01 až IN-03. |
| AD-04 | Vlastné formátovanie čísla namiesto `Intl.NumberFormat`. | Presná zhoda s FR-04 (obyčajná medzera) a rovnaký výstup v Node.js aj v prehliadači. |
| AD-05 | Hranice vstupov sú iba v M2 a validácia aj texty chýb sa z nich odvodzujú. | Zmena hranice na jednom mieste zmení validáciu aj správu. |
| AD-06 | Doména, vstupy, formát, texty a orchestrácia sú bez DOM (NFR-03). | FR-01 až FR-05 a DR-04 sa dajú overiť rýchlymi testami v Node.js. Testy v prehliadači sú potrebné iba pre M9. |
| AD-07 | Žiadny framework ani build (NFR-02). | V1 má 3 vstupy a 3 výstupy. Kompromis: stránku treba spúšťať cez statický server, nie dvojklikom na súbor. |
| AD-08 | Polia sú pri načítaní predvyplnené hodnotami 100 000 / 4 / 30. | Po načítaní sa hneď zobrazí výsledok namiesto troch chýb pri prázdnom formulári. `01-functional.md` to nerieši, treba potvrdiť v review (04). |
| AD-09 | Moduly sú rozdelené podľa SRP na 12 modulov (pozri overenie SRP v sekcii Modules). | Presná matica sledovateľnosti: každý test sa viaže na modul s jedným dôvodom zmeny. Kompromis: viac súborov ako vyžaduje rozsah V1. |

### Zvážené alternatívy

#### ALT-01 Hrubé moduly (3 súbory) – zamietnuté

```
src/core.js      parse, limits, validate, calculate, round, format   (všetko bez DOM)
src/messages.js  slovenské texty
src/ui.js        čítanie formulára, vykreslenie, spustenie
```

| Výhody | Nevýhody |
|--------|----------|
| Zodpovedá veľkosti V1 (3 vstupy, 3 výstupy). Menej súborov a importov. | Matica sledovateľnosti stratí výpovednú hodnotu: FR-01 až FR-05 a všetky DR by ukazovali na `core.js`. To je v rozpore s pravidlom 3 v `CLAUDE.md`. |
| Zostáva testovateľnosť v Node.js (všetko okrem `ui.js`). | `core.js` má 5 dôvodov zmeny (zápis čísla, hranice, vzorce, zaokrúhľovanie, formát), čo porušuje SRP. |
| Menej rozhraní, ktoré treba držať stabilné. | Rastie s každým rozšírením (kalendár, poplatky, LTV) a neskôr by sa aj tak musel rozdeliť. Zaokrúhľovanie a formát v jednom súbore zvyšujú riziko predčasného zaokrúhlenia (DR-03). |

**Dôvod zamietnutia:** porušuje SRP a sledovateľnosť požiadaviek. Úspora niekoľkých súborov to nevyváži.

#### ALT-02 Konfiguračná tabuľka polí – odložené

```
src/fields.js      deklarácia každého vstupu: { id, label, unit, min, max, decimals, message }
src/field.js       generický spracovateľ poľa: parse + validácia + vlastná chyba
src/form.js        zber výsledkov polí, „ktorékoľvek neplatné → žiadne výsledky“ (FR-05)
src/mortgage.js    výpočet
src/money.js       zaokrúhlenie + formát
src/main.js
```

| Výhody | Nevýhody |
|--------|----------|
| Každý vstup je jeden záznam: hranice, desatinné miesta, popis aj text chyby spolu. | Pri 3 poliach pridáva zbytočnú abstrakciu. Kto chce pochopiť správanie výšky úveru, musí najprv pochopiť generický spracovateľ. |
| Nový vstup vo V2 (poplatky, cena nehnuteľnosti) je hlavne nový záznam, bez nového kódu validácie. | FR-05 („žiadne výsledky, ak je ktorékoľvek pole neplatné“) je pravidlo nad všetkými poliami, takže `form.js` je potrebný aj tak. Konfigurácia validáciu úplne nevlastní. |
| IN-01, IN-02 a IN-03 sa mapujú každý na jeden záznam. | Ak pole validuje a zobrazuje vlastnú chybu, validácia sa naviaže na DOM a stratí sa end-to-end test FR-01 až FR-05 v Node.js (M8, NFR-03), pokiaľ sa vrstvy zámerne neoddelia. |

**Dôvod odloženia:** vo V1 sa neoplatí. Architektúra je však pripravená na postupný prechod: M2 (`LIMITS`) už je malá konfiguračná tabuľka. Keď pribudnú ďalšie vstupy, môže dostať aj popisy a šablóny správ (dnes M7) bez prepisovania M1, M3 a M8.
Spúšťač prehodnotenia: viac ako 5 vstupov.
