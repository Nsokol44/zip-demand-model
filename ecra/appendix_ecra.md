# Online Appendix to “Estimating Online Demand with Sparse Geographic Data”

This appendix accompanies the main text. Appendix A reports the Bayesian rare-event layer in full (summarized in Section 6 of the main text). Appendices B and C hold supplementary tables and a supplementary figure. References are numbered as in the main text; the works cited in this appendix are listed at its end.

## A. The Bayesian rare-event layer: a pre-stated test, and a mixed verdict

This section answers one question: does replacing the two-step estimation core with a single Bayesian count model repair the interval failure of Section 5.4? The design, priors, and verdict criteria were fixed in writing before any Bayesian fit was run. The answer is mixed. The layer gives the best point recovery of any estimator tested. It does not repair interval coverage. And it does not beat Fay–Herriot on the decision metric that matters in dollars (significantly worse for one product, indistinguishable for the other, on paired per-draw differences). Nothing in this appendix changes any number in Section 5 of the main text.


### A.1 Model, priors, and the pre-stated criteria

The Bayesian layer replaces the plug-in log rate and the Fay–Herriot stage with one generative count model. For a sampled ZCTA i, the order count is negative binomial (NegBin) with mean equal to households multiplied by the exponential of a latent log rate. Households enter as an offset (a log-households term with its coefficient fixed at 1), so the estimand is the same latent log order rate graded everywhere in Section 5. The latent log rate is an intercept, plus the nine standardized covariates, plus an area effect. The area effect follows the BYM2 parameterization of Riebler, Sørbye, Simpson, and Rue [92], built on the convolution prior of Besag, York, and Mollié [93]: a scaled intrinsic conditional autoregressive (ICAR) component on the study's six-nearest-neighbor graph, mixed with an independent component, with one total standard deviation (σ_b) and one mixing share (φ). The one declared deviation from Section 5 is that the +0.5 continuity correction disappears, because a count likelihood does not need it. The estimator changes. The estimand does not.

Priors were fixed before fitting, and none was centered on the data-generating truth. Regression coefficients take Normal(0, 1) priors and the intercept is effectively flat. Log(size) takes a Normal(2.0, 1.25) prior (median size about 7.4, against a truth of 6.0). σ_b takes a Half-Normal(0, 1) prior and φ is uniform. This discipline follows the penalized-complexity prior argument of Simpson, Rue, Riebler, Martins, and Sørbye [94]: priors are set by a base-model argument in advance, so the interval test is honest rather than tuned to pass. The closest recent analogue [95] models sparse counts in retail analytics with a Bayesian hierarchy, without the pre-stated coverage audit across replicate draws added here.

Computation is by Markov chain Monte Carlo (MCMC) with the No-U-Turn sampler: four chains, 1,000 tuning and 1,000 draws per chain, per replicate. The full Bayesian field (a BYM2 sparse-precision parameterization) timed at about 48 minutes per fit in the pilot, beyond the design note's 15-minute rule. The authorized fallback was therefore taken for all fits, before any grading output was examined: an eigen-truncated ICAR field using the top 300 eigenvectors. Throughout, “the Bayesian layer” means that BYM2-type prior under its top-300 eigenvector approximation, estimated by MCMC. INLA [96] fits this model class without MCMC but sits outside our Python replication stack, and no claim is made about whether it would change the verdicts. A sanity gate passed before fitting: the unmodified pipeline reproduces Table 4 of the main text (Fay–Herriot RMSE 0.512 and 0.529). Every comparison below is like-for-like, on the same 24 draws, the same 8 percent stratified design, and the same grading metrics as Section 5, plus targeting regret, the dollar loss from targeting the top decile of areas by estimated rather than true log rate.

The design fixed two Tier 1 criteria in advance, and a third that Tier 2 would have graded. Criterion C1 (calibration) requires sampled-area coverage closer to 95 percent than bootstrap-calibrated Fay–Herriot for both products, at no more than 1.5 times its width. Criterion C2 (recovery) requires all-area RMSE no worse than Fay–Herriot, paired on the same draws, for both products. Criterion C3 (transport) requires Tier 2 held-out performance within the econometric layers' near-tie band on at least three of four evaluations. The Tier 2 Bayesian fits have since been run for one evaluation, the electronic-shopping outcome, and are reported in Section 8 of the main text: on that evaluation the layer falls far outside the band. One evaluation of the three C3 requires has been run, so C3 remains not assessable, and no transport claim is made.


### A.2 Results and verdict

Point recovery improves, and Table A3 and Figure A2 give the detail. The Bayesian layer has the lowest all-area RMSE of any estimator on both products, 0.530 ± 0.011 (steamers) and 0.521 ± 0.009 (trio), against Fay–Herriot 0.538 ± 0.013 and 0.528 ± 0.012, ordinary least squares 0.541 and 0.531, and the best spatial model 0.545 and 0.534. Coefficient recovery is reasonable, with mean absolute error of 0.090 (steamers) and 0.066 (trio).

Intervals do not improve. Sampled-area coverage of the nominal 95 percent posterior intervals is 88.5 percent ± 12.1 (steamers) and 91.9 percent ± 4.0 (trio), graded on paired per-draw differences because the draw-to-draw spread is wide. Against the bootstrap-calibrated Fay–Herriot intervals of Section 5.4 (91.4 percent and 90.0 percent on the same draws), the paired differences (Bayesian minus calibrated Fay–Herriot) are −2.9 percentage points for steamers (95 percent confidence interval −7.7 to +1.9) and +1.9 points for trio (−1.4 to +5.2). Both intervals cover zero, so across draws the Bayesian layer's coverage is indistinguishable from its calibrated competitor for either product. Against the uncalibrated plug-in intervals (88.5 percent and 87.6 percent), the paired differences are 0.0 points for steamers (−5.0 to +5.0) and +4.3 points for trio (+1.2 to +7.4), the one coverage contrast whose interval excludes zero. Interval widths are comparable (Bayesian 1.366 and 1.429, against Fay–Herriot 1.371 and 1.388 on sampled areas), so the differences are not bought with width.

Decisions do not improve either. Mean targeting regret is higher for the Bayesian layer in dollars, $836.93 against $817.47 (steamers) and $483.95 against $478.26 (trio), at regret rates of about 0.004 and 0.003 for both estimators. The paired per-draw differences are +$19.46 for steamers (95 percent confidence interval +$0.81 to +$38.12), which excludes zero, and +$5.69 for trio (−$6.64 to +$18.01), which does not. The best point estimates do not make the best targeting decisions here.

Two diagnostics explain why the intervals do not repair. The variance split stays weakly identified, now inside the posterior. Posterior mean size is 10.37 ± 6.83 (steamers) and 13.97 ± 9.92 (trio) against a truth of 6.0. That is closer than the maximum-likelihood Fay–Herriot fits (14.8 and 24.7 on the same draws), but still high and dispersed, and the posterior correlation between log(size) and σ_b is about 0.80. The ridge of Section 5.4 survives into the posterior, and carrying the ridge, rather than plugging in one point of it, was not sufficient to widen the intervals to nominal on sampled areas. The spatial field itself is weakly recovered: the posterior-mean field correlates only 0.159 (steamers) and 0.179 (trio) with the true spatial autoregressive field, with field RMSE of 0.498 and 0.496. The layer predicts rates well while recovering the field that generated them poorly.

Convergence is reported, not hidden. The gates pre-specified in the dated design note (maximum split R-hat at most 1.01 and bulk effective sample size at least 400 on the gated parameters) pass in only 1 of 24 fits (steamers) and 0 of 24 fits (trio), with failures concentrated on the ridge parameters, log(size) and σ_b. Per-chain posterior means agree closely, and failing fits were re-run once with 2,000 tuning draws and are retained and graded, not discarded. An implementation self-test on data simulated from the fitted model itself recovered sampled coverage of 0.955 and all-area coverage of 0.972. The sampler is correct, and the under-coverage on our data-generating process is a property of the posterior under that process, not an implementation error.

The verdict on the pre-stated criteria is narrow. Criterion C2 (recovery) holds: the Bayesian layer is marginally the best point-recovery estimator tested. Criterion C1 (calibration) fails: it is met for trio and missed for steamers, so the layer is not presented as a remedy for the interval pathology. Criterion C3 (transport) is not assessable: the layer has been run on one Tier 2 evaluation, the electronic-shopping outcome, where it fell far outside the econometric near-tie band (Section 8 of the main text). A principled count model with principled priors improves point recovery slightly, leaves the calibration pathology in place for one of two products, and does not improve the dollar decision metric.

A temporal extension, designed separately and labeled as such wherever it appears, was run as a single-replicate pilot. Its testbed runs 52 weeks for steamers, with two pre-fixed calendar moments whose effects differ by region: a holiday-gift window (weeks 48–51, true effects +0.45 in the Southeast and +0.30 in the New York City metro) and a spring event week (week 19, +0.25 and +0.40). One replicate of the eight designed (n = 1) was run. All four moment effects were recovered with the truth inside the 95 percent credible interval: posterior means 0.437 (holiday window, Southeast, truth +0.45), 0.333 (holiday window, New York City metro, truth +0.30), 0.302 (spring event, Southeast, truth +0.25), and 0.440 (spring event, New York City metro, truth +0.40). Weekly-surface RMSE was 0.513 for the Bayesian layer against 0.522 for the week-pooled cross-sectional comparator. Moment-week targeting regret was $21.67 for the Bayesian layer against $20.73 for the pooled comparator: slightly worse, in line with the cross-sectional regret result. Seven of the eight designed replicates were not run. No temporal claim beyond this single-replicate recovery is made.

**Table A3 and Figure A2 follow.**

**Table A3. The Bayesian rare-event layer on Tier 1 (24 draws, both products; means ± 1 sd). The fitted model is the BYM2-type prior of Appendix A.1 under its top-300 eigenvector approximation, estimated by MCMC. Comparators are the same draws graded in Section 5. FH = Fay–Herriot; RMSE = root mean square error on the log-rate scale; CrI = credible interval; CI = confidence interval.**

| Quantity | Steamers | Trio |
| --- | --- | --- |
| RMSE, all areas. Bayesian layer | 0.530 ± 0.011 | 0.521 ± 0.009 |
| RMSE, all areas. FH | 0.538 ± 0.013 | 0.528 ± 0.012 |
| RMSE, all areas. Ordinary least squares | 0.541 | 0.531 |
| RMSE, all areas. Best spatial model | 0.545 | 0.534 |
| Coverage, sampled areas. Bayesian 95% CrI | 88.5% ± 12.1 | 91.9% ± 4.0 |
| Coverage, sampled areas, FH plug-in | 88.5% | 87.6% |
| Coverage, sampled areas, FH bootstrap-calibrated | 91.4% | 90.0% |
| Interval width, sampled areas. Bayesian / FH | 1.366 / 1.371 | 1.429 / 1.388 |
| Coefficient mean absolute error, Bayesian | 0.090 | 0.066 |
| Coefficient 95% CrI coverage, Bayesian | 81.0% | 89.4% |
| Posterior size (truth 6.0). Bayesian / FH maximum likelihood | 10.37 ± 6.83 / 14.8 | 13.97 ± 9.92 / 24.7 |
| Posterior σ_b / φ. Bayesian | 0.446 / 0.182 | 0.483 / 0.158 |
| Field recovery: correlation with true field / RMSE | 0.159 / 0.498 | 0.179 / 0.496 |
| Targeting regret ($). Bayesian / FH | 836.93 / 817.47 | 483.95 / 478.26 |
| Paired difference in sampled-area coverage, Bayesian − FH plug-in (percentage points, mean and 95% CI) | 0.0 (−5.0 to +5.0) | +4.3 (+1.2 to +7.4) |
| Paired difference in sampled-area coverage, Bayesian − FH bootstrap-calibrated (percentage points, mean and 95% CI) | −2.9 (−7.7 to +1.9) | +1.9 (−1.4 to +5.2) |
| Paired difference in targeting regret, Bayesian − FH (US$, mean and 95% CI) | +19.46 (+0.81 to +38.12) | +5.69 (−6.64 to +18.01) |
| Convergence gates passed | 1 of 24 fits | 0 of 24 fits |


**Figure A2. The Bayesian layer does not repair interval coverage. The bars show coverage, in percent, of nominal 95 percent intervals on the sampled areas, by method and product (steamers, blue; trio, vermillion), as means across the same 24 sample draws for every method; error bars are ± 1 standard deviation (sd) across draws, the value printed inside the top of each bar is its mean, and the dashed line is the nominal 95 percent (see the legend above the axes). Three methods are compared (main text, Sections 5.4 and 6): plug-in Fay–Herriot (FH) intervals, which cover 88.5 percent (steamers) and 87.6 percent (trio); bootstrap-calibrated FH intervals, which cover 91.4 and 90.0 percent; and the Bayesian layer's posterior intervals, which cover 88.5 and 91.9 percent. On paired per-draw differences the Bayesian coverage is indistinguishable from the calibrated Fay–Herriot coverage for both products (Appendix A.2 and Table A3), and both sit short of nominal, at interval widths comparable to the Fay–Herriot intervals.**

![Figure A2](figures_new/calibration_coverage.png)


## B. Supplementary tables

**Table A1. Competitor-response strategies in the game-theory layer (all values are stated assumptions).**

| Strategy | Incumbent attractiveness | Entrant CAC | Entrant margin |
| --- | --- | --- | --- |
| No response | ×1.00 | ×1.00 | ×1.00 |
| Moderate | ×1.25 | ×1.20 | ×0.95 |
| Aggressive | ×1.60 | ×1.50 | ×0.85 |


**Table A2. Top five clusters per region by expected annual orders (steamers product, model scale). Coherence: Southeast 0.25 (17 clusters); NYC metro 0.42 (12 clusters).**

| Region | Cluster | ZIPs | Households | Exp. orders/yr | Mean uptake | Mean renter | Mean income |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Southeast | 15 | 185 | 2,227,362 | 123,508 | 0.045 | 0.61 | $50,821 |
| Southeast | 9 | 72 | 626,261 | 122,419 | 0.077 | 0.70 | $81,329 |
| Southeast | 5 | 260 | 3,457,265 | 118,366 | 0.063 | 0.40 | $93,305 |
| Southeast | 1 | 438 | 4,722,727 | 69,521 | 0.034 | 0.44 | $53,954 |
| Southeast | 11 | 481 | 5,249,939 | 37,254 | 0.044 | 0.25 | $80,190 |
| NYC metro | 6 | 61 | 1,255,673 | 218,171 | 0.063 | 0.70 | $69,261 |
| NYC metro | 2 | 33 | 670,910 | 185,125 | 0.087 | 0.68 | $101,180 |
| NYC metro | 7 | 37 | 561,899 | 171,581 | 0.124 | 0.71 | $158,999 |
| NYC metro | 10 | 34 | 749,854 | 150,145 | 0.053 | 0.87 | $47,237 |
| NYC metro | 0 | 33 | 320,845 | 23,009 | 0.074 | 0.41 | $110,469 |


## C. Supplementary figure

**Figure A1. Payoff distribution for the showcase play-through. The histogram shows the Monte Carlo one-year payoff (US dollars) for paid market entry into ZIP 10282 (New York metro) for steamers, across 500 draws of the incumbent's response, advertising prices and conversion rates (main text, Section 5.9). Dashed lines mark the 10th and 90th percentiles of the payoff (−$812 and −$293); the median is −$522; the vermillion line marks a payoff of zero. Every draw loses money (win rate 0 percent), and the pre-stated decision rule returns Avoid for this ZIP.**

![Figure A1](figures_new/Figure_4.png)


## References cited in this appendix

[92] A. Riebler, S.H. Sørbye, D. Simpson, H. Rue, An intuitive Bayesian spatial model for disease mapping that accounts for scaling, Stat. Methods Med. Res. 25 (2016) 1145 – 1165.

[93] J. Besag, J. York, A. Mollié, Bayesian image restoration, with two applications in spatial statistics, Ann. Inst. Stat. Math. 43 (1991) 1 – 20.

[94] D. Simpson, H. Rue, A. Riebler, T.G. Martins, S.H. Sørbye, Penalising model component complexity: A principled, practical approach to constructing priors, Stat. Sci. 32 (2017) 1 – 28.

[95] J. Pitkin, I. Manolopoulou, G. Ross, Bayesian hierarchical modelling of sparse count processes in retail analytics, Ann. Appl. Stat. 18 (2024) 946 – 965.

[96] H. Rue, S. Martino, N. Chopin, Approximate Bayesian inference for latent Gaussian models by using integrated nested Laplace approximations, J. R. Stat. Soc. Ser. B (Stat. Methodol.) 71 (2009) 319 – 392.
