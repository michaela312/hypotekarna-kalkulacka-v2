# 04 – Review

## Rozsah kontroly

Nezávislá kontrola dokumentov `01-functional.md`, `02-architecture.md` a `03-test-scenarios.md` (stav commitu `dddb490`).

Kontrolór overoval:
1. Pokrytie: každá požiadavka má modul a test a každý test overuje skutočnú požiadavku.
2. Nejednoznačné požiadavky, ktoré pripúšťajú dve implementácie s rôznym výsledkom.
3. Chýbajúce hraničné prípady a neplatné vstupy.
4. Moduly, ktoré by sa museli zmeniť pri 3 funkciách mimo rozsahu V1.
5. Všetky referenčné hodnoty, prepočítané v samostatnom skripte.

## Overenie referenčných hodnôt

Hodnoty sa prepočítali dvoma nezávislými skriptmi v Node.js:
- **presný výpočet** – racionálna aritmetika cez `BigInt`, bez čísel s pohyblivou desatinnou čiarkou;
- **výpočet podľa 02** – vzorec z M4 a zaokrúhlenie posunom exponentu z M5 v type `number`.

| P (€) | Sadzba (%) | Roky | Presne: splátka · celkom · úrok | Zdroj | Výsledok |
|------:|-----------:|-----:|---------------------------------|-------|----------|
| 100 000 | 4 | 30 | 477,4152954654… → 477,42 · 171 869,51 · 71 869,51 | 01 DR-04 r. 1 | zhoda |
| 12 000 | 0 | 1 | 1 000,00 · 12 000,00 · 0,00 | 01 DR-04 r. 2 | zhoda |
| 1 000 000 | 20 | 30 | 16 710,1868… → 16 710,19 · 6 015 667,2704902… → 6 015 667,27 · 5 015 667,27 | 01 DR-04 r. 3 | zhoda |
| 1 000 | 0,01 | 1 | 83,33784… → 83,34 · 1 000,05416… → 1 000,05 · 0,05416… → 0,05 | 01 DR-03, DR-04 r. 4 | zhoda |
| 150 000 | 3,5 | 25 | 750,94 · 225 280,61 · 75 280,61 | 03 M8, e2e | zhoda |
| 100 000 | 3,5 | 30 | 449,04 · 161 656,09 · 61 656,09 | 03 M8 | zhoda |
| 99 999,99 | 4,25 | 25 | 541,74 · 162 521,41 · 62 521,42 | 03 M8 | zhoda |
| 1 000 | 0 | 1 | 83,33 · 1 000,00 · 0,00 | 03 M4, M8 | zhoda |
| 1 000 | 0 | 29 | 2,87 · 1 000,00 · 0,00 | 03 M8 | zhoda |
| 1 000 | 4 | 30 | 4,77 · 1 718,70 · 718,70 | 03 e2e | zhoda |
| 100 000 | 4 | 25 | 527,84 | 03 e2e (NFR-01) | zhoda |

Ďalšie overené tvrdenia:
- 477,42 × 360 = 171 871,20.
- Mesačná splátka pre 100 000 / 4 / 30 v type `number` je presne `477.4152954654538`.
- Úrok pre 1 000 / 0 / 29 v type `number` je presne `-1.1368683772161603e-13`.
- Zaokrúhlenie podľa M5: 0,005 → 0,01; 0,004999 → 0; 1,005 → 1,01; 2,675 → 2,68; 2,5 → 3 (0 desatinných miest); 999,995 → 1 000.
- `Number("1.8e-12e2")` je `NaN`, takže pravidlo pre |hodnota| < 1e-6 v M5 je potrebné.
- Pri sadzbe 0 % má 1 856 z 30 000 kombinácií (P = 1 000 až 1 000 000 po 1 000, doba 1 až 30 rokov) nenulový zvyšok. Najväčší je 1,16e-10, teda pod hranicou 1e-6.
- Pri 200 000 náhodných platných vstupoch dal výpočet podľa 02 po zaokrúhlení vždy rovnaký výsledok ako presný výpočet. Zobrazená celková suma mínus výška úveru sa vždy rovnala zobrazenému úroku.

Hodnoty označené v `03-test-scenarios.md` ako NEOVERENÉ sú týmto overené.

## Nálezy

| # | Závažnosť | Týka sa | Nález | Rozhodnutie autora | Dôvod |
|---|-----------|---------|-------|--------------------|-------|
| 1 | major | IN-01 až IN-03, M1, M3, testy M3 | Pravidlo „viac desatinných miest, než povoľuje Krok“ má dva výklady: počet zapísaných číslic alebo násobok kroku. M1 počíta číslice, takže `4,250` (sadzba), `30,0` (doba) a `1000,000` (úver) sú neplatné. Pri kontrole hodnoty by boli platné. Koncové nuly nemajú test. | prijaté | Do časti 3 v 01 sa doplní, že rozhoduje počet zapísaných desatinných miest vrátane koncových núl, čo zodpovedá M1 aj AD-02. Do 03 sa doplnia testy `4,250` a `30,0` (`step`). |
| 2 | major | FR-02, DR-03, M4 | FR-02 hovorí „súčet všetkých mesačných splátok“, čo sa dá čítať ako 477,42 × 360 = 171 871,20. DR-03 a príklady používajú nezaokrúhlenú splátku × n = 171 869,51. Zobrazená splátka × n sa líši od zobrazenej celkovej sumy v 9 890 z 10 000 náhodných vstupov. | prijaté | Výstup FR-02 sa preformuluje na „M × n s nezaokrúhleným M podľa DR-03“. Príklady a test `test_splatka_bez_zaokruhlenia_medzivysledkov` už správanie určujú. Vysvetľujúca poznámka v UI sa presúva do V2. |
| 3 | major | 01 časť 3, AD-08, M11, testy e2e | 01 neurčuje stav formulára po načítaní. AD-08 (predvyplnené 100 000 / 4 / 30) nie je potvrdené. Bez neho by prázdna stránka pri AD-01 hneď zobrazila tri chyby. Štyri e2e testy predvyplnenie predpokladajú. | prijaté | AD-08 sa potvrdzuje. Do 01 sa doplní, že po načítaní sú polia predvyplnené referenčným príkladom DR-04 r. 1 a zobrazí sa jeho výsledok. |
| 4 | major | EP-01, M4, M5, DR-03, K-04 | EP-01 (splátkový kalendár) tvrdí, že M1 až M5 sa nemenia. Kalendár so zaokrúhlenou splátkou a dorovnaním poslednej splátky sa v ~99 % vstupov nesčíta na celkovú sumu z M4 (pozri nález 2). Zmení sa buď definícia celkovej sumy v M4 a DR-03, alebo kalendár bude v rozpore so zobrazenou sumou. | prijaté | Riadok EP-01 v 02 sa upraví: nemenia sa iba M1 až M3. Pravidlo poslednej splátky a dopad na M4, M5 a DR-03 sa rozhodne pri návrhu V2. |
| 5 | major | EP-05, M4, dátový model | EP-05 (fixácie) tvrdí, že M4 sa nemení, ale nahrádza `LoanParams.annualRatePct`, ktoré M4 číta. Prepočet po každom období potrebuje aj zostatok istiny, ktorý M4 neposkytuje. | prijaté | Riadok EP-05 v 02 sa opraví: M4 sa mení (signatúra) a EP-05 závisí od EP-01 (zostatok istiny). |
| 6 | minor | EP-08, M9 | EP-08 (ukladanie a zdieľanie) tvrdí, že M1 až M9 sa nemenia. Načítanie hodnôt z URL ich musí zapísať do formulára, ale M9 má iba `readForm`, `render` a `bind`. | prijaté | Do EP-08 sa doplní nová funkcia M9 na zápis hodnôt do formulára. |
| 7 | minor | IN-01 až IN-03, M1 | „Medzery medzi číslicami“ nie sú definované: iba U+0020, alebo aj nezalomiteľná medzera a tabulátor (bežné pri kopírovaní z webov bánk)? Neurčené sú aj medzery pri oddeľovači (`3 ,5`), jednotky (`150 000 €`, `3,5 %`) a typografické mínus `−`. | zamietnuté | Vo V1 je to ošetrené implicitne. M1 prijme iba U+0020 medzi číslicami a všetko ostatné vráti ako `'nan'`. Používateľ dostane správu s povoleným rozsahom a nikdy nesprávny výsledok. Rozšírenie o ďalšie znaky je kandidát do V2. |
| 8 | minor | IN-02, M1, M3 | Znamienka nie sú definované. Vzor M1 `-?…` robí `-0` a `-0,00` platnou sadzbou, kým `+5` je „nie je číslo“. | zamietnuté | `-0` sa matematicky rovná 0, je v rozsahu a dá správny výsledok pre 0 %. `+5` sa odmietne so správou o rozsahu. Ani jeden prípad nevedie k nesprávnemu výsledku, preto to vo V1 nie je kritické. |
| 9 | minor | IN-01, M1, M7 | Bodka ako oddeľovač tisícov sa číta zle: `100.000` je 100 s 3 desatinnými miestami (chyba), `1.000.000` je „nie je číslo“. Správanie je definované, ale pre slovenského používateľa môže byť správa mätúca. | zamietnuté | 01 jednoznačne určuje bodku ako desatinný oddeľovač. Vstup sa odmietne a správa uvádza povolený rozsah, takže nevznikne nesprávny výsledok. Nápoveda k formátu je kandidát do V2. |
| 10 | minor | testy M5 a M6 | Testy s hodnotami 2,675 a 999,995 neodhalia naivné zaokrúhlenie `Math.round(v*100)/100`, ktoré dá tiež 2,68 a 1000. Chybu zachytí iba test s 1,005. | prijaté | Testy sa doplnia o hodnoty, pri ktorých naivné zaokrúhlenie zlyhá (overené: 0,145 → 0,15, naivne 0,14; 1,015 → 1,02, naivne 1,01). Test s 1,005 ostáva. |
| 11 | minor | 03, FR-04, TQ-01, TQ-04 | Niektoré testy neoverujú požiadavku z 01. E2E test nezalomenia súm overuje pravidlo z 02, nie FR-04. Tri testy `RangeError` pre M4 až M6 overujú nepotvrdený návrh TQ-01. Test zvyšku pri 0 % porovnáva presné bity typu `number`. | prijaté | Test nezalomenia sa naviaže na M12 a 02, nie na FR-04. Návrh TQ-01 sa potvrdzuje, takže testy `RangeError` overujú rozhodnutie z review. Test zvyšku sa zmení na podmienku \|úrok\| < 1e-6 namiesto presnej hodnoty. |
| 12 | minor | testy M1, M3, M8 | Chýbajú testy: „nie je číslo“ pre `rate` a `years`; iba medzery v jednotlivých poliach v M3; `,5` a `5.`; úvodné nuly (`030`); hodnoty tesne vo vnútri rozsahu (`999999,99`, `0,01`, `19,99`). Žiadny test neoveruje, že výsledok `ok` nemá kľúč `errors`. | prijaté | Testy sa doplnia do 03. Sú lacné a pokrývajú vstupy, ktoré používateľ reálne zadá. |
| 13 | minor | matica sledovateľnosti v 02 | FR-01 a FR-02 neuvádzajú M5 a M6, hoci obe vyžadujú zaokrúhlenie. FR-05 neuvádza M2, hoci rozsahy v chybových správach pochádzajú z neho. | prijaté | Matica v 02 sa doplní. |
| 14 | minor | 02 M6 | Preklep v príklade rozhrania M6: `formatNumber(1000000, 0) → "1 000"` má byť `"1 000 000"` (potvrdzuje TQ-05). | prijaté | Príklad v 02 sa opraví. |
| 15 | minor | FR-04, FR-05, M7 | Formát percent a rokov v chybových správach nie je definovaný. 01 definuje iba formát peňažných súm. „od 0 do 20 %“ funguje iba preto, že hranice sú celé čísla. | zamietnuté | Všetky hranice vo V1 sú celé čísla a M7 ich formátuje cez `formatNumber(…, 0)`. Pri zmene hraníc sa podľa AD-05 mení iba M2 a M7. Vo V1 to nie je kritické. |
| 16 | minor | 02 M5 | Tvrdenie „Overené: pri 961 kombináciách“ sa z dokumentov nedá zopakovať. Kontrola na 30 000 kombináciách záver potvrdila. | prijaté | Text v M5 sa nahradí opakovateľným opisom: P = 1 000 až 1 000 000 po 1 000, doba 1 až 30 rokov, najväčší zvyšok 1,16e-10. |

## Funkcie mimo rozsahu – moduly, ktoré sa musia zmeniť

Pre 3 funkcie mimo rozsahu V1 kontrolór určil moduly, ktoré by sa museli zmeniť. Výsledok sa líši od stĺpca „Čo sa nemení“ v 02 (pozri nálezy 4 a 5).

| Funkcia | Musí sa zmeniť | Nemení sa | Rozdiel oproti 02 |
|---------|----------------|-----------|-------------------|
| EP-01 Splátkový kalendár | nový `domain/schedule.js`; **M4** (definícia celkovej sumy a úroku, nález 4); použitie **M5** a DR-03 (zaokrúhlenie každého riadku je zaokrúhlenie medzivýsledku, ktoré DR-03 zakazuje); M8 (`results`); M9 (vykreslenie tabuľky); M11 (markup tabuľky); M12 (360 riadkov na mobile); typy `LoanResult` a `CalculationResult` | M1, M2, M3, M7 | 02 uvádza, že sa nemenia M1 až M5 |
| EP-05 Fixácie a zmeny sadzby | `RawInput` (zoznam období a sadzieb); M2 (hranice období); **M3** (validácia zoznamu a pravidlo medzi poľami: súčet období = doba splácania); **M7** (správa pre pravidlo medzi poľami porušuje pravidlo „jedna správa s rozsahom na pole“); **M4** (signatúra `LoanParams`, potrebuje zostatok istiny, teda závisí od EP-01); M8; M9 (dynamické riadky); M11; M12; `CalculationResult` (viac mesačných splátok, takže sa mení jediný výstup FR-01) | M1, M5, M6 | 02 uvádza, že sa nemení M4 |
| EP-09 Viac mien | `RawInput` (+ mena); M9 a M11 (výber meny); M2 (hranice pre každú menu); **M3** (`validateInputs` musí dostať menu, aby vybral hranice); **M7** (`€` v správach); **M6** (poloha symbolu a počet desatinných miest pre každú menu, viac než jeden parameter); M8 (odovzdá menu) | M1, M4, M5 | 02 uvádza iba zmenu M6 a M2 |

## Výsledok

| Závažnosť | Počet | Prijaté | Zamietnuté |
|-----------|------:|--------:|-----------:|
| blocker | 0 | – | – |
| major | 5 | 5 | 0 |
| minor | 11 | 7 | 4 |
| **spolu** | **16** | **12** | **4** |

Prebehlo 1. kolo kontroly. Výsledok je **0 blockerov**, preto je plán **schválený na realizáciu**.
Prijaté nálezy sa zapracujú do `01-functional.md`, `02-architecture.md` a `03-test-scenarios.md` v rámci implementačného plánu (`05-plan.md`).
