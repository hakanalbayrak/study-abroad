# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A single-file interactive 3D study-abroad explorer. No build step, no package manager — the entire app lives in `index.html`. Open it directly in a browser or serve via GitHub Pages (`hakanalbayrak.github.io/study-abroad`).

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
