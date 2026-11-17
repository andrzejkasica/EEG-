# FIX_LOG: Step 6 round 5, iteration 1 (APPLY)

All 4 fixes applied, in order. No schematic lock was present. The PCB was not touched and DRC was not run.

**Tools** are in `scratchpad/s6tools/`:
- `export.sh`: kicad-cli netlist, ERC and BOMs into `scratchpad/s6fix/`.
- `cmp.py`: compares per-net node sets, with a rename map.
- `iso.py`: isolation flood-fill.

The pre-flight export (s0) reproduced the baseline exactly. ERC was 0/1.

## P-S6-001 (S6-003): APPLIED
- **Snapshot:** `snapshots/P-S6-001/analog_in.kicad_sch`
- **Pre-check:** passed. C32/34/38/39/42/46 were "0.1u", C_0603, and the only occurrences of that value.
- **Action:** `batch_edit_schematic_components` set value "100n" on all six (6 updated, 0 errors). The diff is exactly the 6 Value lines.
- **Netlist:** OK.
- **ERC:** 0/1.
- **BOM:** grouped rows went 55 → 54, with one line `C21,C25,C32,C34,C38,C39,C42,C46 | 100n | 0603 | 8`.

## P-S6-002 (S6-004): APPLIED
- **Snapshot:** `snapshots/P-S6-002/{stm32,analog_in,power}.kicad_sch`
- **Script:** `p002.py`, the plan's script plus extra asserts on the count and the file length. `(in_bom no)` counts went stm32 0 → 7, analog_in 0 → 1, power 0 → 2. The diffs are only those lines.
- **BOM:**
  - The flat default export has 137 rows, missing exactly {JP1, TP1–TP9}.
  - With `--include-excluded-from-bom` it has 147 rows, identical to the post-001 state.
  - Grouped rows went 54 → 44.
- **Netlist:** OK. The 10 parts gained an `exclude_from_bom` property.
- **ERC:** 0/1.

## P-S6-003 (S6-005): APPLIED
- **Snapshot:** `snapshots/P-S6-003/usb.kicad_sch`
- **Script:** `p003.py`, the plan's script verbatim. All asserts passed.
  - 8 global labels converted to local labels (D±/UD±), keeping their uuids and coordinates.
  - USB_OTG_FS_DP/DM changed to bidirectional.
  - The file now has 2 global and 10 local labels. The set of uuids is identical (209).
- **Netlist:** the renames D± → /USBC/D± and UD± → /USBC/UD± kept identical members. USB_OTG_FS_* are unchanged. Netlist OK.
- **ERC:** 0/1.

## P-S6-004 (F-012): APPLIED
- **Snapshot:** `snapshots/P-S6-004/stm32.kicad_sch`
- **Changes:**
  - D1/D2: value LED_RED; LCSC C2286, MPN KT-0603R.
  - R19/R20: LCSC C11702, MPN 0402WGF1001TCE, 1%.
  - All new fields are hidden.
- **Netlist:** OK.
- **ERC:** 0/1.
- **BOM:** `D1,D2 | LED_RED` and `R19,R20 | 1k`.
- **Note:** the MCP wrote the new properties in a compact s-expression style. kicad-cli parses it fine, and Eeschema reformats it on the next save.

## Overlaps
- usb: none.
- stm32 (5) and analog_in (3): the same #PWR bounding-box items as in the baseline.
- The new LED_RED text clears the nearby GND values by about 1 mm (tight, but no collision).

## Final
- **ERC:** 0 errors, 1 warning (GND/GNDA).
- **Size:** 147 components, 128 nets.
- **Netlist vs baseline:** only the allowed differences:
  - the 4 USB net renames, with identical members;
  - the value and field changes;
  - `exclude_from_bom` on the 10 TP/JP parts.
- **BOM rows:** flat 137 (147 with excluded parts); grouped 44 (was 55).
- **Isolation:** PASS. Only U7 and U9 straddle the barrier, and the primary domain contains no GND, +3V3 or +5V net.
- **Final netlist:** `scratchpad/s6fix/final.net`
- **Result:** applied 4, blocked 0.
