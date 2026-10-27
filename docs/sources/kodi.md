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

## Not found or not checked

- The screen itself was not measured, only the two programs' own frames.
- Not checked here: OpenGL ES (no glslang on the Mac), Linux and LibreELEC (the PR author tested those), and
  Android.

## Where the code uses it

- `tools/make_glsl.py` (`write_kodi`, `kodi_samplers`, `kodi_chain`): makes `kodi/lola-retro`.
- `tools/check_shaders.py` (`kodi_source`): compiles the passes as Kodi assembles them.
- The README in `kodi/lola-retro`, which is written by hand: install, macOS, differences.
