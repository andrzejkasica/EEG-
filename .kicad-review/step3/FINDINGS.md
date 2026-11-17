# FINDINGS: Step 3 diff review (round 2, iteration 1)

Counts: CRITICAL 0, HIGH 0, MEDIUM 2, LOW 7, INFO 6 (15 findings).

## S3-001 [MEDIUM] Documentation/Firmware — No note on the sheet giving the register settings the hardware needs
- Source: manual review; `grep "(text "` on analog_in.kicad_sch returns 0 text items.
- Location: analog_in.kicad_sch (whole sheet), U3.
- Evidence:
  - The front end only works with register states that differ from the defaults:
    - MISC1.SRB1 resets to 0 (switches open). Datasheet §9.6.1.15, lines 3869–3885.
    - CONFIG3 resets to 0x60: BIASREF_INT = 0 and PD_BIAS = 0 (BIAS amp powered down). Datasheet §9.6.1.4, lines 3275–3310.
  - IN1N–IN8N are left floating, so LOFF_SENSN must stay 0x00. The datasheet example code sets LOFF_SENSN 0xFF (§10.1.2.1, line 4106); with floating N pins that would make the comparators report lead-off constantly.
  - The sheet has no text recording any of this.
- Fixability: mcp-approval (add_schematic_text)
- Suggested fix: add a text block near U3:
  - "FW REQUIRED: MISC1=0x20 (SRB1→all INxN). CONFIG3=0xEC (PD_REFBUF=1, BIASREF_INT=1, PD_BIAS=1).
  - CHnSET: MUX=000, SRB2=0.
  - BIAS_SENSP = channels used for bias; set BIAS_SENSN to suit, and note that the loop gain scales with the number of sensed inputs (see S3-002).
  - LOFF_SENSN=0x00 (INxN are NC).
  - LOFF current ≤24 nA (ILEAD_OFF 6/24 nA).
  - INxN NC is valid only with SRB1=1."
- Risk if changed: none (text only).

## S3-002 [MEDIUM] Analog/BIAS — Bias-loop compensation (1 MΩ ∥ 1.5 nF) comes from a 2-electrode example; with 8 sensed inputs plus a 100 kΩ series R, phase margin is not assured
- Source: datasheet review and hand loop calculation.
- Location: R34 (1M), C63 (1.5n), R35 (100k), nets BIASINV, BIASOUT, E_BIAS.
- Evidence:
  - Fig. 68 (PDF p.63, §10.1.3) shows 1 MΩ ∥ 1.5 nF for a 3-electrode system, which means 1–2 sensed inputs.
  - The loop gain scales with N (Eq. 11, line 4519: G = Rf·N/330 kΩ; Fig. 73 draws 220 kΩ per PGA output).
  - With N = 8:
    - The input resistance is 27.5–41 kΩ.
    - The integrator crossover is 1/(2π·R_in·1.5 nF) ≈ 2.6–3.9 kHz.
    - The DC gain is 24–36.
  - The patient path adds a pole: (R35 100 kΩ + electrode 10–50 kΩ) × (lead/body capacitance 100–300 pF) ≈ 3.5–16 kHz. That is at, or within about 4× of, the crossover.
  - The bias amp has GBW 100 kHz and slew 0.07 V/µs (lines 616–624).
  - TI's own ADS1299EEG-FE EVM uses 392 kΩ / 10 nF (SLAU443B §7.1.3, R8/C20). That gives about 0.6 kHz crossover at N = 8, and TI warns that "optimization may be needed … if additional filtering components and long cables are added".
  - R35 itself matches Fig. 73: R_P sits outside the feedback node (feedback taken at the BIASOUT pin), and the netlist confirms this. See S3-010.
- Fixability: manual
- Suggested fix: keep R35 = 100k. Do one of:
  - (a) raise C63 to 4.7–10 nF C0G, which puts the crossover at about 0.6–1.2 kHz with N = 8 and keeps more than 10× margin over the 50/60 Hz loop gain; or
  - (b) keep 1.5 nF but limit BIAS_SENSP to 2–3 channels.

  Either way, bench-verify with a step on a body phantom (for example 51k ∥ 47n electrodes and 200 pF to GND) and look for less than 10% overshoot on BIASOUT. Keep the 0603 C0G footprint so the value can be changed.
- Risk if changed: a larger Cf lowers the bias bandwidth, which slightly lowers mains-CM suppression above about 100 Hz. That is irrelevant for EEG.

## S3-003 [LOW] Spec/Analog — The spec misreads Fig. 18 for INxN in SRB1 mode; NC is still acceptable
- Source: datasheet Fig. 18 (PDF p.20, lines 1460–1516), checked against the rendered figure.
- Location: U3 pins 1, 3, 5, 7, 9, 11, 13, 15 (IN8N…IN1N), each with a no-connect flag. Spec section "Unused U3 pins".
- Evidence:
  - The spec says "Per Fig. 18, the INnN pins stay on that node". The figure shows the opposite.
  - The INxN pin reaches PGAN only through a switch labelled "MAIN AND S̄R̄B̄1̄" (overbar; the overbar is lost in the .txt extraction).
  - SRB1 reaches PGAN through a separate switch labelled "MAIN AND SRB1".
  - So with MISC1.SRB1 = 1, INxN is **disconnected** from the PGA. Only the LoffN current source and the "MUX=111/BIAS" switches (all off in normal mode) touch it.
  - The SLAU443B §5.3.3 text agrees: "the signal on SRB1 pin is routed to negative inputs of all channels instead of VINN inputs".
  - Consequences:
    - NC does not "fight the reference", and tying to AVDD would not fight it either. Both are electrically safe.
    - The datasheet rule (pin-table note 2, line 460; §10.1.1, line 3961: "connect unused analog inputs directly to AVDD") is written for powered-down channels.
    - NC works, provided LOFF_SENSN = 0 (S3-001).
    - In SRB1 mode, the N-side lead-off sources cannot sense the REF electrode. A REF lead-off shows up instead as all channels saturating together.
- Fixability: info-only (correct the spec text). Changing the tie would be manual.
- Suggested fix:
  - Correct the spec rationale.
  - Keep NC (it matches OpenBCI Cyton practice).
  - Optional alternatives:
    - Tie INxN to AVDD per §10.1.1. This gives a defined potential, and the cost is nil.
    - Tie INxN to SRB1_F. This allows non-SRB1 referencing and N-side lead-off on REF, at the cost of 8 more pin leakages on the REF line.
- Risk if changed: AVDD tie: a channel rails if firmware leaves SRB1 = 0, which is harmless. SRB1_F tie: more leakage and capacitance on the REF node.

## S3-004 [LOW] EMI — No common-mode RF caps and no DNP footprints for them
- Source: datasheet §10.2.2 text (PDF p.68, lines 4496–4501).
- Location: nets CH1–CH8 and SRB1_F.
- Evidence:
  - The datasheet says: "If the system is likely to be exposed to high-frequency EMI, adding very small-value, common-mode capacitors… should be 10 or 20 times smaller than the differential capacitor."
  - The spec defers this to "if EMI shows up". With no footprints on the board, that would mean a re-spin.
  - The patient leads are unshielded and on a 2.54 mm header, which pick up RF easily.
- Fixability: manual
- Suggested fix: add 9 DNP 0402 C0G footprints of 220–470 pF from each INxP (CH1–CH8) and SRB1_F to GND (that is 4.7 nF/20 to 4.7 nF/10). Mark them DNP in the BOM.
- Risk if changed: none while DNP. If fitted, a ±5% mismatch costs some CMRR; my nodal estimate is still about −89 dB CM→DM at 50 Hz with 470 pF and 5% mismatch.

## S3-005 [LOW] BOM/DFM — New parts have no LCSC, MPN or tolerance fields; the LCSC numbers from the spec were not entered
- Source: netlist fields. The analyzer's SS-001 now lists 24 more refs missing an MPN.
- Location: J4, U10–U12, R25–R35, C55–C63.
- Evidence:
  - The only fields present are Footprint and Description. Values carry no tolerance or voltage ("4.99k", "100k", "1M", "4.7n C0G", "1.5n C0G").
  - LCSC/jlcsearch lookup results:

    | Part | LCSC | Class | Stock / price |
    |---|---|---|---|
    | TVS (TPD4E1B06DCKR-TP) | C2923390 | Extended | 4,203 in stock, $0.24 |
    | 1.5 nF 50 V C0G 0603 (GRM1885C1H152JA01D) | C162204 | Extended | 15,788 in stock |
    | J4 header | C5156617 | Extended | 2,220 in stock, THT ("Plugin") |
    | 4.7 nF 50 V C0G 0402 (GRM1555C1H472JE01D) | C1518204 | Extended | – |
    | 4.99k 1% 0402 (0402WGF4991TCE) | C25903 | jlcsearch reports not basic | – |
    | 1M 1% 0402 (0402WGF1004TCE) | C26083 | Basic | – |
    | 100k 1% 0402 (0402WGF1003TCE) | C25741 | Basic | – |

  - That makes about 5 unique extended lines, roughly $15 in setup fees, which matches the spec's estimate.
  - The rest of the project has no LCSC fields either, so this is a project-wide gap, not a Step 3 regression.
- Fixability: mcp-approval (set_schematic_component_property)
- Suggested fix: add LCSC, MPN and Tolerance (1%) properties to the new parts, using the codes above or the bom/lcsc skill. Confirm stock at order time.
- Risk if changed: none (properties only).

## S3-006 [LOW] DFM — J4 is a through-hole header
- Source: LCSC lookup.
- Location: J4 (PinHeader_1x10_P2.54mm_Vertical, C5156617).
- Evidence: C5156617 is listed as a "Plugin" (THT) part. JLCPCB places THT parts with its separate THT/hand-soldering assembly service, which adds cost and lead time. Alternatively, the user can solder it.
- Fixability: manual
- Suggested fix: accept this and hand-solder J4, or order JLCPCB THT assembly. An SMD 2.54 mm header is an option if the board must be fully SMT-assembled.
- Risk if changed: footprint change at layout.

## S3-007 [LOW] Cosmetic — C55–C62 reference designators overlap the capacitor bodies
- Source: get_schematic_view_region render (x 20–130, y 105–135).
- Location: C55–C62, around x 30–125 mm, y 120 mm.
- Evidence: each rotated Reference ("C55"…"C62") is drawn across the capacitor plates. The Value field ("4.7n C0G") sits next to it. The text is legible but cluttered. Everything else added in Step 3 renders cleanly: J4, U10–U12 and R25–R35 have no overlaps.
- Fixability: mcp-approval (autoplace_schematic_fields or set_schematic_property_position)
- Suggested fix: move each Reference to the left of the cap body (offset about −2.5 mm in x), or autoplace the fields. Then re-render to check, because field angles on rotated symbols behave oddly.
- Risk if changed: none.

## S3-008 [LOW] File hygiene — The MCP write left mixed indentation and floating-point noise in coordinates
- Source: validate_schematic (indent_depth_mismatch at line 10652); grep.
- Location: analog_in.kicad_sch.
  - Power symbols appended from line ~10641 use 2-space formatting next to tab formatting.
  - 32 coordinates carry float noise, for example `45.720000000000006` at lines 9982–10072 and 10636/10640, and `92.71000000000001` at lines 10092–10272. The base file has 2.
- Evidence: kicad-cli loads the file, and ERC and netlist are correct. Every value is on the 1.27 mm grid within 1e-14, so the connections are unaffected. The only harm is noisy diffs and the validator flag.
- Fixability: manual
- Suggested fix: open the sheet in Eeschema and save it once, with no edits, before committing. Eeschema re-serialises the file and normalises both issues. Then re-run validate_schematic and ERC.
- Risk if changed: none (whitespace and number formatting only).

## S3-009 [LOW] Safety/Spec — The spec overstates fault-current limiting by the 4.99 kΩ channel resistors
- Source: spec "Series resistors" bullet; hand calculation.
- Location: R25–R33.
- Evidence:
  - If an internal fault ties an input to a rail, 2.5 V / 4.99 kΩ ≈ 0.5 mA flows into the patient. IEC 60601-1 allows a single-fault DC patient auxiliary current of 50 µA (10 µA in normal condition).
  - The datasheet notes that "R_Filt has a minimum set by technical standards" (line 4496).
  - Raising R increases noise. Two 5 kΩ resistors already add about 0.67 µVpp in 65 Hz (SLAU443B §8.2).
  - The ADS1299 lead-off sources can be set as high as 24 µA DC.
  - Medical certification is a non-goal and the isolation is functional only, so this is a documentation issue.
- Fixability: info-only
- Suggested fix: reword the spec. Only R35 limits patient current to IEC levels; R25–R33 limit ESD and overvoltage current into U3 (see S3-011). Firmware should restrict lead-off current to the 6 nA or 24 nA settings.
- Risk if changed: none.

## S3-010 [INFO] Analog/BIAS — The 100 kΩ series R on the BIAS electrode is correct (focus Q1)
- Source: Fig. 73 (PDF p.67), Fig. 68 (p.63), bias amp specs (lines 616–624), netlist.
- Location: R35 (E_BIAS ↔ BIASOUT).
- Evidence:
  - **Topology.** Fig. 73 places R_P between BIASOUT and the bias electrode, outside the Rf ∥ Cf feedback. The netlist matches this: BIASOUT = {U3.63, R34.2, C63.2, R35.2}, E_BIAS = {J4.10, R35.1, U12.2}.
  - **Patient current.**
    - Normal-condition DC current is only the sum of the input leakages: 9 × ≤300 pA (lines 578–583) plus TVS leakage, so nA level.
    - In a fault where BIASOUT rails against a body held at GND, the current is 2.5 V / 100 kΩ = 25 µA. The worst case, a full 5 V swing, is 50 µA. Both are within the IEC 60601-1 single-fault limit of 50 µA, compared with up to 1.1 mA short-circuit current without R35.
  - **Drive.**
    - Mains CM displacement currents are typically below 1 µA. At 1 µA the drop across 100k plus about 50k electrode impedance is 0.15 V, against about ±2.2 V of headroom.
    - Loop gain at 50 Hz is |1M ∥ 2.1M| / (R/N), roughly 22–33. That is enough to suppress mains CM.
    - R35's thermal noise is common-mode and is rejected.
  - **Stability** is the only open item; it is handled in S3-002.
- Fixability: info-only
- Suggested fix: none.
- Risk if changed: n/a

## S3-011 [INFO] ESD — The TVS choice and clamp level protect U3 adequately, and leakage is irrelevant at this operating point (focus Q3)
- Source:
  - TECH PUBLIC TPD4E1B06DCKR-TP datasheet, p.2: VRWM ±5.5 V; VBR 6.8–9.5 V; Vc 9 V max at 1 A, 14.5 V at 2.8 A; I_leak 0.9 nA typ at 2.5 V; Cj 0.6–0.9 pF.
  - TI TPD4E1B06 (SLLSEB0), §5: I_leak 0.5 nA max at 2.5 V; VBR 7–9.5 V; Vclamp 10.9 V at 1 A.
  - ADS1299 §7.1 (lines 485–503).
- Location: U10–U12 on the E_* nets (connector side of the 4.99k and 100k resistors).
- Evidence:
  - **Clamp level.** The TVS does not hold the pin within AVSS−0.3 to AVDD+0.3 by itself, and it does not need to. ADS1299 note 2 (line 502) says the input pins are diode-clamped to the rails, and that the input current should be limited to 10 mA or less (abs max ±10 mA continuous, line 494) when the voltage is outside that range. Behind the 4.99 kΩ resistor:
    - TVS clamp at 1 A ESD: (10.9 − 2.8) V / 4.99 kΩ ≈ 1.6 mA.
    - At 14.5 V: 2.3 mA.
    - Continuous 5 V fault below VBR: 0.44 mA.
    - BIAS line through 100k: about 0.1 mA.

    All of these are well under 10 mA, so the TVS plus R plus the internal diodes form a correct two-stage clamp. The TVS's working voltage of ±5.5 V is well clear of the ±2.5 V signal range, so it stays off in normal operation.
  - **Leakage.** Both TVS GND and the electrodes sit near 0 V, because BIASREF_INT drives the body to (AVDD+AVSS)/2 = 0 V. So the bias across each TVS is about 0 ± a few hundred mV, and the leakage is far below the 2.5 V spec figure.
    - Even at 0.9 nA, 0.9 nA × 50 kΩ gives 45 µV of DC offset. A 1 MΩ dry electrode gives 0.9 mV. The DC-coupled ADS1299 at gain 24 handles this.
    - Shot noise is about 17 fA/√Hz, which is negligible.
  - **Pinout.** The clone pinout is identical to the TI DCK pinout, so the genuine TI part is a drop-in (see S3-013).
  - **Lower-leakage options**, if wanted:
    - Genuine TI TPD4E1B06 (0.5 nA max).
    - BAV199-type low-leakage diode pairs steered to AVDD/AVSS (pA-level leakage, a common choice in precision front ends).
- Fixability: info-only
- Suggested fix: none. Prefer genuine TI samples if they are available.
- Risk if changed: n/a

## S3-012 [INFO] Analog filter — Values, topology and dielectric are sound; the spec's corner numbers need correcting (focus Q4)
- Source: Fig. 73 (PDF p.67); §10.2.2 (lines 4490–4501); SLAU443B EVM schematic (also 4.99 kΩ / 4.7 nF); my complex nodal analysis of the 8-channel shared-SRB1_F network.
- Location: R25–R33, C55–C62, net SRB1_F.
- Evidence:
  - **Topology** is exactly Fig. 73: differential caps from INxP to the filtered SRB1 node. The netlist confirms SRB1_F = {C55–C62 pin 2, R33.2, U3.17}.
  - **C0G** is right for the differential caps: no voltage or piezo coefficient. Their tolerance (±5%) does not affect CMRR in this topology.
  - **Corners.** Because the REF node is shared, the corners differ from the spec's 3.4 kHz (2R·C pair):
    - A single-channel differential signal has its −3 dB point at about 5.2 kHz.
    - A signal on REF only sees 8 caps, giving about 755 Hz.

    Both are far above the EEG band and the ADC bandwidth.
  - **Attenuation at f_MOD = 1.024 MHz:** −44.6 dB on a channel and −62.7 dB on REF.
  - **Noise.** Two 4.99k resistors add 12.8 nV/√Hz, about 0.67 µVpp in 65 Hz (SLAU443B §8.2), against about 1 µVpp for the ADS1299 itself.
  - **Bias-current offsets:**
    - On a channel: 300 pA × 4.99k = 1.5 µV.
    - On SRB1: 8 × 300 pA × 4.99k ≈ 12 µV, common to all channels.
  - **Caveat (estimate).** SRB1 drives 8 PGA N inputs. Assuming 20 pF input capacitance per pin (line 579), the τ mismatch between INxP and SRB1_F gives about −73 dB CM→DM at 50 Hz before the bias loop's roughly 30 dB of suppression. This is inherent to Fig. 73 and should be checked on the bench.
  - Common-mode caps are handled in S3-004.
- Fixability: info-only
- Suggested fix: update the spec to the 5.2 kHz / 755 Hz figures.
- Risk if changed: n/a

## S3-013 [INFO] Library — The custom symbol pin numbers match the SOT-363 footprint pads and both datasheets (focus Q5)
- Source:
  - EEG_custom.kicad_sym and the embedded lib_symbol in analog_in.kicad_sch (identical).
  - `/usr/share/kicad/footprints/Package_TO_SOT_SMD.pretty/SOT-363_SC-70-6.kicad_mod`.
  - TECH PUBLIC datasheet p.1.
  - TI SLLSEB0, Table 4-1 / Fig. 4-1.
- Location: U10–U12.
- Evidence:
  - **Symbol:** 1 IO1, 2 IO2, 3 GND (passive), 4 IO3, 5 IO4, 6 NC (no_connect).
  - **Footprint pads:**
    - 1 (−0.8875, −0.65), 2 (−0.8875, 0), 3 (−0.8875, +0.65): left column, top to bottom.
    - 4 (+0.8875, +0.65), 5 (+0.8875, 0), 6 (+0.8875, −0.65): right column, bottom to top.

    This is standard counter-clockwise SC-70-6 numbering, the same as the package drawing (1-2-3 on one side, 4-5-6 opposite and reversed).
  - **Datasheets:** the TI DCK pinout is IO1 = 1, IO2 = 2, GND = 3, IO3 = 4, IO4 = 5, NC = 6, the same as the clone. (TI's DRL package differs, but it is not used here.)
  - **Library checks:** validate_symbol_library reports the library as valid, and sym-lib-table uses ${KIPRJMOD}.
  - **Footprints of the other new parts:** R 0402 HandSolder (project convention, 31 uses), C 0402 / C63 0603 (allowed by the spec), J4 PinHeader_1x10 vertical. All are correct.
- Fixability: info-only
- Suggested fix: none.
- Risk if changed: n/a

## S3-014 [INFO] Netlist — The spec circuit is implemented exactly; ERC target met
- Source: kicad-cli netlist and ERC diff.
- Location: /ANALOG_IN/.
- Evidence:
  - **Channels.** E_CHn = {J4.n, R(24+n).1, TVS IO}. CHn = {R.2, C(54+n).1, U3 INnP}, with pins 16/14/12/10/8/6/4/2.
  - **TVS mapping.** U10 IO1–IO4 = CH1–4; U11 = CH5–8; U12 IO1 = E_REF, IO2 = E_BIAS. U12 IO3/IO4 have NC flags. All TVS pin 3 go to GND.
  - **REF.** E_REF = {J4.9, R33.1, U12.1}.
  - **BIAS.** BIASINV = {U3.61, R34, C63}.
  - **No-connect flags** on U3 IN1N–IN8N, SRB2, BIASIN, BIASREF.
  - **ERC.** The 41 /ANALOG_IN/ items went to 0, with no new items.
  - **MCP checks.** No orphaned wires, no floating labels, no wires crossing symbols. There are no new overlaps; R16–R18 vs #PWR were there before Step 3.
- Fixability: info-only
- Suggested fix: none.
- Risk if changed: n/a

## S3-015 [INFO] Tooling — Analyzer false positives from this diff
- Source: diff_analysis.py and analyze_schematic.py.
- Location: CH1–CH8, BIASINV, J4, R35/C63.
- Evidence:
  - **"no_driver" on CH1–8 and BIASINV.** These nets hold only passive parts and IC analog inputs, which is expected; kicad-cli ERC reports no pin_not_driven.
  - **CG-AUD "J4 has no ground pins".** This is intentional, since J4 is a patient electrode header. A ground pin on it would be wrong unless shielded leads are adopted.
  - **RC-DET "R35/C63 at 1061 Hz".** This pairing is spurious; the real feedback pole is R34·C63, about 106 Hz.
  - **RC-DET 6.8 kHz.** This treats each R and C as an isolated pair (see S3-012 for the actual corners).
- Fixability: info-only
- Suggested fix: none.
- Risk if changed: n/a
