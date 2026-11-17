# KiCad Review Loop: Step 6 full deep review (round 5, whole schematic)

- Base `ad3e7bb`. Date 2026-11-17. 1 iteration. Verifier result: 4 PASS / 0 FAIL / 0 REGRESSION.

## Plan target (Task 2 Step 6): MET
- ERC has 0 errors. The only warning is the intentional GND/GNDA one.
- No high or error findings, apart from SS-001 (the Task 3 MPN gate) and the tracked F-002 / S5-001.

## Findings

| ID | Severity | Topic | Outcome |
|---|---|---|---|
| S6-001 | MEDIUM | Master plan treated GND/GNDA as the isolation barrier | Fixed (docs) |
| S6-002 | LOW | MLCC voltage/dielectric | Task 3 sourcing |
| S6-003 | LOW | "0.1u"/"100n" BOM split | Fixed |
| S6-004 | LOW | TPs/JP1 included in BOM | Fixed |
| S6-005 | LOW | Single-sheet global USB labels and shape mismatch | Fixed |
| S6-006 | INFO | PB3/PB4 reset state | Firmware doc |
| S6-007 | INFO | J1 SBU pads | Check DRC at Step 7 |
| S6-008 | INFO | LC post-filter damping | Bring-up scope check |
| S6-009 | INFO | Engineering pass | Clean |
| S6-010 | INFO | False positives | Recorded |

Round 1 carry-overs:
- F-012 (LED colour): fixed. D1/D2 are now red, C2286.
- F-018: closed as accepted.
- F-019: resolved.
- F-022: deferred to Task 4.

## Fixes

| Fix | Change | Result |
|---|---|---|
| P-S6-001 | Six caps "0.1u" → "100n"; one 0603 100n BOM line ×8 | PASS |
| P-S6-002 | TP1–TP9 and JP1 excluded from BOM; grouped BOM 55 → 44 lines | PASS |
| P-S6-003 | D±/UD± made local labels; USB_OTG_FS_DP/DM made bidirectional | PASS |
| P-S6-004 | D1/D2 → LED_RED (C2286); R19/R20 LCSC fields | PASS |

## Documentation
- The master plan's isolation checks and rail names are corrected (S6-001).
- The firmware doc has a new PB3/PB4 note.

## Remaining
- **Before commit:** open, save and close in Eeschema, to normalise the compact property formatting.
- **Step 7:** re-sync the PCB from the schematic (F8). Check J1 SBU pad DRC (S6-007).
- **Task 3:**
  - SS-001: MPN coverage is 15/43 lines.
  - F-002: +5V must stay ≤ 5.25 V.
  - S6-002: MLCC ratings.
  - TPS72325: use the M3 variant.
