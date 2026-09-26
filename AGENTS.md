# Agent guide: go60-config

This repo holds the firmware history, current layout, and flashing scripts for my MoErgo Go60
split keyboard (ZMK firmware). I edit the layout in MoErgo's web Layout Editor (my.moergo.com),
not as ZMK source. The OS is Omarchy (Arch + Hyprland) with the Finnish keyboard layout (`fi`).

## Files

| Path | What it is |
|------|------------|
| `layout/current.json` | The current layout, exported from the Layout Editor (pretty-printed). **Read this to answer questions about the layout.** `git log -p layout/current.json` shows how it changed over time. |
| `firmware/*.uf2` | Every firmware file that was flashed, named `<flash date>_v<firmware version>_<layout name>_<layout id>.uf2`. Compiled binaries: don't try to read keymaps from them. |
| `scripts/go60-flash` | Flashes a `.uf2` to both halves, archives it, and saves the matching JSON export as `layout/current.json`. Interactive; don't run it without the keyboard unless you use `--dry-run`. |
| `scripts/go60-layout` | Prints `layout/current.json` as per-layer grids. `-i` adds key indexes, `-l <n or name>` shows one layer. |

`go60-flash` and `go60-layout` are symlinked into `~/.local/bin`. The Hyprland shortcut
Super+Shift+Ctrl+K (in `~/.config/hypr/bindings.lua`) runs `go60-flash --hold` in a terminal.

## Reading layout/current.json

- `layer_names[i]` is the name of layer `i`, and `layers[i]` is an array of **60 key bindings**.
  The current layers are Base, Keypad, SymbolNav, Magic and Factory.
- A binding is `{"value": "<behavior>", "params": [...]}`, where params can be nested.
  For example, `{"value":"&kp","params":[{"value":"LS","params":[{"value":"N7"}]}]}` is `&kp LS(N7)`, Shift+7.
- Common behaviors: `&kp` (key press), `&trans` (transparent: uses the layer below), `&none`,
  `&mo N` (momentary layer), `&to N` / `&layer N` (switch layer), `&mt MOD KEY` (mod-tap),
  `&magic` (the Magic key), `&bt`, `&out`, `&rgb_ug`, `&bootloader`, `&reset`.
- Modifier wrappers: `LS`/`RS` = Shift, `LC`/`RC` = Ctrl, `LA` = Alt, `RA` = **AltGr**, `LG` = Super.
- Other keys in the file: `notes` (the layout description), `macros`, `holdTaps`, `combos`,
  `inputListeners` (trackpad settings), `custom_defined_behaviors`, `custom_devicetree`, and `config_parameters`.

### Key positions (index → physical key)

Verified from the Base and Magic layers:

- Indexes 0–47 are four rows of 12, each with **6 left-hand keys, then 6 right-hand keys**, outer column first on the left:
  - row 0 (0–11): number row (`= 1 2 3 4 5 │ 6 7 8 9 0 -` on a US legend)
  - row 1 (12–23): Tab row (`Tab Q W E R T │ Y U I O P \`)
  - row 2 (24–35): home row (`Esc A S D F G │ H J K L ; '`)
  - row 3 (36–47): bottom letter row (`Magic Z X C V B │ N M , . / <layer 1>`)
- Indexes 48–59 are the bottom row and thumb keys. Their physical order is **not verified yet**, except that
  MoErgo's notes call index 54 "LH T1" (left thumb 1) and index 47 "RH C6R4" (right hand, column 6, row 4).
  Say so if an answer depends on the physical position of 48–59.
- MoErgo notation: `LH`/`RH` = left/right hand, `C1–C6` = column, `R1–R4` = row, and `T1…` = thumb keys.

### What a key types with the Finnish layout

ZMK key names are **US HID codes**. The laptop uses `kb_layout = fi` (the editor's `sv-SE` locale is equivalent),
so many keys type something other than their name. When the user asks "where is X", translate first:

| ZMK code | Types (fi) | With Shift | With AltGr (`RA(...)`) |
|----------|------------|------------|------------------------|
| `GRAVE` | § | ½ | |
| `N1` … `N6` | 1…6 | `!` `"` `#` `¤` `%` `&` | `N2` @, `N3` £, `N4` $, `N5` € |
| `N7` `N8` `N9` `N0` | 7 8 9 0 | `/` `(` `)` `=` | `{` `[` `]` `}` |
| `MINUS` | + | ? | `\` |
| `EQUAL` | ´ (dead key) | \` (dead key) | |
| `LBKT` | å | Å | |
| `RBKT` | ¨ (dead key) | ^ (dead key) | ~ (dead key) |
| `SEMI` | ö | Ö | |
| `SQT` | ä | Ä | |
| `BSLH` / `NON_US_HASH` | ' | * | |
| `NON_US_BSLH` | < | > | \| |
| `COMMA` `DOT` `FSLH` | , . - | ; : _ | |

So `&kp LS(N7)` types `/`, not `&`, and `&kp LBKT` types `å`. The factory SymbolNav layer was designed for a US
layout, so several of its symbols come out differently on this laptop.

## Workflow and rules

- Layout changes happen in the web Layout Editor: Save and Build downloads a `.uf2`, and the layout's JSON
  download gives the export. Both land in `~/Downloads`, and `go60-flash` moves them into this repo
  (pairing them by layout ID) and offers to commit.
- `layout/current.json` is an export, and the editor stays the source of truth. If you suggest a layout
  change, describe it as editor steps (layer, key, behavior). Editing the JSON only helps if it gets
  imported back into the editor.
- Don't edit or rewrite files in `firmware/`: they are the flash history.
- After a firmware *version* change (for example v25.08 to v25.11), the halves need a configuration reset.
  `go60-flash` prints the steps, and `README.md` has them too.
- Planned for later: move to MoErgo's `go60-zmk-config` template (keymap as ZMK source under `config/`, built
  locally or with GitHub Actions). Keep the top level free for those files. This repo only uses `scripts/`,
  `firmware/` and `layout/`.
