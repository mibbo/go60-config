# Editing the layout as text (config/go60.keymap)

The layout can be changed in two ways, and both end in `go60-flash`:

- **Layout Editor** (web): Save and Build and download the JSON, then run `go60-flash`.
- **Text keymap**: edit `config/go60.keymap`, then run `go60-build`, which builds locally with Podman
  and then runs `go60-flash`.

`layout/current.json` always describes what's flashed, whichever way was used. After an editor flash,
`go60-flash` also regenerates the keymap, so the text version stays current. It only skips that if the
keymap has edits that were never flashed, and it warns about it.

## Contents
1. Workflow
2. How the file is organized
3. Common edits (with examples)
4. Switching back to the Layout Editor
5. Problems

## 1. Workflow

```bash
# edit config/go60.keymap (by hand or ask Claude)
go60-keymap check     # validates, and lists every changed key with its position and Finnish legend
go60-keymap format    # optional: re-align columns and refresh the legend comments
go60-build            # offers to commit, builds (Podman), then runs go60-flash
```

- `go60-build -- --two-cables` passes options on to `go60-flash`.
- `go60-build --no-flash` only builds, leaving the firmware in `build/`.
- The first build creates the build container, which downloads the ZMK toolchain and takes a while.
  Later builds take a minute or two.
- Builds use the same ZMK version as the currently flashed firmware (e.g. v25.11), so the firmware
  version doesn't change by accident. `--zmk v26.xx` upgrades on purpose, and `go60-flash` then prints
  the configuration-reset reminder.

**When Claude edits the keymap:** make the change, run `go60-keymap check`, and show the user the
changed keys as summary lines (position names, old → new). Then let the user run `go60-build`, because
flashing needs their hands on the keyboard. Commit only if the user asks, since `go60-build` offers to commit anyway.

## 2. How the file is organized

1. **Header comment**: a short guide.
2. **`#include` lines and `#define LAYER_<Name> <n>`**: layer numbers.
3. **Standard MoErgo behaviors** (generated): the Magic key, `td_LAYER_<Name>` (hold for the layer,
   double-tap to lock it), `bt_0`–`bt_3`, and the RGB status macro. **Don't edit these.** They're
   regenerated, and the Layout Editor has its own versions.
4. **Custom behaviors section**, between the `go60-config: custom behaviors` markers. This is the place
   for your own hold-taps, macros and tap-dances. It's kept as-is and carried into the editor JSON (its
   "Custom Defined Behaviors" field).
5. **`keymap { … }`**: one `layer_<Name>` per layer, in layer-number order, each with exactly
   **60 bindings** laid out like the keyboard:

```
/*    left  C6 C5 C4 C3 C2 C1  |  right C1 C2 C3 C4 C5 C6  (thumbs: left T1 T2 T3 | right T3 T2 T1) */
/* R1 */ &kp EQUAL  &kp N1 …                                  ← code
//       ´          1      …                                  ← what it types (Finnish), comment only
/* R5 */ (left C4 C3 C2)            (right C2 C3 C4)
/* T  */ (left T1 T2 T3)            (right T3 T2 T1)
```

   The **text order is what counts**, not the column alignment. Thumb keys in text order are: left
   T1 (innermost), T2, T3, then right T3, T2, T1 (innermost).
6. **Trackpad settings** (`&cirque_*_listener`) and the **custom devicetree** section.

## 3. Common edits

Key codes are US names. Pick the code that types the right **Finnish** character with
`references/finnish-layout.md` or `go60-keys find <char>`.

| Goal | Binding |
|------|---------|
| type å / ö / ä | `&kp LBKT` / `&kp SEMI` / `&kp SQT` |
| type { } [ ] | `&kp RA(N7)` `&kp RA(N0)` `&kp RA(N8)` `&kp RA(N9)` |
| type @ $ € \\ \| | `&kp RA(N2)` `&kp RA(N4)` `&kp RA(E)` `&kp RA(MINUS)` `&kp RA(NON_US_BSLH)` |
| type / ( ) = ? | `&kp LS(N7)` `&kp LS(N8)` `&kp LS(N9)` `&kp LS(N0)` `&kp LS(MINUS)` |
| shortcut | `&kp LC(C)` (Ctrl+C), `&kp LG(RIGHT)` (Super+→), `&kp LC(LS(T))` |
| tap: key, hold: modifier ("home-row mod") | `&mt LCTRL A`, `&mt LSHFT F` |
| tap: key, hold: layer | `&lt LAYER_SymbolNav SPACE` |
| layer while held / lock with double-tap | `&mo LAYER_X` / `&td_LAYER_X` |
| switch to a layer (and stay) | `&to LAYER_Base` |
| same as the layer below / nothing | `&trans` / `&none` |

- **Swap two keys:** swap the two binding texts.
- **Change a key on one layer only:** edit only that layer's binding.
- **Add a layer:**
  1. Add `#define LAYER_<Name> <n>` using the next number.
  2. Add a `layer_<Name> { display-name = "<Name>"; bindings = < …60 bindings… >; };` at that position,
     easiest by copying a layer and replacing keys with `&trans`.
  3. Give it a way in, such as `&mo LAYER_<Name>` on some key.
  4. For `&td_LAYER_<Name>`, add a tap-dance in the custom section:
     `td_LAYER_<Name>: td_LAYER_<Name> { compatible = "zmk,behavior-tap-dance"; #binding-cells = <0>;
     tapping-term-ms = <200>; bindings = <&mo LAYER_<Name>>, <&to LAYER_<Name>>; };`
     (inside `/ { behaviors { … }; };`).
- Keep the **Magic** layer and a Magic key: they hold the bootloader keys used for flashing (Magic+Tab / Magic+\\).

## 4. Switching back to the Layout Editor

`go60-keymap to-json -o ~/Downloads/go60-from-keymap.json` writes the keymap in the editor's format. Import
it in the editor: enable Settings → *Local Backup and Restore*, then use the import control at the bottom left.
MoErgo notes that the JSON format may change between editor versions. After that, edit in the editor and flash
as usual, and `go60-flash` brings the keymap along.

## 5. Problems

- **`go60-keymap check` reports "has N bindings, expected 60"**: a binding was deleted or split. Every
  key needs one binding, and `&none` is fine for unused keys.
- **Unknown key code**: usually a typo (`PAUSE_BRAEK`). ZMK's key names are listed at zmk.dev/docs/keymaps/list-of-keycodes.
- **Build fails**: read the first error line. It usually names the bad binding or behavior.
- **`go60-build` warns that the editor layout is newer**: the keyboard was flashed from the editor after
  the keymap was last edited. Choose **update** to start from the flashed layout.
- **Podman missing**: `omarchy pkg add podman`.
