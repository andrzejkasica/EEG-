# Step 3 diff baseline

Base is the b3af525 copy in `.kicad-review/step3/base/`; current is the working tree. Analyzer, ERC and netlist outputs are in `.kicad-review/step3/analysis/{base,current}/`, and the diff is in `analysis/diff.txt` / `diff.json`.

## kicad-cli 9.0.9 ERC (json, mm)

| Severity / type | Base | Current | Delta |
|---|---|---|---|
| error pin_not_connected | 54 (22 /ANALOG_IN/, 32 /STM32/) | 32 (all /STM32/) | −22 |
| error pin_not_driven | 19 (/ANALOG_IN/) | 0 | −19 |
| warning global_label_dangling | 2 (/) | 2 (/) | 0 |
| warning multiple_net_names | 1 (/POWER_SUPPLY/) | 1 | 0 |
| **Total** | **76** (73 err / 3 warn) | **35** (32 err / 3 warn) | **−41** |

The spec's target was met: all 41 Step-3 items on /ANALOG_IN/ are cleared, with no new ERC items of any type. The 32 /STM32/ items and the 3 warnings were there before Step 3 and are out of scope.

## kicad-happy analyze_schematic.py

| | Base | Current |
|---|---|---|
| Total findings | 105 (2 error / 55 warning / 48 info) | 98 (1 error / 34 warning / 63 info) |
| NT-001 single-pin-net warnings | 54 | 32 (the 22 U3 nets are resolved) |
| New rules | – | CG-AUD ×1 (J4 has no ground pin); RC-DET 1→11; PD-DET 1→4; EP-AUD 3→4 (J4 has full ESD coverage); DS-003 ×1 |
| Errors | SS-001 (MPN coverage), DS-001 (no datasheets dir; an artifact of the base copy's path) | SS-001 only |
| diff_analysis | – | 35 changes (+35 / −0). It flags 9 "no_driver" regressions (CH1–CH8, BIASINV); kicad-cli ERC does not report these (see S3-015). |

## Components and nets (kicad-cli kicadxml netlist)

| | Base | Current |
|---|---|---|
| Components | 101 | 125 (+24: J4, U10–U12, R25–R35, C55–C63) |
| Nets | 119 | 134 |
| Unique BOM lines (analyzer) | 39 | 45 |
| No-connect flags | 3 | 16 (+11 on U3: IN1N–IN8N, SRB2, BIASIN, BIASREF; +2 on U12 IO3/IO4) |
| Components changed or removed | – | none |

## MCP checks on analog_in.kicad_sch
- validate_schematic: 1 "error", `indent_depth_mismatch` at line 10652. This is a formatting issue only: kicad-cli loads the file, and ERC and netlist ran cleanly.
- find_orphaned_wires: 0.
- list_floating_labels: 0.
- find_wires_crossing_symbols: 0.
- find_overlapping_elements: 3 (R16/R17/R18 ↔ #PWR089–091). These parts are not part of Step 3.
- validate_symbol_library on EEG_custom.kicad_sym: valid, 1 symbol, kicad-cli OK.
