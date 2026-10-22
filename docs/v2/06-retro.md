# 06 – Retrospektíva V2 (realizácia `05-plan.md`)

Realizácia krokov 1 až 13 `05-plan.md` prebehla 2026-10-22 v jednej relácii. Krok 12 (Supabase naživo) nie je hotový, čaká na používateľku.

## 1. Plán vs. skutočnosť

| Ukazovateľ | Plán (`05-plan.md`) | Skutočnosť | Rozdiel |
|------------|---------------------|------------|---------|
| Testy `pytest` | ≥ 196 + 110 = 306 (D-V2-01) | **401**, všetky prechádzajú | +95 nad minimum |
| Testy e2e | ≥ 14 (D-V2-02) | **18**, 4 behy za sebou 18/18 | +4 |
| DR-04 a DR-10 na 0,01 € (D-V2-03) | 4/4 a 8/8 | 4/4 a 8/8 v `pytest`; 8/8 aj ručne v prehliadači | – |
| Výkon (D-V2-05) | medián ≤ 50 ms; ≤ 500 ms v prehliadači | test `NFR-V2-02` (B9 aj API) a e2e `NFR-V2-01` prechádzajú | uloženie a zoznam ≤ 2 s proti Supabase neoverené (krok 12) |
| Vrstvy (D-V2-04) | 0 zakázaných importov, `fetch(` iba v F5 | `test_architecture.py`, `test_frontend_fetch_iba_v_f5` | – |
| Commity | 1 na krok | 1 na krok 1–11 + 1 za review + 1 za krok 13 | – |
| Krok 12 | Supabase naživo | **neurobený** | `backend/.env` má prázdny `SUPABASE_SERVICE_ROLE_KEY` |

Počty nových testov po krokoch (plán → skutočnosť): 1: 14 → 29, 2: 8 → 20, 3: 12 → 26, 4: 16 → 31, 5: 18 → 23, 6: 10 → 21, 7: 10 → 22, 8: 12 → 17 (+ 5 nahradených), 9: 6 → 7, 10: 4 → 7 (+ 2 v review), 11: 14 → 18.

## 2. Odchýlky a zistenia

| # | Krok | Zistenie | Riešenie |
|---|------|----------|----------|
| O-01 | 1 | Existujúci test B3 vyžaduje `values == {}` pri chybe, ale B9 potrebuje platné časti vstupu na správu IN-05 so zostatkom. | `ValidationResult.partial` (platné polia aj pri chybe); `values` zostali bez zmeny. |
| O-02 | 2 | Pri 1 000 000 €, 20 % je \|B_360\| = 1,4e-6 € – nad prahom 1e-6 z DR-07 (R-P-02 sa potvrdilo). | Test B4 s relatívnou toleranciou; cyklus DR-07 v B6 má strop n − K splátok a posledný krok zaplatí celý zostatok. |
| O-03 | 3 | 8/8 riadkov DR-10 sedelo na prvý pokus. | – |
| O-04 | 6 | Povinný kľúč `extra` rozbil 5 starých testov API (poslali požiadavku bez neho). | Telá doplnené o `extra`; frontend zmenený v tom istom commite (R-P-01). |
| O-05 | 7 | `postgrest` pri 5xx opakuje GET 3× s čakaním ~7 s. Pri pozastavenom projekte (R-V2-03) by zoznam čakal dlhšie ako timeout frontendu 5 s a NFR-V2-07 (2 s). | `.retry(False)` v `list_latest` + test „503 = 1 požiadavka, < 1 s“. |
| O-06 | 8 | Na Windows chýbali časové pásma (`ZoneInfoNotFoundError`, R-P-03 sa potvrdilo). | `tzdata==2026.5` v `requirements.txt`. |
| O-07 | 8 | AD-V2-15 v kóde: 5 testov automatického ukladania (AD-V2-14) nahradených testami `test_calculate_neuklada` a `test_calculate_funguje_aj_bez_databazy`. | README a `backend/README.md` upravené. |
| O-08 | 9 | Text „300 mesiacov (o 60 mesiacov menej)“ s `white-space: nowrap` pretekal pri šírke 264 px. | Text počtu splátok sa zalamuje, sumy nie (FR-04). |
| O-09 | 10 | Tlačidlo „Uložiť“ je neaktívne aj počas písania (od zmeny po novú odpoveď), nielen pri chybe. FR-10 hovorí „iba keď sa zobrazujú výsledky“; počas písania sú zobrazené výsledky staré. | Zámerne prísnejšie: uloží sa vždy to, čo je zobrazené. |
| O-10 | 11 | `webServer.command` s „/“ v ceste nefunguje v `cmd.exe`. | `path.join` v `playwright.config.js`. Verzia `@playwright/test` 1.64.0 (najnovšia staršia ako 2 týždne). |
| O-11 | 11 | E2E bežia na porte 8001, aby sa nebili s vývojovým serverom na 8000. | `playwright.config.js`. |
| O-12 | – | `backend/.env` existuje (handoff uvádzal opak), `STORAGE=supabase`, kľúč prázdny → backend sa s ním nespustí. | `.claude/launch.json` má konfiguráciu `backend-memory` so `STORAGE=memory`. |

## 3. Review kódu (krok 13)

`/code-review` nad `577f910..HEAD` (42 súborov, +2 434 / −195 riadkov), 6 nálezov:

| Nález | Stav |
|-------|------|
| Odpoveď na ceste po úprave formulára zapla „Uložiť“ pre staré hodnoty (FR-10) | opravené (`onEdit` zvýši `lastRequest`), statický test |
| `section()` v `test_frontend.py` zlyhá po checkoute s CRLF (`core.autocrlf=true`, bez `.gitattributes`) | opravené, test s CRLF |
| Nedosiahnuteľná vetva `raise ValueError` v B6 | opravené (`AssertionError` s vysvetlením) |
| B9 a B6 počítajú `balance_after` a `calculate_mortgage` dvakrát | ponechané: ≤ 359 krokov, NFR-V2-02 má rezervu; rozhranie B6 zostáva podľa 02 |
| Pomocné funkcie mocku Supabase skopírované v 2 testovacích súboroch | ponechané |
| Ručné mapovanie B9 → B10 v `to_api_response` | ponechané |

`/simplify` sa samostatne nespustil: review bežalo aj s uhlami reuse, simplification a efficiency a ich nálezy sú v tabuľke vyššie.

## 4. Čo zostáva

1. **Krok 12 – Supabase naživo** (používateľka): projekt v `eu-central-1`, migrácia S1 v SQL Editore, `SUPABASE_URL` a `SUPABASE_SERVICE_ROLE_KEY` v `backend/.env`. Potom overenie podľa `02a-tiers.md` 4.4 (1 uloženie → riadok s `monthly_payment = 477.42`, riadok s mimoriadnou splátkou má 9 stĺpcov `extra_*`, anon kľúč dostane `[]`, uloženie aj zoznam ≤ 2 s).
2. Voliteľne `.gitattributes` s `eol=lf` pre `*.html`, `*.py`, `*.js`, aby statické testy nezáviseli od `core.autocrlf`.
3. Review `05-plan.md` a kódu v čistej session (04 V2) – experiment E2 vo V1 ukázal, že čistý kontrolór nájde viac.
