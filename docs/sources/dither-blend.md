# Dither blend: how much composite blends

Worked out 2026-10-22 for a question on the libretro forum (Lola Retro thread): which Dither blend
(`LR_DBLEND`) on the RGB preset matches the composite preset. Used in the README (Optional: dither blend on
RGB) and in the Parameters table of `shaders/lola-retro/README.md`. Since 2026-10-24 the shader works the
same sums out itself for Dither blend auto (`LR_DBLEND_AUTO`, see the last section).

## What the two do

- Composite (`encode.inc`, `decode.inc`): Dither blend is not used. A 1-pixel stripe is a luma signal at
  half the pixel clock. The console's luma trap (Luma trap in the console, 0.75 in the TV presets) and the
  TV's trap (0.92 deep) take out a band around the colour subcarrier, so stripes near the subcarrier go and
  stripes far from it stay. The colour of the stripes always goes: the chroma band is narrow (0.6 MHz NTSC,
  0.8 PAL).
- Dither blend (`common.inc`, DBW): takes out the given share of the part that alternates from one console
  pixel to the next. On RGB from R, G and B alike (brightness and colour), on S-Video from luma.

So the two match only in brightness. Composite takes out all of the stripes' colour; Dither blend the same
share of both.

## Worked out

The gain of each filter at the stripe's frequency (half the pixel clock), from the filter values in the
code. All are Gaussians with `exp(-2 pi^2 (0.1325 / fc)^2 f^2)` (-3 dB at fc):

- console trap: `1 - trap * (G(f - fsc, 0.5) + G(f + fsc, 0.5))`
- TV luma, composite: `(1 + s) G(f, fcY) - s G(f, fcY / 2.5)`, s = 1.4 x Sharpness (0.35), fcY 3.3 NTSC,
  4.2 PAL, minus the trap `0.92 * hf * (G(f - fsc, fcC) + G(f + fsc, fcC))`, hf the luma gain at fsc
- RGB: `G(f, 6.5)`; S-Video luma: as composite luma with fcY 4.6 NTSC, 5.0 PAL, no trap

Dither blend matching composite is 1 - composite / RGB (or / S-Video):

| Mode (pixel clock) | NTSC, vs RGB | NTSC, vs S-Video | PAL, vs RGB | PAL, vs S-Video |
|---|---|---|---|---|
| 256 wide (5.37 MHz: NES, SNES, Master System, Mega Drive H32, PS1 256) | 0.47 | 0.54 | 0.03 | 0.15 |
| 320 wide (6.71 MHz: PS1 320, Mega Drive H40) | 0.95 | 0.96 | 0.42 | 0.51 |
| 368 wide (7.67 MHz: PS1 368) | 0.97 | | 0.79 | |

Rounded for the README: NTSC 1 and 0.5, PAL about 0.45 and 0.1. PAL blends less because its subcarrier,
4.43 MHz, is further from stripes at 2.7 and 3.3 MHz than NTSC's 3.58 MHz.

The same for other settings (NTSC, vs RGB): Luma trap in the console 0 (an early Mega Drive): 0.30 and
0.83; 1: 0.53 and 0.99. Comb filter on: 0.13 and 0.65 (the comb keeps vertical stripes in luma, they do
not change from line to line).

This is what the shader's composite does, not a measurement of a real TV. The beam and the mask act on
both pictures alike, so they are left out.

## Dither blend auto (2026-10-24)

Asked for on the forum (Arviel, JHorbach1): Dither blend set by itself, per system. Dither blend is a
compromise (no TV blended dither on RGB), so it stays a separate parameter, off by default; auto only takes its
amount from the shader's composite model instead of a number the user picks.

What it does (`ditherBlend` in `common.inc`, used by `decode.inc` for RGB and `encode.inc` for S-Video):

- Luma share: `1 - composite / path in use` at the pattern's frequency, the sums above, from the preset's own
  Luma trap in the console, Sharpness and Comb filter. The path in use: RGB `G(f, 6.5)`, S-Video its luma filter.
- Colour share 1. Composite's chroma band (0.6 MHz NTSC, 0.8 PAL) takes all of a 1-pixel pattern's colour (the
  pattern is at 2.5 MHz or more). On S-Video the encoder's 1.5 MHz and the decoder's 0.9 MHz chroma filters
  already leave about 1.5% of it, so auto only touches luma there. Dither blend by hand takes the same share of
  luma and colour, as before.
- Only on 15 kHz TV rasters (scan mode 0): the consoles and the Amiga, most of whose players used composite or
  RF. Not on arcade boards (Console timing 8: RGB monitors, never composite) or computer monitors (VGA, 24 kHz,
  X68000, Frames over 300 lines 2); there Dither blend stays as set.
- Pattern frequency: half of `t.pclk / t.scale`. For every TV timing the nominal width spans the same active
  line (about 47.7 us), so `t.pclk` is about 0.021 MHz per frame pixel whichever console the shader guesses
  (SNES, Mega Drive, PlayStation, arcade rows 0.02097; PlayStation 2 0.02109). A wrong console guess changes the
  subcarrier rhythm, not this. Cores that crop or add borders do change it, as they change composite:
  NES cropped to 240 px reads 5.03 MHz (NTSC share 0.30 instead of 0.47), H32 with borders (284 px) 5.96 MHz
  (0.75), H40 with borders (348 px) 7.30 MHz (0.98 instead of 0.95; PAL 0.69 instead of 0.44).
- PAL or NTSC: `t.pal` from `getTiming`, TV standard (auto: `OriginalFPS`, the core's frame rate, under 52 Hz
  is PAL where RetroArch passes it, from 1.20 with `_HAS_FRAMETIME_UNIFORMS`; otherwise the line count, which
  reads PAL games with 224 or 240 lines as NTSC: NTSC share 0.47 instead of 0.03 for 256-wide). First written
  as a helper of its own (`palByRate`), folded into `t.pal` on 2026-10-24. The rates per core were measured
  in [core-frame-rates.md](core-frame-rates.md): PAL cores 49.7 to 50.2, 60 Hz ones 54.7 or more; exactly 60
  is left to the line count. The ports (Amiberry, 86Box) have no such uniform and keep the line count.

Checked with a ctypes render of the whole chain on Apple's OpenGL (decoder output; amplitude of the stripes'
fundamental; grey stripes 64/191 for luma, two colours of about equal luma for colour), against the same TV
switched to composite:

| Case | RGB, no blend | Auto | Composite |
|---|---|---|---|
| 256x224 NTSC, luma / colour | 0.314 / 0.403 | 0.166 / 0.000 | 0.169 / 0.000 |
| 320x224 NTSC, luma | 0.304 | 0.0155 | 0.0167 |
| 512x224 NTSC, luma | 0.263 | 0.183 | 0.185 |
| 640x224 NTSC, luma | 0.234 | 0.120 | 0.131 |
| 256x224 at 50.007 Hz, luma | 0.314 | 0.307 | 0.311 |
| 256x224 S-Video (Trinitron), luma | | 0.163 | 0.163 |
| 320x224 Amiga timing, luma | 0.300 | 0.0065 | 0.0070 |
| 256x224 lite / super lite, luma | | 0.166 / 0.164 | 0.169 / 0.167 |

(Measured again after the RGB amplifier and the console trap were made to follow their filters, see
composite-luma-bandwidth.md; the first measurements had S-Video 6% above composite, super lite's composite 17%
above the full chain's, and 512 and 640 wide off by 20% and more, all from those two.) Dither blend 0.47 by hand
on the 256-wide frame leaves 0.213 of the colour. Arcade timing with auto renders the same as without. Without
`_HAS_FRAMETIME_UNIFORMS`, at 60.099 Hz, and at 50 Hz with TV standard NTSC by hand the 256x224 frame stays NTSC.

Not right yet:

- 640 wide: composite passes about 10% more of a 1-pixel stripe than its filters give, so auto takes out a little
  more than the composite preset (0.120 against 0.131). The encoder has 1280 samples per line, 2 per pixel at
  640 wide, and the stripe's third harmonic folds back onto the stripe; more samples would cost every preset.
- Whether composite's luma filter is right above 4 MHz at all (Kirby's Dream Land 3's 512-wide transparency is
  remembered as blended): composite-luma-bandwidth.md, where the datasheets say it is.
- Patterns wider than one pixel, and composite's rainbow, are not part of it.
