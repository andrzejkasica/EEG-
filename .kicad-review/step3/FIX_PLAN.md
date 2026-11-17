# FIX_PLAN: Step 3 round 2, iteration 1 (schematic scope only)

Sheet: `hardware/EEG_Kicad_Project/analog_in.kicad_sch` (shortened to SCH below; MCP calls use the absolute path).
Root project used for checks: `hardware/EEG_Kicad_Project/EEG_Kicad_Project.kicad_sch`.

**Baseline, measured 2026-11-17:**
- ERC: 35 violations.
- /ANALOG_IN/SRB1_F: 10 nodes (C55–C62.2, R33.2, U3.17).
- /ANALOG_IN/CHn: 3 nodes each (C(54+n).1, R(24+n).2, U3 INnP).
- BIASOUT: 4 nodes.
- GND: 76 nodes.
- The highest C on any sheet is C63, and the highest #PWR is #PWR0115.

## Global rules for the apply phase

**Lock.** Before every fix, check that no `hardware/EEG_Kicad_Project/~*.kicad_sch.lck` exists (in particular `~EEG_Kicad_Project.kicad_sch.lck` and `~analog_in.kicad_sch.lck`). If one exists, STOP.
- Ignore the PCB lock `~EEG Kicad Project.kicad_pcb.lck`; the PCB is out of scope.

**Snapshot before each fix:**
- `mkdir -p .kicad-review/step3/snapshots/P-S3-00x && cp SCH .kicad-review/step3/snapshots/P-S3-00x/`

**Checks after each fix:**
- `kicad-cli sch export netlist --format kicadxml -o <scratch>/P-S3-00x.xml EEG_Kicad_Project.kicad_sch`
- `kicad-cli sch erc --format json --units mm -o <scratch>/P-S3-00x_erc.json EEG_Kicad_Project.kicad_sch`
- The ERC target is to stay at 35. Any new item, or a changed node list beyond the expected result, means rollback.

**Order:** P-S3-002 → P-S3-003 → P-S3-004 → P-S3-005 → P-S3-007 → P-S3-001.

**PCB:** do not touch it or sync it. PCB re-sync is deferred (see M-S3-003).

---

## S3-002 → P-S3-002  [x] APPROVE   [ ] SKIP   [ ] MANUAL
- Actions (in order):
  1. `mcp__kicad__edit_schematic_component` {schematicPath: SCH, reference: "C63", value: "10n C0G"}. Keep the footprint `Capacitor_SMD:C_0603_1608Metric`; pass no footprint argument.
- Pre-checks:
  - Lock absent; snapshot taken.
  - `grep -c '"Value" "1.5n C0G"' SCH` == 1, and that match is C63 at (236.22, 27.94, rot 90).
- Expected netlist result:
  - No connectivity change. BIASINV = {U3.61, R34, C63} and BIASOUT = {C63.2, R34.2, R35.2, U3.63} are unchanged.
  - C63 value becomes "10n C0G" and its footprint is still C_0603_1608Metric.
  - ERC 35.
- Post-check: render with `get_schematic_view_region` x 225–250, y 20–40 and confirm the "10n C0G" text does not collide with the C63 body or the BIASINV/BIASOUT labels.
- Rollback: restore snapshot taken before this fix.
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## S3-003 → P-S3-003  [x] APPROVE   [ ] SKIP   [ ] MANUAL
- Actions (in order):
  1. ⚠ DESTRUCTIVE: scripted exact-block removal of the 8 no-connect flags on U3 IN1N–IN8N. No MCP tool can delete a no_connect; only `add_no_connect` and `batch_add_no_connects` exist.

     Run with `python3 -I`, cwd = repo root:
     ```python
     p = "hardware/EEG_Kicad_Project/analog_in.kicad_sch"
     s = open(p).read()
     n0 = s.count("(no_connect")
     items = [  # (pin, y-string exactly as in file, uuid)
       (15, "49.53",              "08048960-8114-4f7e-b795-efeabefb2cfa"),
       (13, "57.150000000000006", "4cb44faf-e640-4201-8247-e87ba0c80aa0"),
       (11, "64.77000000000001",  "939dcca2-e4df-47fb-8bd1-4c6750968658"),
       (9,  "72.39",              "2f9061f4-19fe-49e0-848f-924216b04e0b"),
       (7,  "80.01",              "65320fcf-78e3-401b-8be0-d61eeb554088"),
       (5,  "87.63000000000001",  "a143ece5-8874-408f-aa28-259c58d4bf95"),
       (3,  "95.25",              "5e2481be-7b02-4b42-863f-1ce12bb4a4f1"),
       (1,  "102.87",             "a8f1c3b0-83db-478c-a864-955ea1575aa0"),
     ]
     for pin, y, u in items:
         blk = f'\t(no_connect\n\t\t(at 171.45 {y})\n\t\t(uuid "{u}")\n\t)\n'
         assert s.count(blk) == 1, (pin, y, u)
         assert s.count(u) == 1, u
         s = s.replace(blk, "", 1)
     assert s.count("(no_connect") == n0 - 8
     open(p, "w").write(s)
     ```
     The file is currently around lines 10591–10622. Leave the other NCs untouched: SRB2 (207.01, 62.23), BIASREF (207.01, 54.61), BIASIN (207.01, 52.07), U3 NC pins 27/29 (204.47), RESV/RESERVED (207.01), and the U12 IO3/IO4 NCs at x 45.72.
  2. Add 8 local labels with `mcp__kicad__add_schematic_net_label`. Each call uses {schematicPath: SCH, netName: "SRB1_F", componentRef: "U3", pinNumber: P, labelType: "label"}, with no orientation (it auto-orients outward, which gives 180, the same as the CHn labels).

     | pin | input | snapped to |
     |---|---|---|
     | 15 | IN1N | (171.45, 49.53) |
     | 13 | IN2N | (171.45, 57.15) |
     | 11 | IN3N | (171.45, 64.77) |
     | 9 | IN4N | (171.45, 72.39) |
     | 7 | IN5N | (171.45, 80.01) |
     | 5 | IN6N | (171.45, 87.63) |
     | 3 | IN7N | (171.45, 95.25) |
     | 1 | IN8N | (171.45, 102.87) |

     Check each response: `snapped_to_pin` is present, and `actual_position` matches the table within 1e-6.
- Pre-checks:
  - Lock absent; snapshot taken.
  - `get_schematic_pin_locations U3` still gives pins 1/3/5/7/9/11/13/15 at x = 171.45 with angle 180.
  - `list_schematic_labels` shows no label yet at these 8 points.
- Overlap analysis and verification:
  - The existing CHn labels sit on the INxP pins 2.54 mm above each INxN pin. They are at 180°, justify "right bottom", so the text is above the anchor and runs leftward from x 171.45.
  - The new SRB1_F labels have the same orientation and justification. Their text box is about y−1.5…y, about 7.6 mm long (x ≈ 163.8–171.45). The CHn text box ends at y_CH ≈ y−2.54, which leaves a gap of about 1 mm between the two text boxes.
  - Nothing else lies left of x 163 in rows y 45–105; the area back to x ≈ 101 is empty.
  - Verify by rendering `get_schematic_view_region` x 150–180, y 43–106 at 800×1200 and checking that no glyphs touch. Also run `mcp__kicad__find_overlapping_elements` and `mcp__kicad__list_floating_labels` on SCH; there must be no new entries.
- Expected netlist result:
  - /ANALOG_IN/SRB1_F grows from 10 to 18 nodes: C55–C62.2, R33.2, U3.17, U3.1, U3.3, U3.5, U3.7, U3.9, U3.11, U3.13, U3.15.
  - No other net changes.
  - ERC stays at 35: the pins are no longer flagged NC, but each is on a multi-pin net, so there is no pin_not_connected and no "no_connect_connected".
- Rollback: restore snapshot taken before this fix.
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## S3-004 → P-S3-004  [x] APPROVE   [ ] SKIP   [ ] MANUAL
- Actions (in order):
  1. Place the 9 caps with `mcp__kicad__batch_add_components` {schematicPath: SCH, auto_position_fields: true, components: [...]}. Every entry has symbol "Device:C", value "470p C0G", footprint "Capacitor_SMD:C_0402_1005Metric" and rotation 0. The positions are on the 1.27 mm grid, in the empty area x 102–165, y 20–105 between the R25–R35 label column (which ends at x ≈ 100.6) and U3's left labels (which start at x ≈ 163).
     - Row A, y = 40.64:
       - C64 (106.68, 40.64)
       - C65 (116.84, 40.64)
       - C66 (127.00, 40.64)
       - C67 (137.16, 40.64)
       - C68 (147.32, 40.64)
     - Row B, y = 68.58:
       - C69 (106.68, 68.58)
       - C70 (116.84, 68.58)
       - C71 (127.00, 68.58)
       - C72 (137.16, 68.58)
  2. `mcp__kicad__get_schematic_pin_locations` for C64 and C72. Confirm pin 1 is at (x, y−3.81) and pin 2 at (x, y+3.81). If this is inverted, swap the label and GND points below accordingly.
  3. Add 9 local labels with `mcp__kicad__add_schematic_net_label` {schematicPath: SCH, componentRef, pinNumber: "1", netName, labelType: "label"}, with no orientation (auto, outward = up):
     - C64 → CH1, C65 → CH2, C66 → CH3, C67 → CH4, C68 → CH5
     - C69 → CH6, C70 → CH7, C71 → CH8
     - C72 → SRB1_F
  4. Add 9 GND symbols with `mcp__kicad__add_schematic_component` {schematicPath: SCH, symbol: "power:GND", reference, value: "GND", angle: 0, position}. The positions are exactly on pin 2:
     - #PWR0116 (106.68, 44.45), #PWR0117 (116.84, 44.45), #PWR0118 (127.00, 44.45), #PWR0119 (137.16, 44.45), #PWR0120 (147.32, 44.45)
     - #PWR0121 (106.68, 72.39), #PWR0122 (116.84, 72.39), #PWR0123 (127.00, 72.39), #PWR0124 (137.16, 72.39)
  5. Set DNP with a scripted edit. This is not destructive: a string swap of `(dnp no)` → `(dnp yes)`. No MCP tool sets the dnp attribute; add/edit only write `(dnp no)`, and `edit_schematic_component` has no dnp field.

     Run with `python3 -I`, cwd = repo root:
     ```python
     p = "hardware/EEG_Kicad_Project/analog_in.kicad_sch"
     s = open(p).read()
     def block_bounds(s, i):
         a = max(s.rfind("\n\t(symbol", 0, i), s.rfind("\n  (symbol", 0, i)) + 1
         d = 0
         for j in range(a, len(s)):
             if s[j] == "(": d += 1
             elif s[j] == ")":
                 d -= 1
                 if d == 0: return a, j + 1
     for n in range(64, 73):
         ref = f"C{n}"
         key = f'(property "Reference" "{ref}"'
         assert s.count(key) == 1, ref
         a, b = block_bounds(s, s.index(key))
         blk = s[a:b]
         assert '(lib_id "Device:C")' in blk and f'(reference "{ref}")' in blk, ref
         assert blk.count("(dnp no)") == 1 and "(dnp yes)" not in blk, ref
         s = s[:a] + blk.replace("(dnp no)", "(dnp yes)") + s[b:]
     assert s.count("(dnp yes)") == 9
     open(p, "w").write(s)
     ```
- Pre-checks:
  - Lock absent; snapshot taken.
  - Confirm the next free refs again across ALL sheets. Max C is C63; max #PWR is #PWR0115.
    - `cat hardware/EEG_Kicad_Project/*.kicad_sch | grep -oE '(reference|"Reference") "(C|#PWR)[0-9]+"' | sort -V | uniq | tail`
  - Confirm that `get_elements_in_region` / render of x 100–162, y 25–80 is still empty after P-S3-003.
- Verification:
  - Render `get_schematic_view_region` x 98–165, y 25–80 (800×700). Check:
    - Labels (vertical, text above each pin 1) do not hit the row-A GND "GND" text (y ≈ 48–49 vs the row-B label tops at y ≈ 56.6).
    - The auto-placed Ref/Value fields (to the right of each body, ≈ x+2.5…x+11) do not reach the next cap at +10.16 mm, or U3's labels at x ≈ 163 for C68.

    If something collides, move only the fields with `batch_set_schematic_property_positions` and re-render.
  - KiCad draws the DNP cross over C64–C72 in the render.
  - Run `find_overlapping_elements` and `list_floating_labels`: no new entries.
  - The netlist comp entries for C64–C72 carry the dnp property. Alternatively, `kicad-cli sch export bom --exclude-dnp` omits them.
- Expected netlist result:
  - /ANALOG_IN/CH1…CH8 each go from 3 to 4 nodes. For example, CH1 = {C55.1, R25.2, U3.16, C64.1} … CH8 = {C62.1, R32.2, U3.2, C71.1}.
  - /ANALOG_IN/SRB1_F goes from 18 to 19 nodes (+C72.1).
  - GND goes from 76 to 85 nodes (+C64.2…C72.2).
  - 9 new comps, value "470p C0G", footprint C_0402_1005Metric, DNP.
  - ERC 35.
- Rollback: restore snapshot taken before this fix.
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## S3-005 → P-S3-005  [x] APPROVE   [ ] SKIP   [ ] MANUAL
- Sourcing. All stock figures were re-checked with `search_lcsc.py <Cxxxx>` and jlcsearch on 2026-11-17:

  | Part | LCSC | MPN | Class | Stock |
  |---|---|---|---|---|
  | TVS | C2923390 | TPD4E1B06DCKR-TP | Ext | 4,203 |
  | J4 | C5156617 | 2.54-1*10 | Ext, THT | 2,220 |
  | 4.99k 1% 0402 | C25903 | 0402WGF4991TCE | Ext | 578,400 |
  | 1M 1% 0402 | C26083 | 0402WGF1004TCE | Basic | 321,900 |
  | 100k 1% 0402 | C25741 | 0402WGF1003TCE | Basic | 1,818,000 |
  | 4.7n C0G 50V 0402 | C1518204 | GRM1555C1H472JE01D | Ext | 243,750 |
  | 10n C0G 0603 | C432938 | CGA3E1C0G2A103JT0Y0E (TDK, 100 V, ±5%) | Ext | 5,910, $0.109 |
  | 470p C0G 50V 0402 | C76971 | GRM1555C1H471JA01D (Murata, ±5%) | Ext | 283,100, $0.0119 |

  - **10n C0G 0603:** no 50 V part is usefully stocked. C82282 0603CG103J500NT has 0, C85973 GRM1885C1H103JA01D has 0, C76599 has 120 and C76710 has 240. No Basic part exists. The 100 V rating is harmless here and the footprint stays 0603.
  - **470p C0G 0402:** no Basic part exists. The alternative is C106259 CC0402JRNPO9BN471 (NP0, 152,000, $0.0031).
- Actions (in order):
  1. `mcp__kicad__batch_edit_schematic_components` {schematicPath: SCH, components: {...}}. Each entry is {properties: {...}}; new properties default to hidden.
     - U10, U11, U12: {LCSC: "C2923390", MPN: "TPD4E1B06DCKR-TP"}
     - J4: {LCSC: "C5156617", MPN: "2.54-1*10"}
     - R25, R26, R27, R28, R29, R30, R31, R32, R33: {LCSC: "C25903", MPN: "0402WGF4991TCE", Tolerance: "1%"}
     - R34: {LCSC: "C26083", MPN: "0402WGF1004TCE", Tolerance: "1%"}
     - R35: {LCSC: "C25741", MPN: "0402WGF1003TCE", Tolerance: "1%"}
     - C55, C56, C57, C58, C59, C60, C61, C62: {LCSC: "C1518204", MPN: "GRM1555C1H472JE01D", Tolerance: "5%"}
     - C63: {LCSC: "C432938", MPN: "CGA3E1C0G2A103JT0Y0E", Tolerance: "5%"}
     - C64, C65, C66, C67, C68, C69, C70, C71, C72: {LCSC: "C76971", MPN: "GRM1555C1H471JA01D", Tolerance: "5%"}

     That is 34 refs. If the batch reports any per-ref error, redo that ref with `mcp__kicad__edit_schematic_component` {reference, properties}.
- Pre-checks:
  - Lock absent; snapshot taken.
  - P-S3-004 is applied, so C64–C72 exist.
  - No existing LCSC/MPN/Tolerance field on these refs: `grep -c '"LCSC"' SCH` is 0 now.
- Verification:
  - `grep -c '(property "LCSC"' SCH` == 34, `grep -c '(property "MPN"' SCH` == 34 and `grep -c '(property "Tolerance"' SCH` == 29.
  - All new fields are hidden. Render x 20–165, y 20–135 to confirm no new visible text.
  - Spot-check with `get_schematic_component` R34 and C63.
- Expected netlist result: no connectivity change. The comps gain fields LCSC/MPN, plus Tolerance on the 29 R/C. ERC 35.
- Rollback: restore snapshot taken before this fix.
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## S3-007 → P-S3-007  [ ] APPROVE   [ ] SKIP   [x] MANUAL   (user fixes layout overlaps in Eeschema)
- Current state:
  - C55–C62 are Device:C at rotation 0, at x = 30.48 + 12.7·k and y = 119.38.
  - The Reference is at (x+2.54, 119.38) at 90°, justify left, which lands on the plate edge (the plates span x±2.03).
  - The Value is at (x+4.572, 119.38) at 90°.
  - The CHn label is on top (y 115.57) and the SRB1_F label at the bottom (y 123.19), both vertical on x.
- Actions (in order):
  1. For each cap, call `mcp__kicad__edit_schematic_component` {schematicPath: SCH, reference, fieldPositions: {Reference: {x: X, y: 119.38, angle: 0, justify: "right"}}}. This puts a horizontal Reference left of the body, ending 0.5 mm clear of the left plate. Values of X:

     | Ref | X |
     |---|---|
     | C55 | 27.94 |
     | C56 | 40.64 |
     | C57 | 53.34 |
     | C58 | 66.04 |
     | C59 | 78.74 |
     | C60 | 91.44 |
     | C61 | 104.14 |
     | C62 | 116.84 |

     Each text spans about X−3.7…X. The previous cap's Value at x+4.57 spans about (X−8.1)…(X−6.8), so the gap is about 3 mm.
  2. Render `mcp__kicad__get_schematic_view_region` x 20–130, y 108–132 at 1200×300.
  3. If the angle or justify renders wrong (the known oddity), iterate per cap. Fallback A: angle 90, justify "left", at (x−2.54, 119.38). Fallback B: `mcp__kicad__autoplace_schematic_fields` {references: ["C55",…,"C62"]}. Re-render after each attempt. Stop after 3 iterations; if it is still bad, mark it MANUAL.
- Pre-checks: lock absent; snapshot taken. The C55 Reference is currently at (33.02, 119.38, 90).
- Expected netlist result: no change (cosmetic). ERC 35. Run `find_overlapping_elements` to check for no new overlaps.
- Rollback: restore snapshot taken before this fix.
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## S3-001 → P-S3-001  [x] APPROVE   [ ] SKIP   [ ] MANUAL
- Placement:
  - The sheet has 0 text items.
  - The area left of U3 (x 102–165) is now used by C64–C72.
  - The empty space nearest U3 that is wide enough for a 96-char line is the band below the decoupling row and left of the title block: x 15–175, y 165–198. The title block starts at x ≈ 177, y ≈ 166, and the decoupling row's −2V5/GND symbol texts end at y ≈ 162.
  - Anchor (20.32, 170.18), left-justified. The longest line is 96 chars ≈ 115 mm at 1.27 mm font, so it ends at x ≈ 136. That is well inside the A4 frame (x 285) and clear of the title block.
  - 6 lines ≈ 14 mm, so the text ends at y ≈ 185.
- Actions (in order):
  1. `mcp__kicad__add_schematic_text` {schematicPath: SCH, position: [20.32, 170.18], fontSize: 1.27, justify: "left", text: the 6 lines joined with "\n"}. The text is ASCII only:
     ```
     FW REQUIRED (ADS1299 U3):
     MISC1=0x20 (SRB1 -> all channel N inputs; INxN are also tied to SRB1_F so REF works with SRB1=0)
     CONFIG3=0xEC (PD_REFBUF=1, BIASREF_INT=1, PD_BIAS=1)
     CHnSET: MUX=000, SRB2=0
     BIAS_SENSP = channels used for bias drive (C63=10n is compensated for all 8)
     Lead-off: current <=24 nA (ILEAD_OFF 6/24 nA); REF lead-off via one LOFF_SENSN bit
     ```
  2. Render `get_schematic_view_region` x 10–200, y 158–200 at 1600×360.
     - Confirm the text shows as 6 lines, nothing overlaps, and the right end is below 175 mm.
     - If "\n" is written literally, so the text comes out as one line, restore the snapshot. Then use 6 separate `add_schematic_text` calls at y = 170.18, 172.72, 175.26, 177.80, 180.34, 182.88 (x 20.32), with the first line bold: true.
- Pre-checks:
  - Lock absent; snapshot taken. `grep -c "(text " SCH` == 0.
  - The text must not say "INxN NC". It reflects P-S3-003.
- Expected netlist result: no change (text only). ERC 35.
- Rollback: restore snapshot taken before this fix.
- Touches schematic? yes | Requires sync_schematic_to_board? no (PCB re-sync deferred)

## Counts
- Entries planned: 6.
- Destructive actions: 1 (P-S3-003 step 1). The P-S3-004 DNP edit is scripted but not destructive.
- Manual items: 5.
