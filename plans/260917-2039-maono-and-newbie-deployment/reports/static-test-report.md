# Static MAONO Phase 01 test report

Date: 2026-09-17
Scope: `index.html`, `maono/`, Phase 01 acceptance criteria
Result: PASS

## Gates

- PASS — `PATH=/Library/Developer/CommandLineTools/usr/bin:/usr/bin:/bin python3 .agents/skills/manage-training-games/scripts/validate-training-site.py`
  - Output: `OK: brand catalogs, game entry points, local assets, public files, and URL stability validated`
- PASS — `PATH=/Library/Developer/CommandLineTools/usr/bin:/usr/bin:/bin git diff --check`
- PASS — all inline JavaScript parsed with Node `vm.Script`:
  - Brand Learning: 1 script
  - Product Lineup: 1 script
  - Sound Lab: 1 script
- PASS — source/destination recursive comparison. Each game is byte-identical to its supplied source except the intentionally omitted `00_READ_ME_FIRST.png`.
- PASS — no `00_READ_ME_FIRST.png`, ZIP, `.env`, or PEM file found under `maono/`.

## Local HTTP and asset checks

Local server: repository root on `127.0.0.1:8765`.

All four Phase 01 entrypoints returned HTTP 200:

- `/maono/`
- `/maono/brand-learning/`
- `/maono/product-lineup/`
- `/maono/sound-lab/?qa=1`

All six referenced local asset files returned HTTP 200 with exact filename case:

- `maono/brand-learning/assets/dgm20-box.png`
- `maono/brand-learning/assets/maono-logo.png`
- `maono/brand-learning/assets/maono-wave-t5.png`
- `maono/brand-learning/assets/maonocaster-e2.webp`
- `maono/product-lineup/assets/maono-logo.png`
- `maono/sound-lab/assets/maono-logo.png`

A filesystem exact-case scan also resolved every static local `src`/`href`. Dynamic Brand Learning asset strings were verified against the same six-file runtime inventory.

## Catalog checks

- Root catalog preserves existing links `divoom/`, `mophie/`, and `pitaka/`; only `maono/` was added.
- Root footer reports `04 brand spaces`.
- MAONO catalog exposes exactly three game links:
  - `brand-learning/`
  - `product-lineup/`
  - `sound-lab/`
- MAONO back navigation is relative: `../`.
- Browser smoke test loaded the catalog and all three games with expected page titles and accessible page trees.
- Browser console reported no warnings or errors after the smoke sequence.
- The browser made one implicit `/favicon.ico` request from the catalog and received 404; no page references that file, and no game/runtime asset failed.
- Sound Lab was opened with `?qa=1`; no learner form was submitted and no tracking record was sent.

## Notes

- Repository root has no `README.md` or `CLAUDE.md`; testing used `AGENTS.md`, `docs/deployment.md`, the required `manage-training-games` skill, and the Phase 01 plan.
- Worktree contains unrelated/unscoped changes (`need_deploy/`, plans, and validator work). This report does not approve staging them; publish must stage only intended release files.
- Interactive completion/scoring flows were not submitted because Brand Learning and Product Lineup can transmit learner records. Static syntax, page load, asset, catalog, and console coverage passed.

## Unresolved questions

None for Phase 01 static deployment.
