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

### 1.4 Exploratory Data Visualization

- [ ] **1.4.1** Visualize Bluebikes arrival patterns (time-of-day, day-of-week, monthly)
- [ ] **1.4.2** Visualize MBTA arrival patterns and headways
- [ ] **1.4.3** Visualize inter-arrival time distributions (histograms) for both systems
- [ ] **1.4.4** Visualize estimated dock fullness periods for Bluebikes stations
  - > **Checkpoint:** Review visualizations with user before proceeding to Phase 2. Additional questions may arise.

---

## Phase 2: Descriptive Arrival-Process Analysis (Week 2: Apr 15–21)

### 2.1 Summary Statistics

- [ ] **2.1.1** Compute mean, standard deviation, coefficient of variation (CV), and skewness of inter-arrival times for Bluebikes
- [ ] **2.1.2** Compute the same statistics for MBTA
- [ ] **2.1.3** Compare CV to 1.0 (CV = 1 is the theoretical value for exponential inter-arrival times under a Poisson process)

### 2.2 Distribution Fitting and Comparison

- [ ] **2.2.1** Plot empirical inter-arrival time distributions (histograms, CDFs) for both systems
- [ ] **2.2.2** Fit exponential distribution to observed inter-arrival times
- [ ] **2.2.3** Fit candidate non-Poisson distributions (e.g., log-normal, Weibull, gamma) and select best-fit
- [ ] **2.2.4** Perform goodness-of-fit tests (Kolmogorov-Smirnov, Anderson-Darling, chi-squared) to formally test the exponential (Poisson) hypothesis

### 2.3 Arrival Count Analysis

- [ ] **2.3.1** Count arrivals in multiple time windows (15-min, 30-min, 1-hour) to examine scale dependence
- [ ] **2.3.2** Compare mean vs. variance of arrival counts per window (equal mean and variance is a hallmark of a Poisson distribution)
- [ ] **2.3.3** Compute the Index of Dispersion (variance/mean ratio) across time windows
- [ ] **2.3.4** Segment analysis by time-of-day and day-of-week to check for non-stationarity

### 2.4 Interim Findings

- [ ] **2.4.1** Summarize whether each system's arrivals appear Poisson, and characterize deviations
- [ ] **2.4.2** Identify the best-fit alternative distribution for each system
  - > **Checkpoint:** Review interim findings with user before proceeding to queueing analysis.

---

## Phase 3: Queueing Analysis and Simulation (Week 3: Apr 22–28)

### 3.0 Select Queueing Baseline

- [ ] **3.0.1** Confirm M/M/1 as the primary Poisson-based queueing model
- [ ] **3.0.2** Define service time assumptions for each system
  - Bluebikes: dwell time direction (TBD — to be finalized based on Phase 1–2 findings)
  - MBTA: to be defined
  - > **Decision needed (deferred):** Service time definitions will be finalized after descriptive analysis. Will revisit before simulation.
- [ ] **3.0.3** Document model assumptions and parameters

### 3.1 M/M/1 Analytical Baseline

- [ ] **3.1.1** Compute M/M/1 theoretical predictions using observed mean arrival rate (λ) and assumed service rate (μ):
  - Average delay (Wq)
  - Average queue length (Lq)
  - Average system time (W)
- [ ] **3.1.2** Compute predictions for both Bluebikes and MBTA

### 3.2 Discrete-Event Simulation (SimPy)

- [ ] **3.2.1** Build a discrete-event simulation using SimPy with the empirical inter-arrival distribution
- [ ] **3.2.2** Build a DES variant using the best-fit non-Poisson distribution from Phase 2
- [ ] **3.2.3** Run simulations for both Bluebikes and MBTA
- [ ] **3.2.4** Collect simulation outputs: average delay, average queue length, average system time
- [ ] **3.2.5** Validate simulation (warm-up period, sufficient run length, multiple replications for confidence intervals)

### 3.3 Error Quantification

- [ ] **3.3.1** Compare M/M/1 predictions vs. empirical-DES outcomes for each metric
- [ ] **3.3.2** Compare M/M/1 predictions vs. best-fit-DES outcomes for each metric
- [ ] **3.3.3** Quantify relative and absolute error for each metric and each system
- [ ] **3.3.4** Visualize the comparison (tables and/or plots)

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
| D5 | Service time definition for M/M/1 | **Deferred** | Bluebikes: dwell time direction. Finalize after data exploration |
| D6 | Time window granularity | **Resolved** | Inter-arrival time analysis (continuous, no window) as primary; arrival count analysis at 15/30/60-min windows as supplementary |
| D7 | Simulation framework | **Resolved** | SimPy (Python) |
| D8 | Presentation format | **Resolved** | Slide presentation (15 min + Q&A) |
| D9 | MBTA Red Line station | **Resolved** | Kendall/MIT |
