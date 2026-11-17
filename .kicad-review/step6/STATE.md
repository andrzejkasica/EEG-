# KiCad Review Loop: STATE (round 5, Task 2 Step 6: full deep review)

- **Phase:** done. Verify 4 PASS, plan target MET. The user did the Eeschema save (netlist identical). Committed.
- **Mode:** full loop, **whole schematic** (not a diff), schematic scope only. Base commit `ad3e7bb`.
- **Round folder:** `.kicad-review/step6/`. Rounds 1–4 are closed; their files are in `.kicad-review/` (round 1) and `.kicad-review/step3|step4|step5/`.
- **Plan target** (`docs/superpowers/plans/2026-10-23-eeg-board-completion.md`, Task 2 Step 6): zero ERC errors, and no `high`/`error` findings except the MPN-coverage gate (SS-001).
- **PCB:** out of scope (unsynced, locked; Step 7 re-syncs it). No DRC, no PCB analyzers.
- **Lock rule:** no `hardware/EEG_Kicad_Project/~*.kicad_sch.lck` before any write.
- **Tooling:**
  - kicad-cli 9.0.9.
  - kicad-happy skills: kicad (`/home/andrzej/.claude/plugins/marketplaces/kicad-happy/skills/kicad/scripts/`), emc (schematic-level parts only), spice (optional, for filters/dividers), datasheets.
  - LCSC scripts under `/home/andrzej/.claude/plugins/cache/kicad-happy/kicad-happy/2.3.2/skills/lcsc/scripts/`.
  - Datasheets in `docs/datasheets/`; more are in `/tmp/claude-1000/-home-andrzej-Documents-Repos-EEG-/2322c6a4-79fd-4009-8cf0-42fae3306225/scratchpad/step5/ds/`.
  - Subagents cannot write report .md files; the Orchestrator saves them.
- **Baseline ERC:** 1, the intentional GND/GNDA multiple_net_names.

## Known, accepted or tracked items (do not re-raise as new; reference them by ID if relevant)
- **F-002 / S5-001 (HIGH, open, Task 3):** U7 TMU3-0511 is unregulated. The isolated +5V must stay ≤ 5.25 V (TPS60403 recommended max). Converter choice is pending.
- **F-023 (INFO):** isolation is functional grade only; there is no medical certification target.
- **SS-001:** the MPN-coverage gate (Task 3).
- **Intentional:**
  - GND/GNDA merged (multiple_net_names).
  - J4 has no ground pin (patient header).
  - JP1 BOOT0 jumper.
- **Analyzer false positives already established:**
  - DO-DET "missing caps" on U2/U4/U6 (the caps sit behind the inductors).
  - RC-DET R35/C63 pairing.
  - U4 "gpio_controlled".
  - RS-001 on 5V_L1.
  - USB dp/dm series-resistor "info" (R21/R22 are behind U8 by design).
  - The I2C vol_compatibility 67 Ω miscalculation.
  - Wire crossings on the D1/D2/D4 LED bounding boxes.
- **Decided:** C24 1 µF and C25 100 nF NR caps are kept (F-011 closed). The TPS72325 M3 die is a Task 3 sourcing item.
- **Firmware items (documented in `docs/firmware/ads1299-power-up.md`):** F-021 VBUS sensing, BOR, SPI prescaler.
- **Round-1 LOW/INFO items never actioned; re-check whether still valid:**
  - F-012: D1/D2 LED colour unspecified with 1k.
  - F-018: U4 symbol TPS73625 vs value TPS73225.
  - F-019: file hygiene. The Eeschema re-saves may have fixed it.
  - F-022: no ESD on J1 CC1/CC2 or the J2/J3 debug headers.

## Decisions (user, 2026-11-17)
- Schematic fixes to plan:
  - S6-003: "0.1u" → "100n" on C32, C34, C38, C39, C42, C46.
  - S6-004: `in_bom no` on TP1–TP9 and JP1.
  - S6-005: D+, D-, UD+, UD- become local labels on usb; USB labels get consistent bidirectional shape.
- F-012: D1/D2 become red 0603 LEDs, keeping the 1k resistors (R19/R20). Set Value and LCSC/MPN fields.
- Docs (Orchestrator): S6-001 master-plan fix; PB3/PB4 note in the firmware doc; close F-018 (accepted) and F-019 (resolved); F-022 moves to Task 4.
- Task 3 (sourcing): S6-002 (MLCC voltage/dielectric).
- Info only: S6-007, S6-008 (bring-up scope check).

## Approvals (user, 2026-11-17, via chat)
- APPROVED: P-S6-001, P-S6-002, P-S6-003, P-S6-004, in that order. Cosmetic overlaps are reported only.
