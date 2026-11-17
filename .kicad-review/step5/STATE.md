# KiCad Review Loop: STATE (round 4, Task 2 Step 5: power sequencing)

- **Phase:** done. Verify 7 PASS, ERC 1. The user did the M-S5-001 tidy and Eeschema save (netlist identical). Committed.
- **Mode:** full loop, but this is mainly an analysis step. Schematic scope only. Base commit `66f244b`.
- **Round folder:** `.kicad-review/step5/`. Rounds 1–3 are closed.
- **PCB:** out of scope. It is unsynced and locked. No DRC.
- **Lock rule:** no `hardware/EEG_Kicad_Project/~*.kicad_sch.lck` before any write.
- **Tooling:**
  - kicad-cli 9.0.9 (ERC json, netlist kicadxml).
  - kicad-happy scripts: `/home/andrzej/.claude/plugins/marketplaces/kicad-happy/skills/kicad/scripts/`. This includes the analyzer's power-sequencing / regulator detection, and the `spice` skill if it is useful.
  - LCSC datasheet fetch: `python3 -I /home/andrzej/.claude/plugins/cache/kicad-happy/kicad-happy/2.3.2/skills/lcsc/scripts/fetch_datasheet_lcsc.py --search <MPN> -o <path>`.
  - Datasheets already on disk in `docs/datasheets/`: ads1299, tlv757p, TRN3, rm0390 (STM32F446 reference manual).
  - Subagents cannot write report .md files; the Orchestrator saves them.
- **Baseline ERC:** 1, the intentional GND/GNDA item.

## Task (plan Task 2, Step 5)
Verify power sequencing against ADS1299 §11.1 (SBAS499C lines ~4616–4655, Fig. 76, Table 30):
- "Before device power up, all digital and analog inputs must be low. At the time of power up, keep all of these signals low until the power supplies have stabilized."
- Then start CLK. The board uses the internal clock (CLKSEL high), so check how CLKSEL is tied.
- Wait tPOR (2^18 tCLK).
- Reset after tPOR or once VCAP1 > 1.1 V, whichever is longer.

The power tree (see the `project_power_design` memory facts in round-1 FINDINGS and the power sheet):
- USB 5 V → U7 TMU3-0511 isolated DC-DC → +5V.
- From +5V:
  - U5 TLV75733P → +3V3 (STM32 VDD and ADS1299 DVDD);
  - L1 → U2 TPS60403 charge pump → about −5 V;
  - U4 TPS73225 → +2V5 (AVDD);
  - U6 TPS72325 → −2V5 (AVSS).

Question to answer: in what order and with what timing do the rails come up, and do any ADS1299 digital or analog inputs see a voltage before or above its supplies? Abs max: digital inputs DGND−0.3 to DVDD+0.3; analog inputs AVSS−0.3 to AVDD+0.3.

Inputs to check:
- From the STM32: CS, START, RESET, PWDN, SCLK, DIN, CLK and CLKSEL.
  - The STM32 GPIOs are high-Z inputs during reset, except the SWD pins and BOOT0.
  - The Step 2 pulls are: CS 100k up to +3V3, START/RESET/PWDN 100k down (R15–R18).
- Electrode inputs, through 4.99k / TVS, and the BIAS drive while AVDD/AVSS are not yet up.
- VREFP/VREFN and VCAP pins: only caps.

Also cover:
- whether the regulators' EN pins or soft-starts give a defined order;
- the charge-pump start-up delay and the −2V5 ramp vs the +2V5 ramp;
- inrush and soft-start interaction with the isolated DC-DC current limit;
- whether AVDD − AVSS ever exceeds 5.5 V abs max, or reverse-biases;
- the STM32 POR/BOR vs the +3V3 ramp;
- any need for a supervisor or a delayed-enable;
- the firmware power-up procedure needed: wait times, RESET pulse width (tRST), the SDATAC before configuring, and PWDN handling.

Round-1 F-013 (LOW, docs): the Step 2 spec's wording on the CS pull-up contradicts §11.1. It is relevant here, so resolve it in this round.

## Decisions (user, 2026-11-17)
- Hardware to plan: S5-004 (100k pull-downs on SPI1_SCK/SPI1_MOSI at U3), S5-002 (test point on VCAP1), S5-007 (Schottky across U6 IN–OUT, per TPS723 Fig. 7-1).
- NR caps: keep C24 1 µF / C25 100 nF. Specify the TPS72325 new-die (M3) orderable in Task 3 sourcing. Close F-011 as intentional (lower noise; 250 ms firmware wait).
- Docs, done by the Orchestrator: fix the F-013 wording in the Step 2 spec; write `docs/firmware/ads1299-power-up.md`.
- S5-001: folded into F-002. The converter requirement is now +5V ≤ 5.25 V (TPS60403 recommended max).
- Extras approved for planning (user, 2026-11-17), after a proposal:
  - E1 (F-016): 100k pull-down on SPI1_MISO.
  - E2 (F-017): test points on the isolated +5V and on −5V.
  - E3 (S5-001 bring-up): 0402 0 Ω link between L1's output and the U2/U4 input node (Net-(U2-IN)), so +5V can be measured before the charge pump and U4 see it. The BOM marks it fitted; leaving it unfitted for first power-up is a bring-up option.
  - E4: green power LED plus series resistor on +3V3, about 1 mA.

## Approvals (user, 2026-11-17, via chat)
- APPROVED: P-S5-001 … P-S5-007 (all 7), including the ⚠ wire delete in P-S5-006.
- Cosmetic overlaps: report only; the user tidies them by hand and saves in Eeschema before commit.
