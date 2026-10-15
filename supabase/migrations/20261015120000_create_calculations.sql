-- S1 – tabuľka uložených výpočtov (docs/v2/02-architecture.md, Data Model → V Supabase).
-- Implementuje FR-10, FR-11 a AD-V2-06.
-- Jeden riadok = jedno uloženie: vstupy IN-01 až IN-06, výsledky FR-01 až FR-08 a čas uloženia.
-- Sumy sú zaokrúhlené na 0,01 € a pri čítaní sa neprepočítavajú (AD-V2-08).

create table public.calculations (
  id                   uuid primary key default gen_random_uuid(),
  created_at           timestamptz not null default now(),
  amount               numeric(10,2) not null check (amount between 1000 and 1000000),   -- IN-01
  rate                 numeric(4,2)  not null check (rate between 0 and 20),             -- IN-02
  years                smallint      not null check (years between 1 and 30),            -- IN-03
  monthly_payment      numeric(12,2) not null,                                           -- FR-01
  total_paid           numeric(12,2) not null,                                           -- FR-02
  total_interest       numeric(12,2) not null,                                           -- FR-03
  extra_month          smallint      check (extra_month between 1 and 359),              -- IN-04
  extra_amount         numeric(10,2) check (extra_amount >= 100),                        -- IN-05
  extra_mode           text          check (extra_mode in ('shorter_term', 'lower_payment')), -- IN-06
  extra_payments       smallint,                                                         -- FR-06
  extra_last_payment   numeric(12,2),                                                    -- FR-06
  extra_new_monthly    numeric(12,2),                                                    -- FR-07
  extra_total_paid     numeric(12,2),                                                    -- FR-06, FR-07
  extra_total_interest numeric(12,2),                                                    -- FR-06, FR-07
  extra_interest_saved numeric(12,2),                                                    -- FR-08
  constraint extra_all_or_nothing check (
    (extra_month is null) = (extra_amount is null) and
    (extra_month is null) = (extra_mode is null) and
    (extra_month is null) = (extra_total_paid is null))
);

comment on table public.calculations is 'Uložené výpočty hypotekárnej kalkulačky V2 (FR-10, FR-11).';

-- FR-11: 20 najnovších záznamov.
create index calculations_created_at_idx on public.calculations (created_at desc);

-- AD-V2-06: RLS bez politík. Kľúče anon a authenticated nemajú prístup, iba backend s kľúčom service_role.
alter table public.calculations enable row level security;
