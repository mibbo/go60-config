"""Convert between MoErgo Layout Editor JSON and a readable ZMK keymap (config/go60.keymap).

JSON -> keymap: `to_keymap(data)` writes a complete keymap for MoErgo's go60-zmk-config build,
laid out like the keyboard. Keymap -> JSON: `to_json(text, base)` parses it back into the
editor's format, reusing entries from `base` wherever a key's meaning didn't change, so
diffs of layout/current.json only show real changes.
"""

import copy
import json
import re
import time

# ------------------------------------------------------------------ layout ---

# Array indexes per text row, in array order. Rows R1-R4: left C6..C1, right C1..C6.
ROWS = [list(range(r * 12, r * 12 + 12)) for r in range(4)] + [list(range(48, 54)), list(range(54, 60))]
# Grid column (0-11) of each index in the row, so the text lines up like the keyboard.
GRID = {}
for r in range(4):
    for j in range(12):
        GRID[r * 12 + j] = j
for i, col in zip(range(48, 54), (2, 3, 4, 7, 8, 9)):
    GRID[i] = col
for i, col in zip(range(54, 60), (3, 4, 5, 6, 7, 8)):
    GRID[i] = col
ROW_LABELS = ["R1", "R2", "R3", "R4", "R5", "T "]

LAYER_PARAM_BEHAVIORS = {"&mo", "&to", "&tog", "&sl", "&lt"}
NUMBER_LAYER_BEHAVIORS = {"&layer", "&to"}   # the editor stores these layer params as numbers

MARK = "go60-config"
CUSTOM_BEHAVIORS_BEGIN = f"/* {MARK}: custom behaviors (kept when converting to Layout Editor JSON) */"
CUSTOM_BEHAVIORS_END = f"/* {MARK}: end of custom behaviors */"
CUSTOM_DT_BEGIN = f"/* {MARK}: custom devicetree */"
CUSTOM_DT_END = f"/* {MARK}: end of custom devicetree */"


class KeymapError(Exception):
    pass


def ident(name):
    s = re.sub(r"\W", "_", str(name))
    return s if not s[0].isdigit() else "_" + s


# -------------------------------------------------------- JSON -> keymap ---

def _param_text(p):
    s = str(p.get("value"))
    if p.get("params"):
        s += "(" + ",".join(_param_text(q) for q in p["params"]) + ")"
    return s


def binding_text(b, names):
    v = b.get("value", "")
    ps = b.get("params") or []

    def layer_ref(p):
        try:
            return f"LAYER_{ident(names[int(p.get('value'))])}"
        except (ValueError, IndexError, TypeError):
            return _param_text(p)

    if v == "&layer" and ps:
        return f"&td_LAYER_{ident(names[int(ps[0]['value'])])}"
    if v == "&magic" and not ps:
        return "&magic LAYER_Magic 0" if "Magic" in names else "&magic 0 0"
    if v == "&reset":
        return "&sys_reset"
    parts = [v]
    for n, p in enumerate(ps):
        parts.append(layer_ref(p) if v in LAYER_PARAM_BEHAVIORS and n == 0 else _param_text(p))
    return " ".join(parts)


def _processor_text(proc):
    params = []
    for p in proc.get("params") or []:
        if isinstance(p, list):
            params.append(p[0] if len(p) == 1 else "(" + " | ".join(p) + ")")
        else:
            params.append(str(p))
    return "<" + " ".join([proc["code"]] + params) + ">"


def _listener_text(listener):
    out = [f"{listener['code']} {{"]
    if listener.get("inputProcessors"):
        out.append("    input-processors = " + ", ".join(_processor_text(p) for p in listener["inputProcessors"]) + ";")
    for node in listener.get("nodes") or []:
        out.append(f"    {node['code']} {{")
        out.append("        layers = <" + " ".join(str(x) for x in node.get("layers") or []) + ">;")
        if node.get("inputProcessors"):
            out.append("        input-processors = " + ", ".join(_processor_text(p) for p in node["inputProcessors"]) + ";")
        out.append("    };")
    out.append("};")
    return "\n".join(out)


def _grid_lines(cells, legends, widths, indent="            "):
    lines = []
    for r, row in enumerate(ROWS):
        for kind, values in (("code", cells), ("legend", legends)):
            slots = [""] * 12
            for i in row:
                slots[GRID[i]] = values[i]
            text = ""
            for c in range(12):
                gap = "    " if c == 6 else " "
                text += (gap if c else "") + slots[c].ljust(widths[c])
            prefix = f"/* {ROW_LABELS[r]} */ " if kind == "code" else "//       "
            lines.append(f"{indent}{prefix}{text.rstrip()}")
    return lines


def _legends(data):
    """What each key does, in short (Finnish characters), for the comment lines."""
    try:
        import keymap as km
    except ImportError:
        return None
    L = km.Layout(data)
    out = []
    for layer in data["layers"]:
        row = []
        for b in layer:
            d = L.describe(b)
            lab = {"trans": "▽", "none": "·"}.get(d["kind"], d["label"] or "·")
            if d["kind"] == "mod" and d["sub"].startswith("hold "):
                lab = f"{lab}/{d['sub'][5:]}"   # e.g. Enter/AltGr for a mod-tap
            row.append(lab.replace(" ", "_") if len(lab) > 1 else lab)
        out.append(row)
    return out


def _header(data):
    title = data.get("title", "Go60 layout")
    return f"""/*
 * Go60 keymap: edit this file to change the layout, then run `go60-build` and `go60-flash`.
 * Started from the Layout Editor layout "{title}" ({data.get('uuid', '')[:8]}).
 *
 * Each layer's bindings are laid out like the keyboard, one text row per key row:
 *   R1-R4  left half C6 C5 C4 C3 C2 C1  |  right half C1 C2 C3 C4 C5 C6
 *          (C1 = inner index-finger column, C6 = outer pinky column; R1 = number row, R3 = home row)
 *   R5     the extra bottom keys: left C4 C3 C2  |  right C2 C3 C4
 *   T      thumb keys, in this order: left T1 T2 T3  |  right T3 T2 T1  (T1 = innermost)
 *
 * The // line under each row shows what the keys type with the Finnish layout (▽ = same as the base
 * layer, · = nothing). It's a comment for reading only; `go60-keymap format` refreshes it after edits.
 *
 * Every layer needs exactly 60 bindings. Common ones:
 *   &kp X            press key X (US key names: &kp LBKT types å with the Finnish layout)
 *   &kp RA(N7)       AltGr+7 = {{     &kp LS(N7) = Shift+7 = /     (see go60-keys / finnish-layout.md)
 *   &mt LCTRL A      tap: A, hold: Ctrl          &mo LAYER_X   layer X while held
 *   &td_LAYER_X      hold: layer X, double-tap: lock layer X     &to LAYER_X   switch to layer X
 *   &trans           same as the layer below     &none         nothing
 *
 * Check your edits with `go60-keymap check` (validates and lists what changed since the last flash).
 * Put your own behaviors and macros in the "custom behaviors" section, not in the generated ones.
 */"""


def to_keymap(data):
    names = data.get("layer_names") or []
    for field in ("macros", "holdTaps", "combos"):
        if data.get(field):
            raise KeymapError(f"the layout uses Layout Editor {field}, which go60-keymap can't convert yet")
    if "Magic" not in names:
        raise KeymapError("the layout has no layer named 'Magic' (needed by the Magic key)")
    layers = data["layers"]
    for n, layer in enumerate(layers):
        if len(layer) != 60:
            raise KeymapError(f"layer {names[n]} has {len(layer)} keys, expected 60")

    out = [_header(data), "",
           "#include <behaviors.dtsi>", "",
           "#include <dt-bindings/zmk/bt.h>",
           "#include <dt-bindings/zmk/ext_power.h>",
           "#include <dt-bindings/zmk/keys.h>",
           "#include <dt-bindings/zmk/outputs.h>",
           "#include <dt-bindings/zmk/rgb.h>",
           "#include <dt-bindings/zmk/input_transform.h>",
           "#include <dt-bindings/zmk/pointing.h>", "",
           "#include <input/processors.dtsi>",
           "#include <zephyr/dt-bindings/input/input-event-codes.h>", "",
           "// Layers (the number is the layer's position in the keymap below)"]
    out += [f"#define LAYER_{ident(n)} {i}" for i, n in enumerate(names)]
    used_td = sorted({int(b["params"][0]["value"]) for layer in layers for b in layer
                      if b.get("value") == "&layer" and b.get("params")})

    out += ["", "/ {", "    input_processors {",
            "        zip_click_to_right_click_mapper: zip_click_to_right_click_mapper {",
            '            compatible = "zmk,input-processor-code-mapper";',
            "            #input-processor-cells = <0>;",
            "            type = <INPUT_EV_KEY>;",
            "            map = <INPUT_BTN_0 INPUT_BTN_1>;",
            "        };", "    };", "",
            "    // Standard MoErgo behaviors (generated; the Layout Editor provides these itself)",
            "    behaviors {",
            "        // Magic key: hold for the Magic layer, tap to show status on the RGB LEDs",
            "        magic: magic {",
            '            compatible = "zmk,behavior-hold-tap";',
            "            #binding-cells = <2>;",
            '            flavor = "tap-preferred";',
            "            tapping-term-ms = <200>;",
            "            bindings = <&mo>, <&rgb_ug_status_macro>;",
            "        };"]
    for n in used_td:
        nm = ident(names[n])
        out += ["",
                f"        // &td_LAYER_{nm}: hold for the {names[n]} layer, double-tap to lock it on",
                f"        td_LAYER_{nm}: td_LAYER_{nm} {{",
                '            compatible = "zmk,behavior-tap-dance";',
                "            #binding-cells = <0>;",
                "            tapping-term-ms = <200>;",
                f"            bindings = <&mo LAYER_{nm}>, <&to LAYER_{nm}>;",
                "        };"]
    for k in range(4):
        out += ["",
                f"        // &bt_{k}: tap to use Bluetooth profile {k}, double-tap to disconnect it",
                f"        bt_{k}: bt_{k} {{",
                '            compatible = "zmk,behavior-tap-dance";',
                "            #binding-cells = <0>;",
                "            tapping-term-ms = <200>;",
                f"            bindings = <&bt_select_{k}>, <&bt BT_DISC {k}>;",
                "        };"]
    out += ["    };", "", "    macros {",
            "        rgb_ug_status_macro: rgb_ug_status_macro {",
            '            compatible = "zmk,behavior-macro";',
            "            #binding-cells = <0>;",
            "            bindings = <&rgb_ug RGB_STATUS>;",
            "        };"]
    for k in range(4):
        out += ["",
                f"        bt_select_{k}: bt_select_{k} {{",
                '            compatible = "zmk,behavior-macro";',
                "            #binding-cells = <0>;",
                f"            bindings = <&out OUT_BLE>, <&bt BT_SEL {k}>;",
                "        };"]
    out += ["    };", "};", "",
            CUSTOM_BEHAVIORS_BEGIN,
            (data.get("custom_defined_behaviors") or "").strip("\n"),
            CUSTOM_BEHAVIORS_END, "",
            "/ {", "    keymap {", '        compatible = "zmk,keymap";']

    cells = [[binding_text(b, names) for b in layer] for layer in layers]
    legends = _legends(data) or [[""] * 60 for _ in layers]
    for n, layer in enumerate(layers):
        widths = [max(max(len(cells[n][i]), len(legends[n][i])) for i in range(60) if GRID[i] == col)
                  for col in range(12)]
        out += ["",
                f"        layer_{ident(names[n])} {{",
                f'            display-name = "{names[n]}";',
                "            bindings = <",
                "            /*    left  C6 C5 C4 C3 C2 C1  |  right C1 C2 C3 C4 C5 C6  (thumbs: left T1 T2 T3 | right T3 T2 T1) */"]
        out += _grid_lines(cells[n], legends[n], widths)
        out += ["            >;", "        };"]
    out += ["    };", "};", "", "// Trackpad settings (Layout Editor: input listeners)"]
    for listener in data.get("inputListeners") or []:
        out += [_listener_text(listener), ""]
    out += [CUSTOM_DT_BEGIN, (data.get("custom_devicetree") or "").strip("\n"), CUSTOM_DT_END, ""]
    return "\n".join(line for line in out)


# -------------------------------------------------------- keymap -> JSON ---

def _between(text, begin, end):
    a = text.find(begin)
    b = text.find(end, a + len(begin)) if a >= 0 else -1
    if a < 0 or b < 0:
        return "", text
    inner = text[a + len(begin):b].strip("\n")
    return inner, text[:a] + text[b + len(end):]


def _strip_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def _block(text, start):
    """Return the contents of the {...} block whose '{' is at or after `start`, and the end index."""
    i = text.index("{", start)
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j + 1
    raise KeymapError("unbalanced braces")


def _parse_param(tok):
    """'LS(LC(V))' -> {'value': 'LS', 'params': [{'value': 'LC', 'params': [{'value': 'V'}]}]}"""
    tok = tok.strip()
    m = re.fullmatch(r"(\w+)\((.*)\)", tok)
    if not m:
        return {"value": tok}
    inner, depth, parts, cur = m.group(2), 0, [], ""
    for ch in inner:
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
            continue
        depth += ch == "("
        depth -= ch == ")"
        cur += ch
    parts.append(cur)
    return {"value": m.group(1), "params": [_parse_param(p) for p in parts if p.strip()]}


def _tokens(bindings):
    """Split a bindings list into [[behavior, param, ...], ...]. Parentheses may contain spaces."""
    toks, cur, depth = [], "", 0
    for ch in bindings:
        if ch.isspace() and depth == 0:
            if cur:
                toks.append(cur)
                cur = ""
            continue
        depth += ch == "("
        depth -= ch == ")"
        cur += ch
    if cur:
        toks.append(cur)
    out = []
    for t in toks:
        if t.startswith("&"):
            out.append([t])
        elif not out:
            raise KeymapError(f"'{t}' before the first behavior")
        else:
            out[-1].append(t)
    return out


def _parse_processors(s):
    procs = []
    for m in re.finditer(r"<\s*(&\w+)([^>]*)>", s):
        params = []
        for tok in re.findall(r"\([^)]*\)|\S+", m.group(2)):
            if re.fullmatch(r"-?\d+", tok):
                params.append(int(tok))
            else:
                params.append([f.strip() for f in tok.strip("()").split("|")])
        procs.append({"code": m.group(1), "params": params})
    return procs


def parse_keymap(text):
    """Parse a keymap into a dict with layer_names, layers (editor JSON bindings),
    inputListeners, custom_defined_behaviors, custom_devicetree."""
    custom_beh, text = _between(text, CUSTOM_BEHAVIORS_BEGIN, CUSTOM_BEHAVIORS_END)
    custom_dt, text = _between(text, CUSTOM_DT_BEGIN, CUSTOM_DT_END)
    clean = _strip_comments(text)

    defines = {m.group(1): int(m.group(2)) for m in re.finditer(r"#define\s+(LAYER_\w+)\s+(\d+)", clean)}

    # Tap-dances of the form <&mo L>, <&to L> are the editor's "&layer L".
    layer_td = {}
    for m in re.finditer(r"(\w+)\s*:\s*[\w-]+\s*\{", clean):
        body, _ = _block(clean, m.end() - 1)
        if "zmk,behavior-tap-dance" in body:
            b = re.search(r"bindings\s*=\s*<\s*&mo\s+(\w+)\s*>\s*,\s*<\s*&to\s+(\w+)\s*>", body)
            if b and b.group(1) == b.group(2):
                layer_td[m.group(1)] = b.group(1)

    km = re.search(r"\bkeymap\s*\{", clean)
    if not km:
        raise KeymapError("no 'keymap { ... }' node found")
    body, _ = _block(clean, km.end() - 1)
    names, raw_layers, pos = [], [], 0
    for m in re.finditer(r"([\w-]+)\s*\{", body):
        if m.start() < pos:
            continue
        node, pos = _block(body, m.end() - 1)
        dn = re.search(r'display-name\s*=\s*"([^"]*)"', node)
        bd = re.search(r"bindings\s*=\s*<(.*?)>\s*;", node, flags=re.S)
        if not bd:
            continue
        names.append(dn.group(1) if dn else re.sub(r"^layer_", "", m.group(1)))
        raw_layers.append(_tokens(bd.group(1)))

    index_of = {f"LAYER_{ident(n)}": i for i, n in enumerate(names)}
    index_of.update(defines)

    def layer_number(tok):
        if tok in index_of:
            return index_of[tok]
        if re.fullmatch(r"\d+", tok):
            return int(tok)
        raise KeymapError(f"unknown layer '{tok}'")

    layers = []
    for n, raw in enumerate(raw_layers):
        if len(raw) != 60:
            raise KeymapError(f"layer {names[n]} has {len(raw)} bindings, expected 60")
        layer = []
        for toks in raw:
            v, ps = toks[0], toks[1:]
            if v[1:] in layer_td and not ps:
                b = {"value": "&layer", "params": [{"value": layer_number(layer_td[v[1:]])}]}
            elif v == "&magic":
                b = {"value": "&magic"}
            elif v == "&sys_reset":
                b = {"value": "&reset"}
            else:
                b = {"value": v}
                params = []
                for k, p in enumerate(ps):
                    if k == 0 and (v in LAYER_PARAM_BEHAVIORS):
                        num = layer_number(p)
                        params.append({"value": num if v in NUMBER_LAYER_BEHAVIORS else str(num)})
                    else:
                        params.append(_parse_param(p))
                if params:
                    b["params"] = params
            layer.append(b)
        layers.append(layer)

    listeners = []
    for m in re.finditer(r"(&\w+_listener)\s*\{", clean):
        lbody, _ = _block(clean, m.end() - 1)
        top = re.sub(r"[\w-]+\s*\{.*?\}\s*;", "", lbody, flags=re.S)
        lst = {"code": m.group(1),
               "inputProcessors": _parse_processors(re.search(r"input-processors\s*=\s*([^;]*);", top).group(1))
               if "input-processors" in top else [],
               "nodes": []}
        for nm in re.finditer(r"([\w-]+)\s*\{(.*?)\}\s*;", lbody, flags=re.S):
            nb = nm.group(2)
            lay = re.search(r"layers\s*=\s*<([^>]*)>", nb)
            ip = re.search(r"input-processors\s*=\s*([^;]*);", nb)
            lst["nodes"].append({"code": nm.group(1),
                                 "layers": [int(x) for x in lay.group(1).split()] if lay else [],
                                 "inputProcessors": _parse_processors(ip.group(1)) if ip else []})
        listeners.append(lst)

    return {"layer_names": names, "layers": layers, "inputListeners": listeners,
            "custom_defined_behaviors": custom_beh, "custom_devicetree": custom_dt}


# ------------------------------------------------------------ comparison ---

def normalize(b):
    """Binding with values as strings and empty params dropped, for comparing meaning."""
    out = {"value": str(b.get("value"))}
    ps = [normalize(p) for p in b.get("params") or []]
    if ps:
        out["params"] = ps
    return out


def same(a, b):
    return normalize(a) == normalize(b)


def to_json(text, base):
    """Keymap text -> editor JSON, starting from `base` (the previous layout JSON)."""
    parsed = parse_keymap(text)
    data = copy.deepcopy(base)
    old_layers = base.get("layers") or []
    new_layers = []
    for n, layer in enumerate(parsed["layers"]):
        old = old_layers[n] if n < len(old_layers) else []
        new_layers.append([old[i] if i < len(old) and same(old[i], b) else b for i, b in enumerate(layer)])
    changed = (new_layers != old_layers or parsed["layer_names"] != base.get("layer_names")
               or parsed["inputListeners"] != base.get("inputListeners")
               or parsed["custom_defined_behaviors"] != (base.get("custom_defined_behaviors") or "")
               or parsed["custom_devicetree"] != (base.get("custom_devicetree") or ""))
    data["layer_names"] = parsed["layer_names"]
    data["layers"] = new_layers
    data["inputListeners"] = parsed["inputListeners"]
    data["custom_defined_behaviors"] = parsed["custom_defined_behaviors"]
    data["custom_devicetree"] = parsed["custom_devicetree"]
    if changed:
        data["date"] = int(time.time())
    return data, changed


def dumps(data):
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"
