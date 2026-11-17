# ADS1299 power-up and STM32 firmware notes

This is the firmware procedure the EEG board's hardware requires. It comes from the Step 5 power-sequencing review (`.kicad-review/step5/FINDINGS.md`, S5-INFO-FW / S5-INFO-TL), with references to ADS1299 SBAS499C §11.1, Fig. 67, Fig. 76 and Table 30.

## Hardware assumptions

The hardware the firmware relies on:
- **ADS1299 (U3) runs on its internal 2.048 MHz oscillator.** CLKSEL is strapped high by R13, so the CLK pin is unused (CONFIG1.CLK_EN = 0, with R14 pulling it down).
- **Hardware pulls hold the control lines while the STM32 is in reset:** START, RESET and PWDN are pulled down by 100k each (R16–R18), and CS is pulled up to +3V3 by R15. SCLK, DIN and MISO also get 100k pull-downs (Step 5).
- **Supplies:** DVDD = +3V3 is final about 1 ms after the isolated +5V. AVDD/AVSS = ±2.5 V reach 99 % at about 125 ms and 184 ms, because of the large NR caps C24/C25 (kept for low noise). These times are estimates, so measure them at bring-up.
- **VCAP1 has a 100 µF cap (C43).** Its charge to 1.1 V is estimated at 1.5–2.4 s. A test point is planned on VCAP1 so this can be measured.

## STM32 setup (once / at boot)

- **Option bytes:** BOR_LEV = 3 (2.92 V rising). Code then runs only once VDD is close to 3.3 V.
- **USB:** disable VBUS sensing, because PA9 is not connected (round-1 F-021).
- **Unused pins:** set every no-connect GPIO to analog mode.
- **SPI1:** mode 1 (CPOL = 0, CPHA = 1), MSB first. Start at SCLK ≤ 4 MHz.
  - Prescaler 2 gives 36 MHz, which is above the 20 MHz maximum. Use prescaler ≥ 8 (9 MHz).
  - Above 4 MHz, keep ≥ 4 tCLK (about 2 µs) between command bytes (tSDECODE).
- **LED pins (S6-006):** configure PB4 (D1) and PB3 (D2) as GPIO outputs early in init.
  - After reset, PB4 is NJTRST with its internal pull-up on, so D1 glows faintly (about 30 µA) until the pin is reconfigured.
  - PB3 is JTDO/SWO, so SWO trace is unavailable. That's fine, because J3 is 2-wire SWD.
- **J5 expansion header:** PB6/PB7 = I2C1 (AF4, open-drain; external 4.7k pull-ups R36/R37). PA2/PA3 = USART2 (AF7). PA0 = WKUP/GPIO.

## ADS1299 power-up procedure

1. **Earliest in `main()`.** Write the output data latches first, then switch the pin modes, so nothing glitches:
   - PWDN (PB12), RESET (PB1) and START (PB0): push-pull outputs driven **low**.
   - CS (PA4): push-pull output driven **high**.
   - Configure SPI1 as above, and DRDY (PC4) as an EXTI input on the falling edge.
2. **Wait ≥ 250 ms from boot.** AVDD/AVSS must settle (§11.1, "allow time for the supply voltages to reach their final value"). The MCU can't see the analog rails, so this is a fixed delay. Shorten it only after measuring the rails.
3. **Set PWDN = 1, then RESET = 1.** The internal oscillator starts within 20 µs, and tPOR starts counting here.
4. **Wait max(tPOR, VCAP1 > 1.1 V).**
   - tPOR = 2^18 tCLK = 128 ms (131 ms at the −2.5 % oscillator limit), so wait ≥ 150 ms.
   - VCAP1 > 1.1 V: use **3 s** until it has been measured. After bring-up, use 2× the measured time, and never less than 150 ms.
   - Most example code waits only tPOR. On this board that would reset too early.
5. **Reset pulse.** Hold RESET low for ≥ 2 tCLK (use 10 µs), release it, then wait ≥ 18 tCLK (use ≥ 20 µs). Sending the RESET command (0x06) also works.
6. **Set CS = 0 and send SDATAC (0x11).** The device wakes up in RDATAC mode and ignores RREG/WREG until SDATAC is sent. Keep ≥ 4 tCLK between bytes and before CS goes high, and keep CS high pulses ≥ 2 tCLK.
7. **Read RREG ID (0x20 0x00).** Expect `(ID & 0x1F) == 0x1E`.
8. **Write CONFIG3 = 0xEC** (PD_REFBUF = 1, BIASREF_INT = 1, PD_BIAS = 1), then wait ≥ 150 ms for the internal reference.
9. **Write the remaining registers:**
   - MISC1 = 0x20, which routes SRB1 to all channel N inputs. IN1N–IN8N are also tied to SRB1_F, so the reference still works if this is 0.
   - CHnSET: MUX = 000, SRB2 = 0, plus the gain.
   - CONFIG1 (data rate) and CONFIG2.
   - BIAS_SENSP = the channels used for bias drive. C63 = 10 nF is compensated for all 8.
   - Lead-off: current ≤ 24 nA (ILEAD_OFF 6 or 24 nA). One LOFF_SENSN bit detects a loose REF electrode.
   - Optionally, run an input-short noise check first (CHnSET = 0x01).
10. **Start conversions.** Set START = 1 (or send the START command 0x08 with the pin low), then send RDATAC (0x10). On every DRDY falling edge, read 24 status bits plus 8 × 24 data bits.

## Power-down and wake

- **Enter power-down:** send SDATAC, then set PWDN = 0.
- **Wake:** set PWDN = 1, then repeat steps 4–9. The oscillator and reference need wake-up time, and VCAP1 may have discharged.
- Never drive START, RESET or PWDN high before step 2 has completed.

## Bring-up measurements that refine this procedure

- Scope VCAP1 against AVSS (VCAP1 test point vs TP3 −2V5) after PWDN↑, and record the time to 1.1 V. Use it for step 4.
- Capture +5V, +2V5 and −2V5 at power-on, with no load and with a dummy load. Accept if +2V5 ≤ 2.6 V and AVDD − AVSS ≤ 5.2 V (S5-006). The measured settle times can shorten step 2.
- Before fitting the 0 Ω link to U2/U4, measure the isolated +5V with no load. It must be ≤ 5.25 V, the TPS60403 recommended maximum (S5-001 / F-002).
- Capture U6 IN and OUT at power-down to confirm that the Schottky clamps the reverse condition (S5-007).
