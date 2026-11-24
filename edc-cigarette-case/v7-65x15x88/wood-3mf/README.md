# Rollie Book · wood PLA · FINAL print files (v10.4, 24 Nov)

There are six Bambu Studio projects. Each one prints **two complete cases on one plate**, **by object**, with **no pauses**; you glue the magnets in afterwards.
- There are three pairs, each with A·B and without initials.
- **Delete every older 3MF and print only these.**

## Before you press Print: 60-second checklist
1. **Use these six files only (v10.4).** Earlier versions have corner holes, deep magnets or longer print times.
2. **AMS lite slots:** 1 **Oak**, 2 **Teak**, 3 **Cherry**, 4 **Walnut**. When Bambu Studio shows the **filament mapping** on Send, check that 1→Oak, 2→Teak, 3→Cherry and 4→Walnut.
3. **Textured PEI plate**, as set in the file.
4. **Don't press Arrange, and don't move the parts.** The four parts on each plate are spaced so the A1 can print them one at a time without the toolhead hitting a finished part. If Bambu ever warns about clearance, reload the file.
5. **Purge dialog: leave it alone.** Don't press Re-calculate, and keep the Multiplier at 1, or the times below grow.
6. **Dry the wood spools first** (55 °C, 8 h). Wet wood PLA strings, blobs and can snap in the AMS lite.
7. **Nozzle:** wood fibres wear stainless nozzles over many prints. A hardened-steel 0.4 mm nozzle is the long-term fix.

## The projects
| Project file | Cases | Estimated time* | Filament | Colour swaps |
|---|---|---|---|---|
| `AB_Rollie_Book_wood_Kumiko_Dial_A1.3mf` | KUMIKO + DIAL, with A·B | **3 h 43 m** | 69 g | 9 |
| `Rollie_Book_wood_Kumiko_Dial_A1_no_initials.3mf` | KUMIKO + DIAL | **3 h 34 m** | 69 g | 4 |
| `AB_Rollie_Book_wood_Riva_Parquet_A1.3mf` | RIVA + PARQUET, with A·B | **4 h 05 m** | 70 g | 24 |
| `Rollie_Book_wood_Riva_Parquet_A1_no_initials.3mf` | RIVA + PARQUET | **3 h 58 m** | 70 g | 20 |
| `AB_Rollie_Book_wood_Endgrain_Cubes_A1.3mf` | ENDGRAIN + CUBES, with A·B | **4 h 37 m** | 70 g | 25 |
| `Rollie_Book_wood_Endgrain_Cubes_A1_no_initials.3mf` | ENDGRAIN + CUBES | **4 h 23 m** | 70 g | 16 |

\* **How the times are estimated:** an A1-emulated slice using Bambu's own speeds and accelerations from the preset, the 54 s load and unload per colour swap, and the purge for every swap. Bambu Studio shows its own figure, which should be within a few minutes of this. The printer also spends about 5 minutes heating and levelling before it starts.

**The time targets you set:** the simple pair (KUMIKO + DIAL) stays under 4.5 h. The multi-colour pairs (RIVA + PARQUET, ENDGRAIN + CUBES) stay under 5 h.

## Print quality
Bambu's own **0.16 mm High Quality @BBL A1** preset. The whole design is built on this layer grid: the inlays are exactly 4 layers, the engraving steps are 45°, and the magnet floors land on layer boundaries. On top of that preset:
- **4 walls**, so no infill shows through the 2 mm walls, plus a 1.0 mm top skin.
- **A slow, narrow first layer** (40 mm/s, 0.42 mm lines). That layer is the outside face, so the inlays, engraving and A·B come out crisp.
- **Scarf seams** on the outer walls, which blend the seam line on the curved sides.
- **Travel avoids crossing walls.**
- Outer walls run at Bambu's High Quality 60 mm/s.

**Seams:** if you'd rather not use scarf seams, go to **Filament settings → Seam → Scarf seam type → None** for each filament.

## What's on each plate
There are four objects, printed one after the other: lid A, tray A, lid B, tray B.

**Hinge sleeves:** each case's sleeve prints in its own accent wood, standing next to a part of the **same colour**, and their brims join. Snap them apart after printing. Match the sleeves to the cases by colour:

| Case | KUMIKO | DIAL | RIVA | PARQUET | ENDGRAIN | CUBES |
|---|---|---|---|---|---|---|
| Sleeve wood | walnut | walnut | oak | cherry | oak | walnut |

## Magnets: flush, glued in after printing
You need **4 × Ø5 × 2 mm magnets per case**, 8 per plate.

**How they sit:**
- Each pocket is exactly magnet-deep, and its floor is placed on a layer boundary. A glued magnet sits **0.08 mm below the face**: flush to the eye, and it can't stick out and stop the case closing.
- Closed, the magnet faces are **0.30 mm apart**. The test print had 2.4 mm.
- That's about **4.6× the pull of the test print**: ~815 g for both pairs on an N35 model. It's the maximum these magnets can give.
- Each lid magnet sits inside its round boss, with the full 2 mm lid plate behind it, so nothing shows on the outside.

**Polarity** (once per case):
1. Stack the four magnets in one column.
2. Mark the **top** face of each one.
3. **Lid:** marked face **UP**. **Tray:** marked face **DOWN**.

**Gluing:**
1. Lay each part **inside-up**.
2. Put **one tiny drop** of super glue (CA gel) on the floor of each pocket. The pocket is only magnet-deep, so extra glue wells up.
3. Press each magnet **flush** with a toothpick or the flat end of a plastic pen, not steel tweezers. Wipe off any glue that comes up.
4. **Check the polarity while the glue is still wet.** Gently close the case: both corners must pull shut. If a corner pushes apart, flip that lid magnet straight away.
5. **Leave it open for 10 minutes to cure.** At this distance the magnets will rip out of wet glue.

**Too strong?** Stick tape or thin felt on each **lid** magnet. No reprint is needed.

| Padding on each lid magnet | Approximate pull |
|---|---|
| none | ~815 g |
| 0.15 mm (e.g. one layer of electrical tape) | ~700 g |
| 0.45 mm | ~540 g |
| 0.7 mm (e.g. thin felt) | ~445 g |

**Hinge pin:** 1.75 mm PETG filament.

## What changed in this final version
- **v10.1:** fixed the slots at the corners and the hole in the thumb scoop. Walls are now at least 1.2 mm everywhere, and the tray cavity is enclosed on every layer.
- **v10.3 / v10.4:** flush magnets, with the pocket floors snapped to the layer grid so the printed depth is exact.
- **v10.4:** the 0.16 mm High Quality profile with extras, so every plate fits your time targets.

## How these were checked
`src/w_pair_verify.py` reads only the 3MF. All six print **ALL PASS**, 37 checks each; the reports are in `checks/`.
1. **Bambu loader check,** emulated from Bambu's source at v02.03.01.51, v02.08.04.61 and v02.09.01.70. It's identical to the 26-flag baseline that loads fine, using the same key set as the test files you've already opened.
2. **Settings:**
   - 4 × Bambu PLA Wood;
   - 0.16 mm High Quality;
   - scarf seams on;
   - by object, no pause anywhere.
3. **Plate:**
   - every pair of objects is at least 74 mm apart (Bambu needs more than 72.8);
   - everything plus the brim is on the bed;
   - both sleeves are present.
4. **Each lid and tray:**
   - R4.5 rounded edges;
   - colour work only in the first 5 layers;
   - walls of at least 1.1 mm to the outside on every layer (thinnest 1.19 mm), and the tray cavity enclosed floor to rim. An independent second scanner agrees, with zero thin outer walls.
   - magnet pockets flush, 0.08 mm deep;
   - closed case: magnet faces 0.30 mm apart.
5. **A1-emulated slice** of every file: sequential with the A1's 73 mm clearance, with no pauses.

**Expected slicer notes (benign):** "Long bridging" / "Loose extrusions" on parts with **engraved** patterns (KUMIKO, the DIAL, PARQUET and ENDGRAIN backs). These are the 45° stepped groove ceilings in the first face-down layers.
