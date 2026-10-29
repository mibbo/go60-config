# Go60 lights (RGB)

The Go60 has one RGB LED under every key (30 per half). Stock firmware lights them all the same way. This
repo adds **per-key colour presets** on top, but only in firmware built locally with `go60-build`.

## Controls on the keyboard

All lighting keys are on the Magic layer: hold **Magic** (LH C6R4) and tap a left-hand key. Check them
with `go60-keys find rgb` (the layout may change); in the factory layout:

| Key | Top row (R2) | Home row (R3) |
|-----|--------------|---------------|
| C1 (inner index) | on/off (`RGB_TOG`) | next effect (`RGB_EFF`) |
| C2 (index) | brightness + | brightness − |
| C3 (middle) | hue + | hue − |
| C4 (ring) | saturation + | saturation − |
| C5 (pinky) | animation speed + | speed − |

A plain tap of Magic shows status (battery, Bluetooth profile, layer) on the LEDs for a few seconds.
The keyboard remembers the last effect and colour.

## Effects and presets

`go60-leds list` shows the order. MoErgo's effects come first: 0 Solid, 1 Breathe, 2 Spectrum,
3 Swirl (the moving rainbow, factory default). Each preset in `config/led-presets.json` adds one more
effect (4, 5, …), in file order. "Next effect" cycles through all of them and wraps around.

- Presets are static colours. **Brightness** keys dim them; hue, saturation and speed keys only affect
  MoErgo's effects.
- A key can jump straight to an effect with `&rgb_ug RGB_EFS_CMD <number>` in the keymap (e.g. on a free
  Magic-layer key). Numbers shift if presets are reordered or deleted.
- If a preset the keyboard was showing is deleted, it falls back to Solid.

## Editing presets

1. `go60-leds edit` starts a small local server (127.0.0.1 only) and opens the editor in the browser:
   preset tabs, a colour picker and palette, click or drag to paint keys, right-click to pick up a
   colour, fill buttons per finger (both hands, left or right), rename, duplicate, reorder and delete.
   **Save** (Ctrl+S) writes `config/led-presets.json`. Ctrl+C in the terminal stops the server.
2. `go60-build` builds the presets in (it commits `config/` first; a presets-only commit is titled
   "LED presets: …"), then flashes.

The JSON can also be edited by hand: `{"presets": [{"name": "…", "keys": {"LH C6R1": "#ff3b30", …}}]}`,
keys by MoErgo position name, colours as `#rrggbb`, `#000000` = off, missing keys = off.
`go60-leds check` validates it. At most 16 presets.

The repo ships with **Fingers** (one colour per finger, for learning touch typing) and **LED check**
(each row its own colour: R1 red, R2 yellow, R3 green, R4 blue, R5 purple; thumbs T1 white, T2 cyan,
T3 pink). LED check is there to verify the LED order after the first flash; delete it after that.

## How it works (for changes)

- `config/patches/rgb-presets.patch` patches MoErgo's `app/src/rgb_underglow.c` (v25.11): extra effects
  after Swirl, each drawing a per-LED colour table scaled by brightness.
- `go60-build` runs `go60-leds header` to turn the JSON into `led_presets.h` (one table per half,
  chosen by `CONFIG_BOARD_GO60_LH`), and `config/default.nix` applies the patch and copies the header in.
  Without the header the build is stock.
- Key → LED order is `LED_COLUMNS` / `LED_THUMBS` in `scripts/keymap.py`. The left half comes from the LED
  map in MoErgo's `go60_lh.dts`; the right half is assumed to mirror it, and the thumb order is read from
  that drawing. **Unverified until the user checks LED check on the keyboard.** If a column or thumb is
  wrong on one half, fix the mapping there (make it per side if the halves differ) and rebuild.
- If a new ZMK version (`go60-build --zmk`) changes `rgb_underglow.c`, the patch may fail to apply and the
  build stops at "applying patch". Re-make the patch against the new file (extract it from the build
  container's `/src` after `git checkout <tag>`).

## Things to tell the user

- **Layout Editor firmware has no presets.** Flashing an editor build drops them (`go60-flash` warns);
  the next `go60-build` brings them back.
- After flashing, the keyboard may still show the old effect. Step to the preset with Magic + LH C1R3.
