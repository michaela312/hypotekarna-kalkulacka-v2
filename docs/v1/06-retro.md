# 06 – Retrospektíva

## Experiment E1: bez plánu vs. s plánom

**Otázka:** Koľko scenárov z `03-test-scenarios.md` splní kalkulačka, ktorú agent postaví bez akýchkoľvek podkladov?

**Dátum:** 2026-10-14.

### Postup

1. Nový subagent (`general-purpose`, ten istý model ako pri plánovaní) dostal iba prompt:
   > Build a mortgage calculator.

   Okrem promptu dostal len pokyn pracovať v izolovanom priečinku `scratchpad/e1-noplan` a nečítať súbory mimo neho. `docs/v1/` nevidel. `CLAUDE.md` projektu sa mu načítal automaticky, ale podľa neho nepostupoval (pozri Obmedzenia).
2. Výstup agenta sa vyhodnotil voči všetkým 97 scenárom z `03`:
   - výpočet a validácia priamo v Node.js (`mortgage.js`);
   - stránka v Chromiu cez Playwright MCP a lokálny statický server (písanie do polí, čítanie zobrazeného textu).
3. Scenáre z `03` sú písané voči rozhraniam modulov M1 až M12 (`parseNumber`, `formatMoney`, `[data-result]` …). Kód bez plánu tieto rozhrania nemá. Preto sa hodnotilo **správanie**: rovnaký vstup sa zadal do ekvivalentnej funkcie alebo do formulára a porovnal sa výsledok s očakávaným výstupom. Scenáre bez akéhokoľvek ekvivalentu sú označené N/A.

### 1. Priebeh: čo agent postavil

Za 106 s a 16 krokov vznikli 3 súbory, 260 riadkov:

| Súbor | Obsah |
|-------|-------|
| `mortgage.js` (78 r.) | anuitný vzorec, 0 % úrok (`P / n`), splátkový kalendár, mimoriadne splátky, validácia |
| `index.html` (132 r.) | formulár s `type="number"`, prepočet pri udalosti `input`, kalendár po rokoch/mesiacoch, export CSV, svetlý/tmavý režim |
| `mortgage.test.js` (50 r.) | 7 testov, všetky zelené (`node --test`) |

Rozhodnutia, ktoré agent urobil sám, lebo mu ich nikto nezadal:

| Téma | Bez plánu | Plán (01/02) |
|------|-----------|--------------|
| Jazyk | angličtina (`lang="en"`, anglické správy) | slovenčina |
| Formát súm | `en-IE`: `€171,869.51` | `171 869,51 €` (FR-04) |
| Výška úveru | > 0, bez hornej hranice | 1 000 až 1 000 000 € (IN-01) |
| Sadzba | 0 až 100 % | 0 až 20 % (IN-02) |
| Doba | 1 až 50 rokov | 1 až 30 rokov (IN-03) |
| Kontrola počtu desatinných miest | žiadna | krok 0,01 / 1 (IN-01 až IN-03) |
| Predvyplnené hodnoty | 150 000 / 4,5 / 30 | 100 000 / 4 / 30 (AD-08) |
| Chybové správy | jeden spoločný zoznam nad výsledkami | správa pri každom poli, `aria-invalid`, `aria-describedby` (NFR-04) |
| Rozsah | + splátkový kalendár, mimoriadne splátky, CSV, graf | tieto funkcie sú výslovne mimo V1 (01 časť 5) |
| Testy | 7 | 97 v `03`, 110 po zapracovaní 04 |

Agent počas práce sám našiel a opravil jednu chybu: súčet zaokrúhlených splátok sa líšil od výšky úveru o 1,57 €. Opravil to sčítaním nezaokrúhlených hodnôt.

### 2. Porovnanie: koľko scenárov prešlo

#### Verzia bez plánu (namerané)

| Časť `03` | Scenárov | Prešlo | Zlyhalo | N/A | Hlavná príčina zlyhaní |
|-----------|---------:|-------:|--------:|----:|------------------------|
| M1 prevod textu | 14 | 10 | 4 | 0 | `0x10` → 10 €, `1,2,3` → 1,23, `3,` → 3, `1e3` → 1000 sú prijaté ako čísla |
| M2 hranice | 1 | 0 | 1 | 0 | iné hranice (> 0 / 0–100 / 1–50) |
| M3 validácia | 19 | 12 | 7 | 0 | prijme `999,99`, `1000000,01`, `100,005`, `20,01`, `3,125`, `31` |
| M4 výpočet | 8 | 6 | 1 | 1 | `years: 0` vráti `Infinity` namiesto chyby |
| M5 zaokrúhľovanie | 9 | 6 | 2 | 1 | vráti `-0`; `NaN` prepustí bez chyby |
| M6 formát | 11 | 0 | 9 | 2 | anglický formát `€1,000.00`, `-€0.00`, `€NaN` |
| M7 správy | 4 | 0 | 4 | 0 | anglické správy s inými rozsahmi |
| M8 orchestrácia | 14 | 0 | 14 | 0 | formát súm (9×), chýbajúca validácia hraníc (5×) |
| Architektonické kontroly | 3 | 2 | 1 | 0 | výpočtový súbor odkazuje na `window` |
| M9 DOM adaptér | 6 | 3 | 1 | 2 | chyby bez `aria-invalid` a bez väzby na pole |
| E2E | 8 | 1 | 7 | 0 | formát súm, iné predvyplnené hodnoty, `999` neprejde ako chyba |
| **Spolu** | **97** | **40 (41 %)** | **51 (53 %)** | **6 (6 %)** | |

Konkrétne prípady:

- **0 % úrok je ošetrený správne.** 12 000 € / 0 % / 1 rok dá splátku 1 000, celkom 12 000, úrok 0. Hypotéza o chýbajúcom ošetrení 0 % sa **nepotvrdila**.
- **Zaokrúhľovanie výsledkov je správne.** Všetkých 11 číselných očakávaní z `01` DR-04 a `03` M8/e2e sa zhoduje na centy, napríklad 477,42 / 171 869,51 / 71 869,51 aj 1 000,05 / 0,05 pri 0,01 %. `round2(1.005) = 1.01` a `round2(2.675) = 2.68`. Jediná odchýlka je `-0` pri zápornom zvyšku (M5).
- **Validácia chýba.** Úver 999 € (príklad 1 z FR-05) sa vypočíta: splátka 4,77 €, žiadna chyba. Rovnako 31 rokov, sadzba 20,01 % aj úver 100,005 €.
- **Formát je zlý vo všetkých 9 scenároch s výsledkom.** Zobrazí sa `€477.42` namiesto `477,42 €`.
- **Prevod textu funguje iba vďaka prehliadaču.** `150 000` a `3,5` prešli preto, lebo ich Chromium v poli `type="number"` sám prevedie. Kód aplikácie volá `parseFloat`, ktorý z `"150 000"` urobí 150 a z `"3,5"` urobí 3. V inom prehliadači či lokalizácii sa to nemuselo overiť.

#### Verzia s plánom (hlavná vetva `main`)

Na `main` zatiaľ **neexistuje kód**: plán je hotový (vrstvy 1 až 5), implementácia je časť B. Počet prejdených testov sa preto zatiaľ nedá zmerať. Zmerať sa dá toto:

| Ukazovateľ | Bez plánu | S plánom |
|------------|-----------|----------|
| Scenáre s presne určeným očakávaným výstupom | 0 (agent si kritériá určil sám) | 97 z 97 |
| Overené referenčné hodnoty | 2 hodnoty v jeho vlastných testoch | 11 z 11, nezávisle cez `BigInt` (04) |
| Splnené scenáre z `03` | 40 z 97 (41 %) | podľa AK v `05`: všetkých 110 musí prejsť, inak krok nie je hotový (D-01 až D-06) |
| Funkcie mimo rozsahu V1 | 4 (kalendár, mimoriadne splátky, CSV, graf) | 0 |
| Požiadavky s ID v module a teste | 0 | všetky (matica sledovateľnosti v 02 a 03) |

Úplné porovnanie „prešlo / neprešlo“ bude možné až po kroku 14 z `05-plan.md`. Vtedy treba tento dokument doplniť (pozri Ďalšie kroky).

### 3. Záver: prečo má metodika zmysel

1. **Plánovanie neopravilo výpočet, ale určilo, čo je správne.** Výpočtové jadro bez plánu bolo numericky správne. Agent vzorec aj 0 % úrok pozná. Zlyhal na tom, čo z promptu „Build a mortgage calculator.“ nevyplýva: slovenský formát, hranice vstupov, krok desatinných miest, texty chýb, prístupnosť a správanie pri vstupe mimo kontraktu (`-0`, `NaN`, `Infinity`, TQ-01). Ani jedno z 51 zlyhaní nie je chyba vzorca.
2. **Bez plánu nie je čím merať.** 7 testov agenta je zelených, lebo si ich napísal podľa vlastných predpokladov. Proti `03` z rovnakého kódu prejde 41 %. Zelené testy bez nezávislých kritérií neznamenajú hotovú aplikáciu.
3. **Čísla namiesto prídavných mien (pravidlo 2 v `CLAUDE.md`) sa ukázali ako kľúčové.** Každé zlyhanie v tabuľke vyššie je odchýlka od konkrétneho čísla alebo reťazca z `01` (1 000 až 1 000 000 €, `477,42 €`, presné texty chýb). Bez nich by sa nedalo rozhodnúť, či je `€477.42` chyba.
4. **Rozsah sa bez plánu nafúkne.** Agent pridal 4 funkcie, ktoré `01` časť 5 výslovne odkladá. Splátkový kalendár mal pritom vlastnú chybu zaokrúhlenia (1,57 €), ktorú musel opravovať. Toto je presne dôvod, prečo je kalendár mimo V1.
5. **Cena plánu je vyššia, ale predvídateľná.** Bez plánu: 1 prompt, 106 s, výsledok splní 41 % kritérií a nie je jasné, čo ďalej. S plánom: 5 vrstiev dokumentov pred prvým riadkom kódu, ale každý krok stavby má zoznam testov, ktoré musia prejsť.

### Obmedzenia experimentu

- **n = 1.** Jeden beh jedného agenta. Iný beh by mohol zvoliť iný formát alebo hranice.
- Subagent mal v kontexte `CLAUDE.md` projektu (pravidlá, nie obsah `docs/v1/`). Výsledok to podľa všetkého neovplyvnilo, lebo pravidlá ignoroval.
- Hodnotilo sa správanie, nie rozhrania. Pri striktnom hodnotení podľa mien funkcií a selektorov z `03` by prešlo 0 z 97.
- Strana „s plánom“ ešte nemá implementáciu, takže porovnanie je zatiaľ medzi nameraným výsledkom a záväznými kritériami, nie medzi dvoma nameranými výsledkami.

### Ďalšie kroky

- Po kroku 14 z `05-plan.md` spustiť `npm test` a `npm run test:e2e` a doplniť sem skutočný počet prejdených testov verzie s plánom.

## Experiment E2: kontrola v tej istej session vs. v čistej session

**Otázka:** Nájde kontrolór s kontextom autora (tá istá session) menej chýb ako kontrolór bez neho (čistá session)? Inými slovami: potvrdzuje kontrola v autorskej session iba vlastné predpoklady?

**Dátum:** 2026-10-15.

**Kontrolovaný dokument:** `05-plan.md` voči `01` až `04` (stav commitu `f4015fc`). Podľa `handoff.md` je to ďalší krok („test kvality plánu“).

### Postup

1. Obidve časti dostali **rovnaké zadanie kontroly** (`prompts.md`, sekcia 06 – E2) a rovnakú stupnicu závažnosti ako v `04`: blocker, major, minor. Bežali súbežne ako dva subagenty (`general-purpose`, rovnaký model).
2. **Časť A – tá istá session (autorský kontext).** Kontrolór dostal rámec „si autor plánu a pokračuješ v session, v ktorej si ho vytvoril“. Pred kontrolou si prečítal `handoff.md` a `prompts.md`, teda autorove poznámky vrátane záznamu, že review (04) skončilo s 0 blockermi a plán je schválený.
3. **Časť B – čistá session.** Kontrolór smel čítať iba `01` až `05`. Zakázané mal `handoff.md`, `prompts.md`, `06-retro.md` aj git históriu.
4. Nálezy oboch častí sa porovnali. Nálezy, ktoré opisujú ten istý problém, sa zlúčili do jedného. Pri 6 zo 7 majorov z časti B sa citované riadky v `05`, `03` a `02` overili ručne a všetky sedia.

### 1. Výsledky

| Ukazovateľ | Časť A (tá istá session) | Časť B (čistá session) |
|------------|-------------------------:|-----------------------:|
| Blocker | 0 | 0 |
| Major | 5 | 7 |
| Minor | 9 | 13 |
| **Nálezy spolu** | **14** | **20** |
| Rôzne problémy (po zlúčení duplicít) | 14 z 22 (64 %) | 18 z 22 (82 %) |
| Nálezy, ktoré našla iba táto časť | 4 | 8 |
| Čas / volania nástrojov | 150 s / 11 | 127 s / 6 |
| Verdikt | nepripravený na realizáciu | pripravený až po oprave 7 majorov |

Spolu ide o 22 rôznych problémov. 10 z nich našli obidve časti, 4 iba časť A a 8 iba časť B.

**Nájdené v oboch častiach (10).** Patria sem všetky problémy závažnosti major:

| Problém | A | B |
|---------|---|---|
| OQ-P1 sa podľa §2.2 zapracuje v kroku 0, podľa R-02 a §7.2 až pred krokom 11 | major | major |
| `node --test` bez cesty spustí aj `tests/browser/*.test.js`, takže `npm test` = 96 neplatí | major | major |
| `test_ziadne_zavislosti` (03) zakazuje `devDependencies`, ktoré krok 11 pridá, a súbor testu nie je v kroku 11 | major | major |
| `/end-session` spúšťa `test:e2e` aj v krokoch 1 až 10, keď tento skript ešte neexistuje | major | major |
| Súbory mimo stĺpca „Súbory“ (skill v kroku 1, `.gitattributes`, `/simplify` v kroku 14) porušujú D-04 | major | 2× major |
| R-05 „3× / aspoň 2×“ je nejasné a odporuje T-01 („0 zlyhaných“) | minor | major |
| `test_e2e_maximalne_sumy_sa_nezalomia` po náleze 11 nemá ID požiadavky | minor | minor |
| Rozdiely v `04` pri EP-09 (a EP-05) sa do `02` nedostanú | minor | minor |
| Nemerateľné formulácie (R-06 „menšie písmo“, hook „pod 2 s“) | minor | minor |
| Úvod §4 neopisuje skutočné poradie krokov (M3 je pred M5) | minor | minor |

**Iba časť A (4):** krok 0 neaktualizuje tabuľku pokrytia v `03`, TQ-02 je fakticky rozhodnutý nálezom 12, ID v správach commitov (kroky 6 a 12) sa líšia od `02`, chýba náhradné riešenie, ak sa OQ-P1 zamietne.

**Iba časť B (8):** 4 hodnoty z `03` nie sú v `04` overené, hoci ich plán označí ako overené. 2 nové testy nemajú presný výstup (iba „→ platné“). Predvyplnené hodnoty nemajú ID požiadavky. Formát `test_<nazov> [ID]` (T-04) je v rozpore s „rovnakým názvom ako v 03“. T-05 vynecháva M11 a M12 mimo `src/`. TQ-02 chýba v tabuľke kroku 0. Riadok 19 v `02` („iba … `test`“) sa neaktualizuje. `index.html` v krokoch 11 a 12 načítava `src/main.js`, ktorý ešte neexistuje (404 v konzole, v rozpore s T-02).

### 2. Čo z toho vyplýva

- **Čistá session našla o 43 % viac nálezov (20 vs. 14) a o 4 rôzne problémy viac (18 vs. 14).** Kontrolór A prehliadol 8 z 22 problémov (36 %), kontrolór B 4 (18 %).
- **Rozdiel je v šírke, nie v tom najzávažnejšom.** Všetkých 5 problémov závažnosti major, ktoré našla časť A, našla aj časť B. Nálezy iba z časti B sa týkajú takmer výhradne sledovateľnosti a presnosti testov (ID, presné výstupy, overenie hodnôt). To sú presne miesta, kde autor „vie, čo tým myslel“, a preto medzeru nevidí.
- **Autorský kontext má aj prínos.** 2 zo 4 nálezov, ktoré našla iba časť A (TQ-02 je už rozhodnutý, chýba záložné riešenie pre OQ-P1), vyžadujú poznať históriu rozhodnutí. Autorský kontext teda nie je bezcenný, iba nestačí sám.
- **Skutočná tá istá session plán odovzdala ako hotový.** Session, ktorá napísala `05`, ho commitla a v handoffe ho označila za hotový, pričom neuviedla ani jeden z 5 majorov, ktoré teraz nezávisle našli obidva kontrolóri. Rozpor medzi D-04 a stĺpcom „Súbory“ by sa prejavil už v kroku 1.

### 3. Záver: prečo je pravidlo nezávislosti vo Vrstve 4 kľúčové

1. **Autor kontroluje to, čo zamýšľal, nie to, čo napísal.** Z 8 problémov, ktoré našla iba čistá session, 7 vzniká medzi dvoma miestami dokumentov (napr. T-04 vs. „rovnaký názov“, T-05 vs. M11/M12, §2.2 vs. `04`). Kto pozná zámer, v hlave ich spojí a rozpor neuvidí.
2. **Kontrola v tej istej session má tendenciu potvrdiť, že je hotovo.** Pôvodná autorská session odovzdala `05` bez jediného nálezu. Nezávislé kontroly našli 5 až 7 majorov. Bez kontroly v čistom kontexte by sa tieto chyby ukázali až pri stavbe: v kroku 1 (`/end-session`, D-04) a v kroku 11 (`npm test`, `test_ziadne_zavislosti`). Tam je oprava drahšia, lebo už existuje kód a commity.
3. **Nezávislosť je lacná.** Časť B trvala 127 s a 6 volaní nástrojov, menej ako časť A. Nezávislá kontrola teda nič nestojí navyše, iba musí bežať v novom kontexte.
4. **Pravidlo pre ďalšie vrstvy:** kontrolu robí session alebo subagent, ktorý nevidí `handoff.md`, prompty ani históriu, iba kontrolované dokumenty. Autorský kontext sa môže pridať ako **druhá**, doplnková kontrola, nie ako náhrada. Plán `05` už takto počíta so subagentmi v krokoch 6, 9 a 14.

### Obmedzenia experimentu

- **n = 1** pre každú časť. Rozdiel 14 vs. 20 je z jedného behu a pri opakovaní sa môže zmeniť.
- **Časť A je simulácia.** Skutočná autorská session (tá, ktorá napísala `05`) už neexistuje. Kontrolór A dostal autorove poznámky a rámec „si autor“, ale nie jeho skutočné úvahy počas písania. Skutočné skreslenie autora je preto pravdepodobne väčšie, ako ukazuje tabuľka.
- Kontrolór A dostal pokyn „skontroluj“ s rovnakou stupnicou, nie „potvrď“, a plán neschválil (verdikt „nepripravený“). Autorská session bez explicitného zadania kontroly ho odovzdala ako hotový (bod 2 v Závere).
- Zlučovanie duplicít a počet rôznych problémov (22) je ručné rozhodnutie. Hranica medzi „ten istý“ a „podobný“ problém je subjektívna.

### Ďalšie kroky

- Pred krokom 0 opraviť v `05-plan.md` 5 spoločných majorov a R-05, potom posúdiť minor nálezy z oboch častí (spolu 22 problémov).
