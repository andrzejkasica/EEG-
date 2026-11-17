# KiCad Review Loop: Step 4 (round 3, schematic scope)

- Base `ac94ad0` → working tree. Run on 2026-11-17.
- 1 iteration, with a re-run of 003/004 after a false-positive pre-check (M-S4-003, resolved).

| Metric | Base | Final |
|---|---|---|
| ERC | 35 | **1** (intentional GND/GNDA) |
| Components | 134 | 137 |
| Isolation barrier | intact | intact |

| Fix | Change | Result |
|---|---|---|
| P-S4-001 (F-015) | D±→UD± labels at R22/R21, so USB runs J1 → U8 flow-through → R21/R22 → U9 | PASS |
| P-S4-002 | Removed the user's "Not UD+ UD-…" note | PASS |
| P-S4-003 | J5 1×8 expansion header: 3V3, GND, I2C1 SCL/SDA, USART2 TX/RX, PA0 WKUP, GND | PASS |
| P-S4-004 | R36/R37 4.7k I2C pull-ups to 3V3 | PASS |
| P-S4-005 | Warning text now covers J2/J3/J5 | PASS |
| P-S4-006 (F-014) | 27 no-connects on the spare U1 pins | PASS |

New info items:
- N-1: a redundant junction.
- N-2: J5 has no ESD protection (it is a patient-side internal header).
- N-3: tooling notes.

## Manual actions
1. **M-S4-002, before commit:** tidy the text overlaps around J5, R36/R37, the U1 pins 14/16/17/58/59 labels and the usb UD+ label, then save once in Eeschema and close.
2. **M-S4-001, at layout:** run Update PCB from Schematic (F8).

## Firmware notes
- Disable USB VBUS sensing, because PA9 is not connected.
- Set all no-connect pins to analog mode.
- Pin functions: PB6/PB7 are I2C1 (AF4, open-drain), PA2/PA3 are USART2 (AF7), and PA0 is WKUP.
