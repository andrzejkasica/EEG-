# EEG Board Completion Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Take `hardware/EEG_Kicad_Project` from its current state (power supply and USB drawn with isolation; ADS1299 unwired; STM32 only partly connected) to an ordered, assembled, bring-up-tested board.

**Architecture:** USB-powered with a galvanic isolation barrier. Non-isolated side: USB connector, magnetics/ESD, ADuM3160BRWZ (USB isolator). Isolated side: STM32F446, ADS1299, the existing ±2.5V/-5V analog supply chain, powered from an isolated 5V DC-DC (TMU3-0511) instead of USB VBUS directly. Electrodes only ever touch the isolated side.

**Tech Stack:** KiCad 8, `kicad-happy` plugin (schematic/PCB analysis, BOM, EMC, SPICE, fab prep), JLCPCB for fab/assembly.

**Spec:** This plan is self-contained — no separate design doc was written (brainstorm was short, single open decision resolved in chat: USB-powered + isolated, per project memory `project_power_design.md`).

## Global Constraints

- Isolation barrier must be a single, continuous split — no second accidental path (shared shield, mounting screw, connector) bridging isolated/non-isolated ground.
- GND and GNDA are merged into one net on the isolated side (the datasheet split is optional), so `GND` is the isolated ground and `GND_PRI` the USB-side ground. They must never connect.
- No medical certification target — but maintain basic creepage/clearance at the isolation barrier since electrodes contact the scalp while USB-connected to a PC.
- BOM must reach 100% MPN coverage before ordering (pre-fab gate, currently 0%).

## Review Focus

- Isolation barrier accidentally bridged by a second ground path (connector shield, test point, mounting hardware) — invisible to ERC, only caught by manual net-trace + layout inspection.
- USB D+/D- and electrode input ESD protection — floating/unprotected external-facing pins are common oversights.
- Barrier creepage/clearance on PCB layout not meeting the isolator's rated working voltage.
- Power sequencing across the isolation boundary (isolated 5V DC-DC must be stable before ADuM3160 and the LDO chain enable).

---

### Task 1: Add the isolation barrier to the schematic

**Files:**
- Modify: `hardware/EEG_Kicad_Project/power.kicad_sch` (isolated DC-DC)
- Modify: `hardware/EEG_Kicad_Project/usb.kicad_sch` (ADuM3160 placement relative to USB connector)

**Interfaces:**
- Isolated DC-DC output net: new `+5V_ISO` rail, feeds the existing TPS60403/TPS72325/TPS73225/TLV75709 chain (replaces their current `+5V` source).
- ADuM3160: USB-host-side pins stay on non-isolated `+5V`/`GND`; USB-device-side pins (to STM32) move to `+5V_ISO`/isolated `GND`.

- [ ] **Step 1:** Decide and record the isolated DC-DC part (RECOM R-78E5.0 or equivalent, isolated ≥1kV working voltage, enough current margin for the whole analog+digital load). Pull its datasheet via `digikey`/`mouser` skill.
- [ ] **Step 2:** Place the DC-DC in `power.kicad_sch`, rewire the existing `+5V`-sourced chain (TPS60403, TLV75709) to the new `+5V_ISO` net.
- [ ] **Step 3:** Place ADuM3160BRWZ in `usb.kicad_sch` between the USB connector and STM32's USB pins, splitting the net into non-isolated (`USB_DP_RAW`/`USB_DM_RAW`) and isolated (`USB_DP_ISO`/`USB_DM_ISO`) halves.
- [ ] **Step 4:** Resolve the TLV75709 vs TLV757P33 discrepancy — pick one, update the schematic and the project memory note.
- [ ] **Step 5:** Run `kicad-happy:kicad` schematic analyzer (`analyze_schematic.py`). Expected: no new ERC errors; confirm the two ground domains (`GND` non-isolated, `GNDA` isolated) still have exactly one tie point at U3.
- [ ] **Step 6:** Commit: `git commit -m "add USB isolation barrier (ADuM3160 + isolated 5V DC-DC)"`

### Task 2: Finish the schematic

Revised 2026-11-04 after ERC triage: the ADS1299 had never been wired, so this task is much larger than first written. Decisions: 8 channels wired, shared reference on SRB1 plus BIAS drive electrode, internal ADS1299 clock (CLKSEL high).

**Files:**
- Modify: `hardware/EEG_Kicad_Project/analog_in.kicad_sch`
- Modify: `hardware/EEG_Kicad_Project/stm32.kicad_sch`
- Modify: `hardware/EEG_Kicad_Project/usb.kicad_sch`
- Modify: `hardware/EEG_Kicad_Project/power.kicad_sch`

- [x] **Step 0:** Replace U5 with the 3.3V TLV75733P (`772ae0a`).
- [ ] **Step 1:** Wire ADS1299 power, reference, decoupling and tie-offs, per `2026-11-04-ads1299-step1-wiring.md`.
- [ ] **Step 2:** Connect the STM32: SPI1 plus CS, DRDY, START, RESET, PWDN to U3; 8MHz HSE crystal (per CubeMX); SWD header; UART header on PB10/PC5 (schematic labels are on the wrong pins, PC10/PC11); LEDs on PB3/PB4; test points.
- [ ] **Step 3:** Add the electrode connector and input network with ESD protection for all 8 channels, SRB1 reference and BIAS drive, including bias amp feedback parts.
- [ ] **Step 4:** Route U9 through U8's pass-through pins (`UD+`/`UD-`), decide R3-R6, add `PWR_FLAG`s, flag spare STM32 pins no-connect.
- [ ] **Step 5:** Verify power sequencing against ADS1299 §11.1: digital and analog inputs low until supplies settle.
- [ ] **Step 6:** Run `kicad-cli sch erc` and the `kicad-happy:kicad` deep review. Expected: zero ERC errors and no `high`/`error` findings besides the MPN-coverage gate.
- [ ] **Step 7:** Re-sync the PCB from the schematic and commit.

### Task 3: Source parts and close the BOM

**Files:**
- Modify: all `.kicad_sch` files (MPN property on each symbol)

- [ ] **Step 1:** Run `kicad-happy:bom` to identify every unsourced line (currently 15 lines, 0% MPN coverage).
- [ ] **Step 2:** Search DigiKey (primary) / Mouser / LCSC for each part, write MPNs back via the `bom` skill.
- [ ] **Step 3:** Re-run the sourcing gate (`SS-001`). Expected: 100% MPN coverage, finding clears.
- [ ] **Step 4:** Sync datasheets for all newly-sourced MPNs (`digikey`/`lcsc` sync script) for the deep-review pass to re-verify pin usage.
- [ ] **Step 5:** Commit: `git commit -m "complete BOM sourcing, 100% MPN coverage"`

### Task 4: PCB layout and routing

**Files:**
- Modify: `hardware/EEG_Kicad_Project/EEG_Kicad_Project.kicad_pcb`

- [ ] **Step 1:** Place isolation-barrier components (ADuM3160, isolated DC-DC) with the clearance/creepage their datasheets specify between isolated and non-isolated copper/silkscreen — add a milled slot or explicit keepout if the working voltage calls for it.
- [ ] **Step 2:** Route power: wide traces for the analog supply chain, continuous `GND`/`GNDA` planes with the single tie point under/near U3.
- [ ] **Step 3:** Route USB as a controlled-impedance differential pair on both sides of the isolator; keep each half entirely within its own ground domain.
- [ ] **Step 4:** Place decoupling caps per the standard rule (same layer, no via between cap and IC pin, closest to the pin).
- [ ] **Step 5:** Fill zones, run `kicad-happy:kicad` PCB analyzer (`analyze_pcb.py --full`) + cross-domain analyzer. Expected: no DRC errors, no `CC-001`/`EG-001`/`DA-001`/`XV-00x` findings.
- [ ] **Step 6:** Run `kicad-happy:emc` pre-compliance. Expected: no critical findings on the isolation barrier, switching charge pump harmonics, or USB diff-pair skew.
- [ ] **Step 7:** Commit: `git commit -m "complete PCB layout and routing"`

### Task 5: Fab and assembly prep

**Files:**
- Create: `hardware/EEG_Kicad_Project/fab/` (gerbers, drill, BOM/CPL exports)

- [ ] **Step 1:** Run `kicad-happy:jlcpcb` DFM check against the current layout.
- [ ] **Step 2:** Export gerbers/drill/BOM/CPL via the `bom` skill's JLCPCB workflow.
- [ ] **Step 3:** Review JLCPCB basic-vs-extended part classification; swap any extended part you don't want assembly cost on.
- [ ] **Step 4:** Get user sign-off before placing the actual order (real money, irreversible once parts are pulled).

### Task 6: Bring-up and test

**Files:**
- Create: `docs/bring_up_test_plan.md`

- [ ] **Step 1:** Write a short bring-up checklist: power-on sequence, rail voltage checks (+5V, +5V_ISO, ±2.5V, -5V, +3V3) at each test point, isolation continuity check (confirm *no* DC path between `GND` and `GNDA` — a multimeter beep here means the barrier failed).
- [ ] **Step 2:** Power up incrementally (bench supply current-limited) before populating the STM32/ADS1299, verify each rail.
- [ ] **Step 3:** Flash minimal firmware, confirm USB enumerates through the isolator.
- [ ] **Step 4:** Confirm ADS1299 reads plausible EEG-band noise with shorted/dummy inputs before connecting real electrodes.
- [ ] **Step 5:** Commit: `git commit -m "add bring-up test plan"`
