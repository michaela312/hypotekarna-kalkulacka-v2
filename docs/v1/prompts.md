# Prompty

## 01 – Funkčné požiadavky

> Interview me about the functional scope of V1 for my calculator app. Ask one question at a time. Push back when I add features that don't belong in V1. Make sure we cover: Purpose, Functional requirements, Inputs and boundaries, Domain rules, Out of scope for V1, and Open questions. Start with the first question.

> Skontroluj teraz práve vytvorený súbor `docs/v1/01-functional.md` oproti tomuto kontrolnému zoznamu a ak niečo nesedí, uprav to:
> - Každá požiadavka má vstup, výstup a aspoň jeden príklad s konkrétnymi hodnotami.
> - Sekcia „Mimo rozsahu V1“ nie je prázdna.
> - Žiadna veta neobsahuje technológiu (framework, databáza, atď.).
> - Opisuje to, čo používateľ dostane, nie ako to postavíme (žiadne zoznamy obrazoviek).

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
