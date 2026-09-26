# Split keyboard basics for the Go60

Use this to explain concepts in plain words. Always check the real layout with `go60-keys` before
naming specific keys, because the user may have changed it.

## Contents
1. Home position and columns
2. Layers
3. Thumb keys and the Magic key
4. Learning tips
5. Changing the layout
6. Flashing and troubleshooting

## 1. Home position and columns

- Each hand rests on its home row (R3): left fingers on A S D F, right fingers on J K L Ö. The index
  fingers find F and J by the bumps on those keys, when the keycaps have them.
- Keys sit in straight columns, not staggered rows. Each finger moves straight up and down its own
  column. The index fingers cover two columns (C1 and C2), and the pinkies cover two (C5 and C6).
- Keys that sat in the middle of a normal keyboard (T, G, B, Y, H, N) are now reached by the index
  finger moving inward, into column C1.

## 2. Layers

A layer is a whole second (third, …) set of meanings for the same keys, like Shift but for everything.
The base layer is active by default. Other layers are reached with layer keys:

- **Hold** a layer key: the layer is on only while it's held, like Shift.
- **Double-tap** a MoErgo layer key (`&layer`): the layer stays on. Tap the key once more to go back.
- **`&to`** keys switch to a layer and stay there until another `&to` key is pressed.
- Keys marked ▽ (transparent) on a layer do whatever the base layer does.

If typing suddenly produces numbers or arrows instead of letters, a layer is probably locked on. Tap
the layer key again, or use the key that returns to the base layer.

## 3. Thumb keys and the Magic key

- Each hand has three thumb keys (T1 innermost, T3 outermost and wider). On a split keyboard the thumbs
  do much more than space: in the factory layout they hold Shift, Ctrl, Alt, AltGr, Space, Enter and
  the SymbolNav layer.
- **Magic** (factory: left pinky, outer bottom key, LH C6R4) is held to reach the Magic layer. That layer
  has Bluetooth profiles, RGB lighting, USB/Bluetooth output, reset, and the bootloader keys
  (Magic+Tab for the left half, Magic+\ for the right).
- Hold-tap keys (`&mt`) do one thing when tapped and another when held. In the factory layout, the right
  innermost thumb is Enter on tap and AltGr on hold. Holding it too long when you meant Enter gives AltGr instead.

## 4. Learning tips

- Expect a slow start: most people are back to normal speed after one to three weeks of daily use.
  Accuracy first, speed later.
- Practice in short sessions with a typing trainer, such as keybr.com or monkeytype.com, which support a
  Finnish word list.
- Learn the layers one at a time. Start with the letters, then the symbols you use most, then navigation.
- Keep the cheat sheet open while learning: `go60-keys cheatsheet --open` shows each layer with Finnish
  legends and has a search box.
- Remap only after using the layout for a while. Change things that keep bothering you, one or two at a time.

## 5. Changing the layout

There are two ways. You can **ask Claude to change the text keymap** (`config/go60.keymap`, see
`keymap-editing.md`) and then run `go60-build`, or use the web Layout Editor:

1. Open the Layout Editor at my.moergo.com (Go60) and edit the layer or key.
2. **Save and Build** downloads a `.uf2` to `~/Downloads`.
3. Also download the layout as **JSON**, so the repo keeps a readable copy.
4. Run `go60-flash` (or press Super+Shift+Ctrl+K). It flashes both halves, moves both files into the repo,
   and offers to commit them.

When suggesting a change for the editor, describe it as editor steps: which layer, which key (in plain words plus the
position name), and which behavior (e.g. "Key Press → AltGr+7" for `{`). Use `references/finnish-layout.md`
to pick the code that gives the right Finnish character.

## 6. Flashing and troubleshooting

- `go60-flash` walks through it. The bootloader keys are Magic+\ (right half) and Magic+Tab (left half).
  The fallbacks are: power off, hold Alt+K (right) or Ctrl+D (left), and power on. A slowly pulsing red LED
  means bootloader mode.
- After a firmware *version* change, do the configuration reset that `go60-flash` prints.
- Use direct USB-C cables without a hub. MoErgo says bad hubs and cables cause most flashing failures.
