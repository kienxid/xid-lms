# Deployment

## Platform

GitHub Pages publishes the repository root from the `main` branch.

Production URL: <https://elearning.xid.my/>

GitHub Pages fallback: <https://kienxid.github.io/xid-lms/>

## Automatic deployment

Every push to `main` triggers a GitHub Pages deployment. No build command or environment variables are required.

The public URL structure is:

- `/` — brand catalog.
- `/<brand>/` — training catalog for one brand.
- `/<brand>/<game>/` — one self-contained training game.

To publish a new training game:

1. Add a folder containing its own `index.html` and assets under the correct brand folder.
2. Add the game card to that brand's `index.html`.
3. Commit and push both changes to `main`.
4. Confirm the Pages workflow succeeds in GitHub Actions.

To add a brand, create its top-level folder and catalog, then add one brand card to the root `index.html`. A brand catalog may display Coming Soon before it has games.

## Codex workflow

Open this repository in Codex and describe the change in plain language. Codex automatically follows `AGENTS.md` and the repo-local `manage-training-games` skill.

Include `publish`, `push`, `deploy`, or `đăng lên` only when Codex should commit and push the validated change. For example:

> Thêm folder game này vào trang training, đặt tên “Product Quiz 3”, kiểm tra và đăng lên giúp mình.

## Custom domain

The root `CNAME` configures `elearning.xid.my`. Keep this file at the repository root. Google Sites should link to the custom-domain brand or game URL, for example `https://elearning.xid.my/divoom/`.

## Rollback

Revert the faulty commit and push the revert to `main`. GitHub Pages will automatically publish the restored version.
