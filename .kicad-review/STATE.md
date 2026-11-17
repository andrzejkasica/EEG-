# KiCad Review Loop: STATE

- **Phase:** 6 complete (REVIEW.md written 2026-11-17). Iter 1: 9 PASS; iter 2: 4 PASS. F-002 on hold. Loop finished for F-001..F-010.
- **Scope (user, 2026-11-17):** CRITICAL+HIGH+MEDIUM = F-001..F-010.
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

## Manual decisions (user, 2026-11-17)
- F-002: replace U7 with a REGULATED isolated 5 V DC-DC. Fixer proposes candidates (package, isolation >=1.5 kV, >=200 mA, KiCad symbol/footprint availability); user picks.
- F-003: DELETE R3-R6. Keep fixed LDOs; NR pins keep only their caps.
- F-004: Fixer proposes footprints for all: L1-L4 Inductor_SMD:L_0805_2012Metric; J1 a library USB-C footprint matching GCT USB4135-GF-A / USB4105 with pads matching the symbol; SW1 a common SMD tact switch. Each listed for approval. R3-R6 resolved by F-003.
- F-009: add spec properties now (Y1: CL=12pF, ESR<=60R, C0<=3pF, 3225; C48/C49 value '15p C0G'). Crystal MPN in Task 3. No 0R on OSC_OUT.

## Approvals (user, 2026-11-17, via chat)
- APPROVED: P-001, P-003, P-004, P-005, P-006, P-007, P-008, P-009, P-010.
- Destructive actions explicitly approved: P-001 (2 wire deletes), P-003 (delete R3-R6 + 9 wires).
- P-002: ON HOLD (user, 2026-11-17). TRN 3-0511 datasheet (docs/datasheets/TRN3.pdf) passes M-001 checks but is 9 V-nominal, 4.5 V min input: too little headroom on USB VBUS (can sag to 4.40 V). User wants a regulated 5 V-nominal-input isolated part, to be found in Task 3. F-002 stays OPEN. Do not apply P-002.
- Execution order: P-003 → P-004 → P-001 → P-005 → P-006 → P-007 → P-008 → P-009 → P-010 → P-002.

## Process notes
- The harness blocks subagents from writing report files ("return findings as text"). The Orchestrator saves the returned content into `.kicad-review/` verbatim. The Fixer still writes design changes via MCP; only report files are affected.

## Iteration 2 queue (user approved 2026-11-17)
- M-004 → add power:PWR_FLAG on VDD1_ISO1 (option a). APPROVED.
- M-005 → delete wire 0fe28947 (199.39,48.26)→(208.28,48.26) ⚠ DESTRUCTIVE and replace with a VDD1_ISO1 local label on U9 pin 3 (option a). APPROVED incl. the wire delete.
- N-002 → move Value fields of #PWR0104–#PWR0112 to standard offsets (above + arrows, below GND). APPROVED (user, 2026-11-17).
- N-003 → wrap the two usb.kicad_sch notes at (200.66,115.57)/(200.66,120.65) into 2–3 lines and move them left inside the A4 frame. APPROVED. Allowed: delete+re-add of those two text items only (⚠ DESTRUCTIVE, text only).
- Iteration-1 verify: 9 PASS / 0 FAIL / 1 REGRESSION (R-001 = ERC VDD1, kept; fixed by M-004). See VERIFY.md.
