# Research Plan: Is Poisson Good Enough?

**Evaluating Queueing Models for Urban Mobility Systems**

Course: MIT 1.200 Transportation: Foundations and Methods, Spring 2026
Timeline: 2026-04-08 → 2026-05-08

---

## Phase 1: Data Acquisition and Pipeline Setup (Week 1: Apr 8–14)

### 1.1 Dataset Selection and Download

- [x] **1.1.1** Identify and download Bluebikes public trip data (Sep–Dec 2025)
  - Downloaded: 202509, 202510, 202511, 202512 (~373MB total)
  - Selected stations: M32004 (Kendall T), M32042 (MIT Vassar St)
- [x] **1.1.2** Identify and download MBTA LAMP subway performance data — Red Line
  - Downloaded: 122 daily Parquet files (Sep–Dec 2025, ~219MB)
  - Kendall/MIT station: place-knncl
- [x] **1.1.3** Document raw data sources, formats, and licensing in a data dictionary
  - Created: project-docs/data-artifacts/data_dictionary.md

### 1.2 Define Arrival Events

- [x] **1.2.1** Define "arrival" for Bluebikes: trip end (bike return) at two selected stations:
  - Station A: M32004 (Kendall T)
  - Station B: M32042 (MIT Vassar St)
- [x] **1.2.2** Define "arrival" for MBTA: train arrival at Kendall/MIT Red Line station (place-knncl)
- [x] **1.2.3** Document arrival definitions in the data dictionary

### 1.3 Data Pipeline Construction

- [x] **1.3.1** Build pipeline to extract arrival timestamps from Bluebikes data
- [x] **1.3.2** Build pipeline to extract arrival timestamps from MBTA data
- [x] **1.3.3** Compute inter-arrival times for both systems
- [x] **1.3.4** Validate pipeline output (spot-check timestamps, handle missing data)
  - Segment data to operating hours only
  - Flag periods of service disruption and exclude from primary analysis (6.8% flagged)
- [x] **1.3.5** Address Bluebikes dock fullness censoring
  - Implemented look-ahead corrected inventory reconstruction
  - Station capacities: Kendall T = 23, MIT Vassar St = 53
  - Kendall T: at capacity 5.3%, empty 2.7%
  - MIT Vassar St: at capacity 0.4%, empty 6.3%
  - Reconstruct approximate station inventory using arrival/departure counts
  - Flag time periods where station is likely at full capacity (arrivals are censored)
  - Exclusion of full-capacity periods will be applied in Phase 2 analysis
  - Document censoring as a known limitation in the report
- [x] **1.3.6** *(Alex)* Literature review on dock fullness adjustment methods for bike-share systems
  - Reviewed Mellou & Jaillet (2019), "Dynamic Resource Redistribution and Demand Estimation: An Application to Bike Sharing Systems" (MIT working paper)
  - Method: AVG + TREND convex combination estimator (eq. 4, §3.2.3) for lost demand; shift model with distance-based reallocation (§3.3)
  - Validated on Capital Bikeshare DC data (May–Sep 2017); optimal λ*=75.56% via hold-out MSE minimization
  - **Decision:** Do NOT implement. Document as Limitations + cite in Future Work.
  - Rationale: (1) scope mismatch — paper targets rebalancing, we target arrival-process characterization; (2) injecting estimated "true" arrivals would confound whether Poisson deviation is a real property or estimator artifact; (3) current full-capacity exclusion barely moves results (CV/best-fit robust); (4) implementation cost exceeds remaining timeline budget

### 1.4 Exploratory Data Visualization

- [x] **1.4.1** Visualize Bluebikes arrival patterns (time-of-day, day-of-week, monthly)
- [x] **1.4.2** Visualize MBTA arrival patterns and headways
- [x] **1.4.3** Visualize inter-arrival time distributions (histograms) for both systems
- [x] **1.4.4** Visualize estimated dock fullness periods for Bluebikes stations
  - > **Checkpoint:** Review visualizations with user before proceeding to Phase 2. Additional questions may arise.
- [ ] **1.4.5** *(Alex)* Review visualizations and identify additional questions or issues

---

## Phase 2: Descriptive Arrival-Process Analysis (Week 2: Apr 15–21)

### 2.1 Summary Statistics

- [x] **2.1.1** Compute mean, standard deviation, coefficient of variation (CV), and skewness of inter-arrival times for Bluebikes
  - Kendall T: N=9,090, mean=11.2min, CV=1.75, skewness=6.8
  - MIT Vassar St: N=19,275, mean=6.3min, CV=1.90, skewness=7.7
  - Both stations CV > 1 (more variable than Poisson)
- [x] **2.1.2** Compute the same statistics for MBTA
  - Northbound: N=20,366, mean=6.5min, CV=0.71, skewness=3.3
  - Southbound: N=20,880, mean=6.3min, CV=0.63, skewness=4.5
  - Both directions CV < 1 (more regular than Poisson, schedule-driven)
  - Note: overnight gaps excluded (intraday IAT); Bluebikes full-capacity periods excluded
- [x] **2.1.3** Compare CV to 1.0 (CV = 1 is the theoretical value for exponential inter-arrival times under a Poisson process)
  - Interpret CV < 1 (more regular than Poisson, e.g., schedule-driven) vs. CV > 1 (more variable than Poisson, e.g., bursty demand)
  - Discuss the magnitude of deviation: how close to 1 is "close enough" for practical purposes?
  - Bluebikes: CV=1.75–1.90 (overdispersed, bursty demand driven by time-of-day non-stationarity)
  - MBTA: CV=0.63–0.71 (underdispersed, schedule-driven regularity with operational noise)
  - All four systems reject Poisson; Bluebikes and MBTA deviate in opposite directions
  - > **Taka memo:** MIT Vassar St (residential) having higher CV than Kendall T (transit hub) is surprising. A station with steady all-day traffic may appear more Poisson-like over a full day. However, when segmented into 1-hour windows, the residential station may actually be closer to Poisson — to be tested in Step 2.1.4.
- [x] **2.1.4** Segment CV analysis by time-of-day (peak vs. off-peak) and day-of-week for both systems
  - Assess whether Poisson holds better during certain periods (e.g., off-peak may be more Poisson-like)
  - Kendall T: strong peak/off-peak difference (2.00 vs 1.37); off-peak and late night approach Poisson (CV≈1.0 at midnight)
  - MIT Vassar St: smaller peak/off-peak difference (1.71 vs 1.57); CV > 1 at all hours
  - MBTA: CV < 1 at all hours; weekends more regular than weekdays
  - Taka hypothesis (residential station more Poisson when segmented hourly) not supported — Kendall T approaches Poisson faster in off-peak

### 2.2 Distribution Fitting and Comparison

- [x] **2.2.1** Plot empirical inter-arrival time distributions (histograms, CDFs) for both systems
  - Generated: phase2_histograms.png, phase2_cdfs.png, phase2_histograms_log.png
  - Bluebikes: heavy-tailed, overdispersed vs exponential; MBTA: light-tailed, underdispersed vs exponential
- [x] **2.2.2** Fit exponential distribution to observed inter-arrival times
  - Exponential is the worst fit (highest AIC) for all four systems
- [x] **2.2.3** Fit candidate non-Poisson distributions (e.g., log-normal, Weibull, gamma) and select best-fit
  - Document rationale for candidate distribution selection and cite relevant literature
  - Bluebikes: Weibull best (c=0.714–0.716, shape < 1 indicates decreasing hazard rate / bursty arrivals)
  - MBTA: Log-normal best (schedule + multiplicative noise)
  - AIC improvement over exponential: −2,167 to −17,833 across systems
  - Generated: phase2_fitted_distributions.png
- [x] **2.2.4** Perform goodness-of-fit tests (Kolmogorov-Smirnov, Anderson-Darling, chi-squared) to formally test the exponential (Poisson) hypothesis
  - All three tests reject exponential (Poisson) for all systems (p ≈ 0)
  - All parametric distributions formally rejected due to large sample sizes (N=9k–21k)
  - Relative comparison: Weibull (Bluebikes) and Log-normal (MBTA) have much smaller KS statistics than exponential
  - Anderson-Darling: exponential statistic 480–2,734 vs critical value ≈ 2 (extreme rejection)
- [x] **2.2.5** Explain in the report why both empirical and parametric non-Poisson distributions are used
  - Empirical DES: assumption-free, closest to reality, but dataset-specific and hard to generalize
  - Parametric best-fit DES: compact representation, interpretable parameters, generalizable to other contexts
  - Both compared against M/M/1 (exponential) baseline to quantify the "cost of the Poisson assumption"
  - Candidate distributions chosen for theoretical grounding: log-normal (multiplicative noise, common in travel times), Weibull (flexible hazard rate), gamma (natural generalization of exponential)

### 2.3 Arrival Count Analysis

- [x] **2.3.1** Count arrivals in multiple time windows (15-min, 30-min, 1-hour) to examine scale dependence
- [x] **2.3.2** Compare mean vs. variance of arrival counts per window (equal mean and variance is a hallmark of a Poisson distribution)
- [x] **2.3.3** Compute the Index of Dispersion (variance/mean ratio) across time windows
  - Bluebikes IoD=2.2–8.0 (overdispersed), increases with window size (non-stationarity effect)
  - MBTA IoD=0.4–0.6 (underdispersed), approaches 1.0 with larger windows
- [x] **2.3.4** Segment analysis by time-of-day and day-of-week to check for non-stationarity
  - Bluebikes: peak IoD > off-peak IoD; MBTA: peak IoD < off-peak IoD (opposite behavior)
  - MBTA weekends very regular (IoD≈0.31)

### 2.4 Interim Findings

- [x] **2.4.1** Summarize whether each system's arrivals appear Poisson, and characterize deviations
  - Bluebikes: NOT Poisson — overdispersed (CV>1, IoD>>1), bursty arrivals driven by time-of-day non-stationarity
  - MBTA: NOT Poisson — underdispersed (CV<1, IoD<1), schedule-driven regularity
  - Deviations are in opposite directions: Bluebikes too variable, MBTA too regular
- [x] **2.4.2** Identify the best-fit alternative distribution for each system
  - Bluebikes: Weibull (c=0.714–0.716), AIC improvement −2,167 to −4,890 over exponential
  - MBTA: Log-normal (s=0.49–0.57), AIC improvement −12,878 to −17,833 over exponential
  - > **Checkpoint:** Review interim findings with user before proceeding to queueing analysis.

---

## Phase 3: Queueing Analysis and Simulation (Week 3: Apr 22–28)

### 3.0 Select Queueing Baseline

- [x] **3.0.1** Confirm M/M/1 as the primary Poisson-based queueing model
  - Document why M/M/1 was selected (simplest memoryless queueing model; serves as a baseline to measure the cost of the Poisson assumption)
  - Briefly compare with alternatives (M/G/1, G/G/1) and cite relevant literature
  - M/M/1 chosen because: (1) closed-form solutions for Wq, Lq, W enable direct comparison, (2) isolates the arrival-process assumption (both arrival and service memoryless), (3) M/G/1 generalizes service but conflates two effects, G/G/1 has no closed-form solution
- [x] **3.0.2** Define service time assumptions for each system
  - Bluebikes: dock occupancy time (time a bike occupies a dock slot from arrival until next departure)
  - MBTA: dwell time (time a train is stopped at the platform)
  - > **Decision D5 resolved:** Bluebikes = dock occupancy, MBTA = dwell time
- [x] **3.0.3** Document model assumptions and parameters
  - M/M/1 assumptions: Poisson arrivals (rate λ), exponential service (rate μ), single server, FCFS, infinite queue, steady state (λ < μ)

### 3.1 M/M/1 Analytical Baseline

- [x] **3.1.1** Compute M/M/1 and M/M/c theoretical predictions using observed mean arrival rate (λ) and service rate (μ):
  - Average delay (Wq), average queue length (Lq), average system time (W)
  - M/M/c uses Erlang C formula; c = dock count for Bluebikes, c = 1 for MBTA
  - Bluebikes service rate estimated via Little's Law (avg inventory / arrival rate)
  - MBTA service rate from dwell time data
- [x] **3.1.2** Compute predictions for both Bluebikes and MBTA
  - Bluebikes M/M/1: UNSTABLE (ρ=11.2–17.6) — single-server model physically inappropriate
  - Bluebikes M/M/c: stable (ρ_server=0.33–0.49), near-zero wait times — consistent with real-world observation
  - MBTA M/M/1: stable (ρ=0.15–0.20), low wait times (10.7–20.1 sec)
  - Key finding: Bluebikes analysis must use M/M/c (not M/M/1) as the Poisson baseline

### 3.2 Discrete-Event Simulation (SimPy)

- [x] **3.2.1** Build a discrete-event simulation using SimPy with the empirical inter-arrival distribution
- [x] **3.2.2** Build a DES variant using the best-fit non-Poisson distribution from Phase 2
- [x] **3.2.3** Run simulations for both Bluebikes and MBTA
- [x] **3.2.4** Collect simulation outputs: average delay, average queue length, average system time
- [x] **3.2.5** Validate simulation (warm-up period, sufficient run length, multiple replications for confidence intervals)
  - 2,000 warmup arrivals, 20,000 total, 10 replications with 95% CI
  - Poisson DES matches analytical solutions (M/M/1 within 2%, M/M/c within 0.2% for W)
  - Key results: Poisson underestimates Bluebikes Wq by ~7x (1.6s vs 10.8s), overestimates MBTA Wq by 5–12x
  - Empirical and best-fit DES produce nearly identical results (Weibull/Log-normal are good approximations)
  - All results use fullness-corrected data for Bluebikes

### 3.2a Fullness Correction and Model Revision (inserted retroactively)

> **Background:** Phase 2 and initial Phase 3 results did NOT exclude Bluebikes full-capacity periods from analysis, despite Step 1.3.5 planning to do so. This introduces censoring bias (λ underestimated, service time estimates skewed). Additionally, the M/M/c infinite-queue model does not match Bluebikes reality (full docks reject arrivals, no waiting). This section corrects both issues.

**Data usage strategy:**

| Analysis | Full-capacity data | Purpose |
|---|---|---|
| λ estimation (BB) | **Exclude** | Recover true (unconstrained) arrival rate |
| Distribution fitting (BB) | **Exclude** | Unbiased inter-arrival time distribution |
| μ estimation (BB inventory) | **Exclude** | Avoid capacity-clamped inventory bias |
| M/M/c analytical (BB) | Use corrected λ, μ | Theoretical baseline (infinite queue) |
| M/M/c/c Erlang B (BB) | Use corrected λ, μ | Predict blocking probability |
| Erlang B validation | **Use observed fullness rate** | Compare predicted vs actual blocking |
| MBTA analysis | No change | No fullness censoring issue |

**Modification steps:**

- [x] **3.2a.1** Implement full-capacity exclusion for Bluebikes inter-arrival times
  - Created src/fullness_filter.py: merges overlapping full-capacity periods, excludes affected IATs
  - Kendall T: 1,145 arrivals excluded (11.0%), MIT Vassar St: 176 excluded (0.9%)
- [x] **3.2a.2** Re-run Phase 2 Bluebikes analysis with corrected data
  - Created src/phase2_rerun.py: before/after comparison
  - Kendall T: CV 1.69→1.75 (+3.6%), Weibull c=0.730→0.716
  - MIT Vassar St: virtually unchanged (CV 1.90→1.90)
  - Weibull remains best-fit for both stations after correction
- [x] **3.2a.3** Re-estimate μ from inventory data excluding full-capacity periods
  - Kendall T: mean service 8,083→7,549 sec (−6.6%), ρ_server 0.51→0.49
  - MIT Vassar St: mean service 6,886→6,699 sec (−2.7%), ρ_server 0.34→0.33
- [x] **3.2a.4** Compute M/M/c/c (Erlang B) analytical predictions for Bluebikes
  - Kendall T: Erlang B predicts 0.07% blocking, observed fullness is 5.32% — **75× gap**
  - MIT Vassar St: Erlang B predicts ≈0%, observed 0.42%
  - Gap indicates exponential service time assumption is also violated (non-stationary dock occupancy)
- [x] **3.2a.5** Re-run M/M/c analytical predictions with corrected λ, μ
  - Kendall T: Wq=0.9s (corrected), MIT Vassar St: Wq≈0
- [x] **3.2a.6** Re-run DES simulations for Bluebikes with corrected inter-arrival data
  - Infinite queue: Poisson Wq=1.6s vs Empirical Wq=10.8s (6.6× underestimate)
  - Finite capacity: Poisson block=0.10% vs Empirical block=0.60% (6× underestimate)
  - Both models show Poisson underestimates congestion, but even empirical-arrival DES cannot reproduce observed 5.3% fullness — service process non-stationarity is the missing factor
- [x] **3.2a.7** Update all Bluebikes figures and tables with corrected results
  - Generated: phase3_wq_comparison.png, phase3_blocking_comparison.png, phase3_error_summary.png

### 3.2b Fullness-flag State-Transition Revision (inserted 2026-04-24)

> **Background:** Review of Appendix A.1 (2026-04-24) surfaced two defects in the original fullness-detection algorithm in `data_pipeline.py` + `fullness_filter.py`:
> 1. **Over-counting via clamp:** `at_full[i] = True` fired every time the running count exceeded $C_s$, including repeat trip-ends during an already-at-capacity state. Each such event is physical evidence that a slot was available at that instant (otherwise the trip-end would have been rejected), so flagging it as "full" is self-contradictory and inflates the observed fullness rate.
> 2. **Missing retract logic:** A candidate full interval $[T_1, T_2]$ that is interrupted by an intervening trip-end was nevertheless retained in the original algorithm (its end was defined by the next trip-start). The intervening trip-end proves non-fullness at that instant, so the interval cannot be claimed as continuously full without additional information.

**Revised definitions:**

- **Full flag (per event):** set only at a trip-end that causes the natural increment $I_s: C_s - 1 \to C_s$. clamp events (overflow corrections) remain in the code as bookkeeping for drift but do not set the flag.
- **Full interval (per segment):** $[T_1, T_2]$ is declared full iff (a) $T_1$ is a natural C-1→C entry, (b) $T_2$ is the next event at station $s$, (c) $T_2$ is a trip-start, AND (d) no trip-end appears in $(T_1, T_2)$. If (d) fails, the entire candidate interval is retracted; no partial interval is retained.

**Expected downstream effects:**

| Metric | Direction of change |
|---|---|
| Observed fullness rate (Kendall/MIT) | Lower (likely substantially below 5.32%) |
| Excluded IAT count | Lower (fewer intervals rejected) |
| $N$ after fullness exclusion | Higher (more IATs retained) |
| $\lambda$, $\mu$ estimates | Small change (depends on shift in excluded set) |
| Erlang B blocking prediction | Small change (λ, μ both slightly shift) |
| "75× gap" headline | **Likely shrinks** (observed numerator decreases) |

**Modification steps:**

- [x] **3.2b.1** Rewrote `reconstruct_inventory()` in `data_pipeline.py`: `at_full` fires only on natural $C_s-1 \to C_s$ trip-end increments (and `at_empty` symmetric); clamp remains as bookkeeping for unlogged rebalancing but does not set the flag. Dropped the `| (inventory >= capacity)` clause on `at_capacity`.
- [x] **3.2b.2** Rewrote `get_full_capacity_periods()` in `fullness_filter.py`: each natural entry is a candidate, committed only if the next station event is a trip-start with no intervening trip-end. Added helper `mark_in_full_periods()`; updated `get_observed_fullness_rate()` to a time-weighted fraction and `filter_inventory_for_service_rate()` to mask events inside committed spans.
- [x] **3.2b.3** Regenerated `data/processed/bb_inventory_*.parquet`. Observed fullness (time-weighted): Kendall/MIT **3.73%** (was 5.32%), MIT Vassar St **2.88%** (was 0.42%; the Vassar jump reflects the move from event-count to time-weighted, not a worsening of the station).
- [x] **3.2b.4** Re-ran `phase2_descriptive.py`. $N$_Kendall 9,090 → **9,566**; $N$_Vassar 19,275 → **19,300**. CV essentially unchanged (Kendall 1.75 → 1.753; Vassar 1.90 → 1.896). Weibull remains best-fit for BB; log-normal remains best-fit for MBTA. MBTA rows unchanged.
- [x] **3.2b.5** Re-ran `phase3_queueing.py` and `phase3_simulation.py`. Kendall M/M/c analytical $W_q$ 1.6 → **0.8 s**; empirical-DES $W_q$ 10.8 → **9.4 s**; Erlang B blocking 0.07% → **0.068%**; empirical-DES finite-capacity block 0.60% → **0.54%**. Headline Erlang B gap: 75× → **55×** at Kendall; Vassar now shows a non-trivial Erlang B ≈ 0 vs observed 2.88% gap that the old algorithm had masked. MBTA values essentially unchanged.
- [x] **3.2b.6** Regenerated all Phase 2/3 PNGs; copied into `project-docs/report/figures/`. Caught and fixed pre-revision hardcoded values in `visualize_phase3.py` (`plot_wq_comparison`, `plot_blocking_comparison`, `plot_error_summary`) so Fig 1 (main) and Table 2 stay synchronised.
- [x] **3.2b.7** Rewrote Appendix A.1 as four paragraphs (inventory reconstruction / full-capacity windows / exclusion rule / robustness). Removed the Mellou citation from A.1 (kept only in §6 Limitations and §7 Future Work). Stated the initial condition $\lfloor C_s/2 \rfloor$ honestly; described clamp as bookkeeping and the full flag as a state-transition with retract-on-intervening-trip-end semantics; dropped the "< 1 minute merge" sentence that was inconsistent with the implementation.
- [x] **3.2b.8** Updated numerical values throughout main.tex — Abstract ($55\times$ replaces $75\times$; wait underestimate reframed as "roughly an order of magnitude"), Contributions ($55\times$), §2 Data ($N$ and fullness rates), §4.2 Table 2, §4.3 narrative, §5 User-side risk, §6 Service non-stationarity, §7 Future Work, §8 Conclusion. Appendix A.2 service times (7,367 s Kendall; 6,670 s Vassar); Appendix Table B.4 $W_q$ and blocking values; Appendix Fig C.6 caption.
- [x] **3.2b.9** Added "Inventory reconstruction uncertainty" paragraph to §6 Limitations: $I_s$ carries a rebalancing bias between clamps; the retract rule biases toward omitting short full spans, so observed fullness and the $55\times$ gap are conservative lower bounds.
- [x] **3.2b.10** Recompiled LaTeX; main body stayed at 5 pages after tightening §4.2 / §5 / §6 / §8 prose. Final PDF is 15 pages total (main 5 + references 1 + appendix 9). Commits: 829ad75 (core revision), 588e1c9 (visualize_phase3 fix), 82eef07 (Wq infinite-queue clarification).

### 3.3 Error Quantification

- [x] **3.3.1** Compare Poisson-based predictions vs. empirical-DES outcomes for each metric
  - Bluebikes: M/M/c and M/M/c/c vs DES
  - MBTA: M/M/1 vs DES
- [x] **3.3.2** Compare Poisson-based predictions vs. best-fit-DES outcomes for each metric
  - Best-fit DES closely matches empirical DES for all systems
- [x] **3.3.3** Quantify relative and absolute error for each metric and each system
  - BB Kendall T Wq: Poisson underestimates by ~85% (1.6s vs 10.8s)
  - BB Kendall T blocking: Erlang B 0.07% vs DES Empirical 0.60% vs observed 5.32%
  - MBTA North Wq: Poisson overestimates by ~386% (20.5s vs 4.2s)
  - MBTA South Wq: Poisson overestimates by ~1,069% (10.9s vs 0.9s)
- [x] **3.3.4** Visualize the comparison (tables and/or plots)
  - Generated: phase3_wq_comparison.png, phase3_blocking_comparison.png, phase3_error_summary.png

---

## Phase 4: Synthesis, Reporting, and Presentation (Week 4: Apr 29–May 8)

### 4.1 Cross-Modal Synthesis

- [x] **4.1.1** Compare Poisson-fit quality: Bluebikes (user-driven) vs. MBTA (schedule-driven)
  - Both reject Poisson but in opposite directions: BB overdispersed (CV=1.75–1.90), MBTA underdispersed (CV=0.63–0.71)
  - Best-fit: Weibull for BB (bursty demand), Log-normal for MBTA (scheduled + noise)
  - MBTA deviates more strongly from exponential (KS=0.27–0.29) than BB (KS=0.13–0.14)
- [x] **4.1.2** Compare M/M/1 error magnitude across the two systems
  - BB Kendall T (M/M/c): Poisson underestimates Wq by ~7× (1.6s vs 10.8s)
  - MBTA: Poisson overestimates Wq by 5–12× (20.5s vs 4.2s North, 10.9s vs 0.9s South)
  - Error directions are opposite: Poisson is anti-conservative for BB, conservative for MBTA
  - Erlang B vs observed blocking (0.07% vs 5.32%) reveals service non-stationarity as additional error source
- [x] **4.1.3** Identify conditions under which Poisson is a reasonable engineering approximation
  - Short time windows with stable arrival rate (e.g., BB Kendall T midnight CV≈1.0)
  - High-capacity systems where arrival process doesn't matter (BB MIT Vassar St, 53 docks → Wq≈0 always)
  - Low-utilization systems where Poisson overestimates (conservative): MBTA ρ=0.15–0.20
- [x] **4.1.4** Identify conditions where Poisson breaks down and more general approaches are needed
  - Strong time-of-day non-stationarity (BB peak hours, CV>2)
  - Schedule-driven systems (MBTA, Poisson overestimates by 5–12×)
  - Finite-capacity systems at moderate utilization (BB Kendall T: blocking prediction off by 75×)
  - When both arrival AND service processes are non-stationary (blocking rate cannot be reproduced by correcting arrivals alone)

### 4.2 Final Report

- [x] **4.2.1** Draft report structure (problem statement, formulation, hypotheses, methods, results, conclusions)
  - Outline at `project-docs/report/outline.md`; structure approved 2026-04-21
  - > **Note for Limitations section:** Bluebikes arrival data is censored when docks are full — observed arrivals underestimate true demand. Mellou & Jaillet (2019) provide a canonical AVG+TREND estimator for lost incoming demand at full stations; Kendall T's 5.32% full-capacity rate is the primary candidate for such correction in our data. Beyond this study's scope (see §1.3.6 decision); acknowledged in Limitations and deferred to Future Work.
  - > **Note for Future Work section:** Re-run Poisson/M/M/c/c tests on arrivals reconstructed via Mellou & Jaillet's AVG+TREND estimator. The 75× Erlang B blocking-probability gap (predicted 0.07% vs observed 5.32%) at Kendall T is a natural candidate: does censoring correction close the gap, or does it confirm the gap is driven by service-process non-stationarity?
- [x] **4.2.2** Write main report (max 5 pages excluding references)
  - First prose draft complete; trimmed to 5 pages exactly on 2026-04-22
  - Source: `project-docs/report/report.tex` + `main.tex`; compiled `report.pdf` at **15 pages total** (main 5 + references 1 + appendix 9) after §3.2b revision and figure insertion
  - LaTeX setup: `\documentclass[11pt]{article}`, 1-inch margins, 1.15 line spacing, natbib numeric citations, IEEEtran bibliography, titlesec-tightened section spacing
- [x] **4.2.3** Prepare appendix with supplementary figures, tables, simulation details (max 10 pages)
  - Source: `project-docs/report/appendix.tex`
  - A. Methodology details (fullness algorithm with exclusion counts, Little's Law μ estimate, SimPy resource model, arrival generators)
  - B. Four data tables with real numbers: B.1 goodness-of-fit (KS/AD/χ²/AIC for 4 distributions × 4 systems), B.2 CV by hour-of-day, B.3 CV by day-of-week + IoD peak/off-peak, B.4 queueing outcomes with 95% CI and blocking
  - C. Seven supplementary figures (existing PNGs copied into `report/figures/`)
  - D. Derivations (M/M/c Wq via Erlang C, Erlang B recursion, Little's Law μ for Bluebikes)
- [ ] **4.2.2a** Resolve open review points from first-draft checkpoint (2026-04-22)
  - **A. Fact-checks (high priority)**
    - A1. Verify Appendix B.1 KS/AD/χ²/AIC values (transcribed from `visualize_phase2.py` output) — sample 1–2 cells
    - [x] A2. Superseded 2026-05-03: the §4.3 claim was softened from "isolating service-process non-stationarity" to "consistent with time-varying $\mu(t)$ (...) and time-varying $\lambda(t)$ that the i.i.d. bootstrap does not test", and §6 Limitations now flags the attribution to service as suggestive (D18). The dock-occupancy-direction parenthetical is retained but the claim no longer rests on it.
    - [x] A3. Verify A.2 service-time estimates are plausible for dock occupancy. Revised values (post-§3.2b): Kendall/MIT 7,367 s ≈ 2.05 h, MIT Vassar 6,670 s ≈ 1.85 h.
  - **B. Argument**
    - [x] B1. §5.4 "Error direction is predictable from structure" — superseded 2026-05-03: paragraph merged into the §5 "Off the decision path: MBTA wait" closing sentence as a single observation, removing the standalone-claim concern and freeing 1 line of page budget.
    - B2. §6 Mellou–Jaillet paragraph — one-sentence citation only; too compressed, or appropriately scoped?
  - **C. Structure / readability**
    - C1. `\paragraph` layout in §3 Methods, §5 Discussion, §6 Limitations — readable enough, or revert to subsections?
    - C2. §4.1 → §4.2 → §4.3 flow — does the key finding land?
    - C3. Appendix C figure placement — default [h], may scatter; consider grouping on single pages
  - **D. Outstanding content**
    - [x] D1. Main-text Fig 1 and Fig 2 placeholder frameboxes resolved (2026-04-24): inserted `phase3_wq_comparison.png` as Fig 1 in §4.2 (main); moved CDF content to Appendix C as `\label{fig:cdfs}` (per option B). Main body still 5 pages; total 15.
    - D2. References currently 8 entries — add O'Mahony 2015 and other supporting citations as needed in Task #7
    - [x] D3. Appendix A.1 algorithm description defects resolved (2026-04-24) via §3.2b: Mellou citation removed from A.1; "< 1 minute merge" sentence removed; initial condition $\lfloor C_s/2 \rfloor$ stated honestly; state-transition full flag with retract-on-intervening-trip-end semantics implemented and documented.
    - [x] D4. `visualize_phase3.py` had pre-revision hardcoded values causing Figure 1 vs Table 2 inconsistency (caught 2026-04-24). Fixed by updating the three plot functions with post-§3.2b numbers; Fig 1 and Table 2 now consistent. Commit 588e1c9.
    - [x] D5. Bluebikes $W_q$ clarification (caught 2026-04-24): readers could misread the 9.4 s empirical-DES $W_q$ as a physically observed wait, but real Bluebikes rejects rather than queues. Added infinite-queue idealisation notes to §3 Methods, §4.2 narrative, main Table 2 caption, and Appendix Table B.4 caption. Commit 82eef07.
### 4.2c Editorial revisions: framing and metric-split emphasis (2026-05-01 → 2026-05-03)

> **Background:** A series of substantive editorial passes after the §3.2b revision sharpened the framing of the report's findings without changing any underlying analysis. Each pass was driven by a specific user critique of the prose. Numerical results, figures, and tables are unchanged from §3.2b.

**Modification steps:**

- [x] **4.2c.1** §4.2 narrative — added MBTA Northbound vs Southbound dwell-time asymmetry note (mean 82 s vs 61 s, morning-peak boarding asymmetry on the inbound platform). Clarifies that the $W_q$ direction spread (20.1 vs 10.7 s analytical) traces to dwell, not arrivals. Commit `94cbd64` (2026-05-01).
- [x] **4.2c.2** Reframed MBTA over-prediction from "wasteful infrastructure / over-provisioning risk" to "off the decision path" (D16). Real transit infrastructure is not sized from per-train $W_q$, so the 5–12$\times$ over-prediction is harmless rather than dangerous. Edits to Abstract, §1 Contributions, §5 Discussion ("Operator-side risk" paragraph replaced with "Off the decision path: MBTA wait" + "Harmless regime" folded in), §8 Conclusion. Added decision path as a third axis to the §5 error-evaluation framework (was: direction + magnitude). Commit `83adf71` (2026-05-03).
- [x] **4.2c.3** Removed the §5 "Off the decision path" closing sentence "The same logic neutralises Bluebikes MIT Vassar St, where 53 docks push $W_q$ to zero" — that sentence conflated decision-path harmlessness (MBTA) with magnitude-axis harmlessness (Vassar) and ignored the Vassar blocking gap that §4.3 reports. Commit `b3d1c30` (2026-05-03).
- [x] **4.2c.4** Rewrote §6 Limitation 1 from "Arrival censoring at full Bluebikes docks" to "Latent demand suppression at Bluebikes" (D17). The old framing claimed $\lambda$ was a lower bound because of zero arrivals during full periods, but those periods are already excluded by the §3.2b pipeline. The residual is divert/abandon by users who anticipate fullness — exactly what Mellou–Jaillet's lost-demand estimator targets. Title and body rewritten; Mellou citation now correctly positioned. Commit `4abf79f` (2026-05-03).
- [x] **4.2c.5** Softened "isolating service-process non-stationarity" to "consistent with non-stationarity in $\lambda(t)$ and/or $\mu(t)$" everywhere it appeared (Abstract, §1 Contributions, §4.3 subsection title and body, §6 Limitations, §7 Future Work, §8 Conclusion) — the §4.3 attribution was tested only with a stationary i.i.d. bootstrap that destroys arrival-side temporal structure (peak-hour clusters), so service vs arrival cannot be distinguished from the current evidence (D18). Renamed §6 paragraph from "Service-process non-stationarity unmodelled" to "Non-stationarity unmodelled". Added a new §7 Future Work entry: pair NHPP $\lambda(t)$ with time-varying $\mu(t)$ for Bluebikes to test whether joint non-stationarity closes the 55$\times$ gap. Commit `4abf79f` (2026-05-03).
- [x] **4.2c.6** Surfaced the $W_q$ vs blocking metric split in three new locations (D19): Abstract gains a one-sentence summary ("Best-fit Weibull/log-normal IATs reproduce $W_q$ to within a second but close only about a seventh of the $55\times$ blocking gap"); §4.2 ends with a forward pointer to §4.3 ("This conclusion does not survive the move from $W_q$ to blocking..."); §5 Discussion opens with a metric-by-metric paragraph ($W_q$ = marginal IAT sufficient; blocking = i.i.d. ceiling that the marginal cannot lift) before the three-axes paragraph. Compensating compressions across §1 Intro, §5, §6, §7, §8 to keep main body at 5 pages. Plan recorded at `project-docs/plans/phase4_3_metric_split_emphasis_plan.md`. Commit `1b184f7` (2026-05-03).
- [x] **4.2c.7** Removed stale Phase 1 figure `bb_interarrival_hist.png` (pre-fullness-exclusion, never referenced from `appendix.tex`) and its generator `plot_bb_interarrival_hist` in `src/visualize_exploratory.py` to prevent stale-output regeneration. Commit `822939e` (2026-05-03).
- [x] **4.2c.8** Fixed reversed physics in §4.3 parenthetical (D20): old "dock occupancy swells at peak departures, collapses midday" had μ(t) backwards (high demand → high turnover → short occupancy → high μ, not low). Replaced with Kendall-specific asymmetric-flow framing: "at Kendall, morning commuter inflow piles incoming bikes against a low outflow rate, suppressing μ(t) exactly when λ(t) peaks". This parallels the §4.2 dwell-asymmetry note for MBTA and gives a physical mechanism for why blocking concentrates in morning hours at the transit hub. Commit `25672c7` (2026-05-03).
- [x] **4.2c.9** Merged §6 Limitations and §7 Future Work into a single "Limitations and future work" section (D21): three of the five limitation paragraphs (Latent demand suppression, DES destroys autocorrelation, Non-stationarity unmodelled) now have their corresponding future-work clause appended directly. Removed the standalone §7 section heading and "Three extensions" lead-in. Updated `appendix.tex:253` cross-reference `\S\ref{sec:future}` → `\S\ref{sec:limitations}`. The merge frees roughly 3 lines of page budget. Commit `2701b12` (2026-05-03).
- [x] **4.2c.10** Expanded §8 Conclusion (now §7 after the merge) from a single paragraph to two paragraphs (D22): para 1 makes the decision-path frame concrete with the binding/harmless asymmetry (Bluebikes 55× → service-failure miss; MBTA harmless → no decision lever); para 2 makes the metric split concrete (marginal IAT enough for $W_q$ via Weibull/log-normal; not enough for blocking — empirical i.i.d. closes only 1/7 of the gap, leaving λ(t)/μ(t) non-stationarity as the residual). Closes with the three-axis evaluation rule. Compensating compressions absorbed by the §6+§7 merge plus a few one-line trims; main body still 5 pages. Commit `2701b12` (2026-05-03).

**Cumulative effect on the report's framing:**

| Aspect | Before (≤ 2026-04-24) | After (2026-05-03) |
|---|---|---|
| MBTA over-prediction framing | "Operator-side over-provisioning risk; wasteful infrastructure" | "Off the decision path; harmless because per-train $W_q$ does not size transit" |
| Error-evaluation axes (§5) | 2 (direction + magnitude) | 3 (direction + magnitude + decision path) |
| §6 Limitation 1 title | "Arrival censoring at full Bluebikes docks" | "Latent demand suppression at Bluebikes" |
| Source of residual blocking gap | "Isolated to service-process non-stationarity" | "Consistent with $\lambda(t)$ and/or $\mu(t)$ non-stationarity; i.i.d. bootstrap cannot distinguish" |
| Wq vs blocking finding | Scattered across §4.2 / §4.3, not surfaced | Stated in Abstract + §4.2 preview + §5 Discussion preamble |
| §4.3 μ(t) physics | "swells at peak departures, collapses midday" (reversed) | "morning commuter inflow piles incoming bikes against a low outflow rate, suppressing μ(t) exactly when λ(t) peaks" |
| §6 / §7 structure | Two separate sections (Limitations, Future Work) | One merged section "Limitations and future work" with future-work clauses appended to matching limitations |
| §8 Conclusion | One terse paragraph | Two paragraphs: decision-path frame (binding vs harmless) + metric split (Wq sufficient with marginal, blocking is not) |
| Page budget | 15 (main 5 / refs 1 / appendix 9) | 15 (unchanged) |

### 4.2d Editorial revisions: Phase 4.4 post-presentation pass (2026-05-07)

Phase 4.4 is a focused post-presentation revision pass driven by three sources: Alex's review email (Little's Law derivation correctness, numerical consistency audit), final video/slide alignment (three-effect structure for §4.3), and Wu's Day-1 Q&A pattern analysis (intuition-first preference, i.i.d. resampling probe, "is it really?" attacks on universal claims). Plan recorded at `project-docs/plans/report_revision.md`. Eight substantive commits + one skip-log commit; main body remains 5 pages, total 15 pages.

- [x] **4.2d.1** Numerical consistency fixes (D24): (a) §A.2 Little's Law derivation rewritten to match §D.3 — old form had $\mu = \lambda \bar{W}_{\text{slot}}/(L_{\text{non-full}} \cdot c)$ which is dimensionally circular ($\bar{W}_{\text{slot}}$ was defined as $1/\mu$); new form derives $\bar{W}_{\text{slot}} = L_{\text{non-full}}/\lambda$ from per-slot Little's Law, giving $\mu = \lambda/L_{\text{non-full}}$ without circularity, numerical values (7367s, 6670s, $\rho=0.48, 0.33$) preserved; (b) added best-fit Weibull DES blocking value 0.46% to §4.3 prose — previously absent from main.tex and appendix.tex despite appearing as a 5th bar in `phase3_blocking_comparison.png`; (c) §4.1 IoD ranges aligned with Table 1 only ("IoD 2--8" → "IoD 3.2--4.7" for Bluebikes, "IoD 0.4--0.6" → "IoD 0.52--0.58" for MBTA) — old ranges silently mixed Table 1 (30-min) and Table 5 (60-min, peak/off-peak); (d) Figure 8 caption updated from 4-bar list to 5-bar list (added "DES (Weibull best-fit)") and prefixed "at Kendall/MIT" since the figure title shows Kendall only. Commit `ae6c25e`.

- [x] **4.2d.2** §3 Methods Diagnostic-intuition paragraph (D25, Phase 2.1): new `\paragraph{Diagnostic intuition.}` ahead of Arrival-process characterization — frames CV / IoD as complementary diagnostic tools and introduces the "aggregation artefact vs persistent within-window feature" test for segmentation results. Adopted a tightened 3-line version (not the Plan's 5-line version) by stripping the redundant "$\mathrm{CV} = \mathrm{IoD} = 1$ for Poisson" rephrase that was already in the next paragraph. Acts as the methodological forward-buttress for §4.1 segmentation results (4.2d.7). Commit `b0a22e5`.

- [x] **4.2d.3** §3 Methods 4-distribution rationale (D25, Phase 2.2): new sentence appended after the AIC-ranking sentence — "The four candidates span the relevant inter-arrival behaviors: exponential is the Poisson memoryless baseline; Weibull captures clustered or regular gaps through its shape parameter; log-normal arises naturally when arrivals are scheduled with multiplicative jitter; gamma is a flexible comparator that nests several of these regimes." Adopted option E (no hazard-rate jargon) over the Plan original's "hazard structure" framing — same coverage argument, accessible without survival-analysis background. Pre-empts "why these four distributions?" Q&A. Commit `9b3ad61`.

- [x] **4.2d.4** §3 Methods GoF-test rationale (D25, Phase 2.3): 3-line append to the existing testing-statistics sentence — "KS captures global CDF shape mismatch; AD weighs tail discrepancies, where rare events (including blocking) sit; $\chi^2$ provides a binned-frequency robustness check." Adopted option B (微修正版): "weighs" instead of "emphasizes" (statistically more accurate verb), "where rare events ... sit" instead of "where predictions of rare events live" (less literary). The AD-tail link methodologically buttresses §4.3's blocking-as-rare-event treatment. Commit `82e5d0c`.

- [x] **4.2d.5** §3 Methods i.i.d. bootstrap honesty (D25, Phase 2.4): 3-line insert into the Discrete-event simulation paragraph after the three-generator listing — "The empirical bootstrap preserves the marginal IAT distribution exactly but samples i.i.d., intentionally removing any sequential or time-of-day structure. We exploit this property in §4.3 to attribute residual blocking error to non-stationarity rather than to the marginal distribution." The active "we exploit this property" framing transforms the i.i.d. limitation from a perceived weakness into a deliberate analytical tool, and forward-links §3 to §4.3 so that the residual-attribution argument does not appear retroactive. Highest-priority Wu defence (Wu hit Xian's i.i.d. resampling 4× consecutively in Day 1, transcript 9:02 / 9:26 / 9:58 / 10:21). Commit `d08fd30`.

- [x] **4.2d.6** §4.3 three time-structure effects + page geometry tightening (D26 + D27, Phase 2.5 + density): (a) replaced the dense single-sentence residual explanation in §4.3 with three semicolon-separated effects matching slides 22-25 in **content** (not format) — time-varying $\lambda(t)$ (bike returns peak at commute hours, averaged out by single-$\lambda$ models); time-varying $\mu(t)$ (Kendall dock turnover slows during peak return demand when rentals drop, missed by fixed-$\mu$ assumption); temporal coupling ($\lambda$ peaks coincide with $\mu$ valleys at the same hour, compounding blocking multiplicatively); MBTA disclaimer at $\rho=0.15$--$0.20$ preserved. Adopted case C (prose with three named effects) over Plan original's enumerated (i)(ii)(iii) format — slide-report parity is on content, not format, since the report stands alone and slides are read in the live presentation. (b) Restructure tipped page count to 16 (main body spilled to p.6); recovered to 15 with a Phase A density tightening: margin 1in→0.85in and setstretch 1.15→1.10, recovering ~13% page density without 2-column layout risk. Visual check confirmed all main-body figures (Fig 1 3-panel) and tables (Tables 1, 2 in main; Tables 3, 4 with 14 columns, 5, 6 in appendix) intact under the new geometry. Commit `595cdff`.

- [x] **4.2d.7** §4.1 segmentation claim softened (D26, Phase 2.7): rewrote the Within-day segmentation sentence to absorb Wu's likely "is the Poisson rejection solely a non-stationarity artefact?" attack while preserving the existing structural elements (MBTA contrast, peak-hour punchline, Fig 7 reference). Adopted case B synthesis over Plan original (which would have dropped MBTA contrast / punchline / Fig 7 ref). New sentence: "Within-day segmentation (Appendix B.2, Table 4; empirical CDFs with fits in Appendix C, Fig. 7) shows that the Bluebikes CV reflects both non-stationarity and within-window non-Poissonness: Kendall/MIT falls to CV ≈ 1.0 at midnight and peaks at 2.4 at 18:00 but stays ≥ 1.0 at every hour, while MBTA stays below 1 throughout. The rejection of Poisson is not solely an aggregation artefact—a single-window Poisson hypothesis fails at every hour, more strongly at peak." Numerical precision upgrade "peaks at 2.4 at 18:00" replaces the round "peaks near 2.0". Connects upward to §3 Diagnostic intuition (4.2d.2) which framed segmentation as the test for "aggregation vs persistent within-window feature" — §4.1 now reports the result of that test. Commit `3ed445d`.

- [x] **4.2d.8** "Harmless" softened to "low-risk in this context" (D26, Phase 2.6): two coordinated changes to make the MBTA-wait framing context-bound instead of universal. §5 Off-the-decision-path: "harmless rather than wasteful" → "low-risk in this context---no planning decision uses per-train $W_q$ as an input." User flagged the Plan-original "decision path that depends on per-train accuracy" phrasing as too abstract (double abstraction); adopted "no planning decision uses per-train $W_q$ as an input" as the cleaner meta-claim. Also dropped "rather than wasteful" — leftover rhetorical contrast that introduced "wasteful" without prior context. §7 Conclusion: "harmless because per-train $W_q$ does not feed transit planning" → "low-risk in this context because per-train $W_q$ does not feed transit planning" (word swap only — preserves Conclusion terseness, lets §5 carry the substantive elaboration). Asymmetric depth (§5 substantive / §7 terse) preserves the Phase 4.3 D22 split. Commit `7551e0e`.

- [x] **4.2d.9** Documented skip decisions: Plan §2.8 (priority summary paragraph at end of §6 future work) skipped after user observed that **Wu does not open the report mid-Q&A** — the priority answer just needs to be in the team's heads, not in writing. Also conflicted structurally with Phase 4.3 D21's deliberate distribution of future-work clauses into limitation paragraphs (a closing "three extensions" summary would have partially undone D21). Plan §3.1 ("engineering approximation" framing for §1 first sentence) skipped because §1 already conveys the approximation message twice ("the assumption is approximate" in sentence 4, "they almost never are" in sentence 5). Q&A priority for the team's prep (not in report): (1st) NHPP × time-varying $\mu(t)$ — directly tests §4.3 residual attribution; (2nd) autocorrelation-preserving generator — tests timetable-structure on MBTA $W_q$; (3rd) Mellou--Jaillet reconstruction — censoring vs real non-Poissonness separation. Commit `7d08542` (skip-log only).

**Cumulative effect on the report (Phase 4.4 increments):**

| Aspect | Before Phase 4.4 (≤ 2026-05-03) | After Phase 4.4 (2026-05-07) |
|---|---|---|
| §A.2 Little's Law derivation | Circular: $\mu$ defined via $\bar{W}_{\text{slot}}$ which itself defined as $1/\mu$ | Non-circular: $\bar{W}_{\text{slot}} = L_{\text{non-full}}/\lambda$ from per-slot Little's Law, then $\mu = \lambda/L_{\text{non-full}}$ (matches §D.3) |
| §4.3 distributions reported | Erlang B + empirical DES + observed (3 values) | + best-fit Weibull DES = 0.46% (4 distinct values, marginal-IAT-insufficient claim quantified) |
| Figure 8 caption | "Erlang B vs DES (Poisson) vs DES (empirical) vs observed" (4-bar list, mismatched the 5-bar figure) | "Erlang B vs DES (Poisson) vs DES (empirical) vs DES (Weibull best-fit) vs observed" (matches actual figure) |
| §4.1 IoD ranges | "IoD 2--8" / "IoD 0.4--0.6" — silently mixed Table 1 (30-min) and Table 5 (60-min, peak/off-peak) | "IoD 3.2--4.7" / "IoD 0.52--0.58" — aligned with Table 1 only |
| §3 Methods Wu Q&A defence | None explicit | 4 vectors: Diagnostic intuition (CV/IoD framing) + 4-distribution rationale + GoF-test rationale + i.i.d. bootstrap honesty |
| §4.1 segmentation claim | "attributes the Bluebikes CV to non-stationarity" (strong, Wu-attackable) | "reflects both non-stationarity and within-window non-Poissonness ... not solely an aggregation artefact" (context-bound, defensible) |
| §4.3 residual structure | Dense single-sentence prose explaining $\mu(t)$, $\lambda(t)$, and their coupling | Three-effect prose matching slide content: time-varying $\lambda(t)$; time-varying $\mu(t)$; temporal coupling (multiplicative compounding) |
| §5 "harmless" framing | "the over-prediction is harmless rather than wasteful" (universal, Wu-attackable) | "low-risk in this context---no planning decision uses per-train $W_q$ as an input" (context-bound) |
| §7 Conclusion "harmless" | "harmless because per-train $W_q$ does not feed transit planning" | "low-risk in this context because per-train $W_q$ does not feed transit planning" (word swap, terseness preserved) |
| Page geometry | margin 1in, setstretch 1.15 | margin 0.85in, setstretch 1.10 (enabler for Phase 4.4 net additions) |
| Page budget | 15 (main 5 / refs 1 / appendix 9) | 15 (main 5 / refs 1 / appendix 9) — unchanged |

- [ ] **4.2.4** Add references
  - > **Checkpoint:** Review draft report with user before finalization.
- [ ] **4.2.5** Finalize report for submission by 5/8 11:59pm ET
- [ ] **4.2.6** *(Alex)* Review and edit report for clarity and consistency
- [ ] **4.2.7** *(Alex)* Read all code and add comments explaining logic and flow

### 4.3 Reproducibility (per Recitation 8 guidelines)

- [ ] **4.3.1** Initialize Git repository and push to GitHub
- [ ] **4.3.2** Create `environment.yml` (or `requirements.txt`) with all dependencies and pinned versions
- [ ] **4.3.3** Fix random seeds in all simulation code for reproducible results
- [ ] **4.3.4** Write `README.md` with:
  - Project title and description
  - Installation and environment setup instructions
  - How to reproduce all figures and results
  - Data sources and download instructions
- [ ] **4.3.5** Organize repository structure (separate directories for data, code, outputs, docs)
- [ ] **4.3.6** Add MIT license
- [ ] **4.3.7** Verify reproducibility: clone repo from scratch and confirm all results can be regenerated

### 4.4 Presentation

- [ ] **4.4.1** Prepare presentation slides (15 min + Q&A)
- [ ] **4.4.2** Rehearse and refine
- [ ] **4.4.3** Submit slides to teaching staff before presentation session (5/6 or 5/8)
- [x] **4.4.4** SimPy DES animation for slides — **implemented 2026-05-03** (D23)
  - Goal: visually demonstrate the $W_q$ vs blocking metric split (D19) — show how the real Kendall/MIT inventory $N(t)$ reaches 23 (saturates) repeatedly during morning Commuter inflow + Saturation periods, while a Poisson DES with the same daily arrival rate never even reaches full state
  - Implementation: `src/animation_des.py` (~280 lines, standalone). Heap-based finite-capacity simulation for the LEFT (Poisson) panel; direct replay of the §3.2b inventory reconstruction for the RIGHT (real data) panel — no service-time simulation on the right. Blocking events on the right are §3.2b committed full-interval starts, not simulator outputs
  - Representative day: 2025-09-17 (Wed) — 31 committed full intervals, 291.9 min total full-time, 08:27–15:21 saturation arc; 12-hour window 06:00–18:00 compressed to 36 sec (1080 frames at 30 fps)
  - Visual: 23 horizontal dock cells per panel; burned-in title "Poisson DES (left, simulated) vs real Kendall/MIT inventory $N(t)$ (right, observed)"; time + period label ("Early morning / Commuter inflow / Saturation / Afternoon drain / Evening") at top; per-panel sub-labels at bottom explicitly stating data provenance; right-panel red flash + giant white-on-red "BLOCKED" overlay (with black stroke) at each committed full-interval start
  - Outputs: `outputs/animations/des_blocking_comparison.mp4` (1920×1080, 30 fps, 36 sec, 3.0 MB), `outputs/animations/frame_to_event_log.csv` (1080 rows for narration script reference), `outputs/animations/preview_*.png` (sample frames at 06:00 / 08:30 / 10:00 / 14:00 / 17:30)
  - Tooling: `imageio-ffmpeg` (Python-only, no system ffmpeg required); installed via `python3 -m pip install imageio-ffmpeg`
  - Iteration history: first version (commit `3c9e539`) used Empirical DES on the right (real arrivals + Exp(1/μ̄) service); switched to direct real-data replay (commit `3409c7a`) after Taka noted the simulator-output framing risked confusing observers about data provenance
  - Result: Poisson DES 0 blocks, real Kendall data 31 committed full intervals (291.9 min observed full-time = 41% of 12 operating hours). Visual mapping to §4.3 main claim is direct: same arrival rate, opposite outcome — model vs reality, not model vs model

---

## Summary of Decisions

| # | Decision | Status | Resolution |
|---|----------|--------|------------|
| D1 | Bluebikes data time period | **Resolved** | Sep–Dec 2025 |
| D2 | MBTA line selection | **Resolved** | Red Line |
| D3 | Bluebikes station selection | **Resolved** | 2 stations: Kendall/MIT area + MIT Vassar St (Westgate) |
| D4 | Outlier / operating hours handling | **Resolved** | Operating hours only; flag and exclude disruptions |
| D5 | Service time definition for M/M/1 | **Resolved** | Bluebikes: dock occupancy time (arrival → next departure of that dock slot). MBTA: dwell time (station stop duration) |
| D6 | Time window granularity | **Resolved** | Inter-arrival time analysis (continuous, no window) as primary; arrival count analysis at 15/30/60-min windows as supplementary |
| D7 | Simulation framework | **Resolved** | SimPy (Python) |
| D8 | Presentation format | **Resolved** | Slide presentation (15 min + Q&A) |
| D9 | MBTA Red Line station | **Resolved** | Kendall/MIT |
| D10 | Bluebikes queueing model | **Resolved** | M/M/c (infinite queue, theoretical) + M/M/c/c (Erlang B, loss/rejection model). M/M/1 unstable for BB |
| D11 | Bluebikes fullness data handling | **Resolved** | Exclude from λ/μ estimation and distribution fitting; use observed fullness rate to validate Erlang B blocking probability |
| D12 | Dock fullness correction method (BB) | **Resolved** | Mellou & Jaillet (2019) identified as canonical method. Not implemented (scope/timeline/confounding); documented in Limitations and Future Work |
| D13 | Fullness-flag definition (BB) | **Resolved** | State-transition based: full flag set only on natural $C-1 \to C$ trip-end increment; candidate interval retracted if any trip-end intervenes before next trip-start. Chosen over per-clamp flagging (over-counts) and non-retracting state (ignores physical evidence of non-fullness). Motivates §3.2b revision. |
| D14 | Main-text figure selection | **Resolved** | Option B: Fig 1 = `phase3_wq_comparison.png` in §4.2 (kept in main); Fig 1 (old — CDFs) moved to Appendix C as `fig:cdfs`. Keeps main body at 5 pages while preserving the core queueing-error visual. |
| D15 | Bluebikes $W_q$ reporting caveat | **Resolved** | $W_q$ values for Bluebikes are under an infinite-queue idealisation and do not correspond to a physically observed wait (real system rejects). Reported for common-abstraction comparison with MBTA; observable metric for BB is blocking (§4.3). Note added to §3 Methods, §4.2 narrative, Table 2 caption, and Appendix Table B.4 caption (option C). |
| D16 | MBTA over-prediction framing | **Resolved (2026-05-03)** | Reframed from "operator-side risk / wasteful infrastructure" to "off the decision path". Real transit infrastructure is not sized from per-train $W_q$ (platform length is inherited capital, frequency is set by demand and operations, crowding is the customer metric), so the 5–12$\times$ MBTA over-prediction is harmless rather than dangerous. Decision path added as a third axis to the §5 error-evaluation framework alongside direction and magnitude. |
| D17 | §6 Limitation 1: censoring vs latent demand | **Resolved (2026-05-03)** | Old "Arrival censoring at full Bluebikes docks" double-counted what the §3.2b exclusion pipeline already handles. Rewrote as "Latent demand suppression at Bluebikes" focused on the residual divert/abandon behaviour by users who anticipate a full station — exactly what Mellou–Jaillet's lost-demand estimator targets. The "$\lambda$ is a lower bound" framing is dropped in favour of "$\lambda$ is unbiased for realised trips; the residual is latent demand". |
| D18 | Source of residual blocking gap | **Resolved (2026-05-03)** | Softened "isolating service-process non-stationarity" to "consistent with non-stationarity in $\lambda(t)$ and/or $\mu(t)$". The §4.3 attribution was tested only with a stationary i.i.d. bootstrap that destroys arrival-side temporal structure, so service vs arrival cannot be distinguished from the current evidence. §6 paragraph renamed "Non-stationarity unmodelled". §7 Future Work gains an NHPP $\lambda(t)$ × time-varying $\mu(t)$ Bluebikes test as the canonical experiment to settle the attribution. |
| D19 | Surfacing the $W_q$ vs blocking metric split | **Resolved (2026-05-03)** | The paper's core finding — marginal IAT is sufficient for $W_q$ but hits an i.i.d. ceiling for blocking (closes only ~1/7 of the 55$\times$ gap) — was scattered across §4.2 / §4.3 and not visible on a first read. Promoted to three locations: a one-sentence summary in the Abstract, a forward pointer at the end of §4.2 ("This conclusion does not survive the move from $W_q$ to blocking…"), and a metric-by-metric paragraph at the top of §5 Discussion before the three-axes paragraph. Plan recorded at `project-docs/plans/phase4_3_metric_split_emphasis_plan.md`. |
| D20 | §4.3 μ(t) physics correction | **Resolved (2026-05-03)** | Original parenthetical "dock occupancy swells at peak departures, collapses midday" had the physics reversed — high demand causes high turnover (short occupancy, high μ), not the reverse. Replaced with a Kendall-specific asymmetric-flow framing: "morning commuter inflow piles incoming bikes against a low outflow rate, suppressing μ(t) exactly when λ(t) peaks". Parallels the §4.2 dwell-asymmetry note for MBTA. |
| D21 | §6 / §7 merge structure | **Resolved (2026-05-03)** | §6 Limitations and §7 Future Work merged into a single "Limitations and future work" section. Each of the three matched future-work items now appended directly to its corresponding limitation paragraph (Mellou–Jaillet → Latent demand; autocorrelation-preserving → DES destroys autocorrelation; NHPP × time-varying μ → Non-stationarity unmodelled). Frees ~3 lines of page budget for §8 Conclusion expansion. |
| D22 | §8 Conclusion expansion | **Resolved (2026-05-03)** | Expanded from a single terse paragraph to two paragraphs: para 1 makes the decision-path frame concrete with the binding/harmless asymmetry; para 2 makes the metric split concrete (marginal sufficient for $W_q$, not for blocking, λ(t)/μ(t) non-stationarity is the residual). Closes with the three-axis evaluation rule. Compensated by the §6+§7 merge and one-line trims; main body still 5 pages. |
| D23 | §4.4.4 animation framing: model vs reality | **Resolved (2026-05-03)** | First implementation used Empirical DES (real arrivals + simulated service) on the right panel — the 7 "BLOCKED" events were simulator outputs, not observations. Risked confusing presentation observers about data provenance. Switched right panel to direct §3.2b inventory replay (real trip-end +1 / trip-start −1 events, no service simulation). BLOCKED events now correspond to §3.2b committed full-interval starts (31 events on 2025-09-17, 291.9 min observed full-time). Sub-labels explicitly state "Left: Poisson(λ̄) arrivals + Exp(1/μ̄) service" and "Right: real Kendall data 2025-09-17 — observed inventory N(t)". Comparison is now model-vs-reality, mapping directly to the §4.3 main claim. |
| D24 | Phase 4.4 numerical consistency | **Resolved (2026-05-07)** | Four-part consistency audit and fix following Alex's review email: (a) §A.2 Little's Law derivation rewritten to match §D.3, removing the circular $\mu$-via-$\bar{W}_{\text{slot}}$ definition (numerical values 7367s, 6670s, $\rho=0.48, 0.33$ preserved); (b) best-fit Weibull DES blocking value 0.46% added to §4.3 prose (previously only in `phase3_blocking_comparison.png`); (c) §4.1 IoD ranges aligned with Table 1 only ("3.2--4.7", "0.52--0.58" replacing the Table-1+Table-5-mixed "2--8", "0.4--0.6"); (d) Figure 8 caption updated to mention all 5 bars (Erlang B / DES Poisson / DES empirical / DES Weibull best-fit / observed) and prefixed "at Kendall/MIT" since the figure title shows Kendall only. |
| D25 | §3 Methods Wu Q&A defence quartet | **Resolved (2026-05-07)** | Four added vectors in §3 Methods to pre-empt Wu's most frequent attacks: (1) Diagnostic intuition paragraph framing CV/IoD as complementary tools and introducing "aggregation artefact vs persistent within-window feature" as the segmentation test; (2) 4-distribution rationale ("the four candidates span the relevant inter-arrival behaviors") to deflect "why these four?" attacks without hazard-rate jargon; (3) GoF-test rationale (KS global / AD tail / $\chi^2$ binned) to deflect "why three tests?" attacks and methodologically link AD-tail to §4.3 blocking-as-rare-event; (4) i.i.d. bootstrap honesty ("intentionally removing time-of-day structure ... we exploit this property in §4.3 to attribute residual blocking error to non-stationarity") to deflect Wu's most frequent Day-1 attack vector by transforming the limitation into a deliberate analytical tool. |
| D26 | §4 / §5 / §7 framing tightening | **Resolved (2026-05-07)** | Three coordinated framing changes: (a) §4.1 segmentation softened from "attributes Bluebikes CV to non-stationarity" to "reflects both non-stationarity and within-window non-Poissonness ... not solely an aggregation artefact" — preserves MBTA contrast and peak-hour punchline, picks up "2.4 at 18:00" Table 4 precision over "near 2.0"; (b) §4.3 residual structure replaced the dense single-sentence explanation with three semicolon-separated effects matching slide content (time-varying $\lambda(t)$; time-varying $\mu(t)$; temporal coupling — multiplicative compounding); (c) §5 / §7 "harmless" replaced with "low-risk in this context" to retire the universal claim Wu would attack as "is it really harmless in all contexts?" — §5 carries the substantive elaboration ("no planning decision uses per-train $W_q$ as an input"), §7 keeps the word swap terse to preserve Conclusion structure. |
| D27 | Page geometry tightening | **Resolved (2026-05-07)** | Phase 4.4 net additions (~17 lines across §3 / §4 / §A) tipped main body to p.6 after the Phase 2.5 §4.3 restructure. Switched from margin 1in / setstretch 1.15 to margin 0.85in / setstretch 1.10, recovering ~13% page density without 2-column layout risk. Returned main body to 5 pages with comfortable buffer; total still 15 pages. Project file constraints (`research_plan.md`, `report.tex`) confirmed no explicit single-column requirement; MIT 1.200 syllabus assumed unaffected. All main-body and appendix figures/tables (Fig 1 3-panel, Tables 1-2 main, Tables 3, 4 with 14 columns, 5, 6 in appendix) verified intact under new geometry. |
