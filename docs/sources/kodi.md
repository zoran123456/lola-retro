# The Kodi version: what it needs, and how it was checked

## What it needs

The Kodi port (`kodi/lola-retro`, PR #15 by sunlollyking, merged 2026-10-26) needs Kodi-side fixes. All of
them went into Kodi's Piers branch (22.x) by 2026-10-26, from GitHub xbmc/xbmc:

| PR | What it fixes |
|---|---|
| #29665 | parameters per pass |
| #29829 | the real texture size |
| #29845 | the frame count |
| #29906 | `#pragma parameter` lines |
| #29904 | the GLSL profile |
| #30057 | clamp_to_border on GLES |

Kodi 22.0 RC1 (2026-09-27) has none of them, so the README says RC2 or newer.

## Checked on macOS, 2026-10-26

**Setup.**

- Kodi build `kodi-20261023-989d5fac-retroplayer-22rc1-17540-arm64.dmg` (mirrors.kodi.tv/test-builds/osx/arm64),
  on the author's Mac (M4 Pro, BenQ RD280U at 3840×2560). It reports itself as 22.0 RC1, revision
  20261023-989d5facf7, and comes from garbear's retroplayer-22rc1 branch, which has the fixes.
- Game add-ons from Kodi's repository: Snes9x 1.63.0.64 and Genesis Plus GX 1.7.4.86. game.shader.presets
  22.1.4 is bundled in Kodi.app.
- The bundled game.shader.presets was copied to `~/Library/Application Support/Kodi/addons/`, `lola-retro`
  put into its `resources/glsl`, and all 30 presets added to `resources/ShaderPresetsGLSLP.xml`. Kodi then
  uses the copy: Addons.GetAddonDetails gives its path.

**Loading.** All 30 presets (curved and flat) run live in the Video Filter dialog with Sonic the Hedgehog
(Genesis Plus GX), with no errors in kodi.log. The only shader errors in the log came from Kodi's own
handheld lcd-grid-v2 shader. TV show broadcast (9 passes), Amiga 1084S and PC monitor were also looked at
full screen.

**Against RetroArch.** The test is SNES 240p Test Suite's menu, consumer-tv-composite.

- Kodi: Snes9x, full screen, the picture 3413×2560.
- RetroArch 1.22.2: bsnes 2014, Vulkan, 2880×2160 and 1792×1344.

The two match in geometry, blur, colour and mask. Kodi's picture brought down to 1792 has a mean of
86.4 / 108.4 / 140.7 against RetroArch's 86.4 / 109.2 / 140.7, and the two are 34.2 dB apart. That is about
what resampling alone leaves: RetroArch's 2880 → 1792 against its own 1792 is 37.5 dB. The Kodi pictures are
Kodi's own screenshots (Input.ExecuteAction "screenshot"), which on macOS read Kodi's back buffer
(`CScreenshotSurfaceGL::Read`, `xbmc/rendering/gl/ScreenshotSurfaceGL.cpp`).

## Kodi's screenshots are tagged BT.709

A first comparison, on 2026-10-26, showed Kodi darker: a mean of 77.6 / 100.8 / 135.0, with every palette
colour lower by exactly `sRGB_encode(v^2.4)` (Sonic's 33 → 21, 99 → 90, 206 → 203; the 240p Test Suite's
grey 107 → 99), with Nearest neighbour too. That was put down to Kodi, and v1.18's Kodi README said so. On
2026-10-27 it turned out to be the measurement:

- Kodi tags a screenshot with what it takes the display to show. For SDR wider than 1024 that is BT.709
  (`GetOutputColorMetadata`, `xbmc/rendering/capture/CaptureMetadata.cpp`), and FFmpeg writes it into the PNG
  (`xbmc/guilib/FFmpegImage.cpp`): a cICP chunk of 1/1/0/1 (BT.709 primaries and transfer, RGB, full range),
  cHRM (BT.709) and gAMA (1/2.2). RetroArch's screenshots have no colour chunks.
- The pictures were read with macOS's `sips`, converted to BMP. ImageIO takes the tag as
  `kCGColorSpaceITUR_709` and converts the picture to sRGB, which is the gamma 2.4 → sRGB curve. Untagged
  PNGs are not converted.
- Read with no colour management (the bytes of CGImage's data provider), Kodi's pixels are the core's: the
  grey is 107 / 105 / 107, and Sonic's palette keeps 33, 99, 138, 173, 206 and 239.

sunlollyking (PR #15, 2026-10-27) found the same on LibreELEC (GLES): Kodi's own screenshot of FCEUmm with
Nearest neighbour has exactly the core's colours. So Kodi draws the core's pixels unchanged, on macOS too,
and the port needs nothing for it.

To measure Kodi's screenshots, read their stored bytes, or drop the tag first. Tools that honour cICP
(ImageIO, so `sips` and Preview) convert them.

## On the NVIDIA Shield (game.shader.presets PR #47, 2026-10-28)

**Reported.** garbear tried PR #47 (six presets, curved and flat, 12 entries) on a Shield with GLES. All
of them compiled and rendered (NVIDIA's GLSL ES compiler is strict: it rejected an xBR pass in the same
add-on, not Lola). But scrolling onto the Lola Retro page of the Video Filter dialog took over a minute,
and Android then killed Kodi for running out of memory. sunlollyking's diagnosis: the dialog keeps the
renderer of every filter it has previewed, with all its framebuffers, until the game stops. Going
through all 17 categories on his laptop took Kodi's GPU memory from 77 to 580 MB, and closing the dialog
freed none of it. He is writing a Kodi fix that frees a renderer once its preview is off screen.

**Why Lola tips it over (worked out from the presets and Kodi's code).**

- Kodi gives every `float_framebuffer` pass a `GL_RGBA32F` texture, 16 bytes a pixel
  (`xbmc/cores/RetroPlayer/shaders/gl/ShaderPresetGL.cpp` and `gles/ShaderPresetGLES.cpp`, Piers).
  RetroArch's slang chains, where Lola is made and checked, use `R16G16B16A16_SFLOAT`, 8 bytes a pixel
  (`gfx/drivers_shader/shader_vulkan.c`, `shader_gl3.c`, `slang_process.c`). So each Lola target takes
  twice the memory, and twice the bandwidth, in Kodi.
- The full presets' beam pass is 8192 wide whatever the picture's size, so a small preview still has an
  8192 x 245 beam texture (NES): 31 MB in Kodi, about 70% of the preset's targets in a preview.
- Kodi doesn't allocate the last pass, so the targets are passes 0-6:

| Targets per preset, RGBA32F (MB) | NES 256x240 | SNES 256x224 | Game Boy 160x144 |
|---|---|---|---|
| full, preview 480x360 | 42-44 | 40-41 | 24-27 |
| full, picture 1440x1080 | 63-65 | 61-63 | 45-48 |
| lite (if ported), preview 480x360 | 12.5-12.7 | 11.7-11.8 | 5.5-7.4 |
| lite (if ported), picture 1440x1080 | 16-20 | 15-18 | 10 |

The 12 Lola entries on one page come to about 0.5 GB (NES, previews), on top of the renderers of the
pages before. The Shield TV (2019) has 2 GB of RAM, the Pro 3 GB, shared by the system, the GPU and
Kodi. With RGBA16F, as in RetroArch, the full presets would take half. The preview size (480x360) is an
assumption; the beam texture doesn't depend on it.

**Speed (worked out, not measured).** The Shield's Tegra X1 has 256 Maxwell cores at up to 1 GHz, about
0.5 TFLOPS FP32, and 25.6 GB/s of memory bandwidth (the 2019 X1+ is about 25% faster). That is about a
twelfth of the M4 Pro (6.5-6.9 TFLOPS, 273 GB/s). The full consumer-tv-composite at 1440x1080 takes 1.81
ms on the M4 Pro with RGBA16F ([lite-presets.md](lite-presets.md)), so about 22 ms on the Shield, more
with Kodi's RGBA32F, against 16.7 ms for a 60 Hz frame; lite (1.06 ms) about 13 ms, super lite (0.62 ms)
about 7.5 ms. In the dialog every preview runs its own 8192-wide beam pass each frame (0.60 ms on the
M4 Pro, so about 7 ms each on the Shield), which fits the minute it took to reach the page.

Sources: garbear and sunlollyking on https://github.com/kodi-game/game.shader.presets/pull/47; RAM and
the X1+ from CNX Software (https://www.cnx-software.com/2019/10/29/nvidia-launches-upgraded-shield-tv-with-tegra-x1-plus-processor/);
the X1's GPU clock and bandwidth from published figures (Wikipedia, Tegra), not checked against NVIDIA.

## Not found or not checked

- The screen itself was not measured, only the two programs' own frames.
- The Shield's frame rate with one Lola preset in a game: nobody has measured it yet.
- Not checked here: OpenGL ES (no glslang on the Mac), Linux and LibreELEC (the PR author tested those), and
  Android.

## Where the code uses it

- `tools/make_glsl.py` (`write_kodi`, `kodi_samplers`, `kodi_chain`): makes `kodi/lola-retro`.
- `tools/check_shaders.py` (`kodi_source`): compiles the passes as Kodi assembles them.
- The README in `kodi/lola-retro`, which is written by hand: install, macOS, differences.
