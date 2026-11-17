# MANUAL_ACTIONS: Step 5 round 4

No blocked items. Notes:
- P-S5-006 (R41 0 Ω link): the BOM marks it fitted. For first power-up you can leave it off, measure +5V at R41 pad 1 (it must be ≤ 5.25 V), then fit it. See docs/firmware/ads1299-power-up.md.
- Task 3 sourcing:
  - D4 and its alternative are Extended parts.
  - The BAT54W-class low-leakage alternative to D3 had no usable stock.
  - Order U6 as the TPS72325 new-die (M3) variant.

## M-S5-001 (from P-S5-001…007) — Tidy text overlaps by hand, then do one Eeschema save before commit
- **analog_in:**
  - R38, R39, R40: their fields sit on the bodies, and the #PWR0130–0132 GND values overlap them.
  - TP7: the VCAP1 label overlaps its value and reference.
- **power:**
  - TP8: the "+5V" texts are doubled with #PWR0133, and the arrow touches the TP8 reference.
  - TP9: the −5V text overlaps its reference.
  - D3: its reference touches the section line at y ≈ 97.8, and its value sits directly above U6's ref/value.
  - R41: the 5V_L1 and 5V_REG labels are crowded (optional).
- **stm32:**
  - R42: its fields sit on the body, the #PWR0135 arrow overlaps its end, and the #PWR0135 "+3V3" text sits below the symbol next to R42's value.
  - #PWR0136: its GND text stacks under D2's GND text.
- Save once and close. The save also normalises float noise.
