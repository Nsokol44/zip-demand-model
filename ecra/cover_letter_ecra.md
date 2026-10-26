October 26, 2026

Professor Christopher Yang
Editor-in-Chief
*Electronic Commerce Research and Applications*
Drexel University, Philadelphia, PA, USA

Dear Professor Yang,

I submit the manuscript "Estimating Online Demand with Sparse Geographic Data" for consideration in *Electronic Commerce Research and Applications*.

**The problem and the fit with the journal.** A small online seller faces a simple problem. It can sell anywhere, but it can only learn where demand is by spending money in the places it tests, and its tests cover a sparse, self-selected slice of ZIP codes. That condition is the normal condition of electronic commerce, not an edge case. The question the paper answers sits at the intersection of technological potential and business aims that defines this journal's scope. Which places should a seller test, which should it scale, and which should it avoid, when the evidence comes from a thin and unrepresentative sample of places? Data science and business data analytics, two of the journal's named constituent fields, supply the methods. The paper's contribution is to benchmark those methods honestly for the population of sellers who do not own platform-scale data, and to carry the benchmark through to the decision the seller actually faces.

**What the paper does.** We run a pre-stated stress test at the sampling intensity such a seller can afford, 8% of ZIP Code Tabulation Areas (447 of 5,576), in two tiers. The first tier measures recovery on simulated surfaces whose data-generating process is known. The second benchmarks the finalists against observed outcomes from ZIP Code Business Patterns and Statistics of Income data, including a fully observed e-commerce outcome, Census counts of electronic-shopping establishments. The core under test is an estimation stack. A spatial econometrics layer paired with a Fay–Herriot small area stage is the mainstream baseline. A GeoAI audit layer checks the baseline with a flexible learner and a layer-agreement analysis. A hierarchical Bayesian rare-event layer, tested against criteria stated before it was fitted, models the zero-heavy counts that sparse demand data produce. A Huff-based decision layer is specified with the stack and exercised once, as a short application under stated, assumed economics, converting interval-valued estimates into Launch, Test, and Avoid calls.

**What it finds, stated plainly.** The central finding is an interval failure. Plug-in Fay–Herriot intervals cover 88.5% and 87.6% of sampled areas against a 95% nominal level, because the split between count noise and genuine area variation is weakly identified in a single cross-section. Bootstrap calibration improves coverage (91.4% and 90.0% on sampled areas) but does not repair it. Two candidate repairs are tested in this version: adjusted-likelihood variance estimators from the small-area literature do not repair the intervals either, while a simulated second wave of outcomes largely identifies the split (sampled-area coverage about 0.94), a repair demonstrated in simulation and not yet in the field. Two further failures accompany it. Standard spatial diagnostics detect a strong spatial process in only 17 to 42% of simulation draws at this sampling intensity, so the first diagnostic a practitioner runs is weak evidence about the process that matters. And estimator rankings do not transport across demand surfaces: the ordering that is unambiguous in simulation dissolves on observed outcomes into a near-tie. The Bayesian rare-event layer gives the best point recovery of the layers tested, and we say exactly what that is worth. On paired differences its interval coverage is indistinguishable from the bootstrap-calibrated Fay–Herriot baseline, and its targeting regret is no better in dollars. A Bayesian evaluation on the empirical tier has now been run, for the electronic-shopping outcome, and it reinforces the paper's caution rather than relieving it: the layer's held-out error is the worst of any layer tested in all 24 draws (1.97 against the econometric near-tie band of 1.01), its rankings carry no signal on that outcome, and its intervals cover only about half of the observed target despite running about 3.4 times wider than Fay–Herriot's. In the closing application, under the stated assumed economics, the decision layer returns Avoid for all 50 shortlisted ZIP codes, which is itself a decision-relevant result for a seller deciding where not to spend.

**Originality and transparency.** The manuscript is original, has not been published, and is not under consideration elsewhere. In the interest of transparency, I disclose that an earlier version was submitted to the *International Journal of Electronic Commerce* and was declined at the editorial stage on fit grounds. The editor judged that the work merits submission to another venue. The manuscript has since been reframed for this journal's applied scope, and its reference apparatus has been converted to this journal's style. A companion manuscript by the same author studies a different question, with a different estimand and different data, and the two share no text, tables, figures, or results. The companion manuscript can be identified to the editors on request, consistent with double-anonymized review.

**Competing interests.** I declare the following competing interest. The planned demand test that motivates this study will be run through storefronts operated by me. This paper uses no data from those storefronts and reports no commercial results. The stress test, the benchmark, and all results reported here are independent of any commercial activity. I have no other competing interests to declare.

**Funding.** This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

**Data and code availability.** All code and replication materials are openly available on GitHub at https://github.com/Nsokol44/zip-demand-model. The inputs are public aggregate statistics (American Community Survey 2023, ZIP Code Business Patterns 2022 and 2019 and the ZBP 2022 detail file, IRS Statistics of Income 2022). The analysis uses a fixed random seed and runs end-to-end from the deposited code. The manuscript's data availability statement follows the journal's research data policy, and the anonymized manuscript withholds the repository address only to preserve double-anonymized review.

**Submission route.** I submit under the journal's subscription route and do not elect open access.

**Declaration of generative AI and AI-assisted technologies.** During the preparation of this work, Claude helped with language and grammar. After using this tool, I reviewed and edited the content as needed and I take full responsibility for the content of the submitted article.

Thank you for considering this manuscript. I would be glad to suggest reviewers if that would help.

Sincerely,

Nicholas J. Sokol
Department of Geography and Sustainability
University of Tennessee, Knoxville
nsokol@utk.edu
