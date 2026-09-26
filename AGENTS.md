# Agent guide: go60-config

Firmware history, current layout, flashing scripts and a Claude skill for the user's MoErgo Go60 split
keyboard (ZMK firmware). The layout is edited in MoErgo's web Layout Editor, not as ZMK source. The OS is
Omarchy (Arch + Hyprland) with the Finnish keyboard layout (`fi`). The user is new to split keyboards.

## Files

| Path | What it is |
|------|------------|
| `layout/current.json` | The layout that was last flashed (Layout Editor JSON export). `git log -p layout/current.json` shows changes over time. |
| `firmware/*.uf2` | Every flashed firmware, named `<flash date>_v<firmware version>_<layout name>_<layout id>.uf2`. Binary: don't try to read keymaps from them, and don't edit or rewrite them. |
| `scripts/go60-flash` | Flashing workflow (see `README.md`). Interactive; without the keyboard, only run it with `--dry-run`. |
| `scripts/install` | Symlinks `go60-flash`, `go60-keys` and `go60-status` into `~/.local/bin` and the skill into `~/.claude/skills/go60`. |
| `skills/go60/` | The `go60` Claude skill: `SKILL.md`, the `go60-keys` tool (`scripts/`), the cheat sheet template (`assets/`), and reference docs (`references/`). |

## Answering layout questions

Follow `skills/go60/SKILL.md`. In short, use `go60-keys find|key|layers|show` instead of parsing the JSON by
hand, because it translates key codes to Finnish characters and indexes to physical positions. The reference
docs are in `skills/go60/references/` (key positions, Finnish layout, beginner guide).

## Editing this repo

- Position mapping and Finnish legends are defined once, in `skills/go60/scripts/keymap.py`. The CLI and the
  cheat sheet both use it. Keep `references/*.md` in sync when changing it.
- After changing the skill or `go60-keys`, check with `go60-keys find å '{' enter`,
  `go60-keys show 2` and `go60-keys cheatsheet`. Test prompts are in `skills/go60/evals/evals.json`.
- Planned for later: move to MoErgo's `go60-zmk-config` template (ZMK keymap source under `config/`, built
  locally or with GitHub Actions). Keep the top level free for those files. This repo uses `scripts/`,
  `firmware/`, `layout/` and `skills/`.
