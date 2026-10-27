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

The two match in geometry, blur, colour and mask, but Kodi is darker: the mean of the picture is 77.6 / 100.8
/ 135.0 against 86.4 / 109.2 / 140.7. The resolution doesn't explain it: RetroArch at 2880 brought down to
1792 has the same mean as at 1792 (86.2 / 109.0 / 140.6). Afterglow doesn't either: RetroArch's lite preset
and LR_PERSIST 0 give the same mean.

## Kodi's gamma conversion

Kodi does the same without a shader:

- With Nearest neighbour, the menu's grey (107 in RetroArch) comes out as 99 / 97 / 99 in Kodi.
- With the same core in both (Genesis Plus GX, Sonic's title screen), every palette colour goes down in Kodi:
  33 → 21, 99 → 90, 138 → 132, 140 → 134, 173 → 168, 206 → 203, 239 → 238.

That is exactly `sRGB_encode(v^2.4)`, which predicts 20.8, 90.4, 131.6, 133.7, 168.5, 203.3 and 238.1. In other
words, Kodi takes the game's picture as gamma 2.4 (BT.1886) and converts it to the sRGB curve.

With that conversion applied to RetroArch's picture, Kodi (3413 → 2880) matches RetroArch at 2880 at 34.2 dB,
up from 28.6. That is about what resampling alone leaves: RetroArch's 2880 → 1792 against its own 1792 is
37.5 dB. So the port gives RetroArch's picture, and Kodi darkens it as it darkens every game.

**It happens inside Kodi.** The Kodi numbers come from Kodi's own screenshot (Input.ExecuteAction
"screenshot"). On macOS that reads Kodi's back buffer: `CScreenshotSurfaceGL::Read` does `glReadBuffer(GL_BACK)`
and glReadPixels (`xbmc/rendering/gl/ScreenshotSurfaceGL.cpp`, registered in `xbmc/windowing/osx/WinSystemOSX.mm`,
Piers branch, read 2026-10-27). So the values are already lower in Kodi's frame, before macOS composites the
window and matches its colours to the display.

**What the Kodi side says.** sunlollyking (PR #15, 2026-10-26): it isn't intended. RetroPlayer draws the
core's pixels with no gamma step; he thought macOS colour-matches Kodi's window, since Kodi doesn't set a
colour space on it. The screenshot rules that out as the whole cause. He advised leaving the presets as they
are, because undoing it in the last pass would make them wrong on Linux and LibreELEC, so the port does not
undo it.

## Not found or not checked

- Where in Kodi's GL path the conversion happens, and whether Kodi does it on other systems too, was not
  found.
- Not checked here: OpenGL ES (no glslang on the Mac), Linux and LibreELEC (the PR author tested those), and
  Android.

## Where the code uses it

- `tools/make_glsl.py` (`write_kodi`, `kodi_samplers`, `kodi_chain`): makes `kodi/lola-retro`.
- `tools/check_shaders.py` (`kodi_source`): compiles the passes as Kodi assembles them.
- The README in `kodi/lola-retro`, which is written by hand: install, macOS, differences.
