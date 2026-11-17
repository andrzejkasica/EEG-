# KiCad Review Loop: Step 5 power sequencing (round 4, schematic scope)

- **Base:** `66f244b`
- **Date:** 2026-11-17
- **Iterations:** 1 (Verifier: 7 PASS, 0 FAIL, 0 REGRESSION)

## Verdict

Power sequencing is safe against ADS1299 §11.1:
- No ADS1299 pin exceeds its abs max during the ramp.
- AVDD − AVSS stays at or below 5.1 V.
- U4 is enabled before U6.
- RESET, PWDN and START are held low by hardware until firmware takes over.
- No supervisor or delayed enable is needed.

The firmware procedure is in `docs/firmware/ads1299-power-up.md`. Its key point is a ~3 s VCAP1 wait until that time is measured.

## Summary

| Metric | Base | Final |
|---|---|---|
| ERC | 1 | 1 |
| Components | 137 | 147 |
| Isolation barrier | intact | intact |

Findings: HIGH 1, MEDIUM 1, LOW 6, INFO 13.
- **S5-001 (HIGH):** folded into F-002. The isolated +5V must stay at or below 5.25 V, the TPS60403 recommended max. Still open, for Task 3.
- **S5-002 (MEDIUM):** covered by the firmware procedure, plus the TP7 test point.
- **S5-003 / S5-008:** the M3 die goes in Task 3 sourcing.
- **S5-004:** fixed.
- **S5-005:** firmware note.
- **S5-006:** bring-up check.
- **S5-007:** fixed.
- **F-011:** closed, intentionally (large NR caps kept for low noise).
- **F-013:** fixed (docs).
- **F-016 and F-017:** fixed.

## Fixes (all PASS)

| Fix | Change |
|---|---|
| P-S5-001 | R38/R39 100k pull-downs on SPI1_SCK/MOSI |
| P-S5-002 | R40 100k pull-down on SPI1_MISO (F-016) |
| P-S5-003 | TP7 on VCAP1 |
| P-S5-004 | TP8 on +5V (isolated) and TP9 on −5V (F-017) |
| P-S5-005 | D3 1N5819WS across U6, anode on IN (−5V) and cathode on OUT, per TI Fig. 7-1 |
| P-S5-006 | R41 0 Ω link: L1 → 5V_L1 / 5V_REG → U2/U4. Fitted; leave it off at first power-up to measure +5V |
| P-S5-007 | D4 yellow-green power LED with R42 1.5k on +3V3, about 1 mA |

## Remaining risks and manual items

- **F-002 / S5-001:** choose a regulated isolated DC-DC whose output stays at or below 5.25 V (Task 3).
- **M-S5-001:** tidy the text overlaps by hand and save once in Eeschema before committing.
- **Bring-up measurements**, listed in the firmware doc:
  - +5V before fitting R41;
  - the VCAP1 time to 1.1 V;
  - the rail ramps and overshoot;
  - U6 at power-down.
- **Task 3 sourcing:**
  - TPS72325 new die (M3);
  - D4 is an Extended part;
  - the BAT54W alternative to D3 is out of stock.
