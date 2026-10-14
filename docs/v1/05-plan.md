# 05 – Implementačný plán

Plán stavby V1 podľa `01-functional.md`, `02-architecture.md`, `03-test-scenarios.md` a výsledku kontroly v `04-review.md` (0 blockerov, plán schválený na realizáciu).

## 1. Ciele V1

Každý cieľ sa na konci V1 dá odškrtnúť odpoveďou áno/nie.

| # | Cieľ | Ako sa overí | Splnené |
|---|------|--------------|---------|
| C-01 | Všetkých 110 testov z `03-test-scenarios.md` (97 pôvodných + 13 nových z kontroly 04) prejde. | `npm test` (96 testov v Node.js) aj `npm run test:e2e` (14 testov v prehliadači) skončia s návratovým kódom 0 a 0 preskočenými testami. | áno / nie |
| C-02 | Každá požiadavka FR-01 až FR-05, IN-01 až IN-03, DR-01 až DR-04 a NFR-01 až NFR-04 (16 ID) má aspoň 1 zelený test, ktorý ju uvádza v názve. | Výstup testov sa prehľadá na všetkých 16 ID. Nájdených musí byť 16 zo 16. | áno / nie |
| C-03 | Aplikácia sa spustí 1 príkazom a po načítaní bez interakcie zobrazí `477,42 €`, `171 869,51 €` a `71 869,51 €`. | `npm start`, potom `test_e2e_predvyplnene_hodnoty`. | áno / nie |
| C-04 | Aplikácia má 0 závislostí za behu a 0 požiadaviek na iný pôvod. | `package.json` nemá kľúč `dependencies`; prejdú `test_ziadne_zavislosti` a `test_e2e_ziadne_externe_poziadavky`. | áno / nie |

## 2. Rozsah

Rozsah V1 je definovaný v `01-functional.md`. Funkcie z časti 5 („Mimo rozsahu V1“) sa nestavajú. Body rozšírenia EP-01 až EP-10 z `02-architecture.md` sa neimplementujú vopred.

### 2.1 Požiadavky vo V1

| Skupina | ID | Zdroj |
|---------|----|-------|
| Funkčné požiadavky | FR-01 Mesačná splátka, FR-02 Celková zaplatená suma, FR-03 Celkový zaplatený úrok, FR-04 Formát peňažných súm, FR-05 Neplatný vstup | 01 časť 2 |
| Vstupy a hranice | IN-01 Výška úveru, IN-02 Ročná úroková sadzba, IN-03 Doba splácania | 01 časť 3 |
| Doménové pravidlá | DR-01 Anuitný vzorec, DR-02 Sadzba 0 %, DR-03 Zaokrúhľovanie, DR-04 Referenčné príklady (4 riadky) | 01 časť 4 |
| Nefunkčné požiadavky | NFR-01 Odozva ≤ 100 ms, NFR-02 0 závislostí za behu, NFR-03 Moduly M1 až M8 bez DOM, NFR-04 Prístupnosť formulára | 02 Extension Points & Decisions |
| Rozhodnutia | AD-01 až AD-09 (vrátane OQ-01 → AD-01 a AD-08 potvrdeného v 04) | 02 Rozhodnutia |
| Moduly | M1 až M12 | 02 Modules |

### 2.2 Zmeny vyplývajúce z kontroly v `04-review.md`

Prijatých 12 nálezov sa zapracuje do dokumentov v kroku 0 (sekcia 4), ešte pred prvým riadkom kódu.

| Nález | Dokument | Zmena |
|------:|----------|-------|
| 1 | 01, 03 | Do 01 časť 3 doplniť: rozhoduje počet zapísaných desatinných miest vrátane koncových núl (`4,250` aj `30,0` sú neplatné). Do 03 doplniť testy `test_validacia_sadzba_koncova_nula` (`rate: "4,250"` → `'step'`) a `test_validacia_doba_koncova_nula` (`years: "30,0"` → `'step'`). |
| 2 | 01 | Výstup FR-02 preformulovať na „M × n s nezaokrúhleným M podľa DR-03“. Poznámka v UI sa presúva do V2. |
| 3 | 01, 02, 03 | AD-08 je potvrdené. Do 01 doplniť, že po načítaní sú polia predvyplnené hodnotami DR-04 r. 1 a zobrazí sa ich výsledok. V 02 odstrániť vetu „treba potvrdiť v review“. V 03 zmeniť zdroj `test_e2e_predvyplnene_hodnoty` na „01 (predvyplnené hodnoty); 04 nález 3“. |
| 4 | 02 | EP-01: v stĺpci „Čo sa nemení“ iba M1 až M3. Pravidlo poslednej splátky sa rozhodne vo V2. |
| 5 | 02 | EP-05: M4 sa mení (signatúra `LoanParams`), EP-05 závisí od EP-01 (zostatok istiny). |
| 6 | 02 | EP-08: doplniť novú funkciu M9 na zápis hodnôt do formulára. |
| 10 | 03 | Doplniť `test_zaokruhlenie_naivne_0_145` (`roundHalfUp(0.145, 2)` → `0.15`) a `test_zaokruhlenie_naivne_1_015` (`roundHalfUp(1.015, 2)` → `1.02`). Obe hodnoty naivné `Math.round(v*100)/100` zaokrúhli nesprávne. |
| 11 | 03 | Návrh TQ-01 je potvrdený: testy `RangeError` pre M4, M5 a M6 ostávajú, zdroj sa zmení na „04 nález 11“. `test_splatka_nulova_sadzba_zvysok_float` overí `Math.abs(totalInterest) < 1e-6` namiesto presnej hodnoty (uzatvára TQ-04). `test_e2e_maximalne_sumy_sa_nezalomia` overuje „02 M12“, nie FR-04. |
| 12 | 03 | Doplniť 9 testov: `test_parse_bez_celej_casti` (`",5"` → `'nan'`), `test_parse_bez_desatinnej_casti` (`"5."` → `'nan'`), `test_parse_uvodne_nuly` (`"030"` → `{ ok: true, value: 30, decimals: 0 }`), `test_validacia_sadzba_text` (`rate: "abc"` → `'nan'`), `test_validacia_doba_text` (`years: "abc"` → `'nan'`), `test_validacia_iba_medzery` (všetky 3 polia `"   "` → všetky `'empty'`), `test_validacia_tesne_vnutri_rozsahu` (`{ amount: "999999,99", rate: "19,99", years: "30" }` → platné), `test_validacia_sadzba_tesne_nad_nulou` (`rate: "0,01"` → platné), `test_vypocet_ok_bez_chyb` (`{ amount: "100000", rate: "4", years: "30" }` → objekt nemá kľúč `errors`). |
| 13 | 02 | Matica sledovateľnosti: FR-01 a FR-02 doplniť o M5 a M6, FR-05 o M2. |
| 14 | 02, 03 | Príklad M6: `formatNumber(1000000, 0) → "1 000 000"`. TQ-05 sa uzatvára. |
| 16 | 02 | V M5 nahradiť „961 kombinácií“ opakovateľným opisom: P = 1 000 až 1 000 000 po 1 000, doba 1 až 30 rokov, najväčší zvyšok 1,16e-10. |
| – | 03 | Odstrániť všetky značky NEOVERENÉ a do stĺpca Zdroj doplniť „04 Overenie referenčných hodnôt“. |

Zamietnuté nálezy 7, 8, 9 a 15 nemenia V1. Správanie, ktoré opisujú, ostáva podľa 01 a 02 (chybný vstup dostane správu s povoleným rozsahom, nikdy nesprávny výsledok).

Ďalšie zmeny vyplynuli až z prípravy tohto plánu a z kontroly plánu v `06-retro.md` (E2). Pozri sekciu 7, R-01, OQ-P1, TQ-02 a TQ-03. Zapracujú sa tiež v kroku 0:
- 02 Stack: spustenie cez `npm start` (`node scripts/serve.js`) namiesto `python -m http.server`, lebo Python na vývojovom počítači nie je nainštalovaný.
- 02 Stack: OQ-P1 je rozhodnutá. Testy v prehliadači (M9, M11, e2e) spúšťa `@playwright/test`, jediná položka v `devDependencies`.
- 02 Stack: testy sú rozdelené do 2 adresárov s 2 príponami, aby každý príkaz spustil iba svoje testy:

  | Príkaz | Skript v `package.json` | Súbory | Počet |
  |--------|-------------------------|--------|------:|
  | `npm test` | `node --test "tests/**/*.test.js"` | `tests/**/*.test.js` (Node.js) | 96 |
  | `npm run test:e2e` | `playwright test` (`testDir: "e2e"`) | `e2e/*.spec.js` (prehliadač) | 14 |

  Glob v úvodzovkách rozvinie Node.js sám, preto funguje rovnako vo Windows aj v Unixe. Overené na Node.js v24.20.0: súbory v `e2e/` sa do `npm test` nezapočítajú a pri 0 testoch je návratový kód 0.
- 03 `test_ziadne_zavislosti`: očakávaný výstup sa mení na „`package.json` nemá kľúč `dependencies`; `devDependencies` obsahuje najviac kľúč `@playwright/test`; žiadny `import`, `<script src>` ani `<link href>` neodkazuje na `http://` alebo `https://`“. Kontrola `index.html` sa vykoná, iba ak súbor existuje (od kroku 11). Zdroj: „05 OQ-P1“.
- 03 TQ-02 sa uzatvára: vstup iba z medzier je `'empty'` (zhoduje sa s nálezom 12, `test_validacia_iba_medzery`).
- 03 TQ-03 sa uzatvára: M9 po oprave chyby atribút `aria-invalid` odstráni (`removeAttribute`).

## 3. Akceptačné kritériá

### 3.1 Funkčné

V1 je akceptovaná, keď prejde každý z nasledujúcich 110 testov. Názvy zodpovedajú stĺpcu „Test“ v `03-test-scenarios.md` po zapracovaní kroku 0. Nové testy z kontroly 04 sú označené (nový).

**AK-M1 – `input/parse.js` (17 testov, Node.js):**
`test_parse_cele_cislo`, `test_parse_medzery_medzi_cislicami`, `test_parse_desatinna_ciarka`, `test_parse_desatinna_bodka`, `test_parse_orezanie_okrajovych_medzier`, `test_parse_tri_desatinne_miesta`, `test_parse_zaporne_cislo`, `test_parse_prazdny_retazec`, `test_parse_iba_medzery`, `test_parse_text`, `test_parse_exponent`, `test_parse_hexadecimalne`, `test_parse_viac_oddelovacov`, `test_parse_oddelovac_bez_cislic`, `test_parse_bez_celej_casti` (nový), `test_parse_bez_desatinnej_casti` (nový), `test_parse_uvodne_nuly` (nový)

**AK-M2 – `input/limits.js` (1 test, Node.js):**
`test_limits_podla_tabulky_vstupov`

**AK-M3 – `input/validate.js` (26 testov, Node.js):**
`test_validacia_referencne_vstupy`, `test_validacia_platne_priklady_z_tabulky`, `test_validacia_dolne_hranice`, `test_validacia_horne_hranice`, `test_validacia_vyska_uveru_pod_minimom`, `test_validacia_vyska_uveru_nad_maximom`, `test_validacia_vyska_uveru_privela_desatinnych`, `test_validacia_vyska_uveru_text`, `test_validacia_vyska_uveru_prazdna`, `test_validacia_sadzba_zaporna`, `test_validacia_sadzba_nad_maximom`, `test_validacia_sadzba_tri_desatinne`, `test_validacia_sadzba_prazdna`, `test_validacia_doba_nula`, `test_validacia_doba_nad_maximom`, `test_validacia_doba_desatinna`, `test_validacia_doba_prazdna`, `test_validacia_dve_chyby_naraz`, `test_validacia_tri_chyby_naraz`, `test_validacia_sadzba_koncova_nula` (nový), `test_validacia_doba_koncova_nula` (nový), `test_validacia_sadzba_text` (nový), `test_validacia_doba_text` (nový), `test_validacia_iba_medzery` (nový), `test_validacia_tesne_vnutri_rozsahu` (nový), `test_validacia_sadzba_tesne_nad_nulou` (nový)

**AK-M5 – `domain/rounding.js` (11 testov, Node.js):**
`test_zaokruhlenie_splatky`, `test_zaokruhlenie_polovica_nahor`, `test_zaokruhlenie_tesne_pod_polovicou`, `test_zaokruhlenie_binarna_chyba_1_005`, `test_zaokruhlenie_binarna_chyba_2_675`, `test_zaokruhlenie_na_cele_cislo`, `test_zaokruhlenie_maly_kladny_zvysok`, `test_zaokruhlenie_maly_zaporny_zvysok`, `test_zaokruhlenie_neplatny_vstup_nan`, `test_zaokruhlenie_naivne_0_145` (nový), `test_zaokruhlenie_naivne_1_015` (nový)

**AK-M4 – `domain/mortgage.js` (8 testov, Node.js):**
`test_splatka_zakladny_priklad`, `test_splatka_nulova_sadzba`, `test_splatka_bez_zaokruhlenia_medzivysledkov`, `test_splatka_minimalna_kladna_sadzba`, `test_splatka_maximalne_hodnoty`, `test_splatka_minimalne_hodnoty`, `test_splatka_nulova_sadzba_zvysok_float` (upravený podľa nálezu 11), `test_splatka_neplatna_doba_nula`

**AK-M6 – `format/money.js` (11 testov, Node.js):**
`test_format_suma_miliony`, `test_format_suma_tisic`, `test_format_suma_nula`, `test_format_suma_bez_oddelovaca_tisicov`, `test_format_suma_zaokruhlenie_cez_tisic`, `test_format_suma_milion`, `test_format_suma_bez_zapornej_nuly`, `test_format_suma_obycajne_medzery`, `test_format_cislo_bez_desatinnych`, `test_format_cislo_male`, `test_format_suma_neplatny_vstup_nan`

**AK-M7 – `text/messages.js` (4 testy, Node.js):**
`test_sprava_vyska_uveru`, `test_sprava_sadzba`, `test_sprava_doba`, `test_sprava_rovnaka_pre_vsetky_kody`

**AK-M8 – `app/calculator.js` (15 testov, Node.js):**
`test_vypocet_referencny_priklad`, `test_vypocet_referencny_priklad_nulova_sadzba`, `test_vypocet_referencny_priklad_maximum`, `test_vypocet_referencny_priklad_minimalna_sadzba`, `test_vypocet_medzery_a_ciarka`, `test_vypocet_ciarka_a_bodka_rovnako`, `test_vypocet_desatinna_vyska_uveru`, `test_vypocet_dolne_hranice`, `test_vypocet_nulova_sadzba_bez_zapornej_nuly`, `test_vypocet_neplatna_vyska_uveru`, `test_vypocet_vyska_uveru_tesne_nad_maximom`, `test_vypocet_neplatna_doba`, `test_vypocet_dve_chyby_naraz`, `test_vypocet_tri_chyby_naraz`, `test_vypocet_ok_bez_chyb` (nový)

**AK-ARCH – architektonické kontroly (3 testy, Node.js):**
`test_moduly_bez_dom`, `test_domena_a_data_bez_importov`, `test_ziadne_zavislosti`

**AK-M11 – markup (1 test, prehliadač):**
`test_view_labely_vstupov`

**AK-M9 – `ui/view.js` (5 testov, prehliadač):**
`test_view_citanie_formulara`, `test_view_vykreslenie_vysledkov`, `test_view_vykreslenie_chyby`, `test_view_oprava_chyby`, `test_view_input_vola_callback`

**AK-E2E – celá stránka (8 testov, prehliadač):**
`test_e2e_predvyplnene_hodnoty`, `test_e2e_zadanie_vstupov_zobrazi_vysledok`, `test_e2e_neplatny_vstup_skryje_vysledky`, `test_e2e_dve_chyby_naraz`, `test_e2e_oprava_vstupu_obnovi_vysledky`, `test_e2e_maximalne_sumy_sa_nezalomia`, `test_e2e_odozva_do_100ms`, `test_e2e_ziadne_externe_poziadavky`

| Skupina | Počet | Príkaz |
|---------|------:|--------|
| AK-M1, AK-M2, AK-M3, AK-M5, AK-M4, AK-M6, AK-M7, AK-M8, AK-ARCH | 96 | `npm test` |
| AK-M11, AK-M9, AK-E2E | 14 | `npm run test:e2e` |
| **spolu** | **110** | |

Test sa počíta ako splnený, iba ak beží (nie je `skip` ani `todo`) a jeho očakávaná hodnota sa zhoduje s 03. Ak test v kóde potrebuje inú očakávanú hodnotu, najprv sa opraví 03 v samostatnom commite s odôvodnením a až potom kód.

### 3.2 Technické

| # | Kritérium | Overenie |
|---|-----------|----------|
| T-01 | Príkaz na testy prejde bez chyby. | `npm test` a `npm run test:e2e` skončia s návratovým kódom 0, 0 zlyhaných, 0 preskočených testov. |
| T-02 | Aplikácia sa spustí jedným príkazom. | `npm start` spustí statický server na `http://localhost:8000` do 5 s a stránka sa načíta bez chyby v konzole. |
| T-03 | README opisuje spustenie. | `README.md` obsahuje sekciu „Spustenie“ s požadovanou verziou Node.js (≥ 22, lebo `node --test` s globom vyžaduje verziu 22) a príkazmi `npm install`, `npx playwright install chromium` (jednorazovo), `npm start`, `npm test` a `npm run test:e2e`. |
| T-04 | Každý test uvádza ID požiadavky. | Názov testu v kóde má tvar `test_<nazov> [ID, ID]`, napr. `test_parse_cele_cislo [IN-01]` (pravidlo 3 v `CLAUDE.md`). |
| T-05 | Každý modul uvádza ID požiadaviek. | Prvý riadok každého súboru v `src/` je komentár s modulom a ID z riadku „Implementuje“ v 02, napr. `// M1 – prevod textu na číslo. IN-01, IN-02, IN-03, FR-05`. |

## 4. Poradie stavby

Poradie vychádza zo sekcie Dependency Direction v `02-architecture.md`: najprv moduly bez závislostí (M2, M1, M5), potom moduly, ktoré ich používajú, a nakoniec UI a vstupný bod. M5 je pred M4, lebo testy M4 porovnávajú výsledky cez `roundHalfUp` z M5.

Každý krok končí presne jedným commitom a pushom (pravidlo 4 v `CLAUDE.md`).

| Krok | Modul | Súbory | Testy, ktoré musia prejsť | Commit |
|-----:|-------|--------|---------------------------|--------|
| 0 | – (dokumentácia) | `docs/v1/01-functional.md`, `02-architecture.md`, `03-test-scenarios.md` | žiadne (kód ešte neexistuje); kontrola: 03 má 110 riadkov testov a 0 značiek NEOVERENÉ | `Zapracovanie nálezov z review 04 do 01, 02 a 03` |
| 1 | kostra projektu | `package.json`, `scripts/serve.js`, `README.md`, `.claude/settings.json`, `.claude/skills/end-session/SKILL.md`, `.gitattributes` | `npm test` skončí s kódom 0 (0 testov); `npm start` vráti na `http://localhost:8000/` odpoveď 200 | `Kostra projektu: package.json, statický server, README` |
| 2 | M2 | `src/input/limits.js`, `tests/input/limits.test.js` | AK-M2 (1) | `M2 limits: hranice vstupov (IN-01 až IN-03)` |
| 3 | M1 | `src/input/parse.js`, `tests/input/parse.test.js` | AK-M1 (17) + AK-M2 | `M1 parse: prevod textu na číslo (IN-01 až IN-03, FR-05)` |
| 4 | M3 | `src/input/validate.js`, `tests/input/validate.test.js` | AK-M3 (26) + všetky predchádzajúce | `M3 validate: validácia vstupov (IN-01 až IN-03, FR-05)` |
| 5 | M5 | `src/domain/rounding.js`, `tests/domain/rounding.test.js` | AK-M5 (11) + všetky predchádzajúce | `M5 rounding: zaokrúhľovanie polovica nahor (DR-03)` |
| 6 | M4 | `src/domain/mortgage.js`, `tests/domain/mortgage.test.js` | AK-M4 (8) + všetky predchádzajúce | `M4 mortgage: výpočet splátky a súm (FR-01 až FR-03, DR-01, DR-02)` |
| 7 | M6 | `src/format/money.js`, `tests/format/money.test.js` | AK-M6 (11) + všetky predchádzajúce | `M6 money: slovenský formát súm (FR-04, DR-03)` |
| 8 | M7 | `src/text/messages.js`, `tests/text/messages.test.js` | AK-M7 (4) + všetky predchádzajúce | `M7 messages: chybové správy (FR-05)` |
| 9 | M8 | `src/app/calculator.js`, `tests/app/calculator.test.js` | AK-M8 (15) + všetky predchádzajúce | `M8 calculator: orchestrácia výpočtu (FR-01 až FR-05, DR-04)` |
| 10 | architektonické kontroly | `tests/architecture.test.js` | AK-ARCH (3) + všetky predchádzajúce; `npm test` = 96 testov | `Architektonické kontroly (NFR-02, NFR-03)` |
| 11 | M11, M12 + nástroj pre testy v prehliadači | `index.html`, `styles.css`, `package.json`, `package-lock.json`, `playwright.config.js`, `e2e/markup.spec.js`, `README.md` | AK-M11 (1) + `npm test` (96, vrátane `test_ziadne_zavislosti` nad `index.html` a `devDependencies`) | `M11 markup a M12 štýly (NFR-04, AD-03, AD-08)` |
| 12 | M9 | `src/ui/view.js`, `e2e/view.spec.js` | AK-M9 (5) + všetky predchádzajúce | `M9 view: DOM adaptér (FR-05, NFR-04, AD-01)` |
| 13 | M10 + e2e | `src/main.js`, `index.html` (iba značka `<script>`), `e2e/e2e.spec.js` | AK-E2E (8) + všetky predchádzajúce; `npm test` = 96, `npm run test:e2e` = 14 | `M10 main a e2e testy (OQ-01, NFR-01, NFR-02)` |
| 14 | záverečná kontrola | `README.md`, `docs/handoff.md`, `docs/v1/06-retro.md`; súbory v `src/`, `tests/` a `e2e/` iba pri úpravách z `/simplify` | všetkých 110 (počet testov sa nezmení); ciele C-01 až C-04 a kritériá T-01 až T-05 odškrtnuté | `V1 hotová: akceptačné kritériá splnené` |

Poznámky ku krokom:
- **Krok 0** je jediný krok bez kódu. Bez neho by testy v kóde vychádzali z 03, ktoré ešte nemá nálezy z 04.
- **Krok 6:** pred commitom subagent nezávisle prepočíta hodnoty testov AK-M4 (sekcia 6).
- **Krok 9:** pred commitom subagent nezávisle prepočíta všetky výstupné reťazce AK-M8.
- **Krok 1:** `.gitattributes` s `* text=auto eol=lf` vzniká hneď, nie až pri zlyhaní (R-07).
- **Krok 10:** `test_ziadne_zavislosti` sa píše už podľa upraveného 03 (kontrola `index.html`, iba ak existuje; `devDependencies` najviac `@playwright/test`). V kroku 11 sa preto `tests/architecture.test.js` nemení.
- **Krok 11:** `README.md` dostane príkaz na jednorazovú inštaláciu prehliadača (`npx playwright install chromium`). `test_ziadne_zavislosti` odteraz reálne kontroluje aj `index.html`. `index.html` v krokoch 11 a 12 ešte nenačítava `src/main.js` (vznikne v kroku 13), aby v konzole nebola chyba 404 (T-02). Značka `<script type="module" src="src/main.js">` sa pridá v kroku 13 a `index.html` sa preto pridáva aj do súborov kroku 13.
- **Krok 13:** `test_e2e_maximalne_sumy_sa_nezalomia` sa okrem automatického testu overí aj vizuálne pri šírke 320 px (sekcia 6).

## 5. Definition of Done pre každý krok

Krok je hotový, až keď platí všetkých 6 bodov:

| # | Podmienka | Overenie |
|---|-----------|----------|
| D-01 | Testy daného modulu sú zelené. | Všetky testy skupiny AK z riadku kroku v sekcii 4 prejdú. Žiadny nie je `skip` ani `todo`. |
| D-02 | Staré testy ostávajú zelené. | `npm test` (od kroku 11 aj `npm run test:e2e`) skončí s kódom 0. Počet testov sa oproti predchádzajúcemu kroku zvýši presne o počet testov kroku. |
| D-03 | Testy a modul uvádzajú ID požiadaviek. | Každý nový test spĺňa T-04, každý nový súbor v `src/` spĺňa T-05. |
| D-04 | Zmenili sa iba súbory kroku. | `git status` ukazuje iba súbory zo stĺpca „Súbory“ a `docs/handoff.md`. Zmena iného súboru je samostatný krok s vlastným commitom. |
| D-05 | Jeden commit a push. | Presne 1 commit so správou zo sekcie 4, potom `git push`. |
| D-06 | Handoff je aktualizovaný. | `docs/handoff.md` (v tom istom commite) uvádza: posledný hotový krok, počet zelených testov, otvorené otázky a ďalší krok. |

## 6. Nástroje pri stavbe

| Nástroj | Typ | Kedy | Prečo |
|---------|-----|------|-------|
| Hook na testy | hook `PostToolUse` v `.claude/settings.json` (krok 1) | po každej úprave súboru v `src/` alebo `tests/` (nástroje Edit a Write) spustí `npm test` | Zlyhaný test sa ukáže hneď po zmene, nie až pri commite. Plní D-02 automaticky. `npm test` trvá pod 2 s, preto nespomaľuje prácu. |
| `/end-session` | vlastný skill v `.claude/skills/end-session/` (krok 1) | na konci každého kroku a každej relácie | Jednotne vykoná D-02, D-05 a D-06: spustí `npm test` a navyše `npm run test:e2e`, iba ak `package.json` obsahuje skript `test:e2e` (od kroku 11; v krokoch 1 až 10 skript neexistuje a nespúšťa sa). Potom aktualizuje `docs/handoff.md` podľa šablóny, vytvorí commit so správou zo sekcie 4 a pushne. Pri zlyhanom teste skončí bez commitu. |
| Kontrola výpočtu subagentom | subagent (`general-purpose`) | kroky 6 a 9, pred commitom | Subagent nedostane implementáciu, iba vstupy z 03. Hodnoty prepočíta racionálnou aritmetikou cez `BigInt` ako v 04 a porovná ich s očakávanými hodnotami v testoch. Chráni pred tým, aby sa test prispôsobil chybnému kódu. |
| Kontrola sledovateľnosti subagentom | subagent (`Explore`) | krok 14 | Overí C-02 a T-04: každé zo 16 ID požiadaviek sa nachádza v názve aspoň jedného testu a každý test z 03 existuje v kóde pod rovnakým názvom. |
| `/code-review` | vstavaný skill | kroky 9, 12 a 13 (moduly, ktoré spájajú ostatné) | Hľadá chyby v orchestrácii a DOM adaptéri, ktoré jednotkové testy nemusia zachytiť (napr. zabudnuté odstránenie `aria-invalid`). |
| `/simplify` | vstavaný skill | krok 14 | Odstráni duplicitu v kóde pred uzavretím V1, bez zmeny správania (testy musia ostať zelené). |
| Playwright MCP | MCP server prehliadača | kroky 11 až 13 | Ručné vizuálne overenie stránky pri šírke 320 px a kontrola konzoly. Dopĺňa automatické testy v prehliadači, nenahrádza ich. |

## 7. Riziká a otvorené otázky

### 7.1 Riziká

| # | Riziko | Čo urobíme, keď nastane |
|---|--------|-------------------------|
| R-01 | Python, s ktorým počíta 02 Stack (`python -m http.server`), nie je na vývojovom počítači nainštalovaný. Overené: `python --version` zlyhá, Node.js je v24.20.0. | Spúšťací skript `scripts/serve.js` (približne 30 riadkov, iba vstavané moduly `node:http`, `node:fs`, `node:path`, 0 závislostí). Zmena sa zapíše do 02 Stack v kroku 0. |
| R-02 | Stiahnutie prehliadača pre Playwright (`npx playwright install chromium`) v kroku 11 zlyhá (sieť, firemný proxy). | V `playwright.config.js` sa nastaví `channel: "msedge"` a testy pobežia v nainštalovanom Microsoft Edge (overené: `msedge.exe` je na počítači). Počet testov (14) ani `devDependencies` sa nemenia. Zmena sa zapíše do `README.md`. |
| R-03 | M5: posun exponentu cez reťazec zlyhá, ak `String(value)` vráti exponenciálny zápis (`1e-7`, `1e21`). | Hodnoty pod 1e-6 rieši pravidlo z 02 M5. Najväčšia suma vo V1 je 6 015 667,27, teda ďaleko pod 1e21. Ak test zlyhá, nová hodnota sa doplní ako test do 03 a M5 sa opraví bez zmeny rozhrania. |
| R-04 | Test M4 alebo M8 zlyhá kvôli inému poradiu operácií v type `number`. | Upraví sa kód podľa vzorca v rozhraní M4 (`monthlyPayment * n`), nie očakávaná hodnota. Hodnoty sú dvakrát nezávisle overené v 04. Ak by sa líšil výsledok aj pri vzorci z 02, rozhodne subagent výpočtom cez `BigInt`. |
| R-05 | Odozva nad 100 ms (`test_e2e_odozva_do_100ms`) kvôli pomalému štartu prehliadača, nie kvôli výpočtu. | Meria sa od poslednej udalosti `input` po zmenu textu cez `performance.now()` v stránke, nie čas celého testu. Opakovanie testov je vypnuté (`retries: 0`). Každé zlyhanie je chyba: krok sa neuzavrie, kým sa príčina v M9 alebo M10 neodstráni (T-01 platí bez výnimky). V kroku 14 musí `npm run test:e2e` prejsť 3× za sebou (3 z 3 behov, 0 zlyhaných). Hranica 100 ms sa nezvyšuje bez zmeny NFR-01 v 02. |
| R-06 | Pri šírke 320 px sa suma `6 015 667,27 €` nezmestí do riadku. | `white-space: nowrap` ostáva (M12). Upraví sa rozloženie: popis a hodnota pod sebou, menšie písmo hodnoty. Test sa nemení. |
| R-07 | Architektonické testy na Windows zlyhajú kvôli cestám alebo koncom riadkov (`\r\n`). | Cesty cez `node:path`, regulárne výrazy s `\r?\n`. `.gitattributes` s `* text=auto eol=lf` je v repozitári už od kroku 1. |
| R-08 | Kód sa odchýli od dokumentov (test v kóde má inú hodnotu než 03). | 03 je zdroj pravdy. Zmena očakávanej hodnoty ide najprv do 03 v samostatnom commite s odôvodnením (pravidlo v 3.1). Krok 14 to skontroluje subagentom. |
| R-09 | `git push` zlyhá (overenie na GitHube, sieť). | Commit ostane lokálne a zlyhanie sa zapíše do `docs/handoff.md`. Ďalší krok nezačne, kým push neprejde, aby na GitHube nechýbali kroky. |

### 7.2 Otvorené otázky

| # | Otázka | Návrh | Kedy rozhodnúť |
|---|--------|-------|----------------|
| OQ-P1 | Ktorý nástroj spustí 14 testov v prehliadači? `test_ziadne_zavislosti` dnes zakazuje `devDependencies`, ale NFR-02 hovorí iba o závislostiach **za behu**. | **Rozhodnuté (2026-10-15):** jediná vývojová závislosť `@playwright/test` v `devDependencies`. `test_ziadne_zavislosti` kontroluje kľúč `dependencies`, obsah `devDependencies` a externé URL (sekcia 2.2). Aplikácia ostane bez závislostí za behu (C-04). Alternatíva bez závislostí (vlastné ovládanie prehliadača cez Chrome DevTools Protocol) bola zamietnutá, lebo je krehká a pracná. | Uzavreté. Zmena 02 Stack a 03 sa zapracuje v kroku 0. |
| TQ-02 | Je vstup iba z medzier `'empty'`? (otvorené z 03, review nerozhodlo) | **Rozhodnuté (2026-10-15):** áno, `'empty'`. Vyplýva z orezania medzier v M1 a používateľ dostane rovnakú správu ako pri prázdnom poli. Predpokladajú to `test_parse_iba_medzery` a nový `test_validacia_iba_medzery` (nález 12). | Uzavreté. Zapracuje sa v kroku 0. |
| TQ-03 | Má M9 po oprave chyby atribút `aria-invalid` odstrániť, alebo nastaviť na `"false"`? (otvorené z 03, review nerozhodlo) | **Rozhodnuté (2026-10-15):** odstrániť (`removeAttribute`). Platné pole nepotrebuje atribút a `aria-describedby` sa odstráni spolu s ním. Test overuje iba, že hodnota nie je `"true"`, preto sa nemení. | Uzavreté. Zapracuje sa v kroku 0. |
| TQ-04 | Závislosť testu zvyšku pri 0 % od poradia operácií. | Uzatvára ju nález 11: test overí `\|úrok\| < 1e-6`. | Uzavreté v kroku 0. |
| TQ-05 | Preklep v príklade M6. | Uzatvára ho nález 14. | Uzavreté v kroku 0. |
