# FIX_LOG: Step 4 round 3, iteration 1 (APPLY)

- Fixer run on 2026-11-17. Scratch folder: `/tmp/claude-1000/-home-andrzej-Documents-Repos-EEG-/2322c6a4-79fd-4009-8cf0-42fae3306225/scratchpad/step4/`.
- Checks: kicad-cli 9.0.9 via `chk.py`, writing `<ID>.xml` and `<ID>_erc.json` and comparing per-net node sets against the previous step.
- Pre-run baseline: 134 comps, ERC 35.
- No schematic lock was present at any fix. The PCB was not touched.

## P-S4-001: APPLIED
- Snapshot: `snapshots/P-S4-001/usb.kicad_sch`.
- Pre-checks passed: D+/D- global label counts were 3/3, and R22 pin 1 is at (205.74, 46.99), R21 pin 1 at (201.93, 46.99).
- Calls:
  - `delete_schematic_net_label` D+ at (205.74, 46.99) and D- at (201.93, 46.99). The old uuids fc4c6806… and 1c6d1edb… are gone.
  - `add_schematic_net_label` UD+ and UD- as global labels, orientation 90, at the same points. New uuids are 80984e28… and b8ea26f5….
  - The shape-restore script printed "ok"; both labels now have `(shape input)`.
- Netlist, exactly as expected:
  - D+ = {J1.A6, J1.B6, U8.1}; D- = {J1.A7, J1.B7, U8.3}
  - UD+ = {R22.1, U8.6}; UD- = {R21.1, U8.4}
  - Nothing else changed.
- ERC 35 → 33: the two global_label_dangling items are gone. The multiple_net_names representative changed from #PWR017 to #PWR016; it is the same intentional item.
- No floating labels and no overlaps. The new labels have no Intersheetrefs property (cosmetic only).

## P-S4-002: APPLIED
- Snapshot: `snapshots/P-S4-002/usb.kicad_sch`.
- The exact-block removal printed "ok"; the text count went 7 → 6, and a search for "Isolator instead" now returns 0.
- No netlist change. ERC 33.

## P-S4-003: BLOCKED (pre-check false positive)
- The pre-check "these names do not exist in any sheet (grep -c == 0)" returned I2C1_SCL 3, I2C1_SDA 3, USART2_TX 1, USART2_RX 1, PA0_WKUP 0.
- Every hit is an `(alternate "…" bidirectional line)` pin-function entry inside the cached U1 lib_symbols in stm32.kicad_sch (lines 1712, 1737, 2235, 2261, 2734, 2757, 2781, 2808).
- A label-type grep returns 0, and no net has these names. The Orchestrator confirmed this independently.
- Nothing was written; the snapshot restore was a no-op.

## P-S4-004: BLOCKED (depends on P-S4-003)
- Nothing was written.

## P-S4-005: APPLIED
- Snapshot: `snapshots/P-S4-005/stm32.kicad_sch`.
- The warning text now reads "WARNING: J2/J3/J5 are on the isolated (patient) side." It ends at about x 262, inside the frame.
- No netlist change. ERC 33.

## P-S4-006: APPLIED
- Snapshot: `snapshots/P-S4-006/stm32.kicad_sch`.
- `batch_add_no_connects` on 27 U1 pins (15, 41, 42, 43, 50, 28, 57, 61, 62, 34, 35, 36, 8, 9, 10, 11, 37, 38, 39, 40, 51, 52, 53, 2, 3, 4, 54). Result: "Placed 27, 0 failed".
- U1 pins 14, 16, 17, 58 and 59 (the J5 pins) were deliberately left unflagged.
- Coordinates carry float noise (e.g. 139.70000000000002), but ERC confirms the flags attach.
- No netlist change. ERC 33 → 6.
- Pre-existing overlaps, not caused by this run: ADS_DRDY over USART3_RX near PC4/PC5, SWDIO over the USB_OTG_FS label end, and C54 ↔ #PWR0111.

## Final
- ERC 6: 5 pin_not_connected on U1 pins 14/16/17/58/59 (these clear once P-S4-003 is applied), plus 1 intentional multiple_net_names.
- Trajectory: 35 → 33 → 33 → [003/004 blocked] → 33 → 6.
- Final netlist: `scratchpad/step4/P-S4-006.xml`.
- Isolation check PASS:
  - The primary nets {+5V_PRI, GND_PRI, D±, UD±} share no nodes with the isolated set.
  - Only U7 and U9 straddle the barrier, and each one's pins split correctly between the two sides.
- Files changed: usb.kicad_sch (P-S4-001, P-S4-002) and stm32.kicad_sch (P-S4-005, P-S4-006).

## Re-run 2026-11-17: P-S4-003 and P-S4-004 with the amended name pre-check (M-S4-003)
- Fresh baseline `pre003.xml` matched P-S4-006: 134 comps, ERC 6. No schematic lock was present.

### P-S4-003: APPLIED
- Snapshot: `snapshots/P-S4-003-r2/stm32.kicad_sch`.
- All pre-checks passed:
  - J5, #PWR0125–0129 and R36/R37 are free.
  - The region is empty.
  - The amended label-type grep returned 0 on every sheet, and no such net names exist.
- Calls:
  - J5 Conn_01x08 "EXP", PinHeader_1x08, at (228.6, 45.72). Pin 1 is at (223.52, 38.1) and pin 8 at (223.52, 55.88); the order is not inverted.
  - #PWR0125 +3V3 on J5.1.
  - A wire from J5.2 to (210.82, 40.64), with #PWR0126 GND at angle 270. The render shows it pointing left, so no rotation was needed.
  - #PWR0127 GND on J5.8.
  - 10 local labels: J5 pins 3–7 and U1 pins 58/59/16/17/14, all snapped.
  - J5 got LCSC C358689 and MPN MTP125-1108S1 (hidden).
- Deviation: `find_wires_crossing_symbols` returns 2 (the existing D1/D2 LED wires). It returns the same 2 on the pre-fix snapshot, so this fix added none.
- Netlist:
  - Comps 134 → 135. +3V3 32 → 33, GND 85 → 87.
  - New nets: I2C1_SCL {J5.3, U1.58}, I2C1_SDA {J5.4, U1.59}, USART2_TX {J5.5, U1.16}, USART2_RX {J5.6, U1.17}, PA0_WKUP {J5.7, U1.14}.
  - ERC 6 → 1.
- Overlaps, reported only:
  - The #PWR0125 "+3V3" value sits over the J5 pin numbers and the I2C1_SCL label.
  - The #PWR0126 "GND" value sits on the J5.2 wire.
  - The #PWR0127 "GND" value overlaps the PA0_WKUP label.
  - The "J5" reference sits on the pin 8 line.
  - On the U1 side, the I2C labels butt against pin numbers 58/59.

### P-S4-004: APPLIED
- Snapshot: `snapshots/P-S4-004-r2/stm32.kicad_sch`.
- All pre-checks passed.
- Calls:
  - R36/R37, 4.7k 0402, at (236.22 / 243.84, 48.26). Pins are at y 44.45 and 52.07, as asserted.
  - #PWR0128 and #PWR0129 +3V3 on pin 1.
  - I2C1_SCL and I2C1_SDA labels on pin 2.
  - LCSC C25900, MPN 0402WGF4701TCE, Tolerance 1%.
- No deviations.
- Netlist:
  - I2C1_SCL {J5.3, R36.2, U1.58}; I2C1_SDA {J5.4, R37.2, U1.59}.
  - +3V3 35, comps 137.
  - ERC stays at 1.
- Overlaps, reported only: the "+3V3" values of #PWR0128 and #PWR0129 sit across the R36/R37 bodies and fields, and R36's "4.7k" runs into "R37".

### Final (round 3)
- ERC 1: only the intentional multiple_net_names (GND/GNDA).
- Trajectory: 35 → 33 → 33 → 33 → 6 → 1 → 1.
- Final netlist: `scratchpad/step4/P-S4-004-r2.xml`. Totals: 137 comps, +3V3 35, GND 87.
- Isolation check PASS. The barrier-straddling parts are only U7 and U9, the same set as before. J5, R36 and R37 are on the isolated side only.
- Files changed in this re-run: stm32.kicad_sch only.
