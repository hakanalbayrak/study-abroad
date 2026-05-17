# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Phase 1 MVP of a multi-sided EdTech marketplace (students, agents, accommodation providers). The current codebase is a single-file interactive 3D campus tour. No build step, no package manager — the entire app lives in `index.html`. Deployed via GitHub Pages (`hakanalbayrak.github.io/study-abroad`).

Future phases will introduce Next.js, Supabase, and Stripe — do not scaffold or suggest these unless asked. Make small targeted edits only; never rewrite the full file.

## External Dependencies (CDN)

- **CesiumJS 1.121** — 3D globe renderer and flight animation
- **Google Photorealistic 3D Tiles** — campus-level satellite imagery (key: `GK` constant)
- **Cesium Ion** — token-based access to Cesium services (token: `CT` constant)
- **Google Fonts** — Orbitron + Exo 2

## Architecture

The app is a single HTML file with inline CSS and JS. There is no module system.

**App state machine** (one `<div id="phase-*">` visible at a time, toggled via `showPhase(id)`):

```
welcome → selectHome → atHome → selectDest → flightHud → drone → programs
```

**Key data structures in JS:**
- `ORIGIN` — fixed departure point (Istanbul coordinates)
- `CO[]` — list of selectable home countries with lat/lng/flag
- `DESTS[]` — study destinations; each entry has `campus` coordinates, `uni`, `city`, `country`, and `programs: { ug[], pg[] }`

**Flight animation:** `beginJourney()` computes a great-circle arc via `makeArc()`, animates a canvas-drawn plane entity along it using `setInterval`, then calls `zoomToCampus()`. After zooming, `droneActive=true` triggers a continuous orbit in the Cesium clock tick handler.

## Adding a Destination

Add an entry to the `DESTS` array with the same shape as the existing entries. The `campus` lat/lng should point to the university's main building for accurate drone view centering.

## Adding a Home Country

Add an entry to the `CO` array: `{n, la, lo, f}` (name, latitude, longitude, flag emoji).

## Phase 1 Remaining Work

- Fix plane icon rotation to align with flight path bearing
- Improve camera tracking during flight
- Add 9 universities: EU Business School Barcelona, Corvinus University (Hungary), Charles University (Czech Republic), GBS Malta, University of Europe Dubai, University of Vienna, Alberta College (Canada), Florida International University (USA), University of Twente (Netherlands)
- Student questionnaire (graduation level, English level, field, countries)
- Lead capture form (name, email, WhatsApp)
- Mobile responsive design
- Custom domain setup

Roadmap: https://www.notion.so/362de2a8593e8176bae2e53000bfa415
