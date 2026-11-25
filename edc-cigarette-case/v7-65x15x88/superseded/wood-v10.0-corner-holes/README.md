# Superseded: wood PLA v10.0 files. Do not print.

These files have the defect found in the owner's first wood test print on 24 Nov.

**The defect:**
- **Slot and hole at each opening-edge corner.** The case has big rounded corners (squircle, about 17.6 mm sweep on the opening edge). But the inside cavity, the cover's lip ring and the tray's lip groove were square-cornered boxes.
- **Why it only showed now:** once the end walls went from 9 mm to 2 mm, the cavity corner came within **0.04–0.3 mm** of the outside, from 2 mm above the back face up to the rim. The printer can't lay a wall that thin, so it left a vertical slot with a hole at the bottom.
- **Magnet sockets:** their chamfered mouths left only about 0.5 mm to the outside at the parting line.
- **Thumb scoop:** cut 3.2 mm into a 2.6 mm side wall, so it opened into the tip bay.

**The fix (v10.1)** is in `src/v7.py` and `src/v5.py`. The new files are in `../../wood-3mf/`.
- **Cavity, lip ring and lip groove:** follow the rounded outline, with 2 mm of wall all round.
- **Magnet columns:** sit so the socket mouth keeps 2 mm to the side.
- **Thumb scoop:** 2.6 mm deep, with a solid 1.2 mm backing.
- **New check:** `src/w_pair_verify.py` measures every layer. Any wall under 1.1 mm, or a tray cavity that isn't fully enclosed, now fails.

The originals are kept here for the record only.
