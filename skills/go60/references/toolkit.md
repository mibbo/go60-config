# The go60-config toolkit

What the user's Go60 setup can do, and how to guide them through each task. The user may not have
done a task for months, so walk them through it step by step and don't assume they remember.
**Run `go60-status` first** for anything about flashing, updating or the state of the setup. It shows
the flashed layout and firmware (and when), files waiting in `~/Downloads`, unpushed commits, and
whether the tools are installed.

## Contents
1. What the toolkit can do
2. Changing the layout and flashing (full walkthrough)
3. Flash problems
4. Other tasks: retry one half, roll back, see layout history, new machine
5. Where things are

## 1. What the toolkit can do

| Task | How |
|------|-----|
| Find a key or character, learn the layers | Ask Claude (this skill), or `go60-keys find/key/layers/show` |
| Visual cheat sheet | `go60-keys cheatsheet --open` (updated automatically after each flash) |
| See the state of the setup | `go60-status` |
| Flash a new layout | Layout Editor → Save and Build and download JSON → `go60-flash` (or Super+Shift+Ctrl+K) |
| Retry one half, re-flash, roll back | `go60-flash --right-only` / `--left-only` / `--latest` / `go60-flash firmware/<file>.uf2` |
| Layout history | `git log -p layout/current.json`; firmware history in `firmware/` |
| Rehearse flashing without the keyboard | `go60-flash --dry-run` (changes nothing) |
| Set up on another computer | clone the repo, run `scripts/install` |

`go60-flash --help` lists all flashing options. Check it rather than relying on memory.

## 2. Changing the layout and flashing

1. **Edit** in the MoErgo Layout Editor (my.moergo.com → Go60). For symbols, use
   `references/finnish-layout.md` to pick the combination that types the right character on a Finnish system.
2. **Save and Build.** This downloads `<layout id>_v<version>_<name>.uf2` to `~/Downloads`.
3. **Download the layout as JSON** too (`<layout id>_<name>.json`). Without it, the repo and this skill
   won't know about the change. `go60-flash` warns when it's missing.
4. **Run `go60-flash`** in a terminal, or press **Super+Shift+Ctrl+K**. It:
   - shows the firmware and its version, and warns if the version differs from the last flash
   - moves the `.uf2` to `firmware/` and saves the JSON as `layout/current.json` (both leave Downloads)
   - asks whether one or two USB-C cables are used
5. **Put each half into bootloader mode** when prompted. Notifications say what to do next.
   - Two cables: connect both, press **Magic + \\** (right half) and then **Magic + Tab** (left half).
   - One cable: plug into the right half and press Magic + \\. When told, move the cable to the left half and press Magic + Tab.
   - A slowly pulsing red LED by the power switch means bootloader mode. Each half then shows up as a drive
     (`GO60RHBOOT` / `GO60LHBOOT`), gets the file, and disappears when it's done.
6. **After a firmware version change** (e.g. v25.08 → v25.11, not just a layout change), do the
   configuration reset that `go60-flash` prints. Left half: hold Ctrl+E while powering on, for 5 s.
   Right half: hold Alt+I while powering on, for 5 s. Then power both on, press Magic+T twice, and wait
   1 minute. The layout is kept.
7. **Commit and push** when `go60-flash` asks. If a push fails, `git -C ~/sync/git/go60-config push`
   from a terminal where the SSH key is available.

## 3. Flash problems

- **A combo does nothing**: use the power-on fallback. Power the half off, hold the outermost thumb key
  and the middle-finger home key of that half (T3 + C3R3: **Alt+K** on the right, **Ctrl+D** on the left
  in the factory layout), and power on.
- **Drive never appears**: use a direct cable, not a hub. MoErgo says bad hubs and cables cause most
  failures. Try the other cable or port. In the timeout prompt, choose wait again or skip.
- **Drive stays after copying**: the flash didn't finish. `go60-flash` offers to retry. Put the half
  back into bootloader mode.
- **Halves don't talk to each other after flashing**, or a version changed: do the configuration reset in step 6.
- **Only one half flashed**: `go60-flash --latest --left-only` (or `--right-only`).

## 4. Other tasks

- **Re-flash the current firmware**: `go60-flash --latest`.
- **Roll back to an older firmware**: `go60-flash firmware/<older file>.uf2`. Note that
  `layout/current.json` isn't rolled back automatically, so this skill would describe the wrong layout.
  Restore the matching JSON from git (`git log -- layout/current.json`, then
  `git checkout <commit> -- layout/current.json`), or import that JSON back into the Layout Editor and
  flash normally.
- **See what changed in the layout**: `git log -p layout/current.json`, or compare two versions with
  `go60-keys --file <exported.json> show`.
- **New computer**: `gh repo clone go60-config ~/sync/git/go60-config`, then `scripts/install`. Add the
  Hyprland shortcut again with the omarchy skill if it's needed.

## 5. Where things are

- Repo: `~/sync/git/go60-config` (GitHub: private repo `go60-config`). The human-oriented overview is
  its `README.md`.
- Commands (symlinked into `~/.local/bin` by `scripts/install`): `go60-flash`, `go60-keys`, `go60-status`.
- Skill: `~/.claude/skills/go60`, a symlink to `skills/go60/` in the repo, so edits there apply immediately.
- Cheat sheet file: `~/.cache/go60/cheatsheet.html`.
- Future plan: move to MoErgo's `go60-zmk-config` (keymap as ZMK source under `config/`, built locally or
  with GitHub Actions). The repo layout already leaves room for it.
