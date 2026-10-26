# Estimating Online Demand with Sparse Geographic Data


## Abstract

A small online seller observes demand in a sparse, non-random slice of ZIP codes, the normal condition of electronic commerce. We stress-test the analytics (spatial econometrics with a Fay–Herriot (FH) stage, a GeoAI (geographic artificial intelligence) audit layer, and a decision layer) at 8 percent sampling (447 of 5,576 ZCTAs), in two tiers and 24 draws (simulation recovery against a known truth, and a benchmark on observed outcomes). Three pathologies emerge. Spatial diagnostics detect a strong process in only 17 to 42 percent of draws. Plug-in FH intervals average 88.5 and 87.6 percent coverage of sampled areas (93.1 and 96.0 percent over all areas) against a nominal 95 percent, because the variance split is weakly identified. Estimator rankings do not transport from simulated to real surfaces. A Bayesian rare-event layer (a BYM2-type count model, under an eigenvector approximation) gives the best point recovery but a mixed interval verdict, and it does not transport: on the observed e-commerce outcome it is the worst layer in all 24 draws, its regret no better in dollars. Under stated, assumed economics, the decision layer returns Avoid for all 50 shortlisted ZIP codes. Sparse demand data can support decisions, but only with honest intervals.

Keywords: electronic commerce; diagnostic power; Fay–Herriot model; GeoAI; interval coverage; small area estimation; spatial econometrics


## 1. Introduction

A small online seller faces a simple problem. It can sell anywhere, but it can only learn where demand is by spending money in a few places first. A first demand test reaches a small, non-random slice of the national map: a few hundred ZIP codes out of tens of thousands, picked for affordability, platform deliverability, and prior suspicion. Every other ZIP code is unobserved, yet the seller must still decide, for every place, whether to spend, test further, or stay out. Our subject is the analytics that decision rests on, and how those analytics behave when 92 percent of the map is missing.

That condition is the normal condition of electronic commerce, not an edge case. The storefront is geographically unbounded, in the marketplace structure the field's founding statement describes [1], but fulfillment, delivery cost, and paid acquisition are all priced by place. Marketplaces lower buyer search costs [2], yet the seller's problem of locating demand does not fall with them. Digital economics lowers search, replication, and verification costs [3]; measuring local demand from a sparse test is the cell of that framework we fill. Liu, Zheng, Wei, and Yang [4] show that big-data analytics capability improves e-platform performance; those returns accrue to firms that have big data. We study the complementary population: sellers whose data are small by design.

The design-science framing fits the same point: the pipeline below is an artifact, a composed estimation and decision procedure, and its evaluation is the contribution, in the sense of Hevner, March, Park, and Ram [5], following Peffers, Tuunanen, Rothenberger, and Chatterjee [6]. The evaluation is pre-stated, run in two tiers, and graded against criteria fixed before the new layer was fitted, stricter than the single-context demonstrations the design-science literature usually reports. The strictness matters, because our central finding is that a rigorous simulation evaluation can still fail to transport.

Where will a product sell? For a firm launching a consumer product online but fulfilling it into physical space, the operative geography is the ZIP code: platforms sell targeting by it, carriers price by it, and customers experience delivery through it. Yet the data at that geography are very thin: a new entrant begins with no transaction history, and even a successful test generates outcomes in a few percent of a national market's postal areas. The estimation problem is therefore a small-area problem: produce a defensible estimate, with a stated uncertainty, for every area, when almost every area is unobserved.

The conventional substitute, buying measurement from advertising platforms, is less reliable than its dashboards suggest. Gordon et al. [7], writing from inside the industry’s measurement apparatus, document structural inefficiencies that make platform-reported performance a compromised guide to allocation. The deeper problem is statistical. Lewis and Rao [8] show that the variance of individual-level purchase outcomes is so large relative to plausible advertising effects that detecting the return on advertising at feasible sample sizes is often economically hopeless. Gordon et al. [9] demonstrate that the observational methods used to circumvent this problem disagree with large randomized experiments, frequently and badly, and Gordon, Moakler, and Zettelmeyer [10] find that even the best observational estimators only sometimes approximate experimental ground truth. The lesson for a small entrant is not that measurement is impossible, but that it must be designed: the firm must generate its own geographically structured evidence, and own estimators built for the sparsity that evidence will still exhibit.

We subject that toolkit to an extreme stress test. The vehicle is a three-layer pipeline of exactly the kind an applied program would compose: a spatial-econometric small-area layer that estimates, a GeoAI layer that audits it, and a game-theoretic decision layer that converts estimates into choices. The layers are individually standard; the composition is not the contribution. The contribution is what the stress test finds when the pipeline is run at the sampling fraction the motivating problem actually offers (447 of 5,576 ZCTAs, 8 percent) in two tiers: simulation recovery against a known truth, and an empirical benchmark on observed outcomes. Three findings recur across both tiers, each a failure mode routine output does not announce. First, the standard diagnostics for spatial dependence go blind at this density. Second, the Fay–Herriot intervals overstate their precision because the variance split they plug in is weakly identified. Third, estimator rankings do not transport from one surface to another, so the field's running argument about whether GeoAI beats spatial econometrics has no surface-free answer. Three further pre-stated tests (Section 5) probe the findings rather than assume them: the plug-in intervals are stress-tested against adjusted-likelihood variance estimators; the claim that a second wave would identify the variance split is tested in simulation; and the Tier 1 protocol is rerun at 4 and 16 percent sampling. The layers under test are:

A spatial-econometric small-area layer. A market-potential allocation establishes the scale of each area’s category demand. A spatial regression suite (ordinary least squares alongside spatial autoregressive, spatial error, and spatial Durbin specifications; Anselin, 1988; LeSage & Pace, 2009) models the demand rate from demographic covariates. A Fay–Herriot stage [11] shrinks noisy area-level observations toward the model, returning an estimate and interval for every ZCTA, including the roughly 92% any realistic test leaves unobserved.

A GeoAI layer. Gradient-boosted models [12] predict demand and a funnel “uptake” propensity from the same covariates, augmented with spatial features built under strict leakage controls. The layer’s role is deliberately subordinate and diagnostic: agreement with the structural estimator raises confidence; disagreement localizes where the linear-spatial specification may be failing. This follows the position, now standard in the GeoAI literature, that spatially explicit machine learning complements, not substitutes for, identified geographic models [13, 14], and parallels the absorption of machine learning into econometric practice [15] and geo-enrichment infrastructure [16].

A game-theoretic decision layer. Estimates are not decisions. Following the spatial-competition tradition from Hotelling [17] through modern location games [18], and operationalizing market share through the Huff [19] probabilistic trade-area model, the third layer simulates entry into shortlisted ZIPs against an aggregate incumbent under alternative competitor-response strategies, and applies a pre-stated decision rule (Launch, Test, or Avoid) to the payoff distributions. Its economics are stated assumptions, so it is exercised once, as a short application in Section 5.9.

A methods paper of this kind faces an evidentiary problem: the motivating application (a phased demand-testing program for consumer products sold through owned storefronts, pre-specified in a dated design note) has been designed but has not yet produced ZIP-level outcomes, and no real outcome data exist for it. Rather than fabricate an application or wait, we build the stress test in two tiers. Tier 1 is simulation recovery, a design with a long history in spatial statistics [20]: a data-generating process (DGP) with known parameters, including a spatial error process (ρ = 0.55) the estimators must detect and absorb, generates outcomes over real ACS covariates for 5,576 ZCTAs; a stratified 8% sample mimics the planned test; every layer is fit to the sample alone and graded against the known truth. Tier 2 (Sections 4.6 and 5.7) fits the same layers, on the same 447 sampled areas, to freely available observed outcomes: Census business counts, Internal Revenue Service return counts, and, new in this version, Census counts of electronic-shopping establishments, the benchmark's first fully observed e-commerce outcome, grading them on the roughly 5,100 held-out ZCTAs against concordance questions stated in advance (design note, 2026-10-18; Section 5.8). Tier 2 measures relative out-of-sample performance on real economic geography; it recovers no ground truth and validates no claim about the motivating application's markets, and we make none. The game-theory layer’s outputs under assumed costs are an illustrative application of the decision rule, reported because a decision layer never exercised cannot be evaluated even as machinery.

The design is the measurement counterpart to a claim developed elsewhere in this research program: that locations differ in their receptivity to a product or message in ways that are structured and estimable [21].

Roadmap. Section 2 reviews the literatures; Section 3 describes the data; Section 4 specifies the methods and simulation design. Section 5 reports both tiers' results, their comparison, the three stress tests, and the decision-layer application. Section 6 summarizes the Bayesian layer and its mixed verdict (full test in Online Appendix A). Sections 7 to 9 discuss implications, limitations, and conclusions. Table A gives the design at a glance.

**Table A. Design at a glance.**

| Component | What it is | Where it is graded |
| --- | --- | --- |
| Econometric layer | Spatial regression suite (ordinary least squares, spatial autoregressive, spatial error, spatial Durbin) plus a Fay–Herriot stage | Sections 5.1–5.4; Tier 1 and Tier 2 |
| GeoAI layer | Gradient-boosted audit of the econometric layer, under leakage controls | Sections 5.5–5.6; Tier 1 and Tier 2 |
| Bayesian layer (new) | Single generative count model: negative binomial likelihood, household offset, BYM2-type spatial prior fitted by a top-300 eigenvector approximation to the ICAR field, MCMC | Section 6 and Online Appendix A; Tier 1, plus Tier 2 on the electronic-shopping outcome |
| Sampling design | Stratified 8 percent sample: 447 of 5,576 ZIP Code Tabulation Areas (ZCTAs), region by income tercile | Sections 4.2, 5 |
| Tier 1 evaluation | Simulation recovery against a known data-generating process; 24 draws | Sections 5.1–5.6, 6 |
| Tier 2 evaluation | Benchmark on observed public outcomes (five evaluations, including observed electronic-shopping establishments), fitted on the same 447 areas, graded on the held-out remainder; 24 draws | Sections 5.7–5.8 |
| Decision layer | Huff contest against an aggregate incumbent; pre-stated Launch / Test / Avoid rule | Section 5.9 |
| Temporal extension (labeled) | 52-week extension testbed with two calendar moments; single replicate run of eight designed | Online Appendix A |


## 2. Related work


### 2.1 Spatial econometrics

The econometric layer descends from the spatial econometrics program of Cliff and Ord [22] and Anselin [23]: regressions in which a spatial weights matrix encodes neighbor relations and dependence enters through a spatially lagged dependent variable (the spatial autoregressive model, SAR), spatially autocorrelated errors (SEM), or both, together with lagged covariates (the spatial Durbin model, SDM). LeSage and Pace [24] supply the standard treatment, including the interpretation of SDM effects as partial derivatives, and Elhorst [25] and Halleck Vega and Elhorst [26] clarify model selection and the case for the SLX specification. LeSage [27] warns that spatial models are routinely fit without checking whether the spatial parameter is identified at the available sample scale, a warning that Section 5.1 bears out. Diagnostics follow the classical program: Moran’s [28] I on residuals, with Tobler’s [20] first law in the background, and the specification-search tradition of Anselin and Bera [29]. Computation follows Pebesma and Bivand [30].


### 2.2 Small-area estimation, and its machine-learning challengers

The Fay–Herriot model [11] is the canonical answer to the problem addressed here: noisy area-level direct estimates are modeled as a regression mean plus an area random effect, and the empirical-Bayes compromise between direct estimate and model prediction dominates either alone. Battese, Harter, and Fuller [31] give the unit-level analogue, Rao and Molina [32] the comprehensive treatment, and Pfeffermann [33] the crucial practical point that estimated, not true, variance components are what applied work must use; the coverage shortfall in Section 5.4 is partly that point made empirical. Elbers, Lanjouw, and Lanjouw [34] make the same move at household level for poverty mapping.

Machine-learning challengers now exist: mixed-effects random forests [35] and their extensions [36]. The architecture treats the challenge as a design question: Layer 2 is the nonlinear learner, run in parallel, so the comparison is performed on every run (Section 5.5). What the linear stage retains is calibrated area-level uncertainty under an explicit sampling model, which the decision layer consumes.


### 2.3 GeoAI, spatial machine learning, and validation

GeoAI, spatially explicit artificial intelligence [13, 14], has moved from bespoke spatial features toward learned location representations [37] and country-scale small-area estimates [38, 39]. Layer 2 is deliberately modest by comparison: covariate-based gradient boosting [12, 40], because the binding constraint is outcome sparsity, not feature richness, and the layer must remain interpretable against Layer 1 [41]. Conformal intervals [42] rely on exchangeability that spatial data violate [43, 44], one reason intervals here are graded against known truth.

Validation discipline matters as much as the learner. Random cross-validation inflates performance on spatially structured data [45]; block folds are the remedy [46]; spatial mapping models can fail badly under blocked validation [47]; and predictions are trustworthy only within an area of applicability [48]. Layer 2 follows these critiques by building spatial features from neighbor predictions, never neighbor outcomes, and by reporting holdout error separately from recovery against truth.


### 2.4 Gravity models, Huff shares, and location games

The decision layer's share engine is the Huff [19, 49] model: demand in an origin area patronizes a facility with probability proportional to its attractiveness discounted by resistance, normalized over competitors. It sits in the gravity lineage from Reilly [50] to Wilson [51] and shares its pathology, independence from irrelevant alternatives, which Fotheringham [52] relaxed. Recent work calibrates it with location big data [53]. Applebaum's [54] analog method is the practitioner ancestor of the whole enterprise. The strategic layer follows the location-game tradition from Hotelling [17] to the synthesis in Loertscher [18]. Modern demand estimation [55, 56, 57, 58] recovers substitution patterns far more richly than is possible here. This layer is a reduced-form descendant that uses Huff shares and Monte Carlo draws over response regimes in place of an estimated equilibrium (Section 8).

### 2.5 Advertising measurement and geo-experiments

The applied motivation rests on the advertising-measurement literature. Beyond the critiques cited in Section 1 [7, 8, 9, 10], Blake, Nosko, and Tadelis [59] show that paid-search returns were drastically overestimated by observational attribution. Shapiro, Hitsch, and Tuchman [60] show that with enough experimental variation advertising effects are estimable and heterogeneous; and Goldfarb and Tucker [61] document how the measurement environment itself reshapes measured effectiveness. Geographic experiments, which randomize exposure across areas and read outcomes by area, are therefore the credible design for generating the outcome data this architecture consumes, because they convert an identification problem into a sampling problem. The planned Phase 0 program is designed on that principle, and the simulation measures the estimators’ behavior at that design’s sampling fraction (8% of areas).

Two recent additions sharpen the stakes. Tian, Hoban, and Arora [62] show that cookie-based advertising measurement fails to measure what it claims at the individual level; the geographic analogue, developed here, is not only biased point estimates but intervals that under-cover and rankings that do not transport. Bojinov, Simchi-Levi, and Zhao [63] give the reference design for platform switchback experiments, where randomization runs in time blocks because units interfere; a geographic test is the spatial cousin, and inherits the interference problem in spatial form. Ghost ads improve measurement economics by engineering an individual-level control group [64]; a geographic design buys feasibility at the price of the diagnostic blindness and interval failure documented in Section 5. The distribution-free line has reached e-commerce directly: Han and Dai [65] build online auction design on distribution-free uncertainty quantification, though for data-rich platform auctions, not sparse geographic surfaces.


### 2.6 Electronic commerce demand: why geography still binds, and why sparsity is structural

The founding claim of electronic commerce research is that digital marketplaces cut buyer search costs [2]. The claim is correct and incomplete. Blum and Goldfarb [66] show that distance still binds online once taste differences are accounted for, so the law of gravity survives the internet. Sinai and Waldfogel [67] frame the internet as a complement to cities for some uses and a substitute for others; for a seller who fulfills physical goods, online demand is a complement to place. Forman, Goldfarb, and Greenstein [68] show that location shaped commercial internet adoption through local industry composition, which is why demand surfaces are structured rather than smooth, a fact Section 5.8 uses when it asks why rankings fail to transport. Recent evidence keeps the point current: Cui, Zhu, and Chen [69] find that offline retail density around the consumer shifts mobile shopping app usage, so the local retail environment belongs in the demand surface, not in its error term.

Sparsity is structural on the demand side, too. The long tail of online sales spreads demand thinly across products [70]; Nakano [71] shows that online grocery baskets also concentrate demand in head products, so per-place, per-product counts are small from both directions. Einav, Knoepfle, Levin, and Sundaresan [72] estimate online demand from a large platform's complete transaction data, the abundance end of the spectrum; the entrant's problem is the other end. Platform-scale choice modeling, such as Jiang, Li, and Zhang [73], likewise assumes rich clickstream data. Neither machinery nor flexibility rescues a design in which 92 percent of areas are unobserved; the binding constraint is the sampling design, not the estimator.

The seller-side analytics literature describes the same divide from inside platforms. Marketplace sellers deploy platform functions in configurations whose performance effects are estimated on platform-complete data by Zeng et al. [74]. Cold start (acting in a market before local data exist) is the platform-side name for our estimand problem: Ye, Zhang, Zhang, Zhang, Chen, and Xu [75] solve it algorithmically with platform-scale field experiments, and Liang, Hong, and Gu [76] show it is a structural feature of platform participation, not a temporary inconvenience. From the entrant's side, the 'algorithm' is a small-area estimator, and its failure mode is not slow learning but false confidence: precise-looking intervals that do not cover, and rankings that reverse on the next surface.

Targeting and location decisions presume the estimates we stress-test. Geo-conquesting presumes a firm can locate demand well enough to target by place [77]. Ghose, Goldfarb, and Han [78] show that mobile search is intensely local, which cuts both ways: locality justifies ZIP-level targeting, and it thins the demand signal per area to exactly the counts small-area estimation struggles with. Offline, Hunneman, Bijmolt, and Elhorst [79] evaluate store locations on estimated spatial heterogeneity in sales potential, using data-rich chain-retail data. Section 5.9 asks the entrant's version of their question.


## 3. Data and study areas

Geography. The units are ZIP Code Tabulation Areas (ZCTAs), the Census Bureau’s areal generalization of USPS ZIP codes. Two study regions are used. The Southeast region comprises ZCTAs whose centroids fall in eight states in the Southeast of the United States. The NYC metro region comprises ZCTAs whose centroids fall in the five New York City boroughs plus Nassau, Suffolk, and Westchester counties (New York) and Hudson, Bergen, and Essex counties (New Jersey). ZCTAs with population below 500 or households below 200 are excluded (very small and post-office-box ZCTAs produce meaningless rates), leaving 5,576 study areas: 5,057 Southeast and 519 NYC metro.

ZCTAs are an imperfect geography, used here with these limits in mind. They are not ZIP codes: they are block-aggregated approximations that the Census Bureau itself warns change between censuses; they inherit the modifiable areal unit problem in full [80]; and ZIP- and ZCTA-based analyses can mislead when the areal fiction is forgotten [81, 82]. The defense is pragmatic: the decisions this machinery feeds (advertising targeting, market entry) are denominated in postal geography by the platforms and carriers that execute them, so estimates must be produced in that geography even though inference about underlying social processes would prefer another. Section 8 returns to the consequences.

Covariates. All covariates come from the American Community Survey (ACS) 5-year estimates, vintage 2023 [83], joined from tables B01002 (median age), B01003 (population), B19001 (household income distribution), B19013 (median household income), B25001 (housing units), B25003 (tenure), B25004 (vacancy), B25010 (household size), and B25024 (units in structure). One reproducibility detail: the Census API now requires a personal key, so the pipeline reads the identical published estimates from the Bureau’s official table-based summary files (the same source from which the API serves) and caches them, making the full run reproducible offline from declared inputs. Derived features (the model matrix, standardized) are: log median household income; share of households with income ≥ $100,000; renter share of occupied units; seasonal/recreational vacancy share; single-family share of structures; large-building (20+ unit) share of structures; average household size; median age; and log population density, with density computed from 2023 Gazetteer land areas and centroids. Fifty-four ZCTAs lack a median income; these are median-imputed within region and counted in the run log. Spatial weights are k-nearest-neighbor (k = 6) on Gazetteer centroids, row-standardized.

Products. Two products from the demand-test slate are carried through Layers 1–2 to demonstrate product-conditional demand: a shower-steamer pack (list price $13.99) whose hypothesized fit is renter-occupied, small-bathroom housing, and a three-product bundle (“the Trio,” $39.99) whose hypothesized fit is owner-occupied family housing. The game-theory layer runs on the steamers product. All economic magnitudes attached to the products (margins, basket values, acquisition-cost benchmarks) are stated assumptions, collected in Sections 4.1 and 4.5. They are parameters of the exercise, not measurements.


## 4. Methods


### 4.1 Market-potential allocation

Layer 1 begins with scale. Regional category expenditure is fixed by assumption at $120 per household per year for the bath/body consumables category (a round number in the plausible range of Bureau of Labor Statistics Consumer Expenditure Survey personal-care spending per consumer unit [84]) and is allocated to ZCTAs within each region by shares

si = HHi · exp(w′Zi) / Σj HHj · exp(w′Zj),

where HH is households, Z the standardized covariates, and w a documented allocation weight vector (positive on income and household scale, product-conditional on tenure and structure). Shares sum to one within region by construction. The allocation is not an estimate of demand; it is the denominator discipline that forces every downstream quantity to respect regional totals, in the spirit of the analog tradition [54].


### 4.2 Simulation design (the data-generating process)

In the absence of real outcomes, the observed sample is generated from a known DGP over the real covariates. For product p, the true log order rate per household per year is

log λi = αp + Xi βp + ui, u ~ SAR(ρ = 0.55, σ = 0.45),

where Xi is the standardized covariate vector with elements clipped at |z| = 2.5 in the DGP only, so that the demand response saturates in extreme tails (unclipped, the extreme Manhattan z-scores would imply implausibly large true rates; estimators see the unclipped covariates and must cope with the tails, as they would in reality). Observed orders in sampled areas are Negative Binomial with mean HHi·λi and size 6.0; observed sessions are Poisson at 0.06 sessions per household; observed add-to-carts are Binomial in sessions with a logistic true uptake (intercept −3.35, a baseline session-to-cart propensity of about 3.4%). The sample is 8% of ZCTAs, stratified by region × income tercile, mimicking the planned Phase 0 test design. Table 1 gives the product coefficient vectors. The simulation is fully deterministic given seed 20261013.

*[Insert Table 1 about here]*


### 4.3 Econometric estimators and the Fay–Herriot stage

On the sampled areas, the observed log order rate is regressed on the (unclipped) covariates under four specifications: OLS; SAR and SEM by maximum likelihood; and SDM by maximum likelihood with spatially lagged covariates, using hand-implemented numpy/scipy likelihoods (the replication environment lacks the standard spatial-econometrics packages). Model choice is by AIC, following the selection practice in Elhorst [25]. Coefficient covariance matrices for SAR/SDM use the standard transformed-OLS approximation rather than the full ML Hessian, a disclosed simplification (Section 8). Moran’s I [28] on OLS residuals is reported as a diagnostic, with the caveat, confirmed in the results, that at an 8% sampling fraction the test is low-powered, because each sampled area’s observed rate carries substantial count noise that attenuates the statistic even when the underlying error process is strongly spatial.

The Fay–Herriot stage treats each sampled area’s observed log rate as a direct estimate of a latent area value θi = xi′β + ui, with ui ~ N(0, σ²u) and sampling error variance ψi derived from the count model. The sampling variances come from a joint maximum-likelihood fit (Negative Binomial size and lognormal area-effect variance estimated together by Gauss–Hermite quadrature on the sample counts) rather than from plug-in moments, which confound the two variance components. The shrinkage weight is γi = σ²u/(σ²u + ψi); sampled areas receive the empirical-Bayes blend, unsampled areas the model prediction, and all areas receive intervals from the blended variance. This is the classical construction of Fay and Herriot [11] and Rao and Molina [32], with the sampling side adapted to counts. Its central difficulty, which the results illustrate, is that the split between count overdispersion (NegBin size) and genuine area variance (σ²u) is only weakly identified from a single cross-section: the profile likelihood is nearly flat across the plausible region, and ψ inherits the reciprocals of the estimated size. We report this identification caveat as a finding, not a footnote.


### 4.4 GeoAI design

Layer 2 fits gradient-boosted regressors [12] for two targets: the log order rate (demand) and the uptake propensity (session-to-cart probability). Quantile fits provide intervals. The design constraints are the substance:

Leakage control. Spatial features are neighbor means of covariates and of Layer 1 model predictions, never of neighbor outcomes. Using observed neighbor outcomes as features would leak the answer in-sample and be unavailable for unsampled areas in deployment; the spatial cross-validation literature [45, 46] identifies exactly this failure mode. Predicted-neighbor features are computed by cross-fitting so that no area’s own outcome informs its own feature vector.

Evaluation at two levels. A random holdout within the sample (reported for comparability with standard practice, and labeled as optimistic under spatial structure) and, available only in the simulation design, recovery against the known true surface on all 5,576 areas.

Agreement analysis. Layer 2 predictions are compared to Layer 1 estimates by Pearson and Spearman correlation and top-decile overlap, per the architecture’s diagnostic intent.

Clustering. ZCTAs are clustered by k-means on standardized features, with a geographic-coherence check (the mean share of a ZCTA’s k-nearest neighbors assigned to its own cluster), so clusters can serve as planning units at either pure segments or coherent territories, with the trade-off measured rather than assumed.


### 4.5 The game-theory layer

The decision layer is specified here and exercised once, as a short application, in Section 5.9. The shortlist is the top 25 ZCTAs per region by the average of Layer 1 and Layer 2 percentile ranks for the steamers product. In each shortlisted ZCTA, entry is modeled as a Huff [19] contest between the entrant and an aggregate incumbent whose intensity index is an ACS-covariate proxy (density, large-building share, high-income share), explicitly a stand-in for competitive presence, not a measurement of competitor locations or prices, which the ACS cannot see.

Competitor behavior is simulated over three response strategies, parameterized as multipliers on the contest (Appendix Table A1): no response, moderate (promotion plus advertising escalation), and aggressive (matching plus assortment expansion). The probability that a ZCTA's incumbent escalates (moderate or aggressive, with 40% of escalations aggressive) rises with the incumbent-intensity index through a logistic map (intercept −0.40, slope 0.90). Per-ZIP payoffs over a one-year horizon combine four components. The first is reachable demand (35% of modeled product demand in year 1, an assumption). The second is Huff share under the drawn response. The third is per-order contribution from assumed economics (for the steamers, an assumed basket average order value of $31.00 at a 55% contribution margin, i.e., a median per-order contribution of $17.05) against acquisition cost per customer implied by benchmark funnel economics (Meta Reels cost per click $0.70–$1.10, landing-to-cart conversion 4–8%, cart-to-order 35% by assumption), spread over 2.2 assumed year-1 orders per acquired customer, plus a $200 per-ZIP fixed setup cost. Each ZIP receives 500 Monte Carlo draws (seed-fixed), yielding win rate (share of draws with positive payoff), payoff percentiles, and share percentiles. The decision rule is fixed in advance and printed with the results:

Launch if win rate ≥ 70% and the 10th-percentile payoff exceeds $0; Test if win rate is 40–70%; Avoid otherwise.

*[Insert Appendix Table A1 about here]*

### 4.6 Tier 2: an empirical benchmark on observed outcomes

Tier 1 validates recovery against a known truth, but the truth it knows is one we wrote. A reader is entitled to ask what the machinery does on real economic geography, whose surfaces differ in level and local structure and whose outcomes arrive with their own measurement error. Tier 2 answers that narrower question empirically: it is the standard second half of validation in the small-area literature (a simulation study paired with an empirical application). It is a benchmark of the machinery on observed outcomes, never a market validation of the demand test the architecture was built for: the outcomes below are observed economic mass at ZIP level, not observed demand for any product. The game layer has no observed analogue and is not benchmarked here; nor is GeoAI's uptake target (Section 4.4), which no public dataset records. What Tier 2 tests is the estimation core: Layers 1 and 2, their agreement, and their interval and diagnostic behavior, on real outcomes.

The outcomes are four freely available ZIP-level series for 2022, each expressed as a rate per household over the same 5,576 study ZCTAs with the same American Community Survey covariates as Tier 1: (i) total establishments per household from ZIP Code Business Patterns [85], the closest public analogue of the architecture's intended subject, business presence; (ii) individual income tax returns per household from the IRS Statistics of Income ZIP Code Data [86], observed economic mass in taxpayer form; (iii) returns reporting business or professional net income (SOI field N00900) per household, the taxpayer-side counterpart of the business count; and (iv) electronic-shopping establishments per household, counts of NAICS 454110 (electronic shopping and mail-order houses) establishments from the ZBP 2022 detail file, added in this version. The fourth series is the benchmark's first fully observed e-commerce outcome: observed Census counts of electronic-shopping presence. It is not seller sales, not transactions, and not demand for any product, and it is interpreted as establishment presence only. It is also sparse and discrete by construction: 68.0 percent of study ZCTAs record zero such establishments (1,712 of 5,576 have at least one; 14,620 in total; a further 74 ZCTAs have no ZBP record at all and are excluded from grading), and a ZCTA with no 454110 row in the detail file is an observed zero, not a missing value. The estimation design mirrors Tier 1 exactly: the layers are fitted only on the 447 originally sampled ZCTAs (8 percent) and graded on the held-out remainder (24-draw mean 5,061 graded ZCTAs), on the log-rate scale. The pre-stated metrics are root mean squared error, Spearman correlation, and top-decile overlap with the observed ranking. A temporal transfer repeats the exercise fitting 2019 business counts and grading their 2022 counterparts, for five evaluations in total. Three concordance questions were stated in advance of the Tier 2 analysis (design note, 2026-10-18), before any Tier 2 fit was run: (a) do the layer rankings agree across tiers (in Tier 1, Layer 1 beats GeoAI on point prediction while GeoAI recovers the uptake share nearly exactly)? (b) does interval behavior on real data echo Tier 1's Fay–Herriot under-coverage? and (c) do the simulation's diagnostic failure modes have observable analogues in the real-data diagnostics? Section 5.8 answers each in turn, reporting disagreement where it occurs, because disagreement locates the simulation assumptions that fail to transport.


## 5. Results

Sections 5.1–5.6 report Tier 1: simulation-recovery results, estimates fit to the simulated 8% sample and graded against the known DGP truth on all 5,576 ZCTAs. Section 5.7 reports Tier 2, the empirical benchmark on observed outcomes, and Section 5.8 compares the tiers. Both tiers measure the machinery; neither is a claim about real demand for the motivating products in any place.

Read this section as three failure modes of the analytics e-commerce uses, in the order a practitioner meets them. First, the diagnostics fail: Moran's I and the Lagrange multiplier (LM) tests detect a strong spatial process (true autoregressive parameter 0.55 in every draw) in only 17–42 percent of draws at the 8 percent sample. Second, the intervals fail: nominal 95 percent Fay–Herriot intervals cover the truth on sampled areas in only 88.5 percent (steamers) and 87.6 percent (trio) on average across 24 draws, because the split between count noise and area variation is weakly identified in one cross-section. Third, the rankings fail: the estimator ordering that is unambiguous in simulation dissolves on real surfaces into a near-tie (Section 5.8). None of the three announces itself in routine output; each subsection states its pattern first and leaves cell-level detail in the tables.


### 5.1 Diagnostics and model choice

For the steamers product, Moran’s I on the OLS residuals is 0.062 with a permutation p-value of 0.541, a null diagnostic, even though the DGP error process is strongly spatial (ρ = 0.55). For the Trio, Moran’s I is 0.354 (p = 0.003). The contrast is itself a result: at an 8% sampling fraction, each sampled area’s observed rate is dominated by count noise (mean sampled-area session exposure is small), and that noise attenuates the residual autocorrelation statistic toward zero in the steamers DGP, whose covariate signal concentrates in high-variance urban covariates. A practitioner who screened for spatial structure with Moran’s I at this sampling density and stopped at the steamers null would discard the spatial models out of hand, and for steamers the fit criteria barely rescue them. With all four likelihoods computed on the common maximum-likelihood basis of Table 2, AIC selects the SAR specification (956.7) over OLS (958.3) by 1.6 points, a margin conventionally read as a tie, and the SEM (959.9) and the SDM (967.3) both trail OLS. For the Trio the criteria speak clearly: AIC selects the SEM (1,047.5) over OLS (1,058.7) by 11.2 points, the SAR (1,059.3) is level with OLS, and the SDM (1,068.3) is last. The argument that fit criteria prefer spatial models the diagnostics would discard therefore holds for one product only, and we rest nothing on it for steamers. LeSage’s [27] caution about identification at available sample scales cuts both ways: diagnostics under-reject, and, as the fitted spatial parameters show, the spatial parameters themselves are weakly recovered. The SAR ρ̂ for steamers is −0.025 and the SEM λ̂ is 0.045, both near zero against a true ρ of 0.55; for the Trio the SEM λ̂ is 0.211. The likelihood improves, but the spatial parameter does not travel to its true value. A reasonable reading is that a single 8% cross-section identifies that spatial structure helps prediction more readily than it identifies the spatial process itself, a distinction the simulation design exists to expose.

Would a sharper residual test have caught what Moran's I missed? Across the 24 fresh DGP draws of Section 5.4, the Lagrange multiplier tests of Anselin, Bera, Florax, and Yoon [87] perform no better: LM-error rejects at the 5 percent level in 17% of steamers draws and 42% of trio draws, against Moran rejection rates of 17% and 38%. Conditional on Moran's I missing, LM-error catches the process in 0% (steamers) and 4% (trio) of draws; LM-lag, aimed at the DGP's actual lag form, rejects in only 4% of draws for both products. The tests themselves are sound (in validation worlds they hold their size and reject at full data density). The conclusion is about power, not test choice: at an 8 percent sample, no standard residual diagnostic reliably sees a ρ = 0.55 spatial process, and specification choice must rest on fit criteria and theory.

*[Insert Table 2 about here]*


### 5.2 Coefficient recovery

Table 3 reports sample estimates against DGP truth. Recovery is close for most terms in both products: intercepts are recovered within 0.10; the steamers’ signature renter share coefficient (truth +0.48) is estimated at 0.38–0.40 across specifications; the Trio’s single-family coefficient (truth +0.40) at 0.37–0.38. The systematic pattern is attenuation of the urban-form coefficients (steamers large-building share, truth +0.38, is estimated at +0.19 by every specification, and Trio renter share (−0.38) at −0.21 to −0.23) and one conspicuous overshoot: Trio share of households with income of $100k or more, truth +0.25, is estimated at +0.43 to +0.45. The attenuation has a mechanical cause the design anticipated: the DGP clips covariates at |z| = 2.5 while estimators use unclipped values, so in the extreme urban tails the fitted linear response is dragged toward the saturated truth. This is not a simulation artifact; it is the standard situation of a linear specification meeting a saturating response, reproduced here under controlled conditions, and it is one of the two places (Section 5.5 is the other) where the architecture’s layering earns its keep.

*[Insert Table 3 about here]*

Steamers

Trio


### 5.3 Prediction recovery and the Fay–Herriot improvement

Prediction recovery on all ZCTAs (log-rate scale) is summarized in Table 4. For steamers, RMSE moves from 0.514 (OLS) to 0.518 (best spatial model) to 0.512 (after Fay–Herriot shrinkage). The spatial model does not improve point prediction despite its AIC advantage, and the shrinkage stage contributes the entire net gain, small in absolute terms, but achieved exactly where Fay–Herriot theory says it should be, by discounting noisy direct estimates (mean shrinkage weight γ = 0.27 for steamers). For the Trio, the progression is monotone: 0.538 (OLS) to 0.535 (SEM) to 0.529 (Fay–Herriot), with a much higher mean shrinkage weight (γ = 0.77) and larger estimated area variance (σ²u = 0.439 vs. 0.125). The contrast between products shows that the value of the spatial and shrinkage machinery is itself product-conditional, depending on how much of the true surface the covariates miss.

*[Insert Table 4 about here]*


### 5.4 Interval coverage and the weakly identified variance split

The coverage results are the study’s most consequential output, and they show under-coverage where it matters. We lead with the 24-draw means, because no single sample can carry this comparison. Averaged over the 24 draws, nominal 95% Fay–Herriot intervals cover the truth on 88.5 percent (steamers) and 87.6 percent (trio) of sampled areas, against the 95 percent nominal level. Coverage over all areas is higher, at 93.1 percent and 96.0 percent, because unsampled areas receive the wider model-based intervals. The canonical single run used for illustration in Sections 5.1 to 5.3 is not representative of those means. It sits at the pessimistic end for steamers (83.7 percent over all areas, 83.9 percent on sampled areas), and it over-covers for the Trio overall (97.4 percent) while under-covering on the Trio’s sampled areas (82.8 percent). We report its mechanism next because it is identified in that run’s own calibration analysis, but the draw means are the estimates. The decomposition of count variation into Negative Binomial overdispersion (size) and genuine area variance (σ²u) is weakly identified from a single cross-section (the likelihood is nearly flat across the plausible region, ΔlogLik ≈ 3–11), and the two products land on opposite sides of it. In the canonical run, the steamers size is estimated at 3.7 against a true 6.0 (overdispersion overstated, ψ understated, intervals too narrow). The Trio’s size is estimated at 55.3 against the same true 6.0 (overdispersion effectively denied, area variance overstated at σ²u = 0.439, unsampled-area intervals too wide while sampled-area intervals, which lean on ψ, run narrow). Pfeffermann’s [33] insistence that applied small-area work must live with estimated variance components is usually read as a technicality; here it determines whether intervals reach their nominal coverage. The design implication is direct and is carried into Section 7: a second test wave, or split-window replication within a wave, should identify the (size, σ²u) split directly, a claim we test in simulation at the end of this section; until such data exist, the intervals should be consumed as approximate. The decision layer in Section 5.9 therefore keys its rule to payoff distributions and win rates rather than to Layer 1 interval bounds.

Under-coverage invites an obvious follow-up: can the intervals be repaired? We assess a parametric-bootstrap calibration inside the simulation framework, in the spirit of Prasad and Rao [88], with the multiple-draw robustness checks of Hall and Maiti [89]. For each of 24 fresh DGP draws (both products), the fitted model generates 25 bootstrap worlds; in each world the Fay–Herriot estimator is re-run and the ratio of absolute error to nominal half-width recorded. The sample intervals are then widened by the pooled 95th percentile of that ratio, a multiplier estimated from the fitted model alone, with the truth never consulted. The multipliers average 1.119 (steamers) and 1.107 (trio). Calibration helps, honestly and incompletely. Averaged over draws, all-area coverage rises from 93.1% to 95.3% (steamers) and from 96.0% to 97.5% (trio), at or past nominal. On the sampled areas that motivate the design, coverage rises only from 88.5% to 91.4% (steamers) and 87.6% to 90.0% (trio), still short of 95 percent, and draw-to-draw dispersion stays wide (standard deviations of five to six points). The bootstrap worlds themselves explain the residual gap: inside them, nominal intervals cover only 92.5%–92.8% of the time, because the worlds are generated from the same weakly identified variance split that caused the problem. The estimated negative binomial size averages 14.8 (steamers) and 24.7 (trio) against a true 6.0, with standard deviations nearly as large as the means. Calibration is therefore reported as a partial remedy with a named cause, not a fix: it repairs the all-area average and narrows nothing about the identification problem itself, which only a second wave of outcomes can resolve (Section 8).

A second candidate repair is a better variance estimator. Li and Lahiri [90] and Yoshimori and Lahiri [91] propose adjusted maximum likelihood (AML) estimators of the Fay–Herriot area variance, built to avoid the boundary pathology (a zero estimate of σ²u) of maximum-likelihood-type estimators, which collapses the shrinkage and the intervals built on it. We stress-tested the plug-in against both, holding every other element of the shipped construction fixed and replacing only σ²u (24 draws, both products). No estimator, including plain profile maximum likelihood, returns a boundary zero in any of the 48 draw-product cells, and sampled-area coverage moves by at most 0.004 (steamers: 0.885 shipped, 0.889 under Li and Lahiri [90]; trio: 0.889 shipped, 0.890). A textbook area-level refit tells the same story (coverage 0.862 to 0.871 across ML, REML, and both AML variants). The pre-stated criteria for the AML estimators (strict positivity in all draws; coverage at least as close to nominal as the plug-in) are formally met, and substantively empty: with 447 sampled areas, the pathology that literature treats does not arise in this design, and the under-coverage is not a boundary-estimate problem. On the Tier 2 evaluations the shipped construction is likewise closest to nominal most often, with one exception taken up in Section 5.8: on the sparse electronic-shopping outcome the shipped fit's σ²u collapses (draw mean 0.028) and the Li–Lahiri estimator's intervals behave best (0.654, closest to nominal in all 24 draws), though still far from 0.95. What is new relative to that literature is the location of the failure. The AML guarantees concern the area-level model with known sampling variances and a GLS-profiled regression; this construction estimates the sampling variances themselves from a count-based joint fit, and the failure sits in that ψ channel, and on one sparse real outcome in a collapsed σ²u, neither of which an adjustment to the area-level likelihood reaches.

The remaining candidate is more data of the right kind. Sections 5.4, 7, and 8 state that a second test wave would identify the (size, σ²u) split directly, because repeated counts per area separate count noise, which is independent across waves, from the shared area effect. We tested that claim in simulation, on the same 24 draws and both products: wave 2 counts are fresh Negative Binomial draws at the sampled areas from the same true rates, and the shipped joint model is refit pooling both waves over a shared area effect. All three pre-stated components moved the right way, for both products. Size recovery improves by an order of magnitude (mean |log(size-hat/6.0)| falls from 0.848 to 0.073 for steamers and from 1.082 to 0.093 for trio). The likelihood ridge sharpens roughly tenfold (the mean log-likelihood cost of fixing size at half or twice its fitted value rises from 2.9 to 28.3 for steamers and from 1.9 to 24.6 for trio). And nominal 95 percent intervals built from the pooled split cover the wave-2 sampled areas at 0.941 (steamers) and 0.942 (trio), against 0.889 and 0.885 under the wave-1 split. The claim is therefore supported as stated, with two bounds kept attached: the test is a simulation inside this paper's own data-generating process, so it shows the design identifies the split when the model is right, not that a real second wave would be so clean; and pooled coverage, at 0.94, remains about a point short of nominal, so identifying the split removes most, not all, of the sampled-area shortfall.

**Sampling fractions.** The Tier 1 protocol rerun at 4 and 16 percent sampling (24 draws each, with the shipped 8 percent results between them) shows how the pathologies scale. Raw sampled-area coverage is flat from 4 to 8 percent (steamers 0.885 at both fractions; trio 0.897 and 0.876) and improves at 16 percent (0.916 and 0.910), still some four points short of nominal; bootstrap calibration lifts each fraction by two to three points and comes closest to nominal only at 16 percent (0.948 and 0.938). The fitted size-hat shrinks toward the truth of 6 as the fraction grows (steamers: 24.2 at 4 percent, 14.8 at 8, 9.7 at 16) without reaching it, and the calibration multiplier stays in a narrow band (1.11 to 1.15) at every fraction. Diagnostic power rises with the fraction, as it must: Moran's I rejects in 8 percent of steamers draws at 4 percent sampling, 17 percent at 8, and 46 percent at 16, and still misses the process in over half of draws at the largest fraction. The pathologies attenuate with sample size but do not vanish at twice the design fraction; the 8 percent design point is not a knife edge. (The protocol's replicate function returns coverage, multiplier, and diagnostic outputs but no RMSEs, so no RMSE-by-fraction is reported.)


### 5.5 The GeoAI layer: agreement without superiority

Layer 2’s boosted models reach holdout RMSE (within the sample, log-rate) of 0.752 for steamers and 0.848 for the Trio, numbers that look poor until placed beside their proper benchmark, recovery against truth on all areas: 0.606 and 0.665 respectively, worse than Layer 1’s post-shrinkage 0.512 and 0.529. Uptake, by contrast, is recovered almost exactly (RMSE 0.009 on the probability scale for both products), unsurprising, since the uptake DGP is a smooth logistic in the same covariates the booster sees. The demand result runs against the grain of GeoAI advocacy: on a DGP whose mean structure is linear-plus-spatial-error, a flexible learner trained on 8% of areas cannot beat a correctly specified spatial model with shrinkage, and its deficit is the price of variance in sparse tails, not a coding failure, precisely the outcome the spatial-validation literature predicts [45, 47]. The architecture’s answer is the agreement analysis: Pearson correlations between layers of 0.941 (steamers) and 0.927 (Trio), Spearman 0.888 and 0.912, and top-decile overlaps of 87% and 86%. Where a decision depends only on ranking the best areas, the shortlist construction in Section 5.9, the two layers concur almost completely, and the residual disagreement is a mapped diagnostic (Figure 3), not a hidden risk. Permutation importances expose the different internal logics productively: for steamers the booster leans on large-building share (0.234), renter share (0.133), and single-family share (0.086) (the same urban-form block whose linear coefficients attenuated in Table 3) while for the Trio it leans on renter share (0.405, sign-flipped relative to steamers in effect) and the ≥$100k income share (0.277). Neighbor-covariate features contribute modestly (largest 0.020), consistent with the leakage controls doing their intended work of keeping the spatial lift honest.


### 5.6 Clusters as planning units

Clustering the ZCTAs on standardized features yields 17 Southeast clusters with mean geographic coherence 0.25 and 12 NYC-metro clusters with coherence 0.42. The metro’s clusters are substantially more place-like, a mechanical consequence of the region’s sharper spatial sorting. The planning content is in the contrasts: the Southeast’s largest-order cluster (cluster 15: 185 ZCTAs, 2.23M households, 123,508 expected orders) is a high-renter (0.61), moderate-income ($50,821) segment. Cluster 9, with a quarter of the households (626,261), nearly matches its orders (122,419) at higher uptake (0.077) and income ($81,329), the kind of efficiency contrast a media planner can act on. In the metro, cluster 7 pairs the highest uptake in either region (0.124) with the highest mean income ($158,999) across 37 ZCTAs. These are descriptions of the fitted surface over real covariate geography, valid as machinery outputs, not market findings.

*[Insert Appendix Table A2 about here]*

Figures 1 and 2 map the Layer 2 (GeoAI) predicted demand for steamers in the NYC metro and Southeast regions respectively.

*[Insert Figure 1 about here]*

*[Insert Figure 2 about here]*

*[Insert Figure 3 about here]*


### 5.7 Tier 2 results: the estimators on observed outcomes

Table 5 reports the benchmark; Figures 5 and 6 set it beside Tier 1. Every Tier 2 number in this section is an average over 24 sample draws (the same 24 draws used for the Tier 1 calibration study (Section 5.4), with the real outcomes held fixed), because a single 8 percent sample cannot carry the comparison alone. The Tier 1 ordering does not transport. On the business-count outcome, out-of-sample RMSE (log-rate scale, roughly 5,100 held-out ZCTAs per draw) averages 0.517 ± 0.005 for OLS, 0.518 ± 0.006 for the best spatial model (SEM in 71 percent of draws) and 0.518 ± 0.006 after Fay–Herriot shrinkage, against 0.505 ± 0.006 for GeoAI. The layer that finishes last in Tier 1 is modestly more accurate here, in every one of the 24 draws. The same pattern holds for SOI returns per household (Fay–Herriot 0.215 ± 0.002, GeoAI 0.208 ± 0.004; GeoAI better in 92 percent of draws). The same pattern holds for the 2019-to-2022 temporal transfer (0.523 ± 0.007 versus 0.511 ± 0.007; 96 percent of draws). On SOI business returns per household the layers are tied (0.758 ± 0.013 versus 0.751 ± 0.013, GeoAI better in only 62 percent of draws, a margin inside its draw-to-draw spread).

The fifth evaluation, added in this version, is the benchmark's first fully observed e-commerce outcome: electronic-shopping establishments per household (NAICS 454110, ZBP 2022 detail), graded on the identical protocol. The pre-stated question was whether the GeoAI-versus-Fay–Herriot ordering found on the other real outcomes repeats here. It does, in every one of the 24 draws, and by the widest margin of any evaluation: held-out RMSE averages 1.010 ± 0.008 (OLS), 1.012 ± 0.013 (best spatial model; SEM in 67 percent of draws, SAR in 33 percent) and 1.012 ± 0.013 after Fay–Herriot shrinkage, against 0.944 ± 0.009 for GeoAI, a mean paired margin of 0.068. The levels are not comparable to the other outcomes (the log-rate target is dominated by the outcome's 68.0 percent zeros, and shrinkage is nearly absent, with mean γ = 0.02, because the joint fit's σ²u collapses on this outcome; Section 5.4); the ordering is the content. On ranking quality the gap is wider than anywhere else in the benchmark: Spearman correlation with the observed ranking is 0.501 ± 0.013 for GeoAI against 0.280 ± 0.018 for Fay–Herriot, and top-decile overlap is 0.306 ± 0.021 against 0.272 ± 0.020. The outcome measures observed establishment presence only, not sales or transactions, and nothing in this paragraph should be read as demand for any product. Two cautions keep the finding in proportion. First, outside this outcome the margins are small, one to three percent, and the spatial and shrinkage stages add essentially nothing over OLS for real point prediction: the three econometric columns agree within 0.004 RMSE on every evaluation, as they must in part, because for held-out areas the Fay–Herriot point estimate is the selected model's prediction. Shrinkage acts on the sampled areas and on interval width, not on held-out point forecasts. Second, on ranking quality GeoAI leads on top-decile overlap with the observed ranking on all five evaluations (for business counts, draw-mean overlap 0.45 against Fay–Herriot's 0.41) and on Spearman correlation in four of five (returns are the exception: 0.60 for Fay–Herriot against 0.59 for GeoAI). This extends the pattern Tier 1 found for the uptake target, where the flexible learner's rankings were always its strength.

The layers also agree with each other far less on real geography than on simulated geography. Across draws, Fay–Herriot and GeoAI top-decile agreement averages between 50 and 52 percent on the first four real outcomes, and falls to 29.8 percent on the electronic-shopping outcome, against the 86–87 percent of Tier 1: on real geography, half to two-thirds of each layer's top decile is not in the other's. Diagnostics tell a two-density story, and we report both densities explicitly, because the two are easily conflated. At the 8 percent sample the architecture is designed around, the real-data diagnostics already reject: on the canonical sample, Moran's I on the OLS residuals is 0.300 (permutation p = 0.005) for business counts, 0.370 (p = 0.001) for returns, and 0.213 (p = 0.034) for business returns. LM-error rejects for all three outcomes (p ≤ 0.038), while LM-lag never does (smallest p = 0.057). The simulated blindness of Section 5.1 does not recur on these outcomes, whose dependence is strong enough to see at the design's sampling fraction. Fitted instead to every ZCTA with an observed outcome (n = 5,502–5,511), the same diagnostics are overwhelming (Moran's I of 0.148, 0.229, and 0.218, permutation p = 0.001 for all three; both plain LM tests reject at p < 1e-74), but the robust LM forms do not speak with one voice on the form of dependence: they favor the error form for business counts (robust LM-lag p = 0.058), reject in both forms for returns, and favor the lag form for business returns (robust LM-error p = 0.907, robust LM-lag p < 1e-25). AIC on the sampled fits selects the error model (SEM) in the large majority of draws for every outcome. Interval behavior is taken up with the tier comparison, where it belongs.

*[Insert Table 5 about here]*

*[Insert Figure 4 about here]*


### 5.8 The two tiers compared

(a) Layer rankings: the tiers disagree, with a qualification. Tier 1's ordering (Layer 1 first, GeoAI last on point prediction by a wide margin (canonical steamers RMSE 0.512 versus 0.606; across eight fresh draws, Fay–Herriot 0.539 ± 0.015 versus GeoAI 0.647 ± 0.022)) does not survive contact with the observed outcomes, where GeoAI is modestly better on four of five evaluations and tied on the fifth (Section 5.7). Why the ordering flips is answered only in part, and we separate what is measured from what is hypothesized. Measured: the surfaces differ in spatial structure. Moran's I of the surface itself is 0.70 (steamers truth) and 0.49 (trio truth), against 0.39, 0.40, and 0.30 for the three observed 2022 log-rate surfaces; and the short-lag semivariance ratio (under-15-km semivariance as a fraction of total variance) is 0.63 for the simulated steamers surface against 0.95 for the observed business-count surface. The real surfaces are rougher at local scale. Hypothesized, and tested with a negative result: that this local roughness is what rewards the boosted trees. Augmenting the DGP with an independent local component matched in scale to its smooth spatial error (surface Moran's I 0.61; short-lag ratio 0.68) does not move the ordering toward GeoAI across eight draws; the deficit widens (Fay–Herriot 0.723 ± 0.013, GeoAI 0.842 ± 0.014). Local roughness of that form is therefore not the mechanism. The remaining candidate is functional form: the DGP is linear in the covariates by construction, so in Tier 1 the flexible learner has no structure to exploit that the parametric layer lacks, while nothing constrains the real outcomes to be linear in the same covariates. What transports is narrower and more useful than either ordering: GeoAI's rankings were dependable in both tiers, and the econometric layers' point predictions on real data are indistinguishable from OLS. The architecture's real-data value sits in its intervals, its diagnostics, and the layer comparison itself.

(b) Interval behavior: the tiers disagree once the comparison is made like for like. Tier 2 grades intervals on held-out, unsampled areas, so the Tier 1 comparator is coverage over all areas, not sampled-area coverage. On that basis: across the 24 draws, Tier 2 behavior averages 90.3 ± 4.6% for business counts, 86.8 ± 1.3% for returns, 94.7 ± 1.8% for business returns, and 91.7 ± 3.9% in the temporal transfer, against Tier 1 all-area raw coverage averaging 93.1% (steamers) and 96.0% (trio). Real-data behavior is therefore at or below the simulation's like-for-like level, materially worse for returns, somewhat worse for business counts and the transfer, and near nominal only for business returns. The electronic-shopping outcome sits outside this pattern: behavior averages 29.6 ± 6.5%, because on that sparse count target the shipped fit's σ²u collapses and the intervals shrink toward the model prediction (Section 5.4, where the AML panel shows a likelihood-based area variance behaving better, at 0.654, without reaching nominal). The comparison remains behavioral, not exact: the Tier 2 target is itself an estimate (ZBP counts carry disclosure-avoidance noise and SOI values are rounded), so part of any shortfall is target noise rather than interval width. Read together with Section 5.4, the defensible conclusion is the weaker one: nothing in the real-data behavior contradicts the simulation's diagnosis (a weakly identified variance split yielding intervals narrower than the uncertainty warrants), and the calibration of Section 5.4 should be applied whenever these intervals are reported. The stronger claim that the two tiers' interval behavior 'echoes' is not supported on the like-for-like comparison and is withdrawn.

(c) Diagnostics: the failure mode is a property of the simulated design at its fitted strength, and the real data bound it from the other side. In Tier 1, Moran's I rejects in 17% (steamers) and 38% (trio) of draws at the 8 percent sample, and LM tests do no better (Section 5.1). On the real outcomes the same tests reject even at the 8 percent sample and are overwhelming at full density (Section 5.7). The analogue a user should carry forward is therefore narrower than the simulation alone suggests: sparse-sample diagnostic blindness is real for the simulated process, but the observed outcomes' dependence is strong enough to detect at the design's own sampling fraction, so a quiet Moran's I on real test data at this design should be read as weak dependence rather than assumed to be a power failure. What survives at neither density is form discrimination from the plain LM pair, so specification choice must rest on fit criteria and theory.

*[Insert Table 6 about here]*

*[Insert Figure 5 about here]*

*[Insert Figure 6 about here]*


### 5.9 Application: the entry decision under stated, assumed economics

We report this section as an application of the decision layer under stated, assumed economics. It is not an empirical finding about any real market, and we do not present it as a headline result. Under the assumptions of Section 4.5, all 50 shortlisted ZCTAs (the top 25 per region) receive the decision Avoid. No shortlisted ZCTA in either region clears even the Test bar of the pre-stated rule. Win rates span 0–9 percent (4–9 percent for the top five per region, Table 7). The binding constraint is unit economics, not geography: the median per-order contribution is $17.05, while the benchmark acquisition cost per customer, spread over the assumed 2.2 first-year orders per customer, runs higher before any competitor response is applied. At the stated prices, margins, and acquisition benchmarks, a $13.99 product cannot buy its way into any of the 50 best ZIP codes on the map.

We grid the assumed economics before interpreting the verdict (full grid in the replication archive). The first flips appear at $25.58 per order (1.5 times the assumption), where 9 of the 50 ZCTAs reach Test and none reaches Launch. At $29.84, 40 of 50 reach Test; Launch requires about $43 per order. On the acquisition lever, at 60 percent of benchmark cost 30 of 50 flip to Test and none to Launch; at 40 percent, 46 flip and 10 reach Launch. The verdict is therefore a statement about the assumed economics, with measured flip points, not about the geography: a basket offer that roughly doubles per-order contribution, or an acquisition channel at roughly half the benchmark cost, reverses it for most of the shortlist.

The showcase ZCTA (10282, NYC metro) is the hardest case in the shortlist. Its uncontested Huff share at entry is 3 percent, and its win rate is 0 percent, payoff percentiles of −$812 (p10), −$522 (p50), and −$293 (p90) (Appendix Figure A1). It flips to Test only at $34.10 per order, or at 40 percent of benchmark acquisition cost. The plays the numbers support are to decline paid entry, to enter behind the basket offer if the ZIP is strategically wanted, or to enter organically.

*[Insert Table 7 about here]*

*[Insert Appendix Figure A1 about here]*

## 6. The Bayesian rare-event layer: a pre-stated test, and a mixed verdict

A single generative count model was specified as a candidate repair for the interval failure of Section 5.4, with its design, priors, and verdict criteria fixed in writing before any fit was run: a negative binomial likelihood with a household offset, the nine covariates, and a BYM2-type spatial prior under a top-300 eigenvector approximation to the ICAR field, fitted by MCMC. The full specification, results, and convergence record are in Online Appendix A; the verdict is summarized here. On Tier 1, across the same 24 draws as Section 5, the layer gives the best point recovery of any estimator tested (all-area RMSE 0.530 ± 0.011 for steamers and 0.521 ± 0.009 for trio, against Fay–Herriot's 0.538 ± 0.013 and 0.528 ± 0.012), so the pre-stated recovery criterion (C2) holds. It does not repair the intervals: sampled-area coverage of its nominal 95 percent posterior intervals (88.5 percent steamers, 91.9 percent trio) is indistinguishable from bootstrap-calibrated Fay–Herriot on paired per-draw differences, so the calibration criterion (C1) fails, and its targeting regret in dollars is no better (significantly worse for steamers). The variance-split ridge survives inside the posterior, and the spatial field itself is weakly recovered. In this version the layer's Tier 2 fits were also run, for the electronic-shopping outcome only; their results are reported with the Tier 2 benchmark's transport discussion in Section 8, and one of five evaluations does not make the pre-stated transport criterion (C3) assessable. No transport claim is made.

## 7. Discussion

The failures are the contribution, and each is the kind that routine output does not announce. First, the diagnostics go blind quietly. At the 8 percent sampling fraction this design is built around, Moran's I and the LM tests detect a strong, known spatial process in only 17–42 percent of replicate draws (Section 5.1). Yet on real outcomes the same tests reject even at 8 percent and overwhelmingly at full density (Section 5.7), so the practitioner cannot tell from the tests themselves whether a quiet result means weak dependence or weak power. Second, the intervals overstate their own precision. Fay–Herriot intervals average 88–89 percent coverage on sampled areas against a 95 percent nominal level across replicate draws (Section 5.4). The shortfall traces to a (size, σ²u) variance split that a single cross-section cannot identify, but that a designed second wave can: simulated in Section 5.4, pooling a second wave over the shared area effect recovers the size parameter an order of magnitude more accurately and lifts sampled-area coverage to about 0.94. Parametric-bootstrap calibration improves but does not repair it, and neither do adjusted-likelihood variance estimators. Under this sparsity, a nominal 95 percent interval is a false sense of security for any decision that consumes it. Third, no estimator ranking survives a change of surface. The ordering that is unambiguous against the simulated process dissolves on real outcomes into a near-tie: the econometric layers are indistinguishable from OLS for point prediction, and the flexible learner's edge is one to three percent (Section 5.8). What a decision-maker should take from the pipeline follows from exactly these pathologies. Its intervals have had their actual coverage measured under the design that will generate the real data, rather than assumed. Its second layer is not there to win but to disagree informatively. Concordance of 86–87% in the top decile with the econometric layer in Tier 1, and only roughly half of each top decile shared in Tier 2 (under a third on the electronic-shopping outcome), bound how far any shortlist should be trusted. The mixed-effects-random-forest challenge [35, 36] is best read as an argument for exactly this dual design: when the true surface's functional form is unknown, the layer comparison, graded against real holdouts rather than simulated truth, becomes the model-selection instrument [47]. And the decision layer's all-Avoid output under stated assumptions is not a counsel of despair but a demonstration that decision rules, stated in advance and fed by distributions rather than point estimates, can stop an entry program that looks attractive geographically but is unprofitable: the pre-specification discipline the geo-experiment literature demands of measurement [8, 9], applied to the spending decision itself.

The failures are as informative as the successes, and each maps to a known weakness in the underlying literature. The Moran diagnostic’s failure at 8% sampling (Section 5.1) is a power result that should temper the common workflow of screening spatial models by residual tests on sparse samples. The weakly identified (size, σ²u) split is the small-area literature’s estimated-variance problem in its sharpest form [33]. The covariate-tail attenuation (Section 5.2) is the ecological-inference face of a saturating response; here it is visible because the DGP’s clipping is disclosed, whereas in real applications it would appear as “the model underestimates Manhattan”, one more argument for pairing a linear layer with a flexible one and examining their disagreement map (Figure 3).

Finally, the identification boundary should be stated plainly. Nothing in Layers 1–2, fit to observational outcomes, identifies causal receptivity: covariate demand surfaces describe where demand is likely to be found, not what an intervention will cause there. Areas differ in unobserved ways correlated with both covariates and demand, and the spatial error term is a modeling device for that fact, not a cure for it [97]. The credible path is the one the program is built around: randomized geographic experiments convert Layer 1’s descriptive surface into causal lift estimates and give Layer 2 a valid training target. Econometric demand systems in the Berry–Levinsohn–Pakes lineage [55, 56, 57] show what full structural identification requires; the present architecture is a sparse-data screening step indicating where such investment could pay off.

Tier 2 also revises one Tier 1 impression. Read alone, the simulation casts GeoAI as a well-meaning auditor that should never lead; read with the benchmark, the layers' relative standing does not transport, and the architecture's practical output on real geography is the comparison itself. Where the layers agree, roughly half of each top decile is shared; where they disagree, the disagreement is information about the surface, to be resolved by the demand test's own outcomes when they arrive, not by deference to either layer's simulation ranking.


## 8. Limitations

Simulation recovery validates machinery, not markets. Every Tier 1 result is a property of the stated DGP (linear in covariates, with tail clipping, plus a SAR error) and the estimators; real demand surfaces may be neither, and recovery rankings could differ under a different truth. Tier 2 (Sections 5.7–5.8) probes exactly that and finds the point-prediction ordering does not transport. The game-theory outcomes are doubly conditional (on the DGP and on assumed economics) and are reported as an illustrative application only.

The variance split is weakly identified in one cross-section. The (NegBin size, σ²u) decomposition that drives Fay–Herriot intervals is nearly flat in likelihood over the plausible region (ΔlogLik ≈ 3–11), producing the coverage deviations of Section 5.4. A simulated second wave identifies the split inside this paper's data-generating process and removes most of the shortfall (Section 5.4); a real second wave is untested, and until one exists the intervals are approximate. Nor is the shortfall a boundary-estimate problem that a better area-level variance estimator repairs: adjusted maximum likelihood estimators built to prevent zero area-variance estimates leave the intervals essentially unchanged here, because the failure sits in the estimated sampling variances (Section 5.4).

ZCTA instability and the MAUP. ZCTAs are approximations of postal geography that shift across vintages (the polygons here are 2020 vintage; the covariates 2023), and all areal results are conditional on the areal system [80, 81, 82].

Diagnostic power. At 8% sampling, Moran’s I failed to detect a strong spatial process for one product (Section 5.1); users should select spatial specifications by fit criteria and recovery logic, not residual tests alone.

The incumbent is a proxy, not a measurement. Layer 3’s competitor is an ACS-covariate index containing no competitor locations, prices, assortments, or advertising pressure, and its response probabilities are a parameterized assumption, not estimated behavior. The Huff structure also inherits the independence-from-irrelevant-alternatives property that competing-destinations models relax [52]; with one aggregate incumbent this is second-order, but a multi-incumbent version should not assume so.

Covariance approximations. SAR/SDM coefficient covariances use a transformed-OLS approximation rather than the full ML Hessian; coefficient-level inference inherits it.

Assumed economics. Category spend per household ($120/yr), margins, basket values, funnel benchmarks, reach, repeat rates, and fixed costs are stated assumptions (Sections 3, 4.1, 4.5). They scale Layer 3’s payoffs directly, and the replication archive exposes each in one configuration file for sensitivity analysis.

Tier 2's outcomes are proxies with their own error. Establishment counts and tax returns are observed economic mass, not demand for any product; the electronic-shopping outcome is observed establishment presence, not sales, and is dominated by zeros (68.0 percent of ZCTAs), which is a property of the measure and drives its distinct interval behavior. ZBP totals carry disclosure-avoidance noise and SOI values are rounded, so Tier 2 grades against noisy targets and its interval figures are behavior, not coverage. The benchmark covers the study frame only, one cross-section plus one temporal transfer; the uptake target and the game layer have no public observed analogue and remain simulation-validated only.

The Bayesian layer's transport has now been tested on one Tier 2 evaluation, and it fails. Fitted to the electronic-shopping outcome on the same 24 draws, the layer's held-out RMSE averages 1.969 ± 0.206, against 1.012 ± 0.013 for Fay–Herriot and 0.944 ± 0.009 for GeoAI, and it is worse than Fay–Herriot in every one of the 24 draws (mean paired difference +0.956 ± 0.201). Its rankings carry no signal on this outcome (Spearman −0.033, against 0.280 for Fay–Herriot and 0.501 for GeoAI), and its top-decile overlap is 0.226. Its intervals cover more of the observed target than Fay–Herriot's (0.495 ± 0.065 against 0.296 ± 0.065, higher in all 24 draws), but only at about 3.4 times the width (mean width 2.83 against 0.84), and 0.495 remains far from the nominal 0.95: the extra coverage is bought with width, not earned by calibration. The pre-specified convergence gates pass in only 6 of the 24 fits. Criterion C3 of Section 6 requires near-tie-band performance on at least three evaluations, and the layer has been run on one of the benchmark's five, so C3 remains not assessable and no transport claim is made. On the one real surface where transport can be checked, the layer's Tier 1 recovery advantage (criterion C2) does not survive. The lesson of Section 5.8 applies to the new layer with full force.

Some designed analyses were not run, and are stated here so the record is complete. The Tier 1 econometric protocol has now been run at 4 percent and 16 percent sampling as well as 8 percent (Section 5.4), which narrows the fractions limitation for the econometric core; the Bayesian layer was not rerun at those fractions, so its results remain specific to the 8 percent design. Also not run: the pre-specified prior-sensitivity grid (wider priors on log(size), the regression coefficients, and σ_b), and seven of the eight designed replicates of the temporal extension in Online Appendix A. The Bayesian results are therefore specific to the 8 percent design and the stated priors, in exactly the way the design document anticipated and the manuscript does not conceal.

Convergence of the Bayesian fits is a limitation in its own right: the pre-specified gates pass in only 1 of 24 steamers fits and 0 of 24 trio fits, with failures concentrated on the ridge parameters (Online Appendix A). Per-chain posterior means agree and the implementation self-test recovers nominal coverage on model-simulated data, but the Section 6 interval results are the output of fits that mix slowly along exactly the weakly identified direction.


## 9. Conclusion

We have stress-tested the standard sparse-sample spatial toolkit (spatial econometric small-area estimation with a Fay–Herriot stage, a GeoAI cross-check, and the diagnostics and intervals that connect them) at the sampling fraction where a growing share of applied geographic work actually lives: 447 of 5,576 areas observed, 92 percent of the map missing. Two-tier validation (simulation recovery against a known truth, and an empirical benchmark against observed business, tax-return, and electronic-shopping counts, repeated across 24 sample draws) finds the machinery behaving largely as its literatures predict, with three measured exceptions that should change practice. Diagnostics go blind: at 8 percent sampling, Moran's I and LM tests usually miss a strong spatial process that full-density tests find decisively, and the robust forms disagree about its form even there. Intervals overstate: Fay–Herriot plug-in intervals under-cover because the variance split is weakly identified in one cross-section; bootstrap calibration improves but does not repair the shortfall, and neither do adjusted-likelihood variance estimators, while a simulated second wave identifies the split and removes most of it. Rankings do not transport: the estimator ordering that is unambiguous on the simulated surface dissolves on real surfaces into a near-tie in which the spatial machinery adds nothing over OLS for point prediction. The flexible learner's edge, one to three percent on the proxy outcomes and larger on the observed e-commerce outcome, is consistent across draws on four of the five evaluations and too small to crown a winner. Which estimator wins is a property of the unobserved surface, and the mechanism remains open. The decision layer that motivated the exercise (a spatial interaction model converting the surfaces into Launch, Test, or Avoid choices under competitor response) is reported as an illustrative application: its value is precisely that it consumes the intervals and disagreements the stress test measures, rather than the point estimates the stress test discredits. For the forthcoming empirical study (real outcomes from a geographic demand-test program pre-specified in a dated design note, dropped into the documented interface without changing an estimator) the pathologies specify what must be collected: a second wave, which the simulation of Section 5.4 shows would identify the variance split, and holdout geography dense enough to keep the diagnostics honest. The code and recovery evidence are available for that purpose and for reuse by other sparse-market entrants.

The Bayesian layer added in Section 6 sharpens, rather than softens, that conclusion. A single generative count model with principled priors recovered points marginally better than every comparator, and still did not repair interval coverage for one of the two products, did not recover the spatial field, and did not improve targeting regret in dollars. Better machinery, honestly graded, is not the same as a repaired pathology. The decision layer's answer stands as our practical summary: at the stated economics, all 50 shortlisted ZIP codes are Avoid, and an analytics stack that can say that, with intervals it has audited, has done the seller a service that a confident launch list would not.


## Funding

This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.


## Declaration of competing interests

The planned demand test that motivates this study will be run through storefronts operated by the author. We use no data from those storefronts and report no commercial results. The author has no other financial or personal relationships that could have appeared to influence the work reported here.


## Declaration of generative AI and AI-assisted technologies in the manuscript preparation process

During the preparation of this work, Claude helped with language and grammar. After using this tool, the author reviewed and edited the content as needed and takes full responsibility for the content of the published article.


## Data availability

The code, configuration, and data-fetch script are available in a public GitHub repository; the link is withheld for double-anonymized review and will be supplied on acceptance. Inputs are ACS 2023 5-year summary files and the 2023 Gazetteer, fetched by a one-time script. The Tier 2 benchmark inputs are equally public and are fetched the same way: ZIP Code Business Patterns 2022 and 2019 totals files, the ZBP 2022 detail file (zbp22detail.zip), from which the NAICS 454110 electronic-shopping establishment counts are extracted, and the IRS Statistics of Income ZIP Code Data for tax year 2022 (file 22zpallagi.csv), each from its publisher's public download page, with no registration or restricted access involved. python run_all.py regenerates every table, figure, and number reported here under a fixed random seed (20261013) with pinned dependencies. Real outcomes enter through data/real_outcomes.csv (one row per tested ZCTA per product), after which python run_all.py --real re-runs every estimator unchanged and stamps the output real_outcomes. The strengthening tests reported in Sections 4.6, 5.4, 5.7, and 6 and in Online Appendix A (the electronic-shopping benchmark and its Bayesian fits, the adjusted-likelihood variance estimators, the simulated second wave, and the sampling-fraction reruns) are deposited alongside as ecra/strengthening/, each with its own seeded runner; their result files, the dated design note, and the test memos accompany them. Two artifact classes are not mirrored in the repository: the per-draw prediction file for the observed-outcome benchmark and the binary per-draw fit arrays. Both are regenerated by the deposited code, and the strengthening notes and integration manifest deposited with the results record their names, sizes, and SHA-256 hashes.


## References

[1] V. Zwass, Electronic commerce: Structures and issues, Int. J. Electron. Commer. 1 (1996) 3 – 23.

[2] J.Y. Bakos, Reducing buyer search costs: Implications for electronic marketplaces, Manage. Sci. 43 (1997) 1676 – 1692.

[3] A. Goldfarb, C. Tucker, Digital economics, J. Econ. Lit. 57 (2019) 3 – 43.

[4] Y. Liu, Y. Zheng, J. Wei, Y. Yang, The use of inside-out and outside-in big data analytics on e-platforms: Performance impacts and heterogeneity analysis, Int. J. Electron. Commer. 27 (2023) 36 – 65.

[5] A.R. Hevner, S.T. March, J. Park, S. Ram, Design science in information systems research, MIS Q. 28 (2004) 75 – 106.

[6] K. Peffers, T. Tuunanen, M.A. Rothenberger, S. Chatterjee, A design science research methodology for information systems research, J. Manage. Inf. Syst. 24 (2007) 45 – 77.

[7] B.R. Gordon, K. Jerath, Z. Katona, S. Narayanan, J. Shin, K.C. Wilbur, Inefficiencies in digital advertising markets, J. Mark. 85 (2021) 7 – 25. https://doi.org/10.1177/0022242920913236.

[8] R.A. Lewis, J.M. Rao, The unfavorable economics of measuring the returns to advertising, Q. J. Econ. 130 (2015) 1941 – 1973. https://doi.org/10.1093/qje/qjv023.

[9] B.R. Gordon, F. Zettelmeyer, N. Bhargava, D. Chapsky, A comparison of approaches to advertising measurement: Evidence from big field experiments at Facebook, Mark. Sci. 38 (2019) 193 – 225. https://doi.org/10.1287/mksc.2018.1135.

[10] B.R. Gordon, R. Moakler, F. Zettelmeyer, Close enough? A large-scale exploration of non-experimental approaches to advertising measurement, Mark. Sci. 42 (2023) 768 – 793. https://doi.org/10.1287/mksc.2022.1413.

[11] R.E. Fay, R.A. Herriot, Estimates of income for small places: An application of James-Stein procedures to census data, J. Am. Stat. Assoc. 74 (1979) 269 – 277. https://doi.org/10.1080/01621459.1979.10482505.

[12] J.H. Friedman, Greedy function approximation: A gradient boosting machine, Ann. Stat. 29 (2001) 1189 – 1232. https://doi.org/10.1214/aos/1013203451.

[13] K. Janowicz, S. Gao, G. McKenzie, Y. Hu, B. Bhaduri, GeoAI: Spatially explicit artificial intelligence techniques for geographic knowledge discovery and beyond, Int. J. Geogr. Inf. Sci. 34 (2020) 625 – 636. https://doi.org/10.1080/13658816.2019.1684500.

[14] K. Janowicz, Philosophical foundations of GeoAI: Exploring sustainability, diversity, and bias in GeoAI and spatial data science, in: Handbook of Geospatial Artificial Intelligence, CRC Press, Boca Raton, FL, 2023, pp. 26 – 42. https://doi.org/10.1201/9781003308423-3.

[15] S. Athey, G.W. Imbens, Machine learning methods that economists should know about, Annu. Rev. Econ. 11 (2019) 685 – 725. https://doi.org/10.1146/annurev-economics-080217-053433.

[16] K. Janowicz, P. Hitzler, W. Li, D. Rehberger, M. Schildhauer, R. Zhu, C. Shimizu, C.K. Fisher, L. Cai, G. Mai, J. Zalewski, L. Zhou, S. Stephen, S. Gonzalez, B. Mecum, A. Lopez-Carr, A. Schroeder, D. Smith, D. Wright, S. Wang, Y. Tian, Z. Liu, M. Shi, A. D’Onofrio, Z. Gu, K. Currier, Know, know where, KnowWhereGraph: A densely connected, cross-domain knowledge graph and geo-enrichment service stack for applications in environmental intelligence, AI Mag. 43 (2022) 30 – 39. https://doi.org/10.1002/aaai.12043.

[17] H. Hotelling, Stability in competition, Econ. J. 39 (1929) 41 – 57. https://doi.org/10.2307/2224214.

[18] S. Loertscher, Location games, in: Spatial Economics, Vol. 1, Springer, Cham, 2020, pp. 111 – 128. https://doi.org/10.1007/978-3-030-40098-9_5.

[19] D.L. Huff, A probabilistic analysis of shopping center trade areas, Land Econ. 39 (1963) 81 – 90. https://doi.org/10.2307/3144521.

[20] W.R. Tobler, A computer movie simulating urban growth in the Detroit region, Econ. Geogr. 46 (1970) 234 – 240. https://doi.org/10.2307/143141.

[21] Author, [Reference withheld for double-anonymized review], unpublished manuscript, 2026.

[22] A.D. Cliff, J.K. Ord, Spatial Processes: Models and Applications, Pion, London, 1981.

[23] L. Anselin, Spatial Econometrics: Methods and Models, Kluwer Academic, Dordrecht, 1988. https://doi.org/10.1007/978-94-015-7799-1.

[24] J. LeSage, R.K. Pace, Introduction to Spatial Econometrics, Chapman & Hall/CRC, Boca Raton, FL, 2009. https://doi.org/10.1201/9781420064254.

[25] J.P. Elhorst, Spatial Econometrics: From Cross-Sectional Data to Spatial Panels, Springer, Berlin, 2014. https://doi.org/10.1007/978-3-642-40340-8.

[26] S. Halleck Vega, J.P. Elhorst, The SLX model, J. Reg. Sci. 55 (2015) 339 – 363. https://doi.org/10.1111/jors.12188.

[27] J. LeSage, What regional scientists need to know about spatial econometrics, Rev. Reg. Stud. 44 (2014) 13 – 32. https://doi.org/10.52324/001c.8081.

[28] P.A.P. Moran, Notes on continuous stochastic phenomena, Biometrika 37 (1950) 17 – 23. https://doi.org/10.1093/biomet/37.1-2.17.

[29] L. Anselin, A.K. Bera, Spatial dependence in linear regression models with an introduction to spatial econometrics, in: A. Ullah, D.E. Giles (Eds.), Handbook of Applied Economic Statistics, Marcel Dekker, New York, 1998.

[30] E. Pebesma, R. Bivand, Spatial Data Science: With Applications in R, Chapman & Hall/CRC, Boca Raton, FL, 2023. https://doi.org/10.1201/9780429459016.

[31] G.E. Battese, R.M. Harter, W.A. Fuller, An error-components model for prediction of county crop areas using survey and satellite data, J. Am. Stat. Assoc. 83 (1988) 28 – 36. https://doi.org/10.1080/01621459.1988.10478561.

[32] J.N.K. Rao, I. Molina, Small Area Estimation, second ed., Wiley, Hoboken, NJ, 2015. https://doi.org/10.1002/9781118735855.

[33] D. Pfeffermann, New important developments in small area estimation, Stat. Sci. 28 (2013) 40 – 68. https://doi.org/10.1214/12-STS395.

[34] C. Elbers, J.O. Lanjouw, P. Lanjouw, Micro-level estimation of poverty and inequality, Econometrica 71 (2003) 355 – 364. https://doi.org/10.1111/1468-0262.00399.

[35] P. Krennmair, T. Schmid, Flexible domain prediction using mixed effects random forests, J. R. Stat. Soc. Ser. C (Appl. Stat.) 71 (2022) 1865 – 1894. https://doi.org/10.1111/rssc.12600.

[36] P. Krennmair, N. Würz, T. Schmid, N. Tzavidis, Random forests and mixed effects random forests for small area estimation of general parameters: A poverty mapping case study in Mozambique, Ann. Appl. Stat. 20 (2026) 809 – 832. https://doi.org/10.1214/25-AOAS2126.

[37] K. Klemmer, E. Rolf, C. Robinson, L. Mackey, M. Rußwurm, SatCLIP: Global, general-purpose location embeddings with satellite imagery, Proc. AAAI Conf. Artif. Intell. 39 (2025) 4347 – 4355. https://doi.org/10.1609/aaai.v39i4.32457.

[38] G. Chi, H. Fang, S. Chatterjee, J.E. Blumenstock, Microestimates of wealth for all low- and middle-income countries, Proc. Natl. Acad. Sci. 119 (2022) e2113658119. https://doi.org/10.1073/pnas.2113658119.

[39] E. Rolf, J. Proctor, T. Carleton, I. Bolliger, V. Shankar, K. Ishihara, B. Recht, S. Hsiang, A generalizable and accessible approach to machine learning with global satellite imagery, Nat. Commun. 12 (2021) 4392. https://doi.org/10.1038/s41467-021-24638-z.

[40] L. Breiman, Random forests, Mach. Learn. 45 (2001) 5 – 32. https://doi.org/10.1023/A:1010933404324.

[41] S.M. Lundberg, S.-I. Lee, A unified approach to interpreting model predictions, in: Advances in Neural Information Processing Systems 30, Curran Associates, 2017, pp. 4765 – 4774.

[42] J. Lei, M. G’Sell, A. Rinaldo, R.J. Tibshirani, L. Wasserman, Distribution-free predictive inference for regression, J. Am. Stat. Assoc. 113 (2018) 1094 – 1111. https://doi.org/10.1080/01621459.2017.1307116.

[43] A.N. Angelopoulos, S. Bates, Conformal prediction: A gentle introduction, Found. Trends Mach. Learn. 16 (2023) 494 – 591. https://doi.org/10.1561/2200000101.

[44] R.F. Barber, E.J. Candès, A. Ramdas, R.J. Tibshirani, Conformal prediction beyond exchangeability, Ann. Stat. 51 (2023) 816 – 845. https://doi.org/10.1214/23-AOS2276.

[45] D.R. Roberts, V. Bahn, S. Ciuti, M.S. Boyce, J. Elith, G. Guillera-Arroita, S. Hauenstein, J.J. Lahoz-Monfort, B. Schröder, W. Thuiller, D.I. Warton, B.A. Wintle, F. Hartig, C.F. Dormann, Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure, Ecography 40 (2017) 913 – 929. https://doi.org/10.1111/ecog.02881.

[46] R. Valavi, J. Elith, J.J. Lahoz-Monfort, G. Guillera-Arroita, blockCV: An R package for generating spatially or environmentally separated folds for k-fold cross-validation of species distribution models, Methods Ecol. Evol. 10 (2019) 225 – 232. https://doi.org/10.1111/2041-210X.13107.

[47] P. Ploton, F. Mortier, M. Réjou-Méchain, N. Barbier, N. Picard, V. Rossi, C. Dormann, G. Cornu, G. Viennois, N. Bayol, A. Lyapustin, S. Gourlet-Fleury, R. Pélissier, Spatial validation reveals poor predictive performance of large-scale ecological mapping models, Nat. Commun. 11 (2020) 4540. https://doi.org/10.1038/s41467-020-18321-y.

[48] H. Meyer, E. Pebesma, Predicting into unknown space? Estimating the area of applicability of spatial prediction models, Methods Ecol. Evol. 12 (2021) 1620 – 1633. https://doi.org/10.1111/2041-210X.13650.

[49] D.L. Huff, Defining and estimating a trading area, J. Mark. 28 (1964) 34 – 38. https://doi.org/10.1177/002224296402800307.

[50] W.J. Reilly, The Law of Retail Gravitation, Knickerbocker Press, New York, 1931.

[51] A.G. Wilson, Entropy in Urban and Regional Modelling, Pion, London, 1970.

[52] A.S. Fotheringham, A new set of spatial-interaction models: The theory of competing destinations, Environ. Plan. A 15 (1983) 15 – 36. https://doi.org/10.1068/a150015.

[53] J. Liang, S. Gao, J. Cai, N.Z. Foutz, L. Wu, Calibrating the dynamic Huff model for business analysis using location big data, Trans. GIS 24 (2020) 681 – 703. https://doi.org/10.1111/tgis.12624.

[54] W. Applebaum, Methods for determining store trade areas, market penetration, and potential sales, J. Mark. Res. 3 (1966) 127 – 141. https://doi.org/10.1177/002224376600300202.

[55] S. Berry, J. Levinsohn, A. Pakes, Automobile prices in market equilibrium, Econometrica 63 (1995) 841 – 890. https://doi.org/10.2307/2171802.

[56] S. Berry, P. Haile, Foundations of demand estimation, in: K. Ho, A. Hortaçsu (Eds.), Handbook of Industrial Organization, Vol. 4, Elsevier, Amsterdam, 2021, pp. 1 – 62. https://doi.org/10.1016/bs.hesind.2021.11.001.

[57] C. Conlon, J. Gortmaker, Best practices for differentiated products demand estimation with PyBLP, RAND J. Econ. 51 (2020) 1108 – 1161. https://doi.org/10.1111/1756-2171.12352.

[58] A. Gandhi, J.-F. Houde, Measuring substitution patterns in differentiated-products industries, NBER Working Paper No. 26375, National Bureau of Economic Research, Cambridge, MA, 2019. https://doi.org/10.3386/w26375.

[59] T. Blake, C. Nosko, S. Tadelis, Consumer heterogeneity and paid search effectiveness: A large-scale field experiment, Econometrica 83 (2015) 155 – 174. https://doi.org/10.3982/ECTA12423.

[60] B.T. Shapiro, G.J. Hitsch, A.E. Tuchman, TV advertising effectiveness and profitability: Generalizable results from 288 brands, Econometrica 89 (2021) 1855 – 1879. https://doi.org/10.3982/ECTA17674.

[61] A. Goldfarb, C. Tucker, Privacy regulation and online advertising, Manage. Sci. 57 (2011) 57 – 71. https://doi.org/10.1287/mnsc.1100.1246.

[62] M. Tian, P.R. Hoban, N. Arora, What cookie-based advertising effectiveness fails to measure, Mark. Sci. 43 (2024) 407 – 418.

[63] I. Bojinov, D. Simchi-Levi, J. Zhao, Design and analysis of switchback experiments, Manage. Sci. 69 (2023) 3759 – 3777.

[64] G.A. Johnson, R.A. Lewis, E.I. Nubbemeyer, Ghost ads: Improving the economics of measuring online ad effectiveness, J. Mark. Res. 54 (2017) 867 – 884.

[65] J. Han, X. Dai, Online auction design using distribution-free uncertainty quantification with applications to e-commerce, J. Am. Stat. Assoc. 121 (2026) 137 – 148.

[66] B.S. Blum, A. Goldfarb, Does the internet defy the law of gravity?, J. Int. Econ. 70 (2006) 384 – 405.

[67] T. Sinai, J. Waldfogel, Geography and the Internet: Is the Internet a substitute or a complement for cities?, J. Urban Econ. 56 (2004) 1 – 24.

[68] C. Forman, A. Goldfarb, S. Greenstein, How did location affect adoption of the commercial Internet? Global village vs. urban leadership, J. Urban Econ. 58 (2005) 389 – 420.

[69] X. Cui, T. Zhu, Y. Chen, Where you live matters: The impact of offline retail density on mobile shopping app usage, J. Retail. 100 (2024) 41 – 55.

[70] E. Brynjolfsson, Y. Hu, D. Simester, Goodbye Pareto principle, hello long tail: The effect of search costs on the concentration of product sales, Manage. Sci. 57 (2011) 1373 – 1386.

[71] S. Nakano, Customer demand concentration in online grocery retailing: Differences between online and physical store shopping baskets, Electron. Commer. Res. Appl. 62 (2023) 101336.

[72] L. Einav, D. Knoepfle, J. Levin, N. Sundaresan, Sales taxes and Internet commerce, Am. Econ. Rev. 104 (2014) 1 – 26.

[73] Z. Jiang, J. Li, D. Zhang, A high-dimensional choice model for online retailing, Manage. Sci. 71 (2025) 3320 – 3339.

[74] J. Zeng, Y. Fang, H. Li, Y. Wang, K.H. Lim, Untangling the performance impact of e-marketplace sellers' deployment of platform-based functions: A configurational perspective, Inf. Syst. Res. 36 (2025) 1397 – 1417.

[75] Z. Ye, D.J. Zhang, H. Zhang, R. Zhang, X. Chen, Z. Xu, Cold start to improve market thickness on online advertising platforms: Data-driven algorithms and field experiments, Manage. Sci. 69 (2023) 3838 – 3860.

[76] C. Liang, Y. Hong, B. Gu, Monitoring and the cold start problem in digital platforms: Theory and evidence from online labor markets, Inf. Syst. Res. 36 (2025) 600 – 620.

[77] N.M. Fong, Z. Fang, X. Luo, Geo-conquesting: Competitive locational targeting of mobile promotions, J. Mark. Res. 52 (2015) 726 – 735.

[78] A. Ghose, A. Goldfarb, S.P. Han, How is the mobile Internet different? Search costs and local activities, Inf. Syst. Res. 24 (2013) 613 – 631.

[79] A. Hunneman, T.H.A. Bijmolt, J.P. Elhorst, Evaluating store location and department composition based on spatial heterogeneity in sales potential, J. Retail. Consum. Serv. 73 (2023) 103355.

[80] S. Openshaw, The Modifiable Areal Unit Problem, CATMOG 38, Geo Books, Norwich, 1984.

[81] T.H. Grubesic, T.C. Matisziw, On the use of ZIP codes and ZIP code tabulation areas (ZCTAs) for the spatial analysis of epidemiological data, Int. J. Health Geogr. 5 (2006) 58. https://doi.org/10.1186/1476-072X-5-58.

[82] N. Krieger, J.T. Chen, P.D. Waterman, M.-J. Soobader, S.V. Subramanian, R. Carson, Geocoding and monitoring of US socioeconomic inequalities in mortality and cancer incidence: Does the choice of area-based measure and geographic level matter? The Public Health Disparities Geocoding Project, Am. J. Epidemiol. 156 (2002) 471 – 482. https://doi.org/10.1093/aje/kwf068.

[83] U.S. Census Bureau, American Community Survey 5-year estimates, 2019–2023, U.S. Department of Commerce, Washington, DC, 2024.

[84] U.S. Bureau of Labor Statistics, Consumer expenditure surveys, U.S. Department of Labor, Washington, DC, 2024.

[85] U.S. Census Bureau, County Business Patterns and ZIP Code Business Patterns, 2022 (and 2019), U.S. Department of Commerce, Washington, DC, 2024.

[86] Internal Revenue Service, Statistics of Income Division, SOI Tax Stats — Individual income tax statistics — ZIP Code Data, Tax Year 2022, Internal Revenue Service, Washington, DC, 2025.

[87] L. Anselin, A.K. Bera, R. Florax, M.J. Yoon, Simple diagnostic tests for spatial dependence, Reg. Sci. Urban Econ. 26 (1996) 77 – 104.

[88] N.G.N. Prasad, J.N.K. Rao, The estimation of mean squared error of small-area estimators, J. Am. Stat. Assoc. 85 (1990) 163 – 171.

[89] P. Hall, T. Maiti, On parametric bootstrap methods for small area prediction, J. R. Stat. Soc. Ser. B 68 (2006) 221 – 238.

[90] H. Li, P. Lahiri, An adjusted maximum likelihood method for solving small area estimation problems, J. Multivariate Anal. 101 (2010) 882 – 892.

[91] M. Yoshimori, P. Lahiri, A new adjusted maximum likelihood method for the Fay–Herriot small area model, J. Multivariate Anal. 124 (2014) 281 – 294.

[92] A. Riebler, S.H. Sørbye, D. Simpson, H. Rue, An intuitive Bayesian spatial model for disease mapping that accounts for scaling, Stat. Methods Med. Res. 25 (2016) 1145 – 1165.

[93] J. Besag, J. York, A. Mollié, Bayesian image restoration, with two applications in spatial statistics, Ann. Inst. Stat. Math. 43 (1991) 1 – 20.

[94] D. Simpson, H. Rue, A. Riebler, T.G. Martins, S.H. Sørbye, Penalising model component complexity: A principled, practical approach to constructing priors, Stat. Sci. 32 (2017) 1 – 28.

[95] J. Pitkin, I. Manolopoulou, G. Ross, Bayesian hierarchical modelling of sparse count processes in retail analytics, Ann. Appl. Stat. 18 (2024) 946 – 965.

[96] H. Rue, S. Martino, N. Chopin, Approximate Bayesian inference for latent Gaussian models by using integrated nested Laplace approximations, J. R. Stat. Soc. Ser. B (Stat. Methodol.) 71 (2009) 319 – 392.

[97] H.H. Kelejian, G. Piras, Spatial Econometrics, Academic Press, London, 2017.


## Tables


**Table 1. Data-generating process: true coefficients on standardized covariates (log order-rate scale). Global parameters: ρ = 0.55, σ = 0.45, Negative Binomial size = 6.0, sample fraction 8% (region × income-tercile strata), test session rate 0.06 per household.**

| Term | Steamers β (truth) | Trio β (truth) |
| --- | --- | --- |
| Intercept | −5.10 | −5.55 |
| log income | +0.22 | +0.42 |
| Share of HHs ≥ $100k | +0.10 | +0.25 |
| Renter share | +0.48 | −0.38 |
| Seasonal share | −0.08 | +0.12 |
| % single-family | −0.30 | +0.40 |
| % large building | +0.38 | −0.25 |
| Avg. household size | −0.12 | +0.20 |
| Median age | −0.15 | +0.05 |
| log density | +0.30 | −0.10 |


**Table 2. Model fit on the simulated sample, by product. Spatial parameter is ρ (SAR), λ (SEM), or ρ (SDM). Model chosen by AIC in bold. All log-likelihoods and σ² values are computed on a common maximum-likelihood basis (σ² = RSS/n) for the four specifications.**

| Product | Model | logLik | AIC | Spatial param. | σ² |
| --- | --- | --- | --- | --- | --- |
| Steamers | OLS | −469.2 | 958.3 | n/a | 0.478 |
| Steamers | SAR | −467.4 | 956.7 | −0.025 | 0.474 |
| Steamers | SEM | −468.9 | 959.9 | 0.045 | 0.477 |
| Steamers | SDM | −463.6 | 967.3 | −0.026 | 0.466 |
| Trio | OLS | −519.3 | 1,058.7 | n/a | 0.598 |
| Trio | SAR | −518.7 | 1,059.3 | 0.015 | 0.596 |
| Trio | SEM | −512.8 | 1,047.5 | 0.211 | 0.574 |
| Trio | SDM | −514.2 | 1,068.3 | 0.019 | 0.584 |


**Table 3. Coefficient recovery: DGP truth vs. sample estimates, by product. (a) Steamers. (b) Trio.**

(a) Steamers

| Term | Truth | OLS | SAR | SEM | SDM |
| --- | --- | --- | --- | --- | --- |
| Intercept | −5.10 | −5.15 | −5.20 | −5.15 | −5.20 |
| log income | 0.22 | 0.18 | 0.19 | 0.18 | 0.19 |
| Share ≥ $100k | 0.10 | 0.10 | 0.09 | 0.10 | 0.08 |
| Renter share | 0.48 | 0.39 | 0.38 | 0.40 | 0.39 |
| Seasonal share | −0.08 | −0.08 | −0.09 | −0.08 | −0.10 |
| % single-family | −0.30 | −0.34 | −0.35 | −0.34 | −0.31 |
| % large building | 0.38 | 0.19 | 0.19 | 0.19 | 0.19 |
| Avg. HH size | −0.12 | −0.10 | −0.10 | −0.10 | −0.15 |
| Median age | −0.15 | −0.11 | −0.11 | −0.11 | −0.12 |
| log density | 0.30 | 0.35 | 0.36 | 0.34 | 0.34 |

(b) Trio

| Term | Truth | OLS | SAR | SEM | SDM |
| --- | --- | --- | --- | --- | --- |
| Intercept | −5.55 | −5.57 | −5.54 | −5.56 | −5.53 |
| log income | 0.42 | 0.32 | 0.31 | 0.34 | 0.32 |
| Share ≥ $100k | 0.25 | 0.45 | 0.45 | 0.43 | 0.45 |
| Renter share | −0.38 | −0.21 | −0.22 | −0.23 | −0.22 |
| Seasonal share | 0.12 | 0.04 | 0.05 | 0.06 | 0.05 |
| % single-family | 0.40 | 0.37 | 0.38 | 0.37 | 0.38 |
| % large building | −0.25 | −0.19 | −0.19 | −0.20 | −0.19 |
| Avg. HH size | 0.20 | 0.14 | 0.14 | 0.15 | 0.16 |
| Median age | 0.05 | 0.04 | 0.04 | 0.03 | 0.05 |
| log density | −0.10 | −0.25 | −0.25 | −0.24 | −0.23 |


**Table 4. Recovery summary (log-rate scale unless noted). Interval coverage is for nominal 95% Fay–Herriot intervals, graded against truth on all ZCTAs and on sampled ZCTAs.**

| Quantity | Steamers | Trio |
| --- | --- | --- |
| RMSE, OLS | 0.514 | 0.538 |
| RMSE. Best spatial model | 0.518 | 0.535 |
| RMSE, after Fay–Herriot | 0.512 | 0.529 |
| 95% interval coverage (all ZCTAs) | 83.7% | 97.4% |
| 95% interval coverage (sampled ZCTAs) | 83.9% | 82.8% |
| FH mean shrinkage weight γ | 0.27 | 0.77 |
| FH area variance σ²u | 0.125 | 0.439 |
| NegBin size: estimated (truth 6.0) | 3.7 | 55.3 |
| GeoAI holdout RMSE (within sample) | 0.752 | 0.848 |
| GeoAI recovery RMSE (all ZCTAs) | 0.606 | 0.665 |
| GeoAI uptake RMSE (probability scale) | 0.009 | 0.009 |
| Layer agreement: Pearson r | 0.941 | 0.927 |
| Layer agreement: Spearman ρ | 0.888 | 0.912 |
| Layer agreement: top-decile overlap | 87% | 86% |
| 95% interval coverage, bootstrap-calibrated, 24-draw mean (all ZCTAs) | 95.3% | 97.5% |
| 95% interval coverage, bootstrap-calibrated, 24-draw mean (sampled ZCTAs) | 91.4% | 90.0% |
| Bootstrap half-width multiplier, 24-draw mean | 1.119 | 1.107 |
| Raw 95% coverage across the same 24 draws, mean (sampled ZCTAs) | 88.5% | 87.6% |


**Table 5. Tier 2 benchmark: layers fitted on 447 sampled ZCTAs only; graded against observed outcomes on the held-out ZCTAs (log-rate scale). Entries are means ± 1 sd across the 24 sample draws of Section 5.7; the best spatial model is chosen by AIC per draw (SEM in 67–79 percent of draws). Fay–Herriot behavior is the share of held-out ZCTAs whose observed log rate falls inside the nominal 95% interval. Behavior against a noisy observed target, not coverage of a known truth.**

| Outcome (2022, per household) | Graded ZCTAs (draw mean) | OLS | Best spatial | Fay–Herriot | GeoAI | FH interval behavior |
| --- | --- | --- | --- | --- | --- | --- |
| ZBP establishments | 5,061 | 0.517 ± 0.005 | 0.518 ± 0.006 (AIC) | 0.518 ± 0.006 | 0.505 ± 0.006 | 90.3 ± 4.6% |
| SOI returns | 5,069 | 0.215 ± 0.002 | 0.215 ± 0.002 (AIC) | 0.215 ± 0.002 | 0.208 ± 0.004 | 86.8 ± 1.3% |
| SOI business returns | 5,069 | 0.754 ± 0.008 | 0.758 ± 0.013 (AIC) | 0.758 ± 0.013 | 0.751 ± 0.013 | 94.7 ± 1.8% |
| Temporal transfer: fit ZBP 2019, grade ZBP 2022 | 5,061 | 0.522 ± 0.006 | 0.523 ± 0.007 (AIC) | 0.523 ± 0.007 | 0.511 ± 0.007 | 91.7 ± 3.9% |
| ZBP electronic-shopping establishments (NAICS 454110) | 5,061 | 1.010 ± 0.008 | 1.012 ± 0.013 (AIC) | 1.012 ± 0.013 | 0.944 ± 0.009 | 29.6 ± 6.5% |


**Table 6. Concordance of the two validation tiers against the questions stated in advance of the Tier 2 analysis (design note, 2026-10-18; Section 4.6).**

| Question | Tier 1 (simulation) | Tier 2 (observed) | Verdict |
| --- | --- | --- | --- |
| Layer rankings | Layer 1 best; GeoAI worst on point prediction | GeoAI modestly better on 4 of 5 evaluations (24-draw means), tied on the fifth; Layer 1 ≈ OLS | Disagree. Tier 1 ordering does not transport; mechanism unresolved (roughness test negative) |
| FH interval behavior | Under-coverage on sampled areas (24-draw means 88–89%); all-area means 93.1% / 96.0% | 87–95% of held-out observed rates inside nominal 95% on four evaluations; 29.6% on the sparse electronic-shopping outcome, where the fitted σ²u collapses | Disagree like-for-like. Real-data behavior at or below Tier 1 all-area level; near nominal only for business returns; a distinct collapse mode on the sparse count outcome |
| Diagnostic failure modes | Moran and LM tests usually blind at 8% sampling | Moran and LM-error reject even at the 8% sample; decisive at full density; robust LM forms disagree on form | Partly disagree. Blindness is a simulation power property; real dependence is detectable at the design's sampling fraction |


**Table 7. Game-theory outcomes, top five shortlisted ZCTAs per region (steamers; 500 Monte Carlo draws each), with the economics sensitivity of Section 5.9. The last two columns give, for each ZCTA, the per-order contribution at which its decision flips from Avoid to Test with acquisition cost held at benchmark, and the acquisition-cost multiplier (share of benchmark) at which it flips with contribution held at the assumed $17.05. Thresholds are grid points (contribution in multiples of 0.25 of $17.05; acquisition cost in multiples of 0.20 of benchmark). Full 25-ZIP shortlists are in the replication archive (results/game_shortlist.csv); the full sensitivity grid is in results/econ_sensitivity.csv.**

| Region | ZIP | Win rate | Share p50 | Payoff p10 | Payoff p50 | Payoff p90 | Decision | Contribution at flip to Test | CAC multiplier at flip to Test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Southeast | 33130 | 6% | 0.17 | −$6,325 | −$2,935 | −$481 | Avoid | $25.58 | 0.60 |
| Southeast | 23510 | 6% | 0.17 | −$1,956 | −$915 | −$130 | Avoid | $25.58 | 0.60 |
| Southeast | 37203 | 5% | 0.17 | −$4,932 | −$2,498 | −$383 | Avoid | $25.58 | 0.60 |
| Southeast | 33136 | 5% | 0.26 | −$2,668 | −$1,253 | −$202 | Avoid | $25.58 | 0.60 |
| Southeast | 30308 | 5% | 0.12 | −$4,153 | −$2,072 | −$363 | Avoid | $29.84 | 0.60 |
| NYC metro | 11102 | 9% | 0.16 | −$5,656 | −$2,695 | −$107 | Avoid | $25.58 | 0.60 |
| NYC metro | 10009 | 7% | 0.09 | −$13,968 | −$6,594 | −$802 | Avoid | $25.58 | 0.60 |
| NYC metro | 10012 | 6% | 0.10 | −$5,192 | −$2,540 | −$506 | Avoid | $29.84 | 0.60 |
| NYC metro | 10003 | 5% | 0.07 | −$7,761 | −$4,035 | −$727 | Avoid | $29.84 | 0.60 |
| NYC metro | 10001 | 4% | 0.06 | −$5,114 | −$2,542 | −$452 | Avoid | $29.84 | 0.60 |


## Figures


**Figure 1. Predicted demand for shower steamers in the New York metro area. The map shows Layer 2 (GeoAI gradient-boosting) predicted demand for the steamers product, predicted orders per household per year, for each of the 519 ZIP Code Tabulation Areas (ZCTAs) in the New York metro study region, from the model fitted to the simulated 8 percent sample of areas (Sections 4.4 and 5.5). The color scale (0 to 0.51 orders per household per year) is shared with Figure 2 so the two regions can be compared directly; gray areas have no modeled rate. Predicted demand peaks in the urban core and declines toward the region's periphery. Map lines delineate study areas and do not necessarily depict accepted national boundaries.**

![Figure 1](figures_new/Figure_1.png)


**Figure 2. Predicted demand for shower steamers in the Southeast. Companion to Figure 1 for the Southeast study region: Layer 2 (GeoAI gradient-boosting) predicted demand for the steamers product, predicted orders per household per year, for each of the 5,057 ZIP Code Tabulation Areas (ZCTAs) in the region, from the model fitted to the simulated 8 percent sample of areas (Sections 4.4 and 5.5). The color scale (0 to 0.51 orders per household per year) is the same as in Figure 1; gray areas have no modeled rate. Demand concentrates in the metropolitan areas (Atlanta, Charlotte, Miami, Nashville and the Florida corridor) against a low-rate rural background. Map lines delineate study areas and do not necessarily depict accepted national boundaries.**

![Figure 2](figures_new/Figure_2.png)


**Figure 3. Agreement between the econometric and GeoAI layers. Each point is one of the 5,576 ZIP Code Tabulation Areas (ZCTAs) in the two study regions, plotted by its predicted log order rate for steamers under Layer 1 (the Fay–Herriot (FH) econometric model; horizontal axis) and Layer 2 (GeoAI gradient boosting; vertical axis); blue points are the Southeast and vermillion points the New York metro area, and the black line is the 45-degree line of exact agreement. The two layers agree closely overall (Pearson correlation 0.941; Spearman correlation 0.888), and disagreement concentrates in the extreme urban tail at the right, where Layer 2 flattens the highest Layer 1 predictions (Sections 5.2 and 5.5).**

![Figure 3](figures_new/Figure_3.png)


**Figure 4. Simulated and observed demand surfaces over the same geographies. Each surface is standardized (converted to z-scores), so that spatial pattern, not level, is compared. Left column: SIMULATED. The Tier 1 data-generating process's (DGP's) true log demand rate for steamers, known exactly. Right column: OBSERVED. Log establishments per household, from ZIP Code Business Patterns (ZBP) 2022 [85]. Top row (a, b): Southeast; bottom row (c, d): New York metro. All four panels use the same classes, in standard-deviation (sd) units, shown in the shared legend above the panels; gray areas lack an observed outcome or a simulated rate. Roughness is reported as measured, not eyeballed: Moran's I of the surface is 0.70 for the simulated steamers surface and 0.39 for the observed business-count surface, and the short-lag semivariance ratio (semivariance among ZCTA pairs under 15 km apart, as a fraction of total surface variance) is 0.63 simulated against 0.95 observed: the observed surface carries nearly all of its variance at the shortest observable scale.**

![Figure 4](figures_new/Figure_5.png)


**Figure 5. Estimator performance in the simulation tier and the real-data tier. RMSE is root mean squared error on the log-rate scale, and estimators appear in the same order in both RMSE panels: ordinary least squares (OLS), the best spatial model, Fay–Herriot (FH) shrinkage, and GeoAI. (a) Tier 1 (simulation, canonical run): recovery RMSE against the known data-generating process (DGP) truth. Fay–Herriot 0.512 for steamers and 0.529 for trio, against GeoAI 0.606 and 0.665; the canonical run has no error bars. (b) Tier 2 (real data): out-of-sample RMSE against observed 2022 outcomes, as means ± 1 standard deviation (sd) across the 24 sample draws of Section 5.7, for the four original evaluations: business counts (ZBP; ZIP Code Business Patterns), tax returns per household (SOI ret; Statistics of Income), business returns per household (SOI bus) and the 2019-to-2022 temporal transfer (Transf); the fifth, electronic-shopping evaluation is reported in Table 5 and Section 5.7. (c) Top-decile overlap: the share of each estimator's top decile of areas that is also in the grading target's top decile (Tier 1: canonical run, steamers only; Tier 2: 24-draw means ± 1 sd, for Fay–Herriot and GeoAI on each of these four evaluations). The color key for all three panels is the shared legend above the figure. Levels are not commensurate across tiers, because the grading targets differ. The orderings within each tier are the content.**

![Figure 5](figures_new/Figure_6.png)


**Figure 6. Interval coverage across tiers. All bars are 24-draw means ± 1 standard deviation (sd), in percent, against the dashed line at the nominal 95 percent (key in the legend above the axes). Tier 1 (T1; Section 5.4): coverage of nominal 95 percent Fay–Herriot (FH) intervals against the known truth, for steamers (Stm) and trio, on sampled areas (samp) and on all areas (all). Gray bars are the raw plug-in intervals and blue bars the bootstrap-calibrated intervals. Black diamonds mark the canonical single run (Tier 1) on the raw bars; its sampled-area values (83.9 percent steamers, 82.8 percent trio) sit below the draw means used in every comparison in the text. Tier 2 (T2; vermillion): the share of held-out ZCTAs whose observed 2022 log rate falls inside the real-data intervals, averaged over the same 24 sample draws, for business counts (ZBP), tax returns per household (SOI ret.), business returns per household (SOI bus.) and the 2019-to-2022 temporal transfer (Transf.), interval behavior against a noisy observed target, not true coverage. The fifth evaluation, electronic-shopping establishments, whose behavior averages 29.6 percent, is reported in Table 5 and Section 5.8.**

![Figure 6](figures_new/Figure_7.png)


