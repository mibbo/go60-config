---
name: go60
description: Answers questions about the user's MoErgo Go60 split keyboard using the layout that is actually flashed on it. It finds where a character, key or function is (å, ö, {, @, arrows, Enter, Esc, Bluetooth, bootloader), explains layers, thumb keys and the Magic key, helps a split-keyboard beginner learn the layout, and opens a visual cheat sheet. Use it whenever the user mentions their Go60, split keyboard, ergonomic keyboard, keyboard layers, thumb cluster, "where is X on my keyboard", "how do I type X", or the MoErgo Layout Editor, even if they don't say "Go60". Also use it for changing or re-flashing the Go60 layout (go60-flash).
---

# Go60 keyboard helper

The user is new to split keyboards and owns a MoErgo Go60 (ZMK firmware, 60 keys, two halves).
They edit the layout in MoErgo's web Layout Editor and flash it with `go60-flash`. The laptop
runs Omarchy (Arch + Hyprland) with the **Finnish** keyboard layout.

Everything lives in the git repo `~/sync/git/go60-config`. This skill folder is `skills/go60/` inside it, and
`~/.claude/skills/go60` is a symlink to that folder.

- `layout/current.json`: the layout that was last flashed, as a Layout Editor JSON export. This is the source of truth for questions.
- `firmware/*.uf2`: history of flashed firmware (binary; not readable as a layout).
- `scripts/go60-flash`: the flashing workflow (`README.md` in the repo describes it).

## Answer layout questions with go60-keys

Use the bundled tool rather than reading the JSON by hand. It already handles two things that are easy
to get wrong:
- **Finnish translation.** ZMK key codes are US names, so `LBKT` types `å` and `LS(N7)` types `/`.
- **Physical positions.** Array indexes are mapped to hands, rows, fingers and thumb keys.

```bash
go60-keys find å '{' enter arrows        # where is it? (characters, key names, or functions)
go60-keys key "LH T1" 36                 # what does this key do on every layer?
go60-keys layers                         # the layers and how to reach each one
go60-keys show SymbolNav                 # draw a layer as the physical keyboard
go60-keys cheatsheet --open              # open the interactive HTML cheat sheet in the browser
```

If `go60-keys` isn't on PATH, run `~/.claude/skills/go60/scripts/go60-keys`. Quote single characters
like `'{'` or `'*'` for the shell. `find` also accepts words such as `bootloader`, `bluetooth`, `volume`,
`shift` and `altgr`. For anything else, use a ZMK code such as `C_VOL_UP` or `PG_UP`.

## How to answer

The user is still learning where things are, so answer the way you'd point at a physical keyboard.

**Start every answer with the key combination as a one-line summary**, in a blockquote so it stands
out. Write each key as its MoErgo position name in backticks, in the order to press them, and mark
the keys that are held. The user reads this line first and often needs nothing else:

> **Super + →** : `LH T1` hold + `RH C2R5` hold + `LH C2R3` tap

> **{** : `RH T1` hold + `RH C2R1` tap

> **å** : `RH C3R5`

If there are several good ways, give one summary line for each, easiest first, and put a short label
after the line (e.g. "SymbolNav on the left hand"). Then explain:

1. **Say where each key is in plain words**: which hand, which row, which finger, and for thumbs,
   which thumb key counting from the inside. Put MoErgo's position name in brackets after it, e.g.
   "right hand, bottom row, index finger stretching toward the middle (RH C1R4)". Skip array indexes
   unless the user asks for them.
2. **Say which layer it's on and how to get there.** On the base layer, just press it. On another
   layer, name the key that activates the layer and say whether to hold it or double-tap it to lock.
3. **Include any modifier needed and where it is**, e.g. "hold AltGr (right thumb, innermost key)
   and press 7 to get {".
4. If there's more than one way, lead with the easiest and mention the others briefly.
5. Point out anything surprising, such as dead keys (´ ¨ ^ ` ~ wait for the next key), or a
   symbol layer that was designed for US keyboards and so gives different characters here.

Keep answers short. The user wants to find the key and keep typing, not read a report. For "show me
the layer" questions, paste the `go60-keys show` output in a code block or suggest the cheat sheet.

If something isn't on the layout, or is awkward to reach, say so. Then offer to explain how to add it in
the Layout Editor (layer, key position, behavior). Don't edit `layout/current.json` to "add" keys: the
keyboard only changes when the user rebuilds in the editor and flashes.

## Reference files (read when needed)

- `references/key-positions.md`: position names (C1–C6, R1–R5, T1–T3), fingers, and which facts are
  verified. Read it when an answer depends on exact physical placement.
- `references/finnish-layout.md`: what every key code types with the Finnish layout, plus dead keys and
  AltGr. Read it when explaining symbols or why a key types something unexpected.
- `references/beginner-guide.md`: split-keyboard basics (home position, layers, thumbs, Magic key,
  learning tips) and how to change and flash the layout. Read it for "how do I get started" or
  "how does this work" questions, and when helping the user change their layout.

## Keeping the answers current

`layout/current.json` is updated by `go60-flash` each time the user flashes with a JSON export in
`~/Downloads`. `git -C ~/sync/git/go60-config log -1 --format='%ci %s' -- layout/current.json` shows when
it last changed. If the user says they changed the layout but the file is older, their keyboard may be
running a newer layout than the file describes. Say so, and suggest downloading the JSON and running
`go60-flash`.
