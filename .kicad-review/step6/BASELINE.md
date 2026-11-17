# Baseline: Step 6 whole-schematic deep review (round 5, iteration 1)

- Base `ad3e7bb`, all 5 sheets. Schematic only; no DRC. No schematic lock was present.
- Outputs in `analysis/`: erc.json, netlist.xml, schematic.json, emc.json.

## ERC
- 0 errors.
- 1 warning: multiple_net_names, GND/GNDA (intentional).

## Netlist
- Components: 147 (55 unique; 9 DNP, C64–C72). No duplicate refs, no missing footprint or value.
- Nets: 128. No single-pin nets and no unconnected pins.
- Wires: 342. No-connects: 35.
- Isolation: GND_PRI and +5V_PRI touch only J1, U7 (input side), U8, U9 (side 1), R7, R8, C30, C50, C51 and C53.
- Symbol pins vs footprint pads: all match except J1, whose footprint has pads A8 and B8 (SBU) with no symbol pin (S6-007).

## kicad-happy analyze_schematic
76 findings: 1 error, 3 warning, 72 info.

| Rule | Severity | Count | Disposition |
|---|---|---|---|
| SS-001 | error | 1 | Task 3 gate |
| CG-AUD (J4) | warning | 1 | intentional |
| RS-001 (5V_L1) | warning | 1 | false positive |
| SJ-DET (JP1) | warning | 1 | intentional |
| DO-DET | info | 18 | |
| RC-DET | info | 18 | |
| DC-DET | info | 8 | |
| EP-AUD | info | 5 | |
| PR-DET | info | 5 | |
| PD-DET | info | 4 | |
| LA-AUD | info | 3 | |
| LC-DET | info | 3 | |
| Others | info | 1 each | |

Other analyzer output:
- label_shape_warnings: 4 (USB_OTG_FS_DP/DM mixed shapes; UD± labels set to input on passive nets).
- usb_compliance: 6 pass, 0 fail, 2 info.
- EMC (schematic only): 0 findings from 0 categories checked. Every EMC rule needs the PCB.
- SPICE: not run, because no simulator is installed.

## MCP checks
- validate_schematic: all 5 sheets valid.
- Orphaned wires: 0. Floating labels: 0. lint_offgrid: 0.
- Wires crossing symbols: 3 on stm32 (D1/D2/D4, known false positive).
- Overlapping elements: 5 on stm32 and 3 on analog_in. All are #PWR bounding boxes touching pin ends.
- Duplicate symbols in EEG_custom: 0.

## BOM field coverage (SS-001 is the Task 3 gate)
- MPN on 13/45 unique lines (28.9 %).
- LCSC/MPN on 43/147 components, by sheet:

  | Sheet | Components with LCSC/MPN |
  |---|---|
  | analog_in | 36/65 |
  | stm32 | 5/35 |
  | power | 2/34 |
  | usb | 0/13 |

- Parts with no LCSC/MPN: all ICs U1–U9, J1–J3, SW1, Y1, L1–L4, D1/D2, and the passives from before Step 3.
