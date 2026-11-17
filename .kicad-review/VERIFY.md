# Verify: iteration 1 (schematic only)

- **Date:** 2026-11-17. Branch `task2-schematic-gaps`.
- **What ran:** fresh checks only, nothing taken from FIX_LOG on trust. No design file was modified, no DRC was run, and the PCB was not touched.
- **Lock files:** the schematic `.lck` was absent. Only the PCB `.lck` was present.
- **Git status:** the same before and after the run, apart from the new `analysis/iter-1/`.
- **Artifacts** (`.kicad-review/analysis/iter-1/`):
  - `erc.json`
  - `netlist.xml`
  - `schematic.json`
  - `capability_mode.json`

## Counts

### ERC (kicad-cli 9.0.9, `--units mm`)

| Sheet | Type | Severity | Baseline | Now |
|---|---|---|---|---|
| /STM32/ | pin_not_connected | error | 32 | 32 |
| /ANALOG_IN/ | pin_not_connected | error | 22 | 22 |
| /ANALOG_IN/ | pin_not_driven | error | 19 | 19 |
| / | global_label_dangling (UD+/UD-) | warning | 2 | 2 |
| /POWER_SUPPLY/ | multiple_net_names | warning | 1 | 1 |
| /USBC/ | power_pin_not_driven | error | 0 | **1** |
| **Total** | | | **76** (73 errors, 3 warnings) | **77** (74 errors, 3 warnings) |

- The only new violation is the U9 pin 3 VDD1 power_pin_not_driven at (208.28, 48.26).
- The multiple_net_names item now cites #PWR017 (power:GND) and #PWR028 (power:GNDA). Baseline cited #PWR016/#PWR018. It is the same intentional GND/GNDA merge, with a different representative symbol picked, so it is not new.

### kicad-happy analyze_schematic

| Metric | Baseline | Now |
|---|---|---|
| Findings total | 106 | 106 |
| Components | 96 | 101 (+9 new parts, −4 for R3–R6) |
| Unique parts | 37 | 39 |
| Nets | 114 | 119 |
| missing_footprint | 6 (SW1, J1, L1–L4) | **0** |
| VM-001 (D± crossing, known false positive) | 2 | 0 (nets now split by R21/R22) |
| UC-004 VBUS cap | 1 (0.1 µF) | **0**; usb_compliance vbus_capacitance pass, 4.9 µF |
| usb_compliance dp/dm_series_resistor | info | **pass** |
| DO-DET +3V3 coverage | 11 caps, 3.8 µF, largest 1 µF | 13 caps, 8.6 µF, largest **4.7 µF (C54)** |
| DO-DET / DC-DET +5V_PRI | 1 cap, 0.1 µF | 3 caps (C30, C51, C53), 4.9 µF |
| DC-DET / DO-DET VDD1_ISO1 | n/a | new rail, C50 100n |
| XL-DET / DO-DET Y1 | C48/C49 "15p", dielectric assumed X7R | "15p C0G" is parsed: 15 pF, **dielectric C0G** |
| RS-001 | 0 | **1** (VDD1_ISO1 has no declared source; same root cause as the new ERC error) |
| DO-DET "U2/U4/U6 missing caps" | 3 | 3 (known false positive, unchanged) |
| NT-001 | 54 warnings + 2 info | 54 warnings + 2 info |
| SS-001 / SJ-DET | 1 / 1 | 1 / 1 |

Y1 CL_eff is still reported as 10.5 pF against an 18 pF "frequency_default" target. The analyzer does not read Y1's new CL=12pF property; the status is "unverified". This is an analyzer limitation, not a design issue: 15 pF with 5 pF stray matches a CL of 12 pF.

### Netlist (`analysis/netlist.xml` → `analysis/iter-1/netlist.xml`)

- **Components:** 96 → 101, with 0 duplicate refs and **0 components without a footprint**.
  - Added: C50–C54, R21–R24.
  - Removed: R3–R6.
- **Value/footprint changes:** C48/C49 "15p" → "15p C0G". Footprints were added on L1–L4, J1 and SW1. Nothing else changed.
- **Net diffs:** exactly the 17 nets below. Every other net is byte-identical.
  - +3V3 (+C52.1, C54.1)
  - +5V_PRI (−U9.3/4/5, +C51.1, C53.1)
  - /USBC/VDD1_ISO1 (new: C50.1, U9.3, U9.4, U9.5)
  - D+ (−U9.7, +R22.1)
  - D- (−U9.6, +R21.1)
  - GND (−R4.2, R6.2, +C52.2, C54.2)
  - GND_PRI (+C50.2, C51.2, C53.2)
  - Net-(U4-NR) = C24.1, U4.4
  - Net-(U6-NR) = C25.1, U6.4
  - Net-(U4-OUT) and Net-(U6-OUT) only lose R3.1 and R5.1
  - New nets: Net-(U9-UD±), Net-(U9-DD±)
  - USB_OTG_FS_DP/DM (−U9.10/11, +R23.1/R24.1)
- **Isolation barrier is intact.**
  - +5V = C10, C28, L1.1, U5.1, U5.3, U7.4.
  - +5V_PRI = C30, C51, C53, J1 VBUS×4, U7.2, U8.5, U9.1.
  - GND_PRI = C30, C50, C51, C53, J1 GND/shield, R7, R8, U7.1, U8.2, U9.2, U9.8.
  - Isolated GND has only U9.9 and U9.15 from U9.
  - No node is shared between PRI and the isolated side.
- **U9 side 2 is unchanged:** pins 12, 13, 14 and 16 are on +3V3.
- **Properties:**
  - Y1 fields: CL=12pF, ESR=<=60R, C0=<=3pF, Package=3225.
  - C53: Dielectric=X5R, Voltage=10V.
  - C54: Dielectric=X5R.
  - R21–R24: Tolerance=1%.
- **J1 footprint:** the GCT USB4105 pads (A1/A4/A5/A6/A7/A9/A12, B-side equivalents, S1) cover every pin used by the symbol. A8/B8 (SBU) are unused pads, which is fine.

## Per fix

- **F-001 / P-001: PASS** (electrical), with ERC side effect R-001 below.
  - VDD1_ISO1 = C50.1, U9.3, U9.4, U9.5.
  - C50.2 is on GND_PRI.
  - U9.1 stays on +5V_PRI.
- **F-002 / P-002: OPEN.** On hold by user decision and not applied. U7 TMU3-0511 is unchanged.
- **F-003 / P-003: PASS.**
  - R3–R6 are gone from the netlist.
  - The NR nets contain only C24 (U4) and C25 (U6).
  - No orphaned wires on power.kicad_sch, and the image confirms clean NR stubs.
- **F-004 / P-004: PASS.**
  - L1–L4 have `Inductor_SMD:L_0805_2012Metric`.
  - J1 has `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`, and its pads match the symbol.
  - SW1 has `SW_Push_1P1T_XKB_TS-1187A`.
  - The analyzer's missing_footprint went from 6 to 0, and the netlist has 0 parts without a footprint.
- **F-005 / P-005: PASS** (electrical), with cosmetic issue N-001.
  - R21 sits between D- and U9.6, R22 between D+ and U9.7, R23 between PA12 and U9.10, R24 between PA11 and U9.11.
  - All are 24 Ω, 1 %, 0402. The analyzer series-R checks pass.
- **F-006 / P-006: PASS.**
  - C51 is on +5V_PRI/GND_PRI and C52 on +3V3/GND, both 100n 0402.
  - C50 is on VDD1.
  - The placement note text is present.
- **F-007 / P-007: PASS.**
  - C53 is 4.7u 0805 X5R 10 V on +5V_PRI/GND_PRI.
  - Total VBUS capacitance is 4.9 µF, under the 10 µF limit.
  - UC-004 has cleared.
- **F-008 / P-008: PASS.** The bold 4-line warning sits at (205.74, 27.94) on stm32. It is fully inside the frame (ends at x≈262 mm) and overlaps nothing.
- **F-009 / P-009: PASS.** The Y1 CL/ESR/C0/Package fields are present. C48/C49 are "15p C0G", and the analyzer now parses the dielectric as C0G.
- **F-010 / P-010: PASS.** C54 is 4.7u 0805 X5R on +3V3/GND. The analyzer now shows 4.7 µF as the largest +3V3 cap. There is a cosmetic issue, N-002.

## New findings

### R-001 [LOW] ERC regression from P-001: U9 pin 3 VDD1 power_pin_not_driven
- **Location:** usb.kicad_sch (208.28, 48.26).
- **Evidence:**
  - kicad-cli ERC shows 1 new error.
  - The analyzer's RS-001 says "VDD1_ISO1 has no declared source".
- **Classification:** expected ERC hygiene, not an electrical defect.
  - VDD1 really is sourced by the ADuM3160's internal 3.3 V regulator.
  - The symbol types the pin as Power input, and the net has no power_out pin or PWR_FLAG.
- **Fix (M-004):** add a PWR_FLAG on VDD1_ISO1 (preferred, consistent with commit 8bf5a87), or set U9 pin 3 to power_out in a local symbol copy. That brings ERC back to 76.

### N-001 [MEDIUM, readability / misleading] VDD1 wire drawn through the R21/R22 bodies
- **Location:** usb.kicad_sch, wire (199.39, 48.26)→(208.28, 48.26).
- **Evidence:**
  - `find_wires_crossing_symbols` reports R21 and R22.
  - The image shows the VDD1_ISO1 wire running straight through both resistor bodies, between the D-/D+ global labels and U9 pin 3.
  - The netlist shows no connection, because the R pins end at y=46.99 and y=54.61.
- **Risk:** a reader could take D± as tied to VDD1.
- **Fix:** re-route the VDD1 wire around R21/R22, e.g. move R21/R22 and the D± labels left of x=199 or re-route VDD1 above y=45. This is M-005.

### N-002 [LOW, cosmetic] Value text of the new power symbols sits on the capacitor bodies
- **Affected symbols:** #PWR0104–#PWR0112, on C50, C51, C52 and the R-note area (usb), C53 (power) and C54 (stm32).
- **Evidence:**
  - On C51, C53 and C54 the two values (e.g. "+5V_PRI"/"GND_PRI", "+3V3"/"GND") are printed on top of each other across the cap plates. On C50 the GND_PRI value covers the cap.
  - Root cause: the MCP placed the Value field at the wrong offset. For example, #PWR0111 is at (100.33, 44.45) but its Value is at (100.33, 48.006), inside the cap. KiCad's default puts it above the arrow (y≈40.6).
  - `find_overlapping_elements` reports C54↔#PWR0111. The symbol overlap itself is the same pin-end pattern as the baseline R16–R18 false positive, but the text overlap is real.
- **Fix:** move each Value field to the normal position (above +rail arrows, below GND symbols), or hide it, e.g. with `set_schematic_property_position`.

### N-003 [LOW, cosmetic] The two P-005/P-006 note texts on usb.kicad_sch run past the sheet frame
- **Location:** text at (200.66, 115.57) and (200.66, 120.65), A4 sheet.
- **Evidence:**
  - The "R21-R24 … Place close to U9." line ends at about x≈308 mm, past the A4 paper edge at 297 mm, so it will clip in PDF/print.
  - The "C50 … from U9" line crosses the right frame lines at about x≈285 mm.
- **Fix:** move the notes left or break them into 2–3 lines.

Not new: the D1/D2 wire crossings on stm32 are the known baseline false positive.

## Visual check notes

- **usb, U9 region (x 185–260, y 35–125):**
  - The U9 wiring matches the netlist.
  - The VDD1_ISO1 label sits on the C50 pin 1 stub, and junctions are present at the 199.39 node and the PDEN/SPU tie.
  - Issues found: N-001, N-002 and N-003.
- **power, U4/U6 NR (x 55–235, y 100–142):**
  - Clean. NR goes only to C24 (U4) and C25 (U6), with no stubs or dangling wire left.
  - `find_orphaned_wires` reports 0, and `find_overlapping_elements` reports 0.
- **power, C53 (x 10–70, y 150–190):** wired via the +5V_PRI and GND_PRI power symbols. The value-text overlap (N-002) is the only problem.
- **stm32, warning text (x 195–300, y 15–50):** legible, inside the frame, no overlap.
- **stm32, C54 (x 80–120, y 30–62):** placed next to C1/C2. Its value text overlaps (N-002).
- **MCP read-only checks:**
  - `find_orphaned_wires`: 0 on usb, power and stm32.
  - `find_wires_crossing_symbols`: usb 2 (N-001), power 0, stm32 2 (D1/D2, known false positive).

**Result: 9 PASS, 0 FAIL, 1 REGRESSION (R-001, ERC-only, from P-001; LOW). F-002 OPEN (on hold). 3 new cosmetic/readability findings: N-001 MEDIUM, N-002 LOW, N-003 LOW.**

---

# Verify: iteration 2 (schematic only)

Fresh checks by a new Verifier. No design file was modified, there was no DRC, and the PCB was not touched. Artifacts are in `.kicad-review/analysis/iter-2/`.

## ERC counts

| Sheet | Type | Baseline | Iter-1 | Iter-2 |
|---|---|---|---|---|
| /STM32/ | pin_not_connected | 32 | 32 | 32 |
| /ANALOG_IN/ | pin_not_connected | 22 | 22 | 22 |
| /ANALOG_IN/ | pin_not_driven | 19 | 19 | 19 |
| / | global_label_dangling (UD+/UD-) | 2 | 2 | 2 |
| /POWER_SUPPLY/ | multiple_net_names (GND/GNDA, intentional) | 1 | 1 | 1 |
| /USBC/ | power_pin_not_driven | 0 | 1 | **0** |
| **Total** | | **76** | **77** | **76** |

## Analyzer

- Iter-1 had 106 findings; iter-2 has 105. The one removed is RS-001 "VDD1_ISO1 has no declared source". No findings were added.
- Every other section is byte-identical, except `nets.VDD1_ISO1`: has_pwr_flag is now true.

## Netlist

- Iter-1 vs iter-2: 101 components and 119 nets in both, with 0 diffs in value, footprint, fields or membership.
- /USBC/VDD1_ISO1 = {C50.1, U9.3, U9.4, U9.5}.
- The isolation barrier is intact: (+5V_PRI ∪ GND_PRI) ∩ (+5V ∪ GND ∪ +3V3) = ∅.

## Items

- **I2-1 (M-004/R-001): PASS.**
  - #FLG07 sits at (199.39,63.5) on VDD1_ISO1.
  - /USBC/ has 0 ERC violations.
  - RS-001 has cleared.
- **I2-2 (M-005/N-001): PASS.**
  - The wire through R21/R22 is gone, and U9.3 now connects via the stub and the VDD1_ISO1 label.
  - find_wires_crossing_symbols on usb returns 0.
- **I2-3 (N-002): PASS.**
  - The power-symbol values now sit above the + arrows and below the GND symbols.
  - No text is on the cap bodies.
  - The C54↔#PWR0111 bounding-box overlap is a known false positive.
- **I2-4 (N-003): PASS.**
  - Both notes are 2 lines.
  - The longest line ends at x≈265, inside the frame.

## New findings

- [INFO] Non-normalised coordinate `(xy 208.28 48.260000000000005)` on line 6010 of usb.kicad_sch. It is harmless; opening and saving the file in eeschema normalises it.

**Result: 4 PASS, 0 FAIL, 0 REGRESSION.**
