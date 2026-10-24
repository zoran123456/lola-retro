#!/usr/bin/env python3
"""Convert the Lola Retro slang passes to GLSL for emulators with RetroArch-style .glslp presets.

Three targets:
- Amiberry (Amiga 1084S): amiberry/lola-retro
- 86Box (PC monitor, VGA): 86box/lola-retro
- Kodi (every preset): kodi/lola-retro, described at the end of this text
Every preset also comes in a flat version, as in RetroArch's flat folder (NAME-flat.glslp for
Amiberry and 86Box, curved/ and flat/ folders for Kodi).

Amiberry and 86Box run the passes on OpenGL core profiles (Amiberry 3.3, 86Box 3.2 or newer).
The conversion:
- inlines the includes and turns each pass into one file with a VERTEX and a FRAGMENT part;
- replaces the Vulkan uniform blocks with the plain uniforms the emulator sets;
- builds in the preset's values: the ones worth adjusting stay parameters, the rest become
  constants, so the compiler drops the code they switch off (composite, RF, the TV beam model).

The two emulators differ from RetroArch, and from each other:

Amiberry - every pass's output is sized exactly, and passes are found by their alias.
  It lists the parameters of every pass in its menu, so each parameter is declared once, in the
  first pass, which writes the values into a spare channel of its output (blue, first row);
  the later passes read them from there. It draws every Amiga line twice (LR_FIELDS).
  Rows run bottom-up, as everywhere in OpenGL; that only mirrors the mask pattern and the small
  vertical misconvergence, which does not show.

86Box - the older RetroArch GLSL rules: every texture is rounded up to a power of two with the
  picture in its lower left corner, TexCoord only spans the picture, passes are found by number
  (Pass2Texture), OutputSize is the window for every pass, and the passes have no alpha channel
  (LR_PACKED_SPOT). The conversion rescales every texture read to the picture inside its texture,
  with the same filter and edge behaviour as in RetroArch, and works out each pass's own output
  size. The first pass gets no Orig* values from 86Box; its Source is the frame anyway.
  The frame is read upside down and the last pass turns the picture back, so every pass works
  with the top line first, exactly as in RetroArch. 86Box keeps only "#version" and its number
  of the version line and skips a parameter whose description is longer than 63 characters.

Neither has feedback textures (LR_NO_FEEDBACK, no afterglow), and neither keeps the picture
area 4:3 (LR_FIT_43). The options are described in crt.inc.

Kodi runs RetroArch's own presets: its textures are the exact size of each picture, rows count
from the top, wrap modes and filters mean what they mean in RetroArch, and every pass gets every
parameter of the preset by name. So the Kodi version keeps RetroArch's pass chains (with the
native pass) and every parameter, shares its passes between all the presets, and only renames the
textures: the previous pass is Texture, the frame OrigTexture and an aliased pass <alias>Texture
(Texture again when it is the previous pass). It has no feedback textures either (LR_NO_FEEDBACK).
Kodi turns the version line into OpenGL ES's on GLES devices, so the passes set default precisions.

Usage: python3 tools/make_glsl.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLANG = ROOT / "shaders" / "lola-retro" / "shaders"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_presets import BASE, FLAT, PASSES, PRESET_PASSES, PRESETS, fmt, with_native_pass  # noqa: E402

# The parameters left adjustable, in the order the emulator's list shows them.
# Everything else is fixed at the preset's value.
AMIGA_PARAMS = [
    "LR_NORM", "LR_DBLEND", "LR_SAT", "LR_BRIGHT", "LR_CONTRAST", "LR_STEADY",
    "LR_GAMMA", "LR_CONV", "LR_SMOOTH",
    "LR_MASK_TYPE", "LR_MASK_STR", "LR_MASK_PX", "LR_WHITE", "LR_PHOS",
    "LR_CURV_X", "LR_CURV_Y", "LR_BEND", "LR_CORNER", "LR_GLOW", "LR_GLOW_SIZE", "LR_VIGNETTE", "LR_OVERSCAN", "LR_OVERSCAN_V", "LR_LIN_X", "LR_LIN_Y", "LR_REFLECT",
    "LR_MON_SIZE", "LR_MON_PITCH", "LR_MON_SPOT_LO", "LR_MON_SPOT_HI", "LR_MON_CORNER",
    "LR_SCREEN_H", "LR_SCREEN_UNIT", "LR_BACKDROP", "LR_ROOM", "LR_SPILL", "LR_SCENE_SPEED",
]
PC_PARAMS = [
    "LR_DBLEND", "LR_SAT", "LR_BRIGHT", "LR_CONTRAST",
    "LR_GAMMA", "LR_CONV", "LR_SMOOTH",
    "LR_MASK_TYPE", "LR_MASK_STR", "LR_MASK_PX", "LR_WHITE", "LR_PHOS",
    "LR_CURV_X", "LR_CURV_Y", "LR_BEND", "LR_CORNER", "LR_GLOW", "LR_GLOW_SIZE", "LR_VIGNETTE", "LR_OVERSCAN", "LR_OVERSCAN_V", "LR_LIN_X", "LR_LIN_Y", "LR_REFLECT",
    "LR_MON_SIZE", "LR_MON_PITCH", "LR_MON_SPOT_LO", "LR_MON_SPOT_HI", "LR_MON_CORNER",
    "LR_SCREEN_H", "LR_SCREEN_UNIT", "LR_BACKDROP", "LR_ROOM", "LR_SPILL", "LR_SCENE_SPEED",
]


def retroarch_chain(passes=PASSES):
    """A RetroArch pass chain (make_presets.PASSES unless given). filter and wrap have RetroArch's
    meaning: how the pass samples its Source (a pass's output is read by later passes with the
    filter and wrap of the pass after it)."""
    kv = dict(re.findall(r"^(\w+) = (.+)$", passes, flags=re.M))
    chain = []
    for i in range(int(kv["shaders"])):
        p = dict(src=Path(kv[f"shader{i}"]).stem, alias=kv.get(f"alias{i}", ""),
                 filter=kv.get(f"filter_linear{i}") == "true", wrap=kv.get(f"wrap_mode{i}", "clamp_to_border"),
                 float=kv.get(f"float_framebuffer{i}") == "true")
        for ax in "xy":
            st = kv.get(f"scale_type_{ax}{i}", kv.get(f"scale_type{i}"))
            sc = kv.get(f"scale_{ax}{i}", kv.get(f"scale{i}"))
            p["s" + ax] = (st, float(sc)) if st else None
        chain.append(p)
    return chain


CHAIN = retroarch_chain()
NAMES = [p["src"] for p in CHAIN]
assert NAMES == ["encode", "decode", "glow-h", "glow-v", "beam", "crt", "present"], NAMES
CRT = dict(CHAIN[5], alias="")                    # no feedback, so no alias needed
FIELDS = [dict(src="fields", alias="", filter=True, wrap="clamp_to_edge",     # linear: it is LR_Beam's reader
               sx=("absolute", 1.0), sy=("source", 0.5), float=True),
          dict(src="fields", alias="LR_Fields", filter=False, wrap="clamp_to_edge",
               sx=("absolute", 1.0), sy=("absolute", 1.0), float=True)]

TARGETS = {
    "amiberry": dict(
        api="amiberry",
        preset="amiga-1084s",
        out=ROOT / "amiberry" / "lola-retro",
        title="Commodore 1084S",
        emulator="Amiberry",
        defines=["LR_FIELDS", "LR_NO_FEEDBACK", "LR_FIT_43", "LR_ROWS_UP"],
        params=AMIGA_PARAMS,
        fixed=dict(LR_CONSOLE=6),     # Amiberry only shows Amiga modes
        passes=CHAIN[:5] + FIELDS + [CRT, CHAIN[6]],
    ),
    "86box": dict(
        api="86box",
        preset="pc-monitor-vga",
        out=ROOT / "86box" / "lola-retro",
        title="PC monitor (VGA)",
        emulator="86Box",
        defines=["LR_NO_FEEDBACK", "LR_FIT_43", "LR_PACKED_SPOT"],
        params=PC_PARAMS,
        fixed={},
        # the last pass has no scale, so 86Box lets it draw straight into the window
        passes=CHAIN[:5] + [CRT, dict(CHAIN[6], sx=None, sy=None)],
        # more presets on the same shader files: they only set other parameter values
        variants={"pc-monitor-vga-good": "PC monitor (VGA), good 15-inch",
                  "pc-monitor-vga-premium": "PC monitor (VGA), premium 15-inch",
                  "pc-monitor-vga-premium-plus": "PC monitor (VGA), premium+ 15-inch",
                  "pc-monitor-vga-extreme": "PC monitor (VGA), extreme (sharper than a real tube)"},
    ),
}

# The ports only run RGB: the encode pass then writes nothing, which the Amiberry port relies on
# (it passes its parameters on in the blue channel of that pass, where composite and S-Video
# keep a frame of No flicker's subcarrier cycle).
for _t in TARGETS.values():
    _cable = _t["fixed"].get("LR_CABLE", PRESETS[_t["preset"]].get("LR_CABLE", BASE["LR_CABLE"]))
    assert _cable > 2.5 and "LR_CABLE" not in _t["params"], _t["preset"]

# Kodi runs every preset of the RetroArch version, on the same pass chains (make_presets.py), so its
# passes are shared by all of them and every parameter stays adjustable: a preset only sets values,
# as in RetroArch. Kodi has no feedback textures (no afterglow), and it keeps the picture area to the
# game's shape itself.
KODI = dict(api="kodi", out=ROOT / "kodi" / "lola-retro", title="every preset", emulator="Kodi",
            defines=["LR_NO_FEEDBACK"], fixed={})

TYPES = r"(?:void|bool|int|uint|float|vec2|vec3|vec4|ivec2|mat3|mat4|Timing)"


def expand(path, seen=None):
    """The file with its #include lines replaced by the included files."""
    seen = seen or {path.resolve()}
    out = []
    for line in path.read_text().splitlines():
        m = re.match(r'\s*#include\s+"(.+)"', line)
        if m:
            inc = (path.parent / m.group(1)).resolve()
            if inc in seen:
                raise SystemExit(f"include loop: {inc}")
            out += expand(inc, seen | {inc})
        else:
            out.append(line)
    return out


def resolve_ifdefs(lines, defines):
    """Keep only the #ifdef / #ifndef / #else branches that apply to these defines."""
    out, stack = [], []          # stack of (this branch active, any branch taken)
    for line in lines:
        m = re.match(r"\s*#(ifdef|ifndef|else|endif)\b\s*(\w*)", line)
        if not m:
            if all(a for a, _ in stack):
                out.append(line)
            continue
        kind, name = m.groups()
        if kind in ("ifdef", "ifndef"):
            on = (name in defines) == (kind == "ifdef")
            stack.append((on, on))
        elif kind == "else":
            _, taken = stack.pop()
            stack.append((not taken, True))
        else:
            stack.pop()
    assert not stack, "unbalanced #ifdef"
    return out


def parameter_table():
    """name -> (description, default, min, max, step) from the #pragma parameter lines."""
    table = {}
    for line in (SLANG / "common.inc").read_text().splitlines():
        m = re.match(r'\s*#pragma\s+parameter\s+(\w+)\s+"([^"]*)"\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)
        if m:
            table[m.group(1)] = (m.group(2), *map(float, m.group(3, 4, 5, 6)))
    return table


def functions(code):
    """name -> body of every function defined in code (brace matched)."""
    found = {}
    for m in re.finditer(r"\b" + TYPES + r"\s+(\w+)\s*\(([^;{}()]|\([^()]*\))*\)\s*\{", code):
        depth, i = 1, m.end()
        while depth:
            depth += {"{": 1, "}": -1}.get(code[i], 0)
            i += 1
        found.setdefault(m.group(1), "")
        found[m.group(1)] += code[m.start():i]
    return found


def used_parameters(common, stages, names):
    """The parameters the code reachable from main() reads, in the order of names."""
    used = set()
    for stage in stages:
        funcs = functions(common + "\n" + stage)
        todo, seen = ["lr_main"], set()
        while todo:
            f = todo.pop()
            if f in seen or f not in funcs:
                continue
            seen.add(f)
            body = funcs[f]
            used |= set(re.findall(r"\b(LR_\w+)\b", body))
            todo += re.findall(r"\b(\w+)\s*\(", body)
        # constants and globals outside functions
        outside = common + "\n" + stage
        for body in funcs.values():
            outside = outside.replace(body, "")
        used |= set(re.findall(r"\b(LR_\w+)\b", outside))
    return [n for n in names if n in used]


def size_expr(scale, axis):
    """86Box: this pass's output size along one axis, as GLSL (86Box only passes the window)."""
    if scale is None:
        return f"floor(InputSize.{axis})"
    kind, k = scale
    if kind == "viewport":
        return f"floor(OutputSize.{axis} * {k!r})"
    if kind == "absolute":
        return f"{k!r}"
    return f"floor(InputSize.{axis} * {k!r})"


def box_samplers(stage, passes, index):
    """86Box: rename the samplers of one stage to the names 86Box binds, and read every texture
    through a helper that finds the picture inside its power-of-two texture and repeats
    RetroArch's filter and edge behaviour. Returns the new stage code.

    86Box's own filter setting (View > Filter method), not the preset, decides how the frame
    (the first pass's Source, Original) and the last pass's Source are filtered. Lola Retro reads
    those without filtering, so the helpers for them fetch whole texels and the setting does not
    matter. The other textures get the preset's filter, which is the one RetroArch would use.

    OpenGL counts rows from the bottom, RetroArch's shaders from the top. The frame is read upside
    down, so every pass's output has the top line in row 0 as in RetroArch, and the last pass
    turns the picture the right way up (see convert). Every pass then works exactly as there."""
    declared = re.findall(r"^\s*uniform\s+sampler2D\s+(\w+)\s*;.*$", stage, flags=re.M)
    helpers, decls, seen = [], [], set()
    for name in declared:
        frame = name == "Original" or (name == "Source" and index == 0)
        if name == "Source" or (name == "Original" and index == 0):
            # the first pass's Source is the frame itself; 86Box gives that pass no Orig* values
            tex, size, tsize = "Texture", "LR_SourceSize.xy", "TextureSize"
            linear, wrap = passes[index]["filter"], passes[index]["wrap"]
            ours = index not in (0, len(passes) - 1)
        elif name == "Original":
            tex, size, tsize = "OrigTexture", "OrigInputSize", "OrigTextureSize"
            linear, wrap, ours = passes[0]["filter"], passes[0]["wrap"], False
        else:
            j = next(k for k, p in enumerate(passes) if p["alias"] == name)
            assert j < index, f"{name} is read before it is drawn"
            linear, wrap = passes[j + 1]["filter"], passes[j + 1]["wrap"]
            ours = not (j == index - 1 and index == len(passes) - 1)
            if j == index - 1:
                tex, size, tsize = "Texture", "LR_SourceSize.xy", "TextureSize"
            else:
                # 86Box's PassNInputSize is the input of pass N - 1, so pass j's picture is Pass(j+2)InputSize
                tex, size, tsize = f"Pass{j + 1}Texture", f"floor(Pass{j + 2}InputSize)", f"Pass{j + 2}TextureSize"
                if tex not in seen:
                    decls.append(f"uniform vec2 Pass{j + 2}InputSize, Pass{j + 2}TextureSize;")
        assert ours or not linear, f"pass {index} reads {name} filtered, but 86Box decides that filter"
        if tex not in seen:
            decls.append(f"uniform sampler2D {tex};")
            seen.add(tex)
        stage = re.sub(r"^\s*uniform\s+sampler2D\s+" + name + r"\s*;.*$\n?", "", stage, flags=re.M)
        stage = re.sub(r"\btextureLod\(\s*" + name + r"\s*,", f"lr_tex_{name}(", stage)
        stage = re.sub(r"\btexelFetch\(\s*" + name + r"\s*,", f"lr_fetch_{name}(" if frame else f"texelFetch({tex},", stage)
        # the picture's size, not the texture's
        stage = re.sub(r"\btextureSize\(\s*" + name + r"\s*,\s*0\s*\)", f"ivec2({size})", stage)
        assert not re.search(r"\b(texture|textureSize)\(\s*" + name + r"\b", stage), f"{name}: unhandled read"
        if linear:
            body = ["    uv.y = 1.0 - uv.y;                          // the frame: top line first"] if frame else []
            if wrap == "clamp_to_edge":
                body.append("    uv = clamp(uv, 0.5 / n, 1.0 - 0.5 / n);")
            # (clamp_to_border: outside the picture the texture is cleared to black)
            body.append(f"    return textureLod({tex}, uv * n / {tsize}, lod);")
        else:
            if wrap == "clamp_to_edge":
                body = ["    ivec2 t = ivec2(clamp(floor(uv * n), vec2(0.0), n - 1.0));"]
            else:
                body = ["    if (any(lessThan(uv, vec2(0.0))) || any(greaterThanEqual(uv, vec2(1.0)))) return vec4(0.0);",
                        "    ivec2 t = ivec2(floor(uv * n));"]
            if frame:
                body.append("    t.y = int(n.y) - 1 - t.y;                   // the frame: top line first")
            body.append(f"    return texelFetch({tex}, t, 0);")
        helpers += [f"vec4 lr_tex_{name}(vec2 uv, float lod)   // {'linear' if linear else 'nearest'}, {wrap}",
                    "{",
                    f"    vec2 n = {size};",
                    *body,
                    "}",
                    ""]
        if frame:
            helpers += [f"vec4 lr_fetch_{name}(ivec2 p, int lod)",
                        "{",
                        f"    p.y = int({size}.y) - 1 - p.y;              // the frame: top line first",
                        f"    return texelFetch({tex}, p, lod);",
                        "}",
                        ""]
    if not declared:
        return stage
    code = re.sub(r"//.*", "", stage)
    left = [n for n in declared if re.search(r"(?<!lr_tex_)(?<!lr_fetch_)\b" + n + r"\b", code)]
    assert not left, f"pass {index}: {left} still used directly"
    block = "\n".join(["// Textures as 86Box binds them. The picture sits in the lower left corner of a power-of-two",
                       "// texture (n texels of it), so every read goes through a helper."]
                      + decls + [""] + helpers)
    # after the stage's last input/output declaration, before its first function
    first_fn = re.search(r"^\s*" + TYPES + r"\s+\w+\s*\([^;]*$", stage, flags=re.M)
    cut = first_fn.start() if first_fn else 0
    return stage[:cut] + "\n" + block + stage[cut:]


def kodi_samplers(stage, passes, index):
    """Kodi: rename the samplers of one stage to the names Kodi binds. Kodi calls the previous pass's
    output Texture and the frame OrigTexture. An aliased pass's output is <alias>Texture, but only for
    passes before the previous one, so a pass that reads the previous pass by its alias reads Texture.
    Kodi's textures are the exact size of each picture and its wrap modes and filters mean what they
    mean in RetroArch, so the reads themselves stay as they are."""
    for name in re.findall(r"^\s*uniform\s+sampler2D\s+(\w+)\s*;", stage, flags=re.M):
        if name == "Source":
            new = "Texture"
        elif name == "Original":
            new = "OrigTexture"
        else:
            j = next(k for k, p in enumerate(passes) if p["alias"] == name)
            assert j < index, f"{name} is read before it is drawn"
            new = "Texture" if j == index - 1 else f"{name}Texture"
        stage = re.sub(r"\b" + name + r"\b", new, stage)
    declared = re.findall(r"^\s*uniform\s+sampler2D\s+(\w+)\s*;", stage, flags=re.M)
    assert len(declared) == len(set(declared)), f"pass {index} reads one texture by two names"
    return stage


def convert(index, target, values, table):
    """GLSL source of pass number index."""
    passes, api = target["passes"], target["api"]
    src_name = passes[index]["src"]
    owner = index == 0
    path = SLANG / f"{src_name}.slang"
    lines = [l for l in resolve_ifdefs(expand(path), set(target["defines"]))
             if not l.strip().startswith("#version")
             and not re.match(r"\s*#pragma\s+(parameter|name|format)\b", l)]
    text = "\n".join(lines)

    # uniform blocks: the push constants and the UBO become plain uniforms
    text, n1 = re.subn(r"layout\(push_constant\)\s*uniform\s+Push\s*\{.*?\}\s*params\s*;\n?", "", text, flags=re.S)
    text, n2 = re.subn(r"layout\([^)]*\)\s*uniform\s+UBO\s*\{.*?\}\s*global\s*;\n?", "", text, flags=re.S)
    assert n1 == 1 and n2 == 1, f"{src_name}: uniform blocks not found"
    text = text.replace("global.MVP", "MVPMatrix")
    text = re.sub(r"\bglobal\.(LR_\w+)", r"\1", text)
    text = re.sub(r"\bparams\.(SourceSize|OriginalSize|OutputSize|FrameCount)\b", r"LR_\1", text)
    assert "global." not in text and "params." not in text, src_name
    # GLSL 3.30 has no layout locations on varyings and no descriptor sets
    text = re.sub(r"layout\(\s*location\s*=\s*\d+\s*\)\s*", "", text)
    text = re.sub(r"layout\(\s*set\s*=\s*\d+\s*,\s*binding\s*=\s*\d+\s*\)\s*", "", text)
    assert "layout(" not in text, src_name

    parts = re.split(r"^\s*#pragma\s+stage\s+(\w+)\s*$", text, flags=re.M)
    common, stages = parts[0], dict(zip(parts[1::2], parts[2::2]))
    vs, fs = stages["vertex"], stages["fragment"]
    vs = re.sub(r"\bPosition\b", "VertexCoord", vs)
    # each stage's main() becomes lr_main(); the generated main() around it handles the parameters
    vs, n_vs = re.subn(r"\bvoid\s+main\s*\(\s*\)", "void lr_main()", vs)
    fs, n_fs = re.subn(r"\bvoid\s+main\s*\(\s*\)", "void lr_main()", fs)
    assert n_vs == 1 and n_fs == 1, src_name
    if api == "86box":
        # TexCoord only spans the picture inside the power-of-two texture: make it 0..1 again
        # (the last pass turns the picture the right way up: its rows count from the top, as in
        # RetroArch, while the window's count from the bottom; see box_samplers)
        last = index == len(passes) - 1
        vs, n = re.subn(r"=\s*TexCoord\s*;", "= TexCoord * TextureSize / InputSize" + (
            " * vec2(1.0, -1.0) + vec2(0.0, 1.0);   // top row first" if last else ";"), vs)
        assert n == 1, src_name
        vs = box_samplers(vs, passes, index)
        fs = box_samplers(fs, passes, index)
    elif api == "kodi":
        vs = kodi_samplers(vs, passes, index)
        fs = kodi_samplers(fs, passes, index)

    adjustable = target["params"]
    named = set(re.findall(r"\b(LR_[A-Z_]+)\b", text))
    fixed = sorted(n for n in named if n in table and n not in adjustable)
    declared = [n for n in adjustable if n in named]
    relay = used_parameters(common, [vs, fs], adjustable) if api == "amiberry" and not owner else []

    # Amiberry runs OpenGL 3.3 core. 86Box asks for OpenGL 3.2 (GLSL 1.50) and keeps only "#version"
    # plus one word of this line, so no profile word (150 means core anyway). Kodi turns the version
    # into an OpenGL ES one on GLES (330 is 3.10 es), which needs default precisions; older Kodi keeps
    # a profile word there and the pass fails to compile, so Kodi's has none.
    version = {"amiberry": ["#version 330 core"], "86box": ["#version 150"],
               "kodi": ["#version 330", "#ifdef GL_ES", "precision highp float;", "precision highp int;",
                        "precision highp sampler2D;", "#endif"]}[api]
    out = version + [f"// Lola Retro - {src_name} pass for {target['emulator']} ({target['title']}).",
                     f"// Generated by tools/make_glsl.py from shaders/lola-retro/shaders/{src_name}.slang. Do not edit.",
                     ""]
    out += [f"#define {d}" for d in target["defines"]]
    out.append("")
    if owner:
        out.append("// Adjustable values" + (". They are set here only; this pass hands them to the others."
                                             if api == "amiberry" else " (every pass reads them by name)."))
        for n in adjustable:
            desc, _, lo, hi, step = table[n]
            assert api != "86box" or 0 < len(desc) <= 63, f"86Box would skip {n}: description over 63 characters"
            out.append(f'#pragma parameter {n} "{desc}" {fmt(values[n])} {fmt(lo)} {fmt(hi)} {fmt(step)}')
        out.append("")
    if api in ("amiberry", "kodi"):
        out += ["uniform vec2 TextureSize;       // Source: the previous pass (the frame for the first pass)",
                "uniform vec2 OrigTextureSize;   // Original: the emulator's frame",
                "uniform vec2 OutputSize;        // this pass",
                "uniform int FrameCount;",
                "#define LR_SourceSize vec4(TextureSize, 1.0 / TextureSize)",
                "#define LR_OriginalSize vec4(OrigTextureSize, 1.0 / OrigTextureSize)",
                "#define LR_OutputSize vec4(OutputSize, 1.0 / OutputSize)",
                "#define LR_FrameCount uint(FrameCount)",
                ""]
    else:
        p = passes[index]
        ox, oy = size_expr(p["sx"], "x"), size_expr(p["sy"], "y")
        out += ["uniform vec2 InputSize;         // the previous pass's picture (the frame for the first pass)",
                "uniform vec2 TextureSize;       // its texture, rounded up to a power of two"]
        if owner:
            out += ["uniform vec2 OutputSize;        // the picture area in the window (86Box sends it to every pass)",
                    "uniform int FrameCount;",
                    "#define LR_SourceSize vec4(floor(InputSize), 1.0 / floor(InputSize))",
                    "#define LR_OriginalSize LR_SourceSize   // the frame (86Box gives the first pass no Orig* values)"]
        else:
            out += ["uniform vec2 OrigInputSize;     // the emulator's frame",
                    "uniform vec2 OrigTextureSize;",
                    "uniform vec2 OutputSize;        // the picture area in the window (86Box sends it to every pass)",
                    "uniform int FrameCount;",
                    "#define LR_SourceSize vec4(floor(InputSize), 1.0 / floor(InputSize))",
                    "#define LR_OriginalSize vec4(OrigInputSize, 1.0 / OrigInputSize)"]
        out += [f"#define LR_OutputSize vec4({ox}, {oy}, 1.0 / ({ox}), 1.0 / ({oy}))   // this pass",
                "#define LR_FrameCount uint(FrameCount)",
                ""]
    if fixed:
        out.append("// fixed by the preset")
        out += [f"const float {n} = {float(values[n])!r};" for n in fixed]
        out.append("")
    if owner or api in ("86box", "kodi"):
        names = adjustable if owner else declared
        out += [f"uniform float {n};" for n in names]
        if names:
            out.append("")
    elif declared:
        out.append("// adjustable values, read from the first pass's output in main()")
        if relay:
            out.append(f"uniform sampler2D {passes[0]['alias']};")
        out += [f"float {n};" for n in declared]
        out.append("")
    out.append(common.strip("\n"))
    out += ["", "#if defined(VERTEX)", "uniform mat4 MVPMatrix;"]
    out.append(vs.strip("\n"))
    out.append("")
    nv = (len(relay) + 3) // 4
    if relay:
        out.append(f"flat out vec4 lrParams[{nv}];")
        out.append("")
        out.append("void main()")
        out.append("{")
        out.append("    // the adjustable values: blue channel of the first pass's first row")
        for n in relay:
            out.append(f"    {n} = texelFetch({passes[0]['alias']}, ivec2({adjustable.index(n)}, 0), 0).b;")
        for i in range(nv):
            group = relay[4 * i: 4 * i + 4] + ["0.0"] * (4 - len(relay[4 * i: 4 * i + 4]))
            out.append(f"    lrParams[{i}] = vec4({', '.join(group)});")
        out.append("    lr_main();")
        out.append("}")
    else:
        out += ["void main()", "{", "    lr_main();", "}"]
    out += ["", "#elif defined(FRAGMENT)"]
    out.append(fs.strip("\n"))
    out.append("")
    if owner and api == "amiberry":
        k = len(adjustable)
        out += ["// The adjustable values go to the later passes: texel k of the first row, blue channel.",
                "float lr_param(int k)",
                "{",
                f"    float p[{k}] = float[{k}]({', '.join(adjustable)});",
                "    return p[k];",
                "}",
                "",
                "void main()",
                "{",
                "    lr_main();",
                "    ivec2 q = ivec2(gl_FragCoord.xy);",
                f"    if (q.y == 0 && q.x < {k}) FragColor.b = lr_param(q.x);",
                "}"]
    elif relay:
        out.append(f"flat in vec4 lrParams[{nv}];")
        out.append("")
        out.append("void main()")
        out.append("{")
        for i, n in enumerate(relay):
            out.append(f"    {n} = lrParams[{i // 4}].{'xyzw'[i % 4]};")
        out.append("    lr_main();")
        out.append("}")
    else:
        out += ["void main()", "{", "    lr_main();", "}"]
    out += ["#endif", ""]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out))


def preset_text(target, title=None, overrides=None):
    """The .glslp. Both emulators give a pass's output texture that pass's own wrap mode, where
    RetroArch reads it with the next pass's, so the wrap modes move one pass up. Filters mean the
    same in all three (how a pass reads its Source). overrides: parameter values that differ from
    the ones built into the shader files (a "parameters" list, as in RetroArch presets)."""
    passes = target["passes"]
    lines = [f"# Lola Retro - {title or target['title']} for {target['emulator']}",
             "# Generated by tools/make_glsl.py from the RetroArch slang shaders. Do not edit.",
             "",
             f"shaders = {len(passes)}",
             ""]
    for i, p in enumerate(passes):
        lines.append(f"shader{i} = shaders/{p['src']}.glsl")
        if p["alias"]:
            lines.append(f"alias{i} = {p['alias']}")
        lines.append(f"filter_linear{i} = {'true' if p['filter'] else 'false'}")
        lines.append(f"wrap_mode{i} = {passes[i + 1]['wrap'] if i + 1 < len(passes) else p['wrap']}")
        for ax in "xy":
            if p["s" + ax]:
                st, sc = p["s" + ax]
                lines.append(f"scale_type_{ax}{i} = {st}")
                lines.append(f"scale_{ax}{i} = {sc!r}" if st != "absolute" else f"scale_{ax}{i} = {int(sc)}")
        if p["float"]:
            lines.append(f"float_framebuffer{i} = true")
        lines.append("")
    if overrides:
        lines.append('parameters = "' + ";".join(overrides) + '"')
        lines += [f"{n} = {fmt(v)}" for n, v in overrides.items()]
        lines.append("")      # 86Box drops a last line without a newline
    return "\n".join(lines)


def kodi_chain(name):
    """A preset's RetroArch chain as Kodi runs it: without the CRT pass's alias, which only the
    afterglow reads."""
    text = with_native_pass(PRESET_PASSES.get(name, PASSES))
    text, n = re.subn(r"^alias(\d+) = LR_CRT\n", "", text, flags=re.M)
    assert n == 1, name
    return text


def write_kodi(table):
    """The Kodi version: the shared passes in kodi/lola-retro/shaders and every preset in curved/
    and flat/, with the RetroArch preset's chain and values."""
    target = dict(KODI, params=list(table))
    values = {n: d[1] for n, d in table.items()}
    out = target["out"]
    sources = {}
    for name in PRESETS:
        text = kodi_chain(name)
        passes = retroarch_chain(text)
        for i, p in enumerate(passes):
            glsl = convert(i, dict(target, passes=passes), values, table)
            assert sources.setdefault(p["src"], glsl) == glsl, f"{p['src']} differs between presets"
        chain = re.sub(r"\.\./shaders/([\w-]+)\.slang", r"../shaders/\1.glsl", text)
        for folder, variant in (("curved", {}), ("flat", FLAT)):
            vals = {**BASE, **PRESETS[name], **variant}
            lines = [f"# Lola Retro - {name} ({folder}) for Kodi",
                     "# Generated by tools/make_glsl.py from the RetroArch presets. Do not edit.", "",
                     chain.rstrip(), "",
                     'parameters = "' + ";".join(vals) + '"']
            lines += [f"{n} = {fmt(v)}" for n, v in vals.items()]
            dest = out / folder / f"{name}.glslp"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text("\n".join(lines) + "\n")
            print("wrote", dest.relative_to(ROOT))
    (out / "shaders").mkdir(parents=True, exist_ok=True)
    for src, glsl in sources.items():
        dest = out / "shaders" / f"{src}.glsl"
        dest.write_text(glsl)
        print("wrote", dest.relative_to(ROOT))
    (out / "LICENSE").write_text((ROOT / "LICENSE").read_text())


def main():
    table = parameter_table()
    for target in TARGETS.values():
        values = {n: d[1] for n, d in table.items()}
        values.update(BASE)
        values.update(PRESETS[target["preset"]])
        values.update(target["fixed"])
        out = target["out"]
        (out / "shaders").mkdir(parents=True, exist_ok=True)
        written = set()
        for i, p in enumerate(target["passes"]):
            dest = out / "shaders" / f"{p['src']}.glsl"
            glsl = convert(i, target, values, table)
            if p["src"] in written:
                # one file used by two passes (fields): both must convert the same
                assert glsl == dest.read_text(), f"{p['src']} differs between its passes"
                continue
            dest.write_text(glsl)
            written.add(p["src"])
            print("wrote", dest.relative_to(ROOT))
        # every preset also in a flat version (FLAT of make_presets.py: no curvature, square
        # corners), as in RetroArch's flat folder; its .glslp only sets those parameters
        presets = {target["preset"]: target["title"], **target.get("variants", {})}
        for name, title in presets.items():
            for flat in (False, True):
                vals = {**values, **PRESETS[name], **target["fixed"], **(FLAT if flat else {})}
                diff = {n: v for n, v in vals.items() if n in table and float(v) != float(values[n])}
                fixed = [n for n in diff if n not in target["params"]]
                assert not fixed, f"{name} changes {fixed}, which this version has built in"
                dest = out / f"{name}{'-flat' if flat else ''}.glslp"
                dest.write_text(preset_text(target, title + (", flat" if flat else ""), diff))
                print("wrote", dest.relative_to(ROOT))
        (out / "LICENSE").write_text((ROOT / "LICENSE").read_text())
    write_kodi(table)


if __name__ == "__main__":
    main()
