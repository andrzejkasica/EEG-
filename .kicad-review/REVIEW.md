# KiCad Review Loop: final report (schematic scope)

- **Project:** `hardware/EEG_Kicad_Project`. Branch `task2-schematic-gaps`.
- **Checkpoint:** baseline review at `c348402`; findings committed in `bdf814f`.
- **Dates:** started 2026-11-16 (Phase 1). Fixed and verified 2026-11-17 in 2 iterations.
- **Scope:** CRITICAL + HIGH + MEDIUM, which is F-001 to F-010. The PCB was out of scope and was not touched.

## Summary

| Metric | Baseline | Final |
|---|---|---|
| ERC violations | 76 | 76 |
| Components (netlist) | 96 | 101 |
| Parts without footprint | 10 | 0 |
| kicad-happy findings | 106 | 105 |
| Isolation barrier (PRI ∩ isolated nets) | ∅ | ∅ |

The remaining 76 ERC violations are all the known, accepted items:
- 54 pin_not_connected:
  - 32 spare STM32 GPIOs (F-014)
  - 22 ADS1299 Step-3 pins
- 19 pin_not_driven on Step-3 inputs (F-020)
- 2 dangling UD+/UD− labels (F-015)
- 1 intentional GND/GNDA merge

### Findings in scope

| Severity | Total | Fixed + verified | Open | Manual |
|---|---|---|---|---|
| HIGH | 4 | 3 (F-001, F-003, F-004) | 1 (F-002, on hold) | — |
| MEDIUM | 6 | 6 (F-005 … F-010) | 0 | — |

Out of scope and still open: LOW F-011 to F-019, INFO F-020 to F-023.

## Fixes

| ID | Change | Result |
|---|---|---|
| P-001 | U9 VDD1/PDEN/SPU moved to new net VDD1_ISO1, plus C50 100n to GND_PRI | PASS |
| P-003 | R3–R6 deleted from the NR pins of U4/U6 | PASS |
| P-004 | Footprints added: L1–L4 0805, J1 GCT USB4105 16P, SW1 XKB TS-1187A | PASS |
| P-005 | R21–R24, 24 Ω 1 % series termination on U9 UD± and DD± | PASS |
| P-006 | U9 bypass caps C51 (VBUS1) and C52 (VBUS2/VDD2), plus placement note | PASS |
| P-007 | C53 4.7u X5R on +5V_PRI (VBUS total 4.9 µF) | PASS |
| P-008 | Patient-side warning text at J2/J3 | PASS |
| P-009 | Y1 CL/ESR/C0/Package properties; C48/C49 set to "15p C0G" | PASS |
| P-010 | C54 4.7u X5R bulk cap on +3V3 near U1 | PASS |
| I2-1 | PWR_FLAG #FLG07 on VDD1_ISO1 (fixes iteration-1 regression R-001) | PASS |
| I2-2 | VDD1 wire re-routed off R21/R22 via a label stub (N-001) | PASS |
| I2-3 | Value fields of new power symbols moved off the cap bodies (N-002) | PASS |
| I2-4 | usb notes wrapped to fit the frame (N-003) | PASS |
| P-002 | Replace U7 with a regulated isolated DC-DC | **ON HOLD** |

## Remaining risks

- **F-002 (HIGH, open).** U7 TMU3-0511 is unregulated, so +5V can exceed the 5.5 V input limit of U2, U4 and U5 at light load.
  - The TRN 3-0511 was checked against `docs/datasheets/TRN3.pdf` and rejected by the user. It is a 9 V-nominal 2:1 module, which leaves too little headroom at USB 5 V.
  - **Do not build the board until this is resolved.**
- **F-023 (INFO).** The isolation is functional grade only (1.5 kV); it is not medical 2×MOPP.
- **INFO.** A non-normalised coordinate remains in usb.kicad_sch. Opening and saving the file in eeschema fixes it.

## Manual actions required (see MANUAL_ACTIONS.md)

1. **M-001 / F-002.** In Task 3, choose a regulated isolated DC-DC with:
   - a 5 V-nominal input (4.5–5.5 V class)
   - isolation of at least 1.5 kVDC
   - at least 300 mA output
   - no minimum load

   After that, re-plan P-002.
2. **M-002 (optional).** Delete the stray 2-wire junction dots on usb and power, in eeschema.
3. **M-003.** Components.txt lists GCT USB4135-GF-A, which is power-only. Change it to USB4105-GF-A, matching the J1 footprint.
4. Update `project_power_design` notes. The Orchestrator updates memory.
