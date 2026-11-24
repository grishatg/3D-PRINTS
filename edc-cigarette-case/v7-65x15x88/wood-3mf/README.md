# Rollie Book · wood PLA · FINAL print files (v10.5, 24 Nov)

There are seven Bambu Studio projects, all printing **by object** with **no pauses**. You glue the magnets in afterwards.
- **Six case plates.** Each prints **two complete cases** (lid and tray). There are three pairs, each **with A·B** or **without initials**; print one version of each pair.
- **One hinge-sleeve plate** with all six sleeves (50 min).
- **Delete every older 3MF and print only these (v10.5).**

## Print plan: the long, complicated plates run overnight
| When | Plate | Time* (without initials) | Colour changes (without) |
|---|---|---|---|
| **Tonight** | **ENDGRAIN + CUBES**: the longest, and the showpiece | **5 h 32 m** (5 h 18 m) | 28 (19) |
| Tomorrow morning | **Hinge sleeves**, all six | **50 m** | 2 |
| Tomorrow, daytime | **KUMIKO + DIAL**: the simplest, the one to run while you're around | **4 h 34 m** (4 h 26 m) | 8 (3) |
| Tomorrow night | **RIVA + PARQUET**: the most colour changes | **4 h 55 m** (4 h 48 m) | 29 (25) |

Each part does its colour changes in its first few layers, and the four parts print one after another. So the changes are spread through the night, not bunched at the start. Dry spools (checklist item 7) are what keep the AMS lite feeding cleanly at 3 a.m.

\* **How the times are estimated:**
- an A1-emulated slice using Bambu's own speeds and accelerations from the preset;
- the 54 s load and unload per colour change;
- the purge for every change.

Bambu Studio shows its own figure, which may differ a little. Add about 5 minutes for heating and levelling.

## Before you press Print: checklist
1. **Use these seven files only (v10.5).** Earlier versions have a broken B, corner holes, deep magnets or the sleeves on the case plates.
2. **AMS lite slots:** 1 **Oak**, 2 **Teak**, 3 **Cherry**, 4 **Walnut**. When Bambu Studio shows the **filament mapping** on Send, check that 1→Oak, 2→Teak, 3→Cherry and 4→Walnut.
3. **Textured PEI plate, washed:**
   - use washing-up liquid and warm water, rinse and dry;
   - don't touch the print surface afterwards;
   - a fingerprint is the usual reason a part lets go at hour 4.
4. **Filament:** keep at least **60 g on each spool** for a case plate. The most any plate takes from one spool is 43 g (walnut, KUMIKO + DIAL), plus up to 9 g of purge.
5. **Don't press Arrange, and don't move the parts.** The four parts on each plate are spaced so the A1 can print them one at a time without the toolhead hitting a finished part. If Bambu ever warns about clearance, reload the file.
6. **Purge dialog: leave it alone.** Don't press Re-calculate, and keep the Multiplier at 1, or the times above grow.
7. **Dry the wood spools first** (55 °C, 8 h). Wet wood PLA strings, blobs and can snap in the AMS lite.
8. **Check the A·B in Bambu (10 seconds):**
   - press **Slice**, then in **Preview** drag the layer slider right down to **layer 1** (the outside face);
   - zoom in on each tray's A·B;
   - it should look like `checks/ab_toolpaths_*.png`: solid letters, both holes in the B and the hole in the A open.
9. **Nozzle:** wood fibres wear stainless nozzles over many prints. A hardened-steel 0.4 mm nozzle is the long-term fix.

## What's new in v10.5
- **The A·B is fixed.** Your screenshot showed the B on the CUBES tray with missing bits. There were three causes, all fixed in every design:
  1. **The B's lower hole was filled in.** The font draws that hole in a way the old code read as solid. The letters are now traced from the font outlines properly, holes and all.
  2. **Hairlines too thin to print.** Some serif strokes were thinner than a 0.4 mm nozzle can lay, so the slicer dropped them. Every stroke is now at least **0.5 mm** and every hole at least **0.6 mm** wide. The serif letters are also a touch bigger (7 mm tall, was 6).
  3. **A hairline gap in one typeface's B**, at the middle bar, is now closed.
- **A new check slices every file and reads the first layer back, line by line.** That layer is the outside face, since the trays print face-down.
  - **Inlaid A·B:** A, dot and B come out **98–100 % covered** in their wood, with **no bare spot** as big as 0.3 mm. The holes in the A and B stay open and are filled by the body wood.
  - **KUMIKO's engraved A·B:** the letters stay **100 % open**, and the islands inside the A and B print.
  - Pictures: `checks/ab_toolpaths_*.png`; before and after letters: `checks/ab_letters_before_after.png`.
- **Back on Bambu's 0.12 mm High Quality.** You said up to 6 h is fine, so every plate gets the finer 0.12 mm layers.
- **The hinge sleeves have their own short morning plate,** so the overnight plates carry just the cases.

## The projects
| Project file | Cases | Time | Filament | Colour changes |
|---|---|---|---|---|
| `AB_Rollie_Book_wood_Endgrain_Cubes_A1.3mf` | ENDGRAIN + CUBES, with A·B | **5 h 32 m** | 70 g | 28 |
| `Rollie_Book_wood_Endgrain_Cubes_A1_no_initials.3mf` | ENDGRAIN + CUBES | **5 h 18 m** | 70 g | 19 |
| `AB_Rollie_Book_wood_Riva_Parquet_A1.3mf` | RIVA + PARQUET, with A·B | **4 h 55 m** | 69 g | 29 |
| `Rollie_Book_wood_Riva_Parquet_A1_no_initials.3mf` | RIVA + PARQUET | **4 h 48 m** | 69 g | 25 |
| `AB_Rollie_Book_wood_Kumiko_Dial_A1.3mf` | KUMIKO + DIAL, with A·B | **4 h 34 m** | 70 g | 8 |
| `Rollie_Book_wood_Kumiko_Dial_A1_no_initials.3mf` | KUMIKO + DIAL | **4 h 26 m** | 70 g | 3 |
| `Rollie_Book_wood_hinge_sleeves_all_six_A1.3mf` | the six hinge sleeves | **50 m** | 3 g | 2 |

The filament column is what goes into the parts; purge adds up to 9 g per plate.

## Print quality
Bambu's own **0.12 mm High Quality @BBL A1** preset. The inlays are exactly 5 layers deep and the magnet floors land on layer boundaries. On top of the preset:
- **4 walls**, so no infill shows through the 2 mm walls, plus a 1.0 mm top skin and 6 bottom layers.
- **A slow, narrow first layer** (40 mm/s, 0.42 mm lines). That layer is the outside face, so the inlays, engraving and A·B come out crisp.
- **Arachne walls,** which vary the line width to fill thin strokes, which matters for the letters.
- **Scarf seams** on the outer walls, which blend the seam line on the curved sides.
- **Travel avoids crossing walls.**
- A 3 mm brim on the outside of each part.

**Seams:** if you'd rather not use scarf seams, go to **Filament settings → Seam → Scarf seam type → None** for each filament.

## What's on each plate
**Case plates:** four objects, printed one after the other: lid A, tray A, lid B, tray B.

**Hinge-sleeve plate:** six separate sleeves in three groups, one wood each. Match them to the cases by colour:

| Case | KUMIKO | DIAL | RIVA | PARQUET | ENDGRAIN | CUBES |
|---|---|---|---|---|---|---|
| Sleeve wood | walnut | walnut | oak | cherry | oak | walnut |

## Magnets: flush, glued in after printing
You need **4 × Ø5 × 2 mm magnets per case**, 8 per plate.

**How they sit:**
- Each pocket is exactly magnet-deep, with its floor on a layer boundary. A glued magnet sits **0.04 mm below the face**: flush to the eye, and it can't stick out and stop the case closing.
- Closed, the magnet faces are **0.34 mm apart**. The test print had 2.4 mm.
- That's about **4.5× the pull of the test print**: ~780 g for both pairs on an N35 model. It's the most these magnets can give.
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

**Hinge pin:** 1.75 mm PETG filament.

## Your question: could the printer cap the magnets last, after an overnight pause?
Not on these plates:
- **The plates print by object,** because each case uses different woods, so the printer finishes each part before starting the next. It can't come back at the end to put the last layers on earlier parts.
- **The hinge knuckles stand taller than the magnet bosses,** so the cap layers would never be the last layers anyway.
- **An overnight pause leaves the nozzle sitting hot at 220 °C,** which chars wood PLA.

Glued flush is also the strongest option: any plastic cap between the magnets weakens the pull.

## How these were checked
`src/w_pair_verify.py` reads only the 3MF.
- **Results:** all seven pass **ALL PASS**: 40 checks for each A·B plate, 38–39 for the no-initials plates, 15 for the sleeve plate.
- **Reports:** in `checks/`.

1. **Bambu loader check,** emulated from Bambu's source at v02.03.01.51, v02.08.04.61 and v02.09.01.70. It's identical to the 26-flag baseline that loads fine, using the same key set as the files you've already opened.
2. **Settings:**
   - 4 × Bambu PLA Wood;
   - 0.12 mm High Quality;
   - scarf seams on;
   - by object, with no pause anywhere.
3. **Plate:**
   - every pair of objects is at least 74 mm apart (Bambu needs more than 72.8);
   - everything plus the brim is on the bed;
   - there are no sleeves on the case plates.
4. **Each lid and tray:**
   - R4.5 rounded edges;
   - colour work only in the first 5 layers;
   - walls at least 1.1 mm to the outside on every layer (thinnest 1.19 mm);
   - the tray cavity enclosed from floor to rim;
   - magnet pockets exactly magnet-deep, so a glued magnet sits 0.04 mm below the face;
   - closed case: magnet faces 0.34 mm apart.
5. **A1-emulated slice of the file exactly as laid out:** sequential with the A1's 73 mm clearance, and no pauses.
6. **The A·B as sliced:**
   - every first-layer line of every tray is read back at its real width;
   - the letters must be complete and the holes open, as described above;
   - files without initials must have no letters at all.

**Independent second scanner** (separate code), on all 24 lids and trays:
- No outer wall is thinner than 1.1 mm.
- The only thin spots it flags are deliberate interior features, identical on every design:
  - the 0.8 mm lid magnet bosses;
  - the 1.0 mm socket walls;
  - the filter-tip bay ribs;
  - the hinge-clearance edge at the top of the tray's spine wall.

**Expected slicer notes (benign):** "Long bridging" on parts with an **engraved** pattern. This is layer 5 roofing over the engraved grooves. Each bridge only crosses a groove about 0.5–0.9 mm wide, with solid layers either side, and it's hidden inside the part.
