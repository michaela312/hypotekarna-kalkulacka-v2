# API kontrakt V2

Toto je dohoda medzi frontendom a backendom: aký vstup endpoint prijme a aký výstup vráti.
V kóde mu zodpovedá modul B10 `backend/app/api/schemas.py` (Pydantic modely). Ak sa tento dokument a B10 nezhodujú, je to chyba.
FastAPI z B10 automaticky generuje OpenAPI na `GET /openapi.json` a dokumentáciu na `GET /docs`.

## Spoločné pravidlá

| # | Pravidlo |
|---|----------|
| API-R1 | Všetky endpointy sú pod `/api`. Telo požiadavky aj odpovede je JSON v UTF-8. |
| API-R2 | Kľúče JSON sú v tvare `camelCase` (napr. `extraMonth`). |
| API-R3 | Frontend posiela **surové texty z formulára**, presne tak, ako ich zadal používateľ (`"150 000"`, `"3,5"`). Parsovanie a validácia sú iba v backende (AD-V2-01). |
| API-R4 | Backend vracia **hotové texty na zobrazenie** (`"477,42 €"`). Frontend s nimi nič nepočíta a neformátuje. |
| API-R5 | Neplatný vstup používateľa nie je chyba API. `POST /api/calculate` vtedy vráti HTTP 200 a `"status": "invalid"` (AD-V2-03). |
| API-R6 | HTTP 422 znamená porušenie kontraktu: chýba kľúč, zlý typ alebo neznámy `mode`. Je to chyba vo frontende, používateľ ju nemá ako vyvolať. |
| API-R7 | Frontend čaká na odpoveď najviac 5 s. Potom požiadavku zruší a postupuje ako pri chybe siete (FR-10, FR-11). |

## Typy

```ts
type Mode = 'shorter_term' | 'lower_payment';            // IN-06

// Vstup – vždy všetky kľúče, aj keď je pole prázdne ("")
type CalculationRequest = {
  amount: string;                                        // IN-01
  rate: string;                                          // IN-02
  years: string;                                         // IN-03
  extra: { month: string; amount: string; mode: Mode };  // IN-04, IN-05, IN-06
};

type FieldKey = 'amount' | 'rate' | 'years' | 'extraMonth' | 'extraAmount';

type ExtraResult =
  | { mode: 'shorter_term';                              // FR-06
      payments: string;        // "300 mesiacov (o 60 mesiacov menej)"
      lastPayment: string;     // "325,32 €"
      total: string; interest: string; interestSaved: string }
  | { mode: 'lower_payment';                             // FR-07
      newMonthly: string;      // "428,82 €"
      total: string; interest: string; interestSaved: string };

type CalculationResponse =
  | { status: 'ok';
      results: { monthly: string; total: string; interest: string;   // FR-01 až FR-03
                 extra: ExtraResult | null } }                       // null = IN-04 aj IN-05 prázdne
  | { status: 'invalid';
      errors: Partial<Record<FieldKey, string>> };                   // FR-05, FR-09

type SavedCalculation = {                                            // FR-11
  id: string;           // UUID
  createdAt: string;    // "15. 10. 2026 14:05"
  amount: string;       // "100 000,00 €"
  rate: string;         // "4,00 %"
  years: string;        // "30 rokov"
  monthly: string;      // "477,42 €"
  extra: string | null; // "10 000,00 € v 12. mesiaci, kratšia doba"
};
```

Invarianty: `status: 'ok'` nikdy neobsahuje `errors` a `status: 'invalid'` nikdy neobsahuje `results`. Platí to rovnako ako v V1.

## Endpointy

### `POST /api/calculate` – výpočet (FR-01 až FR-09)

Volá sa 300 ms po poslednej zmene ľubovoľného poľa (AD-V2-02). Pri platnom vstupe uloží výpočet do tabuľky `calculations` po odoslaní odpovede (AD-V2-14). Odpoveď je rovnaká, či sa uloženie podarí alebo nie.

Požiadavka:
```json
{ "amount": "100 000", "rate": "4", "years": "30",
  "extra": { "month": "12", "amount": "10 000", "mode": "shorter_term" } }
```

Odpoveď `200`, platný vstup:
```json
{ "status": "ok",
  "results": {
    "monthly": "477,42 €", "total": "171 869,51 €", "interest": "71 869,51 €",
    "extra": { "mode": "shorter_term",
               "payments": "300 mesiacov (o 60 mesiacov menej)", "lastPayment": "325,32 €",
               "total": "153 072,49 €", "interest": "53 072,49 €", "interestSaved": "18 797,02 €" } } }
```

Odpoveď `200`, neplatný vstup:
```json
{ "status": "invalid",
  "errors": { "amount": "Výška úveru musí byť od 1 000 do 1 000 000 €.",
              "extraAmount": "Mimoriadna splátka musí byť od 100 do 1 000 000 €." } }
```

| Kód | Kedy |
|-----|------|
| 200 | Vždy pri správnej štruktúre JSON, aj pri neplatnom vstupe (API-R5). |
| 422 | Porušenie kontraktu (API-R6). |

### `POST /api/calculations` – uloženie výpočtu (FR-10)

Telo požiadavky je rovnaké ako pri `POST /api/calculate`. Backend výpočet urobí znova a uloží vlastný výsledok. Výsledkom z frontendu neverí.

| Kód | Telo | Kedy |
|-----|------|------|
| 201 | `{ "id": "3f1c…", "createdAt": "15. 10. 2026 14:05" }` | Uložené. |
| 422 | `{ "status": "invalid", "errors": { … } }` | Neplatný vstup. Pri správnom frontende nenastane, lebo tlačidlo je vtedy neaktívne. |
| 503 | `{ "error": "storage_unavailable" }` | Supabase neodpovedá alebo vrátila chybu. |

### `GET /api/calculations` – zoznam uložených výpočtov (FR-11)

Bez parametrov. Vráti najviac 20 záznamov, od najnovšieho.

| Kód | Telo | Kedy |
|-----|------|------|
| 200 | `{ "items": [SavedCalculation, …] }` (0 až 20 položiek) | Vždy, keď je databáza dostupná. |
| 503 | `{ "error": "storage_unavailable" }` | Supabase neodpovedá alebo vrátila chybu. |

### `GET /api/health` – kontrola behu

| Kód | Telo |
|-----|------|
| 200 | `{ "status": "ok" }` |

Nekontroluje Supabase, iba to, že backend beží.
