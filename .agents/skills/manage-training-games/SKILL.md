---
name: manage-training-games
description: Manage the static HTML training-game catalog deployed through GitHub Pages. Use when adding, importing, updating, replacing, renaming, removing, validating, publishing, or troubleshooting a training game; editing the root game catalog; fixing game links or assets; or handling Vietnamese requests such as "thêm game", "sửa trang", "đăng lên", and "publish" in this repository.
---

# Manage Training Games

Maintain the catalog without requiring the Training team to understand Git, hosting, or path rules.

## Site contracts

- Serve production at `https://kienxid.github.io/xid-lms/`.
- Publish the repository root from the `main` branch.
- Treat root `index.html` as the catalog.
- Keep each game self-contained in one top-level folder with an `index.html`.
- Treat published folder paths as stable URLs used by Google Sites.
- Assume every committed file becomes public.

## Workflow

1. Inspect `git status`, root `index.html`, the affected game folder, and `docs/deployment.md`.
2. Identify whether the request adds a game, updates an existing URL, or intentionally migrates/removes one.
3. Preserve unrelated files and user changes.
4. Implement the smallest complete change.
5. Run the validator and `git diff --check`.
6. Review the final diff and report the affected local and production URLs.
7. Commit and push only when the user explicitly requests publishing.

## Add a game

1. Inspect the supplied folder or archive before copying it into the repository.
2. Require one entry file named `index.html`.
3. Prefer a short lowercase kebab-case folder for new URLs unless the user provides a required slug.
4. Keep assets inside the game folder and use relative paths.
5. Add one card to root `index.html` with the display title, description, and folder link.
6. Do not commit the source ZIP; `*.zip` is intentionally ignored.

## Update a game

- Keep its folder name unchanged so existing Google Sites links continue working.
- Change only the requested game unless a shared catalog change is required.
- Preserve progress, scoring, storage keys, and public behavior unless the request changes them.
- Verify referenced images, scripts, styles, fonts, audio, and video exist with exact letter case.

## Rename or remove a game

- Require explicit user confirmation because existing external links may break.
- Prefer leaving the old folder with a redirect to the new URL.
- Update the root catalog and every known internal reference in the same change.
- Never silently delete another game or shared asset.

## Validate

Run:

```bash
python3 .agents/skills/manage-training-games/scripts/validate-training-site.py
git diff --check
```

Fix every error before committing. Preview changed pages when browser tooling is available.

## Publish

Treat `publish`, `push`, `deploy`, and `đăng lên` as permission to commit and push the scoped changes.

1. Fetch and confirm `main` is not behind `origin/main`.
2. Stage only intended files.
3. Scan the staged diff and filenames for secrets.
4. Create a concise conventional commit without AI attribution.
5. Push without force.
6. Wait for the GitHub Actions workflow named `pages build and deployment`.
7. Verify the catalog and affected game URLs return HTTP 200.

If publishing was not requested, leave validated changes uncommitted and explain how to publish later.

## Completion report

Return:

- What changed.
- Validation result.
- Commit hash and deployment result when published.
- Direct production URL for every affected game.
- Any unresolved question at the end.

Use `scripts/validate-training-site.py` as the deterministic pre-publish gate.

