---
phase: 1
title: "Static MAONO catalog and games"
status: pending
priority: P1
dependencies: []
---

# Phase 01: Static MAONO catalog and games

## Context links

- [Deployment guide](../../docs/deployment.md)
- [Root catalog](../../index.html)
- [Planner report](./reports/planner-report.md)

## Overview

Create one MAONO brand catalog and import three supplied offline games without changing existing published paths.

## Requirements

- Root catalog adds one `maono/` card and updates displayed brand count from 3 to 4.
- MAONO catalog links only with relative paths: `brand-learning/`, `product-lineup/`, `sound-lab/`.
- Each game keeps its supplied `index.html` behavior and local `assets/` directory.
- Do not copy unreferenced `00_READ_ME_FIRST.png` screenshots into production.
- Do not change embedded score rules, localStorage keys, tracking endpoint, or supplied question content.

## Architecture

```text
index.html
└── maono/index.html
    ├── brand-learning/index.html + assets/
    ├── product-lineup/index.html + assets/
    └── sound-lab/index.html + assets/
```

All paths are case-sensitive public contracts after first publish.

## Related code files

| Action | Exact path | Change |
|---|---|---|
| Modify | `/Users/kien/git/xid-lms/index.html` | Add MAONO brand card; update brand count |
| Create | `/Users/kien/git/xid-lms/maono/index.html` | Three-game brand catalog, based on current catalog patterns |
| Create | `/Users/kien/git/xid-lms/maono/brand-learning/index.html` | Copy supplied Brand Learning entry file |
| Create | `/Users/kien/git/xid-lms/maono/brand-learning/assets/*` | Copy four supplied referenced assets |
| Create | `/Users/kien/git/xid-lms/maono/product-lineup/index.html` | Copy supplied Product Lineup entry file |
| Create | `/Users/kien/git/xid-lms/maono/product-lineup/assets/maono-logo.png` | Copy referenced logo |
| Create | `/Users/kien/git/xid-lms/maono/sound-lab/index.html` | Copy supplied Sound Lab entry file |
| Create | `/Users/kien/git/xid-lms/maono/sound-lab/assets/maono-logo.png` | Copy referenced logo |

Sources remain under `/Users/kien/git/xid-lms/need_deploy/`; do not edit or delete them during import.

## Implementation steps

1. Preflight:

   ```bash
   cd /Users/kien/git/xid-lms
   git status --short
   test ! -e maono
   ```

   If `maono/` exists, inspect it and stop before overwriting. Preserve unrelated dirty-tree changes.

2. Create destination directories, then copy only runtime files:

   ```bash
   mkdir -p maono/brand-learning maono/product-lineup maono/sound-lab
   cp -R need_deploy/DTR_MAONO_Brand_Learning_Practice_Quiz_v2.1_Offline/index.html need_deploy/DTR_MAONO_Brand_Learning_Practice_Quiz_v2.1_Offline/assets maono/brand-learning/
   cp -R need_deploy/DTR_MAONO_Product_Lineup_Practice_Quiz_v1.6_Offline/index.html need_deploy/DTR_MAONO_Product_Lineup_Practice_Quiz_v1.6_Offline/assets maono/product-lineup/
   cp -R need_deploy/DTR_MAONO_Sound_Lab_Challenge_Zone_v1.8_Offline/index.html need_deploy/DTR_MAONO_Sound_Lab_Challenge_Zone_v1.8_Offline/assets maono/sound-lab/
   ```

3. Create `maono/index.html` using the established Divoom/mophie responsive catalog conventions. Cards:

   - `Brand Learning Practice Quiz` → `brand-learning/`
   - `Product Lineup Practice Quiz` → `product-lineup/`
   - `Sound Lab Challenge Zone` → `sound-lab/`

   Include `../` navigation to the root catalog, accessible labels, keyboard focus, mobile single-column layout, and reduced-motion support.

4. Add MAONO card to root `index.html`:

   - Mark: `MA`.
   - Metadata: `03 modules · Live`.
   - Link: `maono/`.
   - Update footer to `04 brand spaces`.
   - Do not reorder or edit existing Divoom, mophie, or Pitaka paths.

5. Verify copied asset references and forbidden absolute navigation:

   ```bash
   rg -n '(src|href)="/' maono
   rg -n '(src|href)="assets/' maono/*/index.html
   find maono -type f -print | sort
   ```

   A Google Fonts URL and the existing Google Apps Script tracking endpoint are expected external URLs. Root-relative runtime assets are not.

6. Run repository gates:

   ```bash
   python3 .agents/skills/manage-training-games/scripts/validate-training-site.py
   git diff --check
   ```

7. Preview from repository root:

   ```bash
   python3 -m http.server 8080
   ```

   Check `/maono/`, every game at desktop/mobile width, console errors, navigation, and exact-case asset loads. Use `/maono/sound-lab/?qa=1` when exercising submission; do not send training records during QA.

## Success criteria

- [ ] Validator and `git diff --check` pass.
- [ ] Root catalog has four brand spaces and all old links are unchanged.
- [ ] MAONO catalog exposes exactly three working cards.
- [ ] Each game loads without 404, missing image, or console error.
- [ ] Back navigation and keyboard focus work.
- [ ] No source ZIP, handoff screenshot, secret, or learner record is staged.

## Risk assessment

- **Case mismatch:** GitHub Pages is case-sensitive. Validate every referenced filename.
- **Large inline Product Lineup HTML:** avoid reformatting/minifying; copy byte-for-byte.
- **Tracking side effect:** Sound Lab supports `?qa=1`; use it during submission tests. Do not submit Brand Learning with real identity during smoke checks.
- **URL regression:** stage only `index.html` and `maono/`; review `git diff --name-status` before commit.

## Rollback

Before publish, remove only newly created `maono/` and revert the root card. After publish, use `git revert <release-commit>` and push the revert; never rewrite history.

## Next steps

Phase 03 publishes after Phase 02 also passes its build and security gates.

## Unresolved questions

None.
