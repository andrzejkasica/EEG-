# Step 5 baseline: power sequencing (schematic only, base 66f244b)

No design files were modified. Outputs are in `analysis/` (netlist.xml, erc.json, schematic.json). Datasheets are in `scratchpad/step5/ds/`: TPS73225, TPS72325, STM32F446 DS, TPS60403 SLVS324C, TMU3, TPS732 SBVS037S, TPS723 SLVS346E. TLV757P and ADS1299 come from docs/datasheets.

ERC: 1 (the intentional GND/GNDA multiple_net_names).

## Rails
| Rail | Source | Nominal | Feeds |
|---|---|---|---|
| +5V_PRI | USB VBUS (J1) | 5.0 V | U7 primary, U8, U9 side 1 |
| +5V | U7 TMU3-0511 (unregulated, isolated) | 5.0 V (±3.5 % at 60 % load, higher at light load) | U5 IN/EN, L1 |
| Net-(U2-IN) | +5V through L1 3.3 µH | 5.0 V | U2 IN, U4 IN + EN |
| -5V | U2 TPS60403 OUT, then L2 | −VIN | U6 IN + EN |
| +3V3 | U5 TLV75733P | 3.3 V | STM32 VDD/VDDA/VBAT, ADS1299 DVDD, U9 side 2, pull-ups |
| +2V5 | U4 TPS73225, then L3 | 2.5 V (±1 %) | ADS1299 AVDD/AVDD1 |
| −2V5 | U6 TPS72325, then L4 | −2.5 V | ADS1299 AVSS/AVSS1, VREFN, VCAP/VREFP returns |

## Regulators
| Ref | Part | EN tie | NR / soft-start | Start-up |
|---|---|---|---|---|
| U7 | TMU3-0511 | none | internal | ≤5 ms; Ilim 250 %; Cload ≤2200 µF |
| U5 | TLV75733PDBV | EN = IN (+5V) | internal | UVLO 1.3 V; tSTR 550 µs typ |
| U2 | TPS60403DBV | no EN pin | none | Rout 12–15 Ω × about 23 µF, so τ ≈ 0.3 ms (est.) |
| U4 | TPS73225DBVT | EN = IN | C24 1 µF × 27 kΩ, so τ = 27 ms | 90 % at about 59 ms, 99 % at about 125 ms (est.) |
| U6 | TPS72325DBVT | EN = IN (−5V) | C25 100 nF × 400 kΩ (new die), so τ = 40 ms | 90 % at about 88 ms, 99 % at about 184 ms (new die); about 10 ms (legacy die, est.) |

## ADS1299 straps at power-up
| Pin | Net | Driven by during MCU reset |
|---|---|---|
| CS | ADS_CS | R15 100k up to +3V3 |
| START, RESET, PWDN | ADS_START, ADS_RESET, ADS_PWDN | R16/R17/R18 100k to GND |
| SCLK, DIN | SPI1_SCK, SPI1_MOSI | no pull (floating while PA5/PA7 are high-Z) |
| CLKSEL | Net-(U3-CLKSEL) | R13 10k to +3V3 (internal oscillator) |
| CLK | Net-(U3-CLK) | R14 10k to GND |
| GPIO1–4 | — | 10k to GND |
| DAISY_IN, RESV1 | GND | direct |

Caps on the reference and VCAP pins:
- VCAP1: C43 100 µF
- VCAP2/4: 1 µF each
- VCAP3: 1 µF ∥ 0.1 µF
- VREFP: 10 µF ∥ 0.1 µF to VREFN = AVSS

STM32 reset: NRST has R1 10k, C7 100n and SW1. BOOT0 has R2 10k down. LQFP64 has no PDR_ON pin, so the supervisor is always on.
