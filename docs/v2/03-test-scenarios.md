# 03 – Testovacie scenáre V2

Tento dokument vznikol v kroku 13 `05-plan.md` **z testov, ktoré existujú v kóde** (nie naopak, pozri „Vzťah k 03 a 04“ v `05-plan.md`).
Tabuľky sú vygenerované z `backend/tests/` (názov funkcie, docstring, ID požiadaviek v docstringu, názve alebo `pytest.param`) a z `e2e/calculator.spec.js`.
Ak sa test zmení, tabuľka sa vygeneruje znova; ručne sa neupravuje.

## Súhrn (2026-10-22)

| Sada | Príkaz | Počet | Výsledok |
|------|--------|------:|----------|
| Backend (`pytest`) | z `backend/`: `.venv/Scripts/python.exe -m pytest` | 401 prípadov v 184 testovacích funkciách | 401 prešlo |
| E2E (Playwright, Chromium) | z koreňa: `npm run test:e2e` | 18 | 18 prešlo, 4 behy za sebou (R-05 V1, 0 % flaky) |
| Supabase naživo (krok 12) | ručne podľa `02a-tiers.md` 4.4 | – | **neoverené**, čaká na `backend/.env` |

Úrovne: **jednotkový** (B1–B8 bez I/O), **akceptačný** (B9 na referenčných príkladoch DR-04, DR-10 a tabuľke FR-09), **API** (`fastapi.testclient` s `InMemoryRepository`), **integračný (bez siete)** (skutočná knižnica `supabase`, HTTP simuluje `httpx.MockTransport`), **architektúra** (importy cez `ast`), **statický** (obsah `frontend/index.html`), **e2e** (prehliadač).

## Pokrytie požiadaviek

Počet testovacích funkcií (pytest) a e2e testov, ktoré požiadavku uvádzajú. Každá požiadavka z `01-functional.md` V2, API-R z `api-contract.md` a NFR-V2 z `02-architecture.md` má aspoň 1 test.

| Požiadavka | Testov |
|------------|-------:|
| FR-01 | 7 |
| FR-02 | 2 |
| FR-03 | 8 |
| FR-04 | 6 |
| FR-05 | 9 |
| FR-06 | 8 |
| FR-07 | 5 |
| FR-08 | 5 |
| FR-09 | 22 |
| FR-10 | 22 |
| FR-11 | 23 |
| IN-01 | 10 |
| IN-02 | 5 |
| IN-03 | 5 |
| IN-04 | 15 |
| IN-05 | 13 |
| IN-06 | 4 |
| DR-01 | 2 |
| DR-02 | 6 |
| DR-03 | 13 |
| DR-04 | 3 |
| DR-05 | 7 |
| DR-06 | 1 |
| DR-07 | 4 |
| DR-08 | 2 |
| DR-09 | 3 |
| DR-10 | 13 |
| API-R1 | 2 |
| API-R2 | 3 |
| API-R3 | 2 |
| API-R4 | 2 |
| API-R5 | 2 |
| API-R6 | 5 |
| API-R7 | 2 |
| NFR-V2-01 | 2 |
| NFR-V2-02 | 2 |
| NFR-V2-03 | 1 |
| NFR-V2-04 | 5 |
| NFR-V2-05 | 4 |
| NFR-V2-06 | 11 |
| NFR-V2-07 | 6 |
| NFR-V2-08 | 2 |

Ručne overené v prehliadači (kroky 9, 10): 8 riadkov DR-10, 375 px bez vodorovného posunu, svetlý aj tmavý režim. Tieto kontroly nie sú automatizované okrem riadku 1 DR-10 v e2e.

## Scenáre podľa súborov

### `backend/tests/api/test_calculations.py` – B7a, B10, B11, B14

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_b7a_leto` | API | FR-11 | UTC 12:05 v júli → 14:05 (letný čas, UTC+2). | 1 |
| `test_b7a_zima` | API | FR-11 | UTC 13:05 v januári → 14:05 (zimný čas, UTC+1). | 1 |
| `test_b7a_format_bez_nul` | API | FR-11 | deň a mesiac bez úvodnej nuly, hodina a minúta s nulou. | 1 |
| `test_b7a_priklad_fr11` | API | FR-11 | príklad 15. 10. 2026 14:05 (UTC 12:05, letný čas). | 1 |
| `test_b7a_bez_casoveho_pasma` | API | TQ-01 | naivný datetime je porušenie kontraktu. | 1 |
| `test_post_calculations_201` | API | FR-10 | api-contract.md 201: telo { id, createdAt }. | 1 |
| `test_post_calculations_ulozi_1_zaznam` | API | FR-10 | príklad 100 000 €, 4 %, 30 rokov → 1 riadok s monthly_payment = 477.42. | 1 |
| `test_post_calculations_s_extra` | API | DR-10, FR-10 | uloží sa aj mimoriadna splátka ( riadok 1) zaokrúhlená na 0,01 €. | 1 |
| `test_post_calculations_422_neplatny_vstup` | API | – | api-contract.md 422, 02a 2.3: neplatný vstup → { status: 'invalid', errors } a nič sa neuloží. | 1 |
| `test_post_calculations_422_kontrakt` | API | – | 02a 2.3: porušenie kontraktu → 422 vo formáte FastAPI { detail }. | 1 |
| `test_post_calculations_ignoruje_vysledky_klienta` | API | AD-V2-12 | výsledky z frontendu sa nedajú poslať – neznámy kľúč → 422, nič sa neuloží. | 1 |
| `test_post_calculations_503` | API | – | api-contract.md 503: Supabase neodpovedá → { error: 'storage_unavailable' }. | 1 |
| `test_calculate_neuklada` | API | AD-V2-15 | POST /api/calculate do databázy nezapisuje. | 1 |
| `test_calculate_funguje_aj_bez_databazy` | API | AD-V2-15, NFR-V2-07 | výpočet nepotrebuje úložisko, ani keď je nedostupné. | 1 |
| `test_get_calculations_prazdny` | API | FR-11 | api-contract.md 200: prázdne úložisko → { items: [] }. | 1 |
| `test_get_calculations_20_z_25` | API | FR-11 | 25 uložení → 20 najnovších, od najnovšieho. | 1 |
| `test_get_calculations_tvar_savedcalculation` | API | FR-11 | api-contract.md SavedCalculation: hotové texty, camelCase, extra ako text alebo null. | 1 |
| `test_get_calculations_po_ulozeni_prvy` | API | FR-10 | nový záznam je v zozname ako prvý. | 1 |
| `test_get_calculations_503` | API | – | api-contract.md 503. | 1 |
| `test_openapi_4_endpointy` | API | – | Krok 8, Hotové keď: GET /docs (OpenAPI) ukazuje 4 endpointy. | 1 |

### `backend/tests/api/test_extra.py` – B10, B11

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_api_extra_null_ked_prazdne` | API | FR-09, IN-04, IN-05 | 02a 2.2 A, :  aj  prázdne → extra: null. | 1 |
| `test_api_priklad_ok_kratsia_doba` | API | API-R2, FR-06 | api-contract.md, POST /api/calculate (= 02a 2.2 B), , : presný JSON. | 1 |
| `test_api_priklad_ok_nizsia_splatka` | API | FR-07 | 02a 2.2 C, : presný JSON. | 1 |
| `test_api_priklad_invalid_kontrakt` | API | API-R2, API-R5 | api-contract.md, odpoveď 200 pri neplatnom vstupe: amount aj extraAmount (camelCase, , ). | 1 |
| `test_api_invalid_extra_amount` | API | FR-09 | 02a 2.2 D, : E = zostatok → správa so zostatkom. | 1 |
| `test_api_invalid_iba_jedno_pole` | API | FR-09 | 02a 2.2 E, : vyplnený iba mesiac → chyba iba pri extraAmount. | 1 |
| `test_api_invalid_extra_month_camel_case` | API | API-R2, IN-04 | kľúč chyby  je extraMonth. | 1 |
| `test_api_422_bez_extra` | API | API-R6 | 02a 2.2 F, : chýbajúci kľúč extra je porušenie kontraktu. | 1 |
| `test_api_422_neznamy_mode` | API | API-R6 | 02a 2.2 F, : mode musí byť shorter_term alebo lower_payment. | 4 |
| `test_api_422_extra_navyse_kluc` | API | API-R6 | neznámy kľúč v extra → 422 (extra='forbid'). | 1 |
| `test_api_422_extra_cislo_namiesto_textu` | API | API-R3 | mesiac a suma sú surové texty, nie čísla. | 1 |
| `test_api_ok_nema_errors` | API | – | Invariant api-contract.md: status 'ok' nikdy neobsahuje errors. | 3 |
| `test_api_invalid_nema_results` | API | – | Invariant api-contract.md: status 'invalid' nikdy neobsahuje results. | 3 |

### `backend/tests/api/test_routes.py` – B10, B11

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_api_vypocet_referencny_priklad` | API | API-R4, FR-01, FR-04 | až , : hotové texty, extra = null. | 1 |
| `test_api_neplatny_vstup_je_200` | API | API-R5, FR-05 | neplatný vstup je HTTP 200 so status 'invalid' a bez results. | 1 |
| `test_api_porusenie_kontraktu_je_422` | API | API-R3, API-R6 | – | 3 |
| `test_api_health` | API | NFR-V2-08 | – | 1 |
| `test_api_cas_odpovede` | API | NFR-V2-02 | medián zo 100 volaní ≤ 50 ms, s mimoriadnou splátkou v mesiaci 1 pri 30 rokoch. | 1 |

### `backend/tests/db/test_list_latest.py` – B12, B13

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_inmemory_list_latest_20_z_25` | integračný (bez siete) | FR-11 | 25 uložených → 20 najnovších, 5 najstarších chýba. | 1 |
| `test_inmemory_list_poradie` | integračný (bez siete) | FR-11 | od najnovšieho; prázdne úložisko vráti []. | 1 |
| `test_inmemory_fail` | integračný (bez siete) | AD-V2-09 | InMemoryRepository(fail=True) vyhodí StorageError aj pri čítaní. | 1 |
| `test_to_row_17_stlpcov_bez_id_a_created_at` | integračný (bez siete) | – | S1: riadok má 15 stĺpcov = 17 stĺpcov tabuľky bez id a created_at (tie vytvorí databáza). | 1 |
| `test_to_row_extra_null_vsetky_extra_none` | integračný (bez siete) | – | S1 constraint extra_all_or_nothing: bez mimoriadnej splátky sú všetky extra_* None. | 1 |
| `test_to_row_sumy_ako_text` | integračný (bez siete) | DR-10, FR-06, FR-07, FR-10 | 9 stĺpcov extra_* podľa  riadku 1; sumy ako text s 2 desatinnými miestami. | 2 |
| `test_from_row_round_trip` | integračný (bez siete) | FR-11 | riadok z databázy (numeric ako číslo JSON) → SavedRecord s rovnakými hodnotami. | 3 |
| `test_from_row_cele_cislo_ma_2_desatinne` | integračný (bez siete) | FR-11 | PostgREST vráti 100000 namiesto 100000.00 → Decimal('100000.00'). | 1 |
| `test_list_latest_url_a_parametre` | integračný (bez siete) | FR-11, NFR-V2-06 | GET /rest/v1/calculations?select=*&order=created_at.desc&limit=20 s kľúčom service_role. | 1 |
| `test_list_latest_prazdna_tabulka` | integračný (bez siete) | FR-11 | prázdna tabuľka → []. | 1 |
| `test_list_latest_chyby` | integračný (bez siete) | NFR-V2-07, R-V2-03 | každá chyba pri čítaní je StorageError a neprezradí kľúč. | 7 |
| `test_save_s_extra_posle_vsetky_stlpce` | integračný (bez siete) | FR-10 | insert s mimoriadnou splátkou pošle 15 stĺpcov vrátane 9 extra_*. | 1 |
| `test_list_latest_503_bez_opakovania` | integračný (bez siete) | NFR-V2-07 | pri 503 sa GET neopakuje (postgrest by čakal ~7 s) – 1 požiadavka, odpoveď do 1 s. | 1 |

### `backend/tests/db/test_repository.py` – B12

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_pamat_ulozi_zaznam` | integračný (bez siete) | FR-10 | 1 uloženie = 1 záznam s id a časom v UTC. | 1 |
| `test_pamat_rozne_id` | integračný (bez siete) | – | – | 1 |
| `test_pamat_simulovana_chyba` | integračný (bez siete) | AD-V2-09 | testy vedia simulovať nedostupnú databázu. | 1 |

### `backend/tests/db/test_supabase_client.py` – B13

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_klient_dostane_url_kluc_a_timeout` | integračný (bez siete) | NFR-V2-06, NFR-V2-07 | kľúč service_role a čakanie najviac 4 s. | 1 |
| `test_klient_sa_da_vytvorit` | integračný (bez siete) | NFR-V2-07 | skutočná knižnica supabase prijme nastavenia (bez sieťového volania). | 1 |
| `test_klient_pri_pamatovom_ulozisku` | integračný (bez siete) | AD-V2-09 | pri STORAGE=memory sa klient Supabase nevytvára. | 1 |

### `backend/tests/db/test_supabase_repository.py` – B13

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_to_row_sumy_ako_text` | integračný (bez siete) | FR-10 | sumy sa posielajú ako text s 2 desatinnými miestami, nie float (žiadna strata centov). | 1 |
| `test_supabase_poziadavka_na_insert` | integračný (bez siete) | FR-10, NFR-V2-06 | POST na /rest/v1/calculations s kľúčom service_role a riadkom podľa S1. | 1 |
| `test_supabase_odpoved_na_zaznam` | integračný (bez siete) | FR-10 | id a created_at z odpovede Supabase sa prevedú na SavedRecord. | 1 |
| `test_supabase_chyby_su_storage_error` | integračný (bez siete) | NFR-V2-07, R-V2-03 | každá chyba Supabase alebo siete je StorageError. | 7 |
| `test_supabase_chyba_neprezradi_kluc` | integračný (bez siete) | NFR-V2-06 | text chyby neobsahuje kľúč service_role. | 1 |

### `backend/tests/domain/test_balance.py` – B4, B5

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_dr05_b12` | jednotkový | DR-05 | 100 000 €, 4 %, 30 rokov → B_12 = 98 238,9636… | 1 |
| `test_dr05_b60` | jednotkový | DR-05, DR-10 | riadok 2: B_60 = 90 447,51 €. | 1 |
| `test_dr05_b6_nulova_sadzba` | jednotkový | DR-02, DR-05, DR-10 | riadok 3: 12 000 €, 0 %, 1 rok → B_6 = 6 000,00 €. | 1 |
| `test_dr05_b1_20_percent` | jednotkový | DR-05, DR-10 | riadok 4: 1 000 000 €, 20 %, 30 rokov → B_1 = 999 956,48 €. | 1 |
| `test_dr05_b0_je_istina` | jednotkový | DR-05 | B_0 = P. | 1 |
| `test_dr05_b_n_je_nula` | jednotkový | DR-05 | po poslednej splátke je zostatok 0 (\|B_n\| < 1e-6). | 2 |
| `test_dr05_b_n_velky_uver` | jednotkový | DR-05, R-P-02 | pri 1 000 000 €, 20 % zostane po 360 splátkach chyba floatu ~1,4e-6 € (nad prahom 1e-6) | 1 |
| `test_dr05_nezaokruhluje` | jednotkový | DR-03 | zostatok sa nezaokrúhľuje. | 1 |
| `test_dr05_neplatne_parametre` | jednotkový | TQ-01 | porušenie kontraktu je ValueError. | 2 |
| `test_round_down` | jednotkový | IN-05 | horná hranica mimoriadnej splátky je zostatok zaokrúhlený nadol. | 5 |
| `test_round_down_nikdy_minus_nula` | jednotkový | DR-03 | zvyšok binárnej aritmetiky okolo 0 dá 0,00, nikdy nie -0,00. | 3 |
| `test_round_down_vs_half_up` | jednotkový | DR-03, IN-05 | vs. : 1,005 → nadol 1,00, polovica nahor 1,01. | 1 |

### `backend/tests/domain/test_extra_payment.py` – B6

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_dr10_kratsia_doba` | jednotkový | DR-07, DR-09, DR-10, FR-06, FR-08 | každý riadok  presne na 0,01 €. | 4 |
| `test_dr10_nizsia_splatka` | jednotkový | DR-08, DR-09, DR-10, FR-07, FR-08 | každý riadok  presne na 0,01 €. | 4 |
| `test_dr06_dr07_priklad_fr06_nezaokruhleny` | jednotkový | DR-06, DR-07 | B'_12 = B_12 − E; posledná splátka 325,3178… a m = 288 po mesiaci 12. | 1 |
| `test_dr08_priklad_fr07_nezaokruhleny` | jednotkový | DR-08 | M' = 428,8179… | 1 |
| `test_fr08_nulova_sadzba_usetri_0` | jednotkový | FR-08 | pri sadzbe 0 % je ušetrený úrok vždy 0,00 € (bez -0,00). | 2 |
| `test_dr07_cyklus_konci_najviac_po_n_splatkach` | jednotkový | DR-07, R-P-02 | K = 1, E = 100 pri 1 000 000 €, 20 % – počet splátok ≤ n a posledná splátka ≤ M. | 1 |
| `test_dr07_najmensia_mimoriadna_splatka_nepredlzi_uver` | jednotkový | DR-07, R-P-02 | E = 100 € nikdy nepredĺži úver nad n splátok ani nevytvorí splátku navyše (). | 3 |
| `test_dr09_celkovy_urok_je_celkom_minus_istina` | jednotkový | DR-09 | celkový úrok = celkom − P. | 2 |
| `test_b6_nezaokruhluje` | jednotkový | DR-03 | výsledok B6 sú nezaokrúhlené floaty, nie Decimal. | 1 |
| `test_b6_porusenie_kontraktu` | jednotkový | TQ-01 | K mimo 1..n−1, E ≤ 0 alebo E ≥ B_K je ValueError (B9 to nikdy neodovzdá). | 4 |

### `backend/tests/domain/test_mortgage.py` – B4

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_splatka_referencne_priklady` | jednotkový | DR-01, DR-02, DR-04, FR-01, FR-02, FR-03 | – | 5 |
| `test_splatka_nulova_sadzba` | jednotkový | DR-02 | P / n presne, bez zvyšku. | 1 |
| `test_splatka_vzorec_dr01` | jednotkový | DR-01 | M = 477,4153… pre 100 000 €, 4 %, 30 rokov. | 1 |
| `test_splatka_bez_zaokruhlenia_medzivysledkov` | jednotkový | DR-03 | celková suma = M × n s nezaokrúhleným M (171 869,51 €, nie 477,42 × 360 = 171 871,20 €). | 1 |
| `test_splatka_minimalna_kladna_sadzba_na_4_miesta` | jednotkový | DR-03 | (príklad): M = 83,3378…, úrok 0,0542… | 1 |
| `test_splatka_nulova_sadzba_zvysok_float` | jednotkový | DR-02, DR-03, TQ-04 | B4 zvyšok binárnej aritmetiky neupravuje, rieši ho až B5 (). | 1 |
| `test_splatka_neplatne_parametre` | jednotkový | DR-02, TQ-01 | (): vstup mimo kontraktu vyhodí výnimku namiesto Infinity alebo NaN. | 3 |

### `backend/tests/domain/test_rounding.py` – B5

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_zaokruhlenie` | jednotkový | AD-V2-10, DR-03, FR-03 | – | 10 |
| `test_zaokruhlenie_maly_zaporny_zvysok` | jednotkový | DR-03, FR-03 | nikdy nevráti -0. | 1 |
| `test_zaokruhlenie_zaporna_nula_po_zaokruhleni` | jednotkový | DR-03 | 0,004 sa zaokrúhli na 0,00, nie -0,00. | 1 |
| `test_zaokruhlenie_neplatny_vstup_nan` | jednotkový | DR-03, TQ-01 | () | 3 |

### `backend/tests/format/test_money.py` – B7

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_format_suma` | jednotkový | FR-03, FR-04 | – | 7 |
| `test_format_suma_obycajne_medzery` | jednotkový | AD-04, FR-04 | iba U+0020, žiadne nezalomiteľné medzery. | 1 |
| `test_format_cislo` | jednotkový | FR-04, TQ-05 | – | 3 |
| `test_format_suma_neplatny_vstup_nan` | jednotkový | FR-04, TQ-01 | () | 1 |

### `backend/tests/input/test_parse.py` – B1

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_parse_cislo` | jednotkový | IN-01, IN-02, IN-03 | – | 8 |
| `test_parse_neplatne` | jednotkový | FR-05 | – | 8 |

### `backend/tests/input/test_validate.py` – B2, B3

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_limits_podla_tabulky_vstupov` | jednotkový | IN-01, IN-05 | až  (statické hranice) | 1 |
| `test_validacia_platne` | jednotkový | IN-01 | – | 4 |
| `test_validacia_neplatne` | jednotkový | FR-05, IN-01, IN-02, IN-03 | pri chybe sa nevracajú žiadne hodnoty. | 15 |

### `backend/tests/input/test_validate_extra.py` – B2, B3

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_in04_hranice_platne` | jednotkový | IN-04 | 1 až 359 (statická hranica pri 30 rokoch). | 3 |
| `test_in04_hranice_neplatne` | jednotkový | FR-09, IN-04 | – | 4 |
| `test_in04_pri_1_roku` | jednotkový | IN-04 | pri 1 roku (n = 12) je 11 platné a 12 neplatné – hranica n − 1 závisí od úveru. | 1 |
| `test_in05_hranice_platne` | jednotkový | IN-05 | od 100 do 1 000 000 € (statická hranica). | 4 |
| `test_in05_hranice_neplatne` | jednotkový | FR-09, IN-05 | – | 4 |
| `test_in05_menej_ako_zostatok` | jednotkový | IN-05 | E musí byť menej ako zostatok B_K zaokrúhlený nadol (98 238,96 € pri K = 12). | 1 |
| `test_in05_zostatok_pod_100_nie_je_mozny` | jednotkový | FR-09 | zostatok ≤ 100 € → žiadna suma nie je platná (príklad 1 000 €, 0 %, 30 rokov, K = 359). | 1 |
| `test_in05_staticka_chyba_sa_neporovnava_so_zostatkom` | jednotkový | FR-09 | E so statickou chybou (amount=None) nemá ďalšiu chybu voči zostatku. | 1 |
| `test_in04_neplatny_mesiac_ma_prednost_pred_zostatkom` | jednotkový | FR-09 | pri K > n − 1 sa E voči zostatku neoveruje. | 1 |
| `test_fr09_obe_prazdne_nie_je_chyba` | jednotkový | FR-09, IN-04, IN-05 | aj  prázdne = bez mimoriadnej splátky, nie chyba. | 1 |
| `test_fr09_iba_jedno_vyplnene` | jednotkový | FR-09 | vyplnené iba jedno z polí → chyba pri prázdnom poli. | 2 |
| `test_fr09_poradie_kontrol` | jednotkový | FR-09 | prázdne → nie je číslo → priveľa desatinných miest → mimo rozsahu (ako M3 vo V1). | 4 |
| `test_fr09_chyby_zakladu_aj_mimoriadnej_naraz` | jednotkový | FR-05, FR-09, IN-05 | všetky chyby naraz; partial obsahuje platné polia pre správu . | 1 |
| `test_in06_predvoleny_rezim` | jednotkový | IN-06, OQ-V2-03 | predvolený režim je Kratšia doba. | 1 |

### `backend/tests/services/test_calculator.py` – B9

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_vypocet_platny` | akceptačný | DR-02, DR-03, DR-04, FR-01, FR-02, FR-03, FR-04, IN-01, IN-02, IN-03 | – | 12 |
| `test_vypocet_neplatny` | akceptačný | FR-05 | pri chybe žiadne výsledky. | 5 |
| `test_ulozenie_zaokruhlene_hodnoty` | akceptačný | AD-V2-08, DR-03, DR-04, FR-10, IN-01, IN-02 | na uloženie idú platné vstupy a výsledky zaokrúhlené na 0,01 €, rovnaké ako zobrazené. | 3 |
| `test_ulozenie_neplatny_vstup` | akceptačný | FR-05, FR-10 | pri neplatnom vstupe nie je čo uložiť. | 1 |

### `backend/tests/services/test_calculator_extra.py` – B9

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_dr10_akceptacia_kratsia_doba` | akceptačný | DR-10, FR-01, FR-03, FR-06, FR-08 | texty presne podľa tabuľky; základné výsledky  až  sa nemenia. | 4 |
| `test_dr10_akceptacia_nizsia_splatka` | akceptačný | DR-10, FR-07, FR-08 | – | 4 |
| `test_fr09_extra_null_ked_obe_prazdne` | akceptačný | FR-01, FR-03, FR-09, IN-04, IN-05 | aj  prázdne → iba  až , extra = None. | 1 |
| `test_fr09_tabulka` | akceptačný | FR-09, IN-01, IN-04, IN-05 | každý riadok tabuľky správ. | 9 |
| `test_fr09_neplatny_in03_hranica_in04_je_359` | akceptačný | FR-09, IN-03, IN-04 | pri neplatnom  je horná hranica  359. | 1 |
| `test_fr09_ziadne_vysledky_pri_chybe` | akceptačný | FR-01, FR-03, FR-09 | pri chybe mimoriadnej splátky sa nezobrazia ani výsledky  až  a nič sa neuloží. | 1 |
| `test_fr10_saved_extra_zaokruhlene` | akceptačný | AD-V2-08, DR-10, FR-10 | riadok 1 → SavedExtra zaokrúhlené na 0,01 €. | 1 |
| `test_fr10_saved_extra_nizsia_splatka` | akceptačný | FR-10 | v režime lower_payment je payments a last_payment None, new_monthly vyplnené. | 1 |
| `test_nfr_v2_02` | akceptačný | NFR-V2-02 | K = 1, 30 rokov – medián zo 100 výpočtov B9 ≤ 50 ms. | 1 |

### `backend/tests/test_architecture.py` – B1–B15 (importy)

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_jadro_bez_frameworku` | architektúra | NFR-V2-03 | B1 až B9 neimportujú fastapi, pydantic, supabase, app.api ani app.db. | 15 |
| `test_supabase_a_prostredie_iba_v_povolenych_moduloch` | architektúra | NFR-V2-06 | Pravidlo 4, : iba app/db/supabase_*.py importuje supabase, iba B15 číta prostredie. | 25 |
| `test_zakladne_moduly_bez_importov_aplikacie` | architektúra | – | Pravidlo 2: B1, B2, B4 a B5 neimportujú žiadny modul aplikácie. | 4 |
| `test_b6_importuje_iba_b4` | architektúra | – | Pravidlo 2: B6 (extra_payment.py) importuje z aplikácie iba B4 (mortgage.py). | 1 |

### `backend/tests/test_config.py` – B15

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_config_supabase` | jednotkový | NFR-V2-06 | URL a kľúč sa načítajú z prostredia. | 1 |
| `test_config_kluc_nie_je_v_repr` | jednotkový | NFR-V2-06 | kľúč sa nevypíše v logoch. | 1 |
| `test_config_pamatove_uloziste_nepotrebuje_supabase` | jednotkový | AD-V2-09 | STORAGE=memory funguje bez URL a kľúča. | 1 |
| `test_config_chybajuca_premenna` | jednotkový | – | B15: pri STORAGE=supabase (predvolené) chyba uvádza názov chýbajúcej premennej. | 3 |
| `test_config_neplatne_storage` | jednotkový | – | – | 1 |
| `test_config_url_bez_https` | jednotkový | – | – | 1 |

### `backend/tests/test_frontend.py` – F1–F5 (statický)

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_frontend_je_jeden_subor` | statický | AD-V2-13 | frontend je jeden súbor index.html. | 1 |
| `test_frontend_bez_externych_zdrojov` | statický | NFR-V2-05 | 0 načítaní z CDN alebo iných súborov (script src, link href, @import, url()). | 1 |
| `test_frontend_iba_jedno_volanie_fetch` | statický | API-R1 | Pravidlo 5, : v celom skripte je fetch() práve raz (vo funkcii request v F5). | 1 |
| `test_frontend_bez_vypoctov_a_formatovania` | statický | API-R4, NFR-V2-05 | žiadny vzorec, hranice vstupov ani formátovanie čísel. | 1 |
| `test_frontend_polia_maju_label` | statický | AD-03, NFR-V2-04 | každé textové pole má <label for> a type="text" ( V1). | 1 |
| `test_frontend_predvyplnene_hodnoty` | statický | AD-08, IN-04, IN-05 | V1: polia sú predvyplnené 100 000 / 4 / 30,  a  prázdne. | 1 |
| `test_frontend_casove_limity` | statický | API-R7, NFR-V2-01 | (debounce 300 ms),  (timeout 5 s). | 1 |
| `test_backend_servíruje_frontend` | statický | AD-V2-05, NFR-V2-08 | GET / vráti index.html z toho istého servera ako API. | 1 |
| `test_frontend_posiela_extra` | statický | API-R6 | readForm() posiela povinný kľúč extra s month, amount a mode. | 1 |
| `test_nfr_v2_04_fieldset_legend` | statický | IN-04, IN-06, NFR-V2-04 | až  sú vo <fieldset> s <legend>, prepínač  vo vlastnom <fieldset> s <legend>. | 1 |
| `test_nfr_v2_04_kazdy_vstup_ma_label` | statický | NFR-V2-04 | 5 textových polí má <label for> a 2 prepínače sú vnorené v <label> s textom. | 1 |
| `test_nfr_v2_05_ziadne_cisla_hranic` | statický | NFR-V2-05 | skript neobsahuje hranice vstupov (359, 100, 1000000, 1 000 000) ani vzorce. | 1 |
| `test_nfr_v2_05_ziadne_externe_zdroje` | statický | NFR-V2-05 | 0 importov v skripte (žiadne import/require/eval). | 1 |
| `test_frontend_data_atributy_extra` | statický | FR-06, FR-09 | 02a 1.3: atribúty data-* pre  až . | 1 |
| `test_frontend_predvoleny_rezim` | statický | IN-06, OQ-V2-03 | predvolený režim je Kratšia doba (checked). | 1 |
| `test_frontend_zmena_rezimu_spusti_vypocet` | statický | IN-06 | zmena prepínača (udalosť change) naplánuje výpočet. | 1 |
| `test_frontend_fetch_iba_v_f5` | statický | – | Pravidlo 5, 02a 1.2: fetch() iba v F5; F5 nepoužíva document; F3 nevolá fetch ani document. | 1 |
| `test_frontend_fetch_iba_3_cesty_api` | statický | API-R1 | F5 volá presne 3 endpointy z api-contract.md. | 1 |
| `test_frontend_f5_prevod_chyb` | statický | – | 02a 1.6: 503 → storage, 422 → contract + console.error, AbortError → timeout, inak network. | 1 |
| `test_nfr_v2_04_save_role_status` | statický | FR-10, NFR-V2-04 | tlačidlo Uložiť výpočet je predvolene neaktívne, správa je v role="status". | 1 |
| `test_frontend_data_atributy_zoznam` | statický | FR-11 | 02a 1.3, : telo tabuľky data-list="calculations", správa data-status="list", 6 stĺpcov. | 1 |
| `test_frontend_texty_fr10_fr11` | statický | FR-10, FR-11 | texty správ presne podľa 01-functional.md. | 1 |
| `test_frontend_zoznam_bez_innerhtml` | statický | – | Bezpečnosť: texty z API sa vkladajú iba cez textContent, nie innerHTML. | 1 |
| `test_frontend_uprava_zahodi_odpoved_na_ceste` | statický | FR-10, R-V2-04 | úprava formulára zneplatní odpoveď na ceste, aby nezapla tlačidlo pre staré hodnoty. | 1 |
| `test_frontend_sekcie_funguju_aj_s_crlf` | statický | – | Pravidlo 5: rozdelenie skriptu na F5/F4/F3 funguje aj po checkoute s CRLF (core.autocrlf=true). | 1 |

### `backend/tests/test_main.py` – B14

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_start_pamatove_uloziste` | jednotkový | AD-V2-09 | STORAGE=memory → InMemoryRepository. | 1 |
| `test_start_supabase` | jednotkový | FR-10 | STORAGE=supabase → SupabaseRepository (pri vytvorení sa nepripája). | 1 |
| `test_start_bez_premennych_zlyha` | jednotkový | NFR-V2-06 | B15, : pri chýbajúcej premennej sa aplikácia nespustí a chyba uvádza jej názov. | 1 |

### `backend/tests/test_secrets.py` – repozitár

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_env_je_ignorovany_gitom` | jednotkový | NFR-V2-06 | backend/.env je v .gitignore. | 1 |
| `test_env_nie_je_v_repozitari` | jednotkový | NFR-V2-06 | žiadny súbor .env nie je sledovaný gitom. | 1 |
| `test_env_example_bez_hodnot` | jednotkový | NFR-V2-06 | .env.example obsahuje iba názvy premenných, nie URL ani kľúč. | 1 |
| `test_migracia_calculations` | jednotkový | AD-V2-06, FR-10, FR-11 | S1, , , : 17 stĺpcov, index podľa času a zapnuté RLS bez politík. | 1 |

### `backend/tests/text/test_messages.py` – B8

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_sprava` | jednotkový | FR-05, IN-01, IN-02, IN-03 | – | 3 |
| `test_sprava_rovnaka_pre_vsetky_kody` | jednotkový | FR-05 | správa uvádza iba povolený rozsah, nezávisí od kódu chyby. | 4 |

### `backend/tests/text/test_messages_v2.py` – B7, B8

| Test | Úroveň | Požiadavky | Overuje | Prípadov |
|------|--------|------------|---------|---------:|
| `test_plural` | jednotkový | FR-06, FR-11 | 1 → mesiac/rok, 2 až 4 → mesiace/roky, 0 a 5+ → mesiacov/rokov. | 8 |
| `test_fr09_sprava_in04` | jednotkový | FR-09, IN-04 | horná hranica  je n − 1. | 2 |
| `test_fr09_sprava_in05_so_zostatkom` | jednotkový | FR-09, IN-01, IN-04 | riadok 2:  až  platné → správa so zostatkom. | 1 |
| `test_fr09_sprava_in05_bez_zostatku` | jednotkový | FR-09, IN-01, IN-04 | riadok 3: niektorý z  až  je neplatný → statický rozsah. | 4 |
| `test_fr09_sprava_zostatok_pod_100` | jednotkový | FR-09 | riadok 4: príklad 1 000 €, 0 %, 30 rokov, K = 359. | 1 |
| `test_fr06_text_splatok` | jednotkový | DR-10, FR-06 | – | 5 |
| `test_fr11_text_doby` | jednotkový | FR-11 | – | 3 |
| `test_fr11_text_extra` | jednotkový | FR-11 | oba režimy. | 2 |
| `test_fr11_format_rate` | jednotkový | FR-11 | sadzba v tvare 4,00 %. | 5 |

### `e2e/calculator.spec.js` – F1–F5 cez prehliadač (Playwright, Chromium)

| Test | Požiadavky |
|------|------------|
| FR-01: predvyplnené hodnoty → 477,42 € | FR-01 |
| FR-05: 2 chyby naraz, výsledky skryté | FR-05 |
| NFR-V2-04: aria-invalid a aria-describedby | NFR-V2-04 |
| NFR-V2-01: výsledok do 500 ms po poslednej zmene | NFR-V2-01 |
| AD-V2-02: 6 rýchlych zmien = 1 požiadavka | AD-V2-02 |
| R-V2-04: staršia odpoveď sa zahodí | R-V2-04 |
| API-R7: timeout 5 s → stav unavailable | API-R7 |
| OQ-V2-04: Skúsiť znova obnoví výpočet | OQ-V2-04 |
| FR-06: riadok 1 DR-10 (kratšia doba) | FR-06, DR-10 |
| FR-07: riadok 1 DR-10 (nižšia splátka) | FR-07, DR-10 |
| FR-09: iba IN-04 vyplnený → správa pri IN-05 | FR-09, IN-04, IN-05 |
| FR-10: 1 klik = 1 záznam (2 rýchle kliky → 1 uloženie) | FR-10 |
| FR-10: tlačidlo neaktívne pri chybe | FR-10 |
| FR-10: 503 → správa, formulár zostane | FR-10 |
| FR-10: chyba siete pri uložení → správa | FR-10 |
| FR-11: prázdny zoznam → správa | FR-11 |
| FR-11: chyba načítania → správa, kalkulačka funguje ďalej | FR-11 |
| FR-11: 25 uložení → 20 riadkov | FR-11 |
