# Candidate niches — Puerto Rico local businesses

> The agent picks one niche per run from this pool, deduplicated against the
> last 30 days of `history/campaigns.jsonl`. Add new niches as you discover
> them — never delete, only append, so the dedup window stays accurate.

## Home services

- Reparación de celulares (Caguas, Bayamón, Carolina, San Juan)
- Plomería residencial (Guaynabo, Trujillo Alto)
- Cerrajería automotriz 24/7 (San Juan metro)
- Lavado a presión de exteriores (todo PR)
- Fumigación y control de plagas (Bayamón, Guaynabo)
- Mantenimiento de piscinas (San Juan, Dorado)
- Mudanzas y junk removal (área metro)
- Limpieza de casas (Airbnb turnovers)
- Lavanderías (recogido y entrega)

## Auto / vehicular

- Rotulación de vehículos comerciales (Bayamón, Carolina)
- Talleres mecánicos (cambio de aceite, alineamiento)
- Detailing automotriz (área metro)
- Cristalerías automotrices
- Window tint (categoría premium, ya validada en demos previos)

## Health / wellness

- Clínicas dentales (citas online)
- Ópticas (examen + espejuelos)
- Gimnasios y entrenadores personales
- Escuelas de natación (clases)
- Reposterías (cotización bizcochos)
- Floristerías (eventos + WhatsApp)

## Events / hospitality

- Party rentals (eventos)
- Catering corporativo
- Wedding planners

## Construction / commercial

- Construcción y remodeling
- Pintura residencial y comercial
- Impermeabilización de techos
- Cisternas y tinacos (venta + instalación)
- Sistemas solares residenciales

## Education / professional

- Tutorías K-12
- Clases de inglés conversacional
- Coaching de negocios locales

---

## Anti-patterns (do NOT pick)

- Generic categories ("small business", "local services") — pick a concrete vertical + city.
- Niches already in the last 30 days of `history/campaigns.jsonl`.
- Niches that overlap with an active paid campaign (the loop and the paid team must not collide).
- Niches with low buyer intent ("personal branding coaches", "life coaches") — the loop is built for transactional leads.

---

## Refresh cadence

Add 3-5 fresh niches every quarter. When the pool exceeds 50, retire the bottom 10 by usage (least-picked first) so the loop keeps discovering new verticals.