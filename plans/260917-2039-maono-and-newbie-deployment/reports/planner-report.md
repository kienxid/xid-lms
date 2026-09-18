---
title: "MAONO and Newbie deployment planner report"
status: completed
created: 2026-09-17
---

# MAONO and Newbie deployment planner report

## Summary

Deployment is feasible with two isolated tracks. MAONO is a low-risk GitHub Pages import. Newbie requires a runtime/auth/database port before CT114 deployment.

## Findings

- Repository has no root `README.md`; `AGENTS.md` and `docs/deployment.md` are the authoritative local guides.
- GitHub Pages publishes repository root from `main` at `elearning.xid.my`.
- Static handoffs are self-contained:
  - Brand Learning: about 1.3 MB; four local assets; existing Apps Script tracking and localStorage.
  - Product Lineup: about 4.3 MB; one local logo; large inline image data.
  - Sound Lab: about 228 KB; one local logo; `?qa=1` suppresses tracking submission.
- Newbie source is Next 16/Vinext with a Cloudflare D1 binding. It has 35 questions and 34 question image files.
- Current Newbie source hard-codes the Trainer key in both API and client. Direct deployment is unacceptable.
- Current answer scoring performs count-then-insert outside one transaction; SQLite port should close this race.
- CT114 confirmed:
  - App repo `/opt/ddv-training`.
  - Compose `/opt/ddv-training/deploy/compose.yml`.
  - Existing ports 8114, 8117, 8118; 8119 free at inspection time.
  - Existing app pattern: Node 22 standalone Next.js, `better-sqlite3`, D1 compatibility adapter, non-root Docker runtime, persistent `/data` volume, healthchecks.
- CT100 confirmed:
  - nginx site filenames use `.conf`.
  - Existing `live.xid.my` and `mophie.xid.my` proxy to CT114 and use Certbot-managed TLS.
  - No `newbie.xid.my` certificate existed at inspection time.
- Cloudflare is the DNS provider, but credential location was not discovered. Deployment must use safe discovery/approval and never expose tokens.
- Local macOS Git commands were blocked during planning by unaccepted Xcode license. This is a release prerequisite, not a reason to skip Git gates.

## Decisions

- Use `elearning.xid.my/maono/{brand-learning,product-lineup,sound-lab}/`.
- Use `newbie.xid.my`, CT114 host port 8119, container port 3119.
- Reuse CT114 `better-sqlite3` + D1 compatibility pattern.
- Use server-side Trainer login with secure HttpOnly cookie.
- Keep old ChatGPT Sites URL unchanged through production verification.
- Deploy/restart only the new compose service.

## Recommendations

- Execute Phase 01 and Phase 02 independently, then use Phase 03 as a strict integration gate.
- Commit CT114 source before starting the container.
- Extend online backup and retention scripts in the same release.
- Keep a short observation period before considering retirement of the temporary site.

## Unresolved questions

None.
