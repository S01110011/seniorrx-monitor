# The 2023 Beers Criteria — Concepts and Use in This Project

## What the AGS Beers Criteria are

The **Beers Criteria** are a reference list, published and periodically updated by
the **American Geriatrics Society (AGS)**, that identifies medications whose
risk–benefit balance is generally unfavorable in adults aged 65 and older — the
so-called **Potentially Inappropriate Medications (PIM)**. Originally created by
Mark Beers in 1991, they are now maintained by a multidisciplinary expert panel
(geriatrics, clinical pharmacy, pharmacology) using systematic review and formal
consensus (modified Delphi) methodology.

The 2023 update organizes the criteria into **five categories**:

1. PIM to avoid in most older adults, **independent of diagnosis** or condition;
2. PIM to avoid in older adults with **specific diseases/syndromes**
   (disease–drug interactions);
3. medications to **use with caution**;
4. clinically important **drug–drug interactions** to avoid;
5. medications that require **renal-function dose adjustment**.

**Official reference:**
American Geriatrics Society Beers Criteria® Update Expert Panel. *American
Geriatrics Society 2023 updated AGS Beers Criteria® for potentially inappropriate
medication use in older adults.* J Am Geriatr Soc. 2023;71(7):2052–2081.
doi: [10.1111/jgs.18372](https://doi.org/10.1111/jgs.18372)

## Key concepts

- **Polypharmacy**: the concurrent use of multiple medications, conventionally
  defined as **≥ 5 chronic medications** (the threshold adopted in this project —
  see `src/seniorrx/domain/value_objects.py`). **Hyperpolypharmacy**: **≥ 10**.
  Each additional medication increases the risk of interactions, adherence errors,
  and adverse reactions, even when each individual prescription is appropriate.
- **PIM (Potentially Inappropriate Medication)**: a medication whose risk exceeds
  the expected benefit in older adults, typically because of the
  pharmacokinetic/pharmacodynamic changes of aging (reduced renal/hepatic
  clearance, greater CNS sensitivity, lower homeostatic reserve).
- **Drug–drug interaction (DDI)**: an altered pharmacological effect when two
  drugs are used together (e.g., opioid + benzodiazepine potentiating respiratory
  depression).
- **Disease–drug interaction**: a drug that is generally safe but contraindicated
  or high-risk in a specific clinical condition (e.g., NSAID in heart failure).
- **Deprescribing**: the structured, supervised process of reducing or stopping
  medications whose risk has come to outweigh the benefit — the clinical action
  typically recommended after a PIM alert, never an abrupt discontinuation without
  medical assessment.

## Coding standards

Medications are coded with the **WHO Anatomical Therapeutic Chemical (ATC)**
classification and comorbidities with **WHO ICD-10**, which makes the rule
matching robust and internationally portable. Complementary explicit tools such as
the **STOPP/START** criteria (European) are planned as an alternative source (see
`docs/roadmap.md`).

## Real-world grounding

This project operationalizes the same kind of assessment described in published
pharmacovigilance research — including the author's own cross-sectional study of
polypharmacy and PIM in older adults (Chaves et al., 2020, *Brazilian Journal of
Development*), which applied the Beers Criteria and ATC classification and found
65.2% exposure to polypharmacy and 52.2% use of at least one PIM. See
[`docs/references.md`](references.md).

## IMPORTANT — Nature of the content in this repository

The `beers_pim_criteria` table (`sql/seed_beers_pim.sql`) contains an
**illustrative, educational subset** of ~24 widely cited criteria, chosen for
didactic relevance (e.g., benzodiazepines, first-generation antihistamines,
NSAIDs, glibenclamide, the "triple whammy").

- It is **not the full official table** of the 2023 AGS Beers Criteria, which
  contains dozens of additional criteria, specific doses, and exception notes;
- the complete official table is the **intellectual property of the American
  Geriatrics Society**, distributed by Wiley — consult the original publication or
  the official AGS app for real clinical use;
- the project is designed so that adding/correcting criteria is trivial (one row
  in `sql/seed_beers_pim.sql` + a cited source in the pull request — see the "New
  clinical criterion" issue template and `CONTRIBUTING.md`).

## Usage disclaimer

This software is intended for **research and education**. The alerts it generates
are decision support, not a diagnosis or automated prescription, and they **do not
replace the clinical judgement** of the pharmacist or physician responsible for the
patient.
