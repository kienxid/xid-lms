---
title: "MAONO catalog and Newbie LIVE Quiz deployment"
description: "Publish three MAONO static games and move the Newbie LIVE Quiz to CT114 with SQLite and server-side Trainer auth."
status: completed
priority: P1
branch: main
tags: [feature, frontend, backend, database, auth, infra]
blockedBy: []
blocks: []
created: 2026-09-17
---

# MAONO catalog and Newbie LIVE Quiz deployment

## Overview

Two release tracks, one final production gate:

1. GitHub Pages: add MAONO catalog plus three self-contained games.
2. CT114/CT100: port Newbie LIVE Quiz to native Next.js + SQLite, expose at `newbie.xid.my`.

Do not replace or redirect any existing public URL. Keep the ChatGPT Sites source URL available until the new domain passes end-to-end checks.

## Domain map

| Content | Production URL | Runtime |
|---|---|---|
| MAONO catalog | `https://elearning.xid.my/maono/` | GitHub Pages, `main` |
| Brand Learning | `https://elearning.xid.my/maono/brand-learning/` | Static |
| Product Lineup | `https://elearning.xid.my/maono/product-lineup/` | Static |
| Sound Lab | `https://elearning.xid.my/maono/sound-lab/` | Static |
| Newbie learner | `https://newbie.xid.my/` | CT114 port 8119 via CT100 nginx |
| Newbie Trainer | `https://newbie.xid.my/host` | Same app; server-side auth cookie |

## Phases

| Phase | Name | Status | Depends on |
|---|---|---|---|
| 01 | [Static MAONO catalog and games](./phase-01-static-maono.md) | Completed | None |
| 02 | [Newbie LIVE Quiz port](./phase-02-newbie-live-quiz.md) | Completed | None |
| 03 | [Validate and deploy](./phase-03-validate-and-deploy.md) | Completed | 01, 02 |

Phase 01 and Phase 02 may run in parallel. Phase 03 starts only after both pass local/build gates.

## Dependencies

- Repository root publishes from `main`; root `CNAME` remains unchanged.
- CT114: `ssh -J xid-pve root@10.10.10.114`.
- CT114 app repo: `/opt/ddv-training`; compose file: `/opt/ddv-training/deploy/compose.yml`.
- Existing CT114 bindings stay unchanged: 8114 (LMS), 8117 (LIVE.QUIZ), 8118 (mophie). Newbie uses `10.10.10.114:8119` only.
- CT100: `ssh -J xid-pve root@10.10.10.100`; nginx sites in `/etc/nginx/sites-available` and symlinks in `/etc/nginx/sites-enabled`.
- Cloudflare DNS action must use the existing approved account/provider workflow. Discover current `live.xid.my` record first; never print or commit credentials.
- Trainer key is generated and stored only in CT114 `/opt/ddv-training/deploy/.env` as `NEWBIE_QUIZ_HOST_KEY`.

## Release invariants

- No existing folder, domain, port, nginx site, container, or database is renamed or removed.
- No secret, `.env`, token, learner data, or private key enters Git or command output captured in reports.
- Only the new compose service is built/restarted.
- Static games use relative local asset URLs. Existing tracking endpoint behavior remains unchanged.
- SQLite uses WAL, `busy_timeout`, and a persistent CT114 volume.
- Trainer control actions require a server-validated `HttpOnly`, `SameSite=Strict`, `Secure` cookie.

## Acceptance criteria

- Four MAONO URLs return HTTP 200; root and MAONO catalog navigation works.
- All three games load exact-case assets; Sound Lab QA mode does not submit tracking data.
- `newbie.xid.my` learner and `/host` flows work over HTTPS.
- Learner state, answers, ranking, reset, and result persistence survive container restart.
- Trainer key is absent from client bundles, query strings, source maps, and API JSON.
- Container health is healthy on 8119; existing 8114/8117/8118 services remain healthy.
- Static validator, `git diff --check`, app lint/build/tests, nginx test, TLS, and production smoke tests pass.
- GitHub Pages workflow succeeds after `main` push.

## Rollback boundary

- Static: revert only the release commit, push the revert, wait for Pages.
- Newbie app: disable only `newbie.xid.my` nginx site and stop only `newbie-quiz`; preserve its SQLite directory.
- Existing ChatGPT Sites URL remains the fallback and is not modified during this release.

## Unresolved questions

None.
