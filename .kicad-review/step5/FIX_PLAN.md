# FIX_PLAN: Step 5 round 4, iteration 1 (schematic scope only)

Sheets: SCH_AIN = analog_in.kicad_sch, SCH_PWR = power.kicad_sch, SCH_STM = stm32.kicad_sch (under `/home/andrzej/Documents/Repos/EEG-/hardware/EEG_Kicad_Project/`). ROOT = `hardware/EEG_Kicad_Project/EEG_Kicad_Project.kicad_sch`. SCR = `/tmp/claude-1000/-home-andrzej-Documents-Repos-EEG-/2322c6a4-79fd-4009-8cf0-42fae3306225/scratchpad/step5`.

## Baseline (base 66f244b)

**Counts:** ERC 1 (intentional GND/GNDA); 137 comps.

**Net node counts:**
- GND 87, +3V3 35, +5V 6, −5V 5.

**Net members:**
- VCAP1 = {C43.1, U3.28}
- Net-(U6-OUT) = {C23.1, C26.1, L4.1, U6.5}
- Net-(U2-IN) = {C11.1, C12.1, C17.1, L1.2, U2.2, U4.1, U4.3}
- SPI1_SCK = {TP6.1, U1.21, U3.40}
- SPI1_MOSI = {U1.23, U3.34}
- SPI1_MISO = {U1.22, U3.43}

**Highest refs:** R37, D2, TP6, #PWR0129.

**New refs by fix:**
| Fix | New refs |
|---|---|
| 001 | R38, R39, #PWR0130–0131 |
| 002 | R40, #PWR0132 |
| 003 | TP7 |
| 004 | TP8, TP9, #PWR0133–0134 |
| 005 | D3 |
| 006 | R41 |
| 007 | R42, D4, #PWR0135–0136 |

## Symbol facts
- **Device:D_Schottky and Device:LED:** pin 1 = K, pin 2 = A. At angle 180, A is on the left and K on the right (as on D1/D2).
- **Device:R:** at angle 90, pin 1 is on the left; at angle 0, pin 1 is on top.
- **Connector:TestPoint:** the pin is at the symbol origin. TP1–TP6 use the footprint TestPoint_Pad_D1.0mm and have no LCSC fields.
- **D_SOD-323:** pad 1 = cathode.
- **SPI1_\* global labels:** all are shape bidirectional, which is the MCP default.

## Global rules
- **Lock:** before each fix, check that there is no `~*.kicad_sch.lck` (the PCB lock is expected).
- **Snapshot:** save to `.kicad-review/step5/snapshots/P-S5-00n/` before each fix.
- **After each fix:** export the kicad-cli netlist and ERC to SCR and diff per-net node sets. Anything unexpected means rollback.
- **ERC:** expected to stay at 1 after every fix.
- **Isolation check at the end:** the primary nets {+5V_PRI, GND_PRI, D±, UD±} share no nodes with isolated nets, only U7 and U9 straddle the barrier, and every new part is on the isolated side.
- **Order:** 001 → 007.
- **Do not touch the PCB.** Do not iterate on cosmetics; report overlaps only.

## New parts
| Part | LCSC | MPN | Type |
|---|---|---|---|
| 100k 0402 1% | C25741 | 0402WGF1003TCE | Basic |
| 0 Ω 0402 | C17168 | 0402WGF0000TCE | Basic |
| 1.5k 0402 1% | C25867 | 0402WGF1501TCE | Basic |
| Schottky SOD-323 40 V/1 A | C191023 | 1N5819WS | Basic |
| Yellow-green 0603 LED | C2986030 | Everlight 19-217/G7C-AN1P2/6T | Ext (no Basic yellow-green exists) |

---

## S5-004 → P-S5-001  [x] APPROVE   [ ] SKIP   [ ] MANUAL
100k pull-downs on SPI1_SCK and SPI1_MOSI (analog_in, new row under R16–R18).
- Actions:
  1. `batch_add_components` on SCH_AIN:
     - R38 100k, R_0402 HandSolder footprint, at (251.46, 116.84), rotation 0
     - R39 100k, same footprint, at (261.62, 116.84), rotation 0
  2. `get_schematic_pin_locations`: assert pin 1 is at y 113.03 and pin 2 at y 120.65. If not, STOP.
  3. power:GND #PWR0130 at (251.46, 120.65) and #PWR0131 at (261.62, 120.65).
  4. Global label SPI1_SCK snapped to R38.1, and global label SPI1_MOSI snapped to R39.1 (auto-orientation, expected 90).
  5. Set fields on R38 and R39: LCSC C25741, MPN 0402WGF1003TCE, Tolerance 1%.
- Pre-checks: lock and snapshot taken; refs are free; region x 245–280, y 99–130 is empty (verified).
- Expected result:
  - SPI1_SCK = {R38.1, TP6.1, U1.21, U3.40}
  - SPI1_MOSI = {R39.1, U1.23, U3.34}
  - GND 87 → 89; comps 137 → 139
  - ERC 1, and no floating labels.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## E1 (F-016) → P-S5-002  [x] APPROVE   [ ] SKIP   [ ] MANUAL
100k pull-down on SPI1_MISO (analog_in, next to 001).
- Actions:
  1. R40 100k at (271.78, 116.84), rotation 0. Assert pin 1 is at (271.78, 113.03).
  2. power:GND #PWR0132 at (271.78, 120.65).
  3. Global label SPI1_MISO snapped to R40.1.
  4. Fields: LCSC C25741, MPN 0402WGF1003TCE, Tolerance 1%.
- Pre-checks: lock and snapshot taken; R40 and #PWR0132 are free; the region is empty.
- Expected result:
  - SPI1_MISO = {R40.1, U1.22, U3.43}
  - GND +1; comps +1
  - ERC 1.
  - The F-016 firmware note (enable the PA6 internal pull-down) becomes optional.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## S5-002 → P-S5-003  [x] APPROVE   [ ] SKIP   [ ] MANUAL
Test point on VCAP1 (analog_in), connected through a local VCAP1 label as C43 is.
- Actions:
  1. Connector:TestPoint TP7, value "VCAP1", footprint TestPoint_Pad_D1.0mm, at (50.8, 185.42), angle 0. Assert the pin is at (50.8, 185.42).
  2. Local label VCAP1 snapped to TP7.1.
- Pre-checks: lock and snapshot taken; TP7 is free; region x 15–170, y 177–196 is empty; there are exactly 2 existing VCAP1 labels.
- Expected result:
  - VCAP1 = {C43.1, TP7.1, U3.28}
  - comps +1
  - ERC 1.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## E2 (F-017) → P-S5-004  [x] APPROVE   [ ] SKIP   [ ] MANUAL
Test points on +5V and −5V (power). Each is a free-standing TP plus power symbol, the same pattern as TP1 and TP3.
- Actions:
  1. `batch_add_components`:
     - TP8 "+5V" at (88.9, 165.1), rotation 180
     - TP9 "-5V" at (101.6, 165.1), rotation 0
     - both with the TestPoint_Pad_D1.0mm footprint
     - Assert the pins are at those points.
  2. power:+5V #PWR0133 at (88.9, 165.1), angle 0.
  3. power:-5V #PWR0134 at (101.6, 165.1), angle 180 (as #PWR035/#PWR026 are).
- Pre-checks: lock and snapshot taken; refs are free; region x 75–170, y 145–195 is empty.
- Expected result:
  - +5V 6 → 7; −5V 5 → 6
  - comps +2
  - ERC 1.
  - This +5V is the isolated U7 output, not +5V_PRI.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## S5-007 → P-S5-005  [x] APPROVE   [ ] SKIP   [ ] MANUAL
Schottky D3 across U6 (TPS72325) IN–OUT, per TI SLVS346E Fig. 7-1 (power).

**Datasheet basis:**
- §6.3.1: "Do not drive the output less than 0.3V below the input… biases the body diode… current to flow from the input to the output."
- §7.1.4: "large COUT and the input supply collapses with little or no load current…" Fig. 7-1 shows the Schottky in parallel with the body diode, IN to OUT.

**Orientation:** anode to −5V (U6.2 IN), cathode to Net-(U6-OUT) (U6.5, before L4).
- Normal operation: about 2.5 V reverse bias.
- At power-up: about 5 V reverse bias.
- It conducts only when OUT is more than about 0.3 V below IN, and it clamps before the body diode does.

**Part:** 1N5819WS, C191023 (Basic).
- Leakage is about 1–10 µA at 2.5 V and 25 °C (estimated from the graph), and about 0.1 mA at 100 °C. It flows OUT→IN, the same direction as the pass current, so it is negligible against the about 7 mA AVSS load.
- Cj is about 110 pF. Its ripple bypass is −100 dB or better (estimate).
- The low-leakage BAT54W (C8657) has only 5 in stock. The fallback is SD103AWS (C7420360, Ext).

**Actions:**
1. Device:D_Schottky D3 "1N5819WS", footprint D_SOD-323, at (60.96, 100.33), angle 180. Assert A (pin 2) is at (57.15, 100.33) and K (pin 1) at (64.77, 100.33). If not, STOP and do not wire.
2. Wire (48.26, 113.03) → (48.26, 100.33) → (57.15, 100.33). It starts on the existing −5V/U6 IN junction and ends at D3.A.
3. Wire (64.77, 100.33) → (71.12, 100.33) → (71.12, 113.03). It runs from D3.K to U6.5 OUT.
4. Fields: LCSC C191023, MPN 1N5819WS.

**Pre-checks:** lock and snapshot taken; D3 is free; region x 45–75, y 98.5–112 is empty; U6 IN is at (50.8, 113.03) and OUT at (71.12, 113.03); the junction at (48.26, 113.03) exists.

**Expected result:**
- −5V gains D3.2.
- Net-(U6-OUT) gains D3.1. If the net is renamed to Net-(D3-K), that is a name change only.
- comps +1
- ERC 1, and no new wire crossings.

**U4 (TPS73225) needs no fix.** It uses an NMOS pass device with reverse blocking (SBVS037S §6.3.5, IREV ≤ 10 µA), and its OUT abs max does not depend on VIN. Capture it at bring-up power-down only.

- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## E3 (S5-001 bring-up) → P-S5-006  [x] APPROVE   [ ] SKIP   [ ] MANUAL
A 0 Ω link R41 splits Net-(U2-IN) into an L1-output side and a regulator-input side (power).

**Current wiring:**
- L1.2 is at (166.37, 62.23).
- Wire a528380f runs from there to the junction at (168.91, 62.23), which carries #FLG02. That junction leads down to C17/U4 and right to the junction at (173.99, 62.23), which leads to C11, C12 and U2.IN.

**Cap placement:** C11, C12, C17 and #FLG02 all stay on the regulator side, because they are the local input caps for U2 and U4. The L1 side has no cap, and C10 stays before L1.

**Link current:** about 16 mA typical, ≤ 30 mA estimated. 0402 is adequate.

**New nets:**
- /POWER_SUPPLY/5V_L1 = {L1.2, R41.1}
- /POWER_SUPPLY/5V_REG = {R41.2, C11.1, C12.1, C17.1, U2.2, U4.1, U4.3}

**Actions:**
1. Device:R R41 "0" at (170.18, 54.61), angle 90. Assert pin 1 is at (166.37, 54.61) and pin 2 at (173.99, 54.61).
2. ⚠ DESTRUCTIVE: `delete_schematic_wire` (166.37, 62.23) → (168.91, 62.23), uuid a528380f-6c44-4960-a2ea-a794247aff90.
3. Wire (166.37, 62.23) → (166.37, 54.61), from L1.2 to R41.1.
4. Wire (173.99, 54.61) → (173.99, 62.23), from R41.2 to the existing junction.
5. Local labels: 5V_L1 on R41.1 and 5V_REG on R41.2.
6. Fields: LCSC C17168, MPN 0402WGF0000TCE, Tolerance "jumper". Fitted (not DNP).

**Pre-checks:**
- Lock and snapshot taken; R41 is free.
- Region x 163–178, y 50–60 is empty.
- The wire and both junctions exist.
- The names 5V_L1 and 5V_REG are unused.

**Expected result:**
- Net-(U2-IN) is gone, replaced by the two nets above. +5V is unchanged.
- comps +1
- ERC 1, and no new orphaned wires or floating labels.

- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## E4 → P-S5-007  [x] APPROVE   [ ] SKIP   [ ] MANUAL
Power LED D4 with R42, from +3V3 to GND (stm32, a third row under D1/D2).

**Part:**
- The LED is yellow-green AlGaInP (Everlight 19-217/G7C-AN1P2/6T, C2986030). A pure-green InGaN LED, Vf about 3.1 V, would barely light at 3.3 V.
- R42 is 1.5k (Basic), which gives about 0.97 mA. Alternatives: 1.2k (Ext) gives about 1.2 mA, and 1k (Basic) gives about 1.45 mA.

**Actions:**
1. `batch_add_components`:
   - R42 1.5k at (241.3, 132.08), rotation 90
   - D4 "LED_GRN", footprint LED_0603_1608Metric, at (251.46, 132.08), rotation 180
2. Assert:
   - R42 pin 1 is at (237.49, 132.08) and pin 2 at (245.11, 132.08).
   - D4 A is at (247.65, 132.08) and K at (255.27, 132.08). If D4 is inverted, STOP.
3. power:+3V3 #PWR0135 at (237.49, 132.08), and power:GND #PWR0136 at (257.81, 132.08).
4. Wires: (245.11, 132.08) → (247.65, 132.08) and (255.27, 132.08) → (257.81, 132.08).
5. Fields:
   - R42: LCSC C25867, MPN 0402WGF1501TCE, Tolerance 1%
   - D4: LCSC C2986030, MPN 19-217/G7C-AN1P2/6T

**Pre-checks:** lock and snapshot taken; refs are free; region x 228–265, y 126–138 is empty.

**Expected result:**
- Net-(D4-A) = {D4.2, R42.2}
- +3V3 35 → 36; GND +1
- comps +2
- ERC 1.

- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## Cumulative expectation (all 7 applied)
- Comps 137 → 147.
- GND 87 → 91, +3V3 35 → 36, +5V 6 → 7, −5V 5 → 7.
- Net-(U2-IN) is replaced by 5V_L1 (2 nodes) and 5V_REG (7 nodes).
- ERC stays at 1 after every fix.

**Counts:** 7 entries, 1 destructive action (P-S5-006 step 2), 0 manual items.
