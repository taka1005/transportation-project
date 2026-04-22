# Report Outline

**Project:** Is Poisson Good Enough? Evaluating Queueing Models for Urban Mobility Systems
**Authors:** Alexander Lim Yu Sheng, Takayuki Tahara
**Course:** MIT 1.200 Transportation: Foundations and Methods, Spring 2026
**Target:** ≤5 pages main + ≤10 pages appendix
**Status:** Outline — no prose yet (Phase 4.2, Task #1)

---

## Main Report

### Title, Authors, Abstract (top of p.1)

- **Title:** Is Poisson Good Enough? Evaluating Queueing Models for Urban Mobility Systems
- **Abstract (~150 words) — claims to include:**
  - Problem: Poisson is the default arrival assumption in queueing; we ask how far it departs from reality and how much queueing predictions suffer when it does.
  - Approach: two contrasting Boston systems — Bluebikes (user-driven) at Kendall/MIT and MIT Vassar stations and MBTA Red Line (schedule-driven) at Kendall/MIT, Sep–Dec 2025. Inter-arrival statistics, distribution fitting, M/M/c and Erlang B analytics, SimPy DES with Poisson, empirical, and best-fit arrivals.
  - Headline: both systems reject Poisson (KS, AD, χ² p≈0), but in opposite directions — Bluebikes overdispersed (CV 1.75–1.90, best-fit Weibull), MBTA underdispersed (CV 0.63–0.71, best-fit Log-normal).
  - Consequence: Poisson M/M/c underestimates Bluebikes Wq by ≈7× at Kendall/MIT; Poisson M/M/1 overestimates MBTA Wq by 5–12×. Erlang B predicts 0.07% blocking vs 5.32% observed at Kendall/MIT — a 75× gap that arrivals alone cannot close, pointing to service-process non-stationarity.
  - Takeaway: Poisson's errors are directional and asymmetric in cost — it underestimates for user-driven systems (risking under-provisioning and user harm) and overestimates for schedule-driven systems (risking over-investment by the operator). "Conservative" is not "safe" in capital-intensive transport infrastructure; Poisson is a harmless approximation only when predicted and observed values both fall below the decision threshold.

---

### §1. Introduction (p.1)

- **1.1 Motivation**
  - Poisson process is the foundational arrival model in queueing theory; closed-form M/M/c and Erlang B results drive most transportation capacity planning.
  - Real urban mobility arrivals are driven by schedules, time-of-day demand, and operational disruptions — likely non-Poisson.
  - Practical question: when Poisson is wrong, how wrong are its predictions?
- **1.2 Why these two systems**
  - Bluebikes = user-driven, unscheduled, capacity-constrained (finite docks).
  - MBTA Red Line = schedule-driven, timetable-regulated, effectively infinite capacity per platform.
  - Same city, same period, opposite arrival-process regimes — a controlled contrast.
- **1.3 Research questions (verbatim from proposal)**
  1. To what extent do the arrivals deviate from Poisson?
  2. How accurately do Poisson-based queueing models predict Wq, Lq, W, and blocking probability?
  3. When is Poisson a reasonable engineering approximation?
- **1.4 Contributions**
  - Quantitative Poisson-deviation measurements for two real Boston systems.
  - Side-by-side comparison of analytical Poisson queueing vs empirical-distribution and best-fit-distribution DES.
  - Identification of a 75× Erlang B blocking-probability gap that reveals service-process non-stationarity as a distinct error source.
  - A decision-threshold framework for when Poisson is usable in transport planning: we separate the *direction* of Poisson's error (under- vs over-estimation) from its *absolute magnitude relative to the decision threshold*, and show that "conservative" predictions are not automatically safe when over-provisioning carries large capital cost.

---

### §2. Data (p.2, top half)

- **2.1 Bluebikes** — Sep–Dec 2025 public trip data; two stations:
  - M32004 — Kendall/MIT (23 docks, transit hub; N=9,090 after fullness exclusion)
  - M32042 — MIT Vassar St (53 docks, residential; N=19,275 after fullness exclusion)
  - Arrival = trip end at station; operating-hours filter applied.
- **2.2 MBTA Red Line** — Sep–Dec 2025 LAMP subway performance:
  - Kendall/MIT station (`place-knncl`), Northbound (N=20,366) and Southbound (N=20,880).
  - Arrival = train arrival at platform; overnight gaps excluded (intraday IAT).
- **2.3 Data treatment**
  - Service-disruption days flagged and excluded (~6.8% of Bluebikes time).
  - Bluebikes dock-fullness censoring: look-ahead-corrected inventory reconstruction; full-capacity periods excluded from λ, μ, and distribution fitting (see Appendix A.1).
- **2.4 Code and data availability** — *one sentence pointing to GitHub repo (https://github.com/taka1005/transportation-project), MIT license.*

---

### §3. Methods (p.2, bottom half)

- **3.1 Arrival-process characterization**
  - Inter-arrival time (IAT): summary statistics (mean, SD, CV, skewness).
  - Count statistics: Index of Dispersion (IoD) at 15/30/60-min windows.
  - Distribution fitting: exponential, log-normal, Weibull, gamma (MLE).
  - Goodness-of-fit: Kolmogorov–Smirnov, Anderson–Darling, chi-squared.
  - Segmentation by hour-of-day and day-of-week to probe non-stationarity.
- **3.2 Queueing models**
  - Bluebikes: M/M/c (c = dock count; infinite queue) and M/M/c/c (Erlang B, loss model). Service rate μ estimated from inventory via Little's Law.
  - MBTA: M/M/1; service time = dwell time.
  - Key formulas (Wq for M/M/c, Erlang B recursion) — full derivations in Appendix D.
- **3.3 Discrete-event simulation** (SimPy)
  - Three arrival generators per system: Poisson (baseline), empirical-IAT bootstrap, best-fit distribution.
  - 20,000 arrivals per replication, 2,000-arrival warmup, 10 replications, 95% CI.

---

### §4. Results (p.3 + p.4)

#### §4.1 Arrivals reject Poisson — in opposite directions (p.3)

- **Table 1** — Summary statistics for all four systems: N, λ [arr/min], mean IAT, CV, skewness, IoD (30-min window).
- Narrative claims:
  - All four systems reject exponential IAT at p≈0 across KS, AD, χ² — Poisson formally untenable.
  - Bluebikes CV=1.75–1.90 (overdispersed); MBTA CV=0.63–0.71 (underdispersed).
  - Best fit: Weibull for Bluebikes (shape c≈0.72, decreasing hazard = bursty); Log-normal for MBTA (schedule + multiplicative noise).
  - Segmented CV (Appendix B): Bluebikes approaches CV≈1 at midnight off-peak (Kendall/MIT); MBTA stays underdispersed at all hours.
- **Figure 1** (2-panel): (a) empirical CDF of IAT with fitted exponential / Weibull / Log-normal overlays for BB Kendall T and MBTA Northbound; (b) CV by hour-of-day for all four systems with Poisson reference line at CV=1.
  - Source: derived from `outputs/figures/phase2_cdfs.png` + new CV-by-hour panel to be generated.

#### §4.2 Queueing predictions diverge from observations (p.4)

- **Table 2** — Queueing outcomes per system: analytical (M/M/c or M/M/1), Poisson DES, empirical DES, best-fit DES. Columns: Wq [s], 95% CI; blocking probability (BB only).
- Narrative claims:
  - Bluebikes Kendall/MIT: M/M/c predicts Wq=1.6 s; empirical DES 10.8 s — Poisson underestimates by ≈7×.
  - Bluebikes MIT Vassar: Wq≈0 under all models (capacity dominates).
  - MBTA Northbound: M/M/1 predicts 20.5 s; empirical DES 4.2 s — Poisson overestimates by ≈5×.
  - MBTA Southbound: M/M/1 predicts 10.9 s; empirical DES 0.9 s — Poisson overestimates by ≈12× (the 0.9 s is itself a DES artifact from IAT shuffling; true scheduled Wq≈0, discussed in §6.2).
  - Best-fit-distribution DES ≈ empirical DES for all systems → Weibull / Log-normal are good surrogates.
- **Figure 2** — Wq comparison across the four systems (grouped bar chart, log y-axis), showing analytical vs Poisson-DES vs empirical-DES vs best-fit-DES.
  - Source: adapted from `outputs/figures/phase3_wq_comparison.png`.

#### §4.3 The Erlang B blocking gap (p.4, bottom)

- Single-paragraph result:
  - Kendall/MIT observed full-capacity rate: 5.32%.
  - Erlang B prediction: 0.07% (Poisson arrivals, exponential service).
  - Finite-capacity empirical DES prediction: 0.60%.
  - Even with exact empirical arrivals, DES underpredicts by ≈9× — the residual gap points to service-time non-stationarity (dock occupancy varies strongly by hour), a limitation of all Markovian models.
- No separate figure in main text; pointer to Appendix Fig. C.5.

---

### §5. Discussion (p.5, top third)

*Framing: Poisson's error has two orthogonal axes — direction (under- vs over-estimation) and absolute magnitude relative to the decision threshold. "Conservative" in this setting does not mean "safe" because transport infrastructure decisions (platforms, fleet, docks) are capital-intensive and not symmetric in cost.*

- **5.1 Where Poisson misleads user-side decisions (under-provisioning risk)**
  - Bluebikes Kendall/MIT (user-driven, finite capacity, moderate utilization): Poisson M/M/c underestimates Wq by ≈7× and Erlang B underestimates blocking by 75×.
  - Consequence: planners under-size dock capacity or rebalancing effort, leading to service failures (users cannot dock, abandon trips).
  - The underestimation is amplified when the arrival process is both overdispersed (CV 1.75–1.90) and non-stationary (peak/off-peak CV ratio 2.00/1.37 at Kendall/MIT).

- **5.2 Where Poisson misleads operator-side decisions (over-provisioning risk)**
  - MBTA Red Line (schedule-driven, low utilization, ρ=0.15–0.20): Poisson M/M/1 overestimates Wq by 5–12×.
  - Consequence: if such predictions feed capital decisions (platform extensions, fleet acquisition) or operational ones (frequency increases), the agency risks large and irreversible over-investment.
  - "Conservative" is a misleading label in this regime — over-estimating Wq looks safe from the passenger side but can translate into billions of dollars of unnecessary infrastructure.

- **5.3 Where Poisson is a harmless approximation**
  - Condition: both predicted and observed Wq (or blocking probability) lie below any meaningful decision threshold.
  - Examples: Bluebikes MIT Vassar (53 docks → Wq≈0 under all models); MBTA in train-side queueing analyses (10–20 s and 0–4 s are both operationally negligible for decisions framed in minutes); short stationary windows (Bluebikes Kendall/MIT at midnight, CV≈1.0).
  - Caveat: harmlessness is a property of the decision, not the model. The same Poisson estimate becomes dangerous the moment it is used to justify a capital-intensive choice.

- **5.4 Broader implication — error direction is predictable from system structure**
  - Overdispersed (CV > 1) arrivals ⇒ Poisson under-predicts queueing ⇒ user-side risk. Expected for user-driven, unscheduled systems.
  - Underdispersed (CV < 1) arrivals ⇒ Poisson over-predicts queueing ⇒ operator-side risk. Expected for schedule-driven, timetable-regulated systems.
  - Engineers should evaluate error *direction* and *absolute magnitude* separately, and weigh each against the cost asymmetry of their specific decision (user harm vs capital waste).

### §6. Limitations (p.5, middle)

- **6.1 Arrival censoring at full Bluebikes docks.** Observed arrivals at Kendall/MIT understate latent demand during the 5.32% of time the station is full. Mellou and Jaillet (2019) provide an AVG+TREND convex-combination estimator (hold-out-optimized λ*≈0.76 on Capital Bikeshare data) that could recover lost incoming demand; we exclude full-capacity periods rather than reconstruct them to keep our Poisson tests methodologically clean (injecting estimated arrivals would confound "real Poisson deviation" with "estimator residual").
- **6.2 DES destroys IAT autocorrelation.** Our empirical DES samples IATs i.i.d., so the 0.9 s MBTA Southbound Wq is an artifact of occasionally drawing a short interval after a long one — something the real schedule prevents. The marginal distribution is reproduced; the sequence structure is not.
- **6.3 Geographic and temporal scope.** Two Bluebikes stations, one MBTA station, 4 months. Seasonal (winter weather) and other-line generalization untested.
- **6.4 Service-process non-stationarity unmodeled.** The residual Erlang B gap (§4.3) is attributable to service-time variation we did not separately characterize.

### §7. Future Work (p.5, bottom third)

- **7.1 Censoring-corrected Poisson test.** Re-run §4.1 KS / AD / χ² tests on Bluebikes arrivals reconstructed via Mellou–Jaillet. If the corrected arrivals remain non-Poisson with similar CV, current conclusions hold; if they approach CV=1, the observed deviation is partly a censoring artifact. The 75× Erlang B blocking gap at Kendall/MIT is the natural target: does arrival correction alone close it, or does it confirm service-process non-stationarity as the dominant residual?
- **7.2 Autocorrelation-preserving simulation.** Replace i.i.d. IAT bootstrap with time-series bootstrap or Markov-modulated Poisson to recover the ≈0 s MBTA Wq and stress-test whether M/M/· overestimate persists under realistic burstiness.
- **7.3 Non-stationary service models.** Fit hour-of-day-indexed service distributions for Bluebikes; re-compute Erlang B with a time-varying μ.
- **7.4 Broader coverage.** Multiple stations per mode, full-year data, other MBTA lines.

### §8. Conclusion (p.5, last lines)

- One-paragraph closing. Key sentence: *Poisson is good enough only when its error — in whichever direction — stays below the decision threshold that matters to the planner. For schedule-driven transit it over-predicts wait and risks costly over-investment; for user-driven, finite-capacity systems it under-predicts wait and blocking, risking service failure. And because service-process non-stationarity is a separate error source (evidenced by the 75× Erlang B gap), correcting the arrival model alone cannot restore predictive validity once a system operates at meaningful utilization.*

### References (overflow page, does not count toward 5-page limit)

- **Planned citations (compact numeric IEEE style):**
  1. Kleinrock, *Queueing Systems, Vol. 1* (M/M/c, M/M/1 results)
  2. Erlang, *Solution of some problems in the theory of probabilities of significance in automatic telephone exchanges* (1917) — Erlang B
  3. Little, *A Proof for the Queuing Formula L = λW* (1961)
  4. Mellou & Jaillet, *Dynamic Resource Redistribution and Demand Estimation: An Application to Bike Sharing Systems*, MIT working paper (2019)
  5. MBTA LAMP documentation / data source citation
  6. Bluebikes / Metro Bike Share trip data citation (System Data)
  7. SimPy reference (Team SimPy, Discrete-Event Simulation Library)
  8. Scipy reference (distribution fitting, K-S test)
  9. O'Mahony & Shmoys 2015 — bike-share rebalancing (cited by Mellou–Jaillet)
  10. Additional queueing / transportation references as needed

---

## Appendix

### Appendix A — Full methodology details (≈2 pages)

- **A.1 Bluebikes fullness exclusion algorithm.** Look-ahead-corrected inventory reconstruction; merge of overlapping full-capacity periods (cf. Mellou–Jaillet "artificial outage endings"); exclusion of IATs that span any full-capacity interval. Pseudocode + example timeline figure.
- **A.2 Service-rate estimation via Little's Law for Bluebikes.** μ = (avg non-full inventory) / λ per station; sensitivity to inventory reconstruction assumptions.
- **A.3 DES implementation.** SimPy resource model (dock count as server capacity); warmup = 2,000 arrivals chosen from queue-length convergence plots; 10 replications; 95% CI via t-distribution on replication means.
- **A.4 Arrival generators.** (i) Poisson: `Exponential(1/λ)`. (ii) Empirical: i.i.d. bootstrap from observed IAT. (iii) Best-fit: sample from Weibull(c, scale) for BB or Log-normal(μ, σ) for MBTA with MLE-fitted parameters.

### Appendix B — Extended results tables (≈2–3 pages)

- **Table B.1** — Full goodness-of-fit statistics: KS statistic + p-value, AD statistic, χ² statistic + p-value, AIC, for each of {exponential, log-normal, Weibull, gamma} × each of {BB Kendall, BB MIT Vassar, MBTA NB, MBTA SB}.
- **Table B.2** — CV and IoD by hour-of-day (0–23) for all four systems.
- **Table B.3** — CV and IoD by day-of-week for all four systems.
- **Table B.4** — Full queueing outcomes: analytical + 3 DES variants × {Wq mean, Wq 95% CI, Lq mean, W mean, blocking prob (BB)}.

### Appendix C — Supplementary figures (≈4–5 pages)

- **Fig C.1** — Bluebikes daily arrival counts (time series) at both stations.
- **Fig C.2** — Bluebikes hour-of-day arrival profile (both stations, weekday vs weekend).
- **Fig C.3** — MBTA headway by hour, both directions.
- **Fig C.4** — IAT histograms with fitted distributions overlaid (linear and log scales; all four systems).
- **Fig C.5** — Blocking probability comparison: Erlang B vs DES (Poisson) vs DES (empirical) vs observed, for BB stations. Log y-axis.
- **Fig C.6** — Error summary: relative error of analytical vs empirical-DES for Wq, across all four systems.
- **Fig C.7** — Bluebikes dock inventory over time (both stations, 7-day snippet) with full-capacity intervals shaded.
- **Fig C.8** — CV and IoD by hour-of-day line plots.

### Appendix D — Derivations (≈1 page)

- **D.1** M/M/c Wq via Erlang C.
- **D.2** Erlang B recursion `B(c,a) = a·B(c−1,a) / (c + a·B(c−1,a))`.
- **D.3** Little's Law service-rate derivation for Bluebikes: μ = L / (λ·W) with L=avg non-full inventory.

---

## Outstanding items before prose draft

1. User approval of this outline (checkpoint 1).
2. Confirmation of author list and any additional acknowledgements.
3. Decision on whether to include a specific M/M/c or M/M/1 equation inline in §3 or relegate all math to Appendix D.
4. Whether the short Erlang B finding in §4.3 warrants its own small figure in the main text (currently no).
