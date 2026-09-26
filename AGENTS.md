# Agent guide: go60-config

Firmware history, current layout, build and flashing scripts, and a Claude skill for the user's MoErgo Go60
split keyboard (ZMK firmware). The layout is edited either in MoErgo's web Layout Editor or as text in
`config/go60.keymap` (built locally with Podman). Both paths are supported and end in `go60-flash`. The OS is
Omarchy (Arch + Hyprland) with the Finnish keyboard layout (`fi`). The user is new to split keyboards.

## Files

| Path | What it is |
|------|------------|
| `layout/current.json` | The layout that was last flashed (Layout Editor JSON export). `git log -p layout/current.json` shows changes over time. |
| `firmware/*.uf2` | Every flashed firmware, named `<flash date>_v<firmware version>_<layout name>_<layout id>.uf2`. Binary: don't try to read keymaps from them, and don't edit or rewrite them. |
| `config/go60.keymap` | The layout as an editable ZMK keymap (generated grid + Finnish legend comments). `config/*` other files and `Dockerfile` are from MoErgo's go60-zmk-config template (commit 8ccc854; the Dockerfile is patched for Podman: fully qualified base image and a quoted entrypoint heredoc); `build/` is build output (ignored). |
| `scripts/go60-build` | Checks the keymap, commits it, builds with Podman (ZMK version = currently flashed one), then runs `go60-flash --layout-json … --source …`. |
| `scripts/go60-flash` | Flashing workflow (see `README.md`). Interactive; without the keyboard, only run it with `--dry-run`. |
| `scripts/install` | Symlinks `go60-flash`, `go60-build`, `go60-keymap`, `go60-keys` and `go60-status` into `~/.local/bin` and the skill into `~/.claude/skills/go60`. |
| `skills/go60/` | The `go60` Claude skill: `SKILL.md`, tools in `scripts/` (`go60-keys`, `go60-keymap`, `go60-status`; `keymap.py` = positions and Finnish legends, `zmk_keymap.py` = JSON ↔ keymap converter), the cheat sheet template (`assets/`), and reference docs (`references/`). |

## Answering layout questions

Follow `skills/go60/SKILL.md`. In short, use `go60-keys find|key|layers|show` instead of parsing the JSON by
hand, because it translates key codes to Finnish characters and indexes to physical positions. The reference
docs are in `skills/go60/references/` (key positions, Finnish layout, beginner guide).

## Editing this repo

### Keep the docs and the skill in sync (required)

The `go60` skill is how the user gets help from any folder, and `README.md` is their manual. If they fall
behind the code, the user gets wrong answers or misses features. So **every change to what the repo does
must update the docs in the same commit**, without being asked. Before committing, check this table:

| If you change… | Also update |
|----------------|-------------|
| a command, option or behavior in `scripts/go60-flash` | its `--help` text, `README.md` (workflow/options), `skills/go60/references/toolkit.md` |
| `go60-keys` or `go60-status` (commands, output) | `README.md` (Layout help), `skills/go60/SKILL.md` (commands it tells Claude to run), `references/toolkit.md` |
| `keymap.py` (positions, Finnish legends, behaviors) | `references/key-positions.md` or `references/finnish-layout.md` |
| `zmk_keymap.py`, `go60-keymap` or `go60-build` (keymap format, conversion, build) | `references/keymap-editing.md`, the keymap header comment in `zmk_keymap.py`, `README.md` (Editing the layout as text); run the round-trip check below |
| the cheat sheet (`assets/cheatsheet.html`) | the cheat sheet lines in `README.md` and `references/toolkit.md`, if what it does changed |
| a new script, command or file type | `scripts/install` (if it goes on PATH), the file tables in `README.md` and this file, `references/toolkit.md` |
| the flashing procedure, key combos or reset steps | `README.md`, `references/toolkit.md`, `references/beginner-guide.md` |
| the Hyprland shortcut | `README.md`, `references/toolkit.md` (edit `~/.config/hypr/` with the omarchy skill) |
| what the skill should trigger on | the `description` in `skills/go60/SKILL.md` |
| anything with a user-visible effect | a test prompt in `skills/go60/evals/evals.json`, if it's a new kind of question |

Rules of thumb:
- One fact, one place. Keep details in the most specific file and link to it rather than copying.
  For example, flag lists live in `go60-flash --help`, and the other docs point there.
- Keep `SKILL.md` short: it's loaded every time the skill triggers. Put details in `references/`.
- The skill folder is symlinked into `~/.claude/skills/go60`, so edits apply to new Claude sessions
  immediately. If you add something that must be installed, update and re-run `scripts/install`.
- Mention in your final message which docs you updated.

### Other notes

- Position mapping and Finnish legends are defined once, in `skills/go60/scripts/keymap.py`. The CLI and the
  cheat sheet both use it. Keep `references/*.md` in sync when changing it.
- After changing the skill or `go60-keys`, check with `go60-keys find å '{' enter`,
  `go60-keys show 2` and `go60-keys cheatsheet`. Test prompts are in `skills/go60/evals/evals.json`.
- After changing the converter, the JSON → keymap → JSON round trip must stay lossless:
  `go60-keymap --keymap /tmp/t.keymap init --from layout/current.json` checks it. Then run `go60-keymap check`
  on the real keymap.
- `layout/current.json` must always describe what's flashed. Only `go60-flash` writes it, and only after at
  least one half was flashed (rollbacks restore the layout committed with that firmware).
- End-to-end test without the keyboard: copy the repo to a scratch dir, run `git remote remove origin` there,
  and set `GO60_DOWNLOADS` to a scratch dir. Then run that copy's scripts with `GO60_TEST_APPLY_FILES=1` and
  `--dry-run`. The drives are simulated, but archiving, layout saving, keymap sync and commits really happen
  (in the copy). Cover editor flash, unflashed keymap edits + editor flash (no overwrite; `go60-keymap merge`),
  build path, stale editor layout warning, rollback, and nothing flashed. Never set that variable in the real repo.
- The repo follows MoErgo's template layout (`config/`, `Dockerfile` at the top level). Builds are local only;
  don't add MoErgo's GitHub Actions workflow unless asked.
