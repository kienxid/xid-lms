---
title: "MAONO and Newbie deployment"
date: 2026-09-18
status: completed
---

# MAONO and Newbie deployment

## Context

Publish three MAONO static games and move Newbie All-Brand Quiz from temporary ChatGPT Sites hosting to isolated CT114/CT100 infrastructure.

## What happened

- Published MAONO through commit `983ba5e`; Pages and 4 production URLs passed.
- Ported Newbie to Next.js 16 + SQLite; pushed deployment commit `4170666`.
- Built and started only `ddv-newbie-quiz`; existing LIVE.QUIZ and MOPHIE remained healthy.
- Enabled CT100 proxy and Let’s Encrypt HTTPS after user-managed Cloudflare DNS resolved.
- Verified 35-question flow, concurrent scoring, duplicate rejection, restart persistence, backup, QR target, and clean reset.

## Reflection

Host-side `sqlite3` created an empty root-owned database during an early smoke test, leaving the already-open app connection read-only. Correcting ownership and restarting only the new container restored writes. Future first-run checks should let the non-root container initialize SQLite before host integrity commands.

## Decisions

- Use `apps/newbie-quiz`, port 8119, dedicated data volume, and server-issued cookies.
- Keep answers and Trainer key server-only.
- Preserve the old ChatGPT Sites URL through the observation period.
- Leave Cloudflare changes to the user; do not infer DNS authority.

## Next

1. Share the Trainer key through the existing secure channel when the training owner is ready.
2. Observe the first live session and keep the ChatGPT Sites fallback during the agreed window.

## Unresolved questions

None.
