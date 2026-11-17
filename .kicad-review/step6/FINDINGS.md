# Findings: Step 6 whole-schematic deep review (round 5)

**Counts:** CRITICAL 0, HIGH 0, MEDIUM 1, LOW 4, INFO 5.

## Plan target (Task 2 Step 6): MET
- ERC has 0 errors; the only warning is the intentional GND/GNDA one.
- This round raised no HIGH or error findings. The only open ones are SS-001 (MPN gate) and the tracked F-002 / S5-001.

## S6-001 [MEDIUM] Docs / bring-up — the master plan still treats GND/GNDA as the isolation barrier
- Location: `docs/superpowers/plans/2026-10-23-eeg-board-completion.md`
  - Task 1 Step 5 (around l.43)
  - Task 4 Step 2 (around l.82)
  - Task 6 Step 1 (l.104)
  - "+5V_ISO" in Task 1 Step 2 and Task 6 Step 1
- Evidence:
  - GND and GNDA are one net by design. The real barrier is GND_PRI↔GND and +5V_PRI↔+5V, and `+5V_ISO` doesn't exist.
  - The Task 6 continuity check (GND↔GNDA) would always beep and falsely report a failed barrier. The real check is never listed.
- Fixability: docs only
- Suggested fix:
  - Task 6: check for no DC path GND_PRI↔GND and +5V_PRI↔+5V (>10 MΩ).
  - Rename `+5V_ISO` to `+5V`.
  - Note that the analog/digital star point is a layout guideline only. A NetTie would be a separate schematic decision.
- Risk if changed: none.

## S6-002 [LOW] Power/analog — bulk MLCCs have no voltage rating or dielectric, so DC-bias derating is unbounded
- Location:
  - power: C11, C15, C16, C19, C20, C23, C27 (10u 0603)
  - analog_in: C41 (10u, 4.5 V across it), C43 (100u VCAP1), C35–C37 (1u, 5 V across them)
  - stm32: C9 (4.7u VCAP_1, needs ESR < 1 Ω)
- Evidence: a 10 µF 0603 6.3 V X5R keeps only about 30–40 % of its value at 5 V. The ADS1299 VREFP and VCAP1 minimums and the STM32 VCAP_1 ESR requirement must be met at bias.
- Fixability: manual (Task 3 part selection)
- Suggested fix:
  - Use X5R/X7R rated ≥ 10 V (16 V preferred) on the 5 V and 4.5 V nets.
  - Size C41 and C43 for their effective capacitance at bias.
  - Add Voltage and Dielectric fields.
- Risk if changed: low; a bigger case may be needed (footprint change at Step 7).

## S6-003 [LOW] BOM hygiene — "0.1u" and "100n" split the same part into separate BOM lines
- Location: analog_in C32, C34, C38, C39, C42, C46 ("0.1u" 0603) vs power C21 and C25 ("100n" 0603).
- Fixability: mcp-approval (Value)
- Suggested fix: set all six to "100n".
- Risk if changed: none.

## S6-004 [LOW] BOM — TP1–TP9 and JP1 have `in_bom yes` on the symbol
- Location: stm32 TP1–TP6 and JP1; analog_in TP7; power TP8 and TP9.
- Evidence: the footprints exclude these parts from a PCB BOM, but a BOM exported from the schematic lists 10 copper-only lines. JP1 also appears in the SS-001 missing_mpn list.
- Fixability: manual in Eeschema, or a scripted attribute edit
- Suggested fix: set `in_bom no` on all ten.
- Risk if changed: none.

## S6-005 [LOW] Netlist hygiene — primary-side USB nets use global labels that appear on only one sheet
- Location: usb.kicad_sch, global labels D+, D-, UD+ and UD- (2 instances each).
- Evidence:
  - These generic names sit on the non-isolated side. A future global `D+`/`D-` on any other sheet would silently merge across the isolation barrier.
  - The analyzer flags label-shape mismatches: USB_OTG_FS_DP/DM are bidirectional on stm32 but input on usb, and UD± are input on passive-only nets.
- Fixability: mcp-approval
- Suggested fix:
  - Make D+, D-, UD+ and UD- local labels.
  - Use bidirectional shape on all USB labels.
- Risk if changed: low; re-check the netlist afterwards.

## S6-006 [INFO] Firmware — reset states of the LED pins PB3 and PB4
- Evidence:
  - After reset, PB4 is NJTRST with an internal pull-up of about 40 kΩ, so D1 glows faintly (about 30 µA) until firmware takes the pin.
  - PB3 is JTDO/SWO, so SWO trace is unavailable. That's fine, because J3 is 2-wire SWD.
- Suggested fix: configure PB3 and PB4 as GPIO outputs early in init, and note this in docs/firmware.

## S6-007 [INFO] Footprint — J1 USB4105 16P pads A8 and B8 (SBU) have no symbol pin
- This is correct for a USB 2.0 sink (SBU is unused).
- At Step 7, check DRC. In Task 3, confirm the J1 MPN matches the USB4105 land pattern.

## S6-008 [INFO] Power integrity — the ~25 kHz LC post-filters (L1–L4, 3.3 µH) are lightly damped (Q ≈ 3)
- The risk is low.
- At bring-up, scope TP2, TP3 and TP9 for ringing. If needed, add a 1 Ω + 10 µF damping RC or replace the inductors with ferrite beads.

## S6-009 [INFO] Engineering pass — every block verified with no new issues
- **ADS1299:** pins and supplies, VCAP/VREF caps, tie-offs, straps and SPI pins all match §10.1.1.
- **STM32:** decoupling, VCAP_1, HSE, NRST, BOOT0 and the AF7 pin functions are correct.
- **ADuM3160:** pins, VDD1, PDEN/SPU, PIN/SPD, 24 Ω termination and CC 5k1 are correct. VBUS capacitance is 4.9 µF.
- **Power tree:** pinouts, the TPS60403 caps and the EN ties are correct.
- **Labels:** every global label is used on 2 or more sheets, and there is no local-name reuse. No duplicates, missing values or footprints, or wrong DNP flags.

## S6-010 [INFO] Analyzer and MCP false positives

| Item | Reason it is a false positive |
|---|---|
| SS-001 | Task 3 gate |
| CG-AUD J4 | intentional |
| RS-001 5V_L1 | net is fed from +5V via L1 |
| SJ-DET JP1 | intentional |
| DO-DET U2/U4/U6 caps | caps sit behind the inductors |
| RC-DET R35/C63 | bias loop, not a filter |
| RC-DET R1/C7 | NRST RC |
| RC-DET R25–R32/C64–C71 | the caps are DNP; S3-012 already covers the corner |
| PS-001 U5 PG | the TLV75733P has no PG pin |
| LA-AUD D4 "driver U1" | D4 is rail-driven |
| XL-DET Y1 CL_eff 10.5 pF | assumes 3 pF stray; the result is 10.5–12.5 pF, under 15 ppm |
| EP-AUD J2/J3/J5 | internal patient-side headers |
| USB dp/dm series R | R21–R24 sit behind U8/U9 by design |
| D1/D2/D4 wire crossings | LED bounding box |
| 8 overlap hits | #PWR symbols at pin ends |
| EMC 0 findings | not a pass; the EMC rules need the PCB |

## Round-1 re-check
- **F-012: still valid.** D1/D2 are "LED" with no colour on 1k, which only suits red or amber.
- **F-018: still valid but cosmetic.** U4 uses the TPS73625DBV symbol (the stock library has no TPS732xx); the pins match. Recommend closing it as accepted.
- **F-019: resolved** by the Eeschema re-save.
- **F-022: still valid.** No ESD on J1 CC1/CC2 or on J2/J3/J5. Optional; Task 4 EMC.

## Known open items (not re-raised)
- **F-002 / S5-001 (HIGH, Task 3):** the +5V rail must stay ≤ 5.25 V.
- **SS-001:** the MPN coverage gate.
- **F-023:** functional-grade isolation only.
- **Intentional:** GND/GNDA, J4, JP1.
- **S5-003 / S5-008:** order the TPS72325 M3 variant.
- **Firmware items:** see the firmware doc.
- **Manual and bring-up items from earlier rounds:** M-S3-*, M-S4-*, M-S5-*.
