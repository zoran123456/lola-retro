# Lola Retro: notes for Claude

## Principles (from the author)

1. **Realism comes first**, not a fancy or impressive look. The shader simulates what the real chain and
   tube did: console encoder, cable, TV decoder, beam, mask, glass.
2. **A compromise needs a good reason**, for example a display that cannot show the real thing (a mask
   finer than its pixels). Say what the reason is, in the code comment and in the README.
3. **Where a compromise works better as its own option, it is a separate parameter**, off by default, so
   the presets stay realistic. Examples: Dither blend, Mask on screen pixels, Scanline smoothing.
4. **When sources disagree, trust them in this order:** spec sheets, service manuals and measurements;
   then photos of a real screen, which are good for the beam, line gaps and geometry but not for colour or
   brightness (the camera and the screen it is viewed on change both); last, how users remember it or
   see it on their own display. Where the display cannot show the real thing (a mask finer than its
   pixels, phosphor brightness in SDR, flicker at 60 Hz), the compromise shows what the eye saw on
   average, as No flicker does, not something that only looks good.

## Decisions

- `studio-monitor-composite` (Sony PVM-14L2) stays on auto phosphors (SMPTE-C on NTSC, EBU on PAL), as in
  v1.11.1, although Sony's PVM-L2 spec sheet lists P-22 phosphors. Leave it as it is unless the author asks.
- Scanline smoothing stays 0 by default: 1 is more correct (a screen pixel shows the average light over its
  area), but it moves the calibrated line contrast (PC monitor table, 1084S) by 2-3 points, so making it
  the default needs those calibrations checked again.
- RetroArch shows parameters with two decimals, so the ten parameters with steps of 0.005 (beam widths,
  curvature, corners, overscan, brightness, RF noise, antenna ghost) show their values in pairs. They stay
  as they are: every value can still be chosen, and rescaling them would break saved presets. New
  parameters get steps of 0.01 or more (Room reflection was moved to % for this, as LR_REFLECT).

## Workflow

- The author works on `main`: push there, no feature branches.
- Talk to the author in Croatian; texts for users (GitHub issues, Reddit, the libretro forum) in English.
- Write down what research finds, so it can be explained later why a value is used: `docs/sources/`, one note
  per topic, with the sources, what was worked out, what was not found and where the code uses it.
- Presets, the Amiberry, 86Box and Kodi ports and the Unity package are generated: change the slang passes and
  `tools/make_presets.py`, then run `tools/make_presets.py` and `tools/make_glsl.py`. `tools/check_shaders.py`
  compiles every pass (needs glslangValidator).
- Unity (`unity/`) is separate and on hold: don't regenerate it unless asked, and then with the author's
  toolchain (an old spirv-cross rewrites all of `LolaRetro.shader`). `tools/make_unity.py` must still know
  every parameter of `common.inc`, or it stops.
- Releases: four zips, each one `lola-retro/` folder, from `git archive` of `shaders/lola-retro`,
  `amiberry/lola-retro`, `86box/lola-retro` and `kodi/lola-retro`: `lola-retro-vX.zip`,
  `lola-retro-amiberry-vX.zip`, `lola-retro-86box-vX.zip`, `lola-retro-kodi-vX.zip`. The Unity package has its
  own numbers (1.12.0 exists), so RetroArch went from v1.11.2 to v1.13.
