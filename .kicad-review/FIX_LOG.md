# FIX_LOG: iteration 1, Fixer APPLY mode (schematic only)

Date: 2026-11-17. Fixes applied in order: P-003, P-004, P-001, P-005, P-006, P-007, P-008, P-009, P-010. P-002 was not touched (it is gated). The PCB file was not touched and DRC was not run. The `.kicad_pcb` already showed as modified at session start; that change is not from this run.
Lock check: `hardware/EEG_Kicad_Project/~EEG_Kicad_Project.kicad_sch.lck` was absent before every fix and again at the end. Only the PCB `.lck` was present.
Baseline netlist: `/tmp/claude-1000/-home-andrzej-Documents-Repos-EEG-/2322c6a4-79fd-4009-8cf0-42fae3306225/scratchpad/base.net`. Each fix also has its own netlist in the same folder, named `p0xx.net`.

## Global renumbering (deviation from the plan, as the rules allow)
- The planned power-symbol numbers #PWR057 to #PWR065 are already taken across the sheets: #PWR057, #PWR058 and #PWR065 are on analog_in, and the existing numbers run up to #PWR0103 on stm32. They were renumbered to the next free numbers, in plan order:
  - #PWR057 → #PWR0104 (P-001)
  - #PWR058 → #PWR0105, #PWR059 → #PWR0106, #PWR060 → #PWR0107, #PWR061 → #PWR0108 (P-006)
  - #PWR062 → #PWR0109, #PWR063 → #PWR0110 (P-007)
  - #PWR064 → #PWR0111, #PWR065 → #PWR0112 (P-010)
- C50 to C54 and R21 to R24 were free and are used as planned.
- Final check: no duplicate reference in the netlist, and no `(reference "#PWR…")` is used twice.

## P-003: APPLIED
- Snapshot: `.kicad-review/snapshots/P-003/power.kicad_sch`
- Calls:
  - `delete_schematic_component` on power.kicad_sch, refs R3, R4, R5 and R6, with deleteAttachedLabels=false. Each returned "Successfully removed".
  - `delete_schematic_wire`, 9 calls, each returned "Deleted wire":
    - (217.17,110.49)→(217.17,111.76)
    - (217.17,120.65)→(217.17,119.38)
    - (217.17,121.92)→(217.17,123.19)
    - (217.17,130.81)→(217.17,132.08)
    - (217.17,132.08)→(224.79,132.08)
    - (76.2,121.92)→(76.2,120.65)
    - (76.2,123.19)→(76.2,124.46)
    - (76.2,132.08)→(76.2,133.35)
    - (76.2,133.35)→(80.01,133.35)
  - `find_orphaned_wires` on power.kicad_sch returned "No orphaned wires found."
- Netlist:
  - `Net-(U4-NR)` = C24.1, U4.4. `Net-(U6-NR)` = C25.1, U6.4.
  - All other U4/U6 nets are identical to baseline except that R3/R4/R5/R6 are gone.
  - +5V/+5V_PRI and GND/GND_PRI are still separate.

## P-004: APPLIED
- Snapshot: `.kicad-review/snapshots/P-004/` (power, usb and stm32 .kicad_sch)
- Pre-check: all 3 footprint files exist in `/usr/share/kicad/footprints`.
- Calls (`set_schematic_component_property` name=Footprint; each returned "Successfully updated"):
  - L1, L2, L3 and L4 on power: `Inductor_SMD:L_0805_2012Metric`
  - J1 on usb: `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`
  - SW1 on stm32: `Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A`
- Netlist: the footprint fields are filled for all six parts, and no component is left without a footprint. Connectivity is identical to P-003.

## P-001: APPLIED
- Snapshot: `.kicad-review/snapshots/P-001/usb.kicad_sch`
- Pre-checks passed:
  - U9 pins: 1 at (218.44,43.18), 3 at (208.28,48.26), 4 at (208.28,60.96), 5 at (208.28,63.5).
  - Region x 186–198, y 44–62 is empty.
- Calls:
  1. `delete_schematic_wire` (199.39,40.64)→(218.44,40.64): Deleted
  2. `delete_schematic_wire` (199.39,48.26)→(199.39,40.64): Deleted
  3. `add_schematic_component` Device:C C50 "100n", C_0402_1005Metric, at (190.5,52.07), angle 0: added. Pins are at (190.5,48.26) and (190.5,55.88).
  4. `add_schematic_wire` [[190.5,48.26],[199.39,48.26]]: added. The start snapped to C50/1. The tool warned that the end "may be floating", because it only checks pins. The end sits on the existing junction and wire end at (199.39,48.26), and the netlist confirms it connects.
  5. `add_schematic_net_label` VDD1_ISO1, local label, snapped to C50 pin 1 at (190.5,48.26), orientation 90: OK
  6. `add_schematic_component` power:GND **#PWR0104** (renumbered from #PWR057) at (190.5,55.88): added
  7. `set_schematic_component_property` #PWR0104 Value=GND_PRI: OK (set immediately)
- Netlist:
  - `/USBC/VDD1_ISO1` = C50.1, U9.3, U9.4, U9.5
  - `+5V_PRI` = C30.1, J1 VBUS ×4, U7.2, U8.5, U9.1. U9.3, U9.4 and U9.5 are no longer on it.
  - C50.2 is on GND_PRI.
  - The +5V/+5V_PRI and GND/GND_PRI nets are still separate. Isolated GND has only U9.9 and U9.15 from U9.
  - All as planned.
- **New ERC finding, outside the netlist sanity scope:** `power_pin_not_driven` on U9 pin 3 (VDD1, Power input) at (208.28,48.26).
  - VDD1_ISO1 has no power-output pin or PWR_FLAG.
  - This is the only new ERC violation: the total went from 76 at baseline to 77.
  - I did not improvise a fix. See M-004.

## P-005: APPLIED (with one cosmetic note)
- Snapshot: `.kicad-review/snapshots/P-005/usb.kicad_sch`
- Pre-checks passed:
  - The global labels D- (201.93,54.61), D+ (205.74,54.61), USB_OTG_FS_DP (245.11,54.61) and USB_OTG_FS_DM (250.19,54.61) are at their planned positions.
  - Stubs 0ba7d700, ffd8164b, af7d0286 and 25eda688 end at y=54.61.
  - No resistor body crosses x=199.39 or x=240.03.
- Calls:
  - `move_schematic_net_label` ×4 (global_label) to y=46.99, at x = 201.93, 205.74, 245.11 and 250.19: all "Moved"
  - `add_schematic_component` Device:R, value "24", R_0402_1005Metric_Pad0.72x0.64mm_HandSolder, angle 0, all added:
    - R21 at (201.93,50.8)
    - R22 at (205.74,50.8)
    - R23 at (245.11,50.8)
    - R24 at (250.19,50.8)
  - `set_schematic_component_property` Reference with angle=90, hide=false, at x = 203.835, 207.645, 247.015 and 252.095 (y=50.8): OK
  - `set_schematic_component_property` Value=24, hide=true, on R21 to R24: OK
  - `set_schematic_component_property` Tolerance=1% on R21 to R24: added
  - `add_schematic_text` "R21-R24: 24R 1% 0402, ADuM3160 full-speed series termination (UD+/UD-, DD+/DD-). Place close to U9." at (200.66,120.65): added
- Netlist (all as planned):
  - `D-` = J1.A7, J1.B7, R21.1, U8.3
  - `D+` = J1.A6, J1.B6, R22.1, U8.1
  - `Net-(U9-UD-)` = R21.2, U9.6
  - `Net-(U9-UD+)` = R22.2, U9.7
  - `USB_OTG_FS_DP` = R23.1, U1.45 (PA12)
  - `Net-(U9-DD+)` = R23.2, U9.10
  - `USB_OTG_FS_DM` = R24.1, U1.44 (PA11)
  - `Net-(U9-DD-)` = R24.2, U9.11
- **Cosmetic note:**
  - `find_wires_crossing_symbols` on usb reports that the existing VDD1 wire 0fe28947 (199.39,48.26)→(208.28,48.26) crosses the bodies of R21 and R22.
  - There is no electrical connection, because the R pin endpoints are at y=46.99 and y=54.61, and the netlist is correct.
  - The plan's pre-check did not cover this crossing. See M-005.

## P-006: APPLIED
- Snapshot: `.kicad-review/snapshots/P-006/usb.kicad_sch`
- Pre-check: region x 200–240, y 88–122 is empty apart from the P-005 note.
- Calls:
  - `add_schematic_component` Device:C C51 "100n", C_0402, at (209.55,100.33): added
  - `add_schematic_component` power:+5V **#PWR0105** at (209.55,96.52), then Value=+5V_PRI immediately: OK
  - `add_schematic_component` power:GND **#PWR0106** at (209.55,104.14), then Value=GND_PRI immediately: OK
  - `add_schematic_component` Device:C C52 "100n", C_0402, at (232.41,100.33): added
  - `add_schematic_component` power:+3V3 **#PWR0107** at (232.41,96.52): added
  - `add_schematic_component` power:GND **#PWR0108** at (232.41,104.14). Value left as GND (isolated side): added
  - `add_schematic_text` "C50 (VDD1), C51 (VBUS1), C52 (VBUS2/VDD2): ADuM3160 bypass - place <=10 mm from U9" at (200.66,115.57): added
- Netlist: C51.1 is on +5V_PRI, C51.2 on GND_PRI, C52.1 on +3V3 and C52.2 on GND. The PRI and isolated nets are still separate.

## P-007: APPLIED
- Snapshot: `.kicad-review/snapshots/P-007/power.kicad_sch`
- Pre-check: region x 16–31, y 158–182 is empty.
- Calls:
  - `add_schematic_component` Device:C C53 "4.7u", C_0805_2012Metric, at (24.13,170.18): added
  - `add_schematic_component` power:+5V **#PWR0109** at (24.13,166.37), then Value=+5V_PRI immediately: OK
  - `add_schematic_component` power:GND **#PWR0110** at (24.13,173.99), then Value=GND_PRI immediately: OK
  - `set_schematic_component_property` C53 Dielectric=X5R: added
  - `set_schematic_component_property` C53 Voltage=10V: added
- Netlist:
  - `+5V_PRI` = C30.1, C51.1, C53.1, J1.A4, J1.A9, J1.B4, J1.B9, U7.2, U8.5, U9.1
  - C53.2 is on GND_PRI.
  - `+5V` = C10.1, C28.1, L1.1, U5.1, U5.3, U7.4, which is unchanged.
  - Total VBUS capacitance is 4.9 µF.

## P-008: APPLIED
- Snapshot: `.kicad-review/snapshots/P-008/stm32.kicad_sch`
- Pre-check: region x 200–285, y 22–42 is empty. The sheet is A4.
- Call: `add_schematic_text` on stm32 at (205.74,27.94), fontSize 1.27, bold=true, 4 lines (stored with `\n`): added. Text:
  "WARNING: J2/J3 are on the isolated (patient) side. / Connecting a mains-powered PC/debugger bypasses / the USB isolation barrier. Use only with no electrodes / on a person, or via a USB isolator."
- The longest line should end at about x≈275, inside the border at x≈285. This is an estimate and was not checked visually. An SVG export is at `/tmp/claude-1000/-home-andrzej-Documents-Repos-EEG-/2322c6a4-79fd-4009-8cf0-42fae3306225/scratchpad/svg/EEG_Kicad_Project-STM32.svg`.
- Netlist connectivity is unchanged.

## P-009: APPLIED
- Snapshot: `.kicad-review/snapshots/P-009/stm32.kicad_sch`
- Pre-check: the Y1 footprint is `Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm`.
- Calls (`set_schematic_component_property`; each returned "added"/"updated"):
  - Y1: CL=12pF, ESR=<=60R, C0=<=3pF, Package=3225
  - C48: Value="15p C0G"
  - C49: Value="15p C0G"
- Netlist: Y1 carries the fields CL, ESR, C0 and Package. C48 and C49 have value "15p C0G". Connectivity is unchanged.

## P-010: APPLIED
- Snapshot: `.kicad-review/snapshots/P-010/stm32.kicad_sch`
- Pre-check: region x 95–110, y 35–60 is empty.
- Calls:
  - `add_schematic_component` Device:C C54 "4.7u", C_0805_2012Metric, at (100.33,48.26): added
  - `add_schematic_component` power:+3V3 **#PWR0111** at (100.33,44.45): added
  - `add_schematic_component` power:GND **#PWR0112** at (100.33,52.07): added
  - `set_schematic_component_property` C54 Dielectric=X5R: added
- Netlist: C54.1 is on +3V3 and C54.2 on GND.

## Final quick sanity (not a verification verdict)
- +5V and +5V_PRI are separate nets, and so are GND and GND_PRI.
- There are no duplicate references, and every component has a footprint.
- kicad-cli ERC found 77 violations, against 76 at baseline: 54 pin_not_connected, 19 pin_not_driven, 2 global_label_dangling, 1 power_pin_not_driven and 1 multiple_net_names. The one new violation is U9 VDD1 power_pin_not_driven (see M-004). The report is at `/tmp/claude-1000/-home-andrzej-Documents-Repos-EEG-/2322c6a4-79fd-4009-8cf0-42fae3306225/scratchpad/erc_final.rpt`.
- Modified files: `hardware/EEG_Kicad_Project/power.kicad_sch`, `stm32.kicad_sch` and `usb.kicad_sch`.
- An untracked `docs/datasheets/TRN3.pdf` exists (user-supplied for M-001).
- The planned M-002 junction leftovers remain.

## Iteration 2

Pre-checks: the schematic lock `hardware/EEG_Kicad_Project/~EEG_Kicad_Project.kicad_sch.lck` was absent before every item. Only the PCB lock exists, and the PCB was not touched. The baseline for the sanity diffs was `.kicad-review/analysis/iter-1/netlist.xml`, compared by a semantic comparator (components with value and footprint, and net membership sets) at `/tmp/claude-1000/-home-andrzej-Documents-Repos-EEG-/2322c6a4-79fd-4009-8cf0-42fae3306225/scratchpad/i2/cmp.py`. A raw diff is meaningless here because the baseline is XML and kicad-cli now writes s-expressions.

### I2-1 (M-004 / R-001): APPLIED (with deviation in placement)
- Snapshot: `.kicad-review/snapshots/I2-1/usb.kicad_sch`
- Next free #FLG across all sheets: #FLG01–#FLG06 are in use, so the new flag is **#FLG07**.
- Calls:
  1. `add_schematic_component` power:PWR_FLAG, ref #FLG07, value PWR_FLAG, at (195.58,48.26), angle 0: added.
     - **First attempt failed electrically.** ERC went to 78: #FLG07 pin_not_connected, and U9.3 power_pin_not_driven was still there.
     - Cause: a symbol pin sitting in the middle of a wire segment does not connect in KiCad.
     - The tool also put the Value field at (195.58,52.07), on top of C50.
  2. `move_schematic_component` #FLG07 to (199.39,63.5), preserveWires=false: Moved.
     - (199.39,63.5) is the existing corner/endpoint of the column wire (199.39,63.5)→(199.39,60.96) and the U9.5 wire (208.28,63.5)→(199.39,63.5).
  3. `rotate_schematic_component` #FLG07 angle=180 (flag points down into the empty space below the column): Rotated.
  4. `set_schematic_property_position` #FLG07 Value at (199.39,67.31): OK.
  5. `set_schematic_property_position` #FLG07 Reference at (199.39,61.595), visible=false: OK.
- Side effect (benign): the MCP added a junction at (199.39,63.5). That point now joins 2 wire ends and the flag pin, so the junction is valid.
- Deviations from the suggested placement:
  - The flag is not at C50 pin 1 (190.5,48.26), because there it would collide with the vertical VDD1_ISO1 label text.
  - It is not on the middle of the C50 wire either, because a pin there does not connect.
  - It sits on the same net at the bottom corner of the x=199.39 column.
- Sanity:
  - Netlist: 101 components, 119 nets, identical to iter-1. Power symbols and flags do not appear in the netlist.
  - VDD1_ISO1 = C50.1, U9.3, U9.4, U9.5.
  - ERC: 77 → **76**. power_pin_not_driven is gone.
- Render: "PWR_FLAG" text sits at about x 195–204, y 67.3, clear of the C50 GND_PRI text and of U9.

### I2-2 (M-005 / N-001): APPLIED (label on a short stub)
- Snapshot: `.kicad-review/snapshots/I2-2/usb.kicad_sch`
- Calls:
  1. `delete_schematic_wire` (199.39,48.26)→(208.28,48.26), uuid 0fe28947-355a-4f61-a84d-8edafb2342ab: Deleted.
     - This was the only destructive action, and it was approved.
     - The tool also removed the now-redundant junction at (199.39,48.26). That point is now a plain 2-wire corner: the C50 wire (190.5,48.26)→(199.39,48.26) meets column wire a1ec0623 (199.39,60.96)→(199.39,48.26). No junction is needed, and the corner is connected (see netlist).
  2. `add_schematic_wire` [[208.28,48.26],[208.28,40.64]]: added.
     - The start snapped to U9/3.
     - The tool gave its usual "end may be floating" warning, because it only checks pins. The end is terminated by the label in the next call.
     - Cosmetic: the start was written as 48.260000000000005. Connectivity is fine, and KiCad normalises the value on save.
  3. `add_schematic_net_label` VDD1_ISO1, local label, at (208.28,40.64), orientation 90: OK.
- Deviation: I used a stub instead of a label directly on pin 3.
  - A label at pin 3 would point left by default. Its text would run x≈199–208 at y≈47–48, right over the R21/R22 bodies, pins and D± labels.
  - The vertical stub at x=208.28 runs up to y=40.64, which is 1.27 mm clear of the R22 body and the D+ label edge (≈207.0). The label text then runs upward from y=40.64 to about y=31, above the D+ label, overlapping nothing.
- Sanity:
  - Netlist identical to iter-1, and VDD1_ISO1 = {C50.1, U9.3, U9.4, U9.5}.
  - ERC 76.
  - `find_wires_crossing_symbols` on usb returns **0** (it was 2).

### I2-3 (N-002): APPLIED
- Snapshot: `.kicad-review/snapshots/I2-3/` (usb, power, stm32)
- Sheet convention, taken from the existing symbols (e.g. #PWR046 +5V Value at y−5.08, #PWR047 and the other GND Values at y+5.08): +rail Value at y_origin − 5.08, GND Value at y_origin + 5.08, same x, angle 0. Value texts were not changed.
- `batch_set_schematic_property_positions` on usb.kicad_sch (5 applied, 0 failed):

  | Symbol | Rail | Origin y | New Value y |
  |---|---|---|---|
  | #PWR0104 | GND | 55.88 | 60.96 |
  | #PWR0105 | +5V | 96.52 | 91.44 |
  | #PWR0106 | GND | 104.14 | 109.22 |
  | #PWR0107 | +3V3 | 96.52 | 91.44 |
  | #PWR0108 | GND | 104.14 | 109.22 |

- `batch_set_schematic_property_positions` on power.kicad_sch (2 applied, 0 failed):

  | Symbol | New Value position |
  |---|---|
  | #PWR0109 | (24.13, 161.29) |
  | #PWR0110 | (24.13, 179.07) |

- `batch_set_schematic_property_positions` on stm32.kicad_sch (2 applied, 0 failed):

  | Symbol | New Value position |
  |---|---|
  | #PWR0111 | (100.33, 39.37) |
  | #PWR0112 | (100.33, 57.15) |

- Sanity: netlist identical to iter-1, ERC 76.
- Renders show no text left on the cap bodies, at C50/C51/C52 (usb), C53 (power) and C54 (stm32).

### I2-4 (N-003): APPLIED (deviation in method)
- Snapshot: `.kicad-review/snapshots/I2-4/usb.kicad_sch`
- No MCP tool can edit or delete schematic text. `delete_graphic` is PCB-only, and only `list_schematic_texts`/`add_schematic_text` exist.
- Instead of delete+re-add, I edited the two `(text …)` items in place in usb.kicad_sch with a scripted exact-string replace (each match asserted unique). This is less destructive than delete+re-add, and the UUIDs are kept:
  - uuid 2f71bcae… at (200.66,115.57): `C50 (VDD1), C51 (VBUS1), C52 (VBUS2/VDD2):\nADuM3160 bypass - place <=10 mm from U9`. Position unchanged.
  - uuid 29e96914… : `R21-R24: 24R 1% 0402, ADuM3160 full-speed series termination\n(UD+/UD-, DD+/DD-). Place close to U9.` Moved from (200.66,120.65) to **(200.66,123.19)**.
- Why the second note moved: both texts are justified "left bottom", so the extra line grows upward. Without the move, the two notes would sit too close.
- Wording is unchanged, and so are font, size and justification.
- Sanity:
  - The render shows the longest line ending at about x≈265 mm, inside the frame (≈285), with no overlap. The GND_PRI/GND values at y 109.22 are about 2.5 mm above.
  - Netlist identical to iter-1, ERC 76.

### Final
- kicad-cli ERC: **76 violations** (target met): 54 pin_not_connected, 19 pin_not_driven, 2 global_label_dangling, 1 multiple_net_names. power_pin_not_driven is 0.
- Report: `/tmp/claude-1000/-home-andrzej-Documents-Repos-EEG-/2322c6a4-79fd-4009-8cf0-42fae3306225/scratchpad/i2/erc_final.rpt`
- Final netlist: `/tmp/claude-1000/-home-andrzej-Documents-Repos-EEG-/2322c6a4-79fd-4009-8cf0-42fae3306225/scratchpad/i2/net_i2-4.xml`
  - Same 101 components and 119 nets as iter-1.
  - No value, footprint or net changes.
  - /USBC/VDD1_ISO1 = C50.1, U9.3, U9.4, U9.5.
- PCB was not touched and no DRC was run. Its "M" status predates this iteration.
- Pre-existing user note "Not UD+ UD- TO Isolator instead of D+ D-?" at (205.74,26.416) on usb was left untouched. It sits above the area I changed and does not overlap anything.
- Optional tidy-up: the VDD1 stub start is stored as `(xy 208.28 48.260000000000005)`; opening and saving usb.kicad_sch in eeschema normalises it.
- Applied: 4 (I2-1..I2-4). Blocked: 0. Manual actions added: none.
