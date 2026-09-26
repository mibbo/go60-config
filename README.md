# go60-config

Firmware flashing workflow and firmware history for my MoErgo Go60 split keyboard.

- `scripts/go60-flash`: flashes a `.uf2` onto both halves (symlinked to `~/.local/bin/go60-flash`)
- `firmware/`: every `.uf2` I have flashed, named `<date>_v<firmware version>_<layout name>_<layout id>.uf2`.
  This is my layout history until the keymap lives here as text.

## Workflow

1. Edit the layout in the MoErgo Layout Editor (my.moergo.com, Go60), then click **Save and Build**.
   This downloads one `<layout_id>_v25.xx_<layout name>.uf2` into `~/Downloads`.
2. Run `go60-flash`, or press **Super+Shift+Ctrl+K**.
   It shows the file and firmware version, moves the file into `firmware/`, and asks whether
   you are using one cable or two.
3. Put the halves into bootloader mode as prompted. The script watches for the `GO60RHBOOT` and
   `GO60LHBOOT` drives, mounts each one, copies the firmware, and waits for the drive to disappear,
   which means the flash is done. Desktop notifications tell you what to do next.
4. When it finishes, commit (and push) the new firmware file.

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
here as text, building the firmware locally or with GitHub Actions. This repo only uses `scripts/`
and `firmware/`, so MoErgo's files (`config/`, `.github/`, build scripts) can be added at the top level
without conflicts. Only this README would need merging.
