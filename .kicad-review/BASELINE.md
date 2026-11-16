# Baseline: Iteration 1 (schematic only)

- Date: 2026-11-16. Branch `task2-schematic-gaps`, HEAD `c348402`.
- Scope: schematic only. No DRC, no PCB analyzer, `.kicad_pcb` not touched.
- Design files were not modified. `git status` after the review shows only the existing PCB change and `.kicad-review/`. `lint_schematic_cosmetic` ran only with `dryRun: true`.

## Artifacts (`.kicad-review/analysis/`)

| File | Source |
|---|---|
| `schematic.json` | kicad-happy `analyze_schematic.py` (`--output`, one-off) |
| `erc.json` | `kicad-cli sch erc --format json --units mm` (KiCad 9.0.9) |
| `netlist.xml` | `kicad-cli sch export netlist --format kicadxml` |
| `emc.json` | kicad-happy `analyze_emc.py --schematic schematic.json --stage schematic` |
| `capability_mode.json` | analyzer side file |

The ERC JSON `pos` values are in units of 100 mm: `1.4605` means 146.05 mm. This was checked against the `UD+` label at (146.05, 55.88) in `usb.kicad_sch`. All coordinates in FINDINGS.md are in mm.

## ERC (kicad-cli = MCP run_erc): 76 violations, 73 errors, 3 warnings

| Sheet | Type | Severity | Count | Disposition |
|---|---|---|---|---|
| `/STM32/` (stm32.kicad_sch) | pin_not_connected (U1 spare GPIO) | error | 32 | F-014 |
| `/ANALOG_IN/` (analog_in.kicad_sch) | pin_not_connected (U3 IN1P-IN8N, BIAS*, SRB1/2) | error | 22 | Known Step 3 work, F-020 |
| `/ANALOG_IN/` | pin_not_driven (same U3 inputs) | error | 19 | Known Step 3 work, F-020 |
| `/` (reported at root; the labels live in usb.kicad_sch) | global_label_dangling `UD+`, `UD-` | warning | 2 | F-015 |
| `/POWER_SUPPLY/` | multiple_net_names, #PWR016 (GND) / #PWR018 (GNDA) | warning | 1 | Known non-issue: intentional GND/GNDA merge. STATE cites #PWR017/#PWR024, which are the same GND/GNDA pair. |
| `/USBC/` | none | | 0 | |

MCP `run_erc` gave the same result: 76 violations (73 errors, 3 warnings).

## kicad-happy schematic analyzer: 106 findings (3 error, 56 warning, 47 info)

- Components: 96 (netlist agrees: 96 refs, no duplicate references). Unique BOM lines: 31. MPN coverage: 0/31.
- Rule counts:
  - NT-001: 54 warnings + 2 info. These are 32 U1 GPIOs, 22 U3 Step 3 pins, and UD+/UD-.
  - VM-001: 2 errors.
  - SS-001: 1 error.
  - UC-004: 1 warning.
  - SJ-DET: 1 warning.
  - Info-level detections: DO-DET 15, DC-DET 6, PR-DET 5, LC-DET 4, EP-AUD 3, LA-AUD 2, and one each of AD-DET, DI-DET, DS-003, IB-DET, LC-007, PD-DET, PS-001, RC-DET, RS-DET, XL-DET.

### Analyzer triage (verified against netlist.xml and datasheets)

| Analyzer claim | Verdict |
|---|---|
| VM-001 D+/D- 5.0 V/3.3 V crossing | **False positive**, known non-issue. Side-1 USB signalling is 3.3 V. The STATE rationale ("UD± on the VDD1 = 5 V side") is itself inaccurate: VDD1 must be 3.3 V. See F-001. |
| SS-001 / DS-003 MPN coverage | Known non-issue (Task 3). |
| DO-DET "Regulator U2/U4/U6 missing capacitors" | **False positive, dropped.** Per the netlist, U2 IN has C11/C12/C17 and OUT has C14/C15. U4 OUT has C18/C19/C21. U6 OUT has C23/C26. The analyzer resolved the wrong unnamed nets. |
| SJ-DET JP1 open between BOOT0 and +3V3 | **False positive, dropped.** It is intentional: R2 pulls BOOT0 low, so the MCU boots from flash. Bridging JP1 selects the bootloader. |
| PS-001 TLV75733P PG unknown | **Dropped.** The TLV757P DBV pinout is IN/GND/EN/NC/OUT, so there is no PG pin (tlv757p_datasheet.pdf, Table 4-1). |
| NT-001 U3 pins | Known Step 3 work, one INFO entry (F-020). |
| NT-001 U1 32 GPIOs | Kept, F-014. |
| NT-001 UD+/UD- | Kept, merged with ERC global_label_dangling (F-015). |
| UC-004 VBUS 0.1 µF | Kept, F-007. |
| XL-DET/DO-DET Y1 CL = 10.5 pF | Kept. Merged into prior finding F-009 (the analyzer assumed X7R because no dielectric is set). |
| EP-AUD J1 partial (CC1/CC2), J2/J3 none | Kept as INFO (F-022). |
| LA-AUD D1/D2 | Merged into prior finding F-012. |
| LC-DET 4 LC filters (~25 kHz) | Info only. They sit well below the TPS60403 switching frequency. No finding. |
| rail_voltages `-2V5` = 2.5, `-5V` = 5.0 | Analyzer quirk (sign lost). Not a design issue. |
| LC-007 lifecycle skipped | No MPNs, deferred to Task 3. |

## MCP tool results (per sheet)

| Tool | root | analog_in | stm32 | power | usb |
|---|---|---|---|---|---|
| validate_schematic | valid (structure). The kicad-cli confirm step failed on a tool bug: it calls `sch upgrade`, which KiCad 9 lacks. | valid | valid | valid | **1 error**: indent/depth mismatch at line 4884 (#FLG06 PWR_FLAG block). Parens balance and kicad-cli loads the file. F-019. |
| find_orphaned_wires | 0 | 0 | 0 | 0 | 0 |
| list_floating_labels | 0 | 0 | 0 | 0 | 0 |
| find_wires_crossing_symbols | n/a | 0 | 2 (D1, D2) | 0 | 0 |
| find_overlapping_elements | n/a | 3 (R16-18 vs #PWR089-091) | 0 | 0 | 0 |
| lint_schematic_cosmetic (dry run) | n/a | 3 pin-name defs, 24 labels | 3 defs, 18 labels | 7 defs, 0 labels | 4 defs, 0 labels |
| find_duplicate_symbols | Not applicable. The tool needs a project `.kicad_sym` library and the project has none (only stock libraries). The netlist shows 96 unique refs, so there are no duplicate references. | | | | |

- D1/D2 wire crossing: **false positive, dropped.** The wire starts exactly on the LED pin (255.27 mm). The tool's bounding box includes the pin length.
- R16-R18 overlapping their GND symbols: **false positive, dropped.** The GND symbol sits on the resistor pin 2 end (92.71 mm) by design.
- The cosmetic lint counts are optional readability tweaks. No finding was raised (Fixer may apply them on request).

## Other analyzers

- `kicad-happy:emc` (schematic JSON only): 0 findings, 0 categories checked, score 100. The EMC rules need PCB data, so this result is **not evidence of EMC compliance**. EMC concerns from manual review are in F-007 and F-022.
- SPICE: not run. No simulator is installed (`ngspice`, `ltspice` and `xyce` are all absent).
- PCB, cross_analysis, thermal, gerber: out of scope (schematic-only iteration).
- bom / jlcpcb: deferred to Task 3. MPN coverage is a known non-issue.
- lifecycle: not run (no MPNs).

## Datasheets used for verification

- Local: `docs/datasheets/ads1299_datasheet.pdf` (SBAS499C) and `tlv757p_datasheet.pdf`.
- Fetched to the session scratchpad (not committed):
  - ADuM3160 Rev. D
  - TI TPS732 (SBVS037S)
  - TI TPS723 (SLVS346E)
  - TRACO TMU 3 series datasheet
- Not re-fetched: TPS60403, STM32F446 datasheet, USBLC6-2. Those pin checks were made against the netlist plus known pinouts and are consistency-level only.
