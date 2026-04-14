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
- [ ] **1.3.6** *(Alex)* Literature review on dock fullness adjustment methods for bike-share systems
  - If methods exist and are feasible within the project timeframe: implement
  - Otherwise: document as a limitation and include in Future Work section of the report

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

- [ ] **4.1.1** Compare Poisson-fit quality: Bluebikes (user-driven) vs. MBTA (schedule-driven)
- [ ] **4.1.2** Compare M/M/1 error magnitude across the two systems
- [ ] **4.1.3** Identify conditions under which Poisson is a reasonable engineering approximation
- [ ] **4.1.4** Identify conditions where Poisson breaks down and more general approaches are needed

### 4.2 Final Report

- [ ] **4.2.1** Draft report structure (problem statement, formulation, hypotheses, methods, results, conclusions)
  - > **Note for Limitations section:** Bluebikes arrival data is censored when docks are full — observed arrivals underestimate true demand. Methods for estimating unconstrained (latent) demand exist in the literature (e.g., censored regression, EM-based approaches) but are beyond this study's scope. The report should acknowledge this limitation and cite relevant work on latent demand estimation for bike-share systems.
- [ ] **4.2.2** Write main report (max 5 pages excluding references)
- [ ] **4.2.3** Prepare appendix with supplementary figures, tables, simulation details (max 10 pages)
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
