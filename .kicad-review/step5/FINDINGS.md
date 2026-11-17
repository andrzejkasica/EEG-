# Step 5 findings: power sequencing vs ADS1299 §11.1

**Count:** HIGH 1, MEDIUM 1, LOW 6, INFO 13.

## S5-001 [HIGH] Power — the TPS60403 (U2) limit on the unregulated +5V is 5.25 V recommended and 5.5 V abs max on IN and on −OUT (extends F-002)
- Source: TPS60403 SLVS324C §7.1/§7.3; TMU3 datasheet; round-1 F-002.
- Location: power.kicad_sch, U2 (fed from +5V via L1). The same node feeds U4 IN/EN.
- Evidence:
  - Recommended VI is 1.8–5.25 V. Abs max is IN −0.3…5.5 V and OUT −5.5…+0.3 V. Because VO = −VI, a +5V above 5.5 V breaks both abs max limits at once.
  - The TMU3 is unregulated (±3.5 % at 60 % load, rising at light load). Even nominal VBUS × 1.035 = 5.18 V leaves only 70 mV of margin. F-002 assumed a 5.5 V limit; the real recommended limit is 5.25 V.
  - TPS732 and TLV757P are rated 5.5 V recommended and 6 V abs max.
- Fixability: manual
- Suggested fix: resolve with F-002, using either a regulated isolated converter or a ≈4.8–5.0 V post-regulator ahead of L1/U5. At minimum, measure the no-load +5V at bring-up before fitting U2.
- Risk if changed: medium. It changes the isolated power stage, so re-check the timeline afterwards.

## S5-002 [MEDIUM] Firmware/timing — VCAP1 > 1.1 V dominates the reset timing and is not observable by the MCU
- Source: ADS1299 §11.1, Fig. 76 note 1, Fig. 25, Table 30, pin table (VCAP1 100 µF).
- Location: analog_in, C43 100 µF on VCAP1 to −2V5. There is no test point.
- Evidence:
  - The reset must come after max(tPOR, VCAP1 > 1.1 V).
  - tPOR = 2^18 tCLK = 128 ms (131 ms worst case).
  - VCAP1 τ ≈ 9.8 kΩ (Fig. 25 R1) × 100 µF ≈ 0.98 s, so 1.1 V is reached in about 1.5–2.4 s (est.; the final voltage is not given in the DS).
  - Firmware that waits only tPOR resets too early.
  - Charging probably starts at PWDN↑ (§9.4.3).
- Fixability: info-only (firmware). Optional mcp-approval: a test point on VCAP1.
- Suggested fix: wait ≥3 s after PWDN↑ before the reset pulse. At bring-up, scope VCAP1 vs AVSS and set the wait to 2× the measured time, never below 150 ms.
- Risk if changed: none.

## S5-003 [LOW] Power — the −2V5 ramp depends on which TPS723 die ships (legacy vs new), so the AVDD/AVSS ramp completion order is undefined (relates to F-011)
- Source: TPS723 SLVS346E §5.5, §6.3.7, §9 ordering note; TPS732 §6.3.1.
- Location: U6 TPS72325DBVT with C25 100 nF; U4 TPS73225DBVT with C24 1 µF.
- Evidence:
  - The enable order is defined: U4 at +5V ≈ 1.7 V, U6 after −5V passes −2.1/−2.4 V.
  - The ramp order is not defined. AVDD τ is 27 ms. AVSS τ is 40 ms on the new die, or about 4.5 ms on the legacy die.
  - Neither case breaks an abs max. The plain MPN (no M3 suffix) can ship either die.
- Fixability: manual
- Suggested fix:
  - Specify the M3 (new-die) orderable for U6.
  - When resolving F-011, choose similar τ values, for example C24 100 nF (2.7 ms) and C25 10 nF (4 ms). Both rails would then settle in under 20 ms.
  - Keep EN = IN on both, so U4 is always enabled first.
- Risk if changed: low (noise and start-up only).

## S5-004 [LOW] Digital — SCLK and DIN float during MCU reset; §11.1 "inputs low" is not met literally
- Source: ADS1299 §11.1; STM32F446 DS (I/Os float during and after reset).
- Location: SPI1_SCK (PA5 to U3.40, TP6) and SPI1_MOSI (PA7 to U3.34) have no pulls.
- Evidence: there is no abs max risk, because the only drivers are on the same +3V3. With CS held high the SPI ignores both lines. This is a literal deviation from §11.1, plus floating-CMOS input current.
- Fixability: mcp-approval
- Suggested fix: optional 100k pull-downs at U3 on SPI1_SCK and SPI1_MOSI. Pulling down matches SPI mode-1 idle.
- Risk if changed: negligible.

## S5-005 [LOW] MCU — BOR is off by default
- Source: STM32F446 DS Table 21.
- Location: U1 option bytes.
- Evidence: reset releases at VDD ≈ 1.72 V plus 0.5–3 ms. +3V3 settles in about 1 ms, so this is fine in practice, but it is not guaranteed if +5V ramps slowly.
- Fixability: info-only (firmware)
- Suggested fix: set BOR_LEV = 3 (2.92 V).
- Risk if changed: none.

## S5-006 [LOW] Power — the TPS732 (EN = IN) may overshoot if the +5V ramp is slower than a few ms; verify at bring-up
- Source: TPS732 §6.3.3, §6.3.2.
- Location: U4.
- Evidence: TMU3 start-up is ≤5 ms. Any overshoot is bounded by VIN, and it happens while AVSS is near 0 V. Do not move EN to a later signal, because U4 must be enabled before the negative rail.
- Fixability: info-only
- Suggested fix: at bring-up, capture +5V, +2V5 and −2V5 at no load and at a dummy load. Accept if +2V5 ≤ 2.6 V and AVDD − AVSS ≤ 5.2 V.
- Risk if changed: n/a

## S5-007 [LOW] Power — at power-down, the TPS723 (U6) body diode may conduct if −5V collapses faster than −2V5
- Source: TPS723 §6.3.1, §7.1.4, Fig. 7-1.
- Location: U6 (about 22 µF on OUT vs about 12 µF on IN).
- Evidence: this matches TI's listed reverse-current case (large COUT, input collapsing at light load). The charge is about 55 µC, so the stress is mild.
- Fixability: manual
- Suggested fix: an optional Schottky between U6 IN and OUT, per TI Fig. 7-1. Otherwise accept it after a bring-up power-down capture.
- Risk if changed: low.

## S5-008 [LOW] Power — the TPS723 legacy-die input-cap range is 0.1–2.2 µF, but U6 IN has 12.2 µF
- Source: TPS723 §5.3.
- Location: C16 10u + C22 2u2 on −5V.
- Evidence: this is irrelevant if the new die (M3) is specified.
- Fixability: manual
- Suggested fix: specify the M3 orderable, the same action as S5-003.
- Risk if changed: none.

## INFO (pass)

- **S5-INFO-01: digital inputs vs DVDD — PASS.**
  - Every pull is referenced to +3V3 = DVDD or to GND, and all active drivers are on +3V3.
  - START, RESET and PWDN stay low through the ramp and MCU reset.
- **S5-INFO-02: analog inputs, BIAS, VREF and VCAP vs AVDD/AVSS — PASS.**
  - The electrodes sit at about GND, which is always inside the window, because AVDD ≥ 0 ≥ AVSS throughout the ramp.
  - The clamp current is at most 60 µA, against a 10 mA limit.
  - BIASOUT is high-Z while PWDN is low.
- **S5-INFO-03: AVDD − AVSS ≤ 5.5 V — PASS.**
  - The steady-state worst case is 5.10 V, and the difference stays ≤ 5.0 V during the ramp.
  - This depends on +5V ≤ 5.5 V (S5-001) and on no overshoot (S5-006).
- **S5-INFO-04: AVSS never above GND, AVDD never below GND — PASS.**
  - U4 is enabled before U6, as the TPS732 requires.
  - The TPS723 new die has an output pull-up before enable.
  - PWDN is low, so the load is in the µA range.
- **S5-INFO-05: DVDD vs AVDD order — PASS.**
  - The datasheet sets no requirement.
  - DVDD is final at about 1 ms; AVDD and AVSS settle at about 125 and 184 ms.
- **S5-INFO-06: start-up current vs the TMU3 limit — PASS.**
  - Total capacitance is about 37 µF, against a 2200 µF limit.
  - The +3V3 inrush is about 57 mA.
- **S5-INFO-07: STM32 POR and VDD ramp — PASS.**
  - The ramp rate is about 167 µs/V, against a ≥20 µs/V limit.
  - The ADS control pins float during reset and are defined by R15–R18.
  - No external supervisor is needed.
- **S5-INFO-08: CLKSEL and CLK — PASS.**
  - CLKSEL is strapped high (internal oscillator), and CLK is pulled down (3-state with CLK_EN = 0).
  - tPOR starts at PWDN↑, plus 20 µs.
- **S5-INFO-09: VREF and VCAP caps — PASS.** All values match the datasheet, and all return to −2V5.
- **S5-INFO-F013: round-1 F-013 settled — why CS is pulled to DVDD.**
  - What §11.1 guards against is an input driven above an unpowered supply, which back-powers the device through its clamps. CS is pulled to the same +3V3 as DVDD, so it can never exceed DVDD + 0.3 V.
  - CS held high keeps the SPI reset and DOUT high-Z (§9.5.2.1), so the floating SCLK/DIN cannot clock in data. It also keeps MISO uncontended during boot.
  - Power-up gating is done by RESET and PWDN, which are held low.
  - Fix (docs): replace line 17 of `docs/superpowers/plans/2026-11-16-step2-mcu-link.md` with this reasoning.

### S5-INFO-TL: power-up timeline estimate
t = 0 is the start of the +5V ramp.

| Time | Event | Source |
|---|---|---|
| ≤5 ms before t = 0 | TMU3 output starts | DS |
| 0.26 ms | U5 out of UVLO | DS |
| 0.34 ms | U4 enabled; NR τ = 27 ms starts | DS / est. |
| 0.3–0.4 ms | U2 starts pumping | DS / est. |
| 0.5 ms | STM32 POR threshold | DS |
| 0.5–0.9 ms | U6 enabled | DS |
| 1.0–1.3 ms | +3V3 in regulation | DS / est. |
| 1–4 ms | STM32 first instruction | DS / est. |
| about 2 ms | −5V settled | est. |
| 59 ms | AVDD at 90 % | est. |
| 88 ms | AVSS at 90 % (new die) | DS eq. |
| 125 ms | AVDD at 99 % | est. |
| 184 ms | AVSS at 99 % | est. |
| about 250 ms | firmware raises PWDN and RESET | procedure |
| +128 ms (131 worst) | tPOR elapsed | DS |
| +1.5–2.4 s | VCAP1 > 1.1 V | est. |
| about +3 s | reset pulse, then SDATAC and configuration | procedure |

### S5-INFO-FW: firmware power-up procedure (ADS1299 §11.1, Fig. 67, Fig. 76, Table 30)

1. **Option bytes, once.** Set BOR_LEV = 3 (2.92 V).
2. **Earliest in main().**
   - Write the output latches before switching the pin modes. Drive PWDN (PB12), RESET (PB1) and START (PB0) low as push-pull outputs, and drive CS (PA4) high.
   - Set SPI1 to mode 1 (CPOL 0, CPHA 1), MSB first, SCLK ≤ 4 MHz to start with. Note that prescaler 2 gives 36 MHz, which is over the 20 MHz limit.
   - Set DRDY (PC4) as an EXTI input on the falling edge.
   - CLKSEL is hard-strapped by R13, so no action is needed.
3. **Wait ≥250 ms** for AVDD and AVSS to settle.
4. **Set PWDN = 1, then RESET = 1.** The oscillator starts within 20 µs, and tPOR starts here.
5. **Wait max(tPOR ≥ 150 ms, VCAP1 > 1.1 V).** Use 3 s for VCAP1 until it has been measured.
6. **Send the reset pulse.** Hold RESET low ≥2 tCLK (use 10 µs), then wait ≥18 tCLK (use ≥20 µs). The RESET command 0x06 is an alternative.
7. **Set CS = 0 and send SDATAC (0x11).** The device wakes in RDATAC.
   - Keep ≥4 tCLK between bytes and before CS goes high.
8. **Read the ID register** with RREG ID. Expect (ID & 0x1F) == 0x1E.
9. **Write CONFIG3 = 0xEC**, then wait ≥150 ms for the internal reference.
10. **Write the remaining registers:** CONFIG1 (data rate), CONFIG2, CHnSET (MUX 000, SRB2 0), MISC1 = 0x20, BIAS_SENSP and LOFF. Optionally run an input-short noise check first.
11. **Start conversions:** set START = 1 (or send 0x08), then send RDATAC (0x10). On each DRDY↓, read 24 + 8×24 bits.
12. **Power-down and wake.**
    - Power-down: send SDATAC, then set PWDN = 0.
    - Wake: set PWDN = 1, then repeat steps 5–10.
    - Never drive START, RESET or PWDN high before step 3.

### S5-INFO-KH: kicad-happy analyzer
- No sequencing errors.
- False positives:
  - U4 is reported as "gpio_controlled by U2", but U4 EN is tied to its own IN.
  - U2, U4 and U6 are reported as missing caps; the caps sit behind the inductors.
  - Negative rails are shown as positive (a tool limitation).
- Inrush on +3V3: 8.6 µF / 57 mA, which agrees with S5-INFO-06.
