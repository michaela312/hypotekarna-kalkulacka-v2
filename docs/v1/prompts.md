# Prompty

## 01 – Funkčné požiadavky

> Interview me about the functional scope of V1 for my calculator app. Ask one question at a time. Push back when I add features that don't belong in V1. Make sure we cover: Purpose, Functional requirements, Inputs and boundaries, Domain rules, Out of scope for V1, and Open questions. Start with the first question.

> Check the newly created `docs/v1/01-functional.md` file against this checklist and make adjustments if anything does not match:
> - Each requirement includes an input, an output, and at least one example with specific values.
> - The "Out of Scope for V1" section is not empty.
> - No sentence mentions specific technologies (frameworks, databases, etc.).
> - It describes what the user receives, not how we build it (no lists of screens).

## 02 – Architektúra

> Read hypotekarna-kalkulacka-v2/docs/v1/01-functional.md. Propose a modular architecture. For each module give responsibility, interface and which requirements it implements.

> What are two other ways to split this, and what are the trade-offs?

> Read the existing file `docs/v1/02-architecture.md`. Modify it so that its structure exactly matches these mandatory sections: Stack, Modules, Dependency Direction, Data Model, and Extension Points & Decisions (also add the two recently discussed alternatives—coarse-grained modules and a configuration table—to the Decisions section). Verify that each module adheres to the Single Responsibility Principle.

> Check before the next layer.
> - Every requirement from Layer 1 is implemented by at least one module.
> - Each module can be described in a single sentence without the word "and".
> - A computational module depends on neither the UI nor the database.
> - Every deferred function has an extension point.
>
> A common mistake: modules based on technical layers (frontend, backend) rather than responsibility. Another common mistake: an architecture for V5 instead of V1. You design for what you are building now, while leaving a clear place for what is to come.

## 05 – Implementačný plán

> Read docs/v1/01-functional.md, docs/v1/02-architecture.md, docs/v1/03-test-scenarios.md, and docs/v1/04-review.md.
>
> Write docs/v1/05-plan.md following this exact structure:
> 1. Ciele V1 (2-4 merateľné ciele, ktoré sa dajú na konci odškrtnúť áno/nie).
> 2. Rozsah (odkaz na 01, zoznam požiadaviek vo V1 a explicitne uvedené zmeny vyplynulé z kontroly v 04-review.md).
> 3. Akceptačné kritériá:
>    - Funkčné: konkrétny zoznam testov z 03-test-scenarios.md, ktoré musia prejsť. Žiadne vágnuce kritériá, iba konkrétne testy.
>    - Technické: príkaz na testy prejde bez chyby, aplikácia sa spustí jedným príkazom, README opisuje spustenie.
> 4. Poradie stavby (moduly zoradené podľa závislostí z 02-architecture.md. Pri každom kroku uveď: modul, testy, ktoré musia prejsť, a jeden commit).
> 5. Definition of Done pre každý krok (testy daného modulu zelené, staré testy ostávajú zelené, commit, handoff).
> 6. Nástroje pri stavbe (ktoré skills, hooks a subagents použijete, napr. /end-session, hook na testy, kontrola výpočtu subagentom, a prečo).
> 7. Riziká a otvorené otázky (čo môže zlyhať a čo urobíte, keď to zlyhá).
>
> Uistite sa, že text je v slovenčine (s výnimkou názvov súborov či kódov ak je to nutné) a striktne dodržiava štruktúru.

## 06 – Retrospektíva (experiment E1)

> Build a mortgage calculator.

Surový prompt pre subagenta bez podkladov z `docs/v1/`. Výsledok je v `06-retro.md`.

## 06 – Retrospektíva (experiment E2)

Spoločné zadanie kontroly pre časť A aj B:

> Skontroluj `docs/v1/05-plan.md` voči `01-functional.md`, `02-architecture.md`, `03-test-scenarios.md` a `04-review.md` (všetko v `docs/v1/`). Hľadaj: rozpory medzi dokumentmi, chýbajúce alebo nesplniteľné akceptačné kritériá, nesprávne počty testov, požiadavky bez testu alebo bez kroku, nejasné či nemerateľné formulácie (pravidlo: čísla, nie prídavné mená), chyby v poradí krokov a závislostiach, riziká bez mitigácie.
> Každý nález klasifikuj: blocker (plán sa nedá realizovať alebo vedie k zlému výsledku), major (vedie k prepracovaniu alebo nejasnosti v kroku), minor (formulácia, preklep, kozmetika). Pri každom náleze uveď presné miesto (súbor + sekcia/riadok) a dôkaz (citát alebo počet).

Časť A (tá istá session) dostala navyše úvod:

> Si autor implementačného plánu V1 … Pokračuješ v tej istej session, v ktorej si plán vytvoril. Aby si mal svoj kontext, najprv si prečítaj svoje poznámky: `docs/handoff.md` a `docs/v1/prompts.md` … V handoffe máš zaznamenané, že review (04) skončilo s 0 blockermi a plán je schválený na realizáciu.

Časť B (čistá session) dostala navyše úvod:

> Si nezávislý kontrolór. … čítaj IBA súbory `docs/v1/01-functional.md`, `02-architecture.md`, `03-test-scenarios.md`, `04-review.md` a `05-plan.md`. Nečítaj `docs/handoff.md`, `docs/v1/prompts.md`, `docs/v1/06-retro.md` ani git históriu.

Výsledok je v `06-retro.md`.
