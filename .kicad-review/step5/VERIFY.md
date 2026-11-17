# VERIFY: Step 5 round 4, iteration 1

These are fresh checks against the baseline `66f244b`, exported by me with kicad-cli 9.0.9 into `analysis/iter-1/`. The base exports are in `scratchpad/verify5/base/`. No design files or PCB were touched. The root sheet, usb, sym-lib-table, EEG_custom and .kicad_pro all match the base.

## Counts

| Metric | Base | Now | Expected |
|---|---|---|---|
| ERC | 1 | 1 | 1 |
| Comps | 137 | 147 | 147 |
| GND | 87 | 91 | 91 |
| +3V3 | 35 | 36 | 36 |
| +5V (isolated) | 6 | 7 | 7 |
| −5V | 5 | 7 | 7 |
| +5V_PRI / GND_PRI | 10 / 15 | 10 / 15 | unchanged |
| Analyzer findings | 73 | 76 | — |

**ERC.** The one violation is the same intentional GND/GNDA item; only the representative symbol it names has changed, from #PWR028 to #PWR018.

**Component diff.** 10 parts were added: D3, D4, R38–R42 and TP7–TP9. None were removed or changed.

**Net diff.** Only these changes:
- Nets gaining members:
  - +3V3 gains R42.1.
  - +5V gains TP8.1.
  - −5V gains D3.2 and TP9.1.
  - VCAP1 gains TP7.1.
  - GND gains R38.2, R39.2, R40.2 and D4.1.
  - SPI1_SCK, SPI1_MOSI and SPI1_MISO gain R38.1, R39.1 and R40.1.
- Net-(U2-IN) is replaced by 5V_L1 {L1.2, R41.1} and 5V_REG {C11.1, C12.1, C17.1, R41.2, U2.2, U4.1, U4.3}.
- Net-(U6-OUT) becomes Net-(D3-K) {C23.1, C26.1, D3.1, L4.1, U6.5}.
- New net: Net-(D4-A) {D4.2, R42.2}.

## Per fix

- **P-S5-001: PASS.**
  - SPI1_SCK = {R38.1, TP6.1, U1.21, U3.40}.
  - SPI1_MOSI = {R39.1, U1.23, U3.34}.
  - Pin 2 of both resistors is on GND.
  - Fields: 100k, C25741.
- **P-S5-002: PASS.** SPI1_MISO = {R40.1, U1.22, U3.43}, with R40.2 on GND.
- **P-S5-003: PASS.** VCAP1 = {C43.1, TP7.1, U3.28}.
- **P-S5-004: PASS.** TP8 is on the isolated +5V, not on +5V_PRI. TP9 is on −5V.
- **P-S5-005: PASS. Polarity independently confirmed.**
  - D3 anode (pin 2) is on −5V (U6 IN/EN). D3 cathode (pin 1) is on U6 OUT.
  - In the SOD-323 footprint, pad 1 is the cathode (the silk bar side).
  - Checked against TPS723 §6.3.1, §7.1.4 and Fig. 7-1:
    - Normal operation: VAK = −2.5 V, so D3 is off.
    - Power-up: VAK = −5 V, so D3 is off.
    - Input collapse with OUT held at −2.5 V: VAK = +2.5 V, so D3 conducts in parallel with the body diode and clamps the output.
- **P-S5-006: PASS.**
  - The only wire from L1.2 goes to R41.1, and the old wire a528380f is gone.
  - R41.2 goes to the 173.99 junction, which feeds C11, U2/C12 and the 168.91 junction (#FLG02, C17/U4).
  - No path bypasses R41, and #FLG02 is on 5V_REG.
- **P-S5-007: PASS. Polarity confirmed.**
  - D4: A to R42/+3V3, K to GND. LED_0603 pad 1 is the cathode.
  - Current is about 0.9–1.0 mA.
- **Isolation barrier: PASS.**
  - The primary side closes on +5V_PRI, GND_PRI, D±, UD±, VDD1_ISO1, CC1/2 and U9-UD±.
  - Only U7 and U9 straddle the barrier.
  - All new parts are on the isolated side.

## Analyzer (73 → 76)

- **New:**
  - RS-001 "5V_L1 has no declared source" is a false positive: the net is passive, fed from +5V through L1.
  - LA-AUD on D4 is info only.
  - DC/DO-DET 5V_REG decoupling only reflects the rename.
- **Gone:** LC-DET for the L1 filter. The analyzer no longer recognises the LC filter once R41 is in series. With R41 fitted the circuit is physically unchanged.
- Nothing was raised on D3 or R41.

## MCP checks

- `find_wires_crossing_symbols`:
  - analog_in and power: 0 crossings.
  - stm32: D1/D2 (known) plus a new D4 hit. All three are the same LED bounding-box false positive.
- No orphaned wires. No floating labels.

## New findings (all INFO)

- **N-1:** D3's clamp Vf is 0.45 V at 1 A, above the 0.3 V abs max. At the small discharge currents involved it is about 0.2–0.3 V, and this is TI's own recommended fix, so no action is needed.
- **N-2:** analyzer artifacts. RS-001 on 5V_L1 is a false positive, and LC-DET was lost (see above).
- **N-3:** the D4 wire-crossing hit is a false positive.

## Overlaps to add to M-S5-001

- The D3 reference touches the section line at y ≈ 97.8.
- D3's value sits right above U6's reference and value.
- The R41 labels are crowded. This is optional to fix.
- The #PWR0135 "+3V3" value text sits below the symbol, beside R42's value.

**Result: 7 PASS / 0 FAIL / 0 REGRESSION.**
