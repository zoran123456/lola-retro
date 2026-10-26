# Lite and super lite presets: what the chain costs and what can go

Measured 2026-10-21/22 for issue #12 (a request for presets that run on older Android phones with Mali
GPUs). All numbers here are measurements on this project's own passes, not from outside sources; what was
worked out from them, rather than measured, is marked as such.

## How it was measured

- A small harness ran the presets' pass chains the way RetroArch runs them (pass sizes from the scale
  types, filters and wrap modes of the reading pass, float targets in RGBA16F, feedback, the last pass in 8
  bits at the viewport size), on macOS OpenGL 4.1 through ctypes, with the slang passes turned into GLSL
  4.10. The harness is not in the repository.
- GPU: Apple M4 Pro (16-core GPU). Each pass timed three ways that agreed: GL timer queries inside whole
  frames, the pass drawn 30-60 times on its own into two targets in turn, and the same into one target with
  additive blending (no per-pass overhead). The tables use the second.
- A slow device: the Apple Software Renderer (one CPU core), one frame at 640x480.
- Reference shaders from RetroArch's own slang library, run by the same harness, whose behaviour on phones
  is known from users: zfast-crt, crt-geom-mini, crt-guest-advanced(-fastest), crt-royale and others.
- The picture: each lite preset against its full preset on the same frame, PSNR over the 8-bit output, and
  crops side by side at 2-4x zoom. Test frames: the repository's test-images, plus synthetic desktop
  frames (1-pixel lines, checkerboards, bitmap text) at 640x480, 1024x768, 720x568, 640x256, 768x512 and
  512x512 for the sharp monitors.

## Where the time goes (full chain, consumer-tv-composite, ms)

| Pass | 1440x1080 | 960x720 |
|---|---|---|
| encode (1280 x 224) | 0.13 | 0.13 |
| decode (1280 x 224) | 0.35 | 0.35 |
| beam (8192 x 230) | 0.60 | 0.59 |
| crt (screen) | 0.48 | 0.21 |
| native, glow-h, glow-v, present | 0.20 | 0.17 |
| frame | 1.77 | 1.46 |

The beam pass was the largest in every preset (35-60% of the frame; 1.2 ms for a 448-line interlaced
frame, 1.9 ms for 1024x768 on the PC monitor) and does not shrink with the screen. The frame for other
presets at 1440x1080: RF 1.89, S-Video 1.64, SCART RGB 1.38, TV show 2.26, PC monitor (320x200) 0.96,
1084S 1.49, PlayStation 640x448i 3.19.

The same frame through the reference shaders (1440x1080, ms): zfast-crt 0.04, crt-geom-mini 0.09,
guest-advanced-fastest 0.18, crt-easymode-halation 0.40, crt-royale 0.62, guest-advanced 0.85. The full
composite chain costs about 2x guest-advanced and 3x crt-royale.

On the software renderer (640x480, one frame): zfast-crt 11 ms, crt-geom-mini 35 ms, guest-fastest 0.54 s,
guest-advanced 5.4 s, crt-royale 6.3 s, the lite composite chain 11.9 s, of which the decoder 8.1 s (its
tap loops). The full chain did not finish: with the scenes of Around the tube in crt.inc, the renderer's
shader compiler ran for more than 10 minutes on the CRT pass, 15 s without them. (The M4's GL compiler
needs 2.7 s for the whole chain either way.)

## What was tried

Against the full preset, consumer-tv-composite at 1440x1080 unless noted:

| Change | Saves (ms) | Picture (PSNR) | In lite |
|---|---|---|---|
| beam pass one sample per screen pixel instead of 8192 | 0.47 | 57-72 dB on TV presets | yes |
| the same, two samples per pixel | 0.37 | 61-74 dB | for tubes in mm |
| CRT pass writes the screen (present folded in) | 0.06 | identical | yes |
| no afterglow | 0.07 | identical on a still frame | yes |
| scenes code compiled out of the CRT pass | 0.02 | identical | yes |
| beam taps 2 sigma apart instead of 1 | 0.04 | 60 dB | no: small gain, the sum is no longer exact |
| a cheaper dither (gamma 2.2 code + noise) | 0.02 | 51 dB | no: small gain |
| mask from one point instead of 2x2 | 0.01 | 33 dB (moire) | no |
| encoder and decoder at 640 samples per line | 0.30 | 38-51 dB, colour fringes shift a little | no (a compromise, see below) |
| the same at 512 | 0.36 | 31-43 dB, edges visibly greener | no |
| No flicker off | 0.08 | 39 dB, dot crawl moves | no |

Beam width per screen pixel, by preset type (PSNR against the full preset):

| Preset | 1 per pixel | 2 per pixel |
|---|---|---|
| TV presets (composite, TV show, PS1 interlaced), 1440x1080 and 960x720 | 57-72 dB | 61-74 dB |
| studio RGB | 48-54 dB | 58-63 dB |
| PC monitor, 320x200 up to 1024x768 | 39-60 dB | 50-68 dB |
| pc-monitor-vga-extreme, 1024x768 | 24-30 dB | 35-42 dB |
| 1084S, hires 640x256 and 720x568 | 40-52 dB | 50-57 dB |
| X68000, 512x512 and 768x512 | 40-55 dB | 51-61 dB |

Even the lowest numbers (extreme at x1, the 1084S hires at 640x480 at x1) show no difference by eye at 3-4x
zoom; the PSNR comes from edges moved by a fraction of a pixel. The tubes in mm get two samples anyway:
their spots are narrow next to the pixels of hires and 31 kHz modes.

## The lite presets as made

Every lite preset (62) against its full preset: 52-66 dB at 1440x1080, 44-66 dB at 640x480 (lowest: PC-98
and Dreamcast on sharp 640x480 desktop frames, N64 and Saturn).

In RetroArch itself (1.22.2, macOS, a temporary config, the built-in image viewer, a screenshot after 90
frames): every lite preset compiles and runs on Metal with no errors in the log, and a selection (SNES,
TV show, PC monitor, X68000) on glcore and Vulkan. Lite against full in the same RetroArch, same window:
51-65 dB, except the presets with RF snow (old-tv-rf 38-55 dB, tv-show-broadcast 45-58 dB): the snow is
random per frame and the full preset's afterglow smears it, the picture under it is the same.

Time per frame (ms, full -> lite):

| Preset | 1440x1080 | 960x720 | 640x480 |
|---|---|---|---|
| consumer-tv-composite | 1.81 -> 1.07 | 1.47 -> 0.81 | 1.34 -> 0.69 |
| old-tv-rf | 1.80 -> 1.09 | 1.53 -> 0.85 | 1.37 -> 0.72 |
| trinitron-s-video | 1.64 -> 0.88 | 1.30 -> 0.62 | 1.14 -> 0.50 |
| consumer-tv-scart-rgb | 1.39 -> 0.65 | 1.04 -> 0.38 | 0.90 -> 0.26 |
| tv-show-broadcast | 2.26 -> 1.25 | 1.79 -> 0.92 | 1.59 -> 0.72 |
| amiga-1084s | 1.47 -> 0.82 | 1.17 -> 0.46 | 1.01 -> 0.34 |
| x68000-monitor (768x512) | 2.72 -> 1.55 | 2.36 -> 1.06 | 2.14 -> 0.83 |
| pc-monitor-vga (320x200) | 0.96 -> 0.58 | 0.67 -> 0.36 | 0.51 -> 0.27 |
| playstation (640x448i) | 3.10 -> 1.85 | 2.69 -> 1.50 | 2.52 -> 1.30 |

## Super lite

For GPUs too weak for lite: as little GPU time as the model allows, with compromises that change the
picture a little, each where it shows least. Measured the same way.

The CRT pass of lite, by parts (consumer-tv-composite, 1440x1080, each part switched off in turn, ms):
vertical beam sum 0.12, mask (2x2 points) 0.07, glass glow 0.02, phosphor matrix 0.02, dither 0.01,
shoulder 0.01, the rest (geometry, setup, writing the screen) 0.07; 0.34 in all.

| Change on top of lite | Saves (ms, 1440x1080) | Picture | In super lite |
|---|---|---|---|
| no native pass (upscaled frames read one row per line) | 0.03-0.04 | the same at 1x | yes |
| encoder: chroma filter integrated over the pixel steps (each pixel read once, 3-8 reads instead of 17), luma trap one read per pixel with the pixel's sinc instead of 25 taps (since 2026-10-24 the full chain does the same, with 3 Gauss-Legendre points per pixel instead of the sinc: composite-luma-bandwidth.md) | 0.03-0.05 | 44 dB at 1280 samples | yes |
| decoder works out every other sample (taps still on every sample) | 0.17 | 41-50 dB on composite, 43 dB on RGB | yes, not on the 1084S |
| beam pass taps 2 dark-spot widths apart | 0.04 | dark detail up to 1.5% brighter | yes |
| beam pass one sample per screen pixel on the tubes in mm too | 0.1-0.4 (hires) | 47-51 dB | yes |
| CRT pass: 3 beam lines (the nearest and one on each side) instead of 4 | 0.03 | the line left out is over 3.4 spot widths away | yes |
| CRT pass: cheaper dither (noise added to the 8-bit code) | 0.01 | 51 dB | yes |
| no misconvergence | 0.00 | 35 dB on RGB | no: costs nothing |
| mask from one point with edges widened by the pixel's footprint | 0.03 | 38 dB on the 1084S (2 px per triad at 1080p): its pattern changes | no |
| encoder and decoder at 640 samples | 0.12 more than the half-rate decoder | the Mega Drive waterfall's rainbow turns greener (a 1-pixel stripe's third harmonic folds down next to the subcarrier) | no |
| encoder and decoder at 960 | as the half-rate decoder | 40-43 dB at 320 and 256 wide, 27 dB at 640 wide (1.5 samples per pixel) | no |
| glass glow from mipmaps of the beam texture instead of two passes | about 0.07 (the passes' overhead) | the beam texture is about 6x wider than tall: one mip level blurs far too much vertically | no |
| decoder on the 1084S at half rate | 0.2 on hires | 29 dB on hires (its beam reads the signal as a smooth curve) | no |
| the encoder multiplies its signal by the decoder's reference subcarrier (products, averaged over the No flicker frames); the decoder only low-passes them, and its trap is the band of the average signal around the subcarrier. The same sums, so the same picture | decoder 0.18 -> 0.08 (SNES), 0.35 -> 0.16 (PS1 640x448i); encoder +0.005 | 65-74 dB against super lite without it (rounding) | yes |
| the decoder's Gaussian weights by recurrence instead of an exp at every tap | none on the M4 | the same | yes: on the software renderer the PS1 decoder took 4.8 -> 3.1 s (SNES unchanged), so it should help GPUs where exp is slow |
| RF and TV show (2026-10-24): no IF filter ([composite-luma-bandwidth.md](composite-luma-bandwidth.md)). A shorter form of it (bands cut at 2 sigma, the ones weaker than 0.03 left out) was tried and dropped: super lite comes first for speed | the filter would cost old-tv-rf 0.79 -> 0.97 ms, tv-show-broadcast 0.94 -> 1.30 (whole frame) | 512- and 640-wide stripes get through on RF and the TV show, as before the filter | yes (left out) |

Not a compromise, but also in super lite: from 2026-10-26 the encoder's luma is the average over each sample's
span instead of one read at its centre ([encoder-sampling.md](encoder-sampling.md)). It costs the encode pass
0.003-0.005 ms (1280x224), and without it moving detail at 384, 448 and 512 wide shimmers.

On the software renderer (one CPU core, 640x480, one frame), super lite before and after the last two:
SNES 10.7 -> 8.7 s (decoder 7.3 -> 5.2 s), PlayStation 640x448i 16.4 -> 8.9 s (decoder 10.6 -> 3.1 s). The
decoder's own Timing (getTiming at every pixel) costs 0.3 s of the SNES's 5.2 s there and nothing measurable
on the M4: left as it is.

The super lite presets as made, against the full presets (all 62, one frame each): 37.5-51 dB at
1440x1080 (lowest: N64, Saturn and Dreamcast on their 640x480 test frames, S-Video), 30.8-51 dB at 640x480
(lowest: PC-98 on a sharp 640x480 desktop, where 1-pixel stripes on a screen narrower than the frame come
out as their average). The Mega Drive waterfall's rainbow and the blended dithering look as in the full
preset at 2x zoom. In RetroArch (1.22.2, as for lite), with the decoder products: every super lite preset
compiles and runs on Metal with no errors in the log, and SNES, TV show, PC monitor and X68000 on glcore and
Vulkan; against the full presets in the same RetroArch, 37.8-51.6 dB on Metal, 44-51.6 dB on glcore and
Vulkan, as before the products.

Time per frame (ms, full / lite / super lite):

| Preset | 1440x1080 | 960x720 | 640x480 |
|---|---|---|---|
| consumer-tv-composite | 1.81 / 1.06 / 0.62 | 1.49 / 0.82 / 0.41 | 1.34 / 0.68 / 0.31 |
| old-tv-rf | 1.84 / 1.06 / 0.67 | 1.48 / 0.85 / 0.47 | 1.37 / 0.72 / 0.37 |
| trinitron-s-video | 1.62 / 0.87 / 0.54 | 1.25 / 0.65 / 0.34 | 1.14 / 0.51 / 0.24 |
| consumer-tv-scart-rgb | 1.37 / 0.65 / 0.52 | 1.05 / 0.39 / 0.29 | 0.89 / 0.27 / 0.19 |
| tv-show-broadcast | 2.23 / 1.30 / 0.89 | 1.82 / 0.94 / 0.57 | 1.59 / 0.73 / 0.41 |
| amiga-1084s | 1.50 / 0.82 / 0.57 | 1.13 / 0.47 / 0.31 | 1.01 / 0.34 / 0.24 |
| x68000-monitor (768x512) | 2.69 / 1.53 / 0.95 | 2.27 / 1.04 / 0.59 | 2.15 / 0.83 / 0.46 |
| pc-monitor-vga (320x200) | 0.96 / 0.58 / 0.42 | 0.64 / 0.35 / 0.25 | 0.51 / 0.34 / 0.21 |
| pc-monitor-vga (1024x768) | 3.89 / 2.32 / 1.32 | 3.42 / 1.75 / 0.98 | 3.24 / 1.52 / 0.83 |
| playstation (640x448i) | 3.12 / 1.84 / 1.08 | 2.70 / 1.45 / 0.77 | 2.46 / 1.28 / 0.61 |

Where super lite's time goes (consumer-tv-composite, 1440x1080, ms): encoder 0.09, decoder 0.08, the two
glow passes 0.07 (mostly the cost of a pass), beam 0.07, CRT pass 0.31; at 960x720 the CRT pass (0.15) is
still the largest. Ideas not done: glass glow without its two passes, mediump precision in the CRT and beam
passes (faster on Mali, nothing to measure it on here).

## Phones (worked out, not measured)

No Mali GPU was measured. From published throughput figures, a budget Mali of the Mali-G52 MC2 class is
roughly 50-100x slower than the M4 Pro's GPU, which would put the full composite chain at 720p at about
70-140 ms a frame, lite at 40-75 ms, super lite at 20-40 ms, and guest-advanced-fastest at 6-12 ms. Things the M4 does not show and
that should favour the lite presets on phones more than measured here: the full chain's beam texture is
8192 wide (OpenGL ES 3.0 only promises 2048), and lite moves about a third as much render-target data
(estimated from the target sizes). Arm's Mali Offline Compiler would give cycle and register counts per
pass for real Mali GPUs.

## Reported by users

### Intel Graphics in a Core Ultra 5 225U (the author's laptop, 2026-10-22)

Measured, not reported: see [windows-test.md](windows-test.md). At 1600x1200 on Vulkan, the presets' own
cost in ms (full / lite / super lite): consumer-tv-composite 6.58 / 3.42 / 2.48, consumer-tv-scart-rgb
5.42 / 2.19 / 1.68, trinitron-s-video 6.03 / 2.93 / 2.11. About 3.3 times slower than the M4 Pro per pixel.

### AMD Radeon 780M at 4K (issue #14, FARL555, 2026-10-22)

Minisforum mini PC, Ryzen 7 8745H with Radeon 780M graphics, SteamOS, RetroArch 1.22.2 (RetroDeck),
SwanStation, a 4K TV, Lola Retro v1.15. GPU usage with `flat/trinitron-s-video` (full / lite / super lite):
**70% / 60% / 45%**. The internal resolution of this test was not given (the same report tried 1x to 6x).

The hardware, from published figures (not measured here):

| | Radeon 780M (8745H) | Apple M4 Pro, 16-core GPU (this project's measurements) |
|---|---|---|
| GPU | 12 compute units, 768 shaders, up to 2600 MHz (AMD's listing for the 8745HS; the 8745H runs at slightly lower power) | 16 cores |
| FP32 | about 4.0 TFLOPS (768 x 2 x 2.6 GHz; Notebookcheck's iGPU benchmark: 4,045 GFLOPS) | about 6.5-6.9 TFLOPS |
| Memory | the system's DDR5, shared with the CPU: about 90 GB/s if the mini PC has dual-channel DDR5-5600 (not stated) | 273 GB/s |

Worked out, not measured: the 780M has about 0.6 times the M4 Pro's arithmetic and a third of its memory
bandwidth, so the chain should take roughly 2-3 times as long on it. That is still 25-50 times the budget
Mali estimated above: a desktop-class iGPU, not a weak device.

How to read the percentages (inferred):
- GPU usage is the share of time the GPU is busy at the clock it runs at. At 60 Hz, 70% would be about
  12 ms of the 16.7 ms frame, 60% about 10 ms, 45% about 7.5 ms, but only if the clock stayed the same; the
  GPU lowers its clock when there is less to do, which makes the lighter presets look closer to the full
  one than they are. The share also holds SwanStation's own rendering, the same in all three.
- At 4K the CRT pass (once per screen pixel, the same in lite) is a larger part of the frame than at the
  1080p measured here, so lite gains less: 70% to 60% fits that. On the M4 Pro at 1440x1080 the same preset
  takes 1.62 / 0.87 / 0.54 ms.
- Comparable numbers would need the GPU clock next to each percentage (SteamOS's performance overlay shows
  it), or the clock fixed, and the internal resolution.

Sources: AMD Ryzen 7 8745HS product page (https://www.amd.com/zh-tw/products/processors/laptop/ryzen/8000-series/amd-ryzen-7-8745hs.html);
Notebookcheck, Ryzen 7 8745HS (https://www.notebookcheck.com/AMD-Ryzen-7-8745HS-Prozessor-Benchmarks-und-Specs.1007249.0.html);
on the 8745H against the 8745HS (https://www.turbovs.com/review/amd-ryzen-7-8745h-9134); M4 Pro GPU figures
from Low End Mac (https://lowendmac.com/2025/apple-silicon-m4-pro-chip-specs/) and EatYourBytes
(https://www.eatyourbytes.com/applecpu-detail/apple-m4-pro-16-core-gpu/).

## Where the code uses it

- `tools/make_presets.py`, `lite_passes`: the beam (and show-lines) pass at the viewport's width, x2 for
  tubes in mm; crt-lite as the last pass, without present and without scale_type.
- `shaders/crt-lite.slang`: crt.inc with LR_NO_FEEDBACK, LR_NO_BACKDROP and LR_PRESENT.
- `tools/make_presets.py`, `super_lite_passes`: on top of lite, no native pass, the decoder at half the
  encoder's width (not on the 1084S, glow-h twice its share), the beam at x1 for every tube, the super lite
  passes.
- `shaders/encode-super-lite.slang`, `decode-super-lite.slang`, `beam-super-lite.slang`, `crt-super-lite.slang`:
  encode.inc, decode.inc, beam.inc and crt.inc with LR_SUPER_LITE (encode.slang, decode.slang and beam.slang
  include the same files without it). The products: `products` and `tint` in encode.inc, the LR_SUPER_LITE
  branch of the chroma in decode.inc.
