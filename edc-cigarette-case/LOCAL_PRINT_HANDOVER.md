# Local print handover: send and watch the ENDGRAIN + CUBES print from the owner's PC

> **Written 25 Nov 2026 by the cloud session that made the files.** That session could not reach the owner's PC. This file is for a **Claude session running on the PC itself**. It is self-contained: you need this file, the print file named in §1 and (optionally) the two helper scripts (`local-tools/` in the zip, `v7-65x15x88/local-tools/` in the repository).
>
> **Starter prompt for the local session** (the owner can paste this):
> *"Read LOCAL_PRINT_HANDOVER.md in this folder from top to bottom and carry it out: check the print file, send ENDGRAIN + CUBES without initials to my Bambu Lab A1, watch the print and tell me if anything needs me. Ask me before anything the file says needs my OK."*

---

## 0. One-minute summary

| Item | Value |
|---|---|
| **The owner's instruction** | "Use my PC to send to print ENDGRAIN + CUBES without the initials, check on prints and update me if needed", then: "run the print yourself, control everything, monitor everything." |
| **Printer** | Bambu Lab **A1** with **AMS lite**, 0.4 mm nozzle, **textured PEI plate**. |
| **File to print** | `Rollie_Book_wood_Endgrain_Cubes_A1_no_initials.3mf` (a Bambu Studio project, v10.6). |
| **What it prints** | Two rollie cases, four parts, **one after another** ("by object"): ENDGRAIN lid, ENDGRAIN tray, CUBES lid, CUBES tray. |
| **Filament** | Bambu PLA Wood. AMS slot **1 Oak**, slot **2 Teak**, slot **3 not used** (the owner ran out of Cherry), slot **4 Walnut**. |
| **Time** | About **5 h 21 m** plus about 5 min of heating and levelling. Estimated, not yet confirmed by the real Bambu slicer (§5 does that). |
| **Colour changes** | 19, all in the first 0.8 mm of each lid (plus one at the start of each tray). No pauses, no supports, no brim. |
| **Your job** | 1. Check the file. 2. Get the owner's go-ahead on the physical state of the printer. 3. Send the print. 4. Watch it. 5. Tell the owner only what they need. |

**What is not known yet (be honest about these with the owner):**
- Nobody has opened this v10.6 file in the real Bambu Studio. The cloud session checked it with an emulation of Bambu's file loader and a different slicer (PrusaSlicer, set up like the A1). Earlier files built the same way opened and printed fine.
- Whether you can press buttons in Bambu Studio yourself depends on your tools (§6). If you can't control the screen, the owner has to press **Print** once.
- Whether the printer answers status requests over the local network depends on its settings (§8.3).

---

## 1. The job in detail

**Where the file is.** Use whichever the owner gave you:
- **Zip from the cloud session:** `Rollie_Book_wood_v10.6.zip` → `2_without_initials/Rollie_Book_wood_Endgrain_Cubes_A1_no_initials.3mf`. This handover is in the zip's top folder.
- **Git:** repository `grishatg/3D-PRINTS`, branch `claude/hopeful-thompson-ysz39k`, path `edc-cigarette-case/v7-65x15x88/wood-3mf/Rollie_Book_wood_Endgrain_Cubes_A1_no_initials.3mf`.

**Check you have the right file before anything else:**

| Check | Expected |
|---|---|
| Size | 4,475,967 bytes |
| SHA-256 | `2a1f1daad7217b7d8c45ca75556608c82a88921b63b49c12b88e879560889467` |

PowerShell:
```powershell
Get-FileHash -Algorithm SHA256 .\Rollie_Book_wood_Endgrain_Cubes_A1_no_initials.3mf
```
macOS / Linux:
```bash
shasum -a 256 Rollie_Book_wood_Endgrain_Cubes_A1_no_initials.3mf
```
If the hash differs, stop and tell the owner. Do not print a file you can't identify.

**Do not confuse it with these:**
- `AB_Rollie_Book_wood_Endgrain_Cubes_A1.3mf` is the same pair **with** the A·B initials. The owner asked for the one **without**.
- Anything from before 25 Nov (v10.5 or older) has the old hinge with a loose sleeve, a brim and Cherry in slot 3. Don't print those.

---

## 2. Rules

**You may do these without asking:**
- Read files, open Bambu Studio, open the project, slice it, look at the preview.
- Read the printer's status and camera.
- **Pause** or **stop** a running print when §9 says so. Stopping a bad print is always allowed.

**Ask the owner first (one short question, wait for the answer):**
- **Starting the print.** The owner has asked for it, but only they can confirm the physical state (§3). Get that confirmation in your session, then send.
- Resuming after any pause you didn't cause.
- Changing anything in the project: a setting, a part's position, the plate type, the filament list.
- Installing software on the PC (for example `pip install paho-mqtt`).
- Changing anything on the printer: network mode (LAN-only, Developer Mode), firmware, calibration.

**Never:**
- Never press **Arrange** or **Auto orient**, and never move or rotate a part. The four parts are spaced so the A1 can print them one at a time without the toolhead hitting a finished part. The gap is 74 mm; Bambu needs more than 72.8 mm.
- Never press **Re-calculate** in the purge (flushing volumes) dialog, and leave the multiplier at 1. The purge table is tuned for these four woods.
- Never update firmware or Bambu Studio in the middle of this job.
- Never write the printer's serial number, access code, IP address, or the owner's name, email or account into any file, commit or message to an outside service. Use them in memory or environment variables only.
- Never commit or push to the repository unless the owner asks.
- Never leave a paused print sitting hot for long without telling the owner. Wood PLA chars in a hot nozzle.

**If you are unsure whether something is safe: pause the print (if one is running) and ask.**

---

## 3. What the owner must confirm before you send

You can't see or touch the printer. Ask the owner to confirm these in one message. The camera (§8.2) can confirm the first two.

1. **The plate is on, clear and clean.** Textured PEI, nothing left from the last print, washed with washing-up liquid and warm water, not touched on the print surface since.
2. **Nothing is in the way** of the bed or the toolhead.
3. **Spools:** slot **1 Oak**, slot **2 Teak**, slot **4 Walnut**, all Bambu PLA Wood, dried if possible. Slot 3 can be empty.
4. **Enough filament:** at least **60 g of Walnut** (the print takes 48 g plus purge), **20 g of Oak**, **20 g of Teak**.
5. **The nozzle tip is clean** (no blob hanging from it). A dirty tip spoils the bed levelling.
6. **They are happy for it to start now** and know it runs about 5.5 hours.

Suggested wording: *"Ready to send ENDGRAIN + CUBES (no initials), about 5 h 25 m. Please confirm: plate on and clean, nothing in the way, slots 1 Oak / 2 Teak / 4 Walnut with at least 60 g of Walnut, nozzle tip clean. OK to start?"*

---

## 4. Find Bambu Studio and the printer

**Bambu Studio (usual places; check, don't assume):**

| OS | Program | Settings folder |
|---|---|---|
| Windows | `C:\Program Files\Bambu Studio\bambu-studio.exe` | `%APPDATA%\BambuStudio\` |
| macOS | `/Applications/BambuStudio.app/Contents/MacOS/BambuStudio` | `~/Library/Application Support/BambuStudio/` |
| Linux | `bambu-studio` (AppImage or Flatpak) | `~/.config/BambuStudio/` |

- If it isn't installed, ask the owner. Don't install it yourself.
- Note the version (Help → About, or the file properties). The files were checked against Bambu's loader code at versions 2.03, 2.08 and 2.09.
- The owner must be **signed in** to their Bambu account in Bambu Studio, and the A1 must show in the **Device** tab. If it doesn't, ask the owner to sign in or bind the printer. Don't try to do that for them.

**Open the project:**

Windows:
```powershell
& "C:\Program Files\Bambu Studio\bambu-studio.exe" "C:\full\path\Rollie_Book_wood_Endgrain_Cubes_A1_no_initials.3mf"
```
macOS:
```bash
open -a BambuStudio "/full/path/Rollie_Book_wood_Endgrain_Cubes_A1_no_initials.3mf"
```

**If a dialog appears on opening:**
- "Made with a newer / older version": continue and open.
- Anything about presets being modified or different: **keep the project's values**. Never choose an option that discards them or replaces them with the printer's defaults.
- Anything you don't recognise: take a screenshot and ask the owner.

**What you should see once it's open:**

| Where | Expected |
|---|---|
| Printer | Bambu Lab A1 0.4 nozzle |
| Plate type | Textured PEI Plate |
| Process | 0.12mm High Quality @BBL A1 (shown as modified) |
| Filaments | four × Bambu PLA Wood: light oak, mid-brown teak, dark red-brown (unused), dark walnut |
| Objects | four, one near each corner of the plate: ENDGRAIN cover, ENDGRAIN tray, CUBES cover, CUBES tray |
| Print sequence | By object |

If any of these is different, stop and ask the owner.

---

## 5. Cross-check with the real Bambu slicer (recommended, 5 minutes)

This is the first time the real slicer sees this file, so do this before sending. It needs no printer.

**Either in the window:** press **Slice plate**, then look at the result (below).

**Or from the command line** (Bambu's documented `--slice` and `--export-3mf` options):

Windows:
```powershell
& "C:\Program Files\Bambu Studio\bambu-studio.exe" --slice 0 --debug 2 --export-3mf "C:\full\path\sliced_check.gcode.3mf" "C:\full\path\Rollie_Book_wood_Endgrain_Cubes_A1_no_initials.3mf"
```
Then, with Python 3:
```powershell
python .\local-tools\check_bambu_slice.py "C:\full\path\sliced_check.gcode.3mf"
```
- The command-line slicer is known to fail on some builds (a GitHub issue reports no output file on one macOS build). If it produces nothing, use the window instead; it isn't a sign the file is bad.
- `check_bambu_slice.py` only reads the file. It was written from Bambu's known G-code comments but **could not be tried on real Bambu output**, so if it says a marker is missing, read the G-code yourself.

**What a good slice looks like:**

| Thing | Expected | If it's different |
|---|---|---|
| Errors | none | Stop. Tell the owner the exact message. |
| Time | about 5 h 20 m, give or take 20 min | Up to 6 h is fine. Much more: tell the owner before sending. |
| Filament | about 11 g Oak, 12 g Teak, 0 g slot 3, 48 g Walnut | Slot 3 used at all: stop, wrong file. |
| Colour changes | 19 | A few more or fewer is fine. |
| Pauses | none | Any pause: stop, wrong file. |
| Clearance warning | none | If Bambu says parts are too close for by-object printing: **don't move anything**. Close without saving, reopen, slice again. Still there: stop and tell the owner. |

**Warnings that are expected and harmless:**
- "Floating cantilever" or "long bridge" style notes on the trays. The engraved back patterns are roofed over on the fifth layer; each roof spans a groove under 1 mm wide (the ENDGRAIN squares are 4 mm).
- A note about bed adhesion or suggesting a brim on a tray. The brim was removed on purpose (the owner's choice); each part sits on the plate with its whole face.

**Look at layer 1 in the Preview** (drag the layer slider right down). It is the outside face of each part:
- ENDGRAIN lid: teak with walnut squares. CUBES lid: oak with teak and walnut diamonds. Both trays: walnut.
- Inside each square or diamond you should see **one outline and straight parallel lines**, running along the length of the part. You should **not** see four nested rings in each cell. That was the fault in the first print, and it is what this version fixes.
- If you do see nested rings on the lids, the two per-object settings weren't applied. Tell the owner before printing; the print would still work, but the faces would look like last time.

---

## 6. Send the print

Use the first route that works for you.

### Route A: you can control the screen (computer use)
1. In Bambu Studio, with the project open and sliced, press **Print plate** (top right).
2. In the send dialog check:
   - **Printer:** the owner's A1, shown as idle.
   - **Plate:** Textured PEI Plate. It must match the plate that is physically on the bed.
   - **Bed levelling: ON.** Important here: the first print showed the first layer a little high near the front and back of the bed.
   - **Flow dynamics calibration:** leave as the owner has it (Auto is fine).
   - **Timelapse:** off.
   - **Use AMS:** on.
   - **Filament mapping:** project filament 1 → the AMS slot holding **Oak**, 2 → **Teak**, 4 → **Walnut**. Filament 3 isn't used and needs no slot. Check by wood name and colour, not just slot number.
3. Take a screenshot of the dialog and keep it.
4. Only after the owner's go-ahead (§3): press **Send**.

### Route B: you can't control the screen
1. Do everything in §4 and §5 so Bambu Studio is open with the project sliced.
2. Tell the owner exactly this: *"Bambu Studio is open with the right file, sliced and checked. Please press **Print plate**, check Bed levelling is ticked and the filaments map 1 → Oak, 2 → Teak, 4 → Walnut, then press **Send**."*
3. Carry on from §7 once they say it's sent.

### Route C: Bambu Connect (only if the owner already uses it)
Bambu Connect takes a **sliced** file. Bambu's wiki documents this link form, which opens Bambu Connect with the file ready to import:
```
bambu-connect://import-file?path=<URL-encoded absolute path to sliced_check.gcode.3mf>&name=<URL-encoded name>&version=1.0.0
```
Someone still has to pick the printer and press print in Bambu Connect. Bambu's two wiki pages disagree on the parameters, so test before relying on it.

### Not without the owner's explicit OK: direct network control
Community tools can upload a file and start a print over the local network (FTPS plus MQTT). On current firmware that needs the printer in **LAN-only mode with Developer Mode** switched on at the printer's screen. That turns off the Bambu cloud features, including watching from the phone app. It is unsupported by Bambu. **Do not switch modes yourself.** If the owner wants a fully hands-off setup, explain this trade-off and let them decide.

---

## 7. Confirm the start (first 15 minutes)

After sending, in Bambu Studio's **Device** tab you should see, in order: preparing, heating (bed 65 °C, nozzle 220 °C), bed levelling, then printing.

**Send the owner one line** once it is actually laying plastic: *"Started at HH:MM. ENDGRAIN lid first. Should finish about HH:MM."*

**Watch the first layer of the first part** (ENDGRAIN lid, about the first 8 minutes of printing):
- It starts in the **front-left** area of the plate.
- Lines should lie flat and touch each other, and stay put when the nozzle passes again.
- You should see teak go down, then a colour change, then walnut squares (or the other way round).

**Stop the print now if:** plastic is not sticking, is being dragged around, or is balling up on the nozzle. A failed first layer never recovers, and stopping early wastes almost nothing.

---

## 8. Watch the print

### 8.1 Timeline

Times are from the start of printing (after heating and levelling). They are estimates; treat ±15 minutes as normal.

| Part | Where on the plate | Starts | Ends | Colour changes | Risky period |
|---|---|---|---|---|---|
| **1. ENDGRAIN lid** (teak + walnut squares) | front left | 0:00 | 0:59 | 6, all in the first 0.8 mm | first 20 min |
| **2. ENDGRAIN tray** (walnut) | front right | 0:59 | 2:35 | 1, at its start | first 10 min |
| **3. CUBES lid** (oak + teak + walnut) | back left | 2:35 | 3:45 | 11, all in the first 0.8 mm | first 30 min |
| **4. CUBES tray** (walnut) | back right | 3:45 | 5:21 | 1, at its start | first 10 min |

- **Each part's risky period is its start:** a new first layer on bare plate, plus the colour changes. Once a part is a few millimetres tall, little goes wrong.
- A colour change takes about a minute: the toolhead goes to the side, cuts, unloads, loads, purges, wipes. That is normal, not a stall.
- Between parts the toolhead travels over to the next corner. It should never touch a finished part.

### 8.2 How often, and how

| When | How often |
|---|---|
| First 15 min of the whole print | stay on it |
| First 20–30 min of each part (see table) | every 5 min |
| Rest of each part | every 20–30 min |
| Last 10 min | every 5 min |

**Ways to look, best first:**
1. **Bambu Studio → Device tab:** progress, layer, temperatures, any error banner, and the **camera** view. Screenshot it if you can control the screen.
2. **`local-tools/printer_status.py`** (read-only, §8.3) for a one-line status.
3. **Ask the owner** to glance at the Bambu Handy app if you have neither.

**What "fine" looks like:** state printing; percentage and layer going up; nozzle about 220 °C and bed about 65 °C; no error; in the camera, parts are flat on the plate with clean edges and nothing stringy around them.

### 8.3 Read-only status script

`local-tools/printer_status.py` reads the printer's status over the local network. It never sends a print, pause or stop command.

- It needs Python 3 and `paho-mqtt` (ask before installing: `pip install paho-mqtt`).
- It needs the printer's **IP address, serial number and LAN access code**. They are on the printer's screen (Settings, network / WLAN page) and in Bambu Studio's Device tab. Ask the owner to read them out, or read them from the screen. Put them in environment variables only:

```powershell
$env:BAMBU_IP="192.168.x.x"; $env:BAMBU_SERIAL="XXXXXXXXXXXXXXX"; $env:BAMBU_CODE="xxxxxxxx"
python .\local-tools\printer_status.py --watch 300
```

- **It may not work.** Community reports say the printer's local port answers with the access code, but what it allows depends on firmware and mode. If it can't connect or gets nothing, use the Device tab. Don't change printer settings to make it work.
- **It was not tested against a printer** when written.

Useful fields it prints: `state` (`RUNNING`, `PAUSE`, `FINISH`, `FAILED`, `IDLE`), percent, minutes left, layer, temperatures, `error`, `hms` (Bambu's fault codes), and what the AMS says is in each slot.

---

## 9. When something goes wrong

**Stopping** is in the Device tab (Stop), as is **Pause**. You can't fix anything physical; your choices are watch, pause, stop, and tell the owner.

| What you see | What it means | What to do |
|---|---|---|
| First layer not sticking, plastic dragged or balled up | Dirty plate or bad levelling | **Stop.** Tell the owner: wash the plate, clean the nozzle tip, send again with bed levelling on. |
| First-layer lines lie flat but with thin gaps between them | Nozzle a touch high in that area | **Don't stop.** Note where (which part, which end) and tell the owner afterwards. |
| The wrong colour is printing (first part isn't teak with walnut squares) | Filament mapping or slots wrong | **Pause.** Tell the owner at once. |
| Printer paused itself with an AMS or filament message (runout, failed to feed or retract, tangle) | Needs hands at the printer | **Tell the owner immediately**, with the exact message. Don't press resume or retry yourself. |
| A part has come loose and is moving | Lost adhesion | **Stop.** |
| The toolhead hits a finished part | Should not happen (spacing was verified) | **Stop.** Tell the owner; say which two parts. |
| A blob of plastic growing on the nozzle or toolhead | Blob of death starting | **Stop at once.** Tell the owner not to pull it off cold. |
| Loose strands or "spaghetti" in mid-air | A part failed | **Stop.** |
| Anything that looks like smoke, scorching or fire | Emergency | **Stop at once** and tell the owner to go to the printer and cut the power. |
| An error banner with an HMS code | Bambu's fault code | Read the message. Look the code up at `https://wiki.bambulab.com/en/hms/home`. Tell the owner the code, the message and what Bambu says. |
| Bambu Studio shows the printer offline | Usually just the connection | The print normally carries on. Try reconnecting. If it's still offline after 15 min, tell the owner. |
| Progress hasn't moved for 10 min and it isn't a colour change | Stalled or paused | Check for a message. If there's none, tell the owner. |
| Time left grows by more than 30 min over the plan | Slower than estimated | Not a fault. Tell the owner the new finish time. |
| One part failed but the others are fine | | Bambu Studio can skip an object on some printers (Device tab, object list). **Ask the owner** before using it. |

**After any pause:** tell the owner how long it has been paused. A nozzle sitting at 220 °C with wood PLA in it can clog within tens of minutes.

---

## 10. What to tell the owner, and when

Keep every message to one to three lines. Lead with what they need to know or do.

| When | Message |
|---|---|
| Before sending | The §3 question. |
| Printing has started | Start time, expected finish time. |
| First layer of part 1 is down | "First layer looks good" or what's wrong. |
| Each part finishes (0:59, 2:35, 3:45) | One line: "ENDGRAIN lid done, on to the tray. On schedule." Skip it if they said they don't want these. |
| Anything in §9 | At once, with the exact message and what you did. |
| Finished | "Done at HH:MM. Let the plate cool, then the parts pop off." Plus anything you noticed. |

**After the print, remind them how these cases go together now (it changed):**
- **No hinge sleeve any more.** The tray has three hinge knuckles and the lid has two.
- Drop the lid onto the tray so its two knuckles sit between the tray's three.
- Push an **88 mm length of 1.75 mm filament** through from one end as the pin. It grips in the two end knuckles.
- Magnets as before: four Ø5 × 2 mm per case, glued flush, lid marked face up, tray marked face down.

---

## 11. The other two plates (for later)

Same rules, same slots. Print the no-initials or the A·B version of each, not both.

| Plate | File (no initials) | Time | Colour changes | Walnut needed |
|---|---|---|---|---|
| RIVA + PARQUET | `Rollie_Book_wood_Riva_Parquet_A1_no_initials.3mf` | 4 h 46 m | 25 | **58 g** + 7 g purge |
| KUMIKO + DIAL | `Rollie_Book_wood_Kumiko_Dial_A1_no_initials.3mf` | 4 h 30 m | 3 | 45 g |

With A·B initials: `AB_Rollie_Book_wood_<pair>_A1.3mf`, 8 to 14 minutes longer.

**Walnut is the limit.** All three plates together take about 151 g of Walnut plus about 15 g of purge. Ask the owner how much is on the spool before starting the second plate.

---

## 12. The print in numbers (v10.6, ENDGRAIN + CUBES, no initials)

| | |
|---|---|
| Profile | Bambu's 0.12 mm High Quality for the A1, plus: 4 walls, 1.0 mm top skin, 6 bottom layers, 15 % gyroid, first layer 0.2 mm at 40 mm/s, first-layer flow 1.05, scarf seams |
| Temperatures | nozzle 220 °C, textured plate 65 °C |
| Layers | 111 (tray height 13.4 mm, lid 5.7 mm) |
| Estimated time | 5 h 13 m of printing + 9 min of purging = **5 h 21 m** |
| Filament | Oak 10.9 g, Teak 12.2 g, slot 3 0 g, Walnut 48.2 g; about 5 g more as purge |
| Colour changes | 19 |
| Supports, brim, pauses | none |
| Part spacing | 74.0 mm between every pair of parts |
| Plate use | parts span 15 to 241 mm in both directions on the 256 mm bed |

---

## 13. Why this version exists (background)

The owner printed the previous version (v10.5) of this plate overnight on 24–25 Nov and sent photos. v10.6 answers their feedback:

1. **"Put that hinge sleeve connected to the back plate so it prints in one go … the back has 3 hinges, the top 2."** The loose middle sleeve is now a third knuckle on the tray. There is no sleeve part and no sleeve plate.
2. **"Make it so the layers don't show up … the side where it touches the plate, the ones with cubes and squares."** On the lid faces every square and cube had four nested wall rings and a centre patch, clearly visible where the first layer went down slightly high. Now those faces are laid as one outline per cell plus straight lines along the case, and the first layer gets 5 % more plastic.
3. **"Why does it need a brim?"** It doesn't. The brim is gone.
4. **"I ran out of Cherry … use the other, oak wood and walnut."** The CUBES tray is now Walnut. No design uses slot 3.
5. Found on the way: the rounded edges were modelled in 0.1 mm steps, which beat against the 0.12 mm print layers and made a visible band every five layers on the hinge side. They now step evenly.

Full project history and how the files are built and checked: `HANDOVER.md` (§0a) in this folder. The owner's print guide: `v7-65x15x88/wood-3mf/README.md`. The check reports for each file: `v7-65x15x88/wood-3mf/checks/`.

---

## 14. Where the Bambu facts in this file come from

Researched on 25 Nov 2026. None of it was tried on the owner's printer. Check anything you depend on.

- Command-line slicing (`--slice`, `--export-3mf`): Bambu Studio wiki, "Command Line Usage", `https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage`. A report of the command-line slicer producing no file on one build: `https://github.com/bambulab/BambuStudio/issues/9636`.
- Bambu Connect and its import link: `https://wiki.bambulab.com/en/software/bambu-connect` and `https://wiki.bambulab.com/en/software/third-party-integration`.
- Local control, LAN-only and Developer Mode: Bambu's blog post `https://blog.bambulab.com/updates-and-third-party-integration-with-bambu-connect` and All3DP's guide `https://all3dp.com/2/bambu-lab-lan-only-mode-explained/`.
- Local status topics and message shapes (community-documented): `https://synman.github.io/bambu-printer-manager/mqtt-protocol-reference` and the forum thread `https://forum.bambulab.com/t/mqtt-for-a1/50033`.
- First layer sitting high on the textured plate, and the start-G-code offset some owners change: `https://forum.bambulab.com/t/a1-z-offset-appears-to-be-too-low/85426` and `https://forum.bambulab.com/t/z-offset-and-textured-plate/115088`. One owner there reports the offset command being overridden later in the start routine, so treat it as unproven. **Do not edit the printer's start G-code in this project without the owner asking.**
