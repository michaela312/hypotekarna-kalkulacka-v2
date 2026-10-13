# 01 – Funkčné požiadavky

## 1. Účel

Kalkulačka je určená pre dlžníka, ktorý zvažuje hypotéku. Odpovedá na otázku:
„Ak si požičiam X € s úrokom Y % ročne na Z rokov, koľko budem platiť mesačne a koľko spolu?“

Kalkulačka komunikuje v slovenčine a pracuje iba s menou EUR.

## 2. Funkčné požiadavky

### FR-01 Mesačná splátka
- **Vstup:** výška úveru (IN-01), ročná úroková sadzba (IN-02), doba splácania (IN-03), všetky platné.
- **Výstup:** mesačná splátka v € vypočítaná podľa DR-01 (sadzba > 0) alebo DR-02 (sadzba = 0), zaokrúhlená podľa DR-03.
- **Príklady:**
  - 100 000 €, 4 %, 30 rokov → **477,42 €**
  - 12 000 €, 0 %, 1 rok → **1 000,00 €**

### FR-02 Celková zaplatená suma
- **Vstup:** rovnaký ako FR-01.
- **Výstup:** súčet všetkých mesačných splátok v € podľa DR-03.
- **Príklady:**
  - 100 000 €, 4 %, 30 rokov → **171 869,51 €**
  - 12 000 €, 0 %, 1 rok → **12 000,00 €**

### FR-03 Celkový zaplatený úrok
- **Vstup:** rovnaký ako FR-01.
- **Výstup:** celková zaplatená suma mínus výška úveru, v € podľa DR-03.
- **Príklady:**
  - 100 000 €, 4 %, 30 rokov → **71 869,51 €**
  - 12 000 €, 0 %, 1 rok → **0,00 €**

### FR-04 Formát peňažných súm
- **Vstup:** ľubovoľný výsledok FR-01 až FR-03.
- **Výstup:** suma so slovenským formátom:
  - medzera ako oddeľovač tisícov;
  - desatinná čiarka;
  - presne 2 desatinné miesta;
  - symbol `€` za číslom, oddelený medzerou.
- **Príklady:**
  - 6 015 667,2705 → **6 015 667,27 €**
  - 1 000 → **1 000,00 €**
  - 0 → **0,00 €**

### FR-05 Neplatný vstup
- **Vstup:** aspoň jedna hodnota IN-01 až IN-03, ktorá je neplatná podľa časti 3.
- **Výstup:**
  - pri každej neplatnej hodnote sa zobrazí chybová správa s povoleným rozsahom;
  - nezobrazí sa žiadny z výsledkov FR-01 až FR-03.
- **Príklady:**
  - Výška úveru 999 € → „Výška úveru musí byť od 1 000 do 1 000 000 €.“ a žiadne výsledky.
  - Doba splácania 31 rokov → „Doba splácania musí byť od 1 do 30 rokov.“ a žiadne výsledky.
  - Sadzba prázdna a doba splácania 2,5 roka → dve chybové správy (pri sadzbe aj pri dobe splácania) a žiadne výsledky.

## 3. Vstupy a hranice

| ID | Vstup | Jednotka | Min | Max | Krok | Platné príklady | Neplatné príklady |
|----|-------|----------|-----|-----|------|-----------------|-------------------|
| IN-01 | Výška úveru | EUR | 1 000 | 1 000 000 | 0,01 | `1000`, `150 000`, `99999,99`, `1000000` | `999,99`, `1000000,01`, `100,005`, `abc`, prázdne |
| IN-02 | Ročná úroková sadzba | % p. a. | 0 | 20 | 0,01 | `0`, `3,5`, `4.25`, `20` | `-0,01`, `20,01`, `3,125`, prázdne |
| IN-03 | Doba splácania | roky | 1 | 30 | 1 | `1`, `25`, `30` | `0`, `31`, `2,5`, prázdne |

Hranice sú vrátane, takže hodnoty Min aj Max sú platné.

Pravidlá pre všetky vstupy:
- Ako desatinný oddeľovač sa akceptuje čiarka `,` aj bodka `.`. Príklad: `3,5` aj `3.5` znamená 3,5 %.
- Medzery medzi číslicami sa ignorujú. Príklad: `150 000` znamená 150 000 €.
- Splátky sú mesačné, počet splátok je n = IN-03 × 12. Príklad: 30 rokov znamená 360 splátok.

Vstup je neplatný, ak platí aspoň jedna z týchto podmienok:
- je prázdny;
- nie je číslo;
- je mimo rozsahu Min až Max;
- má viac desatinných miest, než povoľuje Krok (IN-03 nesmie mať žiadne).

## 4. Doménové pravidlá

Vo vzorcoch platí:
- P = výška úveru (IN-01);
- i = IN-02 / 100 / 12 (mesačná sadzba);
- n = IN-03 × 12 (počet splátok).

| ID | Pravidlo | Príklad |
|----|----------|---------|
| DR-01 | Pre sadzbu > 0 sa mesačná splátka počíta anuitným vzorcom `M = P · i / (1 − (1 + i)^−n)`. | P = 100 000, sadzba 4 % (i = 0,04/12), n = 360 → M = 477,4153… |
| DR-02 | Pre sadzbu = 0 je mesačná splátka `M = P / n`. | P = 12 000, n = 12 → M = 1 000 |
| DR-03 | Medzivýsledky sa nezaokrúhľujú. Zaokrúhľujú sa iba zobrazené výsledky, na 0,01 € matematicky (polovica nahor). Celková suma = M × n s nezaokrúhleným M. Celkový úrok = M × n − P. | P = 1 000, sadzba 0,01 %, 1 rok: M = 83,3378… → 83,34 €; M × n = 1 000,0542… → 1 000,05 €; úrok 0,0542… → 0,05 € |
| DR-04 | Referenčné príklady sú v tabuľke nižšie. | – |

| P (€) | Sadzba (%) | Roky | Mesačná splátka | Celkom zaplatené | Celkový úrok |
|------:|-----------:|-----:|----------------:|-----------------:|-------------:|
| 100 000 | 4 | 30 | 477,42 € | 171 869,51 € | 71 869,51 € |
| 12 000 | 0 | 1 | 1 000,00 € | 12 000,00 € | 0,00 € |
| 1 000 000 | 20 | 30 | 16 710,19 € | 6 015 667,27 € | 5 015 667,27 € |
| 1 000 | 0,01 | 1 | 83,34 € | 1 000,05 € | 0,05 € |

## 5. Mimo rozsahu V1

| Funkcia | Dôvod |
|---------|-------|
| Splátkový kalendár | Prehľad až 360 splátok a pravidlá pre poslednú splátku. V1 odpovedá iba na otázku o mesačnej splátke a celkovej sume. |
| Grafy | Nepridávajú nový výpočet, iba iný pohľad na tie isté čísla. |
| Mimoriadne a predčasné splátky | Menia celý priebeh splácania a predpokladajú splátkový kalendár. |
| Poplatky, poistenie, RPMN | Vyžadujú ďalšie vstupy a samostatný výpočet RPMN. |
| Fixácie a zmeny sadzby | V1 počíta s jednou sadzbou počas celej doby splácania. |
| Bonita (koľko si môžem požičať) | Je to iná otázka s inými vstupmi (príjem, výdavky) a pravidlami NBS. |
| Cena nehnuteľnosti, vlastné zdroje, LTV | Výška úveru sa zadáva priamo. LTV by pridalo ďalšie pravidlá. |
| Ukladanie a zdieľanie výpočtov | Na zodpovedanie jednej otázky nie je potrebné. |
| Viac mien | Iba EUR. |
| Prepínanie jazyka | Iba slovenčina. |

## 6. Otvorené otázky

| ID | Otázka | Kedy rozhodnúť |
|----|--------|----------------|
| OQ-01 | Majú sa výsledky aktualizovať hneď pri každej zmene vstupu, alebo až keď používateľ výpočet potvrdí? | Vo fáze architektúry (`02-architecture.md`). |
