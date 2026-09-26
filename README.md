# go60-config

Firmware flashing workflow and firmware history for my MoErgo Go60 split keyboard.

- `scripts/go60-flash`: flashes a `.uf2` onto both halves
- `firmware/`: every `.uf2` I have flashed, named `<date>_v<firmware version>_<layout name>_<layout id>.uf2`
- `layout/current.json`: the current layout as a Layout Editor JSON export. `git log -p layout/current.json`
  shows what changed between flashes.
- `skills/go60/`: a Claude Code skill, so Claude can answer "where is å?" or "how do I get to the arrows?"
  from any folder, plus the `go60-keys` command and an interactive cheat sheet
- `AGENTS.md` (and `CLAUDE.md`, which imports it): context for AI agents working in this repo
- `scripts/install`: symlinks everything into place (`~/.local/bin`, `~/.claude/skills/go60`). Run it once
  after cloning; after that, `git pull` updates everything.

## Layout help

```
go60-keys find å '{' enter       # where is it, on which layer, and how to get there
go60-keys key "LH T1"            # what one key does on every layer
go60-keys layers                 # layers and how to reach them
go60-keys show SymbolNav         # draw a layer with Finnish legends
go60-keys cheatsheet --open      # interactive cheat sheet (search, per-layer tabs)
```

You can also just ask Claude about the keyboard in any session. The `go60` skill uses the layout that is actually flashed.

## Workflow

1. Edit the layout in the MoErgo Layout Editor (my.moergo.com, Go60), then click **Save and Build**.
   This downloads one `<layout_id>_v25.xx_<layout name>.uf2` into `~/Downloads`.
   Also download the layout as JSON (`<layout_id>_<layout name>.json`) so the layout is saved in git as text.
2. Run `go60-flash`, or press **Super+Shift+Ctrl+K**.
   It shows the file and firmware version, moves the file into `firmware/`, saves the JSON export with the
   same layout ID as `layout/current.json` (and refreshes the cheat sheet), and asks whether you are using one cable or two. Both files are
   removed from `~/Downloads`. The script also offers to delete older Go60 builds and exports it finds there.
3. Put the halves into bootloader mode as prompted. The script watches for the `GO60RHBOOT` and
   `GO60LHBOOT` drives, mounts each one, copies the firmware, and waits for the drive to disappear,
   which means the flash is done. Desktop notifications tell you what to do next.
4. When it finishes, commit (and push) the new firmware file and layout.

Use the same `.uf2` on both halves, and connect the cables straight to the laptop, not through a hub.
MoErgo says bad hubs and cables cause most flashing failures.

### Two cables (both halves connected)

1. Connect both halves to the laptop.
2. Press **Magic + \\**. The right half enters the bootloader and gets flashed.
3. Press **Magic + Tab**. The left half enters the bootloader and gets flashed.

The quick combos only work while the halves can talk to each other, which is why the right half goes first.
If the left drive appears first, the script flashes it anyway and keeps waiting for the right one.

### One cable

1. Connect the cable to the right half and press **Magic + \\**.
2. When the script says so, move the cable to the left half and press **Magic + Tab**.

### Bootloader key combos

| Half  | Drive label  | Quick combo (while running) | Fallback                               |
|-------|--------------|-----------------------------|----------------------------------------|
| Right | `GO60RHBOOT` | Magic + \\                  | Power off, hold **Alt+K**, power on    |
| Left  | `GO60LHBOOT` | Magic + Tab                 | Power off, hold **Ctrl+D**, power on   |

A slow pulsing red LED next to the power switch means the half is in bootloader mode.

### After a firmware version change

When the version changes (for example v25.08 to v25.11), not just the layout, the script reminds you to
reset the configuration and re-link the halves. Your layout is kept.

1. Left: hold **Ctrl+E** while powering on, and keep holding for 5 seconds.
2. Right: hold **Alt+I** while powering on, and keep holding for 5 seconds.
3. Power both halves on, press **Magic+T** twice, and wait 1 minute.

## go60-flash options

```
go60-flash [options] [file.uf2]
  -1 / -2              one cable / two cables (asked if omitted)
  --right-only         flash only one half (e.g. to retry a failed half)
  --left-only
  -l, --latest         re-flash the latest archived firmware
  -t, --timeout SECS   wait time per bootloader drive (default 300)
  -n, --dry-run[=ORDER]  simulate the drives, e.g. RL, LR, RRL, R, rRL
                       (lowercase = that half never reboots). Changes nothing.
  --no-notify, --hold, --help
```

## Later: text keymap

The plan is to switch to MoErgo's official
[go60-zmk-config](https://github.com/moergo-keyboards/go60-zmk-config) template and keep the keymap
here as ZMK source, building the firmware locally or with GitHub Actions. This repo only uses `scripts/`,
`firmware/`, `layout/` and `skills/`, so MoErgo's files (`config/`, `.github/`, build scripts) can be added at the top level
without conflicts. Only this README would need merging.
