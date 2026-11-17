# FIX_PLAN: iteration 1, Fixer PLAN mode (schematic only)

Scope: F-001 to F-010. Nothing in the design was changed while writing this plan; every check was read-only.
Sheet directory: `/home/andrzej/Documents/Repos/EEG-/hardware/EEG_Kicad_Project/` (written below as `<P>/`).

## Global rules for the EXECUTE phase

- **Lock check.** Before every fix, confirm `<P>/~EEG_Kicad_Project.kicad_sch.lck` does not exist. It was absent at plan time. If it exists, stop and ask the user.
- **"Snapshot".** Before each fix, `cp` the sheet(s) that fix touches to `.kicad-review/snapshots/P-0xx/`. Rollback means copying them back. Do not use `mcp__kicad__snapshot_project`, because it renders the PCB.
- **Coordinates.** All coordinates are sheet mm. New parts sit on the 1.27 mm grid. Device:C and Device:R pins are at ±3.81 mm in Y when angle = 0 (pin 1 on top).
- **Footprint conventions (from existing parts):**
  - 100 nF: `Capacitor_SMD:C_0402_1005Metric` (C30, C2–C8)
  - 4.7 µF 0805: `Capacitor_SMD:C_0805_2012Metric` (C41)
  - R 0402: `Resistor_SMD:R_0402_1005Metric_Pad0.72x0.64mm_HandSolder` (R1, R2, R7–R20)
- **Value style:** "100n", "4.7u", "24".
- **Primary-side power symbols.** The project uses `power:+5V` with Value `+5V_PRI` and `power:GND` with Value `GND_PRI` (#PWR046 and #PWR047 on usb; power-sheet symbols at (34.29,162.56) and (34.29,179.07)). Every new `power:+5V` / `power:GND` placed for a PRI net must have its Value changed **immediately** with `set_schematic_component_property name=Value`. If the Value is left at its default, the part lands on isolated +5V / GND, which shorts the isolation barrier in the netlist.
- **New designators.** The highest existing ones are C49 and R20. The plan uses C50–C54 and R21–R24. R3–R6 are deleted and are not reused.
- **Junctions.** The MCP server has no junction-delete tool. Junctions left with only 2 wires after a deletion are harmless cosmetic leftovers; they are listed in M-002.
- **Verification after each fix:**
  1. `kicad-cli sch export netlist`, then compare the listed nodes.
  2. `kicad-cli sch erc`: no new errors.
  3. Check that `+5V` and `+5V_PRI` are still separate nets, and that `GND` and `GND_PRI` are still separate nets.

# Schematic changes

## F-001 → P-001  [x] APPROVE   [ ] SKIP   [ ] MANUAL
U9 VDD1, PDEN and SPU move to a new local net `VDD1_ISO1`. VBUS1 stays on `+5V_PRI`. Adds C50 100n to GND_PRI. Sheet: `<P>/usb.kicad_sch`.

Current wiring (from the file):
- The +5V_PRI drop is #PWR050 at (218.44,36.83). Wires 4e5addec (218.44,36.83→40.64) and 49275d79 (218.44,40.64→43.18) run to U9.1 VBUS1, with a junction at (218.44,40.64).
- Wire 7dd3ce25 (199.39,40.64)→(218.44,40.64) and wire bf368793 (199.39,48.26)→(199.39,40.64) tie the VDD1 column to +5V_PRI.
- The VDD1 column is:
  - 0fe28947 (199.39,48.26)→(208.28,48.26), to U9.3
  - a1ec0623 (199.39,60.96)→(199.39,48.26)
  - f5ababb4 (199.39,60.96)→(208.28,60.96), to U9.4
  - cf286b22 (199.39,63.5)→(199.39,60.96)
  - b50a5be0 (208.28,63.5)→(199.39,63.5), to U9.5
  - junctions at (199.39,48.26) and (199.39,60.96)

- Actions (in order):
  1. `mcp__kicad__delete_schematic_wire` schematicPath=`<P>/usb.kicad_sch` start={x:199.39,y:40.64} end={x:218.44,y:40.64}   ⚠ DESTRUCTIVE (uuid 7dd3ce25)
  2. `mcp__kicad__delete_schematic_wire` schematicPath=`<P>/usb.kicad_sch` start={x:199.39,y:48.26} end={x:199.39,y:40.64}   ⚠ DESTRUCTIVE (uuid bf368793)
  3. `mcp__kicad__add_schematic_component` schematicPath=`<P>/usb.kicad_sch` symbol=`Device:C` reference=`C50` value=`100n` footprint=`Capacitor_SMD:C_0402_1005Metric` position={x:190.5,y:52.07} angle=0. Pin 1 lands at (190.5,48.26) and pin 2 at (190.5,55.88).
  4. `mcp__kicad__add_schematic_wire` schematicPath=`<P>/usb.kicad_sch` waypoints=[[190.5,48.26],[199.39,48.26]]. The end lands on the existing junction at (199.39,48.26).
  5. `mcp__kicad__add_schematic_net_label` schematicPath=`<P>/usb.kicad_sch` netName=`VDD1_ISO1` labelType=`label` componentRef=`C50` pinNumber=`1`
  6. `mcp__kicad__add_schematic_component` schematicPath=`<P>/usb.kicad_sch` symbol=`power:GND` reference=`#PWR057` position={x:190.5,y:55.88} angle=0
  7. `mcp__kicad__set_schematic_component_property` schematicPath=`<P>/usb.kicad_sch` reference=`#PWR057` name=`Value` value=`GND_PRI`
- Pre-checks:
  - Lock file absent.
  - `get_schematic_pin_locations U9` still gives pin 3 at (208.28,48.26), pin 4 at (208.28,60.96), pin 5 at (208.28,63.5), pin 1 at (218.44,43.18).
  - The region x 186–198, y 44–62 is empty. It was empty at plan time.
  - #PWR057 is free. The highest #PWR on usb is #PWR056; check across all sheets and use the next free number.
- Expected netlist:
  - `VDD1_ISO1` (path-prefixed, e.g. `/USB/VDD1_ISO1`) = U9.3, U9.4, U9.5, C50.1
  - `+5V_PRI` still contains U9.1, but no longer U9.3, U9.4 or U9.5
  - C50.2 is on `GND_PRI`
- Notes:
  - The junction at (218.44,40.64) is left with 2 collinear wires. This is cosmetic only (M-002).
  - The user should correct the memory note `project_power_design.md` afterwards.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred to end of Task 2 per STATE)

## F-002 → P-002  [ ] APPROVE   [ ] SKIP   [x] MANUAL   — ON HOLD 2026-11-17: TRN 3-0511 rejected (9 V-nominal input, thin margin at USB 5 V); find a 5 V-nominal regulated part in Task 3 (see M-001)
Replace U7 TMU3-0511 (unregulated) with a regulated isolated 5 V-in / 5 V-out module. Sheet: `<P>/power.kicad_sch`. U7 is at (48.26,170.18).

Current U7 pins and wires:
- −Vin (38.1,172.72): wire to (34.29,172.72), then down to GND_PRI at (34.29,179.07)
- +Vin (38.1,167.64): wire to (34.29,167.64), then up to +5V_PRI at (34.29,162.56)
- +Vout (58.42,167.64): wire to (63.5,167.64), then up to +5V
- −Vout (58.42,172.72): wire to (63.5,172.72), then down to GND

Candidates. All are regulated, and all have a stock KiCad symbol and footprint (checked in the KiCad 9 libraries). Isolation, current and input-range figures come from the KiCad library descriptions. The datasheets were not downloaded; see M-001.

| # | Part | Regulation | Isolation | Iout | Vin range | Package | Symbol / footprint | Pinout vs current U7 | Re-wire needed |
|---|---|---|---|---|---|---|---|---|---|
| A (recommended) | TRACO **TRN 3-0511** (3 W) | regulated | 1.6 kVDC | 600 mA | 4.5–13.2 V | SIP, pads 1/2/3/5 (2.0/2.8/4.0 mm pitch) | `Converter_DCDC:TRN3-0511` / `Converter_DCDC:Converter_DCDC_TRACO_TRN3-xx1x_Single_THT` | Pin positions are **identical** to TMU3 (±Vin at −10.16/±2.54, ±Vout at +10.16/±2.54). Only the numbers change: +Vout 4→3, −Vout 3→5. | **None.** All four existing wires land on the same coordinates. |
| B | TRACO **TEC 2-1211WI** (2 W) | regulated | 1.6 kVDC | 400 mA | 4.5–18 V | SIP-8 | `Converter_DCDC:TEC2-1211WI` / `Converter_DCDC:Converter_DCDC_TRACO_TEC2-12xxWI_24xxWI_48xxWI_THT` | ±Vin and ±Vout at the same coordinates (pins 1, 2, 6, 7). Extra pin 3 "Remote" (input) lands at (38.1,170.18). Pins 5 and 8 are NC (no_connect type). | Remote pin: add a no-connect flag at (38.1,170.18). This assumes "open = ON", which is **not verified**; check the datasheet. |
| C | XP Power **ITX0505SA-H** (6 W) | fully regulated | 3 kVDC | 1200 mA | about 4.5–9 V (verify) | SIP-8 | `Converter_DCDC:ITX0505SA-H` / `Converter_DCDC:Converter_DCDC_XP_POWER-ITXxxxxSA_THT` | ±Vin and ±Vout at the same coordinates (pins 1, 2, 6, 7). Pin 8 NC is internal. | None. It is oversized: higher no-load input current, bigger, and more expensive. |

- **Excluded as unregulated:** TMU3, TMA, TME, TEA1, TMV, TRI1-0511, Murata NXE1/NXE2/MEE1/MEE3/CRE1, and RECOM R1SX.
- **Not in the stock libraries:** TRACO TMR 1-0511 (only a footprint exists) and RECOM REM (medical 2×MOPP). These would need a custom symbol.
- **Medical-grade isolation.** None of A–C is medical-grade (2×MOPP). The plan states there is no medical certification target. If that changes, look at RECOM REM1/REM3-0505S, which needs a custom symbol.

- **Recommendation: A, TRN3-0511.**
  - It comes from the same vendor family as the current part.
  - It drops in with zero re-wiring.
  - It gives 600 mA of margin over the roughly 200 mA STM32 USB-active load noted in Components.txt.
  - Its 1.6 kVDC rating meets the 1.5 kV requirement.
- Actions (in order, for candidate A):
  1. `mcp__kicad__replace_schematic_component` schematicPath=`<P>/power.kicad_sch` reference=`U7` newSymbol=`Converter_DCDC:TRN3-0511`   ⚠ DESTRUCTIVE (symbol swap)
  2. `mcp__kicad__set_schematic_component_property` schematicPath=`<P>/power.kicad_sch` reference=`U7` name=`Value` value=`TRN3-0511`
  3. `mcp__kicad__set_schematic_component_property` … reference=`U7` name=`Footprint` value=`Converter_DCDC:Converter_DCDC_TRACO_TRN3-xx1x_Single_THT`
  4. `mcp__kicad__set_schematic_component_property` … reference=`U7` name=`Datasheet` value=`https://www.tracopower.com/products/trn3.pdf`
- Pre-checks:
  - The user has picked A, and the M-001 datasheet checks pass.
  - Lock file absent.
  - After step 1, `get_schematic_pin_locations U7` must return: +Vin (38.1,167.64), −Vin (38.1,172.72), +Vout (58.42,167.64), −Vout (58.42,172.72).
  - Netlist: U7.2 on +5V_PRI, U7.1 on GND_PRI, U7.3 on +5V, U7.5 on GND.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred to end of Task 2 per STATE)

## F-003 → P-003  [x] APPROVE   [ ] SKIP   [ ] MANUAL
Delete R3–R6. They are already flagged DNP in the file, but still sit on the NR pins. Sheet: `<P>/power.kicad_sch`.

- Actions (in order):
  1. `mcp__kicad__delete_schematic_component` schematicPath=`<P>/power.kicad_sch` reference=`R3` deleteAttachedLabels=false   ⚠ DESTRUCTIVE
  2. `mcp__kicad__delete_schematic_component` … reference=`R4`   ⚠ DESTRUCTIVE
  3. `mcp__kicad__delete_schematic_component` … reference=`R5`   ⚠ DESTRUCTIVE
  4. `mcp__kicad__delete_schematic_component` … reference=`R6`   ⚠ DESTRUCTIVE
  5. On the U4 side, delete the wires that are now dangling:
     - `mcp__kicad__delete_schematic_wire` start={217.17,110.49} end={217.17,111.76}   ⚠ DESTRUCTIVE (3df5c3ef, R3.1 stub)
     - `mcp__kicad__delete_schematic_wire` start={217.17,120.65} end={217.17,119.38}   ⚠ DESTRUCTIVE (4600d9dd, R3.2 stub)
     - `mcp__kicad__delete_schematic_wire` start={217.17,121.92} end={217.17,123.19}   ⚠ DESTRUCTIVE (893f7bdf, R4.1 stub)
     - `mcp__kicad__delete_schematic_wire` start={217.17,130.81} end={217.17,132.08}   ⚠ DESTRUCTIVE (b57bd597, R4.2 stub)
     - `mcp__kicad__delete_schematic_wire` start={217.17,132.08} end={224.79,132.08}   ⚠ DESTRUCTIVE (85deed22, R4 GND run)
  6. On the U6 side, delete the wires that are now dangling:
     - `mcp__kicad__delete_schematic_wire` start={76.2,121.92} end={76.2,120.65}   ⚠ DESTRUCTIVE (24b93031, R5.2 stub)
     - `mcp__kicad__delete_schematic_wire` start={76.2,123.19} end={76.2,124.46}   ⚠ DESTRUCTIVE (ba69e456, R6.1 stub)
     - `mcp__kicad__delete_schematic_wire` start={76.2,132.08} end={76.2,133.35}   ⚠ DESTRUCTIVE (bdfe19be, R6.2 stub)
     - `mcp__kicad__delete_schematic_wire` start={76.2,133.35} end={80.01,133.35}   ⚠ DESTRUCTIVE (d118660d, R6 GND run)
  7. `mcp__kicad__find_orphaned_wires` (read-only) on power.kicad_sch: expect none near x 76/217.
- Wires that must be KEPT:
  - **U4 NR → C24:** d99b857b (212.09,113.03→121.92), dc7059d6 (→217.17,121.92), **4ac77fdc** (217.17,121.92→120.65), 18f6e161 (→224.79,120.65), 03d9cc47 (→C24.1 at 224.79,123.19).
  - **C24.2 → GND:** 1e98d1a8 (224.79,130.81→132.08) and 9aae9d88 (→229.87,132.08 junction).
  - **U6 NR → C25:** ab5af432 (71.12,115.57→121.92), 25aa3e84 (→76.2,121.92), **71d3ebfc** (76.2,121.92→123.19), e83407f6 (→83.82,123.19), 237cf10a (→C25.1 at 83.82,124.46).
  - **C25.2 → GNDA:** 83e786d1, bb413fef, 81d13887.
- **OUT nets are unaffected.**
  - U4 OUT: 6f12226a (212.09→217.17 @110.49) and 17b910cc (217.17→229.87). Only the R3 stub hung off this run.
  - U6 OUT: dcd78bb2 (71.12→76.2 @113.03) and 02d1e26f (76.2→93.98). R5 pin 1 sat directly on the junction, with no stub wire.
- Pre-checks:
  - Lock file absent.
  - If `delete_schematic_component` already removes attached wires, the matching delete_wire calls fail harmlessly; confirm with `list_schematic_wires`.
- Expected netlist:
  - `Net-(U4-NR)` = C24.1, U4.4 only.
  - `Net-(U6-NR)` = C25.1, U6.4 only.
  - The U4 and U6 OUT nets keep the same members, minus R3 and R5.
  - No new ERC errors.
- Notes: stray 2-wire junctions are left at (217.17,110.49), (217.17,120.65), (217.17,121.92), (224.79,132.08), (76.2,113.03), (76.2,121.92), (76.2,123.19) and (80.01,133.35). These are cosmetic (M-002).
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred to end of Task 2 per STATE)

## F-004 → P-004  [x] APPROVE   [ ] SKIP   [ ] MANUAL
Assign footprints. R3–R6 are covered by F-003.

- Actions (in order):
  1. `mcp__kicad__set_schematic_component_property` schematicPath=`<P>/power.kicad_sch` reference=`L1` name=`Footprint` value=`Inductor_SMD:L_0805_2012Metric`
  2. Same call for `L2`.
  3. Same call for `L3`.
  4. Same call for `L4`.
  5. `mcp__kicad__set_schematic_component_property` schematicPath=`<P>/usb.kicad_sch` reference=`J1` name=`Footprint` value=`Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`
  6. `mcp__kicad__set_schematic_component_property` schematicPath=`<P>/stm32.kicad_sch` reference=`SW1` name=`Footprint` value=`Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A`
- **J1 pad check.**
  - The symbol is `Connector:USB_C_Receptacle_USB2.0_14P`. Its pin numbers are A1, A4, A5, A6, A7, A9, A12, B1, B4, B5, B6, B7, B9, B12 and S1.
  - The USB4105 footprint has pads A1, A4, A5, A6, A7, A8, A9, A12, B1, B4, B5, B6, B7, B8, B9, B12 and S1 (×4).
  - **All 15 symbol pin numbers exist on the footprint; there are no mismatches.**
  - Pads A8 and B8 (SBU1/SBU2) have no symbol pin and stay unconnected (no net). This is acceptable for USB 2.0. Optionally, swap to `Connector:USB_C_Receptacle_USB2.0_16P` plus no-connects so the footprint and symbol pin counts match. That swap is not included in this plan.
  - **Important:** `USB_C_Receptacle_GCT_USB4135-GF-A_6P` is a power-only receptacle (pads A5, A9, A12, B5, B9, B12 and S1; no D+/D−), so it **cannot** be used. The Components.txt entry "GCT USB4135-GF-A" is wrong for a data port; see M-003. The alternative `Connector_USB:USB_C_Receptacle_Amphenol_12401610E4-2A` (24 pads, superset) also matches all 15 pins.
- **SW1:** the `Switch:SW_Push` pins are 1 and 2. TS-1187A (5.1×5.1 mm SMD) has pads 1,1 and 2,2, so it matches. The alternative is `Button_Switch_SMD:SW_SPST_TL3342` (pads 1/2, also matches). The claim that TS-1187A is a JLCPCB basic part was not verified.
- **L1–L4:** the `Device:L` pins are 1 and 2, which match the 0805 pads. The TDK MLZ2012A3R3WT current rating against the converter/LDO current was not re-checked.
- Pre-checks: lock file absent; each footprint exists (verified at plan time in the KiCad 9 stock libraries).
- Expected: the netlist `<footprint>` field is filled for L1–L4, J1 and SW1, and no symbol is left without a footprint (once F-003 has run).
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred to end of Task 2 per STATE)

## F-005 → P-005  [x] APPROVE   [ ] SKIP   [ ] MANUAL
Add four 24 Ω 1 % 0402 series resistors on U9 UD± and DD±. Sheet: `<P>/usb.kicad_sch`.

- **Method.** This is non-destructive. Each global label is moved 7.62 mm up its existing vertical stub, and a vertical resistor is placed in the gap: pin 2 lands on the old label point (on the existing wire end) and pin 1 on the new label point.
- **Run after P-001.** P-001 clears the +5V_PRI wire at y = 40.64 that would otherwise sit under the moved D+/D− labels.
- Actions (in order):
  1. `mcp__kicad__move_schematic_net_label` schematicPath=`<P>/usb.kicad_sch` netName=`D-` labelType=`global_label` currentPosition={201.93,54.61} newPosition={201.93,46.99}
  2. `mcp__kicad__move_schematic_net_label` … netName=`D+` labelType=`global_label` currentPosition={205.74,54.61} newPosition={205.74,46.99}
  3. `mcp__kicad__move_schematic_net_label` … netName=`USB_OTG_FS_DP` currentPosition={245.11,54.61} newPosition={245.11,46.99}
  4. `mcp__kicad__move_schematic_net_label` … netName=`USB_OTG_FS_DM` currentPosition={250.19,54.61} newPosition={250.19,46.99}
  5. `mcp__kicad__add_schematic_component` symbol=`Device:R` reference=`R21` value=`24` footprint=`Resistor_SMD:R_0402_1005Metric_Pad0.72x0.64mm_HandSolder` position={201.93,50.8} angle=0 (U9 UD−; pins at (201.93,46.99) and (201.93,54.61))
  6. `mcp__kicad__add_schematic_component` … reference=`R22` value=`24` (same footprint) position={205.74,50.8} angle=0 (U9 UD+)
  7. `mcp__kicad__add_schematic_component` … reference=`R23` value=`24` (same footprint) position={245.11,50.8} angle=0 (U9 DD+ to PA12)
  8. `mcp__kicad__add_schematic_component` … reference=`R24` value=`24` (same footprint) position={250.19,50.8} angle=0 (U9 DD− to PA11)
  9. For each Rn in {R21: x=201.93, R22: 205.74, R23: 245.11, R24: 250.19}:
     - `mcp__kicad__set_schematic_component_property` reference=Rn name=`Reference` value=Rn x=(x+1.905) y=50.8 angle=90 hide=false
     - `mcp__kicad__set_schematic_component_property` reference=Rn name=`Value` value=`24` hide=true

     Reason: there is only 3.81 mm between R21 and R22, so the fields are drawn vertically and the value text is hidden.
  10. `mcp__kicad__set_schematic_component_property` for R21–R24 name=`Tolerance` value=`1%`
  11. `mcp__kicad__add_schematic_text` schematicPath=`<P>/usb.kicad_sch` text=`R21-R24: 24R 1% 0402, ADuM3160 full-speed series termination (UD+/UD-, DD+/DD-). Place close to U9.` position=[200.66,120.65]
- Pre-checks:
  - Lock file absent.
  - P-001 is done.
  - Each label is exactly at its currentPosition, and the wire stubs ffd8164b, 0ba7d700, af7d0286 and 25eda688 still end at y = 54.61.
  - x = 199.39 (VDD1 column) and x = 240.03 (VDD2 column) are not crossed by any resistor body.
- Expected netlist:
  - `D-` = J1.A7/B7, U8.3, R21.1; new net Net-(U9-UD-) = R21.2, U9.6
  - `D+` = J1.A6/B6, U8.1, R22.1; new net Net-(U9-UD+) = R22.2, U9.7
  - `USB_OTG_FS_DP` = R23.1, U1 PA12; Net-(U9-DD+) = R23.2, U9.10
  - `USB_OTG_FS_DM` = R24.1, U1 PA11; Net-(U9-DD-) = R24.2, U9.11
- **Interaction with F-015 (not fixed here).** F-015 wants U9 fed from U8's pass-through (`UD+`/`UD-` labels at U8.6/U8.4) instead of `D+`/`D-`. After P-005, that fix becomes simply renaming the two moved labels at (201.93,46.99) and (205.74,46.99) from `D-`/`D+` to `UD-`/`UD+`. The resistors stay between the label and U9, which is the correct place. Do not rename them in this pass.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred to end of Task 2 per STATE)

## F-006 → P-006  [x] APPROVE   [ ] SKIP   [ ] MANUAL
Add U9 VBUS1 and VBUS2/VDD2 bypass caps. The VDD1 cap is C50 in P-001. Sheet: `<P>/usb.kicad_sch`. They go in a free area below U9; U9's GND symbol text ends around y = 85.

- Actions (in order):
  1. `mcp__kicad__add_schematic_component` symbol=`Device:C` reference=`C51` value=`100n` footprint=`Capacitor_SMD:C_0402_1005Metric` position={209.55,100.33} angle=0 (pins at (209.55,96.52) and (209.55,104.14))
  2. `mcp__kicad__add_schematic_component` symbol=`power:+5V` reference=`#PWR058` position={209.55,96.52} angle=0
  3. `mcp__kicad__set_schematic_component_property` reference=`#PWR058` name=`Value` value=`+5V_PRI`  (mandatory)
  4. `mcp__kicad__add_schematic_component` symbol=`power:GND` reference=`#PWR059` position={209.55,104.14} angle=0
  5. `mcp__kicad__set_schematic_component_property` reference=`#PWR059` name=`Value` value=`GND_PRI`  (mandatory)
  6. `mcp__kicad__add_schematic_component` symbol=`Device:C` reference=`C52` value=`100n` footprint=`Capacitor_SMD:C_0402_1005Metric` position={232.41,100.33} angle=0 (pins at (232.41,96.52) and (232.41,104.14))
  7. `mcp__kicad__add_schematic_component` symbol=`power:+3V3` reference=`#PWR060` position={232.41,96.52} angle=0
  8. `mcp__kicad__add_schematic_component` symbol=`power:GND` reference=`#PWR061` position={232.41,104.14} angle=0. The Value stays `GND` (isolated side).
  9. `mcp__kicad__add_schematic_text` text=`C50 (VDD1), C51 (VBUS1), C52 (VBUS2/VDD2): ADuM3160 bypass - place <=10 mm from U9` position=[200.66,115.57]
- Pre-checks:
  - Lock file absent.
  - The #PWR numbers are free across all sheets; renumber if needed.
  - The region x 200–240, y 92–122 is empty.
- Expected netlist:
  - C51.1 on `+5V_PRI` and C51.2 on `GND_PRI`
  - C52.1 on `+3V3` and C52.2 on `GND`
  - `+5V_PRI` and `+5V` are still separate; `GND_PRI` and `GND` are still separate
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred to end of Task 2 per STATE)

## F-007 → P-007  [x] APPROVE   [ ] SKIP   [ ] MANUAL
Add a 4.7 µF X5R 0805 bulk cap on +5V_PRI/GND_PRI at the U7 input. Sheet: `<P>/power.kicad_sch`, in the free area left of U7.

- Actions (in order):
  1. `mcp__kicad__add_schematic_component` symbol=`Device:C` reference=`C53` value=`4.7u` footprint=`Capacitor_SMD:C_0805_2012Metric` position={24.13,170.18} angle=0 (pins at (24.13,166.37) and (24.13,173.99))
  2. `mcp__kicad__add_schematic_component` symbol=`power:+5V` reference=`#PWR062` position={24.13,166.37} angle=0
  3. `mcp__kicad__set_schematic_component_property` reference=`#PWR062` name=`Value` value=`+5V_PRI`  (mandatory)
  4. `mcp__kicad__add_schematic_component` symbol=`power:GND` reference=`#PWR063` position={24.13,173.99} angle=0
  5. `mcp__kicad__set_schematic_component_property` reference=`#PWR063` name=`Value` value=`GND_PRI`  (mandatory)
  6. `mcp__kicad__set_schematic_component_property` reference=`C53` name=`Dielectric` value=`X5R` (and name=`Voltage` value=`10V`)
- Pre-checks:
  - Lock file absent.
  - x 18–30, y 160–180 is empty, and the left sheet border is at about x = 12.5.
  - **Total VBUS capacitance:** C30 0.1 µF + C51 0.1 µF + C53 4.7 µF = 4.9 µF, which is within the 10 µF limit. If the chosen converter's datasheet asks for an input cap (M-001), it must fit inside this same budget.
- Expected: `+5V_PRI` members are J1 VBUS, U8.5, U9.1, C30, C51, C53, U7 +Vin, plus the PWR_FLAGs.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred to end of Task 2 per STATE)

## F-008 → P-008  [x] APPROVE   [ ] SKIP   [ ] MANUAL
Add the patient-side warning text near J2 and J3. Sheet: `<P>/stm32.kicad_sch`. J3 is at (266.7,63.5) and J2 at (266.7,88.9). The area above J3 is empty.

- Actions (in order):
  1. `mcp__kicad__add_schematic_text` schematicPath=`<P>/stm32.kicad_sch` position=[205.74,27.94] fontSize=1.27 bold=true text=`WARNING: J2/J3 are on the isolated (patient) side.\nConnecting a mains-powered PC/debugger bypasses\nthe USB isolation barrier. Use only with no electrodes\non a person, or via a USB isolator.`

  The wording is exactly as in FINDINGS; only line breaks were added so the text stays within x 205–265.
- Pre-checks:
  - Lock file absent.
  - Nothing occupies x 200–285, y 25–40.
  - The text must not run past the sheet border at about x = 285. If bold widens it too much, use bold=false.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred to end of Task 2 per STATE)

## F-009 → P-009  [x] APPROVE   [ ] SKIP   [ ] MANUAL
Add the Y1 spec properties and set the C48/C49 dielectric in their value. No 0 Ω on OSC_OUT. Sheet: `<P>/stm32.kicad_sch`.

- Actions (in order):
  1. `mcp__kicad__set_schematic_component_property` schematicPath=`<P>/stm32.kicad_sch` reference=`Y1` name=`CL` value=`12pF`
  2. `mcp__kicad__set_schematic_component_property` … reference=`Y1` name=`ESR` value=`<=60R`
  3. `mcp__kicad__set_schematic_component_property` … reference=`Y1` name=`C0` value=`<=3pF`
  4. `mcp__kicad__set_schematic_component_property` … reference=`Y1` name=`Package` value=`3225`
  5. `mcp__kicad__set_schematic_component_property` … reference=`C48` name=`Value` value=`15p C0G`
  6. `mcp__kicad__set_schematic_component_property` … reference=`C49` name=`Value` value=`15p C0G`
- Pre-checks:
  - Lock file absent.
  - The Y1 footprint is already `Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm`, which is consistent with Package 3225.
  - The new properties are created hidden by default.
- Note: a Value of "15p C0G" may confuse value parsers. The kicad-happy XL-DET check may not parse 15 pF from it; the Verifier should check this. If it does, also add a `Dielectric=C0G` property (that addition is not in this plan).
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred to end of Task 2 per STATE)

## F-010 → P-010  [x] APPROVE   [ ] SKIP   [ ] MANUAL
Add a 4.7 µF bulk cap on +3V3 next to the U1 decoupling bank. Sheet: `<P>/stm32.kicad_sch`.

The existing bank is C8, C6, C5, C4, C3, C2 and C1 at x = 20.32…88.9 (11.43 mm pitch), y = 48.26. The rails are at y = 40.64 and 53.34. The next slot is x = 100.33. Power symbols are used instead of extending the rails, which avoids T-junctions; the MCP server has no add-junction tool.

- Actions (in order):
  1. `mcp__kicad__add_schematic_component` symbol=`Device:C` reference=`C54` value=`4.7u` footprint=`Capacitor_SMD:C_0805_2012Metric` position={100.33,48.26} angle=0 (pins at (100.33,44.45) and (100.33,52.07))
  2. `mcp__kicad__add_schematic_component` symbol=`power:+3V3` reference=`#PWR064` position={100.33,44.45} angle=0
  3. `mcp__kicad__add_schematic_component` symbol=`power:GND` reference=`#PWR065` position={100.33,52.07} angle=0
  4. `mcp__kicad__set_schematic_component_property` reference=`C54` name=`Dielectric` value=`X5R`
- Pre-checks:
  - Lock file absent.
  - x 95–110, y 35–60 is empty.
  - The #PWR numbers are free.
- Expected: C54.1 is on `+3V3` and C54.2 is on `GND`. The kicad-happy DO-DET for +3V3 should report a largest cap of 4.7 µF. TLV757P COUT stays well under 200 µF.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred to end of Task 2 per STATE)

## Suggested execution order
P-003 → P-004 → P-001 → P-005 → P-006 → P-007 → P-008 → P-009 → P-010 → P-002 (after the user's choice).
