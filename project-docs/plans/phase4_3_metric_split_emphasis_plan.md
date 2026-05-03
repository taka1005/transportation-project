# Phase 4.3: Metric-Split Emphasis (Wq vs blocking) Plan

**Date:** 2026-05-03
**Target deadline:** 2026-05-08 23:59 ET (5 days remaining)
**Status:** Pending user approval

---

## 1. Problem

The paper's core finding — *that the marginal IAT distribution is sufficient for $W_q$ but not for blocking* — is currently dispersed across §4.2 and §4.3 and is not visible on a first read. A reviewer scanning §4.2 sees "best-fit-DES tracks empirical-DES" and concludes "Weibull/log-normal works"; only after reading §4.3 do they realise the same fit closes only ~1/7 of the blocking gap. The Discussion (§5) then jumps straight into the decision-path frame without naming the metric-by-metric split.

## 2. Three edits

### (A) §4.2 preview — line 96

**Goal:** Add a forward reference at the end of the §4.2 paragraph that warns the reader the $W_q$ conclusion does not survive the move to blocking.

**Current end of paragraph:**
> ...so a Weibull or log-normal fit retains enough of the arrival-process information to reproduce the queueing outcome. MIT Vassar~St is a $W_q$ null case under every model (53 docks drive the queueing wait to zero), yet \S\ref{sec:results-erlangb} shows it is \emph{not} a blocking null case once the observed fullness rate is reconstructed properly.

**Proposed:**
> ...so a Weibull or log-normal fit retains enough of the arrival-process information to reproduce the queueing outcome. **The conclusion does not survive the move from $W_q$ to blocking: \S\ref{sec:results-erlangb} shows that the same marginal-best-fit closes only about a seventh of the $55\times$ Erlang~B gap, exposing non-stationarity rather than arrival-process shape as the dominant residual.** MIT Vassar~St is a $W_q$ null case under every model (53 docks drive the queueing wait to zero), yet \S\ref{sec:results-erlangb} shows it is \emph{not} a blocking null case once the observed fullness rate is reconstructed properly.

**Net add:** ~2 lines.

---

### (B) §5 Discussion preamble — insert before line 105

**Goal:** Frame the entire Discussion around the metric-by-metric split so the decision-path axes that follow have a clear empirical anchor.

**Current §5 opening:**
> Poisson's error has three orthogonal axes: \emph{direction} (over- vs.\ under-estimation), \emph{magnitude relative to the decision threshold}, and \emph{whether the prediction is on the decision path at all}. The two systems we study fall into qualitatively different regimes.

**Proposed (new paragraph BEFORE the axes paragraph):**
> Two metric-level findings frame this discussion. For $W_q$, the marginal IAT distribution is sufficient: best-fit Weibull or log-normal samples generate empirical-DES values that match within a second across all four arrival processes, so a stationary fit reproduces the wait. For blocking the same marginal-best-fit closes only about a seventh of the $55\times$ Erlang~B gap at Kendall/MIT, hitting an i.i.d.\ ceiling that the marginal cannot lift. Whether Poisson is "good enough" therefore depends as much on the metric as on the system.
>
> Poisson's error has three orthogonal axes: \emph{direction} (over- vs.\ under-estimation), \emph{magnitude relative to the decision threshold}, and \emph{whether the prediction is on the decision path at all}. The two systems we study fall into qualitatively different regimes.

**Net add:** ~5 lines (one full paragraph).

---

### (C) Abstract — line 5

**Goal:** Surface the metric split in the abstract so readers know the headline finding before any section.

**Current sentence (mid-abstract):**
> Analytical Poisson queueing underestimates Bluebikes wait by roughly an order of magnitude and Erlang~B blocking at Kendall/MIT by 55-fold, while overestimating MBTA wait by 5--12$\times$. The 55$\times$ blocking gap persists even when the simulation uses empirical arrivals, suggesting service-process non-stationarity (and untested arrival non-stationarity) as a separate error source that stationary arrival-process correction alone cannot address.

**Proposed:**
> Analytical Poisson queueing underestimates Bluebikes wait by roughly an order of magnitude and Erlang~B blocking at Kendall/MIT by 55-fold, while overestimating MBTA wait by 5--12$\times$. **Best-fit Weibull/log-normal IATs reproduce $W_q$ to within a second but close only about a seventh of the $55\times$ blocking gap**: the marginal IAT distribution is sufficient for wait but not for blocking, and the residual is consistent with non-stationarity in $\lambda(t)$ and/or $\mu(t)$ that stationary arrival-process correction alone cannot address.

**Net add:** ~1.5 lines (compensated partly by absorbing the existing "55× gap persists" sentence into the new framing).

---

## 3. Page budget

Net additions across all three edits: ~7–8 lines. Main body must stay ≤ 5 pages. The most likely overflow vector is page 1 (Abstract) and page 5 (§5 Discussion).

**Compensating compressions, in order of preference:**

1. **§5 "User-side, on the decision path: Bluebikes blocking"** now duplicates the new preamble. Trim opening sentence "Poisson under-estimates Kendall/MIT blocking by 55-fold" (covered in preamble) and the "Bursty arrivals (CV 1.75–1.90)..." sentence — both can go to free 2 lines.
2. **§5 "Error direction is predictable from structure"** — short paragraph, can be merged into a single sentence appended to "Off the decision path" to save 2 lines.
3. **§1 Intro middle paragraph** (line 11) is now long after the May-1 MBTA reframing; can drop the "back-of-envelope wait estimates for studies of transit user experience and transfer planning" parenthetical to save 1 line.
4. **§6 "Latent demand suppression at Bluebikes"** still has slack — "would-be users who divert or abandon when expecting a full station and never appear in the dataset" → "users who divert when expecting a full station" saves 1 line.

Apply compressions only as needed, in this order, until Conclusion fits cleanly on page 5.

## 4. Files modified

- `project-docs/report/main.tex` — three insertions (Abstract, §4.2 last sentence, §5 preamble) + 1–4 compensating tightenings
- `project-docs/report/report.pdf` — recompile

## 5. Verification

1. `cd project-docs/report && pdflatex report.tex && bibtex report && pdflatex report.tex && pdflatex report.tex`
2. `pdfinfo report.pdf | grep Pages` — expect 15
3. Last sentence of page 5 must be the §8 Conclusion close: "evaluate Poisson by direction, magnitude, and decision path."
4. Page 6 must start with "References"; page 7 with "A Methodology details"
5. Visual check: read page 1 abstract aloud — does the new metric-split sentence flow? Read §4.2 last sentence — does the forward reference land? Read §5 first paragraph — does it set up the decision-path frame coherently?

## 6. Commit + push

After verification: stage `main.tex`, recompiled `report.pdf`, and `prompts.md` (with prompt log). Commit message: "Surface the Wq vs blocking metric split in Abstract, §4.2, and §5". Push to origin/main.

---

## 7. Open questions for user before applying

None. The diffs are concrete and the page-budget plan is mechanical. Awaiting "yes" / approve / "go".
