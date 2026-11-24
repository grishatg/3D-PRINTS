# HANDOVER: EDC rollie case ("AB Rollie Book"). Read this first.

> **Written 22 Nov 2026, 15:40 UTC; updated 23 Nov 2026 for v7.1 (first-print feedback) and 24 Nov 2026 for the wood PLA line (§0a, read that first).** This file is self-contained: a new session with only this repository can pick up the work, rebuild every file byte-for-byte, and continue. Every command below was run and checked before handover.

---

## 0. Status in one minute

| Item | State |
|---|---|
| **Current design** | **v7.1**, in `v7-65x15x88/` (folder name kept; the case is now **65 × 13.5 × 88 mm**): clamshell "book" case for 6 rollies (≤ 6 × 60 mm) plus 2 filter-tip bays. Visual language is **Design 6 "Hybrid"** (grey cover, black tray, yellow details). |
| **Print files** | **Three ripple designs**, otherwise identical: `v7-65x15x88/AB_Rollie_Book_v7_A1_by_object_{A_Flow,B_Rings,C_Topo}.3mf`. Each is a Bambu Studio project for the **Bambu Lab A1 + AMS lite**, one plate, **print by object**, with **self-pausing magnet layers**. The owner picks one after printing or viewing (Claude recommended **B · Rings**). |
| **Owner verification** | v7.0 was **opened and sliced** in Bambu Studio on the A1 (22 Nov) and **test-printed (cover only) on 23 Nov**; that feedback drove v7.1 (§6.1). **v7.1 has not yet been opened in real Bambu Studio.** Ask the owner to confirm the preview shows 2 pauses. |
| **Next action** | Owner prints a v7.1 design. Check the self-pauses fire, the magnets drop in and the case closes, warping is fixed and the yellow ripples look clean; then tune with §6. |
| **Public (MakerWorld) version** | `v7-65x15x88/makerworld/3mf/Rollie_Book_v7_A1_by_object_<design>.3mf`, built with **`INITIALS=0`**: no A·B and no "AB" in names. 15 colour swaps, about 2 h 10 m. Listing text is in `makerworld/MakerWorld_listing.md`; images (`src/render/makerworld.py`, `MW_PREFIX=pub_`) are in `makerworld/images/`. **The owner's A·B files stay private.** |
| **Backup fallback files** | `..._geometry_only_<design>.3mf`. Same parts and filaments, no print profile, so it uses the owner's own A1 presets and has **no automatic pauses**: pause by hand at screen layers 25 and 82. |
| **Repo** | `grishatg/3D-PRINTS`, folder `edc-cigarette-case/`. v7.0 arrived via merged PR grishatg/3D-PRINTS#1. v7.1 is on branch **`claude/hopeful-thompson-ysz39k`**, in draft PR **grishatg/3D-PRINTS#2** (https://github.com/grishatg/3D-PRINTS/pull/2). If that PR has been merged, `main` has everything. |
| **Backup** | The original home was `grishatg/General-`, branch `claude/elegant-turing-9djtl2`. That branch is kept as a backup, with a copy of this handover; its PR (grishatg/General-#3) was closed, not merged, when the project moved. |

---

## 0a. Wood PLA line (24 Nov 2026): the CURRENT work. Read this before §0

**What the owner prints now:** wood PLA (Bambu PLA Wood: Oak, Teak, Cherry, Walnut) on the **v10 platform**. §0–§8 describe the PETG v7.1 line, which still stands and still rebuilds identically.

**The v10 platform** is `PLATFORM=v10` plus the env that `v8_concepts` / `v9_concepts` / `w_concepts` set:
- **Shape:** squircle outline, R4.5 rounded long edges, crescent thumb scoop, pinch dishes.
- **Ends and inside:** **2 mm** end walls (owner: "go 2mm"); rounded inside (cavity R2.5, floor fillet R1.2, capsule ribs, rounded lip).
- **Magnets:** two **Ø5 × 2** magnets per half, at the opening-edge corners, sealed under **0.8 mm**. The estimated pull is about 175 g (owner target 150–200 g).
- **A·B:** a maker's mark in the back-plate corner on the hinge side, in the first 4 face-down layers.

| Item | Where / state |
|---|---|
| **Designs** | `v7-65x15x88/wood-designs/` (boards W0–W6 + README). **All six approved and built:** W1 KUMIKO, W2 RIVA, W3 DIAL, W4 PARQUET, W5 ENDGRAIN, W6 CUBES (W5/W6 replaced TAMBOUR and INLAY, which the owner rejected). Design code: `src/w_concepts.py` (`DESIGNS`). |
| **Print files** | `v7-65x15x88/wood-3mf/` (README = owner print guide).<br>• **12 production files:** 6 designs × with / without A·B (swaps with / without: KUMIKO 2/2, DIAL 7/2, RIVA 11/11, ENDGRAIN 12/7, PARQUET 16/12, CUBES 16/12). They pause and chime at **screen layer ≈ 22 (cover, z 3.56)** and **≈ 87 (tray, z 8.36)**; both magnets go in at each pause.<br>• **2 test files:** `TEST_..._glue_magnets.3mf`, KUMIKO + RIVA. `MAGNET_MODE=glue` leaves the pockets open to the face with the floor at the production depth. No pause; 2 walls, 10 % infill, 0.8 mm top minimum (~12–16 % less filament). Lean purge table `FLUSH_LEAN` in `w_export.py` (50 light→dark … 150 dark→light mm³; Bambu's dialog floor is 48, the A1 melt zone is 92 mm³): RIVA test purge 3.1 → 1.2 g. Production keeps `FLUSH`. |
| **AMS slots** | Fixed for every design: **1 Oak, 2 Teak, 3 Cherry, 4 Walnut**. |
| **Exporter** | `src/w_export.py <out> <template_dir> <design> <initials\|noinit> <production\|test>`. It reuses `v7_a1_export.layout()` / `pause_block()` and calls `a1_safe.project_config(..., fil_name='Bambu PLA Wood @BBL A1', flush=4x4)`. The template dir is the unzipped v7.0 file `superseded/v7.0-first-print/AB_Rollie_Book_v7_A1_by_object.3mf`. |
| **Verifier** | `src/w_verify.py <file.3mf> <work_dir>` reads **only the file**:<br>• loader check vs `test-slice/bambu_loader_check_baseline.txt`;<br>• settings and key order;<br>• plate;<br>• R4.5 edges and inlays-in-first-5-layers;<br>• pockets layer by layer (embed or glue);<br>• A1-emulated PrusaSlicer slice of the file's own meshes, with pause positions.<br>It must print `ALL PASS`. The reports for the shipped files are in `wood-3mf/checks/`. |
| **Expected slicer notes** | • "Floating bridge anchors" on production covers: the sealed-pocket roof.<br>• "Long bridging" / "Loose extrusions" on parts with **engraved** patterns: 45° stepped groove ceilings below z 0.7, proven by A/B clipped slices.<br>Both are benign. |
| **Next action** | 1. Owner test-prints the two TEST files and glues the magnets.<br>2. Ask about: hinge, closure pull, rollie fit, crescent / pinch feel, inlay and engraving quality in wood PLA, warping.<br>3. Then the owner prints production files; confirm the 2 self-pauses fire in real Bambu Studio / on the A1. |

**Rebuild one file** (from `v7-65x15x88/`; `tmpl` = the unzipped v7.0 3MF):
```bash
(cd src && python3 w_export.py ../wood-3mf <tmpl> kumiko initials production)
```
```bash
QT_QPA_PLATFORM=offscreen python3 src/w_verify.py wood-3mf/AB_Rollie_Book_Kumiko_wood_A1.3mf /tmp/v_kumiko
```

**Lesson (cost one bad send, 24 Nov): `v7.py` reads its env switches at IMPORT time.**
- `w_export.py` first imported `v7` before `w_concepts`. That built the files on the **old v7 platform**: round corners, R3 edges, no crescent or pinch, A·B on the bottom end. The renders were right, because `w_concepts` was imported first there.
- **The fix:**
  - import `w_concepts` first;
  - `w_export.py` now **asserts** the platform flags;
  - `w_verify.py` checks the edge radius (first-layer inset 2.6–2.75 mm a side vs 1.7–2.0 for R3) and that every inlay ends by z 0.84.
- **Any new entry script must import the concept module before `v7`.**

**Renders:** run `src/w_concepts.py <render_dir> <design> [noinit]`, then `node src/render/shotw.js <render_dir>/w_<design> front,back,open,inside,mark` (needs `http.server` on port 8770 serving `<render_dir>` with `view.html`), then `src/render/w_board.py`.

---

## 1. Where everything is

```
3D-PRINTS/
└── edc-cigarette-case/
    ├── HANDOVER.md                 ← this file
    ├── DESIGN.md                   ← "Trail Kit" design-language spec (v0.2, written at v5; v7 overrides several tokens, see §4)
    ├── README.md                   ← v1 "Topo Edition" README (historic)
    ├── EDC_Cigarette_Case_Topo.3mf, renders/, src/, stl/        ← v1 (10 king-size cigarettes, 87 × 14 × 90, M3 screw + 4 magnets)
    ├── v2-55x13x85/                ← 3 concepts: Ridgeline, Switchback, Summit (renders + src)
    ├── v3-rollies/                 ← 5 rollie concepts (book clamshell + friction cap, flush inlays)
    ├── v4-book/                    ← first Book build: vertical channels, AB monogram, 3 surface variants (Contour, Gridline, Trailhead) + 3MFs
    ├── v5-book/                    ← review-driven fixes (panel bug, magnet walls), faceted shell, inside ruler, 3MFs
    ├── v6-concepts/                ← 5 visual directions + judge's Hybrid (renders only); designer analysis in README
    ├── v6-final/                   ← Design 6 Hybrid final (Michroma A·B, 4 × 6×2 magnets, 2 mm rod): SUPERSEDED
    ├── v6-final-revB/              ← 2 sealed-in Ø9.51 magnets + filament pin, 5 slots, Inter Bold A·B, pauses: SUPERSEDED
    └── v7-65x15x88/                ← ★ CURRENT (v7.1; folder name kept, the case is now 65 × 13.5 × 88)
        ├── AB_Rollie_Book_v7_A1_by_object_{A_Flow,B_Rings,C_Topo}.3mf      ★ the files to print (3 ripple designs)
        ├── AB_Rollie_Book_v7_A1_geometry_only_{A_Flow,B_Rings,C_Topo}.3mf  fallbacks (no project settings, no auto-pause)
        ├── README.md                               owner-facing print and assembly guide + verification table
        ├── ripple_options_v7.1.png, v7_a1_plate.png  the 3 designs (front/back), A1 plate layout
        ├── renders/<design>/                       v7_front / v7_open / v7_back / v7_base .png
        ├── stl/<design>/                           9 loose STLs each (cover, tray, 6 yellow inlay bodies, sleeve)
        ├── fonts/Inter-Bold.ttf + README.md        font for the initials (SIL OFL 1.1), bundled so rebuilds need no download
        ├── test-slice/
        │   ├── a1_hq_petghf_0.16.ini               PrusaSlicer config emulating the A1 (by object, clearances, v7.1 settings + pause block)
        │   ├── a1_one_plate_B_Rings.3mf            PrusaSlicer project built from CAD (Rings)
        │   ├── roundtrip_from_shipped_3mf_B_Rings.3mf  PrusaSlicer project built FROM the shipped Bambu 3MF (round-trip proof)
        │   └── bambu_loader_check_baseline.txt     expected output of the Bambu loader check (26 benign flags per release)
        ├── superseded/                             v7.0-first-print/ (the file printed on 23 Nov, its renders, STLs, test slices) + the P1S three-plate file
        └── src/                                    all generators (see §7)
```

### Git facts
- **Branch:** `claude/elegant-turing-9djtl2` (in both repos).
- **History:** 3D-PRINTS carries the full 16-commit history of `edc-cigarette-case/`, filtered from General- with `git filter-repo --path edc-cigarette-case/` and merged with `--allow-unrelated-histories`. `git log -- edc-cigarette-case` shows every step from v1.
- **Commit trailers:** every commit ends with the `Co-Authored-By` / `Claude-Session` lines.

---

## 2. The owner and how to work with them

- **Role:** UK B2B business-development manager (energy sector) who 3D-prints as a hobby. Time-poor; writes short messages, often with typos ("desind 6", "priter"). Read them for intent.
- **Style wanted:** **British English**; informal but professional; direct; lead with the answer; concise. Challenge flawed reasoning, flag risks, give a recommendation when there's a trade-off, and default to action.
- **Quality bar:** "make sure quality is top"; "check recheck retest". Verify before claiming. Be honest about what was *not* tested; the owner values that.
- **Workflow habits:**
  - Approves designs from **renders before** any 3MF is built ("show designs before building the 3MF").
  - Wants complete, ready-to-use deliverables.
  - Likes skills and agents being used where they genuinely help. Earlier skills: `industrial-product-design-gbt`, design-judge style critique, `packaging-designer`.
- **Privacy:** never put the owner's personal details (name, email) into files, commits or external requests.

---

## 3. Hard requirements: do not break these

1. **Hardware is ONLY:**
   - **2 round magnets Ø9.53 × 2.53 mm** (re-measured 23 Nov; the owner has exactly two). Since v7.1 they are **sealed inside** the cover and tray during the print: the file pauses itself and the owner drops them in;
   - a **1.75 mm filament** hinge pin.

   **No glue, no screws, no steel rod, no other hardware.** ("no other hardware just prints and filament")
2. **All parts in PETG**, printed with Bambu's **PETG HF** profile (240 °C). The owner's spools are **Elegoo Rapid PETG** (yellow) and a **generic PETG** rated 240–260 °C at 100–200 mm/s (black); grey brand unknown. Colours: **grey** cover, **black** tray, **yellow** accents and spine sleeve. AMS lite slots **1 grey / 2 black / 3 yellow**. Don't switch to "Generic PETG HF" (220 °C, below the black's 230 °C minimum). Tell the owner **not to press Sync AMS** (non-RFID spools); map the slots in the Print dialog instead.
3. **Approved visual: Design 6 "Hybrid".**
   - **Cover:** grey PETG-HF with ripple grooves building toward the opening edge.
   - **Tray:** black.
   - **Datum line:** yellow, at the golden section; it wraps the opening edge and repeats inside the cover.
   - **Spine sleeve:** yellow, hexagonal.
4. **Initials:** **uppercase "A·B"** in a **Helvetica-like** font, which is **Inter Bold**. **5 mm** cap height, **centred on the bottom face** (the 65 × 15 end).
5. **Outside yellow is thin:** the yellow visible on the outside faces is **only a few layers** (now **4 layers = 0.68 mm**) and must **not pass through** into the grey or black body. Owner's words: "the line that is visible from the outside only make it a few layers … not pass through the rest of the black or gray".
6. **Printer: Bambu Lab A1 + AMS lite, one plate, print by object.** The owner can pause and resume by hand but wants to be told when; v7.1 does it automatically (§8.10).
7. **Size: 65 × 13.5 × 88 mm** since v7.1 (owner: "panels too thick", agreed to the slimmer case "as long as the magnets fit"). 88 was chosen over 85 for proportion. Rollies are up to **6 mm × 60 mm**.
8. **Quality first, at a reasonable print time** (v7.1: about 2¾–3 h).
9. **Comfort:** rounded edges and corners, no sharp details (v7.1 feedback). **Yellow ripples** run edge to edge (top to bottom) on the cover and the tray back.

---

## 4. v7 design specification

### 4.0 v7.1 changes (23 Nov 2026). These override the v7.0 values further down this section
| Area | v7.0 | **v7.1** |
|---|---|---|
| Depth `D` | 15 | **13.5**: `TC` 3.0 → **2.0**, `WB` 2.6 → **2.0**; channel depth unchanged |
| Envelope | Chamfers 1.6 / 2.2 / 1.0, 6 mm facets | **`round_env()`**: plan outline with R6 (opening) and R1 (spine) corners. Long edges are rounded with `EDGE_R` 3.0, whose fillet turns into a **45° chamfer at each bed face** (`HC` = 0.88 mm), so both bed faces print without overhang. Built as 0.1 mm slabs. |
| Magnets | Snap-in, Ø9.7 pocket + lip | **Sealed in** (`CAPTURE = True`): Ø**9.85** pocket, depth **2.72** (17 layers; the magnet sits 0.19 below the pocket top). Cover: 1.16 mm grey below, **6 layers (0.96 mm, `SKIN`) above**. Tray: 6 layers above. Boss height = `SKIN_OUT + POCKET_H + SKIN − TC` = 2.84. Magnets close **2.60 mm apart** (owner chose about 1.0 mm covers; their stated maximum is 5.5 mm between magnets). Estimated N35 pull: ≈ 400 g at 2.6 mm, ≈ 590 g at 1.64, ≈ 145 g at 5.5. **Tray magnet column is round** (`ROUND_PILLAR`, radius `REC_R` + 1.0), as the owner asked. |
| Pauses | none | Cover **print z 4.04** (screen layer 25), tray **print z 7.56** (screen layer 82), via layer-change G-code (§8.10) |
| Inside | Square lip, notched-octagon frame, V notch, 3 grip notches | **`LIP_R` 3.0** rounded lip, **`INNER_FRAME = False`**, **`NOTCH_ROUND`**, **`GRIP_GROOVES = False`**. These are new `v5.book()` switches; their defaults keep older versions unchanged. |
| Ripples | Stepped V-grooves, broken around the magnet | **Yellow inlays 1.2 mm wide, 4 layers deep, edge to edge (top to bottom)** on the cover and tray back, in 3 designs: `RIPPLE` = `flow` / `rings` / `topo` (env var). Flow `RIP_PHASE` 0.22 → 0.10 so neighbours don't crowd. Lines that would break into dashes are dropped. All keep ≥ 0.6 mm of grey between stripes. |
| Datum | 1.0 mm wide | **`DATUM_W` 2.0** (front, back, inside) |
| Infill | 50% gyroid + 100% modifiers | **100% everywhere, no modifier meshes** (their wall outlines were the "squares") |


### 4.1 Architecture
- **Construction:** a clamshell "book". The **tray** (black) holds the rollies. The **cover** (grey) hinges on a **spine** along one long edge (the hinge axis runs along the 88 mm height).
- **Hinge:** knuckles alternate along the spine in **5 segments**: `SEGS = (0–16) (16–34) (34–54) (54–72) (72–88)` mm.
  - The **1.75 mm filament pin** press-fits in the tray end knuckles (Ø1.80), slips in the cover knuckles (Ø2.0) and spins in the yellow **hex spine sleeve** (Ø2.1).
  - The sleeve sits between the cover knuckles.
- **Inside:** **6 vertical channels**, 6.6 mm wide, separated by 0.8 × 3.0 mm ribs, for rollies ≤ 6 × 60 mm. There are **2 filter-tip bays** above and below the magnet clasp column.
- **Magnet clasp:** centred on the opening edge (x = 25.45 mm, z = 44 mm, i.e. mid-height).
  - The **cover** has a boss on its inner face carrying one magnet.
  - The boss drops into a recess in the **tray**, which carries the other magnet.
  - Closed gap between the magnets: **1.0 mm**.
- **Snap-in magnet pockets (no pauses, no glue):** Ø9.7 pocket for the Ø9.51 magnet.
  - **Lip:** a printed **0.4 mm lip** at the mouth, **0.12 mm radial interference**, with **4 relief slots** 0.8 mm wide. The magnet is pressed past the lip with a thumb and clicks in.
  - **Walls:** ≥ 0.8 mm around each pocket; cover front skin 1.44 mm.
- **Thumb scoop:** z 55–70 mm; notch z 54–71 mm.
- **Shell:** chamfers 1.6 front / 2.2 back / 1.0 ends; opening-side corners faceted at 6.0 mm.

### 4.2 Visual details
- **Ripple grooves:** stepped 45° V-grooves, 1.4 → 1.0 → 0.6 mm wide and 0.2 / 0.4 / 0.6 mm deep, so they print support-free face-down.
  - **Cover (front):** they part around the magnet "like water around a stone" (clearing radius 7.2 mm).
  - **Tray:** mirrored on the back.
- **Yellow datum line:** at **z = 0.382 × H = 33.6 mm**. It runs across the front, wraps the opening edge onto the back, and repeats inside the cover.
- **Outside yellow inlays:** **YD = 0.68 mm** (4 layers: 0.20 + 3 × 0.16). They print against the bed.
- **Initials:** "A·B", Inter Bold, 5.0 mm cap, inlaid **AB_D = 0.68 mm** deep in yellow, centred on the bottom face.
  - The middle dot is replaced by a Ø1.5 mm disc for printability.
  - The glyphs use **nonzero** winding, because even-odd XOR breaks Inter's "A".
- **Colours** (Bambu PETG-HF hex values in the 3MF):

  | Colour | Hex |
  |---|---|
  | Grey | `#9DA1A3` |
  | Black | `#1E1E20` |
  | Yellow | `#FFD00B` |

### 4.3 Parts and print orientation

| Object | Filaments | Orientation | Height on bed |
|---|---|---|---|
| **Cover (grey)** | 1 grey + 3 yellow (2 inlay bodies) + 100% modifier | Outside face down | 5.7 mm |
| **Tray (black)** | 2 black + 3 yellow (2 inlay bodies) + 100% modifier | Back face down | 14.9 mm |
| **Spine sleeve (yellow)** | 3 | Upright | 19.4 mm |

**Plate layout** (object centres; A1 bed 256 × 256 mm):
- **Positions:** cover (40.5, 60), tray (179.5, 60), sleeve (110, 200).
- **Spacing:** cover-to-tray gap is **74 mm**, above the A1's 73 mm by-object clearance radius.
- **Height:** all parts are under the **25 mm** rod height.

### 4.4 Key parameters (in `src/v7.py`). What each controls and when to touch it

| Name | Value | Meaning | Tweak if… |
|---|---|---|---|
| `W, D, H` | 65, 15, 88 | Envelope (set via `v3.W/D/H` **before** any other project import) | size change |
| `TC` | 3.0 | Cover plate thickness | cover flexes / too heavy |
| `WB`, `WS` | 2.6, 2.6 | Tray back wall, side walls | |
| `END` | 9.0 | Solid end-block length | |
| `R`, `G` | 2.8, 0.3 | Knuckle radius, knuckle axial gap | knuckles rub or bind → G 0.35–0.4 |
| `PIN_PRESS` | 1.80 | Tray end-knuckle bore (press fit on 1.75 pin) | pin won't go in → 1.85; pin falls out → 1.75 |
| `PIN_SLIP` | 2.0 | Cover knuckle bore (free rotation) | cover stiff → 2.1 |
| `PIN_SLEEVE` | 2.1 | Sleeve bore | sleeve doesn't spin → 2.2 |
| `SLOTS`, `SLOT_W` | 6, 6.6 | Channel count and width | rollies tight → 6.8 (check `checks()` still passes) |
| `RIB_T`, `RIB_H` | 0.8, 3.0 | Channel rib thickness and height | |
| `MAG_D`, `MAG_T` | 9.51, 2.51 | Magnet size | different magnets |
| `POCKET_D` | 9.7 | Pocket bore | magnet rattles → 9.6 |
| `LIP_H`, `LIP_INT`, `LIP_SLOTS`, `LIP_SLOT_W` | 0.4, 0.12, 4, 0.8 | Snap lip height, radial interference, relief slots | magnet won't snap in → LIP_INT 0.08; pops out → 0.16 or LIP_H 0.5 |
| `GAP` | 0.2 | Boss-to-recess clearance | cover doesn't close flush → 0.3 |
| `YD`, `AB_D` | 0.68, 0.68 | Outside yellow depth, initials depth | show-through → 0.84 (5 layers) |
| `FONT`, `CAP` | Inter-Bold.ttf, 5.0 | Initials font and cap height | |
| `CAPTURE` | False | True = magnets sealed in by pauses (works **only** by layer, not by object) | |
| `USE_BADGE` | False | Initials as a separate press-fit badge (cuts the swaps caused by the upright A·B) | swaps are too slow |
| `SCOOP_Z`, `NOTCH_Z` | (55,70), (54,71) | Thumb scoop and notch heights | |
| `LAYER0`, `LAYER` | 0.20, 0.16 | Used to snap features onto layer boundaries | layer-height change |

### 4.5 `v7.checks()` expected output (v7.1, every `RIPPLE`)
`env [65,13.5,88]`, `pieces (1,1)` (sealed pockets are voids, not pieces), `overlap 0`, `pocket_material (0,0)` (pockets empty), `pocket_unsealed (0,0)` (≥ 0.3 mm of plastic all round), `rollups 6`, `rollups_vs_tray 0`, `swing_contacts []`, `tray_wall_void 0`, `cover_wall_void 0`, `magnet_gap 2.6`, `pauses (4.04, 7.56)`, `cover_front_skin 1.16`, `MX 25.37`, `slot_x1 18.25`, `datum_z 33.6`, `yellow_depth_mm 0.68`.
- **Slot margin:** `slot_x1` leaves only 0.75 mm of slack for the 6 channels. Growing the boss or pocket further will collide with the last channel.
- **v7.0 values** were: `env [65,15,88]`, `magnet_gap 1.0`, `cover_front_skin 1.44`, `MX 25.45`, `slot_x1 18.4`.

---

## 5. Print setup (A1), as built into the main 3MF

- **Presets** (Bambu's **released** system presets, values from tag v02.08.04.61): printer **Bambu Lab A1 0.4 nozzle**, process **0.16mm High Quality @BBL A1**, filaments **Bambu PETG HF @BBL A1** × 3.
- **v7.1 overrides on top of the list below:**
  - 100% infill (zig-zag), no modifiers.
  - `top_surface_pattern` concentric.
  - `brim_type` outer_only, `brim_width` 4.
  - `filament_max_volumetric_speed` 18 / **15** / 18 (black capped).
  - `layer_change_gcode` = the A1 template plus the magnet-pause block (§8.10).
  - Parts 114 mm apart: cover (38.5, 60), tray (217.5, 60), sleeve (128, 200).
  - Expected time (PrusaSlicer A1 emulation): **≈ 2 h 40 m**; 47 swaps, 121 layers, 2 pauses; ≈ 14 / 33.5 / 1.6–2.1 g.
- **Overrides (v7.0 list; still applies except where v7.1 changes it above):**
  - **Layers:** 0.16 (first layer 0.20).
  - **Walls and shells:** 4 walls (arachne), 6 top / 5 bottom shells.
  - **Infill:** 50% gyroid.
  - **Seam:** back.
  - **Elephant foot:** 0.15.
  - **Supports:** none.
  - **Prime tower:** **off**.
  - **Print sequence:** **by object**.
  - **Plate:** **Textured PEI**.
- **Inherited from the preset:** outer wall 60 mm/s at 2000 mm/s²; inner wall 150; default acceleration 4000; nozzle 240 °C; plate 70 °C.
- **Modifiers:** **100% infill + 6 walls** over the hinge knuckles, both end blocks and the magnet clasp (one modifier mesh per object). Object-level settings: 4 walls, 50% gyroid (sleeve 100%).
- **Purge:** **flush into infill** on cover and tray. Purge matrix (mm³, from → to grey/black/yellow): `[[0,150,320],[280,0,460],[150,150,0]]`.
- **Expected** (PrusaSlicer A1 emulation):
  - **Time:** **3 h 44 m** including AMS load/unload, plus about 15–30 s purge per swap, so **about 4–4¼ h real**.
  - **Swaps and layers:** **47 colour swaps**, 121 layers. Most swaps come from the upright A·B on the tray bottom.
  - **Filament:** 19.5 g grey, 36.6 g black, 0.6 g yellow, plus about 15–20 g purge.
  - **Bambu's own estimate:** not recorded. Ask the owner what Bambu Studio showed.
- **The "Customised preset" dialog on open is normal:** the project deliberately differs from the stock presets. Keep the project's settings.

### Assembly (owner instructions, also in `v7-65x15x88/README.md`)
1. **Magnet polarity:** stick the two magnets together and mark the two touching faces. Press each into its pocket **marked face OUT**, until it clicks past the lip. Then the marked faces meet when the case closes, so the magnets attract.
2. **Hinge:** slide the yellow sleeve between the cover knuckles, push the 1.75 mm filament through from the top (about 87 mm), and trim it flush. Optionally, heat the ends briefly to flare them.

---

## 6. Test-print feedback checklist (ask the owner these after each print)

### 6.1 v7.0 first print (23 Nov 2026, cover only): what the owner reported, and the v7.1 fix
- **First layer:** OK, but it **warped** on one side. v7.1 adds a 4 mm brim; the owner should clean the plate and dry the PETG.
- **Outside yellow:** OK.
- **Magnets didn't fit;** they re-measured 9.53 × 2.53. The owner also wanted them **embedded**, with the printer telling them when. v7.1: sealed pockets + self-pause + chime.
- **Panels too thick.** v7.1: 2.0 mm panels, 100% infill, 13.5 mm deep.
- **"Squares" in the surface pattern.** These were modifier and frame outlines. v7.1: no modifiers, no frame, concentric top surfaces.
- **Too many sharp edges.** v7.1: rounded envelope, lip and notch.
- **Yellow line thicker; ripple slits yellow; ripples connected and reaching the top and bottom edges.** v7.1: 2 mm datum lines, yellow edge-to-edge ripples, 3 designs.
- **Photos showed** blobs, zits and stringing on the top surfaces (likely damp PETG), and lumps at the 3 grip notches (now removed).

### 6.2 Checklist

| # | Check | If it fails → change (in `src/v7.py`) |
|---|---|---|
| 1 | First layer: yellow lines crisp, no smearing; plate adhesion | Elephant foot / first-layer settings in the project overrides (`v7_a1_export.py`) |
| 2 | Outside yellow: solid colour, no grey or black showing through at 4 layers | `YD` 0.68 → 0.84 |
| 3 | A·B legible on the bottom (upright, 5 mm Inter Bold) | `AB_D`, `CAP`, or switch `USE_BADGE` |
| 4 | Magnets snap in by thumb and stay put | `LIP_INT` / `LIP_H` / `POCKET_D` (see §4.4) |
| 5 | Closing force: satisfying click, holds closed in a pocket | `GAP` (boss clearance), boss/recess skins. Magnet gap is 1.0 mm now; reduce carefully, keeping walls ≥ 0.8 |
| 6 | Pin goes through; cover swings freely; sleeve spins | `PIN_PRESS`, `PIN_SLIP`, `PIN_SLEEVE`, `G` |
| 7 | Cover closes flush with no rub along the spine | `G`, knuckle `R` |
| 8 | 6 rollies slide in and out; filter tips fit the bays | `SLOT_W`, rib dims |
| 9 | Ripple grooves clean (the 0.6 mm groove ceilings bridge fine) | Groove steps in `v6.grooves` |
| 10 | Print time and real filament use vs the estimate | Record in the v7 README |
| 11 | Overall feel: stiffness, weight, sharp edges | `TC`, `WB`, chamfers |

After any change:
1. Rebuild (§7.3) and rerun **all** checks (§7.4).
2. Re-render (§7.5) if the change is visible.
3. Update the v7 README tables.
4. Commit.

---

## 7. How to rebuild everything (clean-room verified on 22 Nov 2026)

A clean rebuild from this repo alone reproduced both shipped 3MFs **byte-for-byte except for random part UUIDs**, and identical STLs.

### 7.1 Environment
- **Python:** Python 3.13 with:

  | Package | Version |
  |---|---|
  | `manifold3d` | 3.5.5 |
  | `shapely` | 2.2.0 |
  | `scikit-image` | 0.26.0 |
  | `matplotlib` | 3.11.2 |
  | `numpy` | 2.5.3 |
  | `pillow` | 12.3.0 |
  | `trimesh` | 5.2.2 |
  | `fonttools` | any recent |
  | `git-filter-repo` | used only for the repo move |

  ```bash
  pip install manifold3d shapely scikit-image matplotlib numpy pillow trimesh fonttools
  ```
- **PrusaSlicer 2.7.2** (CLI) is the proxy slicer. It was installed from Ubuntu noble *universe*. In the cloud container, plain-HTTP apt hangs (HTTPS-only proxy), so use an HTTPS sources list:
  ```bash
  printf 'deb [signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] https://archive.ubuntu.com/ubuntu noble main universe\ndeb [signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] https://archive.ubuntu.com/ubuntu noble-updates main universe\n' > /tmp/https.list
  ```
  ```bash
  apt-get -o Dir::Etc::sourcelist=/tmp/https.list -o Dir::Etc::sourceparts=- update && apt-get -o Dir::Etc::sourcelist=/tmp/https.list -o Dir::Etc::sourceparts=- install -y prusa-slicer
  ```
  Run it headless with `QT_QPA_PLATFORM=offscreen`.
- **Bambu Studio source** (public; needed by `tagprofile.py`, `bbsvalidate.py`, `a1_safe.py` and `a1_profile.py`): a blob-less sparse clone at **`/home/user/bambulab/bambustudio`**. That path is hard-coded in `src/tagprofile.py` (`REPO`) and `src/a1_profile.py` (`BBL`).
  These are the exact commands used originally:
  ```bash
  GIT_LFS_SKIP_SMUDGE=1 git clone -q --depth 1 --filter=blob:none --sparse https://github.com/bambulab/bambustudio /home/user/bambulab/bambustudio
  ```
  ```bash
  git -C /home/user/bambulab/bambustudio sparse-checkout set resources/profiles/BBL/machine resources/profiles/BBL/process resources/profiles/BBL/filament src/libslic3r src/slic3r/GUI
  ```
  ```bash
  for t in v02.03.01.51 v02.08.04.61 v02.09.01.70; do git -C /home/user/bambulab/bambustudio fetch -q --depth 1 --filter=blob:none origin tag $t; done
  ```
  Notes:
  - `git show <tag>:<path>` fetches blobs on demand.
  - **Do not download Bambu Studio binaries:** GitHub *releases* return 403 in this environment, by network policy. Don't try to work around it.
- **Renders:** Chromium + Playwright are preinstalled in the cloud container (`require('playwright')`, no install). three.js **r128** comes from cdnjs: `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`.

### 7.2 Run everything from `edc-cigarette-case/v7-65x15x88/`

### 7.3 Build geometry and export the 3MFs
- **Template:** the exporter needs a "template" folder holding `Metadata/project_settings.config` and `[Content_Types].xml`.
  - Use the **shipped 3MF itself**: it has the proven 366-key layout.
  - The creator's original 3MF (JanBerry Design) is **not** in the repo; it is not ours to redistribute.
```bash
mkdir -p /tmp/tmpl /tmp/out && (cd /tmp/tmpl && unzip -o -q "$OLDPWD/AB_Rollie_Book_v7_A1_by_object.3mf")
```
```bash
for st in flow rings topo; do RIPPLE=$st python3 src/v7_a1_export.py /tmp/out /tmp/tmpl; done
# public MakerWorld version (no initials, files named Rollie_Book_...):
for st in flow rings topo; do INITIALS=0 RIPPLE=$st python3 src/v7_a1_export.py /tmp/out_pub /tmp/tmpl; done
```
- **v7.1:** each run writes `AB_Rollie_Book_v7_A1_{by_object,geometry_only}_{A_Flow,B_Rings,C_Topo}.3mf` and `stl_<design>/`.
- **Template:** any shipped v7.1 3MF works. The exporter strips its own pause block before re-adding it.
- **Verified 23 Nov:** a rebuild from a shipped v7.1 file reproduces settings, model and STLs byte-for-byte, except UUIDs.
- **What it prints:** `v7.checks()` (§4.5), then both 3MF paths, then: `heights {'Cover (grey)': 5.7, 'Tray (black)': 14.9, 'Spine sleeve (yellow)': 19.4} | min gaps {... 74.0 ...}`, `on bed True | printer Bambu Lab A1 0.16mm High Quality @BBL A1 by object prime tower 0`.
- **Outputs:** `/tmp/out/AB_Rollie_Book_v7_A1_by_object.3mf`, `/tmp/out/AB_Rollie_Book_v7_A1_geometry_only.3mf`, and `/tmp/out/stl/*.stl`. Copy them into place when happy.
- **Build time:** about 20 s.

### 7.4 Verify (all four must pass before shipping a file; then run the independent re-check)
**v7.1 extra:** `python3 src/recheck_3mf.py <shipped.3mf> <roundtrip.gcode>` reads only the shipped file and checks:
- zip, XML and JSON integrity;
- the key set and order match v7.0;
- object order;
- clearances;
- the pause block;
- that the pockets are open on every layer up to each pause and sealed from it;
- that each pocket fits the magnet;
- exactly 2 G-code pauses, cover then tray, at the right z.

It must print `ALL PASS`. `src/render/magnet_section.py` draws the cut-through.
1. **Bambu loader check**, emulated from Bambu's source at three releases:
   ```bash
   python3 src/bbsvalidate.py AB_Rollie_Book_v7_A1_by_object.3mf v02.03.01.51 v02.08.04.61 v02.09.01.70
   ```
   - **Expected:** **26 flags per release**, exactly as listed in `test-slice/bambu_loader_check_baseline.txt`. These 26 are also raised by the creator's original file, which loads fine: they are legacy keys Bambu handles.
   - **Any new flag is a real risk**, especially an "unknown option" or "Invalid configuration" one.
2. **A1-emulated PrusaSlicer slice from CAD:**
   ```bash
   python3 src/slicetest_a1.py /tmp/slice
   ```
   - It writes `/tmp/slice/a1_one_plate.3mf`, `a1_hq_petghf_0.16.ini` and the G-code.
   - **Expected (v7.1, set `RIPPLE`):** ≈ `2h 39m 40s` (Rings) / `2h 39m 46s` (Flow) / `2h 42m 05s` (Topo); 47 toolchanges, 121 layers, `"pauses": 2`.
   - **It also prints** `magnet pauses (object, layer z): [('0', 4.04), ('1', 7.56)]`. The M486 ids are 0 = Cover and 1 = Tray; check the `M486 A` lines.
   - **v7.0 expected** was `3h 44m 10s`, 19.47 / 36.58 / 0.56 g, 0 pauses.
   - Note: this script builds its ini from the clone's **working-tree HEAD** profiles (`a1_profile.py`). That is fine for the PrusaSlicer emulation, but **never** use `a1_profile.project_config` for the Bambu 3MF again (see §8).
3. **Round-trip re-slice of the shipped 3MF.** Run it after step 2, because it needs the ini in that folder:
   ```bash
   python3 src/roundtrip_reslice.py /tmp/slice AB_Rollie_Book_v7_A1_by_object.3mf
   ```
   - It reads meshes, part filaments, modifiers and positions **out of the shipped file**.
   - **Expected (v7.1):** 9 meshes `NoError`, then the same time as step 2 within ±5 s, 47 toolchanges, 121 layers, **2 pauses**.
4. **v7.1: "Detected print stability issues: Cover, Floating bridge anchors"** is expected and benign. It is the 6-layer roof over the sealed cover pocket; in the real print the magnet sits 0.19 mm below it. Proven by an A/B slice: with the pocket filled, the warning disappears.
5. **v7.0 only: "Long bridging"** was expected and benign. It was:
   - the 0.6 mm groove ceilings at z 0.68;
   - the first solid layer over gyroid inside the 3.0 / 2.6 mm floors (z 2.28 cover, z 1.80 tray).

### 7.5 Renders and sheets
```bash
mkdir -p /tmp/r && cp src/render/view.html /tmp/r/ && curl -sSfL -o /tmp/r/three.min.js https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
```
```bash
python3 src/v7_render.py /tmp/r
```
```bash
(python3 -m http.server 8770 --directory /tmp/r >/dev/null 2>&1 &) ; sleep 1
```
```bash
NO_PROXY=127.0.0.1 no_proxy=127.0.0.1 node src/render/shot7.js /tmp/r
```
```bash
python3 src/render/render_sheet.py /tmp/r
```
- **Outputs:** `/tmp/r/v7_{front,open,back,base}.png`, `v7_a1_sheet.png` and `v7_a1_plate.png`. Verified 22 Nov: this exact sequence reproduces the committed PNGs **pixel-for-pixel**.
- **Running `shot7.js`:** it needs Playwright resolvable from the working directory. Run it where `require('playwright')` works (globally installed in the cloud container), and set `PORT` if 8770 is busy.

### 7.6 Source map (`v7-65x15x88/src/`)

| File | Role |
|---|---|
| `case.py` | Low-level helpers (shapely ↔ manifold cross-sections, contours) from v1 |
| `v3.py`, `v4.py`, `v5.py`, `v6.py` | Layered geometry library. `v5.book()` builds the Book; `v6` has text (`text_poly`, nonzero winding), grooves, inlays and fonts dir |
| `v6_final.py` | Mesh XML writer (`model_xml`), STL writer, older project-settings helper |
| `v7.py` | **The v7 design**: parameters, `build()`, `checks()` |
| `v7_a1_export.py` | **A1 by-object 3MF exporter** (both files + STLs) |
| `a1_safe.py` | **Version-safe project_settings builder**: proven key set and order, values from the released A1 presets (v02.08.04.61), plus a self-check |
| `tagprofile.py` | Resolves Bambu presets (inherits/include) at a git **tag** |
| `bbsvalidate.py` | Bambu project-config loader emulator (option types and enums from `PrintConfig.cpp` at a tag) |
| `a1_profile.py` | Resolves presets from the clone's HEAD. **For the PrusaSlicer ini only** |
| `slicetest.py`, `slicetest_a1.py` | PrusaSlicer 3MF writer, ini, slice and report; A1 sequential test. `slicetest.py` parses `sys.argv` **at import** |
| `roundtrip_reslice.py` | Re-slices a shipped Bambu 3MF via PrusaSlicer |
| `v7_export.py` | Old P1S three-plate exporter (by layer, pauses). Superseded |
| `v7_render.py`, `render/` | Render JSON, viewer, screenshot and sheet scripts |

---

## 8. Bambu Studio 3MF knowledge (hard-won; read before touching the exporter)

1. **Structure we write:**
   - `3D/3dmodel.model`: one object per part group, with `<components>` pointing at `3D/Objects/object_N.model`.
   - `Metadata/model_settings.config`:
     - per object: name, extruder, infill/walls, flush_into_infill;
     - per part: `normal_part` with `extruder`, or `modifier_part` with `sparse_infill_density`/`wall_loops`;
     - `<plate>` with `print_sequence`.
   - `Metadata/project_settings.config`: flat JSON, **all values strings or string arrays**.
   - The `Application` metadata says `BambuStudio-01.10.02.76` and the config `version` is `01.10.02.76`, matching the proven template.
2. **Why the first A1 file failed** ("Invalid configuration file" → "no geometry data"):
   - Its project_settings were resolved from Bambu's **development HEAD** profiles: 559 keys, including dual-nozzle (H2D) keys such as `extruder_variant_list`, `filament_extruder_variant` and `filament_self_index`.
   - `filament_colour` sat at key #448. The loader rejected the config, the filament count came out as 0, and `PresetBundle::load_config_file_config` threw. A thrown config error also aborts the geometry load.
3. **The rule that fixed it (keep it):**
   - Write **only** the key set, **in the key order**, of a project known to load. That is now our own shipped file: 366 keys, `filament_colour` at index 62 (0-based).
   - Fill it with values from Bambu's **released** presets at a **tag** (`a1_safe.py`).
   - **No multi-extruder variant keys.**
   - Lists: per-filament → N entries, `machine_*` → 2 entries (normal/silent), `different_settings_to_system` → N + 2, flush matrix N² and vector 2N.
   - `a1_safe.check()` enforces these, and the exporter asserts it.
4. **Geometry-only loading:**
   - **Trigger:** a 3MF with no `project_settings.config`, or opened via *Import geometry only*.
   - **Kept:** Bambu still applies object and part configs from `model_settings.config` (part filaments, modifiers, per-object walls/infill) and **adds filament slots** up to the highest extruder ID. Confirmed in `Plater.cpp`.
   - **Use:** this is what the fallback file relies on.
5. **PrusaSlicer 3MFs are not a deliverable for Bambu:**
   - Bambu's loader has the PrusaSlicer volume file (`Slic3r_PE_model.config`) **commented out**, so multi-part objects collapse into one mesh and the colours are lost.
   - PrusaSlicer G-code also can't drive the A1's AMS lite changes safely.
   - **Use PrusaSlicer only to test-slice** (the owner agreed: "just use prusa slicer").
6. **By-object mode ignores per-layer custom G-code** (pauses, colour changes): `ByObjectPrintData` builds per-object tool ordering without `assign_custom_gcodes`. Hence **snap-in** magnets instead of sealed-in magnets with pauses.
7. **A1 by-object clearance:**
   - `extruder_clearance_max_radius = 73` mm: keep hull gaps ≥ 73 mm (we use 74).
   - `extruder_clearance_height_to_rod = 25` mm: all objects must be shorter.
   - `nozzle_height = 4.76`; `printer_structure = i3`; printable height 256.
8. **A1 start G-code placeholders** are identical from v02.03.01.51 to v02.09.01.70 (13 placeholders), so the release-tag G-code is safe across versions.
9. **"Customised preset" dialog on open** is expected whenever a project overrides system presets. Keep the project settings.
10. **Pausing while printing by object (v7.1).** Bambu's own per-layer pauses are ignored by object (point 6), so the pause lives in **`layer_change_gcode`**:
    - **Condition:** `{if (current_object_idx == 0 and layer_z > 4.03 and layer_z < 4.05) or (current_object_idx == 1 and layer_z > 7.55 and layer_z < 7.57)}`. The values come from `v7.build()`.
    - **Body:** the A1 start-tune chime (`M1006 …`), `; PAUSE_PRINTING` (Bambu's reserved tag, so the preview can show it), then `M400 U1` (= the A1's `machine_pause_gcode`).
    - **Checked in Bambu source at v02.03.01.51, v02.08.04.61 and v02.09.01.70:**
      - `current_object_idx` is set to 0, then to the finished-object count before each object.
      - By-object print order is the **object-list order**, because the auto-sort is `#if 0`'d.
      - The `and` / `or` keywords exist in the placeholder parser.
      - `layer_z` is the new layer's `print_z`.
      - The screen layer (`M73 L`) is cumulative across objects.
    - **Keep the object order** cover → tray → sleeve in the 3MF.
11. **Sealed voids and `decompose()`.** An enclosed pocket is returned by `decompose()` as its own piece, so "keep the largest piece" silently deletes it. Subtract sealed pockets **after** any keep-largest step. `v7.checks()` now asserts that both pockets are empty and sealed.
12. **Sync AMS with non-RFID spools** replaces the project's filament presets with the slot presets. Tell the owner to map slots in the Print dialog instead.

---

## 9. Gotchas and environment constraints

- **Network:** the HTTPS-only proxy has these limits:
  - `github.com` **releases** return 403. GitHub *raw* files sometimes 403 too (they did on 22 Nov for the Inter OFL text). **Do not work around blocked hosts.**
  - Public `git` reads of `bambulab/bambustudio` work.
  - Package registries (pip, npm, apt over HTTPS) work.
- **No wildcard `rm`:** a safety hook blocks it. Use `git mv` / explicit paths.
- **Import order:** `v7.py` sets `v3.W, v3.D, v3.H` **before** importing other project modules; keep it that way.
- **`slicetest.py` reads `sys.argv` at import time:** `roundtrip_reslice.py` resets `sys.argv` before importing it.
- **PrusaSlicer ini quirks:**
  - relative E needs `layer_gcode = G92 E0`;
  - drop `filament_ramming_parameters` (syntax errors);
  - use the TIMING=1 path (no pauses) for time estimates, or the estimator overflows.
- **Fonts:** `v6.py` looks for fonts in `../fonts` relative to `src/`. Only `Inter-Bold.ttf` is bundled (all v7 needs). Older concept fonts came from Google Fonts via `https://fonts.googleapis.com/css2?family=<Name>` → gstatic TTF URLs.
- **Hyper3D (Rodin) MCP** was connected earlier for concept generation. It currently needs re-authorising in claude.ai connector settings before use.
- **Branch rule** for the cloud session: develop on `claude/elegant-turing-9djtl2`, push there, open PRs into `main`.

---

## 10. Design history and decision log

| Ver | What | Key decisions / why it changed |
|---|---|---|
| v1 | Topo Edition: 10 king-size cigarettes, 87 × 14 × 90, screw-pin side hinge, 4 magnets, green + yellow topo inserts | Original brief: transform JanBerry Design's *Hiking Container* language (faceted, rugged) into a slim EDC case; dark forest green + yellow topology accents. All geometry original, no meshes copied. |
| v2 | 55 × 13 × 85 concepts: Ridgeline, Switchback, Summit | Owner set 55 × 13 × 85 and asked for 2–3 designs. |
| v3 | 5 rollie concepts (book clamshell + friction cap, flush inlays) | Switched to **rollies** (60 mm × 5–6 mm). Inlays flush unless deliberately raised. |
| v4 | Book: vertical dividers, AB monogram on the slim bottom, 50%+ infill with 100% modifiers, Contour/Gridline/Trailhead surfaces | "Vertical dividers, no horizontal one; doesn't need 8; look great, feel great, sturdy." |
| v5 | Review-driven fixes (panel bug, magnet walls 0.15 → 1.1 mm), faceted shell, inside ruler | DESIGN.md "Trail Kit" language written here. |
| v6 concepts | Monolith, Ripple, Tide, Form, Instrument + judge's **Hybrid** | Fresh visual rethink. Analysed designers **h3li0** (clean, lowercase "a · b"), **dkdsgn/Abstractia** (ripple lamps), **XXY2025** (pictorial gift boxes). Everything PETG-HF. Palette grey/yellow/green/forest/blue/black. Initials smaller and centred. |
| v6 final | **Design 6 Hybrid approved.** Uppercase A·B; font changed (Michroma), 5 mm "safe" size; 1.0 mm yellow inlays | "design 6 but want initials in uppercase and different font / go to 5mm safe". |
| v6 rev B | Only **2 magnets Ø9.51 × 2.51** + **1.75 filament pin**, no glue; centred clasp; 5 slots + tip bays; **Inter Bold** (Helvetica-like); magnets sealed in with **pauses** | "redesign so it fits only the magnets and nothing else, no other hardware"; "font something like helvetica". |
| v7 (P1S) | Re-proportioned to **65 × 15 × 88** (88 over 85 on proportion); 6 slots; quality profile; 3 plates; test slice | "65 by 15 by 85 or 88 depending on proportions; max quality, reasonable time; test slice". Now in `superseded/`. |
| v7 (A1) | **Bambu A1, one plate, by object**; outside yellow cut to **4 layers**; **snap-in magnets** (pauses don't work by object); A1 presets | "line visible from the outside only a few layers… not pass through"; "Bambu Lab A1, print by object, fit on 1 plate". |
| v7 (A1 fix) | Rebuilt project settings on the proven key set + released values; added geometry-only fallback; loader emulator + round-trip re-slice | First A1 file failed in Bambu ("Invalid configuration file"). **Fixed and confirmed by the owner: opened and sliced fine.** |
| move | Project moved with full history from `grishatg/General-` to **`grishatg/3D-PRINTS`** | Owner request, 22 Nov 2026. |
| v7.1 | **65 × 13.5 × 88**; magnets **sealed in with self-pauses (by object)**; rounded edges; 100% infill, no modifiers; concentric tops; 4 mm brim; 2 mm datums; **yellow edge-to-edge ripples in 3 designs (Flow / Rings / Topo)** | First print of the v7.0 cover on 23 Nov (§6.1). The owner asked for all 3 designs to be built before choosing. |

---

## 11. Open items and ideas backlog

1. **v7.1 print:** confirm the self-pauses fire in real Bambu Studio and on the A1; record which ripple design the owner chose, the real print time, and Bambu's own estimate. Then retire the other two designs into `superseded/`.
1a. **Magnet pull at 2.60 mm:** if the close feels too soft, set `SKIN` to 0.48 (3 layers): 1.64 mm, about 1.5× the pull. If it's too strong or the covers look thin, set `SKIN` to 1.28 (8 layers): about 3.2 mm.
2. **Tolerances are unproven:** snap lip interference (0.12), pin bores (1.80 / 2.0 / 2.1), knuckle gap (0.3), boss gap (0.2).
   - Option: a tiny **tolerance coupon** (pin-bore ladder 1.75–1.90 and lip interference 0.08/0.12/0.16), about 10 min to print, if the first print shows fit issues.
3. **Cutting colour swaps (47):** most come from the upright A·B on the tray bottom.
   - **Option 1:** `USE_BADGE = True` (separate press-fit badge).
   - **Option 2:** accept as is. The time cost is modest (about 15–20 min of swaps).
   - Owner preference so far: keep the initials in the body.
4. **Wear test** of the 1.75 mm filament pin over many open/close cycles. A flare on both ends is the "no hardware" retention.
5. **Optional:** a short README at the 3D-PRINTS root listing future projects as they're added.

---

## 12. Starter prompt for the next session (copy-paste)

> Continue the EDC rollie case project in `grishatg/3D-PRINTS` (folder `edc-cigarette-case/`). Read `edc-cigarette-case/HANDOVER.md` first and follow its hard requirements (§3) and Bambu 3MF rules (§8). Check out `main` if PR #2 has been merged, else branch `claude/hopeful-thompson-ysz39k`. I've printed v7.1 (design: [A Flow / B Rings / C Topo]) on my A1. Here's my feedback: [paste feedback / photos]. Tune the design using the §6 checklist, rebuild, rerun all §7.4 checks, then give me the updated 3MF.
