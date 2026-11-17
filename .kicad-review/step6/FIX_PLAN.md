# FIX_PLAN: Step 6 round 5, iteration 1 (schematic scope only)

Paths:
- Sheets live under `hardware/EEG_Kicad_Project/`: SCH_AIN = analog_in, SCH_PWR = power, SCH_STM = stm32, SCH_USB = usb. ROOT is EEG_Kicad_Project.kicad_sch.
- SCR = `/tmp/claude-1000/-home-andrzej-Documents-Repos-EEG-/2322c6a4-79fd-4009-8cf0-42fae3306225/scratchpad/s6fix`.
- The block parser `SCR/blk.py` is read-only. It provides `blocks(text, head)`: balanced s-expressions, quote-aware.

## Baseline (ad3e7bb)
- ERC: 0 errors, 1 warning (GND/GNDA).
- 147 components, 128 nets.
- Flat BOM: 147 rows, including the 10 TP/JP rows.
- Grouped BOM: the 0603 caps split into two lines, `C21,C25 | 100n` and `C32,C34,C38,C39,C42,C46 | 0.1u`.
- USB nets:
  - D+ = {J1.A6, J1.B6, U8.1}
  - D- = {J1.A7, J1.B7, U8.3}
  - UD+ = {R22.1, U8.6}
  - UD- = {R21.1, U8.4}
  - USB_OTG_FS_DP = {R23.1, U1.45}
  - USB_OTG_FS_DM = {R24.1, U1.44}

## Global rules
- **Lock check** before each fix. Snapshot the touched sheets to `.kicad-review/step6/snapshots/P-S6-00n/`.
- **After each fix**, export the kicad-cli netlist and ERC and diff the per-net node sets. Any unexpected change means rollback.
- **ERC** must stay at 0 errors and 1 warning.
- **Isolation check at the end:**
  - The primary nets {+5V_PRI, GND_PRI, /USBC/D±, /USBC/UD±} share no nodes with isolated nets.
  - Only U7 and U9 straddle the barrier.
- **Order:** 001 → 004.
- **No PCB.** Report cosmetic overlaps only; don't iterate on them.

## Tool facts
- No MCP tool sets `in_bom`, renames a label, changes a label's type, or changes its shape.
- In KiCad 9, "exclude from BOM" is the placed symbol's `(in_bom no)`. Instances have no BOM flag. Leave the lib_symbols cache alone.
- `kicad-cli sch export bom` excludes `in_bom no` by default. `--include-excluded-from-bom` restores those parts.
- The netlist keeps excluded parts and adds an `exclude_from_bom` property to them.

## New parts
| Part | LCSC | MPN | Type | Notes |
|---|---|---|---|---|
| Red LED 0603 | C2286 | KT-0603R (Hubei KENTO) | Basic | 6.1 M in stock, Vf 1.8–2.4 V, 615–630 nm. About 1.3 mA through 1k. |
| 1k 0402 1% | C11702 | 0402WGF1001TCE (UNI-ROYAL) | Basic | |

---

## S6-003 → P-S6-001  [x] APPROVE   [ ] SKIP   [ ] MANUAL
- **Actions:**
  1. Lock check; snapshot SCH_AIN.
  2. `batch_edit_schematic_components` SCH_AIN, setting value "100n" on C32, C34, C38, C39, C42 and C46.
  3. `get_schematic_component` on each: value is 100n and the footprint is unchanged.
- **Pre-checks (verified):**
  - All six are currently "0.1u" `Device:C` with footprint C_0603_1608Metric, `in_bom yes`, `dnp no`, and no LCSC field.
  - They are identical to C21 and C25.
  - "0.1u" appears nowhere else.
- **Expected:**
  - No connectivity change.
  - The BOM merges into one line: `C21,C25,C32,C34,C38,C39,C42,C46 | 100n | 0603 | 8`.
  - ERC 0/1.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## S6-004 → P-S6-002  [x] APPROVE   [ ] SKIP   [ ] MANUAL
- **Actions:**
  1. Lock check; snapshot SCH_STM, SCH_AIN and SCH_PWR.
  2. Run a scripted exact edit (`python3 -I`, importing blk from SCR). It is non-destructive: one token is swapped per block.
     ```python
     TARGETS = {"stm32.kicad_sch": ["TP1","TP2","TP3","TP4","TP5","TP6","JP1"],
                "analog_in.kicad_sch": ["TP7"], "power.kicad_sch": ["TP8","TP9"]}
     for f, refs in TARGETS.items():
         t = open(f).read(); found = {}
         for s, e, b in blocks(t, '\n\t(symbol\n'):
             r = re.search(r'\(property "Reference" "([^"]+)"', b).group(1)
             if r in refs:
                 assert r not in found, f"dup {r}"
                 assert b.count('(in_bom yes)') == 1 and b.count('(in_bom no)') == 0, r
                 assert re.search(r'\(reference "%s"\)' % re.escape(r), b), r
                 found[r] = (s, e, b)
         assert sorted(found) == sorted(refs), (f, found.keys())
         for r, (s, e, b) in sorted(found.items(), key=lambda kv: -kv[1][0]):
             nb = b.replace('(in_bom yes)', '(in_bom no)', 1)
             assert len(nb) == len(b) - 1
             t = t[:s] + nb + t[e:]
         open(f, 'w').write(t)
     ```
     Before each write, assert that the file's `(in_bom no)` count rose by exactly len(refs).
  3. Run `kicad-cli sch export bom` with the default options. Expect 137 rows, missing exactly {TP1–TP9, JP1}.
  4. Run it again with `--include-excluded-from-bom`. The output must equal the baseline's 147 rows.
- **Pre-checks (verified):** all 10 placed blocks have exactly one `(in_bom yes)`, and each has a matching instance reference.
- **Expected:**
  - Connectivity unchanged.
  - The netlist adds `exclude_from_bom` to those 10 parts.
  - ERC 0/1.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## S6-005 → P-S6-003  [x] APPROVE   [ ] SKIP   [ ] MANUAL
**Method:** scripted in-place conversion, as one atomic write. It keeps every uuid and `at` byte-exact and uses exact-block asserts. No MCP tool can change a label's type or shape.

- **Actions:**
  1. Lock check; snapshot SCH_USB.
  2. Run this script (`python3 -I`, importing blk):
     ```python
     CONV = {"2ba0d60e-db48-4465-811e-b04def63359e":("UD+",(146.05,55.88,90)),
             "80984e28-12eb-49e3-bfdf-6d1cb8d4a5d8":("UD+",(205.74,46.99,90)),
             "9e2d387a-c044-4f93-9b64-5c8eabbcd8d9":("UD-",(146.05,60.96,270)),
             "b8ea26f5-8ce8-4256-a908-7f8767edf6dd":("UD-",(201.93,46.99,90)),
             "94a30aeb-bceb-4c2e-bbce-f499c539bd98":("D+",(67.31,64.77,0)),
             "b7d9d575-5972-45aa-bf0d-42e64d295ece":("D+",(123.19,55.88,90)),
             "aba3c5eb-7754-4d42-ae2c-b6f5641b0221":("D-",(123.19,60.96,270)),
             "f0a1c009-f695-4659-a82a-292c70a96dc8":("D-",(67.31,59.69,0))}
     SHAPE = {"3a9195e2-19ce-49da-8392-e866e817ac44":"USB_OTG_FS_DP",
              "700ec754-3dbb-4cb0-83f8-d728241f94fb":"USB_OTG_FS_DM"}
     t = open("usb.kicad_sch").read()
     assert t.count('(global_label ') == 10 and t.count('\t(label ') == 2
     edits = []
     for s, e, b in blocks(t, '(global_label '):
         name = re.match(r'\(global_label "([^"]+)"', b).group(1)
         uid = re.search(r'\(uuid "([^"]+)"\)', b).group(1)
         if uid in CONV:
             n, (x, y, a) = CONV[uid]
             assert name == n and b.count('(shape input)') == 1 and b.count('Intersheetrefs') == 1
             at = re.search(r'\n\t\t\(at ([\d.]+) ([\d.]+) (\d+)\)', b)
             assert (float(at[1]), float(at[2]), int(at[3])) == (x, y, a)
             j = 'left bottom' if a in (0, 90) else 'right bottom'
             fa = '\n\t\t(fields_autoplaced yes)' if '(fields_autoplaced yes)' in b else ''
             nb = (f'(label "{n}"\n\t\t(at {at[1]} {at[2]} {at[3]}){fa}\n\t\t(effects\n\t\t\t(font\n'
                   f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {j})\n\t\t)\n\t\t(uuid "{uid}")\n\t)')
             edits.append((s, e, nb))
         elif uid in SHAPE:
             assert name == SHAPE[uid] and b.count('(shape input)') == 1
             edits.append((s, e, b.replace('(shape input)', '(shape bidirectional)', 1)))
     assert len(edits) == 10
     for s, e, nb in sorted(edits, reverse=True): t = t[:s] + nb + t[e:]
     assert t.count('(global_label ') == 2 and t.count('\t(label ') == 10
     open("usb.kicad_sch", "w").write(t)
     ```
  3. `list_schematic_labels` SCH_USB. Expect 8 local labels (D±/UD± ×2 each) and 2 global labels (USB_OTG_FS_DP/DM, both bidirectional).
- **Pre-checks (verified):**
  - usb has 10 global labels, with the uuids and coordinates listed in the script.
  - On stm32, USB_OTG_FS_DP/DM are already bidirectional.
  - No other sheet uses the names D±/UD±, and there are no sheet pins with those names.
  - The sheet name is "USBC", so the local nets become /USBC/….
- **Expected:**
  - Net names change from D±/UD± to /USBC/D± and /USBC/UD±. Their members are identical.
  - USB_OTG_FS_DP/DM are unchanged.
  - 147 components and 128 nets; every other net is identical.
  - ERC 0/1, and the analyzer's label-shape warnings clear.
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## F-012 → P-S6-004  [x] APPROVE   [ ] SKIP   [ ] MANUAL
- **Actions:**
  1. Lock check; snapshot SCH_STM.
  2. `batch_edit_schematic_components` SCH_STM:
     - D1 and D2: value "LED_RED", plus properties LCSC C2286 and MPN KT-0603R.
     - R19 and R20: properties LCSC C11702, MPN 0402WGF1001TCE and Tolerance 1%.
  3. `get_schematic_component` on all four: the new fields are hidden, and the footprints are unchanged.
- **Pre-checks (verified):**
  - D1 and D2 are `Device:LED`, value "LED", LED_0603, with no LCSC field.
  - R19 and R20 are 1k on the same footprint as R36/R37.
  - The naming follows D4 ("LED_GRN").
- **Expected:**
  - No connectivity change. Only the D1/D2 values and the new fields change.
  - ERC 0/1.
  - "LED_RED" is wider than "LED", so it may overlap other text (report only).
- Rollback: restore snapshot taken before this fix
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## End-of-round checks
- The final netlist against the baseline may differ only by:
  - the 4 USB net renames (same members);
  - the value and property changes;
  - `exclude_from_bom` on the 10 TP/JP parts.
- ERC 0/1.
- Isolation check passes.
- Report any overlaps on usb and stm32.

**Counts:** 4 fixes. 2 use MCP only (001, 004) and 2 are scripted exact edits (002, 003). Nothing is destructive: the label conversion keeps every uuid and coordinate.
