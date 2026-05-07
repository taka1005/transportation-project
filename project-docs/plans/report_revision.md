# 最終レポート修正タスク: Phase 4.4

## 背景

「Is Poisson Good Enough?」プロジェクトのレポート(`project-docs/report/main.tex`
および `project-docs/report/appendix.tex`)に対して、最終調整を行います。
Phase 4.2 (writing) と Phase 4.3 (metric-split emphasis) は完了済みで、
今回はそれらの後の **post-presentation revision pass** です。

修正の根拠は3つの情報源です:

1. **Alex のレビューメール**(共著者からのフィードバック、特に
   Little's Law の式の誤りと数値整合性の指摘)
2. **最終版ビデオ原稿とスライドデッキ**との整合性確認(presentation で
   公に主張する内容と report の内容を一致させる)
3. **Cathy Wu 教授の質疑応答パターン分析**(Day 1 の他チーム発表での
   教授の質問から、Day 2 の自分たちへの質問を予測し、レポート段階で
   先回り対応する)

## 既存ワークフロールールの遵守

これまでの Phase 4.x と同じ規律で進めてください:

- **プランファースト承認ゲート。** 各 Phase 開始前に diff を見せて、私の "yes" / "go" / "approve" を待ってから commit する。その際、各修正におけるあなたの懸念があれば提示してください。
- **prompts.md にプロンプトログを残す。** これまでの慣行どおり。
- **`pdflatex report.tex` のクリーンビルドを各 Phase 後に検証。**
  参照切れ・引用切れに注意。
- **数値は記憶ではなく原典(分析ノートブック・元データ)から取る。**
  値がおかしいと思ったら勝手に変えず、必ずフラグを立てて確認する。
- **セクション全体を書き直さない。** 外科的編集のみ。Phase 4.2 で
  確立した voice と構造を保持する。
- **diff には行番号を必ず添える。** PDF と照合できるように。
- **commit message のフォーマット:** これまでどおり、変更の要点を
  1行で要約する形(例: "Fix Little's Law formula and numerical consistency").

## ページ予算

Phase 4.3 のドキュメントによれば、main body は ≤ 5 ページ、appendix は
≤ 10 ページ。Phase 4.4 で追加されるテキストは正味 +15〜20 行になる
見込みなので、Phase 4.3 の §3 で示された compensating compressions
(優先順位リスト)を必要に応じて適用してください。

ただし、Phase 4.4 の修正の多くは appendix と methods 章で起きるので、
ページオーバーフローのリスクは限定的です。

---

## Phase 1: 必須の正確性修正(最優先)

これらは妥協できません。この順序で対応してください。

### 1.1 Little's Law の式を修正(Appendix A.2)

**問題:** 現在の `appendix.tex` の Equation (2)(§A.2 内)は
dimensional に循環しています — μ を W̄_slot で表しているのに
W̄_slot = 1/μ なので、循環参照です。正しい導出は §D.3 に既にあるので、
A.2 の本文を D.3 と整合する形に書き換えます。

**作業内容:** `appendix.tex` の §A.2 のパラグラフを以下の英文で置き換える:

```latex
For Bluebikes we treat each dock slot as a server and define the service time as the
elapsed time between a bike arriving at the dock and the next departure of that slot.
Let $L_{\text{non-full}}$ be the average number of occupied docks during non-full
periods and $\lambda$ be the accepted arrival rate. By Little's Law applied per-slot,
the mean dock occupancy time is $\bar{W}_{\text{slot}} = L_{\text{non-full}}/\lambda$,
so the per-slot service rate is
\[
\mu = \frac{1}{\bar{W}_{\text{slot}}} = \frac{\lambda}{L_{\text{non-full}}}.
\]
After fullness correction the estimated mean service times are 7,367\,s at Kendall/MIT
and 6,670\,s at MIT Vassar~St, yielding per-server utilisations of $\rho = 0.48$ and
$\rho = 0.33$ respectively. For MBTA the service time is the observed platform dwell
time; $\rho$ ranges from $0.15$ to $0.20$.
```

**検証:** 修正前に、数値(7,367 s、6,670 s、ρ=0.48、ρ=0.33)が分析
ノートブック(`notebooks/phase3_*.ipynb` 等)の結果と一致するか必ず
検証すること。一致しなければ commit せず、ノートブックの値を私に報告する。

### 1.2 数値整合性の監査

**作業内容:** `main.tex` と `appendix.tex` の全文に対して、以下の値の
出現箇所を grep で洗い出し、表形式で報告してください。**この時点では
何も変更しない。** 私が canonical な値を判断します。

| 値 | 期待される標準値 | 確認すべき主な箇所 |
|---|---|---|
| Erlang B Kendall blocking | 0.068% | Abstract, §4.3, Figure 9, Table 6 |
| Empirical DES Kendall blocking | 0.54% | §4.3, Figure 8, Figure 9, Table 6 |
| Best-fit Weibull DES Kendall blocking | 0.46% | Figure 8 のみ — §4.3 の本文に欠けている |
| Observed Kendall fullness | 3.73% | §2, §4.3, Table 6 |
| Bluebikes Kendall IoD (30-min window) | 3.2 (Table 1 に従う) | Table 1, presentation との照合 |
| MBTA Wq Northbound (Poisson DES) | 20.5 s | Table 2, Table 6 |
| MBTA Wq Northbound (empirical DES) | 4.2 s | Table 2, Table 6 |
| Wq Bluebikes Kendall (Poisson DES) | 1.4 s | Table 2, Table 6 |
| Wq Bluebikes Kendall (empirical DES) | 9.4 s | Table 2, Table 6 |

報告フォーマット例:

```
Value: "Erlang B Kendall blocking = 0.068%"
- Abstract (line 4): "0.068" ✓
- §4.3 (line 87): "0.068\%" ✓
- Figure 9 caption (line 154): "0.07%" — 丸めの違い、判断要
- Table 6 (line 170): "0.068" ✓
```

私が「全部 0.068% に統一する」「丸めの違いは許容する」などを判断したのち、
Phase 1.2.1 として実際の修正に進みます。

### 1.3 Best-fit DES の blocking 値を §4.3 の本文に追加

**問題:** §4.3 では "Finite-capacity DES with empirical IATs gives 0.54%"
としか書かれていません。Figure 8 には DES Weibull = 0.46% も表示されており、
**この比較は研究の核心**(marginal distribution alone is insufficient
regardless of empirical or parametric)ですが、本文に欠けています。

**作業内容:** `main.tex` の §4.3 の該当箇所に、empirical-DES の値を
言及した文の直後に以下の英文を追加:

```latex
Best-fit Weibull DES gives 0.46\%, comparable to empirical bootstrap and well short
of the observed 3.73\%; the marginal IAT distribution alone is insufficient
regardless of whether resampled empirically or fit parametrically.
```

これによって、Phase 4.3 で確立した「marginal IAT is sufficient for Wq but
not for blocking」というメッセージが §4.3 内でも定量的に裏付けられます。

---

## Phase 2: Q&A 防御のためのセクション強化

Wu 教授の Day 1 質問パターンから、彼女は次の3点を必ず突いてきます:

(a) 直感的なメカニズムの説明(numbers ではなく why の追求)
(b) i.i.d. bootstrap の正当性(Day 1 で Xian に4回連続で同じ論点を突いた)
(c) decision-relevance の限定("harmless" のような universal claim を challenge する)

これらに対して、レポート段階で先回り対応します。

### 2.1 §3 Methods に CV/IoD の直感的定義を追加

**根拠:** Wu 教授は intuition を最も重視する。現状の §3 では CV と IoD を
定義式だけで導入しており、なぜ両方使うのかが説明されていない。

**作業内容:** `main.tex` §3「Arrival-process characterization」の冒頭、
既存の統計量リストの**前に**以下の英文パラグラフを挿入:

```latex
CV and IoD play complementary diagnostic roles. CV measures irregularity in the
inter-arrival time distribution---whether gaps between consecutive arrivals are
more or less variable than exponential. IoD measures whether arrival counts in
fixed time windows fluctuate more or less than a Poisson process; for a homogeneous
Poisson process, both equal one. Segmenting these metrics by hour, day-of-week, and
peak/off-peak period (Appendix~B) tests whether observed non-Poisson behavior is
an aggregation artefact of mixing periods with different rates, or a persistent
structural feature of each system.
```

### 2.2 §3 Methods に分布選択の rationale を追加

**作業内容:** "We fit exponential, log-normal, Weibull, and gamma by maximum
likelihood and rank them by AIC." の直後に、以下の英文を挿入:

```latex
The four candidates span the relevant hazard structures: exponential is the
Poisson baseline; Weibull with shape $c < 1$ has a monotone-decreasing hazard
suited to bursty arrivals; log-normal has a multiplicative-noise interpretation
suited to scheduled service plus operational jitter; gamma is a flexible
positive-support comparator covering both monotone and unimodal hazard regimes.
```

### 2.3 §3 Methods に GoF テストの rationale を追加

**作業内容:** "Fits are tested with Kolmogorov--Smirnov (KS), Anderson--Darling (AD),
and Pearson $\chi^2$ statistics." の直後に、以下の英文を挿入:

```latex
KS captures global CDF shape mismatch, AD emphasizes tail discrepancies (where
predictions of rare events live, including blocking), and $\chi^2$ provides a
binned-frequency robustness check.
```

### 2.4 i.i.d. bootstrap の限界を §3 で先に明示

**根拠:** Wu 教授は Day 1 で Xian に対して i.i.d. resampling の正当性を
4回連続で突いた(transcript 9:02, 9:26, 9:58, 10:21)。これは教授の最頻出
攻撃ベクトルであり、§6 の limitations に書くだけでは遅い。§3 で導入時に
明示することで、Q&A での先回り対応になる。

**作業内容:** `main.tex` §3「Discrete-event simulation」のパラグラフ末尾
("Each configuration uses 20,000..." の前)に以下の英文を追加:

```latex
The empirical bootstrap preserves the marginal IAT distribution exactly but samples
i.i.d., intentionally removing any sequential or time-of-day structure. We exploit
this property in \S\ref{sec:results-erlangb} to attribute residual blocking error
to non-stationarity rather than to the marginal distribution.
```

### 2.5 §4.3 を3つの time-structure 効果で再構成

**根拠:** スライドデッキ(Slides 22--25)では、residual gap の説明を
λ(t) / μ(t) / temporal coupling の3つに明確に分けている。レポートの §4.3
では現状この構造が不明瞭で、μ と λ の説明が交互に出てくる。プレゼン中に
聴衆が「あれ、スライドでは3つって言ってたけど、レポートでは何個?」と
混乱する可能性がある。両者の構造を揃える。

**作業内容:** `main.tex` §4.3 の "Stationary arrival correction alone therefore
cannot explain..." で始まるパラグラフを、以下の英文で置き換え:

```latex
Three time-structure effects neither stationary model captures:
(i) \emph{Time-varying $\lambda(t)$.} Returns peak at morning and evening commute
and average to a single $\lambda$ in stationary models, suppressing the peak-hour
pressure that drives blocking.
(ii) \emph{Time-varying $\mu(t)$.} At Kendall, dock turnover slows during peak
return demand because rentals drop when commuters are inbound rather than outbound;
the i.i.d.\ exponential service assumption fixes $\mu$ at a daily mean and misses
this dip.
(iii) \emph{Temporal coupling.} $\lambda$ peaks coincide with $\mu$ valleys at the
same hour of day, compounding the blocking pressure multiplicatively. Neither
stationary Erlang~B nor i.i.d.\ empirical DES exposes this coupling---the empirical
bootstrap closes only a seventh of the gap because it preserves marginal burstiness
but, by sampling IATs i.i.d., destroys both time-of-day ordering and any coupling
with $\mu$.
The MBTA has no analogue at $\rho = 0.15$--$0.20$.
```

### 2.6 "harmless" を限定的な表現に変更

**根拠:** Wu 教授は universal claims に対して "is it really?" 攻撃を仕掛ける
傾向がある。"harmless" は現状 unconditional に書かれており、教授は必ず
「他の context では harmful になりうるのでは?」と突いてくる。

**スライドとの方針:** スライドデッキでは "HARMLESS" のラベルをそのまま残す
(発表での記憶に残りやすさ優先)。**レポートのみ**この限定的な表現に変更する。
両者の意図的な使い分けは Alex と同意済み(WhatsApp 連絡済み)。

**作業内容(箇所1):** §5 Discussion の "Off the decision path: MBTA wait"
小節内
- 現状: "the over-prediction is harmless rather than wasteful"
- 変更後(英文):

```latex
the over-prediction is low-risk in this MBTA per-train wait context rather than
wasteful---$W_q$ is not on a planning decision path that depends on per-train
accuracy. In contexts where $W_q$ drives operational decisions (e.g., passenger-flow
signage, staff scheduling), the same 5--12$\times$ error would be problematic
```

**作業内容(箇所2):** §7 Conclusion 内
- 現状: "The MBTA wait over-prediction is harmless because per-train Wq does not
  feed transit planning."
- 変更後(英文):

```latex
The MBTA wait over-prediction is low-risk in this context because per-train $W_q$
does not feed the transit planning decisions at this station---platform sizing is
set by capital infrastructure and service frequency by demand and operations,
not by per-train $W_q$.
```

### 2.7 §4.1 segmentation の主張を慎重な表現に

**根拠:** 現状の主張は "attributes the Bluebikes CV to non-stationarity" で
強すぎる。Table 4 を見ると Bluebikes Kendall は全時間帯で CV ≥ 1.0 なので、
時間帯による変動と「窓内の Poisson からの逸脱」の両方が存在する。教授の
"is it really attributable solely to..." 質問に備えて、より精緻な記述に変える。

**作業内容:** `main.tex` §4.1 の該当箇所を以下の英文に書き換え:

```latex
Within-day segmentation (Appendix~B.2, Table~\ref{tab:cv-hour}) shows substantial
hour-to-hour variation in CV (Kendall: 1.0 at midnight, 2.4 at 18:00), indicating
that part of the aggregate CV reflects rate non-stationarity. However, CV remains
$\geq 1.0$ at every hour---within-window deviations from Poisson persist alongside
the time-of-day pattern, so the rejection of Poisson is not solely an aggregation
artefact.
```

### 2.8 §6 の future work に統合まとめを追加

**根拠:** Wu 教授は future work の actionability を必ず聞く(Day 1 で Speaker 13
に "what would you extend?" を2回聞いた)。優先順位を明示することで、
「どれを最初にやるか?」質問に即答できる。

**作業内容:** `main.tex` §6 の**末尾**に以下の英文パラグラフを追加
(既存のパラグラフは消さない):

```latex
In summary, three concrete extensions follow directly from the limitations above:
(1)~re-running \S\ref{sec:results-arrivals} and \S\ref{sec:results-erlangb} on
Mellou--Jaillet-reconstructed arrivals to separate censoring-induced from real
non-Poissonness; (2)~replacing the i.i.d.\ bootstrap with an autocorrelation-
preserving generator (block bootstrap or Markov-modulated Poisson) to test the
timetable-structure hypothesis on MBTA $W_q$; (3)~implementing a non-homogeneous
Erlang~B with hourly $\lambda(t)$ and time-varying $\mu(t)$ to test whether
joint non-stationarity closes the residual blocking gap. (3) is the highest-priority
extension because it directly tests the residual-attribution argument of
\S\ref{sec:results-erlangb}.
```

---

## Phase 3: 任意の改善(時間があれば)

### 3.1 Introduction の "engineering approximation" フレーミング

**根拠:** Alex の suggestion。現状の Introduction は実は同等の内容を既に
含んでいる("how much queueing predictions suffer when the assumption fails")
が、Alex の提案する明示的フレーミングはより強い。

**作業内容(任意):** `main.tex` §1 の冒頭の文を以下の英文に強化:

- 現状: "Queueing theory in transportation is built on the Poisson arrival assumption."
- 強化後(英文):

```latex
Queueing theory in transportation is built on the Poisson arrival assumption,
used not as a literal claim about arrivals but as an engineering approximation
that trades some accuracy for tractability.
```

ページ予算が厳しければ skip。

### 3.2 Figure 8 のキャプション確認

Figure 8 のキャプションが、実際に描画されている4つのバー(Erlang B / DES
Exponential / DES Empirical / DES Weibull / Observed)と整合しているかを
確認してください。整合していれば変更不要。

---

## 触らないこと(対象外)

- 図そのもの — 確定済み(Phase 4.2 で finalized)
- 参考文献リスト — 本当に欠けているものがない限り追加しない
- Abstract — 既に強い、編集しない。Phase 4.3 の metric-split 文も既に統合済み
- §7 Conclusion 全体 — 既に強い。2.6 で指定した "harmless" の1箇所のみ変更
- Phase 4.3 で確立した metric-split emphasis(§4.2 forward reference,
  §5 preamble paragraph)— これらは保持する。Phase 4.4 はこれらの「上に」
  building up するもの

---

## 各 Phase 終了時の報告フォーマット

これまでの Phase 4.x と同じ形式で:

```
## Phase 4.4.X 完了報告

### 変更箇所
- main.tex line 47--52: CV/IoD definition paragraph を §3 冒頭に挿入
- main.tex line 89: best-fit DES blocking 値を §4.3 に追加
...

### 検証
- pdflatex のクリーンビルド: ✓
- ページ数: 15 (15 のまま、変化なし)
- 参照切れ: なし

### フラグを立てた箇所(私の判断待ち)
- (例) Figure 9 のキャプション "0.07%" は 0.068% に丸めるべきか?

### prompts.md 更新済み: ✓
```

---

## 開始時の最初のアクション

**まず Phase 1.2(数値整合性監査)から始めてください。** これは何も
変更しない読み取り専用のタスクで、結果を見てから他の修正の優先順位を
最終決定します。1.2 の結果報告を受けたあと、私が「1.1 を実行」「1.3 を
実行」など個別に指示します。