# ECRA Compliance — "Estimating Online Demand with Sparse Geographic Data"

Target: *Electronic Commerce Research and Applications* (ECRA), Elsevier.
Built 2026-10-25 from the IJEC canonical build in `../manuscript/` (the version
submitted to IJEC). No number, result, table, or figure changed: the build
script asserts an identical numeric-token multiset outside the reference list,
a byte-identical abstract, and full citation closure after conversion.

## Journal facts (verified 2026-10-25)

- Scope: e-commerce knowledge, technology and applications at the intersection
  of technological potential and business aims. Data Science and Business Data
  Analytics are named constituent fields of the journal.
- Editor-in-Chief: Professor Christopher Yang, Drexel University, Philadelphia,
  PA, USA. Verified from the journal's official editorial board page on
  ScienceDirect (fetched 2026-10-25). Co-Editors: Maurizio Naldi, Lina Zhou.
- Impact factor 6.8, CiteScore 12. Median first decision 1 day (publisher page).
- Subscription route: no publication fee. Optional open access APC $3,440 is
  NOT taken, per the author's no-fee rule. The cover letter states the
  subscription route.

## Guide for Authors requirements and how each is met

- **Peer-review model: double anonymized.** Verified in the Guide for Authors.
  The submission file is `manuscript_anonymised.docx` (formatted version:
  `manuscript_anonymised_formatted.docx`), with author details, acknowledgements,
  competing interests, CRediT statement, and the corresponding author's address
  carried only in the separate title page file. An identified manuscript is
  also included in the package, as in the sibling resubmission packages.
  Anonymisation verified by grep on the anonymised manuscript: no occurrence of
  the author name, the university, the city, or the GitHub account name. One
  reference (the companion manuscript) is cited in withheld form.
- **Title page (separate file):** `title_page_ecra.docx`. Carries the title,
  author name and affiliation, the corresponding author with department,
  institution, city and email, the ORCID, the CRediT authorship contribution
  statement, acknowledgements, the funding statement, the competing-interests
  declaration, an ethics statement, the data availability note with the live
  repository link, and the AI declaration. The guide asks for the corresponding
  author's full postal address. The title page gives the full institutional
  address as it appears in the IJEC package (department, university, city,
  state, country, email). No street address or postal code exists in the source
  materials, and none was fabricated. The author should confirm the portal's
  address fields at submission.
- **Abstract:** 198 words. Byte-identical to the IJEC version until the
  2026-10-25 restructure, which revised one closing clause (recorded in the
  restructure section below). Within the journal's 250-word maximum and the
  author's standing 200-word cap.
- **Keywords:** 7, the journal's maximum (1 to 7 permitted). Unchanged from the
  IJEC version.
- **Highlights: REQUIRED at this journal.** `highlights_ecra.docx` (file name
  contains "highlights"), 5 bullets, each 67 to 79 characters including spaces,
  verified programmatically against the 85-character limit. Every bullet states
  a result reported in the manuscript. (Bullet range was 65 to 79 before the
  2026-10-25 restructure replaced the fifth bullet; see below.)
- **Graphical abstract:** encouraged, not required. None supplied.
- **Manuscript format:** editable .docx, single-column. Tables are editable
  text (12 tables). Figures are embedded in the manuscript at the end and are
  also supplied as separate files in `figures_new/` (Figures 1 to 8, PNG and
  PDF), each with a caption in the manuscript, per the guide's artwork rules.
- **Reference style: ECRA's numbered variant.** The guide's primary reference
  examples are numbered ("[1] J. van der Geer, T. Handgraaf, R.A. Lupton, ..."),
  cited in text as [n], and listed in order of appearance. The guide also
  carries an author–date block (a template artifact; it is the style Spatial
  Statistics uses, not ECRA's) and states that strict formatting is not
  enforced at submission and will be applied at proof stage. We converted to the
  numbered variant because ECRA's published articles use it and the manuscript
  already cited in [n] form. Conversion: all 115 references renumbered by order
  of first appearance (main text, then tables, then figure captions), reordered,
  and reformatted (initials-first authors, LTWA journal abbreviations, volume
  (year) page range with spaced en dash, issue numbers dropped per the guide's
  primary example, books as title, edition, publisher, city, year, chapters
  with "in: Editors (Eds.)"). DOIs are encouraged by the guide, not required.
  The IJEC list carried no DOIs, so DOIs were reattached only where a verified
  match exists in the author's GA v4.2 reference list, keyed by first-author
  surname, year, and title overlap: 55 of 115 entries now carry a DOI. No DOI
  was fabricated. Closure after conversion, verified by script: every in-text
  [n] maps to exactly one entry, every entry is cited, 0 orphans, 0 dangling.
- **Declarations in the manuscript:** funding (Elsevier's standard no-grant
  sentence, already present in the source), declaration of competing interests
  (full storefront disclosure, substance unchanged from the IJEC package),
  declaration of generative AI under Elsevier's exact section heading, and a
  data availability statement. The "Data and code availability" heading was
  retitled "Data availability" to match Elsevier usage. The CRediT statement
  sits on the title page, since it would identify the author in the anonymised
  manuscript.
- **Research data: Option C.** The data availability statement names the public
  input datasets (ACS 2023, ZBP 2022 and 2019, IRS SOI 2022) and deposits the
  code and replication data on GitHub (github.com/Nsokol44/zip-demand-model).
  In the anonymised manuscript the repository address is withheld for review
  and supplied on acceptance, the same wording as the IJEC package. The title
  page and cover letter carry the live link.
- **AI declaration:** the operative sentence is identical in the manuscript,
  the title page, and the cover letter: "Claude helped with language and
  grammar." Nothing more is claimed, per the author's standing wording.
- **Competing interests:** declared in full in three places (title page,
  manuscript declaration section, cover letter), never flattened to "none."

## Framing edits (the only text changes besides references and headings)

1. Introduction: "the marketplace structure this journal's founding statement
   describes" became "the marketplace structure that the field's founding
   statement of electronic commerce research describes". The citation is to
   Zwass (1996), the founding statement of the field, which is now reference
   [1]. The IJEC wording addressed the other journal.
2. Introduction: the scope sentence now reads in ECRA's own terms,
   "electronic commerce at the intersection of technological potential and
   business aims, where data science and business data analytics meet the
   decisions of sellers who do not own platform-scale data", and the words
   "In this journal," before the Liu et al. citation were dropped, because
   that article appeared in IJEC, not ECRA. The paragraph already led with the
   seller's sparse-coverage problem, and the decision value is carried by the
   unchanged abstract, the design-at-a-glance table, and the decision layer.
3. Section heading "Data and code availability" retitled "Data availability".
4. Cover letter rewritten from scratch for ECRA (see below).
   No em dashes were introduced. The only em dashes in the manuscript are the
   two inside the IRS Statistics of Income dataset's official title in
   reference [91], which is a proper name, not author prose.

## Cover letter

Addressed to Professor Christopher Yang, Editor-in-Chief. Contents: the
seller's sparse-coverage problem framed in the journal's scope terms, the
three-layer design and the two-tier stress test, the findings stated with the
honest Bayesian verdict (best point recovery, intervals no better than the
bootstrap-calibrated baseline, no Tier 2 Bayesian claim), originality and sole
consideration, a transparency sentence disclosing the IJEC desk rejection and
the editor's judgment that the work merits another venue, the companion
manuscript disclosure, the competing interests in full, the funding statement,
GitHub-only code and data availability, the subscription route, and the AI
declaration in the author's standing wording.

## Preflight (Manuscript Builder Preflight, profile "nick")

- manuscript_anonymised.docx: fix accepted, "text identical to original: True".
  Formatted file: manuscript_anonymised_formatted.docx.
- manuscript_identified.docx: fix accepted, "text identical to original: True".
  Formatted file: manuscript_identified_formatted.docx.
- title_page_ecra.docx: fix accepted, "text identical to original: True".
  Formatted file: title_page_ecra_formatted.docx.
- Findings dispositioned: (a) AI statements differ in form across the document
  set. The operative sentence is character-identical everywhere. The cover
  letter uses the first-person form a letter requires. (b) Em-dash warning
  counts 2, both inside the IRS dataset's official title (see above).
  (c) Evidence-label warning: the methods text honestly describes the Bayesian
  layer as an eigenvector approximation to a BYM2-type model. That wording is
  the paper's own and is unchanged. (d) One audit ERROR, section cross-reference:
  the introduction says "Sections 5.1–5.9", and Section 5 has no 5.7 (the
  subsections run 5.1 to 5.6, then 5.8, 5.9, 5.10). This is pre-existing in the
  IJEC canonical and in the version IJEC handled. It was NOT changed in the
  original build, because the build was framing-only and the numeric-invariance
  gate forbids altering numbers. Flagged for the author's decision: leave it,
  renumber Section 5, or adjust the range in the introduction and Table 1.
  RESOLVED 2026-10-25: see the resolution note below.
- PDFs were rendered from the formatted DOCX files and visually inspected
  (title block, abstract, introduction, references, tables, figures). The
  anonymised PDF runs 48 pages.

## Resolution of the Section 5 numbering gap (2026-10-25)

Decision: the author chose "Renumber Section 5 to close the 5.7 gap"
(2026-10-25). Applied to the ECRA source (`manuscript_ecra.md`) only, by
`renumber_section5.py` (kept in this package; run order for a full rebuild:
build_ecra.py, then renumber_section5.py, then build_docx.py, then the
preflight fix step, then PDF rendering).

- Mapping (exactly): 5.8 → 5.7 ("Tier 2 results"), 5.9 → 5.8 ("The two tiers
  compared"), 5.10 → 5.9 ("The decision layer"). Section 5 now runs 5.1 to 5.9
  with no gap, so the introduction's "Sections 5.1–5.9" is accurate as written
  and its text is unchanged.
- Inventory first, then anchored substitution (no blind find-and-replace):
  every candidate token in the manuscript was classified in context before any
  edit. Renumbered: 30 tokens in all, 3 subsection headings and 27
  cross-references. By old number (heading included in each count): old
  5.8 → 5.7, 11 tokens; old 5.9 → 5.8, 10 tokens; old 5.10 → 5.9, 9 tokens.
  Both endpoints of the range "Sections 5.8–5.9" moved with the map (it appears
  in Table A and in Section 8 and now reads "Sections 5.7–5.8"). Table, figure
  and equation numbering in this manuscript is sequential, not section-derived,
  so nothing else derives from the section numbers.
- Deliberately NOT renumbered: the two table coefficients "−5.10" (intercepts
  in the results tables, not section references), and the endpoint of
  "Sections 5.1–5.9" in Section 2.6, which the decision leaves as written.
  No other package file (cover letter, title page, highlights) contains a
  Section 5 reference.
- Verification, scripted: the numeric-token multiset of the corrected
  manuscript differs from the pre-fix ECRA manuscript ONLY by the section
  tokens in the map — exact diff: "5.7" +11, "5.8" −1, "5.9" −1, "5.10" −9,
  total token count unchanged. A full re-scan of the corrected text confirms
  every remaining 5.7 token refers to Tier 2 results, every 5.8 to the tier
  comparison, every 5.9 to the decision layer, and the only remaining "5.10"
  strings are the two table coefficients. Rendered PDFs were visually
  inspected at the Table A page, the Section 2.6 page, and the pages carrying
  the three renumbered headings.
- Rebuilt after the fix: both DOCX manuscripts, the preflight-formatted DOCX
  files, and both PDFs. Preflight re-run on the rebuilt manuscripts
  (profile "nick"): manuscript_anonymised.docx and manuscript_identified.docx
  both fixed with "text identical to original: True" against the corrected
  source, recheck clean (no new findings), audit 0 errors with only the three
  previously dispositioned warnings (A1 AI-statement form, A2 the two em
  dashes inside the IRS dataset title, A3 evidence label). The audit's
  cross-reference ERROR no longer appears.
- Historical versions untouched: the IJEC canonical
  (`../manuscript/manuscript.md`) and the GA v4.2 source
  (`../../manuscript.md`) retain the 5.7 gap. They are the as-submitted and
  as-built records of earlier versions and were NOT modified.

## Review fixes (2026-10-25)

Three items from the author's review of this package, resolved the same day.

1. **"Pre-registered" corrected to "pre-stated" (cover letter).** The cover
   letter called the two-tier evaluation a "pre-registered stress test". No
   registry entry exists, and the manuscript's own term throughout is
   "pre-stated" (the evaluation is pre-stated; Section 6 is "a pre-stated
   test"; the criteria are the "pre-stated criteria"). A package-wide search
   found exactly one occurrence of "pre-registered" or "pre-registration",
   in the cover letter; the title page and highlights carry none. The cover
   letter now reads "We run a pre-stated stress test", the manuscript is
   unchanged, and the cover letter DOCX and PDF were rebuilt.
2. **Manuscript length: the guide sets no limit.** The Guide for Authors was
   re-read in full (ScienceDirect, fetched 2026-10-25) and searched for
   length guidance. It states NO word limit, NO page limit, and no suggested
   length for research articles, and it sets no article-type length limits.
   The word "length" does not appear in the guide in relation to manuscripts
   at all. The only length-type constraints anywhere in the guide are the
   abstract (not to exceed 250 words), highlights bullets (maximum 85
   characters each), and file sizes (150 MB per file preferred maximum). The
   manuscript runs about 19,900 words and 48 pages, with 12 tables and 8
   figures. No cuts were made, and none are required by the guide.
   (Superseded on length by the author's restructure of the same day,
   recorded in the final section below. The guide still sets no limit; the
   cut was an editorial decision, not a compliance requirement.)
3. **Repository visibility: wording substituted, because the connector
   cannot change it.** The cover letter originally stated the code is
   "openly available on GitHub at https://github.com/Nsokol44/zip-demand-model".
   Verified through the GitHub connector (2026-10-25): the repository
   Nsokol44/zip-demand-model exists and is PRIVATE ("private": true), with
   its contents intact (run_all.py, the three layer modules, data_fetch.py,
   report.py, figures.py, requirements.txt, README.md, tests/, strengthening/).
   The connector's toolset exposes no repository-settings or visibility
   operation, so the visibility could not be changed through it, and no PAT
   was used. The cover letter's availability paragraph was therefore changed
   to a truthful form: the code and replication materials are "deposited on
   GitHub" at the same address, the repository "is currently private", it
   "will be made public on acceptance, consistent with the manuscript's data
   availability statement", and the code "is available to the editors and
   reviewers on request in the meantime". This matches the manuscript's own
   statement (the code is in a GitHub repository, the link withheld for
   double-anonymized review, supplied on acceptance). **RESOLVED
   2026-10-25:** the author made the repository public himself on
   github.com the same day. Verified through the GitHub connector:
   Nsokol44/zip-demand-model now reports "private": false and its contents
   are intact (root listing: .gitignore, README.md, run_all.py, common.py,
   config.py, data_fetch.py, figures.py, layer1_econometrics.py,
   layer2_geoai.py, layer3_game.py, report.py, requirements.txt, tests/,
   strengthening/). The interim wording is retired: the cover letter's
   availability sentence is restored to its original form, "All code and
   replication materials are openly available on GitHub at
   https://github.com/Nsokol44/zip-demand-model", and that claim is now
   accurate as written. The cover letter DOCX and PDF were rebuilt from
   the corrected source.

## Unverifiable from outside the submission system

- Anything that appears only inside Editorial Manager at submission (field
  level requirements, the declarations tool's generated Word document, reviewer
  suggestion fields) cannot be verified from the guide. The guide offers the
  declarations tool as one route and the title page declaration as the other.
  This package uses the title page plus in-manuscript declarations.
- Whether the portal asks for a graphical abstract for this article type. The
  guide says encouraged only.
- The corresponding author's full postal address with street and postal code.
  Not present in any source material and not fabricated (see title page note).

## Restructure around the estimation core (2026-10-25)

Decision (the author, 2026-10-25, logged): one paper, no split. The paper
is rebuilt around its estimation core; the decision layer is demoted to a
short application section; the standalone decision / prediction paper is
deferred until real seller economics exist (it is not written, and nothing
in this package promises it). The contribution led with is the
interval-coverage failure of Section 5.4 and what to do about it. Applied
by `restructure_ecra.py` (kept in this package; it asserts its own gates
and aborts without writing if the source has drifted). The full-length
pre-restructure ECRA text is retained locally as
`manuscript_ecra_prerestructure.md`. The superseded full-length version
also remains available in the parent "ZIP Demand — IJEC" folder and in
the GA package.

Cut map (word counts are whitespace tokens over each numbered block,
headings and insert markers included, one counter used before and after):

- Section 1 (targeted edits only): 1,906 to 1,903. The decision-layer
  paragraph now states that the layer's economics are stated assumptions
  and that it is exercised once, as a short application in Section 5.9.
  The roadmap sentences match the restructured paper.
- Section 2.4 (gravity, Huff, location games): 187 to 143. The named
  location-game catalogue sentence is cut (d'Aspremont et al.; Eaton and
  Lipsey; Prescott and Visscher; Salop; Loertscher and Muehlheusser).
  Huff, the gravity lineage, the IIA relaxation, the big-data calibration,
  Applebaum, Hotelling, Loertscher, and the modern-demand-estimation
  sentence all remain.
- Section 4.5 (game-theory layer methods): 367 to 327. Compressed to
  what the application section needs: shortlist, Huff contest and
  incumbent proxy, response-strategy multipliers (Table 2), escalation
  map, payoff components with the assumed economics, the 500 draws, and
  the pre-stated rule quoted verbatim. Cut: the narrated play-through
  specification paragraph. The showcase's uncontested Huff share (3
  percent) moved into Section 5.9 so no fact was lost.
- Section 5.9: 841 to 378, and retitled "Application: the entry decision
  under stated, assumed economics". Kept: the paper's own honest framing
  verbatim in substance (an application under stated, assumed economics,
  not an empirical finding, not a headline result), all 50 shortlisted
  ZCTAs Avoid, no ZCTA clearing even the Test bar, win rates 0 to 9
  percent, the binding unit-economics constraint, and the measured flip
  points ($25.58 first flips, 9 of 50 to Test; $29.84, 40 of 50 to Test;
  Launch at about $43; acquisition lever 60 percent and 40 percent), the
  showcase ZCTA 10282 with its payoff percentiles and Figure 4, and
  Table 9. Cut, and recorded here so nothing is silent: the turn-by-turn
  play-through narrative (response probabilities 3 / 58 / 39 percent; the
  1.7 to 2.2 percent share band; the counter-move narration); the two
  small-change robustness points (no flip at $21.31 per order; a 20
  percent acquisition-cost reduction changes nothing) — the full 35-cell
  grid remains in the replication archive; the top-five flip-range
  sentence (per-ZIP thresholds remain in Table 9); and the
  machinery-validation paragraph (its point, that a pre-stated rule can
  stop an unprofitable entry program, is retained in Section 7).
- Section 6 (Bayesian rare-event layer): 1,958 to 1,519, now two
  subsections (6.1 Model, priors, and the pre-stated criteria; 6.2
  Results and verdict). Kept in full: the pre-stated test and criteria
  C1 (calibration, fails), C2 (recovery, holds) and C3 (transport, not
  assessable); the point-recovery numbers (RMSE 0.530 and 0.521, the
  lowest of any estimator); the interval verdict (sampled-area coverage
  88.5 and 91.9 percent; paired differences against calibrated and
  plug-in Fay–Herriot with their intervals; comparable widths); the
  regret comparison ($836.93 against $817.47; $483.95 against $478.26;
  paired differences with intervals); the ridge diagnostic (posterior
  size 10.37 and 13.97 against a truth of 6.0; correlation about 0.80);
  the weak field recovery (0.159 and 0.179); the convergence record
  (gates pass in 1 of 24 and 0 of 24 fits) and the sampler self-test
  (0.955 and 0.972); and the temporal pilot as one labeled paragraph
  (all four moment effects recovered; RMSE 0.513 against 0.522; regret
  $21.67 against $20.73; seven of eight replicates not run). Cut, and
  recorded here: the Section 6.1 literature catalogue (three-fold
  Fay–Herriot; divergence-index small-area models; heteroskedastic
  poverty estimation; the area-level / unit-level calibration bridge;
  direct-assisted Bayesian unit-level models; the heavy-tailed scaled
  BYM2 extension); the fuller INLA discussion and its high-performance
  extension citation; the slope credible-interval coverage figures (81.0
  and 89.4 percent); the posterior point values of sigma_b (0.446 and
  0.483) and phi (0.182 and 0.158), of which only the ridge correlation
  is retained; the temporal pilot's calendar-effects motivation
  literature and its week-by-week comparator RMSE (2.988).
- Sections 2.1 to 2.3, 2.5, 2.6, 3, 4.1 to 4.4, 4.6, 5.1 to 5.8, 7, 8 and
  9: substantively intact. The restructure script asserts the protected
  blocks are byte-identical to the pre-restructure text once citation
  brackets are stripped. Section 8 carries two cross-reference updates
  only (criterion C3 now sits in Section 6.2; the temporal extension now
  sits in Section 6). No number, result, table, or figure in the
  estimation core changed. All 12 tables and 8 figures are retained with
  their numbers unchanged.
- Length, on one consistent counter: main text (Sections 1 to 9) 14,025
  to 13,036 words; the estimation-core span measured the same way as the
  verified pre-restructure figure (Sections 2 to 5.8 plus 6 = 9,345
  words) reads 9,200 words after the restructure with the short
  Section 5.9 included, inside the author's 8,000 to 10,000 target on
  that convention; whole file 20,927 to 19,443 words including
  references, tables, and figure captions.
- Abstract: 198 words before and after. The only change is the close:
  the two decision sentences ("Under stated, assumed economics, all 50
  shortlisted ZIP codes return Avoid. We report its flip thresholds.")
  became one clause, "Applied under stated, assumed economics, the
  decision layer returns Avoid for all 50 shortlisted ZIP codes." The
  four estimation findings are unchanged.
- Highlights: bullet 5 replaced. Out: "The decision layer returns Avoid
  for all 50 shortlisted ZIP codes". In: "Estimator rankings do not
  transport from simulated to real surfaces" (67 characters), the one
  headline estimation finding the set had been missing. All five bullets
  re-verified at 85 characters or fewer, each a real result.
- References: 115 to 95. Cutting text orphaned 20 entries, which the
  closure script removed before renumbering by order of first appearance
  (old numbers): 55 (d'Aspremont, Gabszewicz and Thisse), 56 (Eaton and
  Lipsey), 57 (Prescott and Visscher), 58 (Salop), 59 (Loertscher and
  Muehlheusser), 99 (Marcis et al., three-fold Fay–Herriot), 100 (Cabello
  et al.), 101 (Das and Chambers), 102 (Acero et al.), 103 (McGovern et
  al.), 104 (Michal et al.), 106 (Abdul Fattah, Van Niekerk and Rue,
  INLA+), 107 to 114 (the temporal pilot's calendar-effects literature:
  Chevalier et al.; Warner and Barsky; Wagner and Cleland; Darbanian et
  al.; Wang et al.; Haller et al.; Webel and Smyk; Knorr-Held). Closure
  re-verified by script after renumbering: 0 orphans, 0 dangling, and
  every section cross-reference in the paper resolves to an existing
  heading.
- Cover letter revised to match the restructured paper. The findings
  section now leads with the interval failure (plug-in coverage 88.5 and
  87.6 percent against the 95 nominal, the weakly identified variance
  split, bootstrap calibration improving but not repairing, and the
  second-wave remedy), followed by diagnostic blindness and
  non-transporting rankings, then the honest Bayesian verdict. The
  decision layer is described as specified with the stack and exercised
  once as a short application, with the correct tier names (Launch,
  Test, and Avoid; the earlier draft's "Fund, Pilot, and Avoid" was an
  error and is corrected). The letter also no longer describes the
  GeoAI layer as running a conformal coverage audit, which the
  manuscript does not do. Unchanged: the addressee (Professor
  Christopher Yang), the scope-fit framing, the transparency paragraph
  disclosing the IJEC desk rejection, the companion-manuscript
  disclosure, the competing-interests declaration in full, the funding
  statement, the availability sentence ("All code and replication
  materials are openly available on GitHub at
  https://github.com/Nsokol44/zip-demand-model."), the subscription
  route, and the AI declaration with the author's exact sentence.
- Preflight after the restructure (profile "nick"): manuscript
  anonymised, manuscript identified, and title page all fixed with
  "text identical to original: True"; audit 0 errors, with only the
  three previously dispositioned warnings (A1 AI-statement form across
  document types, A2 the two em dashes inside the IRS dataset's official
  title, A3 the evidence-label note on the honest eigenvector wording).
  PDFs re-rendered from the formatted DOCX files and visually inspected
  (title and abstract page; the Section 5.9 and Section 6 pages; the
  cover letter). The anonymised PDF now runs 45 pages (48 before).
- Rebuild order from this point: build_ecra.py, renumber_section5.py,
  restructure_ecra.py, build_docx.py, the preflight fix step, then PDF
  rendering. Nothing has been submitted. Submission remains the
  author's act.

## Review fixes round 2 (2026-10-25)

Four small fixes from the author's review list, applied to the sources and
rebuilt through the full pipeline (build_docx.py, the preflight fix step,
then PDF rendering):

- **Figure 6 caption typo.** "for all four evaluationsbusiness counts"
  now reads "for all four evaluations: business counts" (manuscript_ecra.md,
  Figure 6 caption). Verified present in all four manuscript DOCX builds;
  the run-together string occurs nowhere in the package's submission files.
  (It survives only in manuscript_ecra_prerestructure.md, the retained
  pre-restructure snapshot, which is not a submission file.) No number
  changed.
- **Highlights bullet 2.** The old bullet quoted the steamers sampled-area
  coverage alone ("cover 88.5% of areas against a 95% nominal level"). It
  now reads "Plug-in Fay–Herriot intervals cover 88.5% and 87.6% of areas,
  against 95% nominal" (81 characters, within the 85-character limit),
  covering both surfaces. highlights_ecra.md/.docx/.pdf rebuilt.
- **Black text only (standing rule).** build_docx.py now forces explicit
  black (000000) on the Title and Heading 1–9 styles and their linked
  character styles, strips the theme-colour attributes, and blackens the
  Title style's paragraph border rule, replacing the python-docx template
  theme colours (Heading 1 #365F91, Heading 2/3 #4F81BD, Title #17365D).
  Style XML verified in every DOCX; rendered PDFs visually inspected
  (title, abstract, Section 1 heading, Table A) and all headings render
  black.
- **Document metadata.** The python-docx template defaults
  (dc:creator "python-docx", description "generated by python-docx") are
  scrubbed at build time: anonymised files carry an empty creator and
  lastModifiedBy and no description; identified files, the title page,
  the cover letter, and the highlights carry creator "Nicholas J. Sokol".
  PDF metadata checked after rendering: the anonymised PDF has no Author
  field (Creator "Writer", Producer "LibreOffice 24.2") and carries
  neither the author's name nor "python-docx"; the identified PDFs carry
  Author "Nicholas J. Sokol".
- Preflight re-run after these fixes (profile "nick"): manuscript
  anonymised, manuscript identified, and title page all fixed with
  "text identical to original: True" relative to the corrected sources;
  audit 0 errors, with only the three previously dispositioned warnings
  (A1, A2, A3). Nothing has been submitted.

## All-writing checker audit (2026-10-26)

At the author's direction, the Manuscript Preflight checker (profile
"nick", check -> fix -> recheck, with the mechanical cross-check audit)
was run over EVERY document in this package, not only the manuscripts.
No manuscript content was edited in this pass; the Figure 6 caption fix
and the round-2 highlight wording were verified present in the files
before the runs (below). Every run reported "text identical to original:
True", so every fix was accepted; each accepted file was re-verified for
black text (Title and Heading 1-9 styles carry an explicit 000000 colour
with no themeColor attribute) and metadata (anonymised creator blank;
identified, title page, cover letter, and highlights creator
"Nicholas J. Sokol"; no "python-docx" anywhere), its PDF rebuilt where
one exists, and the Drive copies updated in place.

Caption and highlight verification (programmatic, both anonymised
builds): "evaluationsbusiness" occurs 0 times and "evaluations:
business counts" occurs once in each of manuscript_anonymised.docx and
manuscript_anonymised_formatted.docx. Highlights bullet 2 in the final
highlights_ecra.docx reads verbatim: "Plug-in Fay–Herriot intervals
cover 88.5% and 87.6% of areas, against 95% nominal" (81 characters).

Per-document outcomes:

- **manuscript_anonymised.docx** — check: 5 findings (FONT-NAMES x14
  and FONT-THEME x288, errors; FONT-PARTIAL x79 and TYPED-BULLETS x8,
  warnings; QUOTES-MIX x68, info). The font findings are the
  build_docx.py output's theme-font references, which the round-2 pass
  had not normalised in this build; the checker normalised them. Fix
  accepted (text identical: True). Recheck: TYPED-BULLETS and
  QUOTES-MIX only, both previously dispositioned. Cross-check audit:
  0 errors, 3 warnings (A1 DISCLOSURE-AI heuristic, A2 the two em
  dashes inside the IRS dataset's official title, A3 EVID-LABEL note),
  8 info — the same three warnings dispositioned in round 2.
- **manuscript_anonymised_formatted.docx** — check: 2 findings
  (TYPED-BULLETS x8, QUOTES-MIX x68). Fix accepted (text identical:
  True). Recheck unchanged. Audit identical to the anonymised build
  (0 errors, same 3 warnings, 8 info). PDF rebuilt (45 pages, no
  Author field).
- **manuscript_identified.docx** — check: 6 findings (the anonymised
  set plus METADATA info). Fix accepted (text identical: True).
  Recheck: TYPED-BULLETS, QUOTES-MIX, METADATA. Audit: 0 errors, same
  3 warnings, 8 info.
- **manuscript_identified_formatted.docx** — check: 3 findings
  (TYPED-BULLETS, QUOTES-MIX, METADATA). Fix accepted (text identical:
  True). Recheck unchanged. Audit: 0 errors, same 3 warnings, 8 info.
  PDF rebuilt (46 pages, Author "Nicholas J. Sokol").
- **title_page_ecra.docx** — check: 5 findings (FONT-NAMES and
  FONT-THEME, errors; FONT-PARTIAL and RUN-IN-LABEL x2, warnings;
  METADATA, info). Fix removed stray bold on 2 run-in labels; accepted
  (text identical: True). Recheck: METADATA info only. Audit: 0
  errors, 3 warnings (DISCLOSURE-AI heuristic, REF-MISSING — a title
  page carries no reference list by design, VOICE-IMPERSONAL), 2 info.
- **title_page_ecra_formatted.docx** — check: 1 finding (METADATA
  info). Fix accepted (text identical: True). Recheck unchanged.
  Audit: 0 errors, same 3 warnings as the plain title page, 2 info.
  PDF rebuilt (Author "Nicholas J. Sokol").
- **cover_letter_ecra.docx** — check: 6 findings (FONT-NAMES and
  FONT-THEME, errors; FONT-PARTIAL and RUN-IN-LABEL x9, warnings;
  INLINE-ITALIC x3 and METADATA, info). Fix removed stray bold on the
  9 run-in labels; accepted (text identical: True). Recheck:
  INLINE-ITALIC and METADATA infos. Audit: 0 errors, 2 warnings
  (REF-MISSING, by design for a cover letter; VOICE-IMPERSONAL — the
  letter is first-person singular by design), 3 info. PDF rebuilt
  (Author "Nicholas J. Sokol").
- **highlights_ecra.docx** — check: 4 findings (FONT-NAMES and
  FONT-THEME, errors; FONT-PARTIAL, warning; METADATA, info). Fix
  accepted (text identical: True). Recheck: METADATA info only.
  Audit: 0 errors, 1 warning (REF-MISSING, by design), 3 info. PDF
  rebuilt (Author "Nicholas J. Sokol").

Net effect: the theme-font and stray-bold formatting defects the
checker is built to catch are now cleared from every document in the
package, with the document text byte-for-byte unchanged in substance
(the checker's own identity assertion held on all eight runs, and an
independent text-extraction comparison matched before and after on all
eight). The remaining findings are the previously dispositioned set.
Nothing has been submitted.

## Files in this package

manuscript_ecra.md (canonical ECRA source), manuscript_anonymised.docx and
manuscript_anonymised_formatted.docx (submission file) with PDF,
manuscript_identified.docx and manuscript_identified_formatted.docx with PDF,
title_page_ecra.md/.docx/_formatted.docx with PDF, cover_letter_ecra.md/.docx
with PDF, highlights_ecra.md/.docx with PDF, ECRA_COMPLIANCE.md,
conversion_report.json, build_ecra.py and build_docx.py (the conversion and
render scripts, so the build is reproducible), renumber_section5.py (the
Section 5 renumbering step, 2026-10-25), restructure_ecra.py with
restructure_report.json (the estimation-core restructure, 2026-10-25),
figures_new/ (Figures 1 to 8,
PNG and PDF). The code folder of the IJEC package is unchanged and is not
duplicated here. Nothing has been submitted. Submission remains the author's act.

## Strengthening completion: Bayesian arm integrated, Phase 4 (2026-10-26)

The Bayesian arm of Test A (the one Phase 2 item that was outstanding) is
complete. Draws 0–9 were fitted on the project VM; draws 10–23 were fitted by
the author locally under the identical shipped protocol and returned as
`test_a_bayes.json` plus `ecra_bayes_test_a_results.zip` (fit files, grading
files, predictions). Verification before integration, all programmatic: the
returned JSON strict-parses and covers all 24 draws; every one of its 24
records matches its per-draw fit file and grading file exactly on all nine
reported fields; the summary means recompute exactly from the records (the
stored standard deviations are population, ddof = 0, the same convention as
`test_a_econ.json`); the per-draw fits carry identical protocol markers
(4,000 posterior draws, the 1,000/2,000 tuning gate with re-run, gated
R-hat and ESS fields, `prior_variant` primary, the same field
parameterisation string), and each fit's convergence flag is consistent with
its gated R-hat (at most 1.01) and ESS values; one prediction file's array
archive matches its CSV exactly, and the no-ZBP-record count (74) matches the
feasibility memo. No discrepancy was found. The one surface difference is
runtime (43–99 s per draw locally against 363–722 s on the contended VM);
the protocol markers above are the evidence it is the same computation.
Integrated 57 files (14 draws x fit, arrays, grading, prediction, plus the
summary JSON) sit alongside the stored draws in `ijec-adaptation/results/`,
with sizes and SHA-256 hashes in
`strengthening/results/INTEGRATION_MANIFEST_BAYES_2026-10-26.json`. Full
verdict computations: `strengthening/results/test_a_bayes_verdicts.json`.

**Final Test A Bayesian verdicts (24 draws, log-rate scale).** RMSE
1.969 ± 0.206 (range 1.671 to 2.416), against Fay–Herriot 1.012 ± 0.013 and
GeoAI 0.944 ± 0.009 on the same draws. Q2 (does the layer fall inside the
econometric near-tie band of 1.010 to 1.012): NO. It is worse than
Fay–Herriot in 24 of 24 draws (mean paired difference +0.956 ± 0.201) and
worse than GeoAI in 24 of 24 (+1.024). Spearman −0.033 ± 0.017 (rankings
carry no signal on this outcome); top-decile overlap 0.226 ± 0.016. Q3
(interval behaviour): 0.495 ± 0.065 against Fay–Herriot's 0.296 ± 0.065,
higher in 24 of 24 draws (paired +0.199 ± 0.058), but at mean width 2.829
against 0.841 (per-draw ratio averaging 3.40), and still far from the
nominal 0.95. The extra coverage is bought with width, not earned by
calibration. Convergence gates pass in 6 of 24 fits. C3 remains not
assessable (one of the three-plus evaluations it requires has been run),
and on that one the layer falls far outside the band. The Tier 1 recovery
advantage does not transport to the observed e-commerce outcome.

**The five Bayes-dependent items, all completed and chased through the
package:** (a) `MEMO_TEST_A_ZBP_2026-10-26.md`, Bayesian section written
with the table and the Q2/Q3 verdicts above. (b) Section 8's limitations
paragraph rewritten: "transport untested" is replaced by the tested result
with its numbers. (c) Appendix A.1's C3 sentence and Appendix A.2's verdict
sentence updated (fits run for one evaluation, far outside the band, C3
still not assessable). (d) Abstract rewritten to carry the transport
failure; 199 words, counted programmatically; the one pre-existing
semicolon in the abstract was removed and three phrases compressed for
length without changing any number or claim. (e) The cover letter's
Bayesian sentence now reports the run and its result (1.97 against the
1.01 band, intervals at about half the target at about 3.4 times the
width). A package-wide stale-claim sweep after the edits finds no remaining
"fits were not run" or "transport is untested" statement in the manuscript,
appendix, cover letter, highlights, or title page. Section 6.2's forward
reference (Tier 2 Bayesian results reported in Section 8) is now accurate
as written. Highlights are unchanged: no bullet states a Bayesian Tier 2
claim, and bullet 2 (plug-in coverage 88.5% and 87.6%, 81 characters) and
the rest remain within the 85-character limit and true.

**Phase 4 checker pass (Manuscript Preflight, profile "nick", this
build).** All six documents were rebuilt from the corrected sources and
run through the checker: anonymised manuscript, identified manuscript,
title page, cover letter, highlights, and (its first checker run in this
program) the Online Appendix. Every fix was accepted with "text identical
to original: True". Audits: manuscripts 0 errors; title page 0; cover
letter 0; highlights 0; appendix 1 error, dispositioned below. Remaining
warnings are the previously dispositioned families plus two scan artifacts:
CITE-UNCITED for references [92] to [96], which are cited in Online
Appendix A (the package-level closure check counts the appendix, the
checker scans one file at a time); DISCLOSURE-AI (the operative sentence
"Claude helped with language and grammar." is identical everywhere);
EM-DASH (the two inside the IRS dataset's official title); EVID-LABEL (the
paper's own honest eigenvector wording). The appendix's single audit error
is XREF-DANGLING on "Table 4 of the main text": the target table is in the
companion manuscript by design, and the sentence names it as such. It is a
false positive of scanning the appendix standalone, recorded here rather
than edited away. Black text and fonts verified programmatically on all
six formatted DOCX files (Title and Heading styles carry explicit 000000
with no themeColor; no run in any document body uses a non-black colour;
Times New Roman throughout via the styles). Metadata: anonymised files
and the appendix carry a blank creator; identified manuscript, title
page, cover letter, and highlights carry "Nicholas J. Sokol"; no file
contains "python-docx". Anonymisation re-verified on the final anonymised
manuscript (no author name, university, city, or GitHub account string in
the text; no comments or footnotes parts; blank core properties; the PDF
has no Author field). PDFs re-rendered from the formatted DOCX files
(anonymised 41 pages, identified 42).

**Drive.** The ECRA subfolder (14rpRRfruAcNSHSaKxN44y4Y4iN7Wl0Od) was
updated in place, file IDs kept, and every updated file verified by size
against its local source: manuscript_ecra.md, cover_letter_ecra.md, both
manuscript DOCX pairs and their PDFs, title page DOCX pair, cover letter
DOCX and PDF, highlights DOCX and PDF, and this file. The Online Appendix
has never been part of the Drive set and remains local only, as before.
The GitHub repository copy of the strengthening materials is not updated
by this pass; the integrated results and verdicts live in the local build
tree and this Drive folder. Nothing has been submitted. Submission remains
the author's act.
