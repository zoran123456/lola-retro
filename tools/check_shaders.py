#!/usr/bin/env python3
"""Compile-check every .slang pass with glslangValidator, the generated GLSL ports and the Unity passes.

The .slang files are preprocessed the way RetroArch does: expands #include, drops the
#pragma parameter/name/format lines, and splits the vertex and fragment stages.
The .glsl files (tools/make_glsl.py) are compiled the way their emulator does, once with
"#define VERTEX" and once with "#define FRAGMENT":
- Amiberry puts the defines right after the #version line;
- 86Box keeps "#version" and the word after it, removes the #pragma parameter lines and any
  "#define texture..." line, and puts an #extension line, the defines and "#line 1" in front;
- Kodi removes the #pragma parameter lines that start a line and puts the version and the defines in
  front, once as OpenGL's 330 and once as OpenGL ES's 310 es (Kodi's version for 330 on GLES).
The Unity passes (tools/make_unity.py) are HLSL: glslang's HLSL front end compiles each one's
vertex and fragment function (LRVert, LRFrag) the way the ShaderLab pass names them. Their GLSL
ES 3.00 versions (Unity's OpenGL ES and WebGL SubShader) are compiled as Unity compiles them.

Usage: python3 tools/check_shaders.py
Needs glslangValidator (package glslang-tools / glslang).
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHADERS = ROOT / "shaders" / "lola-retro" / "shaders"
AMIBERRY = sorted((ROOT / "amiberry").glob("**/*.glsl"))
BOX86 = sorted((ROOT / "86box").glob("**/*.glsl"))
KODI = sorted((ROOT / "kodi").glob("**/*.glsl"))
UNITY = ROOT / "unity" / "lola-retro" / "Shaders"


def expand(path, seen=None):
    seen = seen or set()
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


def split_stages(lines):
    common, stages, current = [], {"vertex": [], "fragment": []}, None
    for line in lines:
        m = re.match(r"\s*#pragma\s+stage\s+(\w+)", line)
        if m:
            current = m.group(1)
            continue
        if re.match(r"\s*#pragma\s+(parameter|name|format)\b", line):
            continue
        if line.strip().startswith("#version"):
            continue
        (stages[current] if current else common).append(line)
    return {k: ["#version 450"] + common + v for k, v in stages.items()}


def compile_stage(name, stage, text, args, ext=None):
    ext = ext or ("vert" if stage == "vertex" else "frag")
    with tempfile.NamedTemporaryFile("w", suffix="." + ext, delete=False, dir=None) as f:
        f.write(text)
        tmp = f.name
    r = subprocess.run(["glslangValidator", *args, tmp], capture_output=True, text=True)
    print(f"{name:18} {stage:8} {'ok' if r.returncode == 0 else 'FAILED'}")
    if r.returncode != 0:
        print(r.stdout + r.stderr)
    return r.returncode == 0


def amiberry_source(src, define):
    cut = src.index("\n") + 1                      # after the #version line
    return src[:cut] + f"#define {define}\n#define PARAMETER_UNIFORM\n" + src[cut:]


def box86_source(src, define):
    """As 86Box's OpenGLRenderer::compile_shader and glslp_parse assemble it."""
    def blank(text, start):
        i = text.find(start)
        while i >= 0:
            j = text.find("\n", i)
            j = len(text) if j < 0 else j
            text = text[:i] + " " * (j - i) + text[j:]
            i = text.find(start)
        return text
    src = blank(blank(src, "#pragma parameter"), "#define texture")
    version = re.search(r"^\s*(#version\s+\w+)", src, flags=re.M).group(1)
    src = re.sub(r"^\s*#version\s+\w+", "", src, flags=re.M)
    return (version + "\n" + "\n#extension GL_ARB_shading_language_420pack : enable\n"
            + f"#define {define}\n#define PARAMETER_UNIFORM\n" + "\n#line 1\n" + src)


def kodi_source(src, define, version):
    """As Kodi's CShaderGL and CShaderGLES assemble it (CShaderUtils::StripParameterPragmas, GetGLSLVersion)."""
    src = re.sub(r"^#pragma parameter.*$", "", src, flags=re.M)
    src = re.sub(r"^\s*#version\s+\w+.*$", "", src, count=1, flags=re.M)
    return f"#version {version}\n#define {define}\n#define PARAMETER_UNIFORM\n" + src


def compile_unity(path, define, stage, entry, short):
    """One stage of a Unity pass (with the #define its ShaderLab pass sets), its includes found
    next to it as Unity finds them."""
    r = subprocess.run(["glslangValidator", "-D", "-V", "-S", short, "-e", entry, "-o", "/dev/null",
                        *([f"-D{define}"] if define else []), str(path)], capture_output=True, text=True)
    name = "unity/" + path.stem.replace("lola-retro-", "") + (f" {define}" if define else "")
    print(f"{name:18} {stage:8} {'ok' if r.returncode == 0 else 'FAILED'}")
    if r.returncode != 0:
        print(r.stdout + r.stderr)
    return r.returncode == 0


def main():
    ok = True
    for slang in sorted(SHADERS.glob("*.slang")):
        for stage, src in split_stages(expand(slang)).items():
            ok &= compile_stage(slang.name, stage, "\n".join(src) + "\n", ["-V", "-o", "/dev/null"])
    for files, assemble, label in ((AMIBERRY, amiberry_source, "amiberry"), (BOX86, box86_source, "86box")):
        for glsl in files:
            src = glsl.read_text()
            for stage, define in (("vertex", "VERTEX"), ("fragment", "FRAGMENT")):
                ok &= compile_stage(f"{label}/{glsl.stem}", stage, assemble(src, define), [])
    for glsl in KODI:
        src = glsl.read_text()
        for version in ("330", "310 es"):
            for stage, define in (("vertex", "VERTEX"), ("fragment", "FRAGMENT")):
                ok &= compile_stage(f"kodi/{glsl.stem} {version}", stage, kodi_source(src, define, version), [])
    unity = [(UNITY / "lola-retro-source.hlsl", None), (UNITY / "lola-retro-source.hlsl", "LR_INPUT_ARRAY"),
             (UNITY / "lola-retro-output-hdr.hlsl", None)] + [(f, None) for f in sorted((UNITY / "Passes").glob("*.hlsl"))]
    for pass_file, define in unity:
        for stage, entry, short in (("vertex", "LRVert", "vert"), ("fragment", "LRFrag", "frag")):
            ok &= compile_unity(pass_file, define, stage, entry, short)
    # the GLSL ES 3.00 passes of Unity's OpenGL ES and WebGL SubShader, as Unity compiles them:
    # the source once with VERTEX and once with FRAGMENT defined
    shader = (UNITY / "Resources" / "LolaRetro.shader").read_text()
    for name, glsl in re.findall(r'Name "([^"]+)"\s*GLSLPROGRAM\n(.*?)\n\s*ENDGLSL', shader, flags=re.S):
        for stage, define in (("vertex", "VERTEX"), ("fragment", "FRAGMENT")):
            src = glsl.replace("#version 300 es\n", f"#version 300 es\n#define {define}\n", 1)
            ok &= compile_stage(f"unity-gles/{name}", stage, src + "\n", [])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
