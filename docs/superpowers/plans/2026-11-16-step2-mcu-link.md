# Step 2: ADS1299 to STM32 link, and MCU support parts

Sheets: `stm32.kicad_sch` (U1, STM32F446RETx LQFP64) and `analog_in.kicad_sch` (U3, ADS1299).
Sources:
- ADS1299 datasheet SBAS499C. Section numbers below refer to it.
- CubeMX config `hardware/MX_Files/MX_Files.ioc`.
- The STM32F446 single-VCAP rule (4.7 µF, ESR < 1 Ω). This comes from the DS10693 power-supply table as quoted for the F412/F446 family. Re-check it against DS10693 Table 18 when the PDF is at hand.

Research came from two read-only agents, merged here on 2026-11-16.

## Decisions

- **Cross-sheet nets use global labels.** The existing local SPI1_* labels on `stm32.kicad_sch` are replaced by global ones.
- **Every ADS1299 control line gets its own GPIO.** START is not tied low: free pins are plentiful, and a GPIO keeps hardware start sync available.
- **Pull resistors sit next to U3,** so U3's inputs have a defined level while the STM32 is in reset with hi-Z pins.
  - START, RESET and PWDN are pulled down. §11.1 wants every input low until the supplies are stable, so the chip stays in reset and power-down until firmware releases it.
  - CS is pulled up, so the SPI interface stays idle (§9.5.2.1).
- **No series resistors on the SPI lines.** The TI EVM has none, and the traces are short on one board.
- **Patient safety: SWD and UART headers are on the isolated (patient) side.** Plugging in a mains-powered PC through them bypasses the USB isolation barrier. Use them only with no electrodes on a person, or through a USB isolator. Both headers deliberately have no +3V3 output pin except SWD VTref, which is a sense pin.

## ADS1299 link (global labels)

| Net | U1 pin | U3 pin | Extra part (next to U3) |
|---|---|---|---|
| `SPI1_SCK` | PA5 (21) | SCLK (40) | none |
| `SPI1_MOSI` | PA7 (23) | DIN (34) | none |
| `SPI1_MISO` | PA6 (22) | DOUT (43) | none (Hi-Z while CS is high) |
| `ADS_CS` | PA4 (20) | ~CS (39) | R15 100k to `+3V3` |
| `ADS_DRDY` | PC4 (24) | ~DRDY (47) | none (push-pull output) |
| `ADS_START` | PB0 (26) | START (38) | R16 100k to `GND` |
| `ADS_RESET` | PB1 (27) | ~RESET (36) | R17 100k to `GND` |
| `ADS_PWDN` | PB12 (33) | ~PWDN (35) | R18 100k to `GND` |

## MCU support parts (stm32.kicad_sch)

| Item | Parts | Connection |
|---|---|---|
| UART | Move local labels `USART3_TX` and `USART3_RX` from PC10/PC11 to PB10 (29) and PC5 (25). Add J2, 1x03 2.54 mm header. | 1 `USART3_TX`, 2 `USART3_RX`, 3 `GND` |
| SWD | J3, 1x05 2.54 mm header | 1 `+3V3` (VTref), 2 SWCLK PA14 (49), 3 SWDIO PA13 (46), 4 `NRST`, 5 `GND`. Power pins are at the ends; 1x05 SWD headers have no fixed standard order, so mark the pins on the silkscreen. |
| HSE | Y1 8 MHz, 3225 4-pin, CL = 12 pF; C48 and C49 15 pF C0G 0603 to `GND` | OSC_IN PH0 (5), OSC_OUT PH1 (6), via the existing `RCC_OSC_IN` / `RCC_OSC_OUT` labels. Y1 case pins go to `GND`. If Task 3 picks a crystal with a different CL, set C = 2 × (CL − 5 pF). |
| LEDs | D1 and D2 (0603), R19 and R20 1k | `LED_1` PB4 → R19 → D1 → `GND`; `LED_2` PB3 → R20 → D2 → `GND`. Active high, about 1.3 mA. |
| VCAP_1 | C9: 1u → **4.7u**, X7R 0603, low ESR | already wired to pin 30 |
| Test points | TP1 `+3V3`, TP2 `+2V5`, TP3 `-2V5`, TP4 `GND`, TP5 `ADS_DRDY`, TP6 `SPI1_SCK` | `TestPoint:TestPoint_Pad_D1.0mm` |

Footprints:
- Resistors: `Resistor_SMD:R_0402_1005Metric_Pad0.72x0.64mm_HandSolder`, same as R9-R14.
- Caps: `Capacitor_SMD:C_0603_1608Metric`.
- LEDs: `LED_SMD:LED_0603_1608Metric`.
- Crystal: `Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm`.
- Headers: `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` / `_1x05_`.

## Firmware follow-ups (not schematic)

- **SPI1 speed:** CubeMX has prescaler 2, which is 36 MHz. That exceeds the ADS1299 limit (tSCLK ≥ 50 ns, so 20 MHz max). Use prescaler 8 (9 MHz). At SCLK ≤ 4 MHz no inter-byte gaps are needed. Above that, respect tSDECODE = 4 tCLK (≈ 2 µs) between command bytes (§9.5.3.1).
- **SPI mode:** use mode 1 (CPOL low, CPHA 2 Edge).
- **GPIO modes:**
  - PA4 (CS): push-pull output, idle high.
  - PC4 (DRDY): EXTI on the falling edge.
  - PB0, PB1, PB12 (START, RESET, PWDN): push-pull outputs, default low.
- **Debug:** set SYS Debug to Serial Wire. PB3 and PB4 are LEDs, so SWO trace is unavailable.
- **Bring-up:**
  1. Keep PWDN and RESET low while the rails ramp.
  2. Set PWDN and RESET high.
  3. Wait at least 150 ms, and until VCAP1 > 1.1 V (100 µF, so allow more).
  4. Pulse RESET low for at least 2 tCLK (use 10 µs).
  5. Wait 18 tCLK.
  6. Send SDATAC (0x11).
  7. Write the registers.
  8. Raise START, then send RDATAC.

  Read data after each DRDY falling edge (§11.1, §9.4.4.1).
- **DMA:** SPI1 RX DMA is circular in the .ioc. A DRDY-triggered read needs normal mode.

## Result (2026-11-16)

Wired and verified via the KiCad MCP server. ERC is down from 106 to 76 violations.
- Every row of both tables is confirmed against the netlist.
- No Step 2 pin has an ERC error.
- The remaining errors are:
  - the Step 3 pins on U3;
  - unused STM32 GPIOs;
  - pre-existing dangling `UD+`/`UD-` global labels on the root sheet;
  - the accepted GND/GNDA merge.

## Done when

- ERC shows no `pin_not_connected` or `pin_not_driven` on U3 pins 34-36, 38-40, 43 and 47, nor on the U1 pins used above.
- A netlist check confirms every row of both tables.
- No new `multiple_net_names` warnings, and no local `SPI1_*` or `USART3_*` labels are left on PC10/PC11.
