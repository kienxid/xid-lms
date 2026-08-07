---
title: Multi-brand training catalog
status: completed
date: 2026-08-07
---

# Multi-brand training catalog

## Overview

Move the existing Divoom catalog and games under `/divoom/`, add a Pitaka placeholder at `/pitaka/`, and turn the root page into the brand catalog.

## Phases

- [x] Create the root brand catalog and Pitaka placeholder.
- [x] Move Divoom pages into `divoom/` and update its catalog links.
- [x] Update repository guidance and validation for brand-scoped games.
- [x] Validate routes, assets, responsive layout, and custom-domain paths.

## Dependencies

- Keep the root `CNAME` file for `elearning.xid.my`.
- Preserve all existing game behavior and assets.

## Success criteria

- `/` lists Divoom and Pitaka brands.
- `/divoom/` contains the current Divoom catalog and all seven games.
- `/pitaka/` displays Coming Soon.
- Legacy top-level game paths are removed without redirects because they were not in use.
- Repository validation and browser route checks pass.

## Unresolved questions

None.
