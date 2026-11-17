# KiCad Review Loop: STATE (round 3, Task 2 Step 4)

- **Phase:** done. Verify 6 PASS, ERC 1. The user did the M-S4-002 tidy and Eeschema save (netlist identical). Committed.
- **Mode:** full loop, **schematic scope only**. Base commit `ac94ad0` (Step 3).
- **Round folder:** `.kicad-review/step4/`. Rounds 1 and 2 are closed.
- **PCB:** out of scope. It is unsynced and locked by its editor. No DRC, and do not touch it.
- **Lock rule:** before any write, check that no `hardware/EEG_Kicad_Project/~*.kicad_sch.lck` exists. The PCB lock is expected.
- **Tooling:**
  - kicad-cli 9.0.9: `sch erc --format json --units mm`, `sch export netlist --format kicadxml`.
  - kicad-happy scripts are in `/home/andrzej/.claude/plugins/marketplaces/kicad-happy/skills/kicad/scripts/`.
  - LCSC search: `python3 -I /home/andrzej/.claude/plugins/cache/kicad-happy/kicad-happy/2.3.2/skills/lcsc/scripts/search_lcsc.py "<q>" --in-stock --limit 5`.
  - The MCP has no tool to delete schematic text, no-connects or junctions. Use a scripted exact-block edit (assert unique), marked ⚠ DESTRUCTIVE.
  - Subagents can't write report .md files; the Orchestrator saves them.
- **Baseline:** ERC 35 = 32 pin_not_connected (/STM32/ U1 spare pins) + 2 global_label_dangling (UD+, UD− on usb) + 1 multiple_net_names (intentional GND/GNDA).

## Work items (user decisions 2026-11-17)
1. **F-015 (round 1): USB data path through U8's flow-through pins.**
   - U8 is USBLC6-2SC6: pins 1 and 6 are I/O1, pins 3 and 4 are I/O2 (internally the same line).
   - Today J1 D+/D− go to U8.1/U8.3. The global labels `UD+` (146.05, 55.88) and `UD−` (146.05, 60.96) sit on U8.6/U8.4 and dangle.
   - U9 is fed from the D± net through R22 (D+) and R21 (D−), whose top-end global labels sit at (205.74, 46.99) "D+" and (201.93, 46.99) "D-" on usb.kicad_sch.
   - **Fix:** rename those two labels to UD+ / UD−. Result: D± = J1 + U8.1/3, and UD± = U8.6/4 + R22.1/R21.1.
   - **Verify** the USBLC6-2SC6 pin pairing (1↔6, 3↔4) from its datasheet; LCSC can fetch it.
2. **Remove the user's note** "Not UD+ UD- TO Isolator instead of D+ D-?" at (205.74, 26.416) on usb.kicad_sch. It is answered by item 1. Use a scripted removal, ⚠ DESTRUCTIVE (approved in principle).
3. **F-014 (round 1) plus a new spare header.** The user chose "spare header + NC rest".
   - Add a 2.54 mm expansion header J5 on stm32.kicad_sch with a proposed pinout: 3V3, GND, PB6 (I2C1_SCL), PB7 (I2C1_SDA), PA2 (USART2_TX), PA3 (USART2_RX), PA0 (WKUP/GPIO), GND (1×8).
   - Propose whether to add I2C pull-ups (e.g. 4.7k to +3V3, possibly DNP), with reasoning.
   - Put no-connect flags on the other unused U1 pins: PA1, PA8, PA9, PA10, PA15, PB2, PB5, PB8, PB9, PB13, PB14, PB15, PC0–PC3, PC6–PC15 and PD2.
   - Firmware notes: VBUS sensing is off (PA9 NC, round-1 F-021); PC14/PC15 are LSE pins and are unused.
   - J5 is on the isolated (patient) side, like J2/J3. Extend the existing J2/J3 warning text, or add a matching note.
   - Add LCSC/MPN fields for the new parts.
- **Target after all items:** ERC 1 (only the intentional multiple_net_names). Isolation barrier intact.

## Approvals (user, 2026-11-17, via chat)
- APPROVED: P-S4-001, P-S4-002, P-S4-003, P-S4-004, P-S4-005, P-S4-006.
- Destructive steps explicitly approved: P-S4-001 (2 label deletes) and P-S4-002 (scripted text removal).
- Cosmetic overlaps: report only; the user tidies them by hand (M-S4-002).
- Order: 001 → 002 → 003 → 004 → 005 → 006.
- **Amendment (user, 2026-11-17):** the P-S4-003 name pre-check is replaced by `grep -cE '\((label|global_label|hierarchical_label) "(I2C1_SCL|I2C1_SDA|USART2_TX|USART2_RX|PA0_WKUP)"' hardware/EEG_Kicad_Project/*.kicad_sch` == 0 on every sheet, plus no such net names in the current netlist. The user approved re-running P-S4-003 → P-S4-004 only.
