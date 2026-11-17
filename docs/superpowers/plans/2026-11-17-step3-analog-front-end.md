# Step 3: ADS1299 analog front end (electrode inputs, ESD, filter, BIAS)

Task 2, Step 3 of `2026-10-23-eeg-board-completion.md`. Sheet: `hardware/EEG_Kicad_Project/analog_in.kicad_sch` (U3 ADS1299).

## Intent
Connect electrodes to U3 so that the board can record 8 EEG channels in a **referential montage**: every channel is measured against one shared reference electrode on SRB1, and a BIAS (driven-ground) electrode holds the body near mid-supply. The design has two goals: (1) protect each patient-facing line from ESD, and (2) filter RF on each line without spoiling the ADS1299's common-mode rejection.

## Decisions (user, 2026-11-17)
- **Connector:** a 2.54 mm pin header. It is the cheapest option, JLCPCB can assemble it, and it fits OpenBCI-style gold-cup electrode leads. It is not touch-proof; a DIN 42802 adapter can be added later.
- **Montage:** shared reference only, with 10 electrode lines: CH1–CH8, REF (SRB1) and BIAS. IN1N–IN8N are not brought out.
- **Already fixed by the plan:** 8 channels, SRB1 reference plus BIAS electrode, internal clock.

## Non-goals
- No sequential (bipolar) montage hardware and no DIN touch-proof sockets on this revision.
- No medical certification. The isolation is functional grade only (see FINDINGS F-023).
- No lead-off hardware. Lead-off detection uses the ADS1299's internal current sources (firmware).

## Circuit (per line, connector side → U3)

```
J4.n ──┬─────────── R_FILT 4.99k ──┬── U3 INnP           (n = 1..8)
       └ TVS IOx (U10–U12)         └── C_FILT 4.7n C0G ── SRB1 node (after R)

J4.9 (REF) ──┬── R_FILT 4.99k ── SRB1 node ── U3 SRB1 (pin 17)
             └ TVS IO

J4.10 (BIAS) ──┬── R_BIAS 100k ── U3 BIASOUT (pin 63)
               └ TVS IO
U3 BIASINV (61) ── 1M ∥ 10n C0G ── U3 BIASOUT (63)
U3 INnN (1,3,…,15) ── SRB1 node            (tied, review S3-003)
CHn / SRB1 node ── 470p C0G DNP ── GND     (C64–C72, review S3-004)
```

- **Filter.** This follows datasheet Fig. 73 (referential montage). Each channel's filter cap sits between INnP and the filtered SRB1 node; the datasheet recommends this differential arrangement over caps to ground because it keeps CMRR independent of component mismatch.
  - *Corrected after review S3-012:* the REF node is shared by all 8 caps, so the corners are about **5.2 kHz** for a single-channel differential signal and about **755 Hz** for a signal on REF. Both are far above the EEG band.
  - Attenuation at f_MOD = 1.024 MHz is about −45 dB on a channel and about −63 dB on REF.
  - **Common-mode RF caps (added after review S3-004):** C64–C72 are 470 pF C0G 0402 footprints from CH1–CH8 and SRB1_F to GND, fitted as **DNP**. That is 1/10 of the differential cap, per §10.2.2. Fit them only if RF pickup shows up.
- **ESD.** Three 4-channel bidirectional TVS arrays (TPD4E1B06-type, SOT-363) sit right at J4. Each GND pin goes to GND (GND and GNDA are one net). 10 lines use 10 of the 12 IOs; the 2 spare IOs are left unconnected with no-connect flags. Working voltage is ±5.5 V, which covers the ±2.5 V rails.
- **BIAS.** Feedback is 1 MΩ ∥ **10 nF** C0G between BIASINV and BIASOUT. *Changed after review S3-002:* the datasheet's 1.5 nF (Fig. 68) is for 1–2 sensed inputs. With all 8 inputs plus the series resistor, 10 nF (matching TI's EVM, 392k/10n) gives about 0.6 kHz crossover. Bench-check the BIASOUT step response at bring-up. Firmware uses BIASREF_INT = 1 (internal mid-supply) and BIAS_SENSP selects the channels.
  - The **100 kΩ series resistor** limits current into the body. Without it, the bias amp can source up to 1.1 mA (short-circuit current). With it, the current stays at ≤ 50 µA even at a full 5 V swing.
  - This value is the builder's call, and the review loop should check it.
- **Series resistors.** *Corrected after review S3-009:* the 4.99 kΩ input resistors limit ESD and overvoltage current into U3 (≤ about 2.3 mA during a TVS clamp, against a 10 mA abs max). They do **not** limit patient fault current to IEC levels: a rail fault gives about 0.5 mA. Only R35 (100 k) does that, on the BIAS line. Firmware should keep lead-off current at 6 or 24 nA.

## U3 negative inputs and unused pins
- **IN1N–IN8N: tied to SRB1_F.** *Changed after review S3-003; the earlier reasoning misread Fig. 18.*
  - With MISC1.SRB1 = 1, the INnN pins are **disconnected** from the PGA. The SRB1 switch replaces them, so leaving them open would also have been safe.
  - Tying them to the filtered reference anyway means the reference still works if SRB1 = 0. It also lets one LOFF_SENSN bit detect a loose REF electrode.
- **SRB2, BIASIN, BIASREF: no-connect flags.** The datasheet allows floating for all three. BIASREF is unused because BIASREF_INT = 1.

## Parts (new references follow the existing ones)

| Ref | Part | Value / MPN | Footprint | LCSC (unit price) |
|---|---|---|---|---|
| J4 | 1×10 pin header, 2.54 mm | — | `Connector_PinHeader_2.54mm:PinHeader_1x10_P2.54mm_Vertical` | C5156617 ($0.05) |
| U10, U11, U12 | 4-ch bidirectional ESD array | TPD4E1B06DCKR (second source TECH PUBLIC -TP; TI original via DigiKey/Mouser) | `Package_TO_SOT_SMD:SOT-363_SC-70-6` | C2923390 ($0.24) |
| R25–R33 | Input series resistor | 4.99k 1 % | 0402 (project convention) | basic/extended passive |
| C55–C62 | Differential filter cap | 4.7n C0G 50 V | 0402 or 0603 | passive |
| R34 | BIAS feedback | 1M 1 % | 0402 | passive |
| C63 | BIAS feedback | 10n C0G (TDK CGA3E1C0G2A103JT0Y0E, 100 V) | 0603 | C432938 ($0.11) |
| C64–C72 | CM RF caps, **DNP** | 470p C0G (Murata GRM1555C1H471JA01D) | 0402 | C76971 |

LCSC, MPN and Tolerance properties are set on all the new parts (review S3-005). A firmware register note sits on the sheet (review S3-001).
| R35 | BIAS series current limit | 100k 1 % | 0402 | passive |

- **J4 pin map:**
  - pins 1–8 → CH1–CH8 (IN1P–IN8P)
  - pin 9 → REF (SRB1)
  - pin 10 → BIAS
- **Silkscreen** (layout task): label each pin, and mark the header with "PATIENT SIDE – ISOLATED".
- **TVS symbol:** none exists in the stock KiCad library. Create `TPD4E1B06DCK` in a project symbol library. Pinout from the datasheet (SOT-363): 1 IO1, 2 IO2, 3 GND, 4 IO3, 5 IO4, 6 NC.

## Cost
- About $1.50 in parts per board.
- JLCPCB charges about $3 per unique extended part once per order, which comes to roughly $12–15 per order for this step.

## Sourcing and samples
- Passives and the header: buy from LCSC.
- TVS: the LCSC parts are second sources, and only typical leakage is specified for the TECH PUBLIC part. If the university is in the TI University Program, request genuine TI TPD4E1B06DCKR samples. Otherwise use C2923390.
- Samtec and Molex offer free connector samples if a different header is wanted.

## Build workflow
- **Wiring:**
  - Claude wires the sheet directly via the KiCad MCP, the same way as in Step 2.
  - Check first that the schematic `.lck` file is absent.
  - If the A4 sheet runs out of room, switch `analog_in` to A3.
  - Use global/local labels (`CH1`–`CH8`, `REF`, `BIAS`) between the connector/ESD block and U3, so the U3 area stays readable.
- **Verify:**
  - `kicad-cli sch erc`: the 41 Step-3 items on /ANALOG_IN/ (22 pin_not_connected + 19 pin_not_driven) should drop to 0, with no new errors.
  - Netlist check of every connection in the circuit above.
  - Render the region to catch overlapping text.
- **Then** run the `kicad-review-loop` on the result before committing.

## Left to the builder
Exact placement and coordinates, label names, and whether each cap is 0402 or 0603.
