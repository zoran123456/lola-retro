#!/usr/bin/env python3
"""Make the Unity version of Lola Retro (unity/lola-retro, a Unity package) from the slang passes.

The passes are translated to HLSL (tools/glsl_to_hlsl.py) and run in Unity as in RetroArch,
with every parameter adjustable. Each pass becomes one file in Shaders/Passes with a vertex and
a fragment function for one pass of the shader Hidden/Lola Retro:
- the vertex function draws one triangle over the target and sets Position and TexCoord, the
  fragment function returns FragColor; the GLSL main() functions work on them unchanged
  (they are static variables, like the varyings);
- the Vulkan uniform blocks become plain uniforms: the parameters by name (the C# side sets
  them on the material), the sizes and the frame count (per pass);
- texture reads go through a helper per texture with RetroArch's edge behaviour for that read
  (clamp_to_border, which Unity has no sampler for, by hand) and with RetroArch's rows: the top
  line first. Unity counts rows from the bottom, so the helpers turn the rows around, and so
  does the vertex function for TexCoord. Every pass then works exactly as in RetroArch, and its
  output is the right way up in Unity. The filter is each texture's own (see texture_helpers);
- the last pass writes linear light in Unity's linear colour space (lr_output).

The CRT pass for HDR displays is made from crt-hdr.slang (its own #defines count).

Written by hand, in the package: Shaders/lola-retro-unity.hlsl (what every pass needs),
Shaders/lola-retro-source.hlsl (Unity's own first pass: the console's frame, made from what Unity
rendered, also from one slice of a texture array for XR and HDRP), Shaders/lola-retro-output-hdr.hlsl
(Unity's last pass on an HDR display) and the C# side in Runtime, which runs the passes
(LolaRetroChain.cs; URP and HDRP each in an assembly of their own). The tables it
needs are written here, from make_presets.py: the pass chain (LolaRetroPasses.cs), the
parameters (LolaRetroSettings.cs) and the presets (LolaRetroPresets.cs). Unity needs a .meta file
with a fixed GUID next to every file of a package; they are written here as well, with GUIDs made
from the file's path, for every file that has none.

tools/unity-preview.py runs the Unity passes the way the C# side does and compares the picture
with the slang passes'; tools/webgl-preview.py does the same in WebGL 2 in a browser.

Needs glslangValidator and spirv-cross on PATH (for the GLSL of OpenGL ES and WebGL, see gles_glsl).

Usage: python3 tools/make_unity.py
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_presets as mp                                               # noqa: E402
from glsl_to_hlsl import convert as to_hlsl                             # noqa: E402
from make_glsl import expand, resolve_ifdefs, parameter_table, fmt      # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SLANG = ROOT / "shaders" / "lola-retro" / "shaders"
OUT = ROOT / "unity" / "lola-retro"

# The whole RetroArch chain with every optional pass: native, encode, decode, glow-h, glow-v,
# beam, show-lines (TV show), crt, present.
FULL = mp.with_native_pass(mp.with_fixed_samples(mp.with_show_lines(mp.PASSES)))


def parse_chain(passes):
    """The passes of a .slangp text. filter and wrap have RetroArch's meaning: how the pass
    samples its Source (a pass's output is read by later passes with the filter and wrap of the
    pass after it)."""
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


CHAIN = parse_chain(FULL)
assert [p["src"] for p in CHAIN] == ["native", "encode", "decode", "glow-h", "glow-v", "beam", "show-lines",
                                     "crt", "present"], [p["src"] for p in CHAIN]
# show-lines only runs on a TV show (Cable 4); without it the beam pass is LR_Beam, read by the
# CRT pass with the CRT pass's filter, as here
assert CHAIN[7]["filter"] and CHAIN[7]["wrap"] == CHAIN[6]["wrap"]

# How each pass reads each of its textures: (filter, wrap) of the read
FEEDBACK = "LR_CRTFeedback"


def reads(index):
    """name -> (linear, wrap) for the textures pass index can read."""
    p = CHAIN[index]
    out = {"Source": (p["filter"], p["wrap"]),
           "Original": (CHAIN[0]["filter"], CHAIN[0]["wrap"])}
    for j, q in enumerate(CHAIN[:index]):
        if q["alias"]:
            nxt = CHAIN[j + 1]
            out[q["alias"]] = (nxt["filter"], nxt["wrap"])
    crt = next(j for j, q in enumerate(CHAIN) if q["alias"] == "LR_CRT")
    out[FEEDBACK] = (CHAIN[crt + 1]["filter"], CHAIN[crt + 1]["wrap"])
    return out


HLSL_TYPES = {"float": "float", "vec2": "float2", "vec3": "float3", "vec4": "float4", "int": "int",
              "uint": "uint", "ivec2": "int2"}


def texture_helpers(name, linear, wrap):
    """HLSL helpers that read texture name the way RetroArch would, rows from the top. The
    filter is the texture's own (sampler<name>): OpenGL ES and WebGL have no inline samplers, so
    the C# side gives every target the filter its readers use (RetroArch's rule: the filter of
    the pass after the one that drew it, LolaRetroPasses.Linear). Every target clamps to the
    edge; clamp_to_border is done here."""
    out = [f"Texture2D {name};",
           f"SamplerState sampler{name};",
           f"int2 lr_size_{name}() {{ uint w, h; {name}.GetDimensions(w, h); return int2(w, h); }}",
           f"float4 lr_tex_{name}(float2 uv, float lod)   // {'linear' if linear else 'nearest'}, {wrap}",
           "{"]
    sample = f"{name}.SampleLevel(sampler{name}, float2(uv.x, 1.0 - uv.y), lod)"
    if linear and wrap == "clamp_to_border":
        out += [f"    float4 c = {sample};",
                "    // within half a texel of the edge the filter blends in the black border",
                f"    float2 w = saturate(min(uv, 1.0 - uv) * (float2)lr_size_{name}() + 0.5);",
                "    return c * (w.x * w.y);"]
    elif wrap == "clamp_to_border":
        out += ["    if (any(uv < 0.0) || any(uv >= 1.0)) return (float4)0.0;",
                f"    return {sample};"]
    else:
        out += [f"    return {sample};"]
    out += ["}",
            f"float4 lr_fetch_{name}(int2 p, int lod) {{ return {name}.Load(int3(p.x, lr_size_{name}().y - 1 - p.y, lod)); }}",
            ""]
    return out


def declarations(stage):
    """The layout declarations of one stage, taken out: (code, inputs, outputs, samplers).
    inputs/outputs: [(name, type, flat)]."""
    ins, outs, samplers = [], [], []

    def take(m):
        flat, kind, typ, name = m.group(1), m.group(2), m.group(3), m.group(4)
        (ins if kind == "in" else outs).append((name, typ, bool(flat)))
        return ""
    stage = re.sub(r"^\s*layout\(\s*location\s*=\s*\d+\s*\)\s*(flat\s+)?(in|out)\s+(\w+)\s+(\w+)\s*;.*\n?",
                   take, stage, flags=re.M)

    def sampler(m):
        samplers.append(m.group(1))
        return ""
    stage = re.sub(r"^\s*layout\(\s*set\s*=\s*\d+\s*,\s*binding\s*=\s*\d+\s*\)\s*uniform\s+sampler2D\s+(\w+)\s*;.*\n?",
                   sampler, stage, flags=re.M)
    assert "layout(" not in stage, stage[stage.index("layout("):][:80]
    return stage, ins, outs, samplers


def pass_hlsl(index, src=None):
    """HLSL of pass number index of CHAIN, from its own slang file or from src (crt-hdr: the CRT
    pass for HDR displays, which reads what the CRT pass reads)."""
    src = src or CHAIN[index]["src"]
    lines = expand(SLANG / f"{src}.slang")
    # the file's own #defines (crt-hdr.slang: LR_HDR) decide its #ifdefs
    defines = {m.group(1) for l in lines for m in [re.match(r"\s*#define\s+(\w+)\s*$", l)] if m}
    lines = [l for l in resolve_ifdefs(lines, defines)
             if not l.strip().startswith("#version")
             and not re.match(r"\s*#define\s+\w+\s*$", l)
             and not re.match(r"\s*#pragma\s+(parameter|name|format)\b", l)]
    text = "\n".join(lines)
    text, n1 = re.subn(r"layout\(push_constant\)\s*uniform\s+Push\s*\{.*?\}\s*params\s*;\n?", "", text, flags=re.S)
    text, n2 = re.subn(r"layout\([^)]*\)\s*uniform\s+UBO\s*\{.*?\}\s*global\s*;\n?", "", text, flags=re.S)
    assert n1 == 1 and n2 == 1, f"{src}: uniform blocks not found"
    text, n = re.subn(r"gl_Position\s*=\s*global\.MVP\s*\*\s*Position\s*;", "gl_Position = Position;", text)
    assert n == 1, src
    text = re.sub(r"\bglobal\.(LR_\w+)", r"\1", text)
    text = re.sub(r"\bparams\.(SourceSize|OriginalSize|OutputSize|FrameCount)\b", r"LR_\1", text)
    assert "global." not in text and "params." not in text, src

    parts = re.split(r"^\s*#pragma\s+stage\s+(\w+)\s*$", text, flags=re.M)
    common, stages = parts[0], dict(zip(parts[1::2], parts[2::2]))
    vs, vs_in, vs_out, vs_tex = declarations(stages["vertex"])
    fs, fs_in, fs_out, fs_tex = declarations(stages["fragment"])
    assert [n for n, _, _ in vs_in] == ["Position", "TexCoord"], vs_in
    assert [(n, t) for n, t, _ in fs_out] == [("FragColor", "vec4")], fs_out
    assert [n for n, _, _ in vs_out] == [n for n, _, _ in fs_in], src
    assert not vs_tex, f"{src}: the vertex stage reads a texture"
    vs, n_vs = re.subn(r"\bvoid\s+main\s*\(\s*\)", "void lr_vertex_main()", vs)
    fs, n_fs = re.subn(r"\bvoid\s+main\s*\(\s*\)", "void lr_fragment_main()", fs)
    assert n_vs == 1 and n_fs == 1, src

    can_read = reads(index)
    helpers = []
    for name in fs_tex:
        linear, wrap = can_read[name]
        helpers += texture_helpers(name, linear, wrap)
        fs = re.sub(r"\btextureLod\(\s*" + name + r"\s*,", f"lr_tex_{name}(", fs)
        fs = re.sub(r"\btexelFetch\(\s*" + name + r"\s*,", f"lr_fetch_{name}(", fs)
        fs = re.sub(r"\btextureSize\(\s*" + name + r"\s*,\s*0\s*\)", f"lr_size_{name}()", fs)
        assert not re.search(r"\b(texture|textureLod|texelFetch|textureSize)\(\s*" + name + r"\b", fs), name

    code = to_hlsl("\n".join([common.strip("\n"), "", "// --- vertex stage", vs.strip("\n"), "",
                              "// --- fragment stage", fs.strip("\n")]))
    varyings = vs_out
    out = [f"// Lola Retro - {src} pass for Unity.",
           f"// Generated by tools/make_unity.py from shaders/lola-retro/shaders/{src}.slang. Do not edit.",
           "",
           '#include "../lola-retro-unity.hlsl"',
           "",
           "// RetroArch's stage inputs and outputs (set by LRVert and LRFrag below)",
           "static float4 Position;",
           "static float2 TexCoord;",
           "static float4 gl_Position;",
           "static float4 FragColor;"]
    out += [f"static {HLSL_TYPES[t]} {n};" for n, t, _ in varyings]
    out.append("")
    if helpers:
        out += ["// Textures, read as RetroArch reads them (rows from the top)"] + helpers
    out += [code.strip("\n"), "",
            "// --- Unity's entry points",
            "struct LRVaryings",
            "{",
            "    float4 position : SV_POSITION;"]
    for k, (n, t, flat) in enumerate(varyings):
        out.append(f"    {'nointerpolation ' if flat else ''}{HLSL_TYPES[t]} {n} : TEXCOORD{k};")
    out += ["};",
            "",
            "LRVaryings LRVert(uint vertexID : SV_VertexID)",
            "{",
            "    lr_fullscreen_triangle(vertexID, Position, TexCoord);",
            "    lr_vertex_main();",
            "    LRVaryings o;",
            "    o.position = gl_Position;"]
    out += [f"    o.{n} = {n};" for n, _, _ in varyings]
    out += ["    return o;",
            "}",
            "",
            "float4 LRFrag(LRVaryings i) : SV_Target",
            "{"]
    out += [f"    {n} = i.{n};" for n, _, _ in varyings]
    out += ["    lr_fragment_main();",
            "    return lr_output(FragColor);" if src == "present" else "    return FragColor;",
            "}",
            ""]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out))


def hdr_parameters():
    """The HDR parameters of hdr.inc (paper white, peak): Unity knows them from the display."""
    return re.findall(r'^\s*#pragma\s+parameter\s+(LR_NITS_\w+)', (SLANG / "hdr.inc").read_text(), flags=re.M)


def params_hlsl(table):
    names = [n for n in table if not n.startswith("LR_HDR_")]
    out = ["// Lola Retro - the parameters, as uniforms the C# side sets on the material.",
           "// Generated by tools/make_unity.py from shaders/lola-retro/shaders/common.inc. Do not edit.",
           ""]
    out += [f"float {n};" for n in names]
    out += ["", "// HDR displays (hdr.inc): set from Unity's HDR output settings"]
    out += [f"float {n};" for n in hdr_parameters()]
    return "\n".join(out) + "\n"


# Passes after CHAIN's, in this order: (name, file, define)
EXTRA_PASSES = [("crt-hdr", "../Passes/crt-hdr.hlsl", None),                 # the CRT pass for HDR displays
                ("output-hdr", "../lola-retro-output-hdr.hlsl", None),       # Unity's last pass for HDR displays
                ("source-array", "../lola-retro-source.hlsl", "LR_INPUT_ARRAY")]   # one slice of a texture array (XR, HDRP)


def run_tool(*args):
    if shutil.which(str(args[0])) is None:
        raise SystemExit(f"{args[0]} is not on PATH (glslang and SPIRV-Cross make the OpenGL ES and WebGL passes)")
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"{args[0]} failed:\n{r.stdout}{r.stderr}")
    return r.stdout


def gles_glsl(path, define):
    """GLSL ES 3.00 of a Unity pass (HLSL), for its GLSLPROGRAM pass: glslang's HLSL front end to
    SPIR-V, SPIRV-Cross to GLSL. Unity's own way there (FXC, then HLSLcc) keeps integers in float
    registers as their bit patterns, tiny denormal floats, which WebGL GPUs flush to zero: the
    passes that use integers came out black. This way the integers stay integers (it is the way
    tools/webgl-preview.py checks against the slang passes). Unity binds uniforms and textures
    by name, so the uniform block becomes plain uniforms, the varyings are named by their
    location, and each texture's sampler takes the texture's name (its filter is the texture's
    own anyway, as in the HLSL passes)."""
    parts = {}
    with tempfile.TemporaryDirectory() as tmp:
        for short, entry in (("vert", "LRVert"), ("frag", "LRFrag")):
            spv = Path(tmp) / f"{short}.spv"
            run_tool("glslangValidator", "-D", "-V", "-S", short, "-e", entry, "-o", spv,
                     *([f"-D{define}"] if define else []), path)
            refl = json.loads(run_tool("spirv-cross", spv, "--reflect", "--entry", entry))
            io = ("outputs", "out") if short == "vert" else ("inputs", "in")
            names = [a for v in refl.get(io[0], []) for a in
                     ("--rename-interface-variable", io[1], v["location"], f"lr_var{v['location']}")]
            glsl = run_tool("spirv-cross", spv, "--es", "--version", "300", "--entry", entry,
                            "--glsl-emit-ubo-as-plain-uniforms", *names)
            # the uniform block, a struct uniform now -> one plain uniform per member
            def plain(m):
                members = [l.strip() for l in m.group(2).split(";") if l.strip()]
                return "".join(f"uniform {member};\n" for member in members)
            glsl, n = re.subn(r"struct (\w+)\s*\{([^}]*)\};\s*uniform \1 (\w+);\n", plain, glsl)
            inst = re.findall(r"uniform _Global (\w+);", glsl)
            assert n <= 1 and not inst, path
            glsl = re.sub(r"\b_\d+\.(?=LR_)", "", glsl)
            # samplers: SPIRV_Cross_Combined<texture><sampler> (or the dummy sampler of Load) -> <texture>
            textures = re.findall(r"^Texture2D(?:Array)?\s+(\w+)\s*;", Path(path).read_text(), flags=re.M)
            if Path(path).name == "lola-retro-source.hlsl":
                textures = ["LR_InputArray" if define == "LR_INPUT_ARRAY" else "LR_Input"]
            for t in sorted(textures, key=len, reverse=True):
                glsl = re.sub(r"\bSPIRV_Cross_Combined" + t + r"\w*", t, glsl)
            decl = re.compile(r"^uniform\s+highp\s+sampler2D(Array)?\s+(\w+)\s*;\n", flags=re.M)
            seen = set()
            glsl = decl.sub(lambda m: "" if m.group(2) in seen or seen.add(m.group(2)) else m.group(0), glsl)
            assert "SPIRV_Cross" not in glsl, (path, re.findall(r"SPIRV_Cross\w*", glsl)[:3])
            glsl = glsl.replace("precision mediump float;", "precision highp float;")
            assert glsl.startswith("#version 300 es\n"), path
            parts[short] = glsl[len("#version 300 es\n"):]
    return "\n".join(["#version 300 es", "#ifdef VERTEX", parts["vert"].strip("\n"), "#endif",
                      "#ifdef FRAGMENT", parts["frag"].strip("\n"), "#endif"])


def shader_lab():
    """Hidden/Lola Retro: Unity's source pass, every pass of CHAIN, then EXTRA_PASSES. First a
    SubShader in GLSL for OpenGL ES 3 and WebGL (see gles_glsl), then one in HLSL for the rest."""
    passes = ([("source", "lola-retro-source.hlsl", None)] + [(p["src"], f"Passes/{p['src']}.hlsl", None) for p in CHAIN]
              + [(n, f[3:], d) for n, f, d in EXTRA_PASSES])
    out = ["// Lola Retro - every pass of the chain, run by the C# side (LolaRetroChain.cs) in this order.",
           "// Generated by tools/make_unity.py. Do not edit.",
           'Shader "Hidden/Lola Retro"',
           "{",
           "    // OpenGL ES 3 and WebGL: GLSL made from the HLSL passes by SPIRV-Cross (tools/make_unity.py, gles_glsl)",
           "    SubShader",
           "    {",
           "        Cull Off ZWrite Off ZTest Always Blend Off",
           ""]
    for name, path, define in passes:
        glsl = gles_glsl(OUT / "Shaders" / path, define)
        out += ["        Pass",
                "        {",
                f'            Name "{name}"',
                "            GLSLPROGRAM",
                glsl,
                "            ENDGLSL",
                "        }",
                ""]
    out += ["    }",
            "",
            "    // everything else",
            "    SubShader",
            "    {",
            "        Cull Off ZWrite Off ZTest Always Blend Off",
            ""]
    for name, path, define in passes:
        out += ["        Pass",
                "        {",
                f'            Name "{name}"',
                "            HLSLPROGRAM",
                "            #pragma target 3.5",
                "            #pragma exclude_renderers gles3",
                "            #pragma vertex LRVert",
                "            #pragma fragment LRFrag"]
        if define:
            out.append(f"            #define {define}")
        out += [f'            #include "../{path}"',
                "            ENDHLSL",
                "        }",
                ""]
    out += ["    }", "}", ""]
    return "\n".join(out)


# --- C# tables

# Each parameter as a field of LolaRetroSettings: name, and its type when it is not a float
# (an enum with its values, bool, or int for a count).
FIELDS = {
    "LR_CONSOLE": ("consoleTiming", ("ConsoleTiming", ["Auto", "NES and SNES", "Mega Drive H40", "Mega Drive H32 and Master System",
                                                       "PlayStation", "PlayStation 2", "Amiga", "PC VGA", "Arcade 15 kHz",
                                                       "Arcade 24 kHz", "X68000", "X68000 256 lines at 15 kHz"])),
    "LR_NORM": ("tvStandard", ("TvStandard", ["Auto", "NTSC", "PAL"])),
    "LR_HIRES": ("framesOver300Lines", ("TallFrames", ["Auto", "Interlaced", "PC monitor"])),
    "LR_CABLE": ("cable", ("Cable", ["RF", "Composite", "S-Video", "RGB", "TV show"])),
    "LR_COMB": ("combFilter", bool),
    "LR_YTRAP": ("lumaTrap", None),
    "LR_DBLEND": ("ditherBlend", None),
    "LR_DBLEND_AUTO": ("ditherBlendAuto", bool),
    "LR_DAMPER": ("damperWires", None),
    "LR_SHARP": ("sharpness", None),
    "LR_SAT": ("colour", None),
    "LR_TINT": ("tint", None),
    "LR_DEMOD": ("colourDecoder", ("ColourDecoder", ["Auto", "Standard", "US TV", "Japanese TV"])),
    "LR_BRIGHT": ("brightness", None),
    "LR_CONTRAST": ("contrast", None),
    "LR_NOISE": ("rfNoise", None),
    "LR_STEADY": ("noFlicker", bool),
    "LR_TAPE": ("tapeCopies", int),
    "LR_GHOST": ("antennaGhost", None),
    "LR_SIG_LO": ("beamWidthDark", None),
    "LR_SIG_HI": ("beamWidthWhite", None),
    "LR_HFOCUS": ("horizontalFocus", None),
    "LR_GAMMA": ("tubeGamma", None),
    "LR_PERSIST": ("phosphorAfterglow", None),
    "LR_CONV": ("misconvergence", None),
    "LR_SMOOTH": ("scanlineSmoothing", None),
    "LR_MASK_TYPE": ("mask", ("MaskType", ["None", "Aperture grille", "Slot mask", "Shadow mask", "Projection screen"])),
    "LR_MASK_STR": ("maskStrength", None),
    "LR_MASK_TRIADS": ("maskTriads", None),
    "LR_MASK_PX": ("maskOnScreenPixels", int),
    "LR_WHITE": ("whitePoint", None),
    "LR_PHOS": ("phosphors", ("Phosphors", ["Auto", "sRGB", "SMPTE-C", "EBU", "Japanese P22"])),
    "LR_CURV_X": ("curvatureHorizontal", None),
    "LR_CURV_Y": ("curvatureVertical", None),
    "LR_BEND": ("rasterBend", None),
    "LR_CORNER": ("roundedCorners", None),
    "LR_GLOW": ("glassGlow", None),
    "LR_GLOW_SIZE": ("glassGlowSize", None),
    "LR_VIGNETTE": ("darkerEdges", None),
    "LR_OVERSCAN": ("overscan", None),
    "LR_OVERSCAN_V": ("overscanHeight", None),
    "LR_FILL": ("linesFillHeight", bool),
    "LR_LIN_X": ("linearityHorizontal", None),
    "LR_LIN_Y": ("linearityVertical", None),
    "LR_REFLECT": ("roomReflection", None),
    "LR_MON_MM": ("monitorInMillimetres", bool),
    "LR_MON_SIZE": ("monitorSize", int),
    "LR_MON_PITCH": ("dotPitch", None),
    "LR_MON_SPOT_LO": ("spotSizeDark", None),
    "LR_MON_SPOT_HI": ("spotSizeWhite", None),
    "LR_MON_CORNER": ("spotSizeCorners", None),
    "LR_SCREEN_H": ("realSizeScreenHeight", None),
    "LR_SCREEN_UNIT": ("realSizeUnit", ("LengthUnit", ["Centimetres", "Inches"])),
    "LR_BACKDROP": ("aroundTheTube", ("AroundTheTube", ["Black", "Room", "Space", "Synthwave", "Tiles", "Bouncing lines",
                                                        "Underwater", "Copper bars", "Amiga demo", "Hills", "Night city",
                                                        "Arcade carpet"])),
    "LR_ROOM": ("roomLight", None),
    "LR_SPILL": ("screenLightOnCasing", None),
    "LR_SCENE_SPEED": ("sceneSpeed", None),
}

# The presets as Unity offers them: device presets, then system presets (a device with the
# system's timing). InspectorName paths make submenus.
DEVICE_TITLES = {
    "consumer-tv-composite": "Consumer TV, composite",
    "consumer-tv-scart-rgb": "Consumer TV, SCART RGB",
    "tv-show-broadcast": "TV show (broadcast)",
    "trinitron-s-video": "Sony Trinitron, S-Video",
    "studio-monitor-rgb": "Studio monitor, RGB",
    "studio-monitor-composite": "Sony PVM-14L2, composite",
    "old-tv-rf": "Old TV, RF",
    "crt-projector": "CRT projector",
    "pc-monitor-vga": "PC monitor (VGA)",
    "pc-monitor-vga-good": "PC monitor (VGA), good",
    "pc-monitor-vga-premium": "PC monitor (VGA), premium",
    "pc-monitor-vga-premium-plus": "PC monitor (VGA), premium+",
    "pc-monitor-vga-extreme": "PC monitor (VGA), extreme",
    "amiga-1084s": "Commodore 1084S (Amiga)",
    "x68000-monitor": "Sharp CZ-600D (X68000)",
}
SYSTEM_TITLES = {
    "nes": "NES", "snes": "SNES", "master-system": "Master System", "mega-drive-genesis": "Mega Drive, Genesis",
    "pc-engine-turbografx": "PC Engine, TurboGrafx-16", "playstation": "PlayStation", "saturn": "Saturn",
    "nintendo-64": "Nintendo 64", "playstation-2": "PlayStation 2", "gamecube": "GameCube", "dreamcast": "Dreamcast",
    "arcade-15khz": "Arcade, 15 kHz", "amiga": "Amiga", "dos-pc": "DOS PC", "pc-98": "PC-98",
    "x68000": "X68000",
}
assert set(DEVICE_TITLES) == set(mp.PRESETS), set(mp.PRESETS) ^ set(DEVICE_TITLES)
assert set(SYSTEM_TITLES) == set(mp.SYSTEMS), set(mp.SYSTEMS) ^ set(SYSTEM_TITLES)


def cs_name(title):
    """An enum member name from a title: "Mega Drive H40" -> MegaDriveH40, "S-Video" -> SVideo."""
    words = re.findall(r"[A-Za-z0-9]+", title.replace("+", " plus"))
    name = "".join(w[0].upper() + w[1:] for w in words)
    return name if not name[0].isdigit() else "_" + name


def cs_float(v):
    s = repr(float(v))
    return (s if "e" in s or "." in s else s + ".0") + "f"


def cs_value(n, v):
    """C# value of parameter n set to v."""
    field, kind = FIELDS[n]
    if kind is None:
        return cs_float(v)
    if kind is bool:
        return "true" if float(v) > 0.5 else "false"
    if kind is int:
        return str(int(round(float(v))))
    enum, members = kind
    return f"{enum}.{cs_name(members[int(round(float(v)))])}"


def cs_settings(table):
    """LolaRetroSettings.cs: every parameter as a field, with the slider range and the label of
    the RetroArch version, and the code that sets them on the material."""
    out = ["// Lola Retro - every parameter of the shader.",
           "// Generated by tools/make_unity.py from shaders/lola-retro/shaders/common.inc. Do not edit.",
           "using System;",
           "using UnityEngine;",
           "",
           "namespace LolaRetro",
           "{"]
    for n, (field, kind) in FIELDS.items():
        if isinstance(kind, tuple):
            enum, members = kind
            out.append(f"    public enum {enum}")
            out.append("    {")
            for k, m in enumerate(members):
                out.append(f'        [InspectorName("{m}")] {cs_name(m)} = {k},')
            out.append("    }")
            out.append("")
    out += ["    /// <summary>The values of every parameter. The presets (LolaRetroPresets) fill them in.</summary>",
            "    [Serializable]",
            "    public class LolaRetroSettings",
            "    {"]
    names = [n for n in table if not n.startswith("LR_HDR_")]
    assert names == list(FIELDS), set(names) ^ set(FIELDS)
    for n in table:
        desc, default, lo, hi, step = table[n]
        if n.startswith("LR_HDR_"):
            out.append(f'        [Header("{desc.strip("- ")}")]')
            continue
        field, kind = FIELDS[n]
        tip = desc.replace('"', '\\"')
        if kind is None:
            out.append(f'        [Tooltip("{tip}"), Range({cs_float(lo)}, {cs_float(hi)})]')
            out.append(f"        public float {field} = {cs_value(n, default)};")
        elif kind is int:
            out.append(f'        [Tooltip("{tip}"), Range({int(lo)}, {int(hi)})]')
            out.append(f"        public int {field} = {cs_value(n, default)};")
        elif kind is bool:
            out.append(f'        [Tooltip("{tip}")]')
            out.append(f"        public bool {field} = {cs_value(n, default)};")
        else:
            out.append(f'        [Tooltip("{tip}")]')
            out.append(f"        public {kind[0]} {field} = {cs_value(n, default)};")
    out += ["",
            "        // the shader's names, found when first needed (not while Unity loads the settings)",
            "        static int[] ids;",
            "",
            "        /// <summary>Sets every parameter on the material.</summary>",
            "        public void Apply(Material m)",
            "        {",
            "            ids ??= new[]",
            "            {"]
    out += [f'                Shader.PropertyToID("{n}"),' for n in names]
    out += ["            };"]
    for k, n in enumerate(names):
        field, kind = FIELDS[n]
        if kind is None:
            v = field
        elif kind is bool:
            v = f"{field} ? 1f : 0f"
        else:
            v = f"(float){field}"
        out.append(f"            m.SetFloat(ids[{k}], {v});")
    out += ["        }",
            "",
            "        /// <summary>A copy of these settings.</summary>",
            "        public LolaRetroSettings Clone() => (LolaRetroSettings)MemberwiseClone();",
            "    }",
            "}",
            ""]
    return "\n".join(out)


def cs_presets(table):
    """LolaRetroPresets.cs: the presets of make_presets.py as settings."""
    defaults = {n: d[1] for n, d in table.items() if not n.startswith("LR_HDR_")}
    out = ["// Lola Retro - the presets of the RetroArch version.",
           "// Generated by tools/make_unity.py from tools/make_presets.py. Do not edit.",
           "namespace LolaRetro",
           "{",
           "    public enum LolaRetroPreset",
           "    {"]
    members = []
    for name, title in DEVICE_TITLES.items():
        members.append((cs_name(title), f"TV and monitors/{title}", {**mp.BASE, **mp.PRESETS[name]}))
    for name, title in SYSTEM_TITLES.items():
        device, over = mp.SYSTEMS[name]
        members.append(("System" + cs_name(title), f"Systems/{title}", {**mp.BASE, **mp.PRESETS[device], **over}))
    for k, (member, path, _) in enumerate(members):
        out.append(f'        [UnityEngine.InspectorName("{path}")] {member} = {k},')
    out += ["    }",
            "",
            "    public static class LolaRetroPresets",
            "    {",
            "        /// <summary>The settings of a preset; flat: with a flat screen and square corners, as the",
            "        /// presets in the RetroArch version's flat folder.</summary>",
            "        public static LolaRetroSettings Get(LolaRetroPreset preset, bool flat = false)",
            "        {",
            "            var s = new LolaRetroSettings();",
            "            switch (preset)",
            "            {"]
    for member, _, values in members:
        changed = {n: v for n, v in values.items() if float(v) != float(defaults[n])}
        out.append(f"                case LolaRetroPreset.{member}:")
        for n, v in changed.items():
            out.append(f"                    s.{FIELDS[n][0]} = {cs_value(n, v)};")
        out.append("                    break;")
    out += ["            }",
            "            if (flat)",
            "            {"]
    out += [f"                s.{FIELDS[n][0]} = {cs_value(n, v)};" for n, v in mp.FLAT.items()]
    out += ["            }",
            "            return s;",
            "        }",
            "    }",
            "}",
            ""]
    return "\n".join(out)


def cs_scale(scale):
    kind, k = scale
    return f"new PassScale(ScaleKind.{kind.capitalize()}, {cs_float(k)})"


def cs_passes():
    """LolaRetroPasses.cs: the passes of Hidden/Lola Retro and the size of each one's output."""
    crt = next(p for p in CHAIN if p["src"] == "crt")
    present = next(p for p in CHAIN if p["src"] == "present")
    source = dict(src="source", sx=None, sy=None, filter=False, float=False)
    # (pass, what it is): Unity's source pass, CHAIN, then EXTRA_PASSES with the sizes and
    # filters of the passes they stand in for
    rows = ([(source, "Unity's own: the console's frame")] + [(p, p["src"]) for p in CHAIN]
            + [(dict(crt, src="crt-hdr"), "the CRT pass for HDR displays"),
               (dict(present, src="output-hdr", float=True), "Unity's own: the last pass for HDR displays"),
               (dict(source, src="source-array"), "Unity's own: the source pass for one slice of a texture array")])
    assert [r[0]["src"] for r in rows[len(CHAIN) + 1:]] == [e[0] for e in EXTRA_PASSES]
    names = [cs_name(p["src"].replace("-", " ")) for p, _ in rows]
    monitor = parse_chain(mp.with_native_pass(mp.PASSES))
    assert monitor[1]["src"] == "encode" and monitor[1]["sx"] == ("source", 4.0), monitor[1]

    def scale(sc):
        return cs_scale(sc) if sc else "default"
    out = ["// Lola Retro - the passes of the shader Hidden/Lola Retro, in the order they run.",
           "// Generated by tools/make_unity.py from tools/make_presets.py. Do not edit.",
           "namespace LolaRetro",
           "{",
           "    static class LolaRetroPasses",
           "    {",
           "        // the shader's passes"]
    out += [f"        public const int {n} = {k};   // {what}" for k, (n, (_, what)) in enumerate(zip(names, rows))]
    out += [f"        public const int Count = {len(names)};",
            "",
            "        // Size of each pass's output, as in RetroArch's presets, along x and y (the source passes",
            "        // make the console's frame)",
            "        public static readonly PassScale[] X =",
            "        {"]
    out += [f"            {scale(p['sx'])},   // {p['src']}" for p, _ in rows]
    out += ["        };",
            "        public static readonly PassScale[] Y =",
            "        {"]
    out += [f"            {scale(p['sy'])},   // {p['src']}" for p, _ in rows]
    out += ["        };",
            "",
            "        // The TV presets run the encoder at a fixed width, the PC and Amiga monitors (and every",
            "        // tube in mm) at this many samples per pixel (see ENC_SAMPLES in common.inc)",
            f"        public static readonly PassScale EncodeMonitorX = {cs_scale(monitor[1]['sx'])};",
            "",
            "        // How each pass samples what it reads (filter_linear): a target gets the filter of the",
            "        // next pass that runs (RetroArch reads a pass's output with the filter of the pass after it)",
            "        public static readonly bool[] Linear = { " + ", ".join(
                "true" if p["filter"] else "false" for p, _ in rows) + " };",
            "",
            "        // Float output (RGBA16F), or 8 bits",
            "        public static readonly bool[] Float = { " + ", ".join(
                "true" if p["float"] else "false" for p, _ in rows) + " };",
            "    }",
            "}",
            ""]
    return "\n".join(out)


def guid(path):
    """A fixed GUID for a file of the package, from its path in the package."""
    return hashlib.md5(("lola-retro-unity/" + path.relative_to(OUT).as_posix()).encode()).hexdigest()


META = {
    ".cs": "MonoImporter:\n  externalObjects: {{}}\n  serializedVersion: 2\n  defaultReferences: []\n"
           "  executionOrder: 0\n  icon: {{instanceID: 0}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n",
    ".shader": "ShaderImporter:\n  externalObjects: {{}}\n  defaultTextures: []\n  nonModifiableTextures: []\n"
               "  userData: \n  assetBundleName: \n  assetBundleVariant: \n",
    ".hlsl": "ShaderIncludeImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n",
    ".asmdef": "AssemblyDefinitionImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n",
    ".json": "PackageManifestImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n",
    ".md": "TextScriptImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n",
    "": "DefaultImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n",
}


def write_metas():
    """A .meta file for every file and folder of the package that has none."""
    for path in sorted(OUT.rglob("*")):
        if path.suffix == ".meta" or path.name.startswith(".") or path.name.endswith("~"):
            continue
        if any(part.endswith("~") for part in path.relative_to(OUT).parts):
            continue                       # folders ending in ~ are not imported (Samples~)
        meta = path.with_name(path.name + ".meta")
        if path.is_dir():
            body = "folderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
        else:
            body = META.get(path.suffix, META[""]).format()
        text = f"fileFormatVersion: 2\nguid: {guid(path)}\n{body}"
        if path.name == "package.json":
            text = f"fileFormatVersion: 2\nguid: {guid(path)}\n{META['.json'].format()}"
        if not meta.exists() or meta.read_text() != text:
            meta.write_text(text)
            print("wrote", meta.relative_to(ROOT))


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text() != text:
        path.write_text(text)
        print("wrote", path.relative_to(ROOT))


def main():
    table = parameter_table()
    for i, p in enumerate(CHAIN):
        write(OUT / "Shaders" / "Passes" / f"{p['src']}.hlsl", pass_hlsl(i))
    crt = next(i for i, p in enumerate(CHAIN) if p["src"] == "crt")
    write(OUT / "Shaders" / "Passes" / "crt-hdr.hlsl", pass_hlsl(crt, "crt-hdr"))
    write(OUT / "Shaders" / "lola-retro-params.hlsl", params_hlsl(table))
    write(OUT / "Shaders" / "Resources" / "LolaRetro.shader", shader_lab())
    write(OUT / "Runtime" / "LolaRetroSettings.cs", cs_settings(table))
    write(OUT / "Runtime" / "LolaRetroPresets.cs", cs_presets(table))
    write(OUT / "Runtime" / "LolaRetroPasses.cs", cs_passes())
    write(OUT / "LICENSE", (ROOT / "LICENSE").read_text())
    write_metas()


if __name__ == "__main__":
    main()
