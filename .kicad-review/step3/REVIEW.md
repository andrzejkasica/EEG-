# KiCad Review Loop: Step 3 analog front end (round 2, schematic scope)

- **What was reviewed:** the Step 3 wiring on analog_in.kicad_sch, compared against `b3af525`. Spec: `docs/superpowers/plans/2026-11-17-step3-analog-front-end.md`.
- **Date:** 2026-11-17.
- **Iterations:** 1. The Verifier found 5 PASS, 0 FAIL and 0 REGRESSION.

## Summary

| Metric | Before Step 3 (b3af525) | After wiring | Final |
|---|---|---|---|
| ERC violations | 76 | 35 | 35 (the /ANALOG_IN/ sheet has 0) |
| Components | 101 | 125 | 134 (9 of them DNP) |
| Parts without footprint | 0 | 0 | 0 |
| Isolation barrier | intact | intact | intact |

**Findings:** 15 in total (0 critical, 0 high, 2 medium, 7 low, 6 info).

| Status | Findings |
|---|---|
| Fixed and verified | S3-001, S3-002 (schematic part), S3-003, S3-004, S3-005 |
| Spec text corrected | S3-003, S3-009, S3-012 |
| Manual | S3-006 (THT header), S3-007 and overlaps (user tidies), S3-008 (Eeschema save) |
| Info (confirmed fine) | S3-010 (100k BIAS R), S3-011 (TVS), S3-012 (filter), S3-013 (custom symbol), S3-014 (netlist), S3-015 (analyzer false positives) |

## Fixes

| ID | Change | Result |
|---|---|---|
| P-S3-002 | C63 1.5n → 10n C0G (TDK C432938, 100 V, 0603) | PASS |
| P-S3-003 | IN1N–IN8N: 8 no-connect flags removed, tied to SRB1_F | PASS |
| P-S3-004 | C64–C72, 470p C0G 0402 DNP, from CH1–8/SRB1_F to GND | PASS |
| P-S3-005 | LCSC/MPN/Tolerance fields on the 33 new parts | PASS |
| P-S3-001 | Firmware register note on the sheet | PASS |
| P-S3-007 | Cap label tidy | Not applied: the user tidies this by hand |

## Remaining risks

- **Bias-loop stability.** Not yet confirmed: it needs the M-S3-004 bench check at bring-up.
- **Patient fault current on the channel lines.** Medical certification is a non-goal, and the isolation is functional grade only. A rail fault can push about 0.5 mA through the channel lines. Only the BIAS line is limited to IEC levels.
- **TVS parts.** These are second-source clones with only typical leakage specified. Use genuine TI parts if samples are available.

## Manual actions required (see MANUAL_ACTIONS.md)

1. **M-S3-006 + M-S3-002 (before commit):** tidy the text overlaps in Eeschema, then save once and close. The overlaps are:
   - the C55–C62 refs;
   - the C63 value;
   - the GND values and refs/values on C64–C72;
   - the firmware note, which needs to move down about 13 mm.
2. **M-S3-001:** J4 is through-hole. Decide at order time whether to hand-solder it or use JLCPCB THT assembly.
3. **M-S3-003:** update the PCB from the schematic (F8) when layout starts.
4. **M-S3-004:** bench-check the BIASOUT step response with a phantom at bring-up.
5. **M-S3-005:** re-check LCSC stock at order time, especially the 10 nF C0G.
