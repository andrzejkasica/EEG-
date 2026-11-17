# FIX_LOG: Step 5 round 4, iteration 1 (APPLY)

- **Scratch and helpers.** Scratch folder `scratchpad/step5/`. Helper scripts are in `scratchpad/tools/`: check.sh, diff.py, region.py, refs.sh, iso.py.
- **Baseline re-verified.** ERC 1, 137 comps; GND 87, +3V3 35, +5V 6, −5V 5.
- **Locks.** No schematic lock before any fix. The PCB was not touched and DRC was not run.
- **Tooling note.** The first version of region.py had a parse bug and returned empty for every region. It was caught at the P-S5-005 pre-check. After the fix, every region pre-check for 001–005 was re-run against the pre-fix snapshots, and all regions were confirmed empty.
- **Footprint naming.** Wherever the plan abbreviated "0402", I used the project's full resistor footprint name, `R_0402_1005Metric_Pad0.72x0.64mm_HandSolder`.

## P-S5-001: APPLIED
- **Snapshot:** `snapshots/P-S5-001/analog_in.kicad_sch`
- **Added:**
  - R38 and R39, 100k, at (251.46/261.62, 116.84). Pin asserts passed.
  - #PWR0130 and #PWR0131 GND.
  - Global labels SPI1_SCK on R38.1 and SPI1_MOSI on R39.1.
  - Fields: C25741, 0402WGF1003TCE, 1%.
- **Netlist and ERC:**
  - SPI1_SCK = {R38.1, TP6.1, U1.21, U3.40}
  - SPI1_MOSI = {R39.1, U1.23, U3.34}
  - GND 87 → 89; comps 139; ERC 1.
- **Overlaps:** the R38 and R39 ref/value texts sit on their bodies, and the GND values of #PWR0130/0131 sit at the resistor centres.

## P-S5-002: APPLIED
- **Snapshot:** `snapshots/P-S5-002/analog_in.kicad_sch`
- **Added:**
  - R40, 100k, at (271.78, 116.84). Pin assert passed.
  - #PWR0132 GND.
  - Global label SPI1_MISO on R40.1.
  - Fields set.
- **Netlist and ERC:** SPI1_MISO = {R40.1, U1.22, U3.43}; GND 90; comps 140; ERC 1.
- **Overlaps:** the R40 fields sit on its body, and the #PWR0132 GND value overlaps it.

## P-S5-003: APPLIED
- **Snapshot:** `snapshots/P-S5-003/analog_in.kicad_sch`
- **Pre-check:** VCAP1 has 2 labels at label level. A raw grep also hits the U3 lib_symbols pin name, which is a false positive.
- **Added:** TP7 "VCAP1" at (50.8, 185.42), with a local label VCAP1 (orientation 270).
- **Netlist and ERC:** VCAP1 = {C43.1, TP7.1, U3.28}; comps 141; ERC 1.
- **Overlaps:** the VCAP1 label text overlaps TP7's value and reference.

## P-S5-004: APPLIED
- **Snapshot:** `snapshots/P-S5-004/power.kicad_sch`
- **Added:**
  - TP8 "+5V" at (88.9, 165.1), rot 180, with #PWR0133 +5V.
  - TP9 "-5V" at (101.6, 165.1), rot 0, with #PWR0134 −5V (angle 180).
- **Netlist and ERC:** +5V 6 → 7 (the isolated rail); −5V 5 → 6; comps 143; ERC 1.
- **Overlaps:**
  - The "+5V" texts of TP8 and #PWR0133 are doubled and overlap, and the #PWR0133 arrow touches TP8's reference.
  - The −5V text overlaps TP9's reference.

## P-S5-005: APPLIED
- **Snapshot:** `snapshots/P-S5-005/power.kicad_sch`
- **Added:**
  - D3 D_Schottky "1N5819WS", Diode_SMD:D_SOD-323, at (60.96, 100.33), angle 180.
  - **Polarity assert passed:** A (pin 2) is at (57.15, 100.33) on the −5V/IN side; K (pin 1) is at (64.77, 100.33) on the OUT side.
  - Wires:
    - (48.26, 113.03) → (48.26, 100.33) → (57.15, 100.33), from the existing −5V junction to D3.A
    - (64.77, 100.33) → (71.12, 100.33) → (71.12, 113.03), from D3.K to U6.5
    - both drawn with snapToPins=false, with exact endpoints
  - Fields: C191023, 1N5819WS.
- **Netlist and ERC:**
  - −5V 6 → 7 (+D3.2).
  - Net-(U6-OUT) is renamed Net-(D3-K) = {C23.1, C26.1, D3.1, L4.1, U6.5}. This is a name change only, which the plan allows.
  - comps 144; ERC 1; 0 wire crossings; no orphans.
- **Overlaps:** none. D3's reference sits close to a section line.

## P-S5-006: APPLIED (approved destructive wire delete)
- **Snapshot:** `snapshots/P-S5-006/power.kicad_sch`
- **Changes:**
  - Added R41 "0" at (170.18, 54.61), angle 90. Pins are at (166.37, 54.61) and (173.99, 54.61).
  - Deleted wire a528380f (166.37, 62.23) → (168.91, 62.23). The other wires at the node are intact.
  - Added wires L1.2 → R41.1 and R41.2 → the junction at (173.99, 62.23).
  - Added local labels 5V_L1 and 5V_REG.
  - Fields: C17168, 0402WGF0000TCE, jumper. Fitted.
- **Netlist and ERC:**
  - Net-(U2-IN) is gone.
  - 5V_L1 = {L1.2, R41.1}
  - 5V_REG = {C11.1, C12.1, C17.1, R41.2, U2.2, U4.1, U4.3}
  - +5V unchanged; comps 145; ERC 1.
  - #FLG02 and all input caps are on the regulator side.
- **Overlaps:** none.

## P-S5-007: APPLIED
- **Snapshot:** `snapshots/P-S5-007/stm32.kicad_sch`
- **Added:**
  - R42 1.5k at (241.3, 132.08), rot 90.
  - D4 LED "LED_GRN", LED_0603, at (251.46, 132.08), rot 180. **Polarity assert passed:** A is at (247.65, 132.08) and K at (255.27, 132.08).
  - #PWR0135 +3V3 and #PWR0136 GND, with 2 wires.
  - Fields: R42 C25867 / 0402WGF1501TCE / 1%; D4 C2986030 / 19-217/G7C-AN1P2/6T.
- **Netlist and ERC:** Net-(D4-A) = {D4.2, R42.2}; +3V3 36; GND 91; comps 147; ERC 1.
- **Overlaps:**
  - R42's fields sit on its body, and the #PWR0135 arrow overlaps R42's left end.
  - The #PWR0136 GND text stacks under D2's GND text.

## Final
- **ERC:** 1, the intentional GND/GNDA multiple_net_names. No errors.
- **Nets:** GND 91, +3V3 36, +5V 7, −5V 7.
- **Components:** 147 (was 137). New: D3, D4, R38–R42, TP7–TP9.
- **Net renames and splits:**
  - Net-(U2-IN) became 5V_L1 + 5V_REG.
  - Net-(U6-OUT) became Net-(D3-K).
  - Net-(D4-A) is new.
- **Diff against the base:** only expected changes.
- **Isolation check: PASS.** A flood-fill from J1 and from U3, not traversing U7 or U9, shows:
  - no shared nets between the two sides;
  - only U7 and U9 straddle the barrier;
  - all 10 new parts are on the isolated side.
- **Final netlist:** `scratchpad/step5/net_007.xml`
- **Final ERC:** `scratchpad/step5/erc_007.json`
- **Applied:** 7. **Blocked:** 0.
