# Rollie Book · wood PLA · print files (v10.3, 24 Nov): max quality, FLUSH magnets

**Six Bambu Studio projects:**
- Each project holds **two designs (two complete cases) on one plate**, printed **by object**.
- There are **no pauses**: you glue the magnets in after printing.
- There are three pairs, each with A·B and without initials.

**Don't print anything older.** The v10.0 files had open slots at the corners and a hole in the thumb scoop; they're archived in `../superseded/wood-v10.0-corner-holes/`.

## What's new in v10.2
- **Max quality print profile**, built on Bambu's own **0.12 mm High Quality @BBL A1** preset:
  - 0.12 mm layers: smoother rounded edges and thumb scoop.
  - 4 walls: no infill showing through the 2 mm walls.
  - 1.0 mm top skin, 0.8 mm bottom skin, 20 % gyroid infill.
  - Slower walls and inside top surfaces.
  - **A slow, narrow first layer:** it's the visible face, so the inlays, engraving and A·B come out crisper.
  - **Scarf seams** on the outer walls, which blend the seam line away on the smooth curved sides.
  - Travel avoids crossing walls.
- **Magnets FLUSH:** each pocket is now only as deep as the magnet. The glued magnet sits **0.04 mm below the face** as printed, so it's flush to the eye and can never stick out and stop the case closing.
  - **Distance:** with the case closed, the magnet faces are **0.34 mm apart** (the test print had 2.4 mm).
  - **Pull:** about **4.4× the test print** (N35 model: ~780 g for both pairs, against ~177 g). That's the most these magnets can give.
  - **Lid:** each lid magnet now sits entirely inside its round boss, with the full 2 mm lid plate behind it.
- **Corner and thumb-scoop fix** from v10.1: walls are ≥ 1.2 mm everywhere, and the tray cavity is enclosed on every layer.

## Load the AMS lite once, the same for every project
| Slot | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Wood | **Oak** | **Teak** | **Cherry** | **Walnut** |

Use the **textured PEI plate**, with a 3 mm brim, no supports and no prime tower.

## The projects
| Project file | Cases on the plate | Time* | Filament | Colour swaps |
|---|---|---|---|---|
| `AB_Rollie_Book_wood_Kumiko_Dial_A1.3mf` | KUMIKO + DIAL, with A·B | 4 h 52 m | 71 g | 9 |
| `Rollie_Book_wood_Kumiko_Dial_A1_no_initials.3mf` | KUMIKO + DIAL | 4 h 46 m | 71 g | 4 |
| `AB_Rollie_Book_wood_Riva_Parquet_A1.3mf` | RIVA + PARQUET, with A·B | 5 h 09 m | 70 g | 30 |
| `Rollie_Book_wood_Riva_Parquet_A1_no_initials.3mf` | RIVA + PARQUET | 5 h 04 m | 70 g | 26 |
| `AB_Rollie_Book_wood_Endgrain_Cubes_A1.3mf` | ENDGRAIN + CUBES, with A·B | 5 h 42 m | 71 g | 29 |
| `Rollie_Book_wood_Endgrain_Cubes_A1_no_initials.3mf` | ENDGRAIN + CUBES | 5 h 33 m | 71 g | 20 |

\* Times and weights come from the A1-emulated slice. Bambu Studio will show a bit more: each colour swap adds about a minute and a 0.2–0.5 g purge. The busiest plate comes to about 6 h.

**What's on each plate:** 4 objects, printed one after the other: lid A, tray A, lid B, tray B. They're laid out in a pinwheel so every object is at least 74 mm from every other, which the A1 needs to print by object without the toolhead hitting a finished part. **Leave them where they are** (don't press Arrange). If Bambu warns about clearance, the layout has been moved.

**Hinge sleeves:**
- Each case's sleeve prints in its own accent wood, beside a part of the same colour, so it adds no colour swaps.
- Match them to the cases by colour:

| Case | KUMIKO | DIAL | RIVA | PARQUET | ENDGRAIN | CUBES |
|---|---|---|---|---|---|---|
| Sleeve wood | walnut | walnut | oak | cherry | oak | walnut |

## Magnets: glue them in after printing
You need **4 × Ø5 × 2 mm magnets per case**, 8 per plate. Each half has two round pockets, one at each corner on the opening edge.

**Polarity** (once per case):
1. Stack the four magnets in one column.
2. Mark the **top** face of each one.
3. **Lid:** marked face **UP**. **Tray:** marked face **DOWN**.

If the halves push apart instead of snapping shut, one pair is flipped.

**Gluing:**
1. Lay each part **inside-up**.
2. Put a small drop of super glue (CA gel is easiest) on the **floor** of each pocket.
3. Use **only a small drop** so glue doesn't well up round the edge. The pocket is just magnet-deep.
4. Press the magnet in until it sits **flush with the surface**. Use a **toothpick**, not steel tweezers, and wipe off any glue that comes up.
5. **Let the glue cure for 10 minutes before you close the case.** Flush magnets pull very hard and will jump out of wet glue.

**Too strong?** This is the maximum. To soften it, stick a small dot of tape or thin felt on each **lid** magnet:

| Padding on each lid magnet | Approximate pull |
|---|---|
| 0.15 mm (e.g. one layer of electrical tape) | ~670 g |
| 0.45 mm | ~520 g |

No reprint is needed.

**Hinge pin:** 1.75 mm PETG filament.

## If you'd rather not use scarf seams
In Bambu Studio: **Filament settings → Seam → Scarf seam type → None**, for each of the four filaments. Everything else stays the same.

## How these were checked
`src/w_pair_verify.py` reads only the 3MF. All six print **ALL PASS** (37 checks each); the reports are in `checks/`. The checks:
1. **Bambu loader check,** emulated from Bambu's source at v02.03.01.51, v02.08.04.61 and v02.09.01.70: identical to the 26-flag baseline that loads fine.
2. **Settings:**
   - the same 366 keys, in the same order, as the v7.0 file that opened in Bambu Studio;
   - 4 × Bambu PLA Wood;
   - 0.12 mm High Quality profile, scarf seams on, no pause anywhere.
3. **Plate:**
   - every pair of objects is at least 73 mm apart (Bambu needs more than 72.8);
   - everything plus the brim is on the bed;
   - both sleeves are present.
4. **Each lid and tray:**
   - R4.5 rounded edges;
   - colour work only in the first 5 layers;
   - walls checked layer by layer: nothing within 1.1 mm of the outside (thinnest 1.19 mm on the trays), and the tray cavity is enclosed on every layer;
   - two Ø5.35 pockets, magnet-deep: the glued magnet sits 0.04 mm below the face.
   - **Closed case: magnet face to magnet face 0.34 mm.**
   - Each lid magnet sits inside its boss, so the 2 mm lid plate has no openings at all.
5. **A1-emulated slice** of each file at 0.12 mm: it slices by object with the A1's 73 mm clearance, with no pauses.

**Expected slicer notes (benign):** "Long bridging" / "Loose extrusions" on parts with **engraved** patterns (KUMIKO, the DIAL, PARQUET and ENDGRAIN backs). These are the stepped groove ceilings in the first face-down layers.
