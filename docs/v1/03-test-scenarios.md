# 03 – Testovacie scenáre

## Pravidlá tabuľky

- **Test** – názov testu, ktorý sa použije v kóde.
- **Úroveň** – `unit` (jeden modul v Node.js), `functional` (M8 v Node.js alebo M9 nad skutočným markupom M11 v prehliadači), `e2e` (celá stránka cez statický server v prehliadači).
- **Modul** – podľa `02-architecture.md` (M1 až M12).
- **Overuje požiadavku** – ID z `01-functional.md` (FR, IN, DR) alebo z `02-architecture.md` (NFR, AD, OQ).
- **Typ** – happy path, hraničný prípad alebo neplatný vstup.
- Reťazce vo výstupe sú uvedené presne, vrátane medzier a symbolu `€`. Všetky medzery v sumách sú obyčajné medzery U+0020 (FR-04, AD-04).
- Ak nie je uvedené inak, ostatné polia vstupu majú platné hodnoty `amount: "100000"`, `rate: "4"`, `years: "30"`.
- **Zdroj očakávanej hodnoty** – miesto v `01-functional.md` (skratka `01`) alebo `02-architecture.md` (skratka `02`), kde je očakávaná hodnota alebo pravidlo uvedené doslovne. `DR-04 r. N` je N-tý riadok referenčnej tabuľky pod DR-04.
- **NEOVERENÉ** – číselná hodnota, ktorá nie je doslovne uvedená v 01 ani v 02, iba z nich vypočítaná. Treba ju overiť nezávisle. Po overení sa doplní stĺpec Zdroj a značka sa odstráni.

Definície pre testy v prehliadači (M9 a e2e):

- **Blok výsledkov je viditeľný** – všetky 3 prvky `[data-result]` majú `checkVisibility() === true`.
- **Blok výsledkov nie je viditeľný** – všetky 3 prvky `[data-result]` majú `checkVisibility() === false`.
- **Žiadna chybová správa nie je zobrazená** – všetky 3 prvky `[data-error]` majú `textContent === ""`.
- **Zobrazená hodnota** – `textContent` príslušného prvku `[data-result]` po orezaní okrajových medzier.
- Každý e2e test začína novým načítaním stránky a nezávisí od iného testu.

## M1 `input/parse.js` – prevod textu na číslo

| Test | Úroveň | Modul | Overuje požiadavku | Vstup | Očakávaný výstup | Zdroj očakávanej hodnoty | Typ |
|------|--------|-------|--------------------|-------|------------------|--------------------------|-----|
| test_parse_cele_cislo | unit | M1 | IN-01 | `parseNumber("1000")` | `{ ok: true, value: 1000, decimals: 0 }` | 01 časť 3 (IN-01 platný príklad `1000`); 02 Data Model (`ParsedNumber`) | happy path |
| test_parse_medzery_medzi_cislicami | unit | M1 | IN-01 | `parseNumber("150 000")` | `{ ok: true, value: 150000, decimals: 0 }` | 01 časť 3 („`150 000` znamená 150 000 €“); 02 M1 | happy path |
| test_parse_desatinna_ciarka | unit | M1 | IN-02 | `parseNumber("3,5")` | `{ ok: true, value: 3.5, decimals: 1 }` | 01 časť 3 („`3,5` aj `3.5` znamená 3,5 %“); 02 M1 | happy path |
| test_parse_desatinna_bodka | unit | M1 | IN-02 | `parseNumber("4.25")` | `{ ok: true, value: 4.25, decimals: 2 }` | 01 časť 3 (IN-02 platný príklad `4.25`); 02 M1 | happy path |
| test_parse_orezanie_okrajovych_medzier | unit | M1 | IN-03 | `parseNumber("  25  ")` | `{ ok: true, value: 25, decimals: 0 }` | 02 M1 („Orezá medzery na začiatku a na konci“) | hraničný prípad |
| test_parse_tri_desatinne_miesta | unit | M1 | IN-01 | `parseNumber("100,005")` | `{ ok: true, value: 100.005, decimals: 3 }` (M1 hranice nepozná, odmietne až M3) | 02 M1 („Vráti aj počet desatinných miest“, „Nepozná hranice“) | hraničný prípad |
| test_parse_zaporne_cislo | unit | M1 | IN-02 | `parseNumber("-0,01")` | `{ ok: true, value: -0.01, decimals: 2 }` | 02 M1 (tvar `-?číslice[,\|.číslice]`) | hraničný prípad |
| test_parse_prazdny_retazec | unit | M1 | FR-05, IN-01 | `parseNumber("")` | `{ ok: false, reason: 'empty' }` | 01 časť 3 („je prázdny“); 02 Data Model | neplatný vstup |
| test_parse_iba_medzery | unit | M1 | FR-05, IN-01 | `parseNumber("   ")` | `{ ok: false, reason: 'empty' }` | 02 M1 (orezanie medzier), pozri TQ-02 | neplatný vstup |
| test_parse_text | unit | M1 | FR-05, IN-01 | `parseNumber("abc")` | `{ ok: false, reason: 'nan' }` | 01 časť 3 (IN-01 neplatný príklad `abc`); 02 Data Model | neplatný vstup |
| test_parse_exponent | unit | M1 | FR-05, IN-01 | `parseNumber("1e3")` | `{ ok: false, reason: 'nan' }` | 02 M1 (`1e3` vráti ako `'nan'`) | neplatný vstup |
| test_parse_hexadecimalne | unit | M1 | FR-05, IN-01 | `parseNumber("0x10")` | `{ ok: false, reason: 'nan' }` | 02 M1 (`0x10` vráti ako `'nan'`) | neplatný vstup |
| test_parse_viac_oddelovacov | unit | M1 | FR-05, IN-02 | `parseNumber("1,2,3")` | `{ ok: false, reason: 'nan' }` | 02 M1 (`1,2,3` vráti ako `'nan'`) | neplatný vstup |
| test_parse_oddelovac_bez_cislic | unit | M1 | FR-05, IN-02 | `parseNumber("3,")` | `{ ok: false, reason: 'nan' }` | 02 M1 (tvar `-?číslice[,\|.číslice]`) | neplatný vstup |

## M2 `input/limits.js` – hranice vstupov

| Test | Úroveň | Modul | Overuje požiadavku | Vstup | Očakávaný výstup | Zdroj očakávanej hodnoty | Typ |
|------|--------|-------|--------------------|-------|------------------|--------------------------|-----|
| test_limits_podla_tabulky_vstupov | unit | M2 | IN-01, IN-02, IN-03 | `LIMITS` | `{ amount: { min: 1000, max: 1000000, decimals: 2 }, rate: { min: 0, max: 20, decimals: 2 }, years: { min: 1, max: 30, decimals: 0 } }` | 01 časť 3 (tabuľka vstupov); 02 M2 | happy path |

## M3 `input/validate.js` – validácia vstupov

| Test | Úroveň | Modul | Overuje požiadavku | Vstup | Očakávaný výstup | Zdroj očakávanej hodnoty | Typ |
|------|--------|-------|--------------------|-------|------------------|--------------------------|-----|
| test_validacia_referencne_vstupy | unit | M3 | IN-01, IN-02, IN-03 | `{ amount: "100 000", rate: "4", years: "30" }` | `{ valid: true, values: { amount: 100000, rate: 4, years: 30 } }` | 01 DR-04 r. 1; 02 Data Model | happy path |
| test_validacia_platne_priklady_z_tabulky | unit | M3 | IN-01, IN-02, IN-03 | `{ amount: "99999,99", rate: "4.25", years: "25" }` | `{ valid: true, values: { amount: 99999.99, rate: 4.25, years: 25 } }` | 01 časť 3 (platné príklady) | happy path |
| test_validacia_dolne_hranice | unit | M3 | IN-01, IN-02, IN-03 | `{ amount: "1000", rate: "0", years: "1" }` | `{ valid: true, values: { amount: 1000, rate: 0, years: 1 } }` | 01 časť 3 (Min, „Hranice sú vrátane“) | hraničný prípad |
| test_validacia_horne_hranice | unit | M3 | IN-01, IN-02, IN-03 | `{ amount: "1000000", rate: "20", years: "30" }` | `{ valid: true, values: { amount: 1000000, rate: 20, years: 30 } }` | 01 časť 3 (Max, „Hranice sú vrátane“) | hraničný prípad |
| test_validacia_vyska_uveru_pod_minimom | unit | M3 | IN-01, FR-05 | `amount: "999,99"` | `{ valid: false, errors: { amount: 'range' } }` | 01 časť 3 (IN-01 neplatný príklad); 02 Data Model | neplatný vstup |
| test_validacia_vyska_uveru_nad_maximom | unit | M3 | IN-01, FR-05 | `amount: "1000000,01"` | `{ valid: false, errors: { amount: 'range' } }` | 01 časť 3 (IN-01 neplatný príklad); 02 Data Model | neplatný vstup |
| test_validacia_vyska_uveru_privela_desatinnych | unit | M3 | IN-01, FR-05 | `amount: "100,005"` | `{ valid: false, errors: { amount: 'step' } }` (nie `'range'` – `step` sa overuje pred rozsahom) | 01 časť 3 (IN-01 neplatný príklad); 02 M3 (poradie podmienok) | neplatný vstup |
| test_validacia_vyska_uveru_text | unit | M3 | IN-01, FR-05 | `amount: "abc"` | `{ valid: false, errors: { amount: 'nan' } }` | 01 časť 3 (IN-01 neplatný príklad); 02 Data Model | neplatný vstup |
| test_validacia_vyska_uveru_prazdna | unit | M3 | IN-01, FR-05 | `amount: ""` | `{ valid: false, errors: { amount: 'empty' } }` | 01 časť 3 (IN-01 neplatný príklad); 02 Data Model | neplatný vstup |
| test_validacia_sadzba_zaporna | unit | M3 | IN-02, FR-05 | `rate: "-0,01"` | `{ valid: false, errors: { rate: 'range' } }` | 01 časť 3 (IN-02 neplatný príklad); 02 Data Model | neplatný vstup |
| test_validacia_sadzba_nad_maximom | unit | M3 | IN-02, FR-05 | `rate: "20,01"` | `{ valid: false, errors: { rate: 'range' } }` | 01 časť 3 (IN-02 neplatný príklad); 02 Data Model | neplatný vstup |
| test_validacia_sadzba_tri_desatinne | unit | M3 | IN-02, FR-05 | `rate: "3,125"` | `{ valid: false, errors: { rate: 'step' } }` | 01 časť 3 (IN-02 neplatný príklad); 02 Data Model | neplatný vstup |
| test_validacia_sadzba_prazdna | unit | M3 | IN-02, FR-05 | `rate: ""` | `{ valid: false, errors: { rate: 'empty' } }` | 01 časť 3 (IN-02 neplatný príklad); 02 Data Model | neplatný vstup |
| test_validacia_doba_nula | unit | M3 | IN-03, FR-05 | `years: "0"` | `{ valid: false, errors: { years: 'range' } }` | 01 časť 3 (IN-03 neplatný príklad); 02 Data Model | neplatný vstup |
| test_validacia_doba_nad_maximom | unit | M3 | IN-03, FR-05 | `years: "31"` | `{ valid: false, errors: { years: 'range' } }` | 01 časť 3 (IN-03 neplatný príklad); 02 Data Model | neplatný vstup |
| test_validacia_doba_desatinna | unit | M3 | IN-03, FR-05 | `years: "2,5"` | `{ valid: false, errors: { years: 'step' } }` | 01 časť 3 (IN-03 neplatný príklad); 02 Data Model | neplatný vstup |
| test_validacia_doba_prazdna | unit | M3 | IN-03, FR-05 | `years: ""` | `{ valid: false, errors: { years: 'empty' } }` | 01 časť 3 (IN-03 neplatný príklad); 02 Data Model | neplatný vstup |
| test_validacia_dve_chyby_naraz | unit | M3 | FR-05 | `{ amount: "100000", rate: "", years: "2,5" }` | `{ valid: false, errors: { rate: 'empty', years: 'step' } }`; `errors` nemá kľúč `amount` | 01 FR-05 (príklad 3); 02 M3 | neplatný vstup |
| test_validacia_tri_chyby_naraz | unit | M3 | FR-05 | `{ amount: "abc", rate: "", years: "31" }` | `{ valid: false, errors: { amount: 'nan', rate: 'empty', years: 'range' } }` | 01 časť 3 (neplatné príklady); 02 M3 („Validuje všetky tri polia naraz“) | neplatný vstup |

## M4 `domain/mortgage.js` – výpočet

M4 vracia nezaokrúhlené čísla (DR-03). Testy ich preto porovnávajú po zaokrúhlení cez `roundHalfUp` z M5.

| Test | Úroveň | Modul | Overuje požiadavku | Vstup | Očakávaný výstup | Zdroj očakávanej hodnoty | Typ |
|------|--------|-------|--------------------|-------|------------------|--------------------------|-----|
| test_splatka_zakladny_priklad | unit | M4 | FR-01, FR-02, FR-03, DR-01 | `{ principal: 100000, annualRatePct: 4, years: 30 }` | `roundHalfUp(monthlyPayment, 2) === 477.42`, `roundHalfUp(totalPaid, 2) === 171869.51`, `roundHalfUp(totalInterest, 2) === 71869.51` | 01 DR-04 r. 1; 01 FR-01, FR-02, FR-03 (príklad 1) | happy path |
| test_splatka_nulova_sadzba | unit | M4 | FR-01, FR-02, FR-03, DR-02 | `{ principal: 12000, annualRatePct: 0, years: 1 }` | `monthlyPayment === 1000`, `totalPaid === 12000`, `totalInterest === 0` | 01 DR-02 (príklad); 01 DR-04 r. 2 | hraničný prípad |
| test_splatka_bez_zaokruhlenia_medzivysledkov | unit | M4 | DR-03 | `{ principal: 100000, annualRatePct: 4, years: 30 }` | `totalPaid === monthlyPayment * 360` (striktná rovnosť); `roundHalfUp(totalPaid, 2) === 171869.51`, nie `171871.20` (= 477,42 × 360 – NEOVERENÉ) | 01 DR-03 („Celková suma = M × n s nezaokrúhleným M“); 01 DR-04 r. 1 | happy path |
| test_splatka_minimalna_kladna_sadzba | unit | M4 | DR-01, DR-03 | `{ principal: 1000, annualRatePct: 0.01, years: 1 }` | `roundHalfUp(monthlyPayment, 4) === 83.3378`, `roundHalfUp(totalInterest, 4) === 0.0542`; `roundHalfUp(monthlyPayment, 2) === 83.34`, `roundHalfUp(totalPaid, 2) === 1000.05`, `roundHalfUp(totalInterest, 2) === 0.05` | 01 DR-03 (príklad); 01 DR-04 r. 4 | hraničný prípad |
| test_splatka_maximalne_hodnoty | unit | M4 | DR-01, DR-04 | `{ principal: 1000000, annualRatePct: 20, years: 30 }` | `roundHalfUp(monthlyPayment, 2) === 16710.19`, `roundHalfUp(totalPaid, 2) === 6015667.27`, `roundHalfUp(totalInterest, 2) === 5015667.27` | 01 DR-04 r. 3 | hraničný prípad |
| test_splatka_minimalne_hodnoty | unit | M4 | DR-02 | `{ principal: 1000, annualRatePct: 0, years: 1 }` | `roundHalfUp(monthlyPayment, 2) === 83.33`, `roundHalfUp(totalPaid, 2) === 1000`, `roundHalfUp(totalInterest, 2) === 0` — NEOVERENÉ | | hraničný prípad |
| test_splatka_nulova_sadzba_zvysok_float | unit | M4 | DR-02, DR-03 | `{ principal: 1000, annualRatePct: 0, years: 29 }` | `totalInterest === -1.1368683772161603e-13` (M4 zvyšok nezaokrúhľuje ani neupravuje, rieši ho M5) — NEOVERENÉ | | hraničný prípad |
| test_splatka_neplatna_doba_nula | unit | M4 | DR-02 (TQ-01) | `{ principal: 1000, annualRatePct: 0, years: 0 }` | vyhodí `RangeError` so správou `"Neplatné parametre úveru."` | návrh TQ-01 | neplatný vstup |

## M5 `domain/rounding.js` – zaokrúhľovanie

| Test | Úroveň | Modul | Overuje požiadavku | Vstup | Očakávaný výstup | Zdroj očakávanej hodnoty | Typ |
|------|--------|-------|--------------------|-------|------------------|--------------------------|-----|
| test_zaokruhlenie_splatky | unit | M5 | DR-03 | `roundHalfUp(477.4152954654538, 2)` | `477.42` | 01 DR-01 (príklad M = 477,4153…); 01 DR-04 r. 1 | happy path |
| test_zaokruhlenie_polovica_nahor | unit | M5 | DR-03 | `roundHalfUp(0.005, 2)` | `0.01` — NEOVERENÉ | | hraničný prípad |
| test_zaokruhlenie_tesne_pod_polovicou | unit | M5 | DR-03 | `roundHalfUp(0.004999, 2)` | `0` — NEOVERENÉ | | hraničný prípad |
| test_zaokruhlenie_binarna_chyba_1_005 | unit | M5 | DR-03 | `roundHalfUp(1.005, 2)` | `1.01` (nie `1.00`) | 02 M5 („`1.005` → `1.01`, nie `1.00`“) | hraničný prípad |
| test_zaokruhlenie_binarna_chyba_2_675 | unit | M5 | DR-03 | `roundHalfUp(2.675, 2)` | `2.68` (nie `2.67`) — NEOVERENÉ | | hraničný prípad |
| test_zaokruhlenie_na_cele_cislo | unit | M5 | DR-03 | `roundHalfUp(2.5, 0)` | `3` — NEOVERENÉ | | hraničný prípad |
| test_zaokruhlenie_maly_kladny_zvysok | unit | M5 | DR-03, FR-03 | `roundHalfUp(1.1368683772161603e-13, 2)` | `0` (nie `NaN`) | 02 M5 („Hodnoty s \|value\| < 1e-6 vráti ako `0`“) | hraničný prípad |
| test_zaokruhlenie_maly_zaporny_zvysok | unit | M5 | DR-03, FR-03 | `roundHalfUp(-1.1368683772161603e-13, 2)` | `0`; `Object.is(vysledok, -0) === false` | 02 M5 („Hodnoty s \|value\| < 1e-6 vráti ako `0`“, „Nikdy nevráti `-0`“) | hraničný prípad |
| test_zaokruhlenie_neplatny_vstup_nan | unit | M5 | DR-03 (TQ-01) | `roundHalfUp(NaN, 2)` | vyhodí `RangeError` so správou `"Neplatné číslo na zaokrúhlenie."` | návrh TQ-01 | neplatný vstup |

## M6 `format/money.js` – formát čísel a súm

| Test | Úroveň | Modul | Overuje požiadavku | Vstup | Očakávaný výstup | Zdroj očakávanej hodnoty | Typ |
|------|--------|-------|--------------------|-------|------------------|--------------------------|-----|
| test_format_suma_miliony | unit | M6 | FR-04, DR-03 | `formatMoney(6015667.2705)` | `"6 015 667,27 €"` | 01 FR-04 (príklad 1); 02 M6 | happy path |
| test_format_suma_tisic | unit | M6 | FR-04 | `formatMoney(1000)` | `"1 000,00 €"` | 01 FR-04 (príklad 2) | happy path |
| test_format_suma_nula | unit | M6 | FR-04 | `formatMoney(0)` | `"0,00 €"` | 01 FR-04 (príklad 3) | hraničný prípad |
| test_format_suma_bez_oddelovaca_tisicov | unit | M6 | FR-04 | `formatMoney(999.99)` | `"999,99 €"` — NEOVERENÉ | | hraničný prípad |
| test_format_suma_zaokruhlenie_cez_tisic | unit | M6 | FR-04, DR-03 | `formatMoney(999.995)` | `"1 000,00 €"` — NEOVERENÉ | | hraničný prípad |
| test_format_suma_milion | unit | M6 | FR-04 | `formatMoney(1000000)` | `"1 000 000,00 €"` — NEOVERENÉ | | hraničný prípad |
| test_format_suma_bez_zapornej_nuly | unit | M6 | FR-03, FR-04 | `formatMoney(-1.1368683772161603e-13)` | `"0,00 €"` (nie `"-0,00 €"`) | 02 M5 („zobrazilo by sa `-0,00 €` namiesto `0,00 €`“) | hraničný prípad |
| test_format_suma_obycajne_medzery | unit | M6 | FR-04, AD-04 | `formatMoney(6015667.2705)` | výstup neobsahuje U+00A0 ani U+202F; obsahuje presne 3 znaky U+0020 | 02 M6, AD-04 (obyčajná medzera) | hraničný prípad |
| test_format_cislo_bez_desatinnych | unit | M6 | FR-04 | `formatNumber(1000000, 0)` | `"1 000 000"` — NEOVERENÉ (pozri TQ-05) | | happy path |
| test_format_cislo_male | unit | M6 | FR-04 | `formatNumber(20, 0)` | `"20"` — NEOVERENÉ | | hraničný prípad |
| test_format_suma_neplatny_vstup_nan | unit | M6 | FR-04 (TQ-01) | `formatMoney(NaN)` | vyhodí `RangeError` so správou `"Neplatná suma na formátovanie."` | návrh TQ-01 | neplatný vstup |

## M7 `text/messages.js` – chybové správy

| Test | Úroveň | Modul | Overuje požiadavku | Vstup | Očakávaný výstup | Zdroj očakávanej hodnoty | Typ |
|------|--------|-------|--------------------|-------|------------------|--------------------------|-----|
| test_sprava_vyska_uveru | unit | M7 | FR-05, IN-01 | `errorMessage('amount', 'range')` | `"Výška úveru musí byť od 1 000 do 1 000 000 €."` | 01 FR-05 (príklad 1); 02 M7 | neplatný vstup |
| test_sprava_sadzba | unit | M7 | FR-05, IN-02 | `errorMessage('rate', 'range')` | `"Ročná úroková sadzba musí byť od 0 do 20 %."` | 02 M7 | neplatný vstup |
| test_sprava_doba | unit | M7 | FR-05, IN-03 | `errorMessage('years', 'range')` | `"Doba splácania musí byť od 1 do 30 rokov."` | 01 FR-05 (príklad 2); 02 M7 | neplatný vstup |
| test_sprava_rovnaka_pre_vsetky_kody | unit | M7 | FR-05 | `errorMessage('amount', c)` pre `c` z `'empty'`, `'nan'`, `'step'`, `'range'` | všetky 4 výsledky sú `"Výška úveru musí byť od 1 000 do 1 000 000 €."` | 02 M7 („Pre všetky kódy chýb jedného poľa vráti tú istú správu“) | hraničný prípad |

## M8 `app/calculator.js` – orchestrácia

Vstup je `RawInput` (surové texty). Výstup je `CalculationResult`.

| Test | Úroveň | Modul | Overuje požiadavku | Vstup | Očakávaný výstup | Zdroj očakávanej hodnoty | Typ |
|------|--------|-------|--------------------|-------|------------------|--------------------------|-----|
| test_vypocet_referencny_priklad | functional | M8 | FR-01, FR-02, FR-03, FR-04, DR-01, DR-04 | `{ amount: "100000", rate: "4", years: "30" }` | `{ status: 'ok', results: { monthly: "477,42 €", total: "171 869,51 €", interest: "71 869,51 €" } }` | 01 DR-04 r. 1 | happy path |
| test_vypocet_referencny_priklad_nulova_sadzba | functional | M8 | FR-01, FR-02, FR-03, DR-02, DR-04 | `{ amount: "12000", rate: "0", years: "1" }` | `{ status: 'ok', results: { monthly: "1 000,00 €", total: "12 000,00 €", interest: "0,00 €" } }` | 01 DR-04 r. 2 | hraničný prípad |
| test_vypocet_referencny_priklad_maximum | functional | M8 | FR-01, FR-02, FR-03, FR-04, DR-04 | `{ amount: "1000000", rate: "20", years: "30" }` | `{ status: 'ok', results: { monthly: "16 710,19 €", total: "6 015 667,27 €", interest: "5 015 667,27 €" } }` | 01 DR-04 r. 3 | hraničný prípad |
| test_vypocet_referencny_priklad_minimalna_sadzba | functional | M8 | DR-03, DR-04 | `{ amount: "1000", rate: "0,01", years: "1" }` | `{ status: 'ok', results: { monthly: "83,34 €", total: "1 000,05 €", interest: "0,05 €" } }` | 01 DR-04 r. 4; 01 DR-03 (príklad) | hraničný prípad |
| test_vypocet_medzery_a_ciarka | functional | M8 | IN-01, IN-02, FR-01, FR-02, FR-03 | `{ amount: "150 000", rate: "3,5", years: "25" }` | `{ status: 'ok', results: { monthly: "750,94 €", total: "225 280,61 €", interest: "75 280,61 €" } }` — NEOVERENÉ | | happy path |
| test_vypocet_ciarka_a_bodka_rovnako | functional | M8 | IN-02 | a) `{ amount: "100000", rate: "3,5", years: "30" }`, b) to isté s `rate: "3.5"` | oba: `{ status: 'ok', results: { monthly: "449,04 €", total: "161 656,09 €", interest: "61 656,09 €" } }` — NEOVERENÉ | | happy path |
| test_vypocet_desatinna_vyska_uveru | functional | M8 | IN-01, FR-03 | `{ amount: "99999,99", rate: "4.25", years: "25" }` | `{ status: 'ok', results: { monthly: "541,74 €", total: "162 521,41 €", interest: "62 521,42 €" } }` — NEOVERENÉ | | hraničný prípad |
| test_vypocet_dolne_hranice | functional | M8 | IN-01, IN-02, IN-03, DR-02 | `{ amount: "1000", rate: "0", years: "1" }` | `{ status: 'ok', results: { monthly: "83,33 €", total: "1 000,00 €", interest: "0,00 €" } }` — NEOVERENÉ | | hraničný prípad |
| test_vypocet_nulova_sadzba_bez_zapornej_nuly | functional | M8 | FR-03, DR-02, DR-03 | `{ amount: "1000", rate: "0", years: "29" }` | `{ status: 'ok', results: { monthly: "2,87 €", total: "1 000,00 €", interest: "0,00 €" } }` — NEOVERENÉ | | hraničný prípad |
| test_vypocet_neplatna_vyska_uveru | functional | M8 | FR-05, IN-01 | `{ amount: "999", rate: "4", years: "30" }` | `{ status: 'invalid', errors: { amount: "Výška úveru musí byť od 1 000 do 1 000 000 €." } }`; objekt nemá kľúč `results` | 01 FR-05 (príklad 1); 02 Data Model (invarianty) | neplatný vstup |
| test_vypocet_vyska_uveru_tesne_nad_maximom | functional | M8 | FR-05, IN-01 | `{ amount: "1000000,01", rate: "4", years: "30" }` | `{ status: 'invalid', errors: { amount: "Výška úveru musí byť od 1 000 do 1 000 000 €." } }`; objekt nemá kľúč `results` | 01 časť 3 (IN-01 neplatný príklad); 01 FR-05; 02 M7 | neplatný vstup |
| test_vypocet_neplatna_doba | functional | M8 | FR-05, IN-03 | `{ amount: "100000", rate: "4", years: "31" }` | `{ status: 'invalid', errors: { years: "Doba splácania musí byť od 1 do 30 rokov." } }`; objekt nemá kľúč `results` | 01 FR-05 (príklad 2) | neplatný vstup |
| test_vypocet_dve_chyby_naraz | functional | M8 | FR-05, IN-02, IN-03 | `{ amount: "100000", rate: "", years: "2,5" }` | `{ status: 'invalid', errors: { rate: "Ročná úroková sadzba musí byť od 0 do 20 %.", years: "Doba splácania musí byť od 1 do 30 rokov." } }`; `errors` nemá kľúč `amount`; objekt nemá kľúč `results` | 01 FR-05 (príklad 3); 02 M7 | neplatný vstup |
| test_vypocet_tri_chyby_naraz | functional | M8 | FR-05 | `{ amount: "abc", rate: "20,01", years: "0" }` | `{ status: 'invalid', errors: { amount: "Výška úveru musí byť od 1 000 do 1 000 000 €.", rate: "Ročná úroková sadzba musí byť od 0 do 20 %.", years: "Doba splácania musí byť od 1 do 30 rokov." } }`; objekt nemá kľúč `results` | 01 časť 3 (neplatné príklady); 01 FR-05; 02 M7 | neplatný vstup |

## Architektonické kontroly

| Test | Úroveň | Modul | Overuje požiadavku | Vstup | Očakávaný výstup | Zdroj očakávanej hodnoty | Typ |
|------|--------|-------|--------------------|-------|------------------|--------------------------|-----|
| test_moduly_bez_dom | unit | M1–M8 | NFR-03, AD-06 | text súborov v `src/input/`, `src/domain/`, `src/format/`, `src/text/`, `src/app/` | 0 výskytov identifikátorov `document` a `window` | 02 NFR-03; 02 Dependency Direction (pravidlá 3 a 6) | happy path |
| test_domena_a_data_bez_importov | unit | M2, M4, M5 | NFR-03 | text súborov `src/input/limits.js`, `src/domain/mortgage.js`, `src/domain/rounding.js` | 0 príkazov `import` | 02 Dependency Direction (pravidlá 2 a 6) | happy path |
| test_ziadne_zavislosti | unit | celý projekt | NFR-02, AD-07 | `package.json`, `index.html`, všetky súbory v `src/` | `package.json` nemá kľúče `dependencies` ani `devDependencies`; žiadny `import`, `<script src>` ani `<link href>` neodkazuje na `http://` alebo `https://` | 02 NFR-02; 02 Stack (`package.json`) | happy path |

## M9 `ui/view.js` – DOM adaptér

Testy bežia v prehliadači nad markupom z `index.html` (M11).

| Test | Úroveň | Modul | Overuje požiadavku | Vstup | Očakávaný výstup | Zdroj očakávanej hodnoty | Typ |
|------|--------|-------|--------------------|-------|------------------|--------------------------|-----|
| test_view_citanie_formulara | functional | M9, M11 | IN-01, IN-02, IN-03, AD-03 | polia: `amount` = `150 000`, `rate` = `3,5`, `years` = `25`; `readForm(root)` | `{ amount: "150 000", rate: "3,5", years: "25" }` (reťazce bez prevodu) | 02 M9 („Prečíta hodnoty polí ako surové texty“); 02 Data Model (tok dát) | happy path |
| test_view_vykreslenie_vysledkov | functional | M9, M11 | FR-01, FR-02, FR-03 | `render(root, { status: 'ok', results: { monthly: "477,42 €", total: "171 869,51 €", interest: "71 869,51 €" } })` | zobrazené hodnoty: `[data-result="monthly"]` = `477,42 €`, `[data-result="total"]` = `171 869,51 €`, `[data-result="interest"]` = `71 869,51 €`; blok výsledkov je viditeľný; žiadne pole nemá `aria-invalid="true"` | 02 M9; 01 DR-04 r. 1 | happy path |
| test_view_vykreslenie_chyby | functional | M9, M11 | FR-05, NFR-04 | `render(root, { status: 'invalid', errors: { amount: "Výška úveru musí byť od 1 000 do 1 000 000 €." } })` | blok výsledkov nie je viditeľný; `[data-error="amount"]` má `textContent` = `Výška úveru musí byť od 1 000 do 1 000 000 €.`; pole `amount` má `aria-invalid="true"` a `aria-describedby` = `id` prvku `[data-error="amount"]`; polia `rate` a `years` nemajú `aria-invalid="true"` | 01 FR-05; 02 M9; 02 NFR-04 | neplatný vstup |
| test_view_oprava_chyby | functional | M9, M11 | FR-05, NFR-04 | `render` so vstupom z `test_view_vykreslenie_chyby`, hneď potom `render` so vstupom z `test_view_vykreslenie_vysledkov` (v tom istom teste) | žiadna chybová správa nie je zobrazená; pole `amount` nemá `aria-invalid="true"`; blok výsledkov je viditeľný; zobrazené hodnoty `477,42 €`, `171 869,51 €`, `71 869,51 €` | 02 M9 („Pri stave `ok` zobrazí tri výsledky a odstráni chyby“), pozri TQ-03 | hraničný prípad |
| test_view_input_vola_callback | functional | M9 | OQ-01, AD-01 | `bind(root, spy)`; 1× udalosť `input` na poli `rate` | `spy` zavolaný presne 1× | 02 M9 („Pri každej udalosti `input` zavolá spätné volanie“); 02 AD-01 | happy path |
| test_view_labely_vstupov | functional | M11 | NFR-04 | `index.html` | každé z 3 polí `[data-field]` má `labels.length === 1` | 02 NFR-04; 02 M11 | happy path |

## E2E – celá stránka

Stránka sa načíta zo statického servera (`index.html`). Používateľ píše do polí a kontroluje sa zobrazený text. Pojmy „viditeľný“ a „zobrazená hodnota“ sú definované v časti Pravidlá tabuľky.

| Test | Úroveň | Modul | Overuje požiadavku | Vstup | Očakávaný výstup | Zdroj očakávanej hodnoty | Typ |
|------|--------|-------|--------------------|-------|------------------|--------------------------|-----|
| test_e2e_predvyplnene_hodnoty | e2e | M1–M12 | AD-08, FR-01, FR-02, FR-03, FR-04, DR-04 | načítanie stránky bez interakcie | zobrazené hodnoty `477,42 €`, `171 869,51 €`, `71 869,51 €`; blok výsledkov je viditeľný; žiadna chybová správa nie je zobrazená | 01 DR-04 r. 1; 02 AD-08 (nepotvrdené, pozri 04) | happy path |
| test_e2e_zadanie_vstupov_zobrazi_vysledok | e2e | M1–M12 | FR-01, FR-02, FR-03, FR-04, IN-01, IN-02, OQ-01 | vymazať všetky polia a napísať `150 000`, `3,5`, `25`; nekliknúť na žiadne tlačidlo | zobrazené hodnoty: mesačná splátka `750,94 €`, celkom zaplatené `225 280,61 €`, celkový úrok `75 280,61 €` — NEOVERENÉ | | happy path |
| test_e2e_neplatny_vstup_skryje_vysledky | e2e | M1–M12 | FR-05, NFR-04 | vymazať výšku úveru a napísať `999` | `[data-error="amount"]` má `textContent` = `Výška úveru musí byť od 1 000 do 1 000 000 €.`; blok výsledkov nie je viditeľný; pole má `aria-invalid="true"` | 01 FR-05 (príklad 1); 02 NFR-04 | neplatný vstup |
| test_e2e_dve_chyby_naraz | e2e | M1–M12 | FR-05 | vymazať sadzbu; vymazať dobu splácania a napísať `2,5` | `[data-error="rate"]` = `Ročná úroková sadzba musí byť od 0 do 20 %.`; `[data-error="years"]` = `Doba splácania musí byť od 1 do 30 rokov.`; `[data-error="amount"]` je prázdny; blok výsledkov nie je viditeľný | 01 FR-05 (príklad 3); 02 M7 | neplatný vstup |
| test_e2e_oprava_vstupu_obnovi_vysledky | e2e | M1–M12 | FR-05, IN-01 | 1. vymazať výšku úveru a napísať `999`; 2. overiť, že blok výsledkov nie je viditeľný; 3. vymazať výšku úveru a napísať `1000` (sadzba `4` a doba `30` ostávajú predvyplnené) | po kroku 3: zobrazené hodnoty `4,77 €`, `1 718,70 €`, `718,70 €`; blok výsledkov je viditeľný; žiadna chybová správa nie je zobrazená — NEOVERENÉ | | hraničný prípad |
| test_e2e_maximalne_sumy_sa_nezalomia | e2e | M6, M11, M12 | FR-04 | šírka okna 320 px; vymazať polia a napísať `1 000 000`, `20`, `30` | zobrazené hodnoty `16 710,19 €`, `6 015 667,27 €`, `5 015 667,27 €`; pre každý prvok `[data-result]` platí `getComputedStyle(el).whiteSpace === "nowrap"` a rozsah (`Range`) nad jeho textom má `getClientRects().length === 1` (text je v jednom riadku) | 01 DR-04 r. 3; 02 M12 (`white-space: nowrap`) | hraničný prípad |
| test_e2e_odozva_do_100ms | e2e | M9, M10 | NFR-01 | predvyplnená stránka; dobu splácania vymazať a napísať `25` | zobrazená hodnota `[data-result="monthly"]` je `527,84 €` najneskôr 100 ms po poslednej udalosti `input` — NEOVERENÉ | | happy path |
| test_e2e_ziadne_externe_poziadavky | e2e | celý projekt | NFR-02 | načítanie stránky | 0 sieťových požiadaviek na iný pôvod (origin) než statický server | 02 NFR-02 | happy path |

## Pokrytie požiadaviek

| Požiadavka | Testy |
|------------|-------|
| FR-01 Mesačná splátka | M4, M8, M9, e2e (`test_e2e_zadanie_vstupov_zobrazi_vysledok`) |
| FR-02 Celková zaplatená suma | M4, M8, M9, e2e |
| FR-03 Celkový zaplatený úrok | M4, M5, M6, M8, M9, e2e |
| FR-04 Formát peňažných súm | M6, M8, e2e (`test_e2e_maximalne_sumy_sa_nezalomia`) |
| FR-05 Neplatný vstup | M1, M3, M7, M8, M9, e2e |
| IN-01 Výška úveru | M1, M2, M3, M7, M8, M9, e2e |
| IN-02 Ročná úroková sadzba | M1, M2, M3, M7, M8, M9, e2e |
| IN-03 Doba splácania | M1, M2, M3, M7, M8, M9 |
| DR-01 Anuitný vzorec | M4, M8 |
| DR-02 Sadzba 0 % | M4, M8 |
| DR-03 Zaokrúhľovanie | M4, M5, M6, M8 |
| DR-04 Referenčné príklady | M4, M8 (všetky 4 riadky tabuľky z `01-functional.md`), e2e |
| OQ-01 / AD-01 Prepočet pri každej zmene | M9, e2e |
| NFR-01 Odozva ≤ 100 ms | e2e |
| NFR-02 0 závislostí | architektonická kontrola, e2e |
| NFR-03 Moduly bez DOM | architektonické kontroly |
| NFR-04 Prístupnosť formulára | M9, M11, e2e |
| AD-08 Predvyplnené hodnoty | e2e |

| Kritérium | Výsledok |
|-----------|----------|
| Každá požiadavka z `01-functional.md` má aspoň jeden test | Splnené: FR-01 až FR-05, IN-01 až IN-03, DR-01 až DR-04. |
| Každý modul s výpočtom má aspoň jeden hraničný prípad a jeden neplatný vstup (hraničné / neplatné) | M1 (3 / 7), M3 (2 / 15), M8 (6 / 5) – splnené podľa 01 a 02. M4 (5 / 1), M5 (7 / 1), M6 (7 / 1) – neplatný vstup závisí od potvrdenia TQ-01. |
| Aspoň jeden e2e scenár prejde od vstupu po zobrazený výsledok | Splnené: `test_e2e_zadanie_vstupov_zobrazi_vysledok`, ďalej `test_e2e_oprava_vstupu_obnovi_vysledky` a `test_e2e_maximalne_sumy_sa_nezalomia`. |

## Otvorené otázky k testom

| ID | Otázka | Dotknuté testy | Kedy rozhodnúť |
|----|--------|----------------|----------------|
| TQ-01 | `02-architecture.md` neurčuje, čo urobia M4, M5 a M6 so vstupom mimo kontraktu (`years: 0`, `NaN`). V aplikácii k tomu nedôjde, lebo M8 volá M4 iba s platnými hodnotami. Návrh: vyhodiť `RangeError` so správami `"Neplatné parametre úveru."` (M4), `"Neplatné číslo na zaokrúhlenie."` (M5) a `"Neplatná suma na formátovanie."` (M6), aby sa chyba neprejavila ako `Infinity` alebo `NaN €` na obrazovke. Ak sa návrh zamietne, M4, M5 a M6 nebudú mať test neplatného vstupu a treba zvoliť iné správanie. | `test_splatka_neplatna_doba_nula`, `test_zaokruhlenie_neplatny_vstup_nan`, `test_format_suma_neplatny_vstup_nan` | Review (04) |
| TQ-02 | `parseNumber("   ")` (iba medzery) vráti `'empty'`. Vyplýva z orezania medzier v M1, ale `01-functional.md` to výslovne neuvádza. | `test_parse_iba_medzery` | Review (04) |
| TQ-03 | Má M9 po oprave chyby atribút `aria-invalid` odstrániť, alebo nastaviť na `"false"`? Test preto overuje iba, že nie je `"true"`. | `test_view_oprava_chyby` | Review (04) |
| TQ-04 | `test_splatka_nulova_sadzba_zvysok_float` závisí od poradia operácií `monthlyPayment * n` podľa rozhrania M4. Pri inom poradí (napr. `M * years * 12`) vznikne zvyšok pri iných vstupoch a test treba upraviť. | `test_splatka_nulova_sadzba_zvysok_float` | Implementácia (05) |
| TQ-05 | Príklad v rozhraní M6 v `02-architecture.md` uvádza `formatNumber(1000000, 0) → "1 000"`. Podľa FR-04 má byť výsledok `"1 000 000"`. Pravdepodobne preklep (správne `1000, 0 → "1 000"`). Test počíta s `"1 000 000"`. | `test_format_cislo_bez_desatinnych` | Review (04) |
