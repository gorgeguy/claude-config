---
name: complete-minimum
description: Second-pass rewrite of a technical document into "complete but minimum" style — every fact, citation, and number survives while words and structure shrink. Use when asked to apply complete-minimum, run an STE pass, crisp/tighten a review, design doc, incident report, or assessment, or restyle a document for action. Rewrite-only; draft content first in natural prose.
---

# Complete-Minimum Rewrite Pass

Rewrite an existing draft. Do not draft new content under this skill; draft
content-first in natural prose, then apply this pass.

## The Ideal

- **Complete:** every fact, number, identifier, citation, URL, and named
  entity in the source survives in the output. Statements repeated in the
  source may collapse to one occurrence.
- **Minimum:** the fewest words and structures that carry those facts. Cut
  hedges, meta-commentary, and rhetorical framing. Never cut evidence.

Judge every edit by both tests. Brevity that drops a fact fails. Fidelity
that keeps filler fails.

## Workflow

1. Read the source in full.
2. Rewrite with the rules below. Write to `<source-stem>-cm.md` beside the
   source unless the user names a path.
3. Spawn one audit subagent with fresh context. Do not audit your own
   rewrite inline. Instruct it to:
   - read both files completely;
   - list every source fact, number, citation, URL, or named entity that is
     missing or altered in the rewrite;
   - list every rewrite claim absent from the source (invention);
   - ignore wording and structure differences; report content only.
4. Repair every confirmed drop or invention. Re-audit after large repairs.
5. Report the drops found and repaired to the user.

## Prose Rules

- One idea per sentence. Target 20 words or fewer; treat 25 as a ceiling.
- Active voice. Present tense for description; imperative for instructions.
- Definite modals: "must" for requirements, "can" for capability, "do not"
  for prohibition. Use "should", "may", or "might" only when uncertainty is
  the actual claim.
- No hedging, no first person, no reviewer or session references.
- Reserve "Thus" and "Therefore" for genuine deduction. Otherwise put cause
  and effect in one short sentence.
- One term per concept for the whole document. Choose the term at first use
  and never alternate synonyms (restore/cleanup/rollback — pick one).

## Structural Patterns, Not a Template

Keep the source document's own outline. Apply these patterns only where
matching content already exists; force none of them:

- **Metadata table** — open with a short `| Item | Value |` table of
  identifying facts. When the document renders a judgment, add a `Verdict`
  row so the disposition is visible before any prose.
- **Findings index** — when the document contains four or more findings, add
  a `| # | Finding |` table after the metadata so a reader can jump.
- **Finding cell** — each finding gets four parts:
  1. heading with severity class and claim: `### Blocker 1: <claim>`;
  2. a bold one-sentence consequence line: `**Consequence: ...**`;
  3. evidence with citations;
  4. a numbered imperative `Required correction:` list, one testable action
     per item.
  State severity once: class in the heading, consequence in the bold line.
  Do not restate the class as a synonym ("Blocker" heading plus "Critical"
  line is a duplicate).
- **Claim headings** — headings state the finding, not the topic: "One event
  can satisfy many test cases", not "Event matching issues".
- **Verification table** — record checks performed as `| Check | Result |`,
  including checks not run and what they leave unproven.

## Telegraphic Zones

Prose gets complete sentences. Structural elements get minimum fragments:

- diagram nodes: verb-first fragments, no terminal periods
  ("poll Azure audit logs", not "The collector polls the Azure audit
  logs.");
- table cells: fragments without terminal periods, unless the cell is
  genuinely a sentence;
- headings and label-like list items: fragments.

Numbered correction lists are imperative sentences and keep their periods.

## Citations

- In prose: a `` See `path:lines`. `` sentence directly after the claim.
- In list items and table cells: a trailing parenthetical `` (`path:lines`) ``.
- Never drop a citation while rewriting. The audit pass checks this.

## Never

- Meta-commentary about the document itself: language notes, style
  disclaimers, "this document uses...".
- Certification or compliance claims about the writing style.
- A fixed outline imposed on a document that lacks the matching content.
- Fact deletion in the name of brevity.
