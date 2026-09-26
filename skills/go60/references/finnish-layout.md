# What keys type with the Finnish layout

The keyboard sends US HID key codes, and Linux turns them into characters using the active layout:
`fi` in the default `kotoistus` variant (checked with `hyprctl devices`, and taken from
`/usr/share/X11/xkb/symbols/fi`). The Layout Editor's `sv-SE` locale shows the same legends.

**AltGr is the right Alt (`RALT`, or the `RA(...)` wrapper).** In the factory layout it's the hold
action of RH T1 (tap = Enter).

| ZMK code | Plain | Shift | AltGr | Shift+AltGr |
|----------|-------|-------|-------|-------------|
| `GRAVE` | § | ½ | | |
| `N1` | 1 | ! | | ¡ |
| `N2` | 2 | " | @ | ” |
| `N3` | 3 | # | £ | » |
| `N4` | 4 | ¤ | $ | « |
| `N5` | 5 | % | ‰ | “ |
| `N6` | 6 | & | ‚ | „ |
| `N7` | 7 | / | { | |
| `N8` | 8 | ( | [ | < |
| `N9` | 9 | ) | ] | > |
| `N0` | 0 | = | } | ° |
| `MINUS` | + | ? | \ | ¿ |
| `EQUAL` | ´ dead | ` dead | | |
| `LBKT` | å | Å | | |
| `RBKT` | ¨ dead | ^ dead | ~ dead | |
| `SEMI` | ö | Ö | ø | Ø |
| `SQT` | ä | Ä | æ | Æ |
| `BSLH`, `NON_US_HASH` | ' | * | | |
| `NON_US_BSLH` | < | > | \| | |
| `COMMA` | , | ; | ’ | ‘ |
| `DOT` | . | : | | |
| `FSLH` | - | _ | – | |
| `E` | e | E | € | |
| `S` | s | S | ß | |
| `I` | i | I | | \| |
| `KP_DOT` | , (with Num Lock) | | | |

**Dead keys** (´ ` ¨ ^ ~) type nothing on their own: press the dead key, then a letter, to get é, ü,
ê and so on. Press it twice or follow it with Space to get the mark itself. Beginners often think these
keys are broken.

**Named shifted codes are US-shifted.** `LPAR` is Shift+9, which gives `)` here, not `(`. `AMPS` is Shift+7,
which gives `/`, not `&`. The factory SymbolNav layer was designed around US legends, which is why some of its
symbols look scrambled on this laptop. `go60-keys` always shows the Finnish result.

To produce a specific symbol from a layout key, the key needs to send the Finnish combination. For example,
`@` is `&kp RA(N2)` and `{` is `&kp RA(N7)`. Use this when helping the user add symbol keys in the Layout Editor.
