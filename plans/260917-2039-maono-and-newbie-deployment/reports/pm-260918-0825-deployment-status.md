---
title: "MAONO and Newbie deployment status"
date: 2026-09-18
status: in-progress
---

# MAONO and Newbie deployment status

## Summary

| Track | Status | Evidence |
|---|---|---|
| MAONO static | Complete | `983ba5e`; Pages run `35293895214`; 4/4 URLs HTTP 200 |
| Newbie app | Complete | `4170666`; container healthy on CT114:8119 |
| CT100 proxy | Complete | HTTP vhost enabled; nginx config valid; route/API smoke passed |
| DNS/TLS | Waiting | `newbie.xid.my` does not resolve; user owns Cloudflare action |

## Delivered

- MAONO catalog plus Brand Learning, Product Lineup, Sound Lab published.
- Newbie Quiz ported to native Next.js 16 + SQLite WAL.
- Server-only Trainer key; HttpOnly secure host/player cookies; same-origin mutations.
- Public payload exposes 35 questions without answer/explanation fields.
- Transactional scoring verified with 20 concurrent correct answers: unique ranks 1–20; duplicate submit returns 409.
- Production-origin flow verified with 2 QA learners through all 35 questions; finished state survived isolated container restart; final reset left empty lobby.
- Newbie SQLite added to online backup and manual retention script.
- Existing `lms`, `live`, `mophie`, `elearning`, and ChatGPT Sites fallback returned HTTP 200.

## Quality gates

| Gate | Result |
|---|---|
| Static validator / diff check | Pass |
| Newbie lint | Pass; 5 non-blocking `img` optimization warnings |
| All 3 DDV apps production build | Pass |
| Docker standalone build | Pass |
| SQLite integrity | `ok` |
| Newbie container health | `healthy` |
| nginx syntax/reload | Pass |
| QR decode | `https://newbie.xid.my/` |
| Online backup test | Pass |

## Remaining

1. Cloudflare: create proxied A record `newbie.xid.my` → `112.213.85.73`.
2. After DNS resolves: run Certbot nginx flow on CT100.
3. Verify public HTTP redirect, HTTPS `/`, `/host`, API 403, and certificate.

## Unresolved questions

- When will the Cloudflare record propagate?
