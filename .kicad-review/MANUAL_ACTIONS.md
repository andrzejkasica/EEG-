# MANUAL_ACTIONS: iteration 1

## M-001 (from F-002) — Choose the regulated isolated DC-DC and confirm its datasheet limits
- **Why blocked:**
  - This is a user part-selection decision.
  - The candidate specs come only from the KiCad library descriptions; the datasheets were not downloaded or verified.
  - The MCP swap itself is straightforward (P-002).
- **Do this:**
  1. Pick A (TRACO TRN 3-0511, recommended), B (TRACO TEC 2-1211WI) or C (XP Power ITX0505SA-H).
  2. Open the datasheet (A: https://www.tracopower.com/products/trn3.pdf) and confirm:
     - the input range minimum is ≤ 4.5 V, so it works at worst-case USB VBUS (about 4.4–4.75 V at the device);
     - the output is regulated with no minimum-load requirement, or a minimum load that this board meets;
     - the isolation is ≥ 1.5 kVDC, and the isolation capacitance, which drives patient leakage (lower is better);
     - any recommended input/output capacitors. Input caps count toward the ≤ 10 µF VBUS limit; 4.9 µF is already planned.
  3. If you choose B, confirm the Remote pin's "open = ON" behaviour.
  4. Tick APPROVE on P-002 and write the chosen letter next to it.
  5. Update `project_power_design.md` and `Components.txt` with the new part.
- **After you're done I will:** run P-002 for the chosen candidate. For A and C no re-wiring is needed; for B I add a no-connect on Remote at (38.1,170.18). Then I re-export the netlist and run ERC.

### M-001 status (2026-11-17)
- TRN 3-0511 checked against docs/datasheets/TRN3.pdf: regulated (±1 % set, 0.2 % line, 1 % load), no minimum load, 1600 VDC / 60 s functional isolation, 75 pF, input cap internal, pinout matches P-002.
- **Rejected by the user:** it is a 9 V-nominal 2:1 module (4.5–13.2 V). At USB 5 V there is only about 0.5 V of headroom (VBUS can be 4.40 V), and specs are only given at 9 V; no-load input current is 75 mA.
- **Open:** in Task 3, find a regulated isolated DC-DC with a 5 V-nominal input (e.g. 4.5–5.5 V input class), at least 1.5 kVDC isolation, at least 300 mA, and no minimum load. Then re-plan P-002 with its pinout. F-002 stays open until then.

## M-002 (from F-001, F-003) — Optional: remove stray 2-wire junction dots
- **Why blocked:** the KiCad MCP server has no junction-delete tool. The leftover junctions are cosmetic only; they do not change connectivity or cause ERC errors.
- **Do this:**
  1. With the PCB editor's lock respected, open the schematic editor after P-001 and P-003 have run.
  2. On usb.kicad_sch, select the junction at (218.44, 40.64) and delete it.
  3. On power.kicad_sch, delete the junctions at (217.17,110.49), (217.17,120.65), (217.17,121.92), (224.79,132.08), (76.2,113.03), (76.2,121.92), (76.2,123.19) and (80.01,133.35). Before each delete, check that only 2 wires meet at that point.
  4. Save, then close the schematic editor so the `.lck` file disappears.
- **After you're done I will:** re-export the netlist and confirm it is identical to the post-fix netlist, then run `lint_schematic_cosmetic`.

## M-003 (from F-004) — Correct the USB-C part in Components.txt
- **Why blocked:** this is a documentation and sourcing edit outside the schematic. `hardware/list_of_components/Components.txt` lists "GCT USB4135-GF-A", which is a power-only 6-pin receptacle with no D+/D− contacts.
- **Do this:**
  1. Change the CON_USB entry to GCT USB4105-GF-A (16P, USB 2.0), matching the footprint in P-004. Alternatively keep Amphenol 12401610E4#2A, which needs the J1 footprint changed to `Connector_USB:USB_C_Receptacle_Amphenol_12401610E4-2A`.
  2. Confirm availability at JLCPCB during Task 3.
- **After you're done I will:** make sure J1's footprint matches the part you listed. If you chose Amphenol, I will re-apply P-004 step 5 with that footprint.

## M-004 (from P-001) — ERC: U9 VDD1 power_pin_not_driven on VDD1_ISO1
- **Why open:**
  - After P-001, U9 pins 3, 4 and 5 sit on the new local net `VDD1_ISO1`. That net has no power-output pin.
  - The ADuM3160 drives VDD1 from its internal regulator, fed from VBUS1. The KiCad symbol types VDD1 as Power input, so ERC flags it.
  - This is the only new ERC violation from this iteration: 76 at baseline, 77 now.
  - The Fixer did not improvise a fix.
- **Do this (pick one and approve):**
  - (a) Add a `power:PWR_FLAG` on `VDD1_ISO1`, for example at C50 pin 1 (190.5,48.26). The project already uses PWR_FLAGs on rails fed through the filter inductors. Use the next free #FLG number.
  - (b) Or exclude this ERC violation in the schematic editor, with a comment.
- **After you're done I will:** re-run ERC and confirm the violation is gone (77 → 76), with no netlist change apart from the flag.

## M-005 (from P-005) — Cosmetic: VDD1 wire passes through R21/R22 bodies
- **Why open:**
  - The existing wire 0fe28947 (199.39,48.26)→(208.28,48.26) runs from the VDD1 column to U9.3. After P-005 it crosses the bodies of R21 (x=201.93) and R22 (x=205.74). `find_wires_crossing_symbols` reports this.
  - It is not an electrical problem: the R pins end at y=46.99 and y=54.61, and the netlist is correct. It does hurt readability.
  - Fixing it means re-routing, which was not in the approved plan.
- **Do this (pick one and approve):**
  - (a) Delete wire 0fe28947 and connect U9.3 with a `VDD1_ISO1` local label snapped to U9 pin 3 at (208.28,48.26). The column at x=199.39 stays tied to U9.4 and U9.5, and to C50 through the label at C50.1. Check that the junction at (199.39,48.26) still has 2 or more wires.
  - (b) Or do the same move by hand in the schematic editor.
- **After you're done I will:** confirm that `/USBC/VDD1_ISO1` still equals {C50.1, U9.3, U9.4, U9.5} and that `find_wires_crossing_symbols` on usb returns none.
