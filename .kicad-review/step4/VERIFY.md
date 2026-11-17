# VERIFY: Step 4 round 3, iteration 1 (schematic scope)

Fresh checks against the baseline `ac94ad0`. I did not modify any design file or the PCB. Outputs are in `analysis/iter-1/`; the base outputs are in `scratchpad/verify4/base/`.

## Counts

| Metric | Base (ac94ad0) | Now |
|---|---|---|
| ERC total | 35 | **1** |
| – pin_not_connected | 32 | 0 |
| – global_label_dangling | 2 | 0 |
| – multiple_net_names (intentional GND/GNDA) | 1 | 1 |
| Components | 134 | 137 (+J5, R36, R37) |
| Nets | 126 | 126 (5 single-pin U1 nets became the 5 J5 nets) |
| +3V3 / GND nodes | 32 / 85 | 35 / 87 |
| no_connect flags, stm32 / total | 0 / 8 | 27 / 35 |
| Duplicate refs / parts without a footprint | 0 / 0 | 0 / 0 |
| Analyzer findings (error / warning / info) | 105 (1/35/69) | 73 (1/2/70) |
| Analyzer NT-001 (single-pin net) | 34 | 0 |
| Wires crossing symbols, stm32 / usb | — | 2 (D1/D2, known from base) / 0 |
| Orphaned wires / floating labels | — | 0 / 0 |

- **Netlist diff.** Every change is on the approved list:
  - D± now connects only J1 and U8.1/3. UD± connects R22.1/R21.1 with U8.6/4.
  - The 5 J5 nets are exact.
  - +3V3 gained J5.1, R36.1 and R37.1. GND gained J5.2 and J5.8.
  - J5, R36 and R37 are new, with LCSC/MPN fields.
  - power, analog_in and root are byte-identical to the base.
- **Isolation barrier is intact.** The primary side closes on +5V_PRI, GND_PRI, D±, UD±, VDD1_ISO1, CC1/2 and U9-UD±. Only U7 and U9 straddle the barrier, and J5, R36 and R37 are on the isolated side only.

## Verdicts

- **P-S4-001: PASS.**
  - The D±/UD± split is exact.
  - The new UD± labels have shape input.
  - The U8 pairing (1↔6 and 3↔4) is confirmed.
  - global_label_dangling went from 2 to 0.
- **P-S4-002: PASS.** The note is gone, and only that one text was removed.
- **P-S4-003: PASS.**
  - The J5 pin order is correct and all 5 nets are exact.
  - The #PWR0126 GND symbol points away from the J5 body.
  - pin_not_connected cleared on U1 pins 14/16/17/58/59.
- **P-S4-004: PASS.**
  - I2C nets include R36/R37, which sit on +3V3.
  - The analyzer's I2C check passes: 100/400 kHz rise time is about 60 ns.
- **P-S4-005: PASS.** The WARNING text reads "J2/J3/J5"; the rest is unchanged.
- **P-S4-006: PASS.**
  - Exactly 27 no-connects, at the planned pins.
  - The J5 pins are not flagged.

## Analyzer

- **F-014 resolved:** NT-001 went from 34 to 0.
- **F-015 resolved:** the UD± single-pin items are gone.
- **USB checks:** dp/dm_series_resistor changed from pass to info. The checker only looks for series resistors on J1's D± nets, and R21/R22 now sit behind U8 by design.
- **I2C:** pull-ups pass. A `vol_compatibility` "max 67 Ω" note is an analyzer miscalculation: 4.7k at 3.3 V sinks only about 0.7 mA.
- **EP-AUD:** a new info item says J5 has no ESD protection (N-2).

## New findings

- **N-1 [INFO/LOW]:** an unplanned junction at stm32 (160.02, 147.32), on U1's stacked VSS pins. It came in with P-S4-003 (an MCP auto-junction). Connectivity is unchanged. Optional: delete it by hand.
- **N-2 [INFO]:** J5's signals have no ESD protection. J5 is a patient-side internal expansion header, and the warning text covers it.
- **N-3 [INFO]:** tooling notes. validate_schematic's kicad-cli step uses `sch upgrade`, which kicad-cli 9.0.9 doesn't have. The no-connect coordinates carry float noise, but ERC confirms they attach.

## Overlaps not in M-S4-002 (cosmetic)

- The U1-side labels PA0_WKUP, USART2_TX and USART2_RX butt against pin numbers 14/16/17.
- The #PWR0126 "GND" value is drawn vertically over the J5.2 wire.
- usb: the UD+ label crowds the VDD1_ISO1 label.

**Result: 6 PASS, 0 FAIL, 0 REGRESSION.**
