# KiCad Review Loop: STATE

- **Phase:** 1 complete. Next: Phase 1 → 2 handoff, asking the user which findings to plan. Iteration 1 of 3.
- **Phase 1 result:** 23 findings (CRITICAL 0, HIGH 4, MEDIUM 6, LOW 9, INFO 4). See FINDINGS.md and BASELINE.md.
- **Mode:** full loop, **schematic scope only**.
- **Started:** 2026-11-16.
- **Audit trail:** the user chose to commit `.kicad-review/` to git.

## Project
- Repo: `/home/andrzej/Documents/Repos/EEG-`, branch `task2-schematic-gaps`.
- Project: `hardware/EEG_Kicad_Project/EEG_Kicad_Project.kicad_pro`.
- Root schematic: `EEG_Kicad_Project.kicad_sch`. Sheets: `analog_in`, `stm32`, `power`, `usb` (`*.kicad_sch`).
- PCB: `EEG_Kicad_Project.kicad_pcb`. **Out of scope.** It is deliberately unsynced and uncommitted (it gets re-synced at the end of Task 2), and layout has not started. Do not run DRC or PCB analyzers, and do not touch the PCB.
- Checkpoint ref: commit `c348402` (Step 2). No tag created.
- Fab target: JLCPCB (per `docs/superpowers/plans/2026-10-23-eeg-board-completion.md`).

## Tooling
- MCP backend: `ipc`. KiCad 9.0.9 is running (pid 7036). The PCB editor is open, holding a lock on the `.kicad_pcb`.
- **Schematic editor must be closed during writes.** Before any write, check that `hardware/EEG_Kicad_Project/~EEG_Kicad_Project.kicad_sch.lck` does not exist. If it exists, stop and ask the user.
- kicad-happy scripts: `/home/andrzej/.claude/plugins/marketplaces/kicad-happy/skills/kicad/scripts/` (`analyze_schematic.py`). Other skills: `emc`, `spice`, `datasheets`, `jlcpcb`.
- `kicad-cli` 9.0.9 is available. Use `kicad-cli sch erc` and `kicad-cli sch export netlist` for ground truth.
- Known MCP quirk: the server may re-save `.kicad_sch` files with normalized formatting (e.g. `127.0` becomes `127`). This is harmless, and the netlist stays identical.

## Design context
- EEG front end: ADS1299 (U3), bipolar ±2.5 V analog supply, DVDD +3.3 V, internal clock, 8 channels planned.
- MCU: STM32F446RETx LQFP64 (U1).
- The whole board sits behind an ADuM3160 USB isolator and an isolated DC-DC (U7 TMU3-0511).
- GND and GNDA are intentionally merged into one net.
- Datasheets live in `docs/datasheets/`. Plans live in `docs/superpowers/plans/`. Steps 1 and 2 are done; Step 3 (analog inputs, SRB, BIAS, ESD) is next and is **not** yet drawn.

## Known non-issues (do not raise as findings)
- `VM-001` on D+/D- (5.0 V/3.3 V domain crossing) is a false positive. However, the earlier reason given here ("VDD1 = 5 V side") was wrong: VDD1 must be 3.3 V. See F-001.
- `SS-001`: 0% MPN coverage is expected. MPN sourcing is Task 3.
- `multiple_net_names` GND/GNDA (#PWR017 / #PWR024) is intentional.
- ERC `pin_not_connected` / `pin_not_driven` on U3 pins IN1P-IN8N, SRB1, SRB2, BIASOUT, BIASINV, BIASIN, BIASREF are Step 3 work, not drawn yet. Record these as a single INFO entry.

## Prior findings to merge (independent Step 2 review, 2026-11-16)
Add each as a finding unless the fresh review already raises it:
1. Y1 crystal not specified: needs ESR ≤ 60-80 Ω, CL 12 pF, C0 ≤ 3 pF; C48/C49 need C0G dielectric. Optionally a 0 Ω footprint on OSC_OUT. (MEDIUM)
2. No 4.7 µF bulk cap on +3V3 near U1 VDD (RM0390 Fig. 8: 12×100 nF + 1×4.7 µF). (MEDIUM)
3. D1/D2 LED colour unspecified. 1k suits red; it is too dim for green/blue. (LOW)
4. The patient-safety warning (SWD/UART headers are on the patient side of the isolation barrier) exists only in the spec. Add a schematic text note on `stm32.kicad_sch`. (MEDIUM, safety documentation)
5. Step 2 spec wording on the CS pull-up contradicts SBAS499C §11.1. The circuit is fine; the doc needs a fix. (LOW, docs: `docs/superpowers/plans/2026-11-16-step2-mcu-link.md`)
6. SPI1_MISO floats while CS is high. Add a firmware note: enable the PA6 pull-down. (LOW, docs)

## Approvals
(none yet)

## Process notes
- The harness blocks subagents from writing report files ("return findings as text"). The Orchestrator saves the returned content into `.kicad-review/` verbatim. The Fixer still writes design changes via MCP; only report files are affected.
