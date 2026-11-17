# MANUAL_ACTIONS: Step 4 round 3

## M-S4-001 (from P-S4-001, P-S4-003, P-S4-004) — PCB re-sync after Step 4 schematic changes
- Why blocked: the PCB is out of scope in this round, and it is open and locked by its editor. This extends M-S3-003.
- Do this: when you are ready for layout, run Tools → Update PCB from Schematic. It brings in J5 (PinHeader_1x08), R36 and R37 (0402), the new nets (I2C1_SCL/SDA, USART2_TX/RX, PA0_WKUP), and the D±/UD± split on R21/R22. Place J5 on the isolated side, away from the barrier.
- After you're done I will: re-run netlist/PCB parity and DRC in the next round.

## M-S4-002 (from P-S4-003, P-S4-004) — tidy field/text overlaps around J5 and R36/R37
- Why blocked: by user preference, cosmetic text placement is tidied by hand. The MCP's auto field placement for power-symbol values (and for the rotated #PWR0126) is not reliable.
- Do this: in Eeschema, nudge the overlapping texts listed in FIX_LOG (re-run section). These are around J5 (#PWR0125/0126/0127 values, the J5 ref), around R36/R37 (the +3V3 values on the bodies, the 4.7k value against R37), and the U1-side labels at pins 14/16/17/58/59. Also the vertical #PWR0126 "GND" value on the J5.2 wire, the UD+ label crowding VDD1_ISO1 on usb, and optionally the redundant junction at stm32 (160.02, 147.32) (N-1). Save once and close. This also normalises the float noise.
- After you're done I will: re-run ERC and the netlist to confirm there is no connectivity change.

## M-S4-003 (from P-S4-003, P-S4-004) — Name pre-check false positive blocked J5 and the I2C pull-ups — **RESOLVED 2026-11-17** (pre-check amended, both fixes applied)
- **Why blocked:** the plain-text grep matched U1's cached pin-function alternates (I2C1_SCL, USART2_TX, …), not real labels or nets.
  - A label-type grep returns 0, and so does a netlist search; both were confirmed by the Orchestrator.
  - Apply rules require BLOCKED on any pre-check failure, so nothing was written.
- **Do this:** approve this corrected pre-check: `grep -cE '\((label|global_label|hierarchical_label) "(I2C1_SCL|I2C1_SDA|USART2_TX|USART2_RX|PA0_WKUP)"' hardware/EEG_Kicad_Project/*.kicad_sch` == 0 on every sheet, and no such net names in the current netlist. Then re-run P-S4-003 → P-S4-004 only.
- **After you're done I will:**
  - Apply P-S4-003 and P-S4-004 and expect ERC 6 → 1.
  - Expect these nets:
    - I2C1_SCL = {J5.3, R36.2, U1.58}
    - I2C1_SDA = {J5.4, R37.2, U1.59}
    - USART2_TX = {J5.5, U1.16}
    - USART2_RX = {J5.6, U1.17}
    - PA0_WKUP = {J5.7, U1.14}
  - Expect +3V3 to have 35 nodes, GND 87, and 137 comps in total.
