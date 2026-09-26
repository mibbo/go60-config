"""Go60 layout model: physical key positions, Finnish (fi, kotoistus) legends and
binding descriptions for a MoErgo Layout Editor JSON export.

Shared by the go60-keys command and the cheat sheet generator.
"""

import json
import os
from pathlib import Path

# ---------------------------------------------------------------- files ---

SKILL_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = SKILL_DIR.parent.parent


def layout_path():
    env = os.environ.get("GO60_LAYOUT_FILE")
    return Path(env) if env else REPO_DIR / "layout" / "current.json"


def load_layout(path=None):
    path = Path(path) if path else layout_path()
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------ physical layout ---
# Index -> position, per MoErgo's naming: C1 = inner (index finger) column,
# C6 = outer pinky column, R1 = number row ... R4 = bottom letter row, R5 = the
# extra bottom keys that only columns C2-C4 have, T1 = innermost thumb key.
# Sources: official go60.keymap row structure, Go60 tech spec (C2-C4 have 5
# rows, 3-key thumb cluster), bootloader docs (T3 + C3R3 = Ctrl+D / Alt+K),
# and the factory layout notes (index 54 = LH T1, index 47 = RH C6R4).

ROW_NAMES = {1: "number row", 2: "top row", 3: "home row", 4: "bottom row", 5: "extra bottom row"}
FINGERS = {1: "index finger", 2: "index finger", 3: "middle finger", 4: "ring finger",
           5: "pinky", 6: "pinky"}
COLUMN_NOTES = {1: "inner column, reach toward the middle", 2: "", 3: "", 4: "",
                5: "", 6: "outer column, reach outward"}
THUMB_NOTES = {1: "innermost thumb key", 2: "middle thumb key", 3: "outermost thumb key (wide)"}


def _build_positions():
    pos = {}
    for r in range(4):
        for j in range(12):
            i = r * 12 + j
            if j < 6:
                pos[i] = ("L", "C", 6 - j, r + 1)
            else:
                pos[i] = ("R", "C", j - 5, r + 1)
    for i, c in zip(range(48, 51), (4, 3, 2)):
        pos[i] = ("L", "C", c, 5)
    for i, c in zip(range(51, 54), (2, 3, 4)):
        pos[i] = ("R", "C", c, 5)
    for i, t in zip(range(54, 57), (1, 2, 3)):
        pos[i] = ("L", "T", t, None)
    for i, t in zip(range(57, 60), (3, 2, 1)):
        pos[i] = ("R", "T", t, None)
    return pos


POSITIONS = _build_positions()


def position_name(i):
    side, kind, n, row = POSITIONS[i]
    hand = "LH" if side == "L" else "RH"
    return f"{hand} T{n}" if kind == "T" else f"{hand} C{n}R{row}"


def position_words(i):
    """Plain-language description, e.g. 'left hand, home row, middle finger'."""
    side, kind, n, row = POSITIONS[i]
    hand = "left hand" if side == "L" else "right hand"
    if kind == "T":
        return f"{hand}, thumb, {THUMB_NOTES[n]}"
    parts = [hand, ROW_NAMES[row], FINGERS[n]]
    if COLUMN_NOTES[n]:
        parts.append(COLUMN_NOTES[n])
    return ", ".join(parts)


def parse_position(text):
    """Accept an index (0-59) or a name like 'LH T1', 'rh-c3r2', 'RHC6R4'."""
    t = text.strip().upper().replace("-", "").replace("_", "").replace(" ", "")
    if t.isdigit() and 0 <= int(t) < 60:
        return int(t)
    for i in range(60):
        if position_name(i).replace(" ", "") == t:
            return i
    raise ValueError(f"unknown key position: {text!r} (use 0-59 or e.g. 'LH T1', 'RH C3R2')")


# ----------------------------------------------------- Finnish legends ---
# What each HID code types with the Finnish layout (xkb fi / kotoistus, the
# default variant): (plain, Shift, AltGr, Shift+AltGr). None = nothing useful.

FI = {
    "GRAVE": ("§", "½", None, None),
    "N1": ("1", "!", None, "¡"),
    "N2": ("2", '"', "@", "”"),
    "N3": ("3", "#", "£", "»"),
    "N4": ("4", "¤", "$", "«"),
    "N5": ("5", "%", "‰", "“"),
    "N6": ("6", "&", "‚", "„"),
    "N7": ("7", "/", "{", None),
    "N8": ("8", "(", "[", "<"),
    "N9": ("9", ")", "]", ">"),
    "N0": ("0", "=", "}", "°"),
    "MINUS": ("+", "?", "\\", "¿"),
    "EQUAL": ("´", "`", None, None),
    "LBKT": ("å", "Å", None, None),
    "RBKT": ("¨", "^", "~", None),
    "SEMI": ("ö", "Ö", "ø", "Ø"),
    "SQT": ("ä", "Ä", "æ", "Æ"),
    "BSLH": ("'", "*", None, None),
    "NON_US_HASH": ("'", "*", None, None),
    "NON_US_BSLH": ("<", ">", "|", None),
    "COMMA": (",", ";", "’", "‘"),
    "DOT": (".", ":", None, None),
    "FSLH": ("-", "_", "–", None),
    "SPACE": (" ", " ", None, None),
    "KP_N0": ("0", None, None, None),
    "KP_DOT": (",", None, None, None),
    "KP_PLUS": ("+", None, None, None),
    "KP_MINUS": ("-", None, None, None),
    "KP_MULTIPLY": ("*", None, None, None),
    "KP_SLASH": ("/", None, None, None),
    "KP_DIVIDE": ("/", None, None, None),
    "KP_EQUAL": ("=", None, None, None),
}
for _c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    FI[_c] = (_c.lower(), _c, None, None)
FI["E"] = ("e", "E", "€", None)
FI["S"] = ("s", "S", "ß", None)
FI["I"] = ("i", "I", None, "|")
for _d in range(1, 10):
    FI[f"KP_N{_d}"] = (str(_d), None, None, None)

# Dead keys: pressing them types nothing until the next key (´ then e = é).
DEAD = {("EQUAL", 0), ("EQUAL", 1), ("RBKT", 0), ("RBKT", 1), ("RBKT", 2)}

# ZMK aliases -> (canonical code, implied modifiers). Shifted aliases are
# US-shifted, e.g. LPAR = Shift+9, which types ")" with the Finnish layout.
ALIASES = {
    "NUMBER_0": "N0", "NUMBER_1": "N1", "NUMBER_2": "N2", "NUMBER_3": "N3", "NUMBER_4": "N4",
    "NUMBER_5": "N5", "NUMBER_6": "N6", "NUMBER_7": "N7", "NUMBER_8": "N8", "NUMBER_9": "N9",
    "SEMICOLON": "SEMI", "APOS": "SQT", "APOSTROPHE": "SQT", "SINGLE_QUOTE": "SQT",
    "SLASH": "FSLH", "BACKSLASH": "BSLH", "LEFT_BRACKET": "LBKT", "RIGHT_BRACKET": "RBKT",
    "PERIOD": "DOT", "GRAVE_ACCENT_AND_TILDE": "GRAVE", "NUBS": "NON_US_BSLH", "NUHS": "NON_US_HASH",
    "ENTER": "RET", "RETURN": "RET", "BACKSPACE": "BSPC", "DELETE": "DEL", "ESCAPE": "ESC",
    "SPC": "SPACE", "LSHIFT": "LSHFT", "RSHIFT": "RSHFT", "LCTL": "LCTRL", "RCTL": "RCTRL",
    "LEFT_ARROW": "LEFT", "RIGHT_ARROW": "RIGHT", "UP_ARROW": "UP", "DOWN_ARROW": "DOWN",
    "PAGE_UP": "PG_UP", "PAGE_DOWN": "PG_DN", "INSERT": "INS", "CAPSLOCK": "CAPS",
    "LEFT_GUI": "LGUI", "RIGHT_GUI": "RGUI", "LWIN": "LGUI", "LCMD": "LGUI",
}
SHIFTED_ALIASES = {
    "EXCL": "N1", "EXCLAMATION": "N1", "AT": "N2", "AT_SIGN": "N2", "HASH": "N3", "POUND": "N3",
    "DOLLAR": "N4", "DLLR": "N4", "PRCNT": "N5", "PERCENT": "N5", "CARET": "N6", "AMPS": "N7",
    "AMPERSAND": "N7", "STAR": "N8", "ASTRK": "N8", "ASTERISK": "N8", "LPAR": "N9",
    "LEFT_PARENTHESIS": "N9", "RPAR": "N0", "RIGHT_PARENTHESIS": "N0", "UNDER": "MINUS",
    "UNDERSCORE": "MINUS", "PLUS": "EQUAL", "LBRC": "LBKT", "LEFT_BRACE": "LBKT",
    "RBRC": "RBKT", "RIGHT_BRACE": "RBKT", "PIPE": "BSLH", "COLON": "SEMI", "DQT": "SQT",
    "DOUBLE_QUOTES": "SQT", "LT": "COMMA", "LESS_THAN": "COMMA", "GT": "DOT",
    "GREATER_THAN": "DOT", "QMARK": "FSLH", "QUESTION": "FSLH", "TILDE": "GRAVE",
}

MOD_WRAPPERS = {"LS": "shift", "RS": "shift", "LC": "ctrl", "RC": "ctrl", "LA": "alt",
                "RA": "altgr", "LG": "super", "RG": "super"}
MOD_KEYS = {"LSHFT": "shift", "RSHFT": "shift", "LCTRL": "ctrl", "RCTRL": "ctrl",
            "LALT": "alt", "RALT": "altgr", "LGUI": "super", "RGUI": "super"}
MOD_LABEL = {"ctrl": "Ctrl", "alt": "Alt", "altgr": "AltGr", "shift": "Shift", "super": "Super"}
MOD_ORDER = ["ctrl", "alt", "altgr", "shift", "super"]

NAMED = {
    "SPACE": "Space", "RET": "Enter", "BSPC": "Backspace", "DEL": "Delete", "TAB": "Tab",
    "ESC": "Esc", "UP": "↑", "DOWN": "↓", "LEFT": "←", "RIGHT": "→", "HOME": "Home",
    "END": "End", "PG_UP": "PgUp", "PG_DN": "PgDn", "INS": "Insert", "CAPS": "Caps Lock",
    "PSCRN": "PrtSc", "SLCK": "Scroll Lock", "PAUSE_BREAK": "Pause", "K_APP": "Menu",
    "KP_NUM": "Num Lock", "KP_ENTER": "Enter (keypad)", "LSHFT": "Shift", "RSHFT": "Shift",
    "LCTRL": "Ctrl", "RCTRL": "Ctrl", "LALT": "Alt", "RALT": "AltGr", "LGUI": "Super",
    "RGUI": "Super", "C_MUTE": "Mute", "C_VOL_UP": "Vol +", "C_VOL_DN": "Vol −",
    "C_PP": "Play/Pause", "C_NEXT": "Next track", "C_PREV": "Prev track",
    "C_BRI_UP": "Bright +", "C_BRI_DN": "Bright −", "C_BRI_INC": "Bright +", "C_BRI_DEC": "Bright −",
}
for _f in range(1, 25):
    NAMED[f"F{_f}"] = f"F{_f}"


def canonical(code):
    """Normalize a ZMK key code. Returns (code, extra_mods)."""
    c = str(code).upper()
    if c in SHIFTED_ALIASES:
        return SHIFTED_ALIASES[c], {"shift"}
    return ALIASES.get(c, c), set()


def parse_key_param(p):
    """A &kp parameter (possibly wrapped in LS(...) etc.) -> (code, mods)."""
    mods = set()
    while p.get("params") and str(p.get("value")).upper() in MOD_WRAPPERS:
        mods.add(MOD_WRAPPERS[str(p["value"]).upper()])
        p = p["params"][0]
    code, extra = canonical(p.get("value"))
    return code, mods | extra


def fi_char(code, mods):
    """Character typed by code+mods with the Finnish layout, or None."""
    legends = FI.get(code)
    if not legends:
        return None
    level = {frozenset(): 0, frozenset({"shift"}): 1, frozenset({"altgr"}): 2,
             frozenset({"shift", "altgr"}): 3}.get(frozenset(mods))
    if level is None:
        return None
    return legends[level]


def is_dead(code, mods):
    level = {frozenset(): 0, frozenset({"shift"}): 1, frozenset({"altgr"}): 2}.get(frozenset(mods))
    return (code, level) in DEAD


def key_label(code, mods):
    """Short human label, e.g. 'å', '/', 'Ctrl+Z', 'Ctrl+Shift+Tab', '↑'."""
    ch = fi_char(code, mods)
    if ch is not None and ch != " ":
        return ch
    base = NAMED.get(code)
    if base is None:
        plain = fi_char(code, set())
        base = plain.upper() if plain and plain.strip() else code
    prefix = "".join(MOD_LABEL[m] + "+" for m in MOD_ORDER if m in mods)
    return prefix + base


def _pv(p):
    return p.get("value") if isinstance(p, dict) else p


def zmk_text(b):
    """Binding as ZMK-like text, e.g. '&kp LS(N7)'."""
    def arg(p):
        s = str(p.get("value"))
        if p.get("params"):
            s += "(" + ",".join(arg(q) for q in p["params"]) + ")"
        return s
    params = b.get("params") or []
    return " ".join([b.get("value", "")] + [arg(p) for p in params])


# ------------------------------------------------------------ bindings ---

class Layout:
    def __init__(self, data):
        self.data = data
        self.names = data.get("layer_names") or [f"Layer {i}" for i in range(len(data["layers"]))]
        self.layers = data["layers"]
        self.macros = {m.get("name"): m for m in data.get("macros") or []}
        self.holdtaps = {h.get("name"): h for h in data.get("holdTaps") or []}
        self.magic_layer = next((i for i, n in enumerate(self.names) if n.lower() == "magic"), None)

    def layer_index(self, text):
        t = str(text).strip()
        if t.isdigit() and int(t) < len(self.layers):
            return int(t)
        for i, n in enumerate(self.names):
            if n.lower() == t.lower():
                return i
        raise ValueError(f"unknown layer {text!r}; layers: {', '.join(self.names)}")

    def layer_label(self, n):
        try:
            n = int(n)
            return f"{self.names[n]} (layer {n})"
        except (ValueError, IndexError, TypeError):
            return f"layer {n}"

    def describe(self, b):
        """Return a dict describing binding b:
        kind: char | mod | layer | nav | media | system | trans | none | other
        label: short legend, sub: secondary legend, text: full plain explanation,
        taps: [(code, mods)] the key sends when tapped, holds: [mod] when held,
        layers: [(layer, how)] layer changes it causes."""
        v = b.get("value", "")
        ps = b.get("params") or []
        d = {"kind": "other", "label": v.lstrip("&"), "sub": "", "text": "", "taps": [], "holds": [],
             "layers": [], "zmk": zmk_text(b)}

        def tap_key(p):
            code, mods = parse_key_param(p)
            d["taps"].append((code, mods))
            return code, mods

        if v == "&kp" and ps:
            code, mods = tap_key(ps[0])
            d["label"] = key_label(code, mods)
            ch = fi_char(code, mods)
            if code in MOD_KEYS and not mods:
                d["kind"] = "mod"
                d["text"] = f"{d['label']} modifier (hold it while pressing another key)"
            elif ch is not None and ch.strip():
                d["kind"] = "char"
                d["text"] = f"types {ch}" + (" (dead key: press it, then the letter)" if is_dead(code, mods) else "")
                if is_dead(code, mods):
                    d["sub"] = "dead key"
            elif code.startswith("C_"):
                d["kind"] = "media"
                d["text"] = d["label"]
            elif code in ("UP", "DOWN", "LEFT", "RIGHT", "HOME", "END", "PG_UP", "PG_DN"):
                d["kind"] = "nav"
                d["text"] = d["label"] if mods else f"{d['label']} (navigation)"
            else:
                d["kind"] = "char" if code in FI else "nav"
                d["text"] = d["label"] if mods else f"{d['label']} key"
                if mods and not (mods <= {"shift"} or mods == {"altgr"}):
                    d["kind"] = "nav"
                    d["text"] = f"shortcut {d['label']}"
        elif v == "&mt" and len(ps) >= 2:
            mod_code, _ = canonical(_pv(ps[0]))
            code, mods = tap_key(ps[1])
            mod = MOD_KEYS.get(mod_code, mod_code)
            d["holds"].append(mod)
            d["kind"] = "mod"
            d["label"] = key_label(code, mods)
            d["sub"] = f"hold {MOD_LABEL.get(mod, mod)}"
            d["text"] = f"tap: {key_label(code, mods)}, hold: {MOD_LABEL.get(mod, mod)}"
        elif v == "&lt" and len(ps) >= 2:
            n = _pv(ps[0])
            code, mods = tap_key(ps[1])
            d["layers"].append((n, "hold this key"))
            d["kind"] = "layer"
            d["label"] = key_label(code, mods)
            d["sub"] = f"hold {self._short(n)}"
            d["text"] = f"tap: {key_label(code, mods)}, hold: {self.layer_label(n)}"
        elif v in ("&mo", "&to", "&tog", "&sl", "&layer") and ps:
            n = _pv(ps[0])
            how = {
                "&mo": "hold this key (the layer is on while you hold it)",
                "&to": "tap this key (switches and stays)",
                "&tog": "tap this key (toggles the layer on/off)",
                "&sl": "tap this key (the next key press uses the layer)",
                "&layer": "hold this key (on while held), or double-tap it to lock the layer on "
                          "(single-tap it again to go back to the base layer)",
            }[v]
            d["layers"].append((n, how))
            d["kind"] = "layer"
            d["label"] = self._short(n)
            d["sub"] = {"&mo": "hold", "&to": "tap: go to", "&tog": "toggle", "&sl": "one-shot",
                        "&layer": "hold / 2×tap"}[v]
            d["text"] = f"{self.layer_label(n)}: {how}"
        elif v == "&magic":
            d["kind"] = "layer"
            d["label"] = "Magic"
            d["sub"] = "hold"
            if self.magic_layer is not None:
                d["layers"].append((self.magic_layer, "hold the Magic key"))
            d["text"] = "Magic key: hold it for the Magic layer (Bluetooth, RGB, bootloader, reset)"
        elif v == "&sk" and ps:
            code, _ = canonical(_pv(ps[0]))
            mod = MOD_KEYS.get(code, code)
            d["kind"] = "mod"
            d["label"] = MOD_LABEL.get(mod, code)
            d["sub"] = "sticky"
            d["text"] = f"sticky {d['label']}: tap it, and it applies to the next key"
        elif v == "&trans":
            d.update(kind="trans", label="▽", text="transparent: does what the key does on the base layer")
        elif v == "&none":
            d.update(kind="none", label="", text="does nothing on this layer")
        elif v == "&bootloader":
            d.update(kind="system", label="Boot", sub="flash mode",
                     text="puts this half into bootloader mode for flashing (GO60LHBOOT / GO60RHBOOT)")
        elif v == "&reset":
            d.update(kind="system", label="Reset", text="restarts this half")
        elif v == "&out" and ps:
            what = str(_pv(ps[0]))
            d.update(kind="system", label={"OUT_USB": "USB", "OUT_BLE": "BT", "OUT_TOG": "USB/BT"}.get(what, what),
                     sub="output", text=f"send keystrokes over {what.replace('OUT_', '')}")
        elif v == "&bt" and ps:
            what = str(_pv(ps[0]))
            extra = f" {_pv(ps[1])}" if len(ps) > 1 else ""
            lab = {"BT_CLR": "BT clear", "BT_CLR_ALL": "BT clear all", "BT_NXT": "BT next",
                   "BT_PRV": "BT prev", "BT_SEL": f"BT {extra.strip()}"}.get(what, what)
            txt = {"BT_CLR": "forget the pairing of the current Bluetooth profile",
                   "BT_CLR_ALL": "forget all Bluetooth pairings"}.get(what, f"Bluetooth: {what}{extra}")
            d.update(kind="system", label=lab, text=txt)
        elif v.startswith("&bt_") and v[4:].isdigit():
            d.update(kind="system", label=f"BT {v[4:]}", sub="profile",
                     text=f"switch to Bluetooth profile {v[4:]}")
        elif v == "&rgb_ug" and ps:
            what = str(_pv(ps[0]))
            d.update(kind="system", label=what.replace("RGB_", ""), sub="RGB", text=f"RGB lighting: {what}")
        elif v.lstrip("&") in self.macros:
            d.update(kind="other", label=v.lstrip("&"), sub="macro", text=f"macro {v.lstrip('&')}")
        elif v.lstrip("&") in self.holdtaps:
            d.update(kind="other", label=v.lstrip("&"), sub="hold-tap", text=f"custom hold-tap {v.lstrip('&')}")
        else:
            d["text"] = d["zmk"]
        return d

    def _short(self, n):
        try:
            return self.names[int(n)]
        except (ValueError, IndexError, TypeError):
            return f"L{n}"

    def binding(self, layer, i):
        return self.layers[layer][i]

    def effective(self, layer, i):
        """(layer, description) actually used at position i on this layer.
        Transparent keys fall through to the base layer, which is where every
        layer in a MoErgo layout is normally reached from."""
        d = self.describe(self.layers[layer][i])
        if d["kind"] == "trans":
            return 0, self.describe(self.layers[0][i])
        return layer, d

    def reach(self, target):
        """How to activate layer `target`: list of (from_layer, index, how)."""
        out = []
        for l, keys in enumerate(self.layers):
            for i, b in enumerate(keys):
                for n, how in self.describe(b)["layers"]:
                    try:
                        if int(n) == target and l != target:
                            out.append((l, i, how))
                    except (ValueError, TypeError):
                        pass
        out.sort(key=lambda t: (t[0] != 0, t[0], t[1]))
        return out

    def is_test_layer(self, l):
        return "factory" in self.names[l].lower() or "test" in self.names[l].lower()
