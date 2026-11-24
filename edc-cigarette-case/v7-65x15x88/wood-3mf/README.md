# Rollie Book · wood PLA · print files (v10.1, 24 Nov)

**Six Bambu Studio projects:**
- Each project holds **two designs (two complete cases) on one plate**, printed **by object**.
- There are **no pauses**: you glue the magnets in after printing.
- There are three pairs, each with A·B and without initials.

The v10.0 files had open slots at the corners and a hole in the thumb scoop. **Don't print them.** They're archived in `../superseded/wood-v10.0-corner-holes/`, and the fix is described under "What was fixed" below.

## Load the AMS lite once, the same for every project
| Slot | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Wood | **Oak** | **Teak** | **Cherry** | **Walnut** |

Use the **textured PEI plate**. Every project uses the 0.16 mm High Quality profile with a 3 mm brim, no supports and no prime tower.

## The projects
| Project file | Cases on the plate | Time* | Filament | Colour swaps |
|---|---|---|---|---|
| `AB_Rollie_Book_wood_Kumiko_Dial_A1.3mf` | KUMIKO + DIAL, with A·B | 3 h 34 m | 69 g | 9 |
| `Rollie_Book_wood_Kumiko_Dial_A1_no_initials.3mf` | KUMIKO + DIAL | 3 h 29 m | 69 g | 4 |
| `AB_Rollie_Book_wood_Riva_Parquet_A1.3mf` | RIVA + PARQUET, with A·B | 3 h 50 m | 70 g | 24 |
| `Rollie_Book_wood_Riva_Parquet_A1_no_initials.3mf` | RIVA + PARQUET | 3 h 45 m | 70 g | 20 |
| `AB_Rollie_Book_wood_Endgrain_Cubes_A1.3mf` | ENDGRAIN + CUBES, with A·B | 4 h 18 m | 70 g | 25 |
| `Rollie_Book_wood_Endgrain_Cubes_A1_no_initials.3mf` | ENDGRAIN + CUBES | 4 h 09 m | 70 g | 16 |

\* Times and weights come from the A1-emulated slice. Bambu Studio will show a bit more: each colour swap adds about a minute and a 0.2–0.5 g purge.

**What's on each plate:** 4 objects, printed one after the other: lid A, tray A, lid B, tray B. They're laid out in a pinwheel so every object is at least 74 mm from every other, which the A1 needs to print by object without the toolhead hitting a finished part. **Leave them where they are** (don't press Arrange). If Bambu warns about clearance, the layout has been moved.

**Hinge sleeves:**
- Each case's small hinge sleeve prints in its own accent wood, standing beside a part of the **same colour**, so it adds no colour swaps.
- Match the sleeves to the cases by colour:

| Case | KUMIKO | DIAL | RIVA | PARQUET | ENDGRAIN | CUBES |
|---|---|---|---|---|---|---|
| Sleeve wood | walnut | walnut | oak | cherry | oak | walnut |

- Where they print:
  - **RIVA + PARQUET:** RIVA's oak sleeve stands by the PARQUET lid; PARQUET's cherry sleeve stands by the RIVA tray.
  - **ENDGRAIN + CUBES:** ENDGRAIN's oak sleeve stands by the CUBES lid; CUBES's walnut sleeve stands by the ENDGRAIN tray.

## Magnets: glue them in after printing
You need **4 × Ø5 × 2 mm magnets per case**, so 8 per plate. Each half has two open round pockets, one at each corner on the opening edge.

**Polarity** (once per case):
1. Stack the four magnets in one column.
2. Mark the **top** face of each one.
3. **Lid:** marked face **UP**. **Tray:** marked face **DOWN**.

**Gluing:**
1. Lay each part **inside-up**.
2. Put a small drop of super glue (CA gel is easiest) on the **floor** of each pocket.
3. Drop the magnet in.
4. Push it flat with a **toothpick**. Steel tweezers will pull it back out.
5. **Let the glue cure for 5–10 minutes before you close the case.** Uncured magnets jump towards each other.

The pocket floors are at the same depth as the sealed-in design, so the closing pull is still about 175 g.

**Hinge pin:** 1.75 mm PETG filament.

## What was fixed in v10.1 (after the 24 Nov test print)
- **Corners:** the case's big rounded corners were cutting into a square-cornered cavity. That left 0.04 mm walls at the opening-edge corners, which printed as slots and holes. The cavity, the lid's lip ring and the tray's lip groove now follow the rounded outline, with 2 mm of wall all round.
- **Magnet sockets:** moved 1.5 mm in from the side. The socket mouth now keeps 2 mm to the outside (it was 0.5 mm). The magnets also sit nearer the ends: 7.5 mm in, instead of 11 mm.
- **Thumb scoop:** now 2.6 mm deep instead of 3.2 mm, with a solid 1.2 mm backing. It can't open into the tip bay any more.
- **Everything else is unchanged:** looks, 2 mm ends, colours and fonts.

## How these were checked
`src/w_pair_verify.py` reads only the 3MF. All six print **ALL PASS** (34 checks each); the reports are in `checks/`. The checks:
1. **Bambu loader check,** emulated from Bambu's source at v02.03.01.51, v02.08.04.61 and v02.09.01.70: identical to the 26-flag baseline that loads fine.
2. **Settings:**
   - the same 366 keys, in the same order, as the v7.0 file that opened in Bambu Studio;
   - 4 × Bambu PLA Wood;
   - by object, with no pause anywhere.
3. **Plate:**
   - every pair of objects is at least 73 mm apart (Bambu needs more than 72.8);
   - everything plus the brim is on the bed;
   - both sleeves are present.
4. **Each lid and tray:**
   - R4.5 rounded edges;
   - colour work only in the first 5 layers;
   - two Ø5.35 glue pockets, open from floor to face;
   - **walls checked layer by layer:**
     - no inside opening comes within 1.1 mm of the outside (thinnest now 1.19 mm on the trays and 2.14 mm on the lids);
     - the tray cavity stays fully enclosed on every layer from floor to rim. This is the check the v10.0 corners would have failed.
5. **A1-emulated slice** of each file: it slices by object with the A1's 73 mm clearance, with no pauses.

An older, independent scanner (`superseded/.../` method) agrees. The only spots under 1.1 mm are the designed 1.0 mm rings round the magnet sockets, which are inside the case.

**Expected slicer notes (benign):** "Long bridging" / "Loose extrusions" on parts with **engraved** patterns (KUMIKO, the DIAL and PARQUET backs). These are the 45° stepped groove ceilings in the first 3 face-down layers.
