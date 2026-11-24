# Rollie Book · wood PLA · print files (A1 + AMS lite)

Fourteen Bambu Studio projects:
- **12 production files:** all 6 designs, each with and without A·B.
- **2 test prints** to run before the magnets arrive.

Every file is one plate, printed **by object**, on the **0.16 mm High Quality @BBL A1** profile, with **Bambu PLA Wood @BBL A1** in all four slots.

## Load the AMS lite once, the same for every design
| Slot | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Wood | **Oak** | **Teak** | **Cherry** | **Walnut** |

Use the **textured PEI plate**. Each file has a 3 mm brim, no supports and no prime tower (the A1 purges into its chute).

## The files

**Production** (magnets sealed in, self-pausing):

| Design | With A·B | Without initials | Woods used | Colour swaps | Time* | Filament* |
|---|---|---|---|---|---|---|
| **KUMIKO** | `AB_Rollie_Book_Kumiko_wood_A1.3mf` | `Rollie_Book_Kumiko_wood_A1_no_initials.3mf` | Oak, Walnut | 2 | 1 h 41 m | 34 g |
| **RIVA** | `AB_Rollie_Book_Riva_wood_A1.3mf` | `Rollie_Book_Riva_wood_A1_no_initials.3mf` | Cherry, Oak | 11 | 1 h 44 m | 34 g |
| **DIAL** | `AB_Rollie_Book_Dial_wood_A1.3mf` | `Rollie_Book_Dial_wood_A1_no_initials.3mf` | Teak, Walnut (+ Oak A·B) | 7 / 2 | 1 h 55 m / 1 h 50 m | 35 g |
| **PARQUET** | `AB_Rollie_Book_Parquet_wood_A1.3mf` | `Rollie_Book_Parquet_wood_A1_no_initials.3mf` | all four | 16 / 12 | 2 h 09 m / 2 h 05 m | 35 g |
| **ENDGRAIN** | `AB_Rollie_Book_Endgrain_wood_A1.3mf` | `Rollie_Book_Endgrain_wood_A1_no_initials.3mf` | Teak, Walnut, Oak | 12 / 7 | 2 h 03 m / 1 h 58 m | 34 g |
| **CUBES** | `AB_Rollie_Book_Cubes_wood_A1.3mf` | `Rollie_Book_Cubes_wood_A1_no_initials.3mf` | all four | 16 / 12 | 2 h 18 m / 2 h 14 m | 35 g |

**Test prints** (magnets glued in afterwards, no pauses):

| Design | File | Time* | Filament* |
|---|---|---|---|
| **KUMIKO** | `TEST_AB_Rollie_Book_Kumiko_wood_A1_glue_magnets.3mf` | 1 h 38 m | 29.5 g |
| **RIVA** | `TEST_AB_Rollie_Book_Riva_wood_A1_glue_magnets.3mf` | 1 h 37 m | 28.8 g |

\* Times and weights come from the A1-emulated slice. Bambu Studio's estimate will run longer on the multi-colour files: each colour swap adds about a minute, and each purge 0.2–0.5 g.

## Production files: the magnet pauses
You need **4 × Ø5 × 2 mm magnets** per case.

**The pauses:**
- The printer **chimes and pauses itself twice**: first on the **cover** (screen layer ≈ **22**, z 3.56), then on the **tray** (screen layer ≈ **87**, z 8.36).
- At each pause, drop **both** magnets into the two round corner pockets, press them flat, then press **Resume**.
- **If a pause doesn't happen,** pause by hand as soon as the screen shows layer 22 or 87. The pocket is still open at that point.

**Polarity** (do this once, before printing):
1. Stack all four magnets in one column.
2. Mark the **top** face of each one with a pen.
3. **Cover:** marked face **UP**. **Tray:** marked face **DOWN**.

The two halves then attract when the case is closed. 0.8 mm of wood (5 layers) seals over each magnet. The pull is about 175 g (N35 estimate).

## Test files: how they differ, and how to glue
| | Production | **Test** |
|---|---|---|
| Magnets | Sealed in at a pause | **Pockets left open**: glue the magnets in afterwards |
| Pauses | 2, with chime | **None** |
| Walls / infill | 3 walls, 15 % gyroid | **2 walls, 10 % gyroid** |
| Shells | Top 5 (min 1.0 mm), bottom 4 | **Top 5 (min 0.8 mm), bottom 3** |
| Shape, patterns, A·B, hinge | — | **Identical** |
| Filament | — | **About 12–16 % less** |

The case is mostly solid wall, so lighter infill only saves 4–6 g per case. The test is still representative:
- **Fit:** the hinge, closure and rollie fit are exactly as in production.
- **Pull:** the pocket floor is at the production magnet depth, so with the magnet glued to the floor the pull matches production.

**Gluing (super glue / CA gel):**
1. Lay the parts **inside-up**, the way they came off the plate.
2. Put a small drop of glue on the **floor** of each pocket.
3. Drop the magnet in using the same polarity rule as production: **cover marked UP, tray marked DOWN**.
4. Push it flat with a **toothpick**. Steel tweezers will pull it back out.
5. **Let the glue cure for 5–10 minutes before closing the case.** Uncured magnets jump out of their pockets towards each other.

## Wood PLA notes
- **Nozzle:** use a **hardened-steel nozzle**. Wood fibres are mildly abrasive and can clog. Go up to 0.6 mm if you get clogs.
- **Drying:** dry the spools first (55 °C, 8 h).
- **Temperatures:** the preset prints at 220 °C, with the bed at 65 °C.
- **Hinge pin:** use 1.75 mm **PETG** filament.
- **Heat:** PLA softens at about 55–60 °C, so **don't leave the case in a hot car**.

## How these were checked
Each file was checked by `src/w_verify.py`, which reads **only the 3MF**. All 14 print **ALL PASS**; the full reports are in `checks/`. The checks:
1. **Bambu loader check**, emulated from Bambu's source at v02.03.01.51, v02.08.04.61 and v02.09.01.70. The output is identical to the 26-flag baseline that loads fine.
2. **Settings:**
   - the same 366 keys, in the same order, as the v7.0 file that opened in Bambu Studio;
   - 4 × Bambu PLA Wood;
   - by object, with no prime tower.
3. **Plate:**
   - print order is cover → tray → sleeve;
   - every mesh is valid;
   - A1 by-object clearance is met;
   - every inlay and the A·B sit in the first 5 layers, so there are no colour swaps up the walls;
   - the R4.5 rounded long edges are present.
4. **Magnet pockets,** sliced layer by layer:
   - **Production:** open on every layer up to each pause and sealed by the layer the printer pauses before.
   - **Test:** open from the floor right up to the face.
5. **A1-emulated slice of the file itself:**
   - **Production:** exactly 2 pauses, cover then tray, at the right layer.
   - **Test:** no pauses.

**Expected slicer notes (benign):**
- **"Floating bridge anchors"** on each production cover: this is the 5-layer roof over the sealed magnet pocket. The magnet sits 0.24 mm under it, and the note disappears in the open-pocket test files.
- **"Long bridging" / "Loose extrusions"** on parts with **engraved** patterns (KUMIKO, the DIAL and PARQUET backs): these are the 45° stepped groove ceilings in the first 3 face-down layers. An A/B slice placed them all below z 0.7 and showed they don't depend on infill. RIVA has no engraving and shows neither; the ENDGRAIN and CUBES backs (larger engraved areas) didn't trigger them either.
