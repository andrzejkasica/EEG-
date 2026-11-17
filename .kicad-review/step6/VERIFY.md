# VERIFY: Step 6 round 5, iteration 1 (base ad3e7bb)

These are fresh exports of the current state and the base, compared with my own scripts. No design file was modified, and no DRC was run. Outputs are in `analysis/iter-1/`; the base exports and scripts are in `scratchpad/verify6/`.

| Metric | Base | Now |
|---|---|---|
| ERC errors / warnings | 0 / 1 | 0 / 1 (same GND/GNDA) |
| Comps / nets | 147 / 128 | 147 / 128 |
| Flat BOM, default | 147 | 137 |
| Flat BOM, `--include-excluded-from-bom` | 147 | 147 (same refs as base) |
| Grouped BOM lines | 55 | 44 |
| 0603 100n lines | 2 | 1 (×8) |
| Parts with exclude_from_bom | 0 | 10 (TP1–TP9, JP1) |
| usb global / local labels | 10 / 2 | 2 / 10 |
| Analyzer findings (error / warning / info) | 1 / 3 / 72 | 1 / 3 / 72 |
| label_shape_warnings | 4 | 0 |
| SS-001 MPN coverage (unique lines) | 13/45 | 15/43 |
| Orphaned wires / floating labels | 0 / 0 | 0 / 0 |

## Diff vs base
Only allowed changes:
- C32/34/38/39/42/46 changed to "100n".
- D1/D2 changed to "LED_RED", with C2286 / KT-0603R.
- R19/R20 gained C11702 / 0402WGF1001TCE / 1%.
- TP1–TP9 and JP1 gained exclude_from_bom.
- Net renames, with identical members:
  - D± → /USBC/D±
  - UD± → /USBC/UD±

Unchanged: root, .kicad_pro, sym-lib-table and EEG_custom.

## Verdicts
- **P-S6-001: PASS.** The 0603 100n caps are now a single BOM line ×8.
- **P-S6-002: PASS.**
  - The default BOM is missing exactly {JP1, TP1–TP9}.
  - With excluded parts included, the refs match the base.
  - JP1 has left the SS-001 missing list.
- **P-S6-003: PASS.**
  - D±/UD± are now local labels.
  - USB_OTG_FS_DP/DM are bidirectional on both usb and stm32.
  - No other sheet uses the names D±/UD±.
  - label_shape_warnings went from 4 to 0.
- **P-S6-004: PASS.**
  - The fields are correct and hidden.
  - SS-001 coverage rose from 13 to 15 lines.
  - Note: the property formatting is compact; Eeschema normalises it on save.
- **Isolation barrier: PASS.**
  - Primary side: 11 nets. Isolated side: 117 nets. They share none.
  - Only U7 and U9 straddle the barrier.

## Analyzer
- Rule counts are identical to the base. The non-info set is the same four known items:
  - SS-001 (error)
  - CG-AUD on J4
  - RS-001 on 5V_L1
  - SJ-DET on JP1
- usb_compliance is unchanged.

## New findings
None.

## Plan target (Task 2 Step 6): MET
- ERC has 0 errors.
- The only high or error items are SS-001 and the tracked F-002.

**Result: 4 PASS / 0 FAIL / 0 REGRESSION.**
