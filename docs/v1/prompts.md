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
