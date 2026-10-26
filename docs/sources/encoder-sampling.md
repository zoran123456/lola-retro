# Encoder sampling: moving detail at widths that don't divide 1280

## The report

Libretro forum, post 46 (Tatsuya79, 2026-10-25,
https://forums.libretro.com/t/lola-retro-crt-shader-simulating-the-full-analog-signal-chain/51367/46): pixels
shimmer while ESP Galuda (FBNeo) scrolls vertically, on composite and S-Video but not on RGB.

- ESP Galuda runs on IGS PGM, 448×224 (the PGM's video mode as MAME and FBNeo emulate it; not checked in their source for this note).
- The game is rotated (tate). RetroArch rotates the picture after the shader chain, so the shader gets the
  frame unrotated, and the game's vertical scrolling runs along the lines.

## The cause

The TV presets run the encoder at a fixed 1280 samples per line (ENC_SAMPLES in common.inc). For each
sample, `encYUV` in encode.inc took the luma of the one source pixel under the sample's centre. That gives
a whole number of samples per pixel only at 256 (5), 320 (4) and 640 (2) pixels wide. At other widths a
pixel got the whole number below or above, depending on where it lay:

- 448 (IGS PGM): 2 or 3 samples of 2.86;
- 384 (CPS1/2): 3 or 4 of 3.33;
- 512 (SNES hires): 2 or 3 of 2.5;
- 368 (PS1): 3 or 4 of 3.48.

The decoder's filters keep that sum, so a 1-pixel detail moving along the line changed its energy from
frame to frame (worked out with a Python model of the encoder and the S-Video luma filter):

| Width | Energy of a 1-pixel detail |
|---|---|
| 448 | 0.70-1.05 |
| 384 | 0.90-1.20 |
| 512 | 0.80-1.20 |

RGB never had it: the decoder integrates the source pixels as flat steps (gaussCdf in decode.inc). The
presets that work at 4 samples per pixel (the PC and Amiga presets, `systems/arcade-15khz`) never had it
either. The encoder's other paths already integrated over the pixel steps:

- the chroma filter: taps 0.4 sigma apart, or integrated in super lite;
- the luma trap: Gauss-Legendre points per pixel;
- the TV show's tape copies: their Gaussian integrated over the pixels.

## The fix

The console's signal is continuous, and its pixels are flat steps. So a sample, which stands for 1/1280 of
the line, now holds the average of the signal over its own span: frame pixels n·ppx to (n+1)·ppx, where ppx
is frame pixels per sample (`spanLuma` in encode.inc).

- Up to 1.5 pixels per sample, the span covers up to three pixels, each weighted by its overlap.
- A wider frame (an upscaled one over 1920 wide) has already been averaged across by the native pass, over
  vBox pixels (native.slang), so one read is enough, as before.
- Dither blend takes its correction from the console pixel under the sample. When the span reaches into
  the next console pixel, the correction is now mixed from the two in the same shares as the luma. With the
  luma averaged but the correction not, a 1-pixel pattern would have kept part of its stripes.

At 256, 320 and 640 wide, and at 4 samples per pixel, the spans end on pixel edges, so the result is the
same as one read.

## Measured

### Full chain, Python model

Run in the session scratchpad. The chain:

1. The encoder.
2. The decoder's luma filter: S-Video 4.6 MHz, Sharpness 0.35.
3. Tube gamma 2.4.
4. The beam's horizontal spot, with the shader's taps and linear reads: Beam width 0.2 / 0.44, Horizontal
   focus 0.5.

Content: a 1-pixel white line on black, moved over 24 positions. The table gives how much its light on the
screen varies.

| Width | Before | Now | Composite, NTSC trap (3.3 MHz): before | Now |
|---|---|---|---|---|
| 256, 320 | 0% | 0% | 0% | 0% |
| 384 | 31% | 2.3% | 34% | 1.5% |
| 448 | 52% | 4.8% | 70% | 7.8% |
| 512 | 52% | 0% | 70% | 0% |

PAL S-Video (5.0 MHz) at 448: 49% before, 6.1% now.

The rest doesn't come from the encoder. The decoded line of a 1-pixel detail is a peak about 3 samples
wide. The beam reads it with linear filtering before the tube's gamma, so its light still depends a little
on where the peak falls between samples. At 512 a pixel can only sit two ways, and both give the same light.

The same cause makes such a line 1% darker at 256 wide (always the same) than the model at 8× the samples
gives, and 2-7% darker at 384-512 wide. A real tube has neither. Removing them would mean changing how the
beam pass reads the decoded line, which costs GPU time and moves the calibrations. Not done.

### The encode pass on the GPU

The encode pass alone, rendered with macOS GL 4.1 (ctypes + CGL) on an M4 Pro, comparing v1.17's
encode.inc with the new one.

**Whole samples per pixel.** Random frames 256, 320 and 640 wide, with the presets consumer-tv-composite,
trinitron-s-video (also with Dither blend 1), studio-monitor-composite and tv-show-broadcast, and super
lite composite and S-Video. Largest difference from v1.17:

- 320 and 640 wide: 0;
- 256 wide: 1.5e-5 (0.2 pixels per sample is not exact in float);
- 256 wide with Dither blend: 1.7e-5.

**RF (old-tv-rf).** Up to 0.057, at one sample per edge of the echo. The echo is 0.8 µs late, 21.5
samples at 320 wide, so its edges now fall between two samples, half in each, instead of on the next
whole sample.

**448 wide.** A 1-pixel white line moved over 24 positions, the S-Video luma summed along the line: v1.17
gives 0.700-1.050, now 1.000-1.000. Dither blend 1 on 1-pixel stripes: the luma stays flat at 0.5000, as in
v1.17.

**Cost of the encode pass** (1280×224):

| Pass | 320 wide | 448 wide |
|---|---|---|
| full | 0.120 → 0.122 ms | 0.134 → 0.137 ms |
| super lite | 0.107 → 0.110 ms | 0.126 → 0.131 ms |

It is a fix rather than a realism feature, and it costs next to nothing, so super lite has it too
(lite-presets.md).

## Not done

- Not run in RetroArch with ESP Galuda; the forum reporter can confirm it.
- glslangValidator is not installed on the author's Mac, so the passes were compiled with the macOS GL
  compiler only (slang passes turned into GLSL 4.10, and the Amiberry and 86Box ports as
  tools/check_shaders.py assembles them).

## Where the code uses it

- `shaders/lola-retro/shaders/encode.inc`:
  - `spanLuma`;
  - `encYUV`: the luma, and the Dither blend's shares.
- `shaders/lola-retro/shaders/native.slang`, `vBox`: frames over 1.5 pixels per sample.
- The Amiberry and 86Box `encode.glsl` (tools/make_glsl.py).
