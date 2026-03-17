"""
containts context of database schemas for llm 
"""

#schemas for postgresql for llm context 

PDB_isin_records="""

Table: PDB_isin_records

Columns:
- id
- isin
- did
- name_of_the_instrument
- description_in_nsdl
- seniority
- secured_or_unsecured
- coupon_fixed
- coupon_floating
- coupon_frequency
- coupon_frequency_number
- coupon_reset_rate
- coupon_reset_condition
- coupon_reset_date
- issue_price
- face_value
- put_option_date
- put_option_price
- call_option_date
- call_option_price
- step_up_rate_bps
- step_up_condition
- step_up_date
- step_down_rate_bps
- step_down_condition
- step_down_date
- total_issue_size_cr
- base_issue_size_cr
- greenshoe_cr
- rated_or_unrated
- mode_of_placement
- taxable_or_taxfree
- record_date
- listed_or_unlisted
- listing_exchange
- reissuance
- cashflow
- remarks_blanks
- maker
- maker_date
- deriv
- deriv_date
- nsdl_autocheck
- partial_redemption_or_partly_redeem
- cashflow_link
- financial_covenants_min_nw
- financial_covenants_cad_ratio
- financial_covenants_min_pat_pbt_ebitda
- financial_covenants_de_ratio
- financial_covenants_gnp_nnpa_par_90
- shareholding_covenants_shareholder_name
- shareholding_covenants_amt_holding
- other_covenants
- total_anchor_investor_amt
- is_same_call_put
- coupon_reset_frequency
- benchmark
- spread_bps
- created_at
- updated_at
- issuer_organization_id
- current_coupon
- suspended
- date_of_Verification
- press_release_link
- restructured_isin
- coupon_additional_condition

"""

PDB_issuer_organization="""
Table: PDB_issuer_organization

Columns:
- id
- issuer_name
- issuer_alias
- issuer_industry
- ownership
- created_at
- updated_at

"""

PDB_tag="""
Table: PDB_tag

Columns:
- id
- tag
- created_at
- updated_at
- isin_id
"""

PDB_redemption="""

Table: PDB_redemption

Columns:
- id
- redemption_date
- redemption_amt
- redemption_type
- redumption_type_of_harrier
- redemption_premium
- created_at
- updated_at
- isin_id
- file_name_tag
"""

PDB_payin="""
Table: PDB_payin

Columns:
- id
- payin_date
- payin_amt
- created_at
- updated_at
- isin_id
- file_name_tag

"""

full_db_context_helper = """
 
JOINS
PDB_isin_records.issuer_organization_id = PDB_issuer_organization.id
PDB_tag.isin_id = PDB_isin_records.id          (many-per-ISIN)
PDB_redemption.isin_id = PDB_isin_records.id    (many-per-ISIN)
PDB_payin.isin_id = PDB_isin_records.id         (many-per-ISIN)
NOTE: PDB_redemption and PDB_payin have many rows per ISIN — use DISTINCT or GROUP BY when joining them to avoid row multiplication.
PDB_tag also has many rows per ISIN, but a single equality filter (WHERE t.tag = 'X') returns at most one row per ISIN, so DISTINCT is NOT needed there.
 
---
 
PDB_issuer_organization — Issuer/company/borrower master.
- id (PK)
- issuer_name → company name, borrower name, entity name
- issuer_alias → short name, ticker, abbreviation | VALS: 'NABARD','PFC','IRFC','REC','NHPC','HUDCO','NHAI'
- issuer_industry → sector, segment, vertical | VALS: 'NBFC','Bank','Infrastructure','Power','Housing Finance'
- ownership → PSU or private, government, state-owned | VALS: 'PSU','Private','State Government','Central Government'
- created_at, updated_at
 
---
 
PDB_isin_records — Core table. ISIN-level bond/security/NCD/debenture details.
- id (PK)
- isin → ISIN code, security identifier | FORMAT: 12-char, starts 'INE', e.g. 'INE001A07KL8'
- did → document ID, deal ID
- name_of_the_instrument → bond name, security name, NCD name, tranche name
- description_in_nsdl → NSDL description
- seniority → claim priority | VALS: 'Senior','Subordinate','Perpetual','Mezzanine'
- secured_or_unsecured → collateral status | VALS: 'Secured','Unsecured'
- coupon_fixed (%) → fixed rate, fixed interest rate, nominal rate
- coupon_floating (%) → floating rate, variable rate, FRB rate
- coupon_frequency → interest payment frequency | VALS: 'Annual','Semi-Annual','Quarterly','Monthly'
- coupon_frequency_number → payments per year (1=annual, 2=semi, 4=quarterly)
- coupon_reset_rate (%) → reset rate, revised rate
- coupon_reset_condition → reset trigger, repricing condition
- coupon_reset_date → next reset date, rate revision date
- issue_price → offer price, subscription price
- face_value → par value, nominal value, denomination, FV
- put_option_date → put date, investor exit date
- put_option_price → put price, exit price
- call_option_date → call date, callable date, prepayment date
- call_option_price → call price, early repayment price
- step_up_rate_bps (bps) → step-up basis points, penalty rate increase
- step_up_condition → step-up trigger, rating downgrade clause
- step_up_date → step-up effective date
- step_down_rate_bps (bps) → step-down basis points, rate decrease
- step_down_condition → step-down trigger, rating upgrade clause
- step_down_date → step-down effective date
- total_issue_size_cr (₹Cr) → total issue size, total amount raised
- base_issue_size_cr (₹Cr) → base size, minimum issue size
- greenshoe_cr (₹Cr) → greenshoe option, overallotment
- rated_or_unrated → rating status | VALS: 'Rated','Unrated'
- mode_of_placement → placement type | VALS: 'Private Placement','Public Issue'
- taxable_or_taxfree → tax status | VALS: 'Taxable','Taxfree'
- record_date → date of record, entitlement date
- listed_or_unlisted → listing status | VALS: 'Listed','Unlisted'
- listing_exchange → exchange | VALS: 'NSE','BSE','NSE & BSE'
- reissuance → tap issue, reopening, re-tap
- cashflow → cashflow available, payment schedule exists
- remarks_blanks → remarks, comments, notes
- maker → maker status, data entry done
- maker_date → data entry date
- deriv → checker status, verified
- deriv_date → verification date
- nsdl_autocheck → NSDL validation status
- partial_redemption_or_partly_redeem → partial redemption, amortizing, staggered
- cashflow_link → cashflow file link
- financial_covenants_min_nw → minimum net worth covenant
- financial_covenants_cad_ratio → capital adequacy ratio, CRAR
- financial_covenants_min_pat_pbt_ebitda → min PAT/PBT/EBITDA covenant
- financial_covenants_de_ratio → debt-to-equity, D/E, leverage ratio
- financial_covenants_gnp_nnpa_par_90 → GNPA, NNPA, NPA ratio, asset quality
- shareholding_covenants_shareholder_name → promoter name, key shareholder
- shareholding_covenants_amt_holding → promoter holding %, ownership stake
- other_covenants → additional covenants, special conditions
- total_anchor_investor_amt → anchor investor amount
- is_same_call_put → call equals put, same call and put date
- coupon_reset_frequency → reset frequency, repricing frequency
- benchmark → reference rate | VALS: 'T-Bill','Repo Rate','MCLR','G-Sec','SOFR'
- spread_bps (bps) → credit spread, basis points over benchmark
- issuer_organization_id (FK → PDB_issuer_organization.id)
- current_coupon (%) → current interest rate, running coupon, prevailing rate
- suspended → halted, inactive, trading suspended
- date_of_Verification → QC date (note: capital V in column name)
- press_release_link → rating rationale, CARE/CRISIL/ICRA report link
- restructured_isin → post-restructuring ISIN
- coupon_additional_condition → extra coupon clause
- created_at, updated_at
 
---
 
PDB_tag — Classification tags. One ISIN can have MULTIPLE tags.
- id (PK)
- tag → label, category, bond type | KNOWN VALS: 'PSU','TAXFREE','FRB','Plain Vanilla','Perpetual','AT1','Tier 2','Zero Coupon','Green Bond'
- isin_id (FK → PDB_isin_records.id)
- created_at, updated_at
 
---
 
PDB_redemption — Maturity/repayment schedule. Can have multiple rows per ISIN (amortizing).
- id (PK)
- redemption_date → maturity date, repayment date, when does it mature
- redemption_amt (₹Cr) → redemption amount, principal repayment
- redemption_type → payment structure | VALS: 'Bullet','Amortizing','Staggered','Balloon'
- redumption_type_of_harrier → full or partial redemption (note: typo in column name)
- redemption_premium → at par, at premium, exit premium
- isin_id (FK → PDB_isin_records.id)
- file_name_tag → source file reference
- created_at, updated_at
 
---
 
PDB_payin — Subscription/investment inflow records.
- id (PK)
- payin_date → payment date, subscription date, allotment date
- payin_amt (₹Cr) → subscription amount, investment amount
- isin_id (FK → PDB_isin_records.id)
- file_name_tag → source file reference
- created_at, updated_at
 
---
 
UNITS: *_cr = ₹ Crores | *_bps = basis points (0.01%) | coupon/rate fields = percentage | tenure = (redemption_date - payin_date)/365.0
 
DISAMBIGUATION:
"coupon rate"/"interest rate" (unqualified) → current_coupon
"fixed rate"/"fixed coupon" → coupon_fixed
"floating rate"/"variable rate" → coupon_floating
"issue size" (unqualified) → total_issue_size_cr
"maturity date" → PDB_redemption.redemption_date (NOT call/put dates)
"tenure"/"maturity period" → COMPUTE (redemption_date - payin_date)/365.0
"PSU bonds" → PDB_tag.tag = 'PSU'
"tax-free bonds" → PDB_tag.tag = 'TAXFREE'
"FRBs"/"floating rate bonds" → PDB_tag.tag ILIKE '%FRB%'
"perpetual bonds" → PDB_tag.tag = 'Perpetual' OR seniority = 'Perpetual'
"issuer"/"company" by name → JOIN PDB_issuer_organization, issuer_alias ILIKE '%name%'
"issued in last X" → PDB_payin.payin_date >= CURRENT_DATE - INTERVAL 'X'
"secured" → secured_or_unsecured = 'Secured'
"listed" → listed_or_unlisted = 'Listed'
"has call option" → call_option_date IS NOT NULL
"has put option" → put_option_date IS NOT NULL
Multi-tag AND (e.g. "PSU AND Tax-Free") → WHERE tag IN (...) GROUP BY ... HAVING COUNT(DISTINCT tag) = N
 
QUERY RULES:
1. Double-quote table names: public."PDB_isin_records"
2. ILIKE with % for name/alias: issuer_alias ILIKE '%NABARD%'
3. Never add LIMIT unless the user explicitly asks for a count or top-N result
4. "how many"/"count" → SELECT COUNT(DISTINCT ir.id), not SELECT *
5. "top N by X" → ORDER BY X DESC LIMIT N  (only add LIMIT when user says "top N" or specifies a count)
6. Use CURRENT_DATE for relative dates
7. Tenure = (redemption_date - payin_date) / 365.0
8. Always use SELECT * (or ir.*, io.* with aliases) — never list individual columns, except when computing derived fields like tenure_years

---

QUERY PATTERNS (what to apply for each question type)

Pattern A — Issuer / company lookup:
  JOIN PDB_issuer_organization ON issuer_organization_id = io.id
  Filter with: io.issuer_alias ILIKE '%<name>%'
  Never hard-code issuer IDs.

Pattern B — Tenure / maturity period:
  Must JOIN both PDB_payin (p) and PDB_redemption (r)
  Compute as: (r.redemption_date - p.payin_date) / 365.0
  Label the column: AS tenure_years

Pattern C — Multi-tag AND (e.g. "PSU and tax-free"):
  JOIN PDB_tag t ON ir.id = t.isin_id
  WHERE t.tag IN ('TAG1', 'TAG2')
  GROUP BY ir.id, ir.isin, ir.name_of_the_instrument
  HAVING COUNT(DISTINCT t.tag) = <number of tags required>
  Use ARRAY_AGG(t.tag) AS tags to show matched tags.

Pattern D — Date range / time window:
  Use BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL 'X'  for future windows
  Use col >= CURRENT_DATE - INTERVAL 'X'  for past windows
  Always use CURRENT_DATE, never hardcode dates.

Pattern E — Count questions ("how many"):
  SELECT COUNT(DISTINCT ir.id) — never SELECT *
  Still JOIN the needed tables for filtering.

Pattern F — Ranking / top-N:
  ORDER BY <metric_column> DESC LIMIT <N>
  Only add LIMIT when the user specifies "top N", "first N", or an explicit number. Never assume a default.

Pattern G — Option / flag checks:
  "has call option"  → call_option_date IS NOT NULL
  "has put option"   → put_option_date IS NOT NULL
  "already called"   → call_option_date < CURRENT_DATE
  "same call and put"→ call_option_date = put_option_date

Pattern H — Tag-based single filter:
  JOIN PDB_tag t ON ir.id = t.isin_id
  A single equality or ILIKE filter (WHERE t.tag = 'PSU') returns one row per ISIN — do NOT add DISTINCT.
  Only add DISTINCT if additionally joining PDB_redemption or PDB_payin in the same query.

---

FEW-SHOT EXAMPLES (NL → PostgreSQL)

---

Example 1: Org lookup with alias (Pattern A)
Q: "Show all issuances of NABARD till date."
SQL:
SELECT ir.*, io.issuer_name
FROM public."PDB_isin_records" ir
JOIN public."PDB_issuer_organization" io
    ON ir.issuer_organization_id = io.id
WHERE io.issuer_alias ILIKE '%NABARD%';

---

Example 2: Multi-table join + tenure + time window (Patterns A, B, D)
Q: "Is there any issuance with tenure greater than 5 years in the last 6 months for PFC?"
SQL:
SELECT ir.*,
       (r.redemption_date - p.payin_date) / 365.0 AS tenure_years
FROM public."PDB_isin_records" ir
JOIN public."PDB_issuer_organization" io
    ON ir.issuer_organization_id = io.id
JOIN public."PDB_payin" p ON ir.id = p.isin_id
JOIN public."PDB_redemption" r ON ir.id = r.isin_id
WHERE io.issuer_alias ILIKE '%PFC%'
AND (r.redemption_date - p.payin_date) / 365.0 > 5
AND p.payin_date >= CURRENT_DATE - INTERVAL '6 months';

"""