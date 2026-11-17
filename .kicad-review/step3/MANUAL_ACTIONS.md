# MANUAL_ACTIONS: Step 3 round 2

## M-S3-001 (from S3-006) — J4 is a through-hole (THT) header
- Why blocked: this is an ordering and assembly decision for you, not a schematic change. LCSC C5156617 (2.54-1*10) is a "Plugin" (THT) part with 2,220 in stock. JLCPCB places THT parts only through its separate THT/hand-solder assembly service, which adds cost and lead time.
- Do this:
  1. At order time choose one of:
     - (a) exclude J4 from the JLCPCB BOM/CPL and hand-solder it;
     - (b) order JLCPCB THT assembly for J4;
     - (c) if the board must be fully SMT-assembled, pick an SMD 2.54 mm 1x10 header. That needs a footprint change at layout.
  2. Tell me which one you chose.
- After you're done I will: record the choice in STATE.md. For (a), I will add a note or BOM exclusion as you prefer. For (c), I will plan the footprint/LCSC change as a new fix.

## M-S3-002 (from S3-008) — Normalise file formatting with an Eeschema open+save
- Why blocked: the MCP writes leave mixed 2-space/tab indentation and float noise in coordinates (for example 45.720000000000006). Only Eeschema's own serialiser cleans this up safely, and this round's fixes will add more of it.
- Do this:
  1. After all approved P-S3 fixes are applied and verified, open `hardware/EEG_Kicad_Project/EEG_Kicad_Project.kicad_pro` in KiCad and open the analog_in sheet in Eeschema.
  2. Make no edits. Press Ctrl+S to save, then close Eeschema so the `~*.kicad_sch.lck` lock is gone.
  3. Tell me when it's done.
- After you're done I will:
  - re-run `validate_schematic`, and expect no indent_depth_mismatch;
  - grep for float noise;
  - re-run the kicad-cli netlist and ERC, and confirm the netlist is identical and ERC is still 35;
  - then hand off to the Verifier.

## M-S3-003 (from S3-002/003/004/005) — Update the PCB from the schematic (deferred)
- Why blocked: the PCB is out of scope and locked by its open editor, and this round must not touch it. The PCB now lacks C64–C72, their DNP flags and the new SRB1_F connections to U3 IN1N–IN8N; C63's value is also stale.
- Do this: when you start layout, close the PCB editor or use it directly. In Pcbnew, run Tools → Update PCB from Schematic (F8), check that it adds C64–C72 (DNP), and save.
- After you're done I will: run DRC and the schematic-vs-PCB cross-check on request, in a PCB-scope round.

## M-S3-004 (from S3-002) — Bench-check bias-loop stability at bring-up
- Why blocked: phase margin with real electrodes, cable and body capacitance can only be confirmed on hardware. C63 = 10 nF follows the TI EVM (392k/10n) but has not been simulated with the patient path.
- Do this: at bring-up, put a step on a body phantom (for example 51k ∥ 47n per electrode and about 200 pF to GND) with BIAS_SENSP set to all 8 channels. Scope BIASOUT and look for less than 10% overshoot and no ringing. If it fails, raise C63 or reduce the number of BIAS_SENSP channels.
- After you're done I will: record the result and propose a value change if needed.

## M-S3-005 (from S3-005) — Re-confirm LCSC stock at order time, especially the 10 nF C0G 0603
- Why blocked: stock changes over time. The 50 V 10 nF C0G 0603 parts are nearly out of stock (C82282: 0, C85973: 0, C76599: 120, C76710: 240), so C63 uses TDK CGA3E1C0G2A103JT0Y0E, C432938, 100 V, 5,910 in stock. No Basic parts exist for the 10n or 470p C0G values. The extended-part count rises by 2 lines (C432938; C76971 only if the DNP caps are ever fitted).
- Do this: before ordering, run the bom/lcsc stock check, or ask me to. If C432938 is short, accept C76710 or C76599, or ask me to search again.
- After you're done I will: update the C63 LCSC/MPN fields if you pick an alternative.

## M-S3-006 (from S3-007 and any overlaps from this round) — Tidy schematic text overlaps by hand
- Why open: the user chose to fix the layout overlaps themselves (2026-11-17). P-S3-007 was not applied by MCP.
- Do this in Eeschema (combine it with M-S3-002, so one save covers both):
  1. C55–C62: move the Reference fields off the cap bodies.
  2. C63: nudge the "10n C0G" Value away from R34's BIASINV label.
  3. #PWR0116–#PWR0124: move each "GND" Value below its symbol, or hide it. It currently sits on the C64–C72 bodies.
  4. C64–C72: make the Reference fields readable (they are under the plates and the DNP cross). Shorten or move the "470p C0G" Values so they don't run under the next cap.
  5. Firmware note: move it down about 13 mm (anchor around (20.32, 182.88)), or set its justify to top. It currently overprints the −2V5/GND texts of the decoupling row at y ≈ 160–162.
- After you're done I will: re-run the netlist and ERC and confirm connectivity is unchanged.
