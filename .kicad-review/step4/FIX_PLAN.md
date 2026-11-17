# FIX_PLAN: Step 4 round 3, iteration 1 (schematic scope only)

Sheets used below:
- SCH_USB = `/home/andrzej/Documents/Repos/EEG-/hardware/EEG_Kicad_Project/usb.kicad_sch`
- SCH_STM = `/home/andrzej/Documents/Repos/EEG-/hardware/EEG_Kicad_Project/stm32.kicad_sch`
- ROOT = `hardware/EEG_Kicad_Project/EEG_Kicad_Project.kicad_sch`
- SCR = `/tmp/claude-1000/-home-andrzej-Documents-Repos-EEG-/2322c6a4-79fd-4009-8cf0-42fae3306225/scratchpad/step4`

**Baseline, measured 2026-11-17 with kicad-cli 9.0.9 (SCR/base_erc.json and SCR/base.xml):**
- ERC 35:
  - 32 pin_not_connected, all on U1: pins 2, 3, 4, 8, 9, 10, 11, 14, 15, 16, 17, 28, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 50, 51, 52, 53, 54, 57, 58, 59, 61, 62.
  - 2 global_label_dangling (UD+, UD-).
  - 1 multiple_net_names (/POWER_SUPPLY/, #PWR017/#PWR028; intentional).
- Nets:
  - D+ = {J1.A6, J1.B6, R22.1, U8.1}
  - D- = {J1.A7, J1.B7, R21.1, U8.3}
  - UD+ = {U8.6}
  - UD- = {U8.4}
  - +3V3 has 32 nodes and GND has 85.
- 134 comps.
- Highest refs across ALL sheets: J4, R35, #PWR0124. The next free refs are J5, R36/R37 and #PWR0125…#PWR0129.
- Label names in the file are ASCII: `UD-` and `D-`, not `−`.

**Datasheet check (F-015).** The USBLC6-2SC6(-MS) datasheet, LCSC C3029034, is saved at SCR/USBLC6-2SC6.pdf. Its graphic symbol on page 2 shows:
- pin 1 = I/O1 = pin 6;
- pin 3 = I/O2 = pin 4;
- pin 5 = VBUS, pin 2 = GND.

The pairs are internally joined, so the 1↔6 and 3↔4 pairing is confirmed. This matches U8's symbol (pins 1 and 6 are named I/O1, pins 3 and 4 are named I/O2).

**MCP rename capability.** No MCP tool can rename a label in place:
- `move_schematic_net_label` changes only the position.
- `add_schematic_net_label` only adds.

So F-015 uses delete plus re-add at the same point with the same orientation (90). The MCP `WireManager.add_label` writes a global_label with no `(shape …)` token, so KiCad would default it to bidirectional. One small scripted step therefore restores `(shape input)` to match the existing D±/UD± labels.

Alternative (not planned, offered only if the user prefers it): a single scripted in-place rename. It would change `"D+"`→`"UD+"` and `"D-"`→`"UD-"` inside the two exact blocks (uuids fc4c6806…, 1c6d1edb…). That keeps the uuid, shape and Intersheetrefs.

## Global rules for the apply phase
- **Lock, before every fix:** `ls hardware/EEG_Kicad_Project/~*.kicad_sch.lck 2>/dev/null` must print nothing, or STOP. The PCB lock `~EEG Kicad Project.kicad_pcb.lck` is expected; ignore it.
- **Snapshot, before every fix:** `mkdir -p .kicad-review/step4/snapshots/P-S4-00n && cp <touched sheet(s)> .kicad-review/step4/snapshots/P-S4-00n/`
- **Checks, after every fix:**
  - `kicad-cli sch export netlist --format kicadxml -o SCR/P-S4-00n.xml ROOT`
  - `kicad-cli sch erc --format json --units mm -o SCR/P-S4-00n_erc.json ROOT`
  - Any ERC item or net change beyond what the entry expects means rollback.
- **Order:** P-S4-001 → 002 → 003 → 004 → 005 → 006. 004 depends on 003; 006 should come after 003 so that only the 27 spare pins remain.
- **PCB:** do not touch or sync it.
- **Cosmetics:** no cosmetic iteration. Field and text overlaps are reported for the user to tidy by hand.

---

## F-015 → P-S4-001  [x] APPROVE   [ ] SKIP   [ ] MANUAL
USB data path through U8's flow-through pins (sheet usb).
- Actions (in order):
  1. ⚠ DESTRUCTIVE: `mcp__kicad__delete_schematic_net_label` {schematicPath: SCH_USB, netName: "D+", position: [205.74, 46.99]}. This is the global label on R22.1, uuid fc4c6806-0c5d-4771-a621-03357c98eba5.
  2. ⚠ DESTRUCTIVE: `mcp__kicad__delete_schematic_net_label` {schematicPath: SCH_USB, netName: "D-", position: [201.93, 46.99]}. This is the global label on R21.1, uuid 1c6d1edb-f9c6-4c47-874e-477e9d1e3cc7.
  3. `mcp__kicad__add_schematic_net_label` {schematicPath: SCH_USB, netName: "UD+", labelType: "global_label", position: [205.74, 46.99], orientation: 90}
  4. `mcp__kicad__add_schematic_net_label` {schematicPath: SCH_USB, netName: "UD-", labelType: "global_label", position: [201.93, 46.99], orientation: 90}
  5. Restore shape `input` on the two new labels. Run with `python3 -I` from the repo root:
     ```python
     import re
     p = "hardware/EEG_Kicad_Project/usb.kicad_sch"
     s = open(p).read()
     for name, x in (("UD+", "205.74"), ("UD-", "201.93")):
         pat = re.compile(r'(\(global_label "' + re.escape(name) + r'"\s*)(\(at ' + re.escape(x) + r' 46\.99 90\))')
         assert len(pat.findall(s)) == 1, (name, len(pat.findall(s)))
         s = pat.sub(lambda m: m.group(1) + "(shape input)\n\t\t" + m.group(2), s, count=1)
     assert s.count('(global_label "UD+"') == 2 and s.count('(global_label "UD-"') == 2
     assert s.count('(global_label "D+"') == 2 and s.count('(global_label "D-"') == 2
     open(p, "w").write(s)
     ```
- Pre-checks:
  - Lock absent; snapshot of usb.kicad_sch taken.
  - `grep -c '(global_label "D+"' SCH_USB` == 3 and `grep -c '(global_label "D-"' SCH_USB` == 3.
  - `get_schematic_pin_locations` R22 gives pin 1 at (205.74, 46.99), and R21 gives pin 1 at (201.93, 46.99). They were verified at plan time: the labels sit directly on the pin-1 endpoints, with no wire.
- Expected netlist result:
  - D+ = {J1.A6, J1.B6, U8.1} and D- = {J1.A7, J1.B7, U8.3} (3 nodes each).
  - UD+ = {R22.1, U8.6} and UD- = {R21.1, U8.4} (2 nodes each).
  - Nothing else changes.
  - ERC 35 → 33: the 2 global_label_dangling items are gone.
- Post-check: `list_floating_labels` SCH_USB shows none. `list_schematic_labels` {netName "UD+"} lists 2 labels, at (146.05, 55.88) and (205.74, 46.99).
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## Item 2 (user note) → P-S4-002  [x] APPROVE   [ ] SKIP   [ ] MANUAL
This removes the note "Not UD+ UD- TO Isolator instead of D+ D-?" on the usb sheet; P-S4-001 answers it.
- Actions (in order):
  1. ⚠ DESTRUCTIVE: scripted exact-block removal. No MCP tool deletes text. Run with `python3 -I` from the repo root:
     ```python
     p = "hardware/EEG_Kicad_Project/usb.kicad_sch"
     s = open(p).read()
     u = "f233c7ae-f16a-4def-a3b5-7d603d13d95b"
     blk = ('\t(text "Not UD+ UD- TO Isolator instead of D+ D-?\\n"\n\t\t(exclude_from_sim no)\n\t\t(at 205.74 26.416 0)\n'
            '\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t)\n\t\t(uuid "' + u + '")\n\t)\n')
     n0 = s.count("(text ")
     assert s.count(blk) == 1 and s.count(u) == 1
     s = s.replace(blk, "", 1)
     assert s.count("(text ") == n0 - 1
     open(p, "w").write(s)
     ```
     The asserts were dry-run at plan time without writing: block count 1, uuid count 1, 7 texts in total.
- Pre-checks: lock absent; snapshot of usb.kicad_sch taken. If P-S4-001 rewrote the file formatting and the block assert fails, STOP and report. Do not loosen the match.
- Expected netlist result: no connectivity change. ERC stays at 33 (or 35 if P-S4-001 was skipped). `list_schematic_texts` SCH_USB {text: "Isolator instead"} returns 0.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## F-014 + spare header → P-S4-003  [x] APPROVE   [ ] SKIP   [ ] MANUAL
Add the J5 1×8 expansion header (sheet stm32), connected through local labels plus +3V3/GND power symbols.

Layout:
- J5 sits at (228.6, 45.72), in the empty area right of U1 under the WARNING text.
- Region x 193–250, y 28–62 was checked: 0 symbols, 0 wires, 0 labels.
- The J5 pins point left at x = 223.52: pin 1 at y 38.10, then every 2.54 mm down to pin 8 at y 55.88.

| J5 pin | net | U1 pin | connection |
|---|---|---|---|
| 1 | +3V3 | — | +3V3 symbol on the pin end (arrow up) |
| 2 | GND | — | 12.7 mm wire stub to the left, then a GND symbol pointing left |
| 3 | I2C1_SCL | 58 PB6 | local label |
| 4 | I2C1_SDA | 59 PB7 | local label |
| 5 | USART2_TX | 16 PA2 | local label |
| 6 | USART2_RX | 17 PA3 | local label |
| 7 | PA0_WKUP | 14 PA0 | local label |
| 8 | GND | — | GND symbol on the pin end (down) |

- Actions (in order):
  1. `mcp__kicad__add_schematic_component` {schematicPath: SCH_STM, symbol: "Connector_Generic:Conn_01x08", reference: "J5", value: "EXP", footprint: "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical", position: {x: 228.6, y: 45.72}, angle: 0}
  2. `mcp__kicad__get_schematic_pin_locations` {SCH_STM, reference "J5"}. Assert pin 1 is at (223.52, 38.1) and pin 8 at (223.52, 55.88), all with angle 180.
     - If the pin order comes out inverted (pin 1 at y 55.88), STOP and report.
  3. `mcp__kicad__add_schematic_component` {SCH_STM, symbol: "power:+3V3", reference: "#PWR0125", value: "+3V3", position: {x: 223.52, y: 38.1}, angle: 0}
  4. `mcp__kicad__add_schematic_wire` {SCH_STM, waypoints: [[223.52, 40.64], [210.82, 40.64]], snapToPins: true}. The start snaps to J5.2; the end is free and gets the GND symbol in step 5.
  5. `mcp__kicad__add_schematic_component` {SCH_STM, symbol: "power:GND", reference: "#PWR0126", value: "GND", position: {x: 210.82, y: 40.64}, angle: 270}. Intent: the GND symbol points left, away from the wire.
     - Post-check with a render of x 200–235, y 30–62. If the symbol body points right, back onto the wire, run `mcp__kicad__rotate_schematic_component` {SCH_STM, reference "#PWR0126", angle: 90}. This is a one-shot orientation correction, not cosmetic iteration.
  6. `mcp__kicad__add_schematic_component` {SCH_STM, symbol: "power:GND", reference: "#PWR0127", value: "GND", position: {x: 223.52, y: 55.88}, angle: 0}
  7. 10× `mcp__kicad__add_schematic_net_label` {schematicPath: SCH_STM, labelType: "label", componentRef, pinNumber, netName}. Pass no orientation, so the label auto-orients outward. Expected placements:
     - J5 labels, orientation 180:
       - J5 pin "3" → I2C1_SCL @ (223.52, 43.18)
       - J5 pin "4" → I2C1_SDA @ (223.52, 45.72)
       - J5 pin "5" → USART2_TX @ (223.52, 48.26)
       - J5 pin "6" → USART2_RX @ (223.52, 50.8)
       - J5 pin "7" → PA0_WKUP @ (223.52, 53.34)
     - U1 labels, orientation 0:
       - U1 pin "58" (PB6) → I2C1_SCL @ (180.34, 119.38)
       - U1 pin "59" (PB7) → I2C1_SDA @ (180.34, 121.92)
       - U1 pin "16" (PA2) → USART2_TX @ (180.34, 66.04)
       - U1 pin "17" (PA3) → USART2_RX @ (180.34, 68.58)
       - U1 pin "14" (PA0) → PA0_WKUP @ (180.34, 60.96)

     The right side of U1 at those y values has no wires or labels; checked x 180–200, y 58–125.
  8. `mcp__kicad__batch_edit_schematic_components` {SCH_STM, components: {"J5": {properties: {LCSC: "C358689", MPN: "MTP125-1108S1"}}}}. The new properties are hidden.
- Pre-checks:
  - Lock absent; snapshot of stm32.kicad_sch taken.
  - Re-confirm the next free refs across all sheets: `cat hardware/EEG_Kicad_Project/*.kicad_sch | grep -oE '"(J|#PWR|R)[0-9]+"' | sort -V | uniq | tail`. The maximums must still be J4, #PWR0124 and R35.
  - `get_elements_in_region` SCH_STM x 193–250, y 28–62 is still empty.
  - The names I2C1_SCL, I2C1_SDA, USART2_TX, USART2_RX and PA0_WKUP do not exist yet in any sheet (`grep -c` gives 0).
- Expected netlist result:
  - New nets:
    - /STM32/I2C1_SCL = {J5.3, U1.58}
    - /STM32/I2C1_SDA = {J5.4, U1.59}
    - /STM32/USART2_TX = {J5.5, U1.16}
    - /STM32/USART2_RX = {J5.6, U1.17}
    - /STM32/PA0_WKUP = {J5.7, U1.14}
  - +3V3 goes from 32 to 33 (+J5.1). GND goes from 85 to 87 (+J5.2, J5.8).
  - Comps go from 134 to 135 (J5, with LCSC/MPN).
  - No other changes.
  - ERC 33 → 28: pin_not_connected on U1 pins 14, 16, 17, 58 and 59 is gone. No new items; J5 has passive pins and the power nets are already driven.
- Post-check: `list_floating_labels` shows none; `find_wires_crossing_symbols` shows 0. Render x 175–250, y 25–130 and report any text overlaps for the user (do not fix them). The likely one is the #PWR0127 "GND" value text near J5 pin 7's label.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## F-014 (I2C pull-ups) → P-S4-004  [x] APPROVE   [ ] SKIP   [ ] MANUAL
Fitted 4.7 kΩ pull-ups on I2C1_SCL and I2C1_SDA to +3V3, placed right of the J5 body. This entry requires P-S4-003.
- Actions (in order):
  1. `mcp__kicad__batch_add_components` {schematicPath: SCH_STM, auto_position_fields: true, components: [
     {symbol: "Device:R", reference: "R36", value: "4.7k", footprint: "Resistor_SMD:R_0402_1005Metric_Pad0.72x0.64mm_HandSolder", position: {x: 236.22, y: 48.26}, rotation: 0},
     {symbol: "Device:R", reference: "R37", value: "4.7k", footprint: "Resistor_SMD:R_0402_1005Metric_Pad0.72x0.64mm_HandSolder", position: {x: 243.84, y: 48.26}, rotation: 0}]}
     This is the same 0402 footprint as the other resistors on this sheet.
  2. `get_schematic_pin_locations` R36 and R37. Assert pin 1 is at (x, 44.45) and pin 2 at (x, 52.07).
  3. `mcp__kicad__add_schematic_component` {SCH_STM, symbol: "power:+3V3", reference: "#PWR0128", value: "+3V3", position: {x: 236.22, y: 44.45}, angle: 0}
  4. `mcp__kicad__add_schematic_component` {SCH_STM, symbol: "power:+3V3", reference: "#PWR0129", value: "+3V3", position: {x: 243.84, y: 44.45}, angle: 0}
  5. `mcp__kicad__add_schematic_net_label` {SCH_STM, labelType: "label", componentRef: "R36", pinNumber: "2", netName: "I2C1_SCL"}. Expected at (236.22, 52.07), orientation 270.
  6. `mcp__kicad__add_schematic_net_label` {SCH_STM, labelType: "label", componentRef: "R37", pinNumber: "2", netName: "I2C1_SDA"}. Expected at (243.84, 52.07), orientation 270.
  7. `mcp__kicad__batch_edit_schematic_components` {SCH_STM, components: {"R36": {properties: {LCSC: "C25900", MPN: "0402WGF4701TCE", Tolerance: "1%"}}, "R37": {properties: {LCSC: "C25900", MPN: "0402WGF4701TCE", Tolerance: "1%"}}}}
- Pre-checks:
  - Lock absent; snapshot of stm32.kicad_sch taken.
  - P-S4-003 is applied: J5 exists, and the I2C1_SCL/SDA labels exist.
  - The highest R is still R35 and the highest #PWR is #PWR0127.
  - `get_elements_in_region` x 233–250, y 38–64 contains nothing.
- Expected netlist result:
  - /STM32/I2C1_SCL = {J5.3, R36.2, U1.58} and /STM32/I2C1_SDA = {J5.4, R37.2, U1.59}.
  - +3V3 goes from 33 to 35 (+R36.1, R37.1).
  - Comps go from 135 to 137.
  - ERC stays at 28.
- Post-check: `list_floating_labels` shows none. Render x 225–255, y 30–65, overlaps to be reported only.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## Item 3 (warning note) → P-S4-005  [x] APPROVE   [ ] SKIP   [ ] MANUAL
Extend the existing WARNING text to cover J5. This is the least invasive option: one token changes, there is no new object, and the line grows by 3 characters. It stays inside the frame, ending around x 262 against the frame edge at about x 287.
- Actions (in order):
  1. Scripted exact replace. Run with `python3 -I` from the repo root:
     ```python
     p = "hardware/EEG_Kicad_Project/stm32.kicad_sch"
     s = open(p).read()
     u = "f14181e2-8563-47be-952c-f281f078c8fc"
     old = '(text "WARNING: J2/J3 are on the isolated (patient) side.\\nConnecting'
     new = '(text "WARNING: J2/J3/J5 are on the isolated (patient) side.\\nConnecting'
     assert s.count(old) == 1 and s.count(u) == 1 and s.count("J2/J3/J5") == 0
     i = s.index(old); assert s.index(u) - i < 600   # same text block
     s = s.replace(old, new, 1)
     open(p, "w").write(s)
     ```
     The asserts were dry-run at plan time: count 1 and uuid count 1.
- Pre-checks: lock absent; snapshot of stm32.kicad_sch taken.
- Expected netlist result: no connectivity change. ERC stays at 28 (or 33 if P-S4-003 was skipped). `list_schematic_texts` {text: "J2/J3/J5"} returns 1, at (205.74, 27.94).
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## F-014 → P-S4-006  [x] APPROVE   [ ] SKIP   [ ] MANUAL
No-connect flags on the 27 remaining spare U1 pins.
- Actions (in order):
  1. `mcp__kicad__batch_add_no_connects` {schematicPath: SCH_STM, pins: [27 entries, each {componentRef: "U1", pinName: "<number>"}]}. Numbers are used to avoid name ambiguity. Each pin name and endpoint was checked against `get_schematic_pin_locations` U1:

     | pin | name | endpoint |
     |---|---|---|
     | 15 | PA1 | (180.34, 63.50) |
     | 41 | PA8 | (180.34, 81.28) |
     | 42 | PA9 | (180.34, 83.82) |
     | 43 | PA10 | (180.34, 86.36) |
     | 50 | PA15 | (180.34, 99.06) |
     | 28 | PB2 | (180.34, 109.22) |
     | 57 | PB5 | (180.34, 116.84) |
     | 61 | PB8 | (180.34, 124.46) |
     | 62 | PB9 | (180.34, 127.00) |
     | 34 | PB13 | (180.34, 134.62) |
     | 35 | PB14 | (180.34, 137.16) |
     | 36 | PB15 | (180.34, 139.70) |
     | 8 | PC0 | (139.70, 83.82) |
     | 9 | PC1 | (139.70, 86.36) |
     | 10 | PC2 | (139.70, 88.90) |
     | 11 | PC3 | (139.70, 91.44) |
     | 37 | PC6 | (139.70, 99.06) |
     | 38 | PC7 | (139.70, 101.60) |
     | 39 | PC8 | (139.70, 104.14) |
     | 40 | PC9 | (139.70, 106.68) |
     | 51 | PC10 | (139.70, 109.22) |
     | 52 | PC11 | (139.70, 111.76) |
     | 53 | PC12 | (139.70, 114.30) |
     | 2 | PC13 | (139.70, 116.84) |
     | 3 | PC14 | (139.70, 119.38) |
     | 4 | PC15 | (139.70, 121.92) |
     | 54 | PD2 | (139.70, 78.74) |

     The pin list in apply-ready form: 15, 41, 42, 43, 50, 28, 57, 61, 62, 34, 35, 36, 8, 9, 10, 11, 37, 38, 39, 40, 51, 52, 53, 2, 3, 4, 54.
- Pre-checks:
  - Lock absent; snapshot of stm32.kicad_sch taken.
  - `grep -c '(no_connect' SCH_STM` == 0.
  - The current ERC pin_not_connected set equals exactly these 27 pins. If P-S4-003 was skipped, it also contains 14, 16, 17, 58 and 59; those must NOT be flagged.
- Expected netlist result:
  - No connectivity change.
  - `grep -c '(no_connect' SCH_STM` == 27, and the result reports "Placed 27 …, 0 failed".
  - ERC 28 → 1: only the intentional multiple_net_names on /POWER_SUPPLY/ remains. This is the final target.
  - Isolation check in the final netlist: GND_PRI and GND share no node, and the D± nets (primary side) have no node in common with the U9 side-2 / U1 nets.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

### ERC trajectory
35 → (001) 33 → (002) 33 → (003) 28 → (004) 28 → (005) 28 → (006) **1**.

### I2C pull-up recommendation (P-S4-004)
Fit 4.7 kΩ to +3V3 on both lines (populated, not DNP):
- **Internal pull-ups are too weak.** The STM32's internal pull-ups (about 40 kΩ) are too weak for I2C at 100 or 400 kHz once a cable and a module are attached.
- **Doubling up is harmless.** If the attached module also has 4.7–10 kΩ pull-ups, the parallel value is about 2.4–3.2 kΩ. That gives a sink current of about 1.0–1.4 mA, well within the 3 mA I2C spec and the STM32 I/O limit.
- **DNP is the riskier choice.** A board with DNP pull-ups plus a module without pull-ups fails silently and needs rework.
- **No effect when the pins are used as GPIO.** If PB6/PB7 are used as GPIO instead, the pull-ups to 3V3 are benign.

DNP remains a no-cost alternative: set `dnp` on R36/R37.

### Firmware notes (no schematic action)
- PA9 is NC: disable VBUS sensing (F-021).
- PC14/PC15 (the LSE pins) are unused.
- Set all NC pins to analog mode.
- PB6/PB7 are AF4 I2C1 open-drain; PA2/PA3 are AF7 USART2; PA0 is WKUP/GPIO.
