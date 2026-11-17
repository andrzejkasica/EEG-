# VERIFY: Step 3 round 2, iteration 1 (schematic scope)

I ran fresh checks rather than relying on FIX_LOG. The outputs are in `.kicad-review/step3/analysis/iter-1/` (erc.json, netlist.xml, schematic.json/.txt). I modified no design files, did not touch the PCB, and did not run DRC.

## Counts

| ERC (kicad-cli 9.0.9) | Pre-fix | Now |
|---|---|---|
| error pin_not_connected (/STM32/) | 32 | 32 |
| warning global_label_dangling (/) | 2 | 2 |
| warning multiple_net_names (/POWER_SUPPLY/) | 1 | 1 |
| **Total** | **35** | **35** (identical item multiset) |

| Netlist / analyzer | Pre-fix | Now |
|---|---|---|
| Components | 125 | 134 (+C64–C72) |
| Nets | 134 | 126 (8 single-pin INxN nets absorbed into SRB1_F) |
| Analyzer findings | 98 | 105 (all extra are info) |
| No-connect flags | 16 | 8 |
| DNP parts | 0 | 9 |
| missing_mpn | 119 | 95 (−24 Step-3 refs) |
| missing_footprint | 0 | 0 |
| SS-001 MPN coverage | 0/39 | 7/39 |

## Per fix

- **P-S3-002: PASS.**
  - C63 is "10n C0G", 0603, LCSC C432938, and is not DNP.
  - The bias nets are unchanged: BIASINV = {C63.1, R34.1, U3.61}, BIASOUT = {C63.2, R34.2, R35.2, U3.63}, E_BIAS = {J4.10, R35.1, U12.2}.
- **P-S3-003: PASS.**
  - SRB1_F has 19 nodes: C55–C62.2, R33.2, U3.17, U3.1/3/5/7/9/11/13/15 (IN8N…IN1N, by pinfunction) and C72.1. This is an exact match.
  - The 8 INxN no-connects are gone. The NCs on SRB2, BIASIN, BIASREF and U12 IO3/IO4 remain.
- **P-S3-004: PASS.**
  - Each CHn = {R(24+n).2, C(54+n).1, U3 INnP, C(63+n).1}, for n = 1..8.
  - C64–C72 are 470p C0G 0402, DNP, with pin 2 on GND (GND went 76→85).
  - `kicad-cli sch export bom --exclude-dnp` leaves out C64–C72 (134 → 125 refs).
- **P-S3-005: PASS.**
  - LCSC and MPN are on all 33 refs, and Tolerance is on all 29 R/C. All 95 properties are hidden.
  - SS-001 coverage went 0/39 → 7/39. The plan's figure of "34 refs" was an arithmetic slip; its list totals 33.
- **P-S3-001: PASS.**
  - One 6-line text item, at (20.32, 170.18).
  - It says INxN are tied to SRB1_F and gives REF lead-off via LOFF_SENSN.
  - It gives MISC1=0x20, CONFIG3=0xEC, CHnSET MUX=000/SRB2=0, and BIAS_SENSP ("C63=10n compensated for all 8").
  - It gives lead-off current ≤24 nA.

## Global checks

- **Isolation barrier: intact.** Tracing from +5V_PRI/GND_PRI, with U7 and U9 treated as cut points, reaches only primary-side nets. It reaches no GND, +5V, +3V3, ±2V5 or /ANALOG_IN/ net.
- **Footprints and refs:** all parts have footprints. There are no duplicate refs and no unannotated refs.
- **No collateral changes:** no other component's value or footprint changed.

## S3-002 bias loop

The phase margin can't be checked from the schematic. It is deferred to M-S3-004 (a bench step-response check with a phantom at bring-up). The schematic change (C63 = 10n) is verified above.

## MCP checks (analog_in.kicad_sch)

- No wires cross symbols, no orphaned wires and no floating labels.
- Overlaps: only the 3 from before Step 3 (R16–R18 ↔ #PWR089–091).
- validate_schematic reports 1 `indent_depth_mismatch` (line 12011, the 2-space #PWR0116 block). This is the S3-008 formatting class and is covered by M-S3-002.

## New findings

None.

## Overlap notes

None beyond M-S3-006 items 2–5.

**Result: 5 PASS, 0 FAIL, 0 REGRESSION.**
