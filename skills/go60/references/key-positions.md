# Go60 key positions

The Layout Editor JSON stores each layer as an array of 60 bindings. `go60-keys` maps indexes to
physical keys using MoErgo's position names.

## Naming

- **LH / RH**: left hand or right hand.
- **C1–C6**: columns counted **from the inside out**. C1 is the inner index-finger column (next to the
  gap between the halves), and C6 is the outer pinky column.
- **R1–R5**: rows from the top. R1 is the number row, R2 the top letter row (Q W E …), R3 the home row
  (A S D …), R4 the bottom letter row (Z X C …), and R5 the extra bottom keys. Only C2, C3 and C4
  have an R5 key.
- **T1–T3**: the curved 3-key thumb cluster, counted **from the inside out**. T1 is the innermost thumb key,
  and T3 is the outermost and wider (1.5U) one.

## Fingers

| Column | Finger |
|--------|--------|
| C1 | index finger (reaching inward) |
| C2 | index finger (home: F on the left, J on the right) |
| C3 | middle finger |
| C4 | ring finger |
| C5 | pinky (home: A on the left, Ö on the right) |
| C6 | pinky (reaching outward: Esc, Tab, Magic …) |
| T1–T3 | thumb |

Home position: left fingers on LH C5R3–C2R3 (A S D F), right fingers on RH C2R3–C5R3 (J K L Ö), and
thumbs resting on the thumb cluster.

## Index → position

| Indexes | Position |
|---------|----------|
| 0–5 | LH C6R1 … LH C1R1 (left number row, outer to inner) |
| 6–11 | RH C1R1 … RH C6R1 (right number row, inner to outer) |
| 12–23 | R2, same pattern |
| 24–35 | R3 (home row), same pattern |
| 36–47 | R4, same pattern (36 = LH C6R4, usually Magic; 47 = RH C6R4) |
| 48, 49, 50 | LH C4R5, LH C3R5, LH C2R5 |
| 51, 52, 53 | RH C2R5, RH C3R5, RH C4R5 |
| 54, 55, 56 | LH T1, LH T2, LH T3 |
| 57, 58, 59 | RH T3, RH T2, RH T1 |

## How this was verified

- Rows 0–47 are 6 left + 6 right keys. This matches the factory Base layer (`= 1 2 3 4 5 │ 6 7 8 9 0 -`,
  `Tab Q W E R T │ Y U I O P`) and the Magic layer, where bootloader sits at Tab (index 12, the left combo
  Magic+Tab) and at `\` (index 23, the right combo Magic+\).
- MoErgo's tech spec says only columns C2–C4 have a fifth row and that the thumb cluster has 3 keys.
  That gives 48 + 6 + 6 = 60 keys.
- The factory layout notes call index 54 "LH T1" and index 47 "RH C6R4".
- MoErgo's bootloader instructions ("hold T3 + C3R3", which is Ctrl+D on the left and Alt+K on the right)
  put LH T3 at index 56 (Ctrl) and RH T3 at index 57 (Alt).
- T2 (55, 58) and RH T1 (59) follow by elimination. The R5 order (48–53) is inferred from the
  outer-to-inner order of the other rows, so treat it as likely rather than confirmed. If the user
  corrects any position, update `scripts/keymap.py` (`_build_positions`) and this file.
