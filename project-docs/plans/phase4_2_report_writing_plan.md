# Phase 4.2: Final Report Writing Plan

**Date:** 2026-04-21
**Target deadline:** 2026-05-08 23:59 ET (17 days remaining)
**Deliverable:** Main report (≤5 pages, excl. refs) + optional Appendix (≤10 pages, incl. figures)

---

## 1. Objectives

Produce a Nature-style research report that answers the three proposal questions:

1. To what extent do Bluebikes and MBTA arrivals deviate from Poisson?
2. When arrivals are not Poisson, how accurately do Poisson-based queueing models predict outcomes (Wq, Lq, W, blocking probability)?
3. When is Poisson a reasonable engineering approximation, and when does it break down?

**Writing principles (from project-guide.md):**
- "Conciseness, focused writing, and crisp messages."
- "A small result described and evaluated well will earn more credit than an ambitious result where no aspect was done well."
- Main report is **self-contained** — appendix optional but report must stand alone.

---

## 2. Main Report Structure (5 pages)

Target page allocation assumes 11pt body font, 1.0–1.15 line spacing, 2-column or 1-column (TBD based on template availability).

### Page 1 — Title, Abstract, Introduction
- **Title:** *Is Poisson Good Enough? Evaluating Queueing Models for Urban Mobility Systems*
- **Abstract (~150 words):** problem, approach, headline result (both systems reject Poisson in opposite directions; M/M/c error ranges from 7× underestimate to 12× overestimate; 75× Erlang B blocking gap).
- **1. Introduction:** motivation, Poisson's role in queueing theory, why Bluebikes + MBTA Red Line are informative contrast cases (user-driven vs schedule-driven), three research questions, contributions.

### Page 2 — Data and Methods
- **2. Data:** Bluebikes trip data (Sep–Dec 2025, stations M32004 and M32042), MBTA LAMP subway performance data (Red Line, Kendall/MIT, both directions). Arrival definitions. Operating-hours filter. Fullness exclusion for Bluebikes. *End the section with one sentence pointing to the GitHub repo (code/data/figures) under MIT license.*
- **3. Methods:**
  - 3.1 Arrival-process characterization: CV, skewness, index of dispersion (IoD), distribution fitting (exponential, log-normal, Weibull, gamma), KS / AD / χ² tests.
  - 3.2 Queueing models: M/M/c (infinite queue, Bluebikes 23/53 servers); M/M/c/c Erlang B for finite-capacity blocking (Bluebikes); M/M/1 for MBTA. Service-time definitions: dock occupancy (BB), dwell time (MBTA).
  - 3.3 Discrete-event simulation (SimPy): Poisson / empirical / best-fit-distribution DES, 10 replications, 2,000-arrival warmup, 20,000-arrival total.

### Page 3 — Results I: Arrival-process characterization
- **4.1 Summary statistics table** for all four systems (BB Kendall T, BB MIT Vassar, MBTA North, MBTA South): N, mean IAT, CV, skewness, IoD.
- **Figure 1:** side-by-side panel. (a) empirical CDF of IAT for one BB station and one MBTA direction overlaid with fitted exponential, Weibull, log-normal; (b) CV by hour-of-day for all four systems, showing opposite deviation direction.
- Narrative: both systems reject Poisson (p≈0 across all three tests), but in opposite directions — BB overdispersed (CV=1.75–1.90, bursty), MBTA underdispersed (CV=0.63–0.71, schedule-driven); best fit Weibull (BB) vs Log-normal (MBTA).

### Page 4 — Results II: Queueing outcomes
- **4.2 Queueing comparison table:** analytical (M/M/c or M/M/1) vs Poisson DES vs empirical DES vs best-fit DES, for Wq and blocking probability (BB only). 95% CI.
- **Figure 2:** Wq comparison bar chart across the four systems (log-scaled y-axis to show direction of error: BB underestimated, MBTA overestimated).
- **4.3 The Erlang B gap:** predicted 0.07% blocking at Kendall T vs observed 5.32% (75× gap). Discuss why: arrivals alone cannot close the gap (empirical-arrival DES still only predicts 0.60%); the residual is attributed to service-process non-stationarity.
- Narrative: Poisson M/M/c underestimates Wq by ~7× at Kendall T; Poisson M/M/1 overestimates MBTA Wq by 5–12×. Directions and magnitudes diverge despite both systems being "non-Poisson."

### Page 5 — Discussion, Limitations, Future Work, Conclusion
- **5. Discussion:**
  - When Poisson is "good enough": low utilization (MBTA ρ=0.15–0.20 → Poisson overestimate is conservative/safe-side); high-capacity systems (BB MIT Vassar, 53 docks → Wq≈0 regardless of arrival model); short time windows with stationary rate (BB Kendall T midnight, CV≈1.0).
  - When Poisson breaks down: strong time-of-day non-stationarity; schedule-driven regularity; finite-capacity systems at moderate utilization; combined arrival + service non-stationarity.
- **6. Limitations:** (a) Bluebikes arrival censoring at full docks (Mellou & Jaillet 2019 provide canonical correction methodology; excluded from this study's scope); (b) empirical DES destroys autocorrelation — explains the artificial 0.9s MBTA Wq; (c) limited geographic scope (2 BB stations, 1 MBTA station); (d) Sep–Dec 2025 window may not generalize across seasons.
- **7. Future Work:** (a) re-run Poisson tests on censoring-corrected Bluebikes arrivals via Mellou & Jaillet's AVG+TREND estimator — does this close the 75× Erlang B gap?; (b) incorporate autocorrelation-preserving arrival generators (time-series bootstrap, Markov-modulated Poisson) to recover the ~0s MBTA Wq; (c) extend to non-stationary service-time models.
- **8. Conclusion:** one-paragraph summary of the core finding and its practical implication for transportation engineers.
- **References** (overflow allowed; does not count toward 5-page limit).

---

## 3. Appendix Structure (≤10 pages)

Only what strengthens the main report; not a dumping ground.

- **A. Full methodology details** (~2 pages): fullness-exclusion algorithm (incl. pseudocode), service-rate estimation via Little's Law for BB, DES implementation details (SimPy resource model, warmup justification, replication CIs).
- **B. Extended results tables** (~2–3 pages): full goodness-of-fit statistics (KS, AD, χ² for all four candidate distributions × four systems); CV/IoD breakdown by hour-of-day and day-of-week; Wq analytical vs all DES variants with 95% CIs.
- **C. Supplementary figures** (~4–5 pages): Phase 1 exploratory plots (time series, hour-of-day arrival patterns, dock fullness over time); Phase 2 histograms and QQ plots; Phase 3 error summary figure.
- **D. Derivations** (~1 page): M/M/c Wq formula, Erlang B recursion, service-rate derivation via Little's Law.

*Reproducibility is handled as separate artifacts (README, environment.yml, seed fixation, MIT license) under Phase 4.3 — the GitHub repo URL is cited in Main §2.*

---

## 4. Figures to include

| # | Location | Content | Source |
|---|---|---|---|
| Fig 1 | Main §4.1 | CDF overlay + CV by hour-of-day (2-panel) | Phase 2 outputs + new composite |
| Fig 2 | Main §4.2 | Wq comparison bar chart (log scale) | `phase3_wq_comparison.png` — may need relabeling |
| Appx A-D | Appendix | ~8 supplementary figures (time series, histograms, error summary) | Existing Phase 1–3 outputs |

Total figures in main report: **2** (keeps page budget realistic).

---

## 5. Writing workflow

### 5.1 Division of labor
- **Takayuki (primary draft):** all sections §1–§8 and Appendix A–D, including the Mellou & Jaillet (2019) paragraphs in §6 Limitations and §7 Future Work.
- **Alex:**
  - Review full report for clarity, consistency, editing (Phase 4.2.6).
  - Code commenting across all scripts (Phase 4.2.7).

### 5.2 Iteration approach
1. **Outline + skeleton (Day 1–2):** populate each section with headers and bullet-point claims. No prose yet. Get user review.
2. **First prose draft (Day 3–6):** fill in each section, keep figures as placeholders. Aim for ~6 pages of prose (will trim to 5).
3. **Figure finalization (Day 5–7):** generate/polish the 2 main-report figures and appendix figures. Consistent styling (fonts, colors, axis labels).
4. **Trim + tighten (Day 8–10):** cut to 5 pages. Every sentence earns its place.
5. **References pass (Day 10):** complete bibliography, consistent citation style (likely numbered / IEEE).
6. **User review checkpoint (Day 10–11):** full draft review.
7. **Alex review (Day 11–13):** Alex reads, edits for clarity.
8. **Final revisions + polish (Day 13–15):** integrate feedback, final page-budget check.
9. **Submission buffer (Day 16–17):** 2 days of slack before 2026-05-08 deadline.

### 5.3 User checkpoints
- **Checkpoint 1:** after outline (Day 2) — approve structure before prose.
- **Checkpoint 2:** after first full prose draft (Day 6) — content approval.
- **Checkpoint 3:** after trim to 5 pages (Day 10) — pre-Alex-review approval.
- **Checkpoint 4 (final):** before submission (Day 15–16).

---

## 6. Format and tooling

- **Source format:** **LaTeX** (confirmed). No course-provided template per guideline review; use plain `article` class.
- **Class file settings:** `\documentclass[11pt]{article}`, 1-inch margins (`geometry` package), single column, 1.15 line spacing.
- **Figures:** regenerate as PDF (vector) where possible; PNG only for bar/bitmap charts.
- **References:** BibTeX file `references.bib`; numeric citation style (IEEE-like, compact — matches "Nature-style" conciseness guidance).
- **Output directory:** `project-docs/report/` (to be created).
- **Working files:** `report.tex` (main), `appendix.tex` (appendix), `references.bib`, `figures/` subdirectory.

---

## 7. Out of scope (explicitly)

- Implementing Mellou & Jaillet (2019) latent demand correction (decided in §1.3.6, D12).
- Adding new stations or time windows.
- Bootstrapped CIs for CV / IoD (not required for the Poisson hypothesis test — KS / AD already establish rejection).
- Formatting as a Nature-journal submission (we follow course guidelines, not Nature's actual template).

---

## 8. Risks and mitigations

| Risk | Mitigation |
|---|---|
| 5-page limit violated | Write to 6 pages, ruthlessly trim in Day 8–10 pass. Move anything marginal to appendix. |
| Course template released late | Start in plain LaTeX; migrate if a template is announced. |
| Figure regeneration needs code changes | All Phase 1–3 figures already generated with fullness-corrected data (per Prompt #99); only styling passes expected. |
| LaTeX compilation issues | Fall back to Pandoc markdown→PDF if LaTeX stalls; slightly less polish but functional. |

---

## 9. First deliverable after approval

Upon approval of this plan, the immediate next output is the **outline document** (`project-docs/report/outline.md`): section headers, subsection bullets, and placeholder figures/tables, with no prose. Estimated effort: 1–2 hours.

---

## 10. Open questions — resolved

1. ~~**LaTeX or Markdown+Pandoc?**~~ → **LaTeX** (confirmed 2026-04-21)
2. ~~**Course-provided template?**~~ → **None** (confirmed via guideline review); use plain `article` class
3. ~~**Citation style?**~~ → **Numeric (IEEE-like)** — default accepted pending user objection
4. ~~**Alex coordination?**~~ → review (4.2.6) + code commenting (4.2.7) only
