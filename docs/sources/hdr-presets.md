# HDR presets: why they are separate presets

## The request

Libretro forum, post 49 (StargazingDog, 2026-10-26,
https://forums.libretro.com/t/lola-retro-crt-shader-simulating-the-full-analog-signal-chain/51367/49):

- HDR versions of the system presets;
- one set of presets with an HDR switch instead of separate folders.

## What RetroArch gives a shader

Read from RetroArch's source on 2026-10-26.

**RetroArch 1.22.2** (the latest stable release, 2025-11-20) and 1.21.0
(`gfx/drivers_shader/slang_reflection.cpp` at those tags):

- No uniform tells a shader whether HDR is on: the semantics are the usual ones, plus OriginalFPS.
- The last pass's output format (`#pragma format A2B10G10R10_UNORM_PACK32` in present-hdr.slang) decides
  whether RetroArch passes the picture to the display as HDR10. That format is fixed in the file.
- So a preset either writes HDR10 or doesn't. A switch inside one preset would come out grey and flat
  (HDR10 shown as SDR) or wrong (SDR taken as HDR10) whenever it is set the wrong way. Keeping the two
  apart is the reason for separate folders.

**RetroArch master** (`gfx/drivers_shader/slang_process.c`; commits of 2026-10-18 such as 5b2fda07ad,
8e993f4fe2 and 29ec3c0390) added:

- the uniforms EnableHDR, PaperWhiteNits, PeakNits, MaxNits, MinNits, SourceHDR and Passthrough;
- an optional `hdr_mode` per preset (`video_shader_get_hdr_mode`). With it, the last pass's format is
  chosen by RetroArch (`glslang_hdr_output_format`).

Once that is in a stable release, one preset set that switches by itself becomes possible. Until then the
`hdr/` presets stay separate.

## What the code does

- `tools/make_presets.py`, `hdr_passes`: the device presets in `hdr/curved` and `hdr/flat`, with
  crt-hdr.slang and present-hdr.slang, and no scale_type on the last pass.
- From 2026-10-26, the same for the system presets: `hdr/systems/curved` and `hdr/systems/flat`. Each is
  its device's HDR preset with the system's settings (the loop after VARIANTS in `main`).
- Checked in RetroArch 1.22.2 on the author's Mac on 2026-10-26, with HDR off. Six of them (systems snes,
  arcade-15khz, pc-98, x68000, mega-drive-genesis curved, playstation flat) load on Vulkan, Metal and glcore,
  with every pass compiled and no errors. The last pass draws straight to the screen: Vulkan's log lists
  float targets for passes 0-6 and none for pass 7.
- With HDR off the picture is grey and flat, as the README says. Between drivers they match at 93-100 dB
  (glcore) and about 61 dB (Metal). They were not run with HDR on, on an HDR display; they use the same
  passes as `hdr/curved`.
