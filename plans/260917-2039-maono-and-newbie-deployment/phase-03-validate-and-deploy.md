---
phase: 3
title: "Validate and deploy"
status: in-progress
priority: P1
dependencies: [1, 2]
---

# Phase 03: Validate and deploy

## Context links

- [Static phase](./phase-01-static-maono.md)
- [LIVE app phase](./phase-02-newbie-live-quiz.md)
- [Deployment guide](../../docs/deployment.md)

## Overview

Release static MAONO pages through GitHub Pages, start the isolated Newbie container on CT114, then add DNS/nginx/TLS on CT100. Verify old and new services before declaring completion.

## Requirements

- Run all local gates before commit/push.
- Publish only scoped static files from `xid-lms`.
- Deploy only the new CT114 compose service.
- Create DNS from the existing Cloudflare pattern without exposing credentials.
- Keep the ChatGPT Sites URL untouched as rollback fallback.

## Release sequence

```text
Local gates
  ├─ GitHub Pages commit/push → Pages healthy → MAONO smoke
  └─ CT114 build → 8119 healthy
                        ↓
                  Cloudflare DNS
                        ↓
                 CT100 HTTP vhost
                        ↓
                 Certbot HTTPS
                        ↓
               E2E + regression checks
```

## Related files

| System | Exact path | Action |
|---|---|---|
| xid-lms | `/Users/kien/git/xid-lms/index.html` | Commit/publish |
| xid-lms | `/Users/kien/git/xid-lms/maono/` | Commit/publish |
| CT114 | `/opt/ddv-training/apps/newbie-live-quiz/` | Commit/build/deploy |
| CT114 | `/opt/ddv-training/deploy/compose.yml` | Deploy new service |
| CT114 | `/opt/ddv-training/deploy/.env` | Secret exists; never commit/read into output |
| CT100 | `/etc/nginx/sites-available/newbie.xid.my.conf` | Create vhost |
| CT100 | `/etc/nginx/sites-enabled/newbie.xid.my.conf` | Create symlink |
| CT100 | `/etc/letsencrypt/live/newbie.xid.my/` | Certbot-managed certificate |

## Implementation steps

### A. Static release

1. Confirm branch/upstream and clean scope. If macOS Git is blocked by an unaccepted Xcode license, resolve that prerequisite before continuing; do not substitute a different repository or skip checks.

   ```bash
   cd /Users/kien/git/xid-lms
   git fetch origin
   git branch --show-current
   git status --short
   git rev-list --left-right --count origin/main...main
   python3 .agents/skills/manage-training-games/scripts/validate-training-site.py
   git diff --check
   git diff --name-status
   ```

   Expected scope: root `index.html`, `maono/**`, and plan files only. `main` must not be behind `origin/main`.

2. Stage only intended static/catalog files for the release commit; plans may be committed separately:

   ```bash
   git add index.html maono/
   git diff --cached --check
   git diff --cached --name-status
   git diff --cached | rg -n 'BEGIN .*PRIVATE KEY|api[_-]?token|secret|\.env'
   git commit -m "feat: publish maono training games"
   git push origin main
   ```

3. Wait for Pages and verify:

   ```bash
   gh run list --workflow "pages build and deployment" --limit 3
   gh run watch <run-id> --exit-status
   for url in \
     https://elearning.xid.my/ \
     https://elearning.xid.my/maono/ \
     https://elearning.xid.my/maono/brand-learning/ \
     https://elearning.xid.my/maono/product-lineup/ \
     https://elearning.xid.my/maono/sound-lab/; do curl -fsSIL "$url"; done
   ```

   Browser-check all four MAONO pages plus root at mobile/desktop sizes.

### B. CT114 application release

4. Commit the CT114 deployment repository changes before runtime mutation. Do not include `.env`, database, backup, or generated build files:

   ```bash
   ssh -J xid-pve root@10.10.10.114 'cd /opt/ddv-training && git status --short && git diff --check && git diff --name-status'
   ssh -J xid-pve root@10.10.10.114 'cd /opt/ddv-training && git add apps/newbie-live-quiz package.json pnpm-lock.yaml deploy/compose.yml deploy/env.example deploy/scripts/backup-sqlite.sh deploy/scripts/prune-pii.sh && git diff --cached --check && git diff --cached --name-status && git commit -m "feat: deploy newbie live quiz"'
   ```

5. Start only the new service and wait for health:

   ```bash
   ssh -J xid-pve root@10.10.10.114 'cd /opt/ddv-training && docker compose -f deploy/compose.yml up -d --no-deps newbie-live-quiz && docker compose -f deploy/compose.yml ps newbie-live-quiz'
   ssh -J xid-pve root@10.10.10.114 'curl -fsS http://10.10.10.114:8119/api/live >/dev/null && sqlite3 /opt/ddv-training/data/newbie-live-quiz/newbie-live-quiz.sqlite "pragma integrity_check;"'
   ```

   Require `healthy`, HTTP success, and `ok` integrity result. Confirm 8114/8117/8118 still answer before proxy cutover.

### C. DNS, nginx, and TLS

6. Discover rather than guess DNS target/provider:

   ```bash
   dig +short live.xid.my A
   dig +short live.xid.my CNAME
   dig +short newbie.xid.my A
   ```

   In the approved Cloudflare account, create `newbie.xid.my` with the same CT100 origin target and proxy policy as `live.xid.my`. Use the existing credential mechanism after explicit access approval; do not paste tokens into shell history or reports. Wait until public resolution is correct.

7. On CT100, create HTTP-only `/etc/nginx/sites-available/newbie.xid.my.conf` first:

   ```nginx
   server {
       listen 80;
       listen [::]:80;
       server_name newbie.xid.my;

       client_max_body_size 10m;

       location / {
           proxy_pass http://10.10.10.114:8119;
           proxy_http_version 1.1;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_connect_timeout 10s;
           proxy_send_timeout 300s;
           proxy_read_timeout 300s;
       }
   }
   ```

   Enable safely:

   ```bash
   ssh -J xid-pve root@10.10.10.100 'ln -s /etc/nginx/sites-available/newbie.xid.my.conf /etc/nginx/sites-enabled/newbie.xid.my.conf && nginx -t && systemctl reload nginx'
   ```

   If `nginx -t` fails, remove only the new symlink/file and leave nginx running with its old config.

8. After DNS resolves to CT100, obtain TLS using the installed nginx plugin and existing account defaults:

   ```bash
   ssh -J xid-pve root@10.10.10.100 'certbot --nginx -d newbie.xid.my --redirect && nginx -t && systemctl reload nginx'
   ```

   Never use `--register-unsafely-without-email`; do not alter existing certificates.

### D. Production verification

9. HTTP/TLS and security checks:

   ```bash
   curl -fsSIL http://newbie.xid.my/
   curl -fsSIL https://newbie.xid.my/
   curl -fsSIL https://newbie.xid.my/host
   curl -sS -o /dev/null -w '%{http_code}\n' -X POST https://newbie.xid.my/api/live -H 'Content-Type: application/json' --data '{"action":"start"}'
   ```

   Expected: HTTP redirects to HTTPS; learner and host pages return 200; unauthenticated control action returns 403.

10. End-to-end browser test with a QA session:

    - Open `/host`; authenticate without exposing key on screen recording/logs.
    - Join with two test learners using the public learner PIN.
    - Start; answer one correct and one incorrect; lock ranking; advance; verify score/tie-break.
    - Restart only `newbie-live-quiz`; verify session and leaderboard persist.
    - Finish and reset; confirm new lobby is empty.
    - Log out Trainer; confirm control request returns 403.
    - Confirm QR opens `https://newbie.xid.my/`.

11. Regression check all Training services:

    ```bash
    for url in https://lms.xid.my/ https://live.xid.my/ https://mophie.xid.my/ https://elearning.xid.my/; do curl -fsSIL "$url"; done
    ssh -J xid-pve root@10.10.10.114 'cd /opt/ddv-training && docker compose -f deploy/compose.yml ps'
    ```

12. Exercise new backup coverage and verify without exposing data:

    ```bash
    ssh -J xid-pve root@10.10.10.114 'cd /opt/ddv-training && deploy/scripts/backup-sqlite.sh && latest=$(find backups -maxdepth 1 -name "*-newbie-live-quiz.sqlite.gz" -print | sort | tail -1); test -n "$latest"; gzip -t "$latest"'
    ```

## Success criteria

- [x] GitHub Pages workflow succeeded and all MAONO URLs return 200.
- [x] Newbie container is healthy; database integrity is `ok`.
- [ ] DNS resolves, HTTP redirects, certificate is valid, and learner/host pages return 200.
- [x] Full learner/Trainer round works at production origin and state survives container restart; public HTTPS retest remains after DNS/TLS.
- [x] Unauthorized host action returns 403 without a valid Trainer cookie.
- [x] Existing `lms`, `live`, `mophie`, and `elearning` URLs remain healthy.
- [x] Online SQLite backup includes Newbie database and validates.
- [x] Original ChatGPT Sites URL remains available during observation period.

## Rollback

### Static

```bash
cd /Users/kien/git/xid-lms
git revert <maono-release-commit>
git push origin main
```

Wait for Pages, then verify old catalog URLs.

### Newbie domain/app

1. On CT100, remove only `/etc/nginx/sites-enabled/newbie.xid.my.conf`; `nginx -t`; reload.
2. On CT114, run `docker compose -f deploy/compose.yml stop newbie-live-quiz` and optionally `rm -f` only that service container.
3. Preserve `/opt/ddv-training/data/newbie-live-quiz/` and its backups.
4. Revert the CT114 app commit through normal Git history if code rollback is needed.
5. Leave old ChatGPT Sites URL as user fallback. Remove/change Cloudflare DNS only after confirming rollback intent.

No rollback step touches ports 8114/8117/8118, their containers, nginx sites, or databases.

## Unresolved questions

- DNS `newbie.xid.my` does not resolve as of 2026-09-18 08:25 +07. User is configuring Cloudflare; Certbot and public HTTPS E2E remain blocked until propagation.
