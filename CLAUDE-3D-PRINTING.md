# 3D printing: how I work, and what Claude needs to know

> Drop this into any new 3D-printing project (rename to `CLAUDE.md` in the repo root, or paste into Project instructions). It captures my setup, preferences and the hard-won lessons from the EDC rollie case project (`grishatg/3D-PRINTS`, folder `edc-cigarette-case/`). Project-specific numbers from that build are marked *(EDC case)*. Treat them as proven starting points, not rules.

---

## 1. Working with me

- **British English.** Informal but professional. Lead with the answer, keep it short.
- I write fast with typos ("desind", "priter"). Read for intent; ask **one** focused question only if genuinely ambiguous.
- **Challenge me.** If an idea won't print well, is fragile, or there's a better approach, say so and recommend. Give options with a recommendation when there's a real trade-off; I make the call.
- **Quality bar: "make sure quality is top" / "check, recheck, retest".** Verify before claiming. Say plainly what was **not** tested (e.g. tolerances unproven until I print).
- **Show renders before building print files.** I approve the look from images first, then you build the 3MF.
- **Complete, ready-to-print deliverables.** Not a sketch: a file I open, slice and print.
- Use skills/agents where they genuinely help (design critique, concept exploration, independent review).
- **Privacy:** never put my name or email in files, commits, filenames or external requests.

## 2. My kit

| Item | Detail |
|---|---|
| Printer | **Bambu Lab A1** (0.4 mm nozzle, 256 × 256 × 256 bed) |
| Multi-colour | **AMS lite** (4 slots) |
| Plate | **Textured PEI** |
| Slicer | **Bambu Studio** (I open and slice; you can't run it in the cloud) |
| Default material | **Bambu PETG-HF** (PETG HF @BBL A1 preset). PLA only for display pieces |
| Colours I've used | Grey `#9DA1A3`, Black `#1E1E20`, Yellow `#FFD00B` (Bambu PETG-HF). Earlier: Forest Green `#39541A` |

Why PETG-HF by default: things live in pockets and cars. UK car cabins hit ~55 °C; PLA softens, PETG-HF holds to ~62 °C.

## 3. Design preferences

- **Minimal hardware.** Prefer print-only solutions. On the EDC case the rule was *"no other hardware, just prints and filament"*: no glue, no screws, no steel rods. Only hardware I've already got (e.g. 2 × Ø9.51 × 2.51 mm round magnets) and **1.75 mm filament as hinge pins**. Always ask what hardware I have before designing around any.
- **Look great, feel great, sturdy.** Solid where loaded (hinges, magnets, edges), lighter elsewhere.
- **Clean, modern, "kit not gadget"** aesthetic: flat planes, chamfers (not fillets on bed edges), restrained detail. Inspirations I liked: h3li0 (clean minimal), dkdsgn/Abstractia (ripple surfaces), JanBerry Design (rugged faceted kit). Inspired by, never copied: all geometry original.
- **One accent colour, used sparingly**, for lines, initials, one hardware element. Never a fill.
- **Accent colour on outside faces is thin: only a few layers (~4 layers / 0.68 mm)** and must **not pass through** into the body colour.
- **Initials:** uppercase **"A·B"**, Helvetica-like font (**Inter Bold**, SIL OFL; bundle the TTF in the repo), ~5 mm cap height is the safe minimum. Centred, small, understated.
- Design the inside too: opening it is a moment.
- **Proportion matters.** I'll pick a slightly bigger size if it looks better (EDC case went 85 → 88 mm).

## 4. Print rules (apply by default)

- **No supports.** Overhangs ≤ 45°, horizontal holes ≤ 3 mm, V-grooves at 45° so they print face-down.
- **Decorated faces print on the bed** so inlays are crisp and flush.
- **Flush inlays** by default; colour inlays snapped to layer boundaries (first layer 0.20, then 0.16).
- Min yellow line width ~1.0 mm (detail) / 1.4–1.6 mm (frames); thinner smears on a 0.4 nozzle.
- Keep ≥ 0.8 mm wall around magnet pockets and keep inlays ≥ 0.8 mm away from them.
- Text: replace tiny dots/details with printable discs (Ø1.5); use **nonzero** winding for glyph outlines (even-odd breaks Inter's "A").

### Default profile (proven on the EDC case)
- Base preset: **0.16mm High Quality @BBL A1**, filament **Bambu PETG HF @BBL A1**.
- 0.16 mm layers (0.20 first), **4 walls (Arachne)**, **6 top / 5 bottom**, **50% gyroid**.
- **Modifiers: 100% infill + 6 walls** over hinges, end blocks, magnet/clasp areas.
- Seam at back, elephant-foot 0.15, Textured PEI, supports off.
- Multi-colour: **prime tower off + flush into infill** works well for chunky parts.
- Target: **max quality at a reasonable time** (EDC case ≈ 4 h, 47 colour swaps). Flag if a design blows up swap count; upright text on a narrow face is the usual culprit.

### Plate preferences
- **One plate where possible.** I like **print by object** for multi-part, multi-colour jobs.
- A1 by-object limits: objects **≥ 73 mm apart** (hull gap; use 74+), every object **< 25 mm tall** (rod height).
- **By-object ignores per-layer pauses / colour changes.** So no "drop the magnet in mid-print" with by-object: use **snap-in pockets** (printed lip, ~0.12 mm radial interference, 4 relief slots) instead.

## 5. Starting tolerances (A1 + PETG-HF) ⚠ not yet confirmed by a test print

| Fit | Value |
|---|---|
| 1.75 filament pin: press fit | Ø1.80 bore |
| 1.75 filament pin: free rotation | Ø2.0 bore (Ø2.1 for a spinning sleeve) |
| Hinge knuckle axial gap | 0.3 mm |
| Boss into recess clearance | 0.2 mm |
| Magnet pocket (Ø9.51) | Ø9.7 + 0.4 mm snap lip |

If a fit matters and it's unproven, offer a **10-minute tolerance coupon** (bore ladder / lip interference steps) before a 4-hour print.

## 6. Bambu Studio 3MF rules (critical: these cost a failed file last time)

1. **Never build `project_settings.config` from Bambu's development HEAD profiles.** It adds unknown and dual-nozzle (H2D) keys; Bambu then says **"Invalid configuration file"** → **"no geometry data"**.
2. **Do:** copy the **exact key set and key order** of a 3MF known to open on my Bambu Studio (e.g. `edc-cigarette-case/v7-65x15x88/AB_Rollie_Book_v7_A1_by_object.3mf`, 366 keys) and fill values from Bambu's **released** presets at a git **tag** (e.g. `v02.08.04.61`). All values are strings / string arrays. No multi-extruder variant keys.
3. **Always ship a geometry-only fallback 3MF** (no project settings). Bambu still keeps per-part filaments, modifiers and per-object walls/infill from `model_settings.config`.
4. **PrusaSlicer 3MFs are not a deliverable** for Bambu (multi-part objects collapse, colours lost). Use PrusaSlicer CLI **only for test-slicing** with an A1-emulating ini.
5. The **"Customised preset"** dialog on open is normal. Keep the project's settings.
6. Reusable tooling lives in `edc-cigarette-case/v7-65x15x88/src/`: `a1_safe.py` (settings builder), `bbsvalidate.py` (loader check across releases), `roundtrip_reslice.py`, `v7_a1_export.py` (by-object 3MF exporter). Reuse rather than rewrite.

## 7. Toolchain (cloud session)

- **Geometry:** Python + `manifold3d`, `shapely`, `trimesh`, `fonttools`, `numpy` (parametric, all dimensions as named parameters with a `checks()` function: envelope, manifold, overlaps, clearances, wall thickness).
- **Test slice:** PrusaSlicer 2.7.2 CLI headless (`QT_QPA_PLATFORM=offscreen`), installed via HTTPS apt sources (plain-HTTP apt hangs behind the proxy).
- **Bambu presets/source:** sparse git clone of `bambulab/bambustudio` (public git reads work; **GitHub releases return 403**, so don't try to download Bambu Studio binaries or work around blocks).
- **Renders:** three.js r128 from cdnjs + preinstalled Playwright/Chromium; deliver a 4-view sheet (front / open / back / base) plus a plate layout image.

## 8. Definition of done for any print file

1. Renders approved by me.
2. Geometry `checks()` all pass (manifold, envelope, clearances, walls, moving parts swing without contact).
3. Bambu loader check passes with no new flags vs a known-good file.
4. Test slice + round-trip re-slice of the shipped 3MF; report time, colour swaps, layers, grams per colour.
5. Owner-facing README: what to load in which AMS slot, plate/sequence settings, assembly steps (e.g. magnet polarity: stick together, mark touching faces, install marked face **out**), verification table with an honest **PENDING** for anything I haven't printed yet.
6. A short `HANDOVER.md` so the next session can pick up cold, plus a test-print feedback checklist mapping each failure to the parameter to tweak.
7. Commit and push; draft PR.
