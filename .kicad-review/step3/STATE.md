# KiCad Review Loop: STATE (round 2, Step 3 diff review)

- **Phase:** done. M-S3-006 + M-S3-002 done by the user; P-S3-SWD label revert applied (ERC 35). Committed.
- **Mode:** Diff review, **schematic scope only**. The change under review is the uncommitted Step 3 analog front end, compared against commit `b3af525`.
- **Started:** 2026-11-17. The user asked for this review before committing Step 3.
- **Round folder:** `.kicad-review/step3/`. All handoff files for this round live here. Round 1 (F-001..F-023) lives in `.kicad-review/*.md` and is closed, except F-002 and the LOW/INFO findings. Do not re-raise round-1 findings unless Step 3 changes them.

## Project
- Repo: `/home/andrzej/Documents/Repos/EEG-`, branch `task2-schematic-gaps`.
- Project: `hardware/EEG_Kicad_Project/EEG_Kicad_Project.kicad_pro`. Root `EEG_Kicad_Project.kicad_sch`. Sheets: `analog_in`, `stm32`, `power`, `usb`.
- **Changed files:**
  - `analog_in.kicad_sch`
  - new `EEG_custom.kicad_sym` (symbol `TPD4E1B06DCK`)
  - new project `sym-lib-table`
- **Base copy of the b3af525 sheets:** `.kicad-review/step3/base/`. Analyze it as a project to get a diff.
- Pre-wiring snapshot: `.kicad-review/snapshots/step3-pre/analog_in.kicad_sch`.
- **Spec:** `docs/superpowers/plans/2026-11-17-step3-analog-front-end.md`. Its design intent and decisions (user-approved) are binding unless a finding shows they are wrong.
- **PCB is out of scope.** It is unsynced and uncommitted, and its editor holds a lock. Do not run DRC or PCB analyzers, and do not touch the PCB.
- Fab target: JLCPCB.

## Tooling
- **Schematic editor must be closed for writes.** Before every write, check `hardware/EEG_Kicad_Project/~EEG_Kicad_Project.kicad_sch.lck` is absent.
- **kicad-happy scripts:** `/home/andrzej/.claude/plugins/marketplaces/kicad-happy/skills/kicad/scripts/`. Other skills: `spice` (filter checks), `datasheets`.
- **kicad-cli 9.0.9:**
  - `kicad-cli sch erc --format json --units mm`
  - `kicad-cli sch export netlist --format kicadxml`
- **Datasheets:**
  - `docs/datasheets/ads1299_datasheet.txt` (SBAS499C; Fig. 18 is the input mux, Fig. 68/73 the bias and referential montage, §10.1.1 unused pins)
  - TVS clone datasheet: `/tmp/claude-1000/-home-andrzej-Documents-Repos-EEG-/2322c6a4-79fd-4009-8cf0-42fae3306225/scratchpad/ds/tpd4e1b06_mcc.pdf` (TECH PUBLIC TPD4E1B06DCKR-TP, image PDF). Its pinout is 1 IO1, 2 IO2, 3 GND, 4 IO3, 5 IO4, 6 NC. Leakage is 0.9 nA typical at 2.5 V, with no maximum given.
- **Harness quirk:** subagents cannot write report .md files. They return the text, and the Orchestrator saves it.
- **MCP field angles:** on rotated symbols, field angles behave oddly. Render the sheet to check.

## Design context
- **ADS1299 (U3) inputs:**
  - Referential montage: 8 channels on IN1P–IN8P, reference electrode to SRB1 (MISC1.SRB1 = 1), BIAS electrode driven from BIASOUT with BIASREF_INT = 1.
  - IN1N–IN8N, SRB2, BIASIN and BIASREF have no-connect flags.
- **Supplies:** bipolar ±2.5 V (AVDD +2V5, AVSS −2V5). GND and GNDA are one net.
- **Isolation:** the board is behind an ADuM3160 and an isolated DC-DC. The isolation is functional grade only (round-1 F-023). There is no medical certification target.

## Focus questions from the user
1. Is the 100 kΩ series resistor on the BIAS electrode right? Consider bias-loop stability and drive with electrode impedance, and patient current: the bias amp's short-circuit current is 1.1 mA.
2. Are the IN1N–IN8N no-connect flags right in SRB1 mode? Check Fig. 18. The alternative is §10.1.1's rule that unused inputs go to AVDD.
3. Is the TVS choice right? It is a clone (TECH PUBLIC/UMW) of TI TPD4E1B06, with leakage specified only as a typical value. Does leakage matter with DC-coupled electrodes? Is the clamp level OK for ±2.5 V signals? Are there better low-leakage options?
4. Filter values: 4.99 kΩ series with 4.7 nF C0G from INxP to the filtered SRB1 node, about 3.4 kHz differential. Check against Fig. 73, the ADS1299 noise and input-current effects, and RF/EMI.
5. Is the custom symbol correct (pin numbers vs the SOT-363 footprint pads), and are the footprints right?

## Decisions and scope (user, 2026-11-17)
- In scope: S3-001, S3-002, S3-003, S3-004, S3-005, S3-007, plus the spec text corrections S3-003/S3-009/S3-012 (doc only, done by the Orchestrator).
- S3-002: change C63 1.5n → **10 nF C0G**, keeping the 0603 footprint. Matches TI EVM 392k/10n. Bench-check the BIASOUT step at bring-up.
- S3-003: **tie IN1N–IN8N to SRB1_F**, replacing the 8 no-connect flags. Reason: the board then works with SRB1 on or off, and the chip can detect a loose REF electrode through N-side lead-off.
- S3-001: the firmware note must reflect S3-003. INxN is tied to SRB1_F, so LOFF_SENSN may be used for REF detection on one channel; do NOT say "INxN NC".
- S3-004: 9 DNP 470 pF C0G 0402 caps, CH1–CH8 and SRB1_F to GND.
- S3-005: LCSC/MPN/Tolerance fields on the new parts (and on new parts added in this round).
- S3-007: tidy the C55–C62 reference fields.
- Not in scope: S3-006 (THT header, user decides at order time) and S3-008 (user does an Eeschema open+save before commit). Both are listed in MANUAL_ACTIONS.

## Approvals (user, 2026-11-17, via chat)
- APPROVED: P-S3-002, P-S3-003 (including the ⚠ scripted removal of 8 no-connects), P-S3-004 (including the scripted DNP edit), P-S3-005, P-S3-001.
- NOT approved: P-S3-007. **The user will fix schematic layout overlaps themselves** in Eeschema. The Fixer must NOT iterate on cosmetic field placement for any fix. Instead, it renders the result and reports any text overlaps in the log for the user. The connectivity-related placement rules still apply: labels on the correct pins, no wires through bodies.
- Order: P-S3-002 → P-S3-003 → P-S3-004 → P-S3-005 → P-S3-001.
