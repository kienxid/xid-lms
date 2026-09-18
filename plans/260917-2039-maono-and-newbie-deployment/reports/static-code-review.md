# Static MAONO code review

## Scope

- Reviewed `index.html`, `maono/**`, and `.agents/skills/manage-training-games/scripts/validate-training-site.py`.
- Compared the current root catalog and published entry points against `origin/main` (`8b23986`).
- Reviewed Phase 01 requirements and the implementation report.
- Review mode: two-pass pre-landing checklist (blocking, then informational) with edge-case scouting.

## Overall assessment

**PASS WITH WARNINGS.** The Phase 01 file set satisfies the requested URL and catalog contracts. No existing brand/game path is removed or renamed. The three imported game entry points and assets are byte-identical to their supplied MAONO sources. Deployment still needs browser/production smoke testing, and the validator has a pre-existing fail-open Git subprocess defect described below.

## Critical issues

None in the reviewed Phase 01 change.

## Warnings

### 1. Validator silently skips published-URL protection when Git fails

- Evidence: `.agents/skills/manage-training-games/scripts/validate-training-site.py:86-101` runs `git diff` with `check=False`, never checks `returncode`, and parses empty stdout as success.
- Reproduced here: the subprocess returned exit 69 because the Xcode license is not accepted; `changed_published_urls()` returned `[]`, while the validator still printed `OK: ... URL stability validated`.
- Impact: a future deleted/renamed published game URL can pass the mandatory validator whenever Git is unavailable or errors.
- Current-release disposition: independent comparison with `/Library/Developer/CommandLineTools/usr/bin/git` found only modifications to `index.html` and the validator; no existing entry point or URL was deleted/renamed.
- Recommended fix: fail validation when the Git subprocess return code is non-zero and include a short sanitized error. Add a regression test for Git failure. This is not caused by the regex change but affects the gate whose output is being relied on.

### 2. Browser/runtime acceptance is not yet proven

- Static validation does not execute JavaScript, render the 4.27 MB Product Lineup document, verify console output, or prove the Google Apps Script write arrived.
- The implementation report explicitly says local HTTP preview was not run.
- Required deployment gate: in Phase 03, load all four MAONO URLs at desktop and mobile widths, verify no asset/console errors, and use `sound-lab/?qa=1` for the Sound Lab submission path.

### 3. Tracking success and client-side PII risks are inherited from the supplied games

- `maono/sound-lab/index.html:90-91` uses `fetch(..., {mode:'no-cors'})` and then displays a successful-send message. An opaque no-CORS response cannot expose an HTTP 4xx/5xx, so rejected submissions can be reported as successful.
- `maono/brand-learning/index.html:305-307,432-450` stores learner identity and tracking history in persistent `localStorage`; `maono/product-lineup/index.html:3` also persists the last payload. On shared training devices, later users or scripts on the same origin can read retained name/email/employee data.
- These behaviors are byte-identical to the supplied sources, and Phase 01 explicitly requires preserving tracking/storage behavior. Treat them as accepted inherited risk for this import, not an accidental implementation change. Before production, verify a real non-QA receipt at the Apps Script destination and define whether browser-retained PII is acceptable for Training devices.

### 4. Source-only tree can be accidentally staged

- `need_deploy/` remains untracked as intended, but root `.gitignore:1-2` does not ignore it.
- No source-only file exists under `maono/`; no `00_READ_ME_FIRST.png`, ZIP, dotenv, key/certificate, credentials JSON, source map, or learner record was found there.
- Deployment must stage an allowlist (`index.html`, `maono/`, and the intentional validator change), not `git add .`.

## Suggestions

1. Add focused validator tests for a large `data:` URI, a normal relative asset, a missing exact-case asset, an external URL, and a failing Git subprocess.
2. Do not modify the copied game HTML merely to address inherited tracking/privacy behavior without Training owner approval; doing so would conflict with the accepted byte-for-byte import requirement.
3. After Phase 03 smoke checks, update Phase 01 status through the controller/project-manager workflow; this review did not mutate plan state.

## Spec and contract verification

| Requirement | Result | Evidence |
|---|---|---|
| Root exposes MAONO and count becomes 04 | PASS | `index.html:312-343`; existing Divoom, mophie, Pitaka links unchanged |
| MAONO catalog has exactly three relative game cards | PASS | `maono/index.html:361-408`: `brand-learning/`, `product-lineup/`, `sound-lab/` |
| Four accepted MAONO entry points exist | PASS | `maono/index.html` plus each game `index.html` present |
| Exact-case local assets resolve | PASS | Independent resolver found 4/4 Brand Learning, 1/1 Product Lineup, and 1/1 Sound Lab references with exact case |
| Imported behavior/content preserved | PASS | SHA-256 of all three entry points and all copied assets matches supplied source files |
| Existing public contracts preserved | PASS | Baseline entry-point tree unchanged; no D/R status; root diff only adds MAONO and updates count |
| No source-only/sensitive artifact under MAONO | PASS | Forbidden filename scan empty; only HTML and referenced image assets present |
| Regex avoids inline-base64 pathological scan | PASS | Validator completed in 0.33 s; an 8 MB `data:` URI test produced zero matches in 0.0206 s |
| Regex still detects local assets/case errors | PASS | Normal relative path samples matched; wrong-case fixture failed with the expected missing-path error |

## Side-effect verdict

- **Catalog:** additive only; existing brands and URLs unchanged.
- **Assets:** self-contained, relative, exact-case.
- **Validator:** regex change is behavior-preserving for supported local asset references and materially removes the inline-base64 scan cost. Global URL-stability validation remains fail-open on Git errors.
- **External data:** deploying the copied games publicly exposes their intended Google Apps Script submission path and sends learner PII/results there. Sound Lab QA mode suppresses that submission; the other copied quizzes have no equivalent QA switch.
- **Verdict:** safe to proceed to Phase 03 static smoke/publish checks with explicit staging, while carrying the warnings above.

## Verification evidence

- `python3 .agents/skills/manage-training-games/scripts/validate-training-site.py` — PASS, 0.33 s.
- `/Library/Developer/CommandLineTools/usr/bin/git diff --check` — PASS.
- Wrong-case fixture — PASS as a negative test (validator exit 1; identified `assets/MAONO-logo.png`).
- Source/destination SHA-256 comparison — PASS for all three HTML files and six copied asset files.
- Browser preview — NOT RUN; deferred to Phase 03.

## Checklist coverage

- Concurrency/N+1/database/auth: not applicable to these static pages; no new server endpoint or database path.
- Error boundaries: reviewed tracking promises and validator subprocess handling; warnings recorded above.
- API contracts/input validation/data exposure: reviewed Apps Script payload path, PII persistence, and Sound Lab QA behavior.
- Backwards compatibility: verified from baseline tree and root diff.
- Type/lint/test coverage metrics: not instrumented for standalone supplied HTML; deterministic repository validator and targeted negative/performance checks used instead.

## Unresolved questions

- Does Training approve persistent learner identity/history in browser `localStorage` on shared devices?
- Is the Apps Script receipt authoritative enough to require server-confirmed acknowledgement instead of no-CORS best-effort submission?

Status: DONE_WITH_CONCERNS
Summary: Phase 01 contracts and files pass review; no URL regression, case mismatch, or source-only artifact was found in `maono/`.
Concerns/Blockers: No Phase 01 code blocker. Phase 03 must perform browser/production smoke checks; validator Git failures currently fail open, and inherited tracking/privacy behavior needs explicit operational acceptance.
