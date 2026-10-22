# 01 – Funkčné požiadavky V2

## 1. Účel

V2 prerába kalkulačku z V1 na 4 časti: frontend, API, backend (Python, FastAPI) a databázu Supabase.
Okrem otázky z V1 („koľko budem platiť mesačne a koľko spolu?“) odpovedá V2 na ďalšie dve otázky:
- „Koľko ušetrím, ak v mesiaci K zaplatím navyše E €?“
- „Ako si výpočet uložím a neskôr ho znova nájdem?“

Kalkulačka komunikuje v slovenčine a pracuje iba s menou EUR.

## 2. Prevzaté z V1 bez zmeny

Tieto požiadavky platia ďalej presne tak, ako sú v `docs/v1/01-functional.md`. Ich ID sa nemenia.

| ID | Názov | Kde je definícia |
|----|-------|------------------|
| FR-01 | Mesačná splátka | `docs/v1/01-functional.md`, časť 2 |
| FR-02 | Celková zaplatená suma | `docs/v1/01-functional.md`, časť 2 |
| FR-03 | Celkový zaplatený úrok | `docs/v1/01-functional.md`, časť 2 |
| FR-04 | Formát peňažných súm | `docs/v1/01-functional.md`, časť 2 |
| FR-05 | Neplatný vstup | `docs/v1/01-functional.md`, časť 2 |
| IN-01 až IN-03 | Výška úveru, sadzba, doba splácania | `docs/v1/01-functional.md`, časť 3 |
| DR-01 až DR-04 | Anuitný vzorec, sadzba 0 %, zaokrúhľovanie, referenčné príklady | `docs/v1/01-functional.md`, časť 4 |

**Doplnenie FR-05 vo V2 (OQ-V2-04):** ak backend neodpovie (chyba siete alebo odpoveď nepríde do 5 s), skryjú sa výsledky a zobrazí sa „Výpočet je dočasne nedostupný. Skúste to znova.“ s tlačidlom „Skúsiť znova“, ktoré výpočet zopakuje.

Zmena oproti V1 je iba v tom, **kde** sa požiadavky plnia (backend namiesto prehliadača). Táto zmena je opísaná v `02-architecture.md`.

## 3. Nové funkčné požiadavky

### FR-06 Mimoriadna splátka – kratšia doba splácania
- **Vstup:** platné IN-01 až IN-03, mesiac K (IN-04), suma E (IN-05), režim „Kratšia doba“ (IN-06).
- **Výstup** podľa DR-05 až DR-07 a DR-09, sumy podľa FR-04:
  - nový počet mesačných splátok a o koľko mesiacov je menší oproti n;
  - výška poslednej splátky;
  - celková zaplatená suma (vrátane E);
  - celkový úrok;
  - ušetrený úrok (FR-08).
- **Príklad:** 100 000 €, 4 %, 30 rokov, E = 10 000 € v mesiaci 12 → **300 mesiacov (o 60 mesiacov menej)**, posledná splátka **325,32 €**, celkom **153 072,49 €**, úrok **53 072,49 €**, ušetrené **18 797,02 €**.

### FR-07 Mimoriadna splátka – nižšia mesačná splátka
- **Vstup:** rovnaký ako FR-06, ale režim „Nižšia splátka“ (IN-06).
- **Výstup** podľa DR-05, DR-06, DR-08 a DR-09, sumy podľa FR-04:
  - nová mesačná splátka, ktorá platí od splátky K + 1 do splátky n;
  - celková zaplatená suma (vrátane E);
  - celkový úrok;
  - ušetrený úrok (FR-08).
- **Príklad:** 100 000 €, 4 %, 30 rokov, E = 10 000 € v mesiaci 12 → nová splátka **428,82 €**, celkom **164 957,63 €**, úrok **64 957,63 €**, ušetrené **6 911,88 €**.

### FR-08 Ušetrený úrok
- **Vstup:** výsledky FR-03 a FR-06 alebo FR-07 pre tie isté IN-01 až IN-03.
- **Výstup:** celkový úrok bez mimoriadnej splátky (FR-03) mínus celkový úrok s mimoriadnou splátkou. Obe hodnoty sú nezaokrúhlené, zaokrúhli sa až rozdiel (DR-03).
- **Príklady:** pozri DR-10. Pri sadzbe 0 % je ušetrený úrok vždy **0,00 €**.

### FR-09 Neplatný vstup mimoriadnej splátky
- **Vstup:** IN-04 alebo IN-05 je neplatný podľa časti 4.
- **Výstup:**
  - pri každom neplatnom poli sa zobrazí chybová správa podľa tabuľky nižšie;
  - nezobrazí sa žiadny výsledok FR-01 až FR-08. Platí rovnaké pravidlo ako vo FR-05.
- Ak sú IN-04 aj IN-05 prázdne, mimoriadna splátka sa nepočíta. Nie je to chyba: zobrazia sa iba výsledky FR-01 až FR-03.

| Situácia | Správa (príklad pre 100 000 €, 4 %, 30 rokov, K = 12) |
|----------|--------------------------------------------------------|
| IN-04 je neplatný | „Mesiac mimoriadnej splátky musí byť od 1 do 359.“ (horná hranica je n − 1) |
| IN-05 je neplatný a IN-01 až IN-04 sú platné | „Mimoriadna splátka musí byť od 100 € a menej ako zostatok úveru 98 238,96 €.“ |
| IN-05 je neplatný a niektorý z IN-01 až IN-04 je neplatný | „Mimoriadna splátka musí byť od 100 do 1 000 000 €.“ |
| Zostatok úveru v mesiaci K zaokrúhlený nadol na 0,01 € je ≤ 100 € | „V mesiaci 359 je zostatok úveru 2,77 €, mimoriadna splátka (min. 100 €) nie je možná.“ (príklad: 1 000 €, 0 %, 30 rokov, K = 359) |
| Vyplnené je iba jedno z polí IN-04 a IN-05 | Pri prázdnom poli sa zobrazí jeho správa z riadkov vyššie. |

Ak je IN-03 neplatný, horná hranica IN-04 je 359 (n − 1 pre 30 rokov).

### FR-10 Uloženie výpočtu
- **Vstup:** kliknutie na tlačidlo „Uložiť výpočet“.
- **Výstup:**
  - Tlačidlo je aktívne iba vtedy, keď sa zobrazujú výsledky (žiadna chyba podľa FR-05 ani FR-09).
  - Uložia sa platné vstupy IN-01 až IN-06 a všetky zobrazené výsledky FR-01 až FR-08, zaokrúhlené na 0,01 €.
  - Po úspechu sa zobrazí „Výpočet bol uložený.“ a nový záznam sa zobrazí v zozname FR-11 ako prvý.
  - Pri chybe databázy, chybe siete alebo odpovedi, ktorá nepríde do 5 s, sa zobrazí „Výpočet sa nepodarilo uložiť. Skúste to znova.“ Hodnoty vo formulári zostanú.
  - Počas ukladania je tlačidlo neaktívne. 1 kliknutie vytvorí najviac 1 záznam.
- **Príklad:** 100 000 €, 4 %, 30 rokov, bez mimoriadnej splátky, klik → 1 nový riadok v tabuľke `calculations` s `monthly_payment = 477.42`.

### FR-11 Zoznam uložených výpočtov
- **Vstup:** načítanie stránky alebo úspešné uloženie (FR-10).
- **Výstup:**
  - Zobrazí sa najviac 20 posledných uložených výpočtov, od najnovšieho.
  - Každý riadok obsahuje:
    - dátum a čas uloženia v tvare `15. 10. 2026 14:05` (časové pásmo Europe/Bratislava);
    - výšku úveru (FR-04);
    - sadzbu v tvare `4,00 %`;
    - dobu splácania v tvare `30 rokov`;
    - mesačnú splátku (FR-04);
    - mimoriadnu splátku v tvare `10 000,00 € v 12. mesiaci, kratšia doba`, prípadne `–`, ak ju výpočet nemal.
  - Ak nie je uložený žiadny výpočet, zobrazí sa „Zatiaľ nie sú uložené žiadne výpočty.“
  - Pri chybe databázy, chybe siete alebo odpovedi, ktorá nepríde do 5 s, sa zobrazí „Uložené výpočty sa nepodarilo načítať.“ Kalkulačka funguje ďalej.
- **Príklad:** 25 uložených výpočtov → zobrazí sa 20 najnovších, 5 najstarších sa nezobrazí.

Slovenské tvary slov podľa čísla (v FR-06 a FR-11):
- 1 → `mesiac`, `rok`;
- 2 až 4 → `mesiace`, `roky`;
- 0 a 5 a viac → `mesiacov`, `rokov`.

## 4. Nové vstupy a hranice

| ID | Vstup | Jednotka | Min | Max | Krok | Platné príklady | Neplatné príklady |
|----|-------|----------|-----|-----|------|-----------------|-------------------|
| IN-04 | Mesiac mimoriadnej splátky (K) | poradové číslo splátky | 1 | n − 1 | 1 | `1`, `12`, `359` (pri 30 rokoch), `11` (pri 1 roku) | `0`, `360` (pri 30 rokoch), `12` (pri 1 roku), `1,5`, `abc` |
| IN-05 | Mimoriadna splátka (E) | EUR | 100 | menej ako zostatok B_K zaokrúhlený nadol na 0,01 €, najviac 1 000 000 | 0,01 | `100`, `10 000`, `98238,95` (pri 100 000 €, 4 %, 30 rokov, K = 12) | `99,99`, `98238,96` (pri tom istom úvere), `100,005`, `abc` |
| IN-06 | Režim mimoriadnej splátky | – | – | – | – | `Kratšia doba` (predvolené), `Nižšia splátka` | iná hodnota (z formulára sa nedá zadať, overuje ju API) |

- Pravidlá zápisu čísla (čiarka aj bodka, medzery medzi číslicami) a podmienky neplatnosti sú rovnaké ako pri IN-01 až IN-03 v V1.
- IN-04 a IN-05 sú voliteľné ako dvojica: buď sú obe prázdne, alebo obe vyplnené (FR-09).
- Mimoriadna splátka sa zaplatí spolu s riadnou splátkou K, nie namiesto nej (DR-06).

## 5. Nové doménové pravidlá

Označenia P, i, n a M sú rovnaké ako v časti 4 `docs/v1/01-functional.md`. K = IN-04, E = IN-05.

| ID | Pravidlo | Príklad |
|----|----------|---------|
| DR-05 | Zostatok po splátke j: `B_0 = P`, `B_j = B_(j−1) · (1 + i) − M`. Nezaokrúhľuje sa (DR-03). | 100 000 €, 4 %, 30 rokov: B_12 = 98 238,9636… |
| DR-06 | Po mimoriadnej splátke v mesiaci K je zostatok `B'_K = B_K − E`. | B'_12 = 98 238,9636… − 10 000 = 88 238,9636… |
| DR-07 | **Kratšia doba:** splátka M sa nemení. Splátky pokračujú, kým zostatok neklesne na 0. Ak `B · (1 + i) ≤ M`, je to posledná splátka vo výške `B · (1 + i)`. Nový počet splátok je K + m, kde m je počet splátok po mesiaci K. | m = 288, spolu 300 splátok, posledná 325,3178… |
| DR-08 | **Nižšia splátka:** nová splátka `M' = B'_K · i / (1 − (1 + i)^−(n−K))`, pri sadzbe 0 % `M' = B'_K / (n − K)`. Platí od splátky K + 1 do n. | M' = 428,8179… |
| DR-09 | Celková zaplatená suma = `K · M + E + súčet splátok po mesiaci K`. Celkový úrok = celková suma − P. Ušetrený úrok = úrok podľa FR-03 − tento úrok. Zaokrúhľujú sa iba zobrazené výsledky (DR-03). | Pozri DR-10. |
| DR-10 | Referenčné príklady sú v tabuľke nižšie. | – |

Referenčné príklady (DR-10). Hodnoty sú vypočítané dvoma nezávislými spôsobmi: postupným prepočtom zostatku po mesiacoch a uzavretým vzorcom zostatku. Výsledky sa zhodujú na 4 desatinné miesta.

**Režim „Kratšia doba“ (FR-06):**

| P (€) | Sadzba | Roky | K | E (€) | Splátok | Kratšie o | Posledná splátka | Celkom zaplatené | Celkový úrok | Ušetrený úrok |
|------:|-------:|-----:|--:|------:|--------:|----------:|-----------------:|-----------------:|-------------:|--------------:|
| 100 000 | 4 % | 30 | 12 | 10 000 | 300 | 60 | 325,32 € | 153 072,49 € | 53 072,49 € | 18 797,02 € |
| 100 000 | 4 % | 30 | 60 | 50 000 | 160 | 200 | 344,53 € | 126 253,56 € | 26 253,56 € | 45 615,95 € |
| 12 000 | 0 % | 1 | 6 | 1 200 | 11 | 1 | 800,00 € | 12 000,00 € | 0,00 € | 0,00 € |
| 1 000 000 | 20 % | 30 | 1 | 100 | 358 | 2 | 12 774,40 € | 5 978 411,11 € | 4 978 411,11 € | 37 256,16 € |

**Režim „Nižšia splátka“ (FR-07):**

| P (€) | Sadzba | Roky | K | E (€) | Nová splátka | Celkom zaplatené | Celkový úrok | Ušetrený úrok |
|------:|-------:|-----:|--:|------:|-------------:|-----------------:|-------------:|--------------:|
| 100 000 | 4 % | 30 | 12 | 10 000 | 428,82 € | 164 957,63 € | 64 957,63 € | 6 911,88 € |
| 100 000 | 4 % | 30 | 60 | 50 000 | 213,50 € | 142 693,98 € | 42 693,98 € | 29 175,53 € |
| 12 000 | 0 % | 1 | 6 | 1 200 | 800,00 € | 12 000,00 € | 0,00 € | 0,00 € |
| 1 000 000 | 20 % | 30 | 1 | 100 | 16 708,52 € | 6 015 167,35 € | 5 015 167,35 € | 499,92 € |

Zostatky pred mimoriadnou splátkou: B_12 = 98 238,96 € (riadok 1), B_60 = 90 447,51 € (riadok 2), B_6 = 6 000,00 € (riadok 3), B_1 = 999 956,48 € (riadok 4).

Poznámka: banka zaokrúhľuje každú splátku na centy, kalkulačka nie (DR-03). Skutočné hodnoty v banke sa preto môžu líšiť o niekoľko centov.

## 6. Mimo rozsahu V2

| Funkcia | Dôvod |
|---------|-------|
| Viac mimoriadnych splátok alebo opakovaná mimoriadna splátka | V2 rieši jednu splátku v jednom mesiaci. Zoznam splátok je ďalší krok (EP-03 z V1). |
| Predčasné splatenie celého úveru (E ≥ zostatok) | Je to iný výsledok (úver končí), nie zníženie splátok. |
| Poplatok za mimoriadnu splátku | Závisí od zmluvy a dátumu fixácie. |
| Zobrazenie splátkového kalendára | Backend ho počíta interne (DR-05), ale nezobrazuje. |
| Úprava, mazanie a otvorenie uloženého výpočtu vo formulári | V2 iba ukladá a zobrazuje zoznam. |
| Prihlásenie používateľov | Zoznam je spoločný (OQ-V2-01). Rozšírenie je EP-V2-03. |
| Nasadenie na internet | V2 beží lokálne (pozri NFR-08 v `02-architecture.md`). |
| Ostatné odložené funkcie z V1 (grafy, RPMN, fixácie, bonita, LTV, viac mien, jazyky) | Bez zmeny oproti `docs/v1/01-functional.md`, časť 5. |

## 7. Otvorené otázky

| ID | Otázka | Návrh | Kedy rozhodnúť |
|----|--------|-------|----------------|
| OQ-V2-01 | Má byť zoznam uložených výpočtov spoločný pre všetkých, alebo treba prihlásenie (Supabase Auth) a každý vidí iba svoje výpočty? | **Rozhodnuté (2026-10-22, RP-02):** spoločný. Neukladajú sa žiadne osobné údaje, iba čísla. | – |
| OQ-V2-02 | Nahrádza V2 realizáciu V1 (kroky 0 až 14 v `docs/v1/05-plan.md`) úplne? | Áno. Dokumenty V1 zostanú ako história a FR, IN a DR z V1 sa prevezmú (časť 2). | Pred `05-plan.md` V2. |
| OQ-V2-03 | Je „Kratšia doba“ správny predvolený režim? | **Rozhodnuté (2026-10-22, RP-03):** áno, lebo ušetrí viac úroku (v príklade 18 797,02 € vs. 6 911,88 €). | – |
