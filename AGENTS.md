# XID Training Games

## Purpose

Maintain the public static training games linked from Google Sites.

Production: <https://kienxid.github.io/xid-lms/>

## Required skill

For requests to add, update, remove, rename, validate, or publish a training game, read and follow `.agents/skills/manage-training-games/SKILL.md` completely before changing files.

## Repository model

- GitHub Pages publishes the repository root from `main`.
- The root `index.html` is the game catalog.
- Each game lives in a top-level folder with its own `index.html` and local assets.
- A published folder path is a public contract because Google Sites may link to it directly.
- The repository and deployed files are public.

## Non-negotiable rules

- Preserve every existing published folder name and URL unless the user explicitly approves a migration.
- When a rename is required, keep the old URL working with a redirect unless the user confirms it is unused.
- Never add secrets, credentials, tokens, private data, `.env` files, or private keys.
- Use relative asset URLs. Root-relative URLs such as `/assets/image.png` break under the `/xid-lms/` project path.
- Treat path letter case as significant because GitHub Pages runs on a case-sensitive filesystem.
- Keep changes limited to the requested game and the root catalog entry.
- Do not force-push, rewrite history, or discard unrelated changes.
- Push only when the user explicitly says `publish`, `push`, `deploy`, or `đăng lên`.

## Required validation

Run before every commit or publish:

```bash
python3 .agents/skills/manage-training-games/scripts/validate-training-site.py
git diff --check
```

Fix all reported errors. After a requested publish, push `main`, wait for the `pages build and deployment` workflow, and verify the affected production URLs return HTTP 200.

