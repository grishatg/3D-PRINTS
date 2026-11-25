# Rollie Book · wood PLA · print files (v10.6, 25 Nov)

There are six Bambu Studio projects. Each prints **two complete cases** (lid and tray each) on one plate, **by object**, with **no pauses, no brim and no supports**. You glue the magnets in afterwards.
- There are three pairs, each **with A·B** or **without initials**. Print one version of each pair.
- **Nothing else to print:** the hinge sleeve is gone. The middle hinge knuckle is now part of the tray.
- **Delete every older 3MF and print only these (v10.6).**

## What changed since your first full print (v10.5)
1. **Hinge: three knuckles on the back, two on the lid.** The loose sleeve is now a third knuckle on the tray, so each case is two printed parts and a pin. The sleeve plate is gone. See `checks/hinge_3_and_2.png`.
2. **The plate-side faces (cubes and squares).** Your lids showed four nested rings and a centre dot inside every square and cube. Two things caused it, and both are changed:
   - **The toolpath.** Each small cell was filled with four wall loops. Now each cell is **one outline plus straight lines running along the case**, so there are no rings and no centre dots. What shows of the lines reads as grain. See `checks/faces_before_after.png`.
   - **The squish.** The rings showed most where the first layer went down a touch high: the front and back of the bed in your photos. The first layer now gets **5 % more plastic**. The rest is on the printer: see checklist item 4.
3. **No brim.** Each part sits on the plate with its whole face, and your first print stuck well.
4. **No Cherry.** Slot 3 isn't used by any design:
   - CUBES base: Walnut (was Cherry).
   - RIVA hull: Walnut with Oak seams (was Cherry).
   - PARQUET staves: Teak and Walnut in the Oak lid (was Teak and Cherry).
5. **Hinge-side layers.** The rounded edges were modelled in 0.1 mm steps, which beat against the 0.12 mm print layers and left a band every five layers, most visible on the lid's hinge knuckles. They now step evenly, and the knuckle barrels are four times smoother.

## The projects
| Project file | Cases | Time* | Colour changes | Walnut |
|---|---|---|---|---|
| `Rollie_Book_wood_Endgrain_Cubes_A1_no_initials.3mf` | ENDGRAIN + CUBES | **5 h 21 m** | 19 | 48 g |
| `AB_Rollie_Book_wood_Endgrain_Cubes_A1.3mf` | ENDGRAIN + CUBES, with A·B | **5 h 35 m** | 28 | 48 g |
| `Rollie_Book_wood_Riva_Parquet_A1_no_initials.3mf` | RIVA + PARQUET | **4 h 46 m** | 25 | 58 g |
| `AB_Rollie_Book_wood_Riva_Parquet_A1.3mf` | RIVA + PARQUET, with A·B | **4 h 54 m** | 29 | 58 g |
| `Rollie_Book_wood_Kumiko_Dial_A1_no_initials.3mf` | KUMIKO + DIAL | **4 h 30 m** | 3 | 45 g |
| `AB_Rollie_Book_wood_Kumiko_Dial_A1.3mf` | KUMIKO + DIAL, with A·B | **4 h 38 m** | 8 | 45 g |

\* **How the times are estimated:**
- an A1-emulated slice using Bambu's own speeds and accelerations from the preset;
- the 54 s load and unload per colour change;
- the purge for every change.

Bambu Studio shows its own figure, which may differ a little. Add about 5 minutes for heating and levelling.

**Each plate uses about 71 g in the parts:** 11–13 g of Oak, 2–13 g of Teak and the Walnut shown, plus up to 8 g of purge.

**Walnut is the one to watch.** The three plates together take about **151 g of Walnut** plus about 15 g of purge. RIVA + PARQUET alone needs about 66 g.

## Before you press Print: checklist
1. **Use these six files only (v10.6).**
2. **AMS lite slots:** 1 **Oak**, 2 **Teak**, 3 **empty** (not used), 4 **Walnut**. On Send, check the filament mapping shows 1 → Oak, 2 → Teak, 4 → Walnut.
3. **Textured PEI plate, washed:**
   - use washing-up liquid and warm water, rinse and dry;
   - don't touch the print surface afterwards;
   - with no brim, a clean plate is what holds the corners down.
4. **Tick "Bed levelling" in the Send dialog, and check the nozzle tip is clean first.** This matters for the faces: your first print's rings showed where the first layer sat slightly high. A blob on the nozzle tip throws the levelling off.
5. **Filament:** at least **60 g of Walnut** for ENDGRAIN + CUBES or KUMIKO + DIAL, **70 g** for RIVA + PARQUET; 20 g each of Oak and Teak.
6. **Don't press Arrange, and don't move the parts.** The four parts are spaced so the A1 can print them one at a time without the toolhead hitting a finished part. If Bambu ever warns about clearance, reload the file.
7. **Purge dialog: leave it alone.** Don't press Re-calculate, and keep the Multiplier at 1.
8. **Dry the wood spools first** (55 °C, 8 h). Wet wood PLA strings, blobs and can snap in the AMS lite.
9. **Look at layer 1 in Bambu's Preview (10 seconds):**
   - press **Slice**, then drag the layer slider right down to **layer 1**;
   - on the lids, each square or cube should show **one outline and straight lines**, not nested rings;
   - with A·B: the letters solid, both holes in the B and the hole in the A open.

## What's on each plate
Four objects, printed one after the other: lid A, tray A, lid B, tray B.

Each part does its colour changes in its first few layers, so the changes come in four bursts through the print, not all at the start.

**ENDGRAIN + CUBES, no initials, as an example:**

| Part | Starts | Ends | Colour changes |
|---|---|---|---|
| ENDGRAIN lid (teak, walnut squares) | 0:00 | 0:59 | 6 |
| ENDGRAIN tray (walnut) | 0:59 | 2:35 | 1 |
| CUBES lid (oak, teak and walnut cubes) | 2:35 | 3:45 | 11 |
| CUBES tray (walnut) | 3:45 | 5:21 | 1 |

## Putting a case together
You need, per case: **4 × Ø5 × 2 mm magnets** and **88 mm of 1.75 mm filament** for the hinge pin.

1. **Magnets first** (below), and let the glue cure.
2. **Drop the lid onto the tray** so the lid's two knuckles sit between the tray's three.
3. **Push the pin through from one end.** It grips in the tray's two end knuckles and slides through the other three. Trim it flush.

The lid swings freely to about 150°, and stops at 166°.

## Magnets: flush, glued in after printing
**How they sit:**
- Each pocket is exactly magnet-deep, with its floor on a layer boundary. A glued magnet sits **0.04 mm below the face**: flush to the eye, and it can't stick out and stop the case closing.
- Closed, the magnet faces are **0.34 mm apart**. That's about 780 g of pull per case on an N35 model.
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
| none | ~780 g |
| 0.15 mm (e.g. one layer of electrical tape) | ~675 g |
| 0.45 mm | ~525 g |
| 0.7 mm (e.g. thin felt) | ~430 g |

## Print quality
Bambu's own **0.12 mm High Quality @BBL A1** preset. The inlays are exactly 5 layers deep and the magnet floors land on layer boundaries. On top of the preset:
- **4 walls**, a 1.0 mm top skin and 6 bottom layers.
- **A slow, narrow first layer** (40 mm/s, 0.42 mm lines) with **5 % extra flow**. That layer is the outside face.
- **The face layer's lines run along the case,** like grain (PARQUET: at 45°, with its staves).
- **Arachne walls** and **scarf seams** on the outer walls.
- **Travel avoids crossing walls.**
- **No brim.** To add one back: Process → Others → Brim type → Outer brim only.

**How each face is laid:**

| Design | Lid | Tray |
|---|---|---|
| ENDGRAIN, CUBES, KUMIKO, RIVA | one outline + lines | one outline + lines |
| DIAL | one outline + lines | wall loops (its 1.85 mm studs are too small for lines) |
| PARQUET | wall loops (they run along each stave, like its grain) | wall loops |

Every **tray with A·B** keeps its wall loops, whatever the design: they are what fills each letter stroke completely.

## If the faces still show lines at one end
That is the first layer going down slightly high in that part of the bed. In order:
1. **Bed levelling ticked, nozzle tip clean, plate washed** (checklist items 3 and 4).
2. **Run the printer's full calibration** from its screen, with the textured plate on.
3. **Tell me which parts and which ends.** The plate offset in the printer's start routine can be lowered a little for these files. Owners report it helps on the textured plate, but one reports the printer overriding it, so I've left it at Bambu's value until we know it's needed.

## How these were checked
`src/w_pair_verify.py` reads only the 3MF.
- **Results:** all six pass every check: 61–62 for the no-initials plates, 63 for the A·B plates.
- **Reports:** in `checks/`.

1. **Bambu loader check,** emulated from Bambu's source at v02.03.01.51, v02.08.04.61 and v02.09.01.70. It's identical to the 26-flag baseline of the files you've already opened and printed.
2. **Settings:**
   - 4 × Bambu PLA Wood, 0.12 mm High Quality, scarf seams;
   - by object, no pause, no brim;
   - first-layer flow 1.05.
3. **Plate:**
   - every pair of objects is 74 mm apart (Bambu needs more than 72.8);
   - everything is on the bed;
   - no sleeve parts;
   - each object carries the right face style.
4. **Each lid and tray:**
   - R4.5 rounded edges that step evenly from layer to layer;
   - colour work only in the first 5 layers;
   - walls at least 1.1 mm to the outside on every layer, and the tray cavity enclosed;
   - magnet pockets exactly magnet-deep;
   - closed case: magnet faces 0.34 mm apart.
5. **Hinge:**
   - three knuckles on the tray, two on the lid, 0.6 mm between neighbours;
   - a straight Ø1.75 pin passes through all five, grips in the two end knuckles and slides through the other three;
   - the lid drops straight onto the tray;
   - the lid swings 0–165° with no contact, and at least 0.12 mm of running clearance at every knuckle up to 150°.
6. **A1-emulated slice of the file exactly as laid out,** with the per-object face settings applied: no pauses, time and filament as in the table.
7. **The A·B as sliced:** A, dot and B 98–100 % covered, no bare spot, holes open.
8. **The faces as sliced:** every wood covers its own area (98–100 %), no rings where lines are used, and no bare spot a 0.5 mm dot fits in. One A·B tray (CUBES) has a single 0.2 mm² spot under the A's crossbar; every other face has none.

**Also checked:**
- **Independent second scanner** (separate code) on all 24 lids and trays: no outer wall under 1.1 mm. The only thin spots it flags are deliberate interior features, the same on every design:
  - the lid's magnet bosses (0.8 mm, chamfered at the top);
  - the 1.0 mm socket walls;
  - the tip-bay ribs;
  - the hinge-clearance edge and barrel tops, now on three tray knuckles.
- **The older PETG files** still rebuild identically.

**What has not been done:** nobody has opened these v10.6 files in the real Bambu Studio yet. The slice check uses a different slicer set up like the A1. The first real slice is step 9 of the checklist.

**Expected slicer notes (benign):**
- "Long bridging" on parts with an **engraved** pattern. This is layer 5 roofing over the engraved grooves; it's what makes the floor of ENDGRAIN's sunken squares look stranded.
- "Low bed adhesion, consider a brim" on a tray with an engraved back. The brim was removed on purpose.
