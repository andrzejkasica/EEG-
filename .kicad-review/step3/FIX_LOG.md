# FIX_LOG: Step 3 round 2, iteration 1 (APPLY)

Sheet: `/home/andrzej/Documents/Repos/EEG-/hardware/EEG_Kicad_Project/analog_in.kicad_sch` (SCH).
Scratch folder: `/tmp/claude-1000/-home-andrzej-Documents-Repos-EEG-/2322c6a4-79fd-4009-8cf0-42fae3306225/scratchpad/s3apply/`.

**Check method.** `check.sh <tag>` runs `kicad-cli sch export netlist --format kicadxml` and `kicad-cli sch erc --format json --units mm` on the root `EEG_Kicad_Project.kicad_sch`. `diff.py` then compares the per-net node sets, the comp value/footprint/properties and the ERC items (type, description, items) against the previous step.

**Baseline before P-S3-002:** ERC 35; SRB1_F 10 nodes; CHn 3 nodes each; BIASOUT 4; BIASINV 3; GND 76; 125 comps. This matches the plan.

**Lock.** No `~*.kicad_sch.lck` existed before any fix. Only the expected PCB lock was present. The PCB was not touched and DRC was not run.

**Pre-existing overlaps.** `find_overlapping_elements` on the P-S3-002 snapshot already reported R16↔#PWR089, R17↔#PWR090 and R18↔#PWR091. These were not introduced by this round, and the same 3 appear after every fix.

## P-S3-002: APPLIED
- **Snapshot:** `.kicad-review/step3/snapshots/P-S3-002/analog_in.kicad_sch`
- **Pre-checks:** lock absent. `grep -c '"Value" "1.5n C0G"'` = 1, and it is C63 at (236.22, 27.94, 90). OK.
- **Tool call:** `mcp__kicad__edit_schematic_component` {schematicPath: SCH, reference: "C63", value: "10n C0G"} → "Successfully updated C63: value=10n C0G".
- **Deviations:** none.
- **Netlist and ERC:** no net changes. C63 changed "1.5n C0G" → "10n C0G" and keeps footprint Capacitor_SMD:C_0603_1608Metric. BIASINV = {C63.1, R34.1, U3.61}; BIASOUT = {C63.2, R34.2, R35.2, U3.63}. ERC 35, with an identical item set. Files: `s3apply/P-S3-002.xml`, `s3apply/P-S3-002_erc.json`.
- **Text overlaps (render x 225–250, y 20–40):** the C63 Value "10n C0G" is longer than before. It now sits between the C63 plates and R34's BIASINV label row, and its bottom almost touches the top of the R34-row "BIASINV" label at (232.41, 35.56). It does not hit the C63 body.

## P-S3-003: APPLIED
- **Snapshot:** `.kicad-review/step3/snapshots/P-S3-003/analog_in.kicad_sch`
- **Pre-checks:**
  - Lock absent.
  - `get_schematic_pin_locations U3`: pins 1/3/5/7/9/11/13/15 are at x 171.45, angle 180, at the planned y values.
  - `list_schematic_labels`: no label at those 8 points. OK.
- **Step 1 (⚠ approved destructive):** ran the plan's script verbatim with `python3 -I` from the repo root. Output: "removed 8, n0 = 16 now 8". All asserts passed. The other 8 NCs are untouched.
- **Step 2:** 8× `mcp__kicad__add_schematic_net_label` {schematicPath: SCH, netName: "SRB1_F", componentRef: "U3", pinNumber: 15/13/11/9/7/5/3/1, labelType: "label"}.
  - Every response had `snapped_to_pin` U3/<pin> and orientation 180.
  - actual_position: (171.45, 49.53), (171.45, 57.150000000000006), (171.45, 64.77000000000001), (171.45, 72.39), (171.45, 80.01), (171.45, 87.63000000000001), (171.45, 95.25), (171.45, 102.87). All match the table within 1e-6.
- **Deviations:** none.
- **Netlist and ERC:**
  - /ANALOG_IN/SRB1_F grew from 10 to 18 nodes: C55–C62.2, R33.2, U3.17, U3.1/3/5/7/9/11/13/15. This matches the plan exactly.
  - The only other change: the 8 single-pin `unconnected-(U3-INxN-Padn)` nets disappeared. That is how kicad-cli exports the previously NC pins, so it is an expected consequence, not a real net change.
  - ERC 35, with an identical item set.
  - `list_floating_labels`: none. `find_overlapping_elements`: only the 3 pre-existing entries.
- **Text overlaps (render x 150–180, y 43–106):** none. Each SRB1_F label sits about 1 mm below the CHn label above it; tight, but the glyphs do not touch. The labels are on the correct pins.

## P-S3-004: APPLIED
- **Snapshot:** `.kicad-review/step3/snapshots/P-S3-004/analog_in.kicad_sch`
- **Pre-checks:**
  - Lock absent.
  - The highest refs across all sheets are C63 and #PWR0115.
  - `get_elements_in_region` x 100–162, y 25–80: 0 symbols, 0 wires, 0 labels. OK.
- **Step 1:** `mcp__kicad__batch_add_components` {schematicPath: SCH, auto_position_fields: true, components: C64..C72}. Each entry was Device:C, "470p C0G", Capacitor_SMD:C_0402_1005Metric, rotation 0, at the planned positions. Result: "Added 9 component(s), 0 error(s)."
- **Step 2:** `get_schematic_pin_locations` gave:
  - C64: pin 1 at (106.68, 36.83), pin 2 at (106.68, 44.45)
  - C72: pin 1 at (137.16, 64.77), pin 2 at (137.16, 72.39)

  This matches the plan; the pins are not inverted.
- **Step 3:** 9× `mcp__kicad__add_schematic_net_label` {componentRef C64..C72, pinNumber "1", netName CH1..CH8 / SRB1_F, labelType "label"}. All have `snapped_to_pin`, orientation 90, and are at (x, y−3.81) as expected.
- **Step 4:** 9× `mcp__kicad__add_schematic_component` {symbol "power:GND", reference #PWR0116..#PWR0124, value "GND", angle 0, position on pin 2}. All succeeded.
- **Step 5:** ran the plan's DNP script verbatim with `python3 -I`. Output: "dnp set on 9". All asserts passed.
- **Deviations:** none.
- **Netlist and ERC:**
  - CH1..CH8 each gained exactly C64.1..C71.1, going from 3 to 4 nodes.
  - SRB1_F went from 18 to 19 (+C72.1).
  - GND went from 76 to 85 (+C64.2..C72.2).
  - 9 new comps, each "470p C0G", C_0402_1005Metric, with the `dnp` property in the netlist.
  - No other changes. ERC 35, with an identical item set.
  - `list_floating_labels`: none. `find_wires_crossing_symbols`: 0. `find_overlapping_elements`: only the 3 pre-existing entries.
  - KiCad draws the DNP crosses on C64–C72.
- **Text overlaps (render x 98–165, y 25–80), for the user to tidy (no field moves made, per user instruction):**
  1. **#PWR0116–#PWR0124:** each GND symbol's Value text "GND" is placed 3.81 mm above the symbol, at the cap centre (for example #PWR0116 Value at (106.68, 40.64)). It sits right on top of the C64–C72 bodies.
  2. **C64–C72 Reference fields:** at (x−2.54, y), angle 0. They are illegible in the render, buried under the plates, the "GND" text and the DNP cross.
  3. **C64–C67 and C69–C71 Value "470p C0G":** at (x+2.54, y). Each runs into the next cap 10.16 mm to the right, so only "470p" is visible.
  4. **C68 and C72 Values:** these have no right-hand neighbour and are clear. C68's text ends about x 160, before U3's left labels at about x 163.8.

## P-S3-005: APPLIED
- **Snapshot:** `.kicad-review/step3/snapshots/P-S3-005/analog_in.kicad_sch`
- **Pre-checks:** lock absent. P-S3-004 is applied (C72 exists). `grep -c '"LCSC"'` = 0, and MPN = 0, Tolerance = 0. OK.
- **Tool call:** `mcp__kicad__batch_edit_schematic_components` {schematicPath: SCH, components: {...}}. The properties were exactly as in the plan table, for U10, U11, U12, J4, R25–R35, C55–C63 and C64–C72. Result: "Updated 33, 0 error(s)."
- **Deviation (plan arithmetic):** the plan says "That is 34 refs" and expects LCSC/MPN count == 34. Its own list adds up to 33 refs: 3 TVS + J4 + 9×4.99k + R34 + R35 + 8×4.7n + C63 + 9×470p. The plan's Tolerance target of 29 is consistent with 33 total (33 − 3 U − J4). Results:
  - LCSC 33, MPN 33, Tolerance 29.
  - No ref from the list is missing, and no per-ref errors.

  I treated this as a typo in the plan, not a failure. The expected netlist result ("no connectivity change") holds.
- **Verification:**
  - All 95 new fields are hidden: a script found 0 LCSC/MPN/Tolerance properties without `(hide yes)`.
  - Spot-checks:
    - R34 has LCSC C26083, MPN 0402WGF1004TCE, Tolerance 1%.
    - C63 has LCSC C432938, MPN CGA3E1C0G2A103JT0Y0E, Tolerance 5%.
  - The render of x 20–165, y 20–135 shows no new visible text.
- **Netlist and ERC:** no net changes. Only the comp property lists gained LCSC/MPN(/Tolerance). ERC 35.
- **Text overlaps:** none new. The render does show the already-tracked C55–C62 Reference text sitting on the plates (M-S3-006 / S3-007) and the P-S3-004 items above.
- **Note for later:** older Step 1/2 parts on this sheet (C31–C47, R9–R18, U3) still have no LCSC/MPN. They were outside this fix's scope and were not touched.

## P-S3-007: NOT APPLIED (not approved; the user tidies this by hand, M-S3-006)

## P-S3-001: APPLIED
- **Snapshot:** `.kicad-review/step3/snapshots/P-S3-001/analog_in.kicad_sch`
- **Pre-checks:** lock absent. `grep -c "(text "` = 0. `get_elements_in_region` x 15–175, y 165–198 is empty. The text says "INxN are also tied to SRB1_F" and never "INxN NC". OK.
- **Tool call:** `mcp__kicad__add_schematic_text` {schematicPath: SCH, position: [20.32, 170.18], fontSize: 1.27, justify: "left", text: the 6 planned lines joined with "\n"} → success. The file stores a single `(text "...\n...")` item with KiCad's `\n` escapes, uuid bf2acd94-77c9-487f-aa7c-11c01e34a909. The render shows 6 lines, so the one-line fallback was not needed.
- **Deviations:** none in the actions.
- **Netlist and ERC:** no changes. ERC 35, with an item set identical to the baseline.
- **Text overlap (render x 10–200, y 158–200), for the user to tidy:**
  - **Cause:** the tool writes `(justify left bottom)`. KiCad anchors multi-line bottom-justified text at the last line, so the block grows upward. It occupies about y 159–171 instead of the planned 170–185.
  - **Effect:** lines 1–2 ("FW REQUIRED…" and "MISC1=0x20…") overprint the decoupling row's −2V5 and GND power-symbol value texts, at about y 160–162 across x 20–125.
  - **Suggested fix:** in Eeschema, move the text down about 13 mm, so the anchor is at (20.32, 182.88) and the block spans about y 171–184. Alternatively, change its vertical justify to top.
  - Nothing else overlaps. The right end is at about x 133, well clear of the title block.

## Final
- **ERC:** 35, with an item set identical to the baseline.
- **Final netlist:** `/tmp/claude-1000/-home-andrzej-Documents-Repos-EEG-/2322c6a4-79fd-4009-8cf0-42fae3306225/scratchpad/s3apply/P-S3-001.xml`
- **Final ERC:** `/tmp/claude-1000/-home-andrzej-Documents-Repos-EEG-/2322c6a4-79fd-4009-8cf0-42fae3306225/scratchpad/s3apply/P-S3-001_erc.json`
- **Final state:**
  - SRB1_F 19 nodes; CH1..CH8 4 nodes each; BIASOUT 4; BIASINV 3; GND 85.
  - 134 comps (125 + C64–C72 DNP).
- **Files modified:** only `analog_in.kicad_sch`. The PCB was untouched; its pre-existing "M" status dates from before this run.
- **Helper scripts:** `s3apply/check.sh`, `s3apply/summ.py`, `s3apply/diff.py`.
- Applied: 5 (P-S3-002, P-S3-003, P-S3-004, P-S3-005, P-S3-001). Blocked: 0. Not applied, by decision: P-S3-007.

## Post-tidy check and P-S3-SWD (2026-11-17)
- The user did M-S3-006 and M-S3-002 in Eeschema: tidied the overlaps, saved and closed. No schematic lock remained.
- **Check against the iter-1 verified state:** netlist node sets identical (126 nets, 134 comps). Formatting noise gone (0 float-noise coordinates, 0 two-space lines).
- **ERC went 35 → 37.** There were 2 new `same_local_global_label` warnings on /STM32/. The tidy had turned the SWDIO/SWCLK labels at U1 (181.61, 93.98 / 96.52) into global labels, while the J3 ends (261.62, 63.5 / 60.96) stayed local.
- **P-S3-SWD:** the user approved reverting them to local labels.
  - Applied by the Orchestrator. Snapshot: `.kicad-review/step3/snapshots/P-S3-SWD/stm32.kicad_sch`.
  - Calls: `delete_schematic_net_label` for SWDIO and SWCLK at the U1 positions, then `add_schematic_net_label` for local labels at the same points, orientation 0.
- **Result:** ERC 35, with the same item set as verified. The netlist is identical to iter-1, including the net names /STM32/SWDIO = {J3.3, U1.46} and /STM32/SWCLK = {J3.2, U1.49}.
