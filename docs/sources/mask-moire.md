# Mask moiré at 1080p, and the shoulder per mask point

Worked out 2026-10-24 for two reports: on the libretro forum (StargazingDog) moiré in the curved composite
preset in SDR with non-integer scaling, gone with the HDR presets and with integer scaling; in a private
message, "vertical shadow bars" at 1080p in most presets, gone with Mask on screen pixels 1. Used in the CRT
pass (`crt.inc`: `maskPoints` and the mask part of `main`) and in the Mask row of the Parameters table in
`shaders/lola-retro/README.md`. All numbers here are measurements of the shader, not of a real tube: a real
tube shows no moiré at all, so the aim is as little as possible.

## How the numbers were measured

A ctypes renderer of the whole slang chain on Apple's OpenGL (M4 Pro), a white 320x240 frame, the CRT pass's
output in linear light. Luminance is blurred to eye scale (Gaussian, sigma 3 px across and 6 px down, which also
takes out the scanlines) and compared with a wider blur (sigma 12 px): the RMS of the ratio minus 1 is the ripple,
across (vertical bars) and down (horizontal bands), in a 6x4 grid of the screen, leaving out 40 px along the
tube's edge. The worst cell is quoted.

## What causes it

- The mask is drawn at the tube's own size: 360 triads per screen height on the consumer TV, so at 1080p a triad
  is exactly 3 screen pixels (flat preset: no ripple at all). Where the curvature takes it a little off 3, or
  where a preset's triad count gives a pitch near a whole number of pixels without being one (trinitron-s-video,
  380 triads: 2.84 px), the mask's harmonics alias to slow beats.
- Each screen pixel averages the mask at 2 points, 0.5 px apart (2x2 for the slot and dot masks). That nulls the
  harmonic that lands near 1 cycle per pixel, the main source of the beat.
- SDR's shoulder (`shoulder`, knee at 0.8) ran once per pixel, on that average. On white a lit stripe is about 1.5
  times white, so the shoulder squeezed it, and how much a pixel lost depended on where the stripes fell on it:
  the nonlinearity brought the aliased harmonic back after the averaging. With the shoulder moved up as in HDR
  (room 2) the SDR preset gave exactly the HDR preset's numbers, so the shoulder was the whole difference.
- Integer scaling made the picture 960 px tall: 2.67 px per triad, far enough from 3 that the beat is fine and
  faint. Mask on screen pixels 1 puts a whole number of pixels in each triad: nothing beats.
- An HDR preset shown on an SDR screen flattens a ripple further: at 200 nits a 1% change in light is 0.18% in the
  PQ signal, 0.4% of light on a gamma 2.2 screen.

## The change

Each mask point's light goes through the rest of the tube (damper wires, white point, halation, the phosphor
matrix, all linear) and through the shoulder on its own, and the pixel shows the average of the points. A stripe
brighter than the display can show is squeezed as a stripe, the same wherever it lands. HDR takes the same path
with its own shoulder. Without a mask, with Mask on screen pixels (already averaged over 16 points per pixel),
and where the mask has faded out, there is one point and the pixel is computed as before (identical within
1/255 in a few values, from the compiler's rounding).

Ripple, worst cell, 1440x1080, before / after:

| Preset | Before | After | HDR preset |
|---|---|---|---|
| consumer-tv-composite curved, bars | 0.69% | 0.34% | 0.43% (unchanged) |
| consumer-tv-composite curved, bands at the sides | 0.48% | 0.30% | |
| trinitron-s-video flat, bars over the whole screen | 1.12% | 0.21% | |

Integer scaling (1280x960) was 0.07% before. The 1-D model behind the change (stripes() sampled at the 2 points,
SDR shoulder): ripple at 2.95 px per triad 6.9% with the shoulder per pixel, 3.8% per point, 3.8% in linear light.
The rest in HDR comes from the 2 points themselves (the 6th harmonic, near 2 cycles per pixel, passes them); a box
over the whole pixel would take most of it out (0.15% in the model), not done here.

## What it changes

White comes out a little darker in SDR, because each lit stripe is squeezed instead of the pixel's average (centre
of a white frame, CRT pass, linear):

| Preset (flat) | 1440x1080 | 2880x2160 |
|---|---|---|
| consumer-tv-composite, consumer-tv-scart-rgb | -0.30% | -0.44% |
| trinitron-s-video | -2.58% | -0.99% |
| studio-monitor-rgb | -3.59% | -2.01% |
| old-tv-rf | -1.24% | -0.55% |
| crt-projector | -1.17% | -0.43% |
| amiga-1084s | -1.12% | -1.02% |
| x68000-monitor | 0 (mask faded out) | -1.74% |
| pc-monitor-vga | 0 (mask faded out) | -1.78% |

Calibrations: the PC monitor table (README) is measured with mask and glow off, so it is unchanged. The 1084S line
contrast (matched to a photo, 39%): on a flat grey frame at the centre, grey 150 unchanged (44.5% PAL, 60.1% NTSC
at 1080p), grey 190 down by 0.6 to 1.0 point (PAL 29.7% to 29.1%, NTSC 44.6% to 43.6%); at 4K the same. Smaller
than the 2-3 points that kept Scanline smoothing off by default, so not recalibrated.

Cost: within the timing noise (about 0.1 ms a frame at 1440x1080) on full, lite and super lite.

RetroArch 1.22.2 on the M4 Pro (image viewer, consumer-tv-composite and trinitron-s-video): Metal, glcore and
Vulkan give the same picture (the screenshots differ only in RetroArch's own message bar at the bottom). One Metal
run, the first after the change, stalled after compiling all passes without drawing a frame; 8 more interleaved
Metal runs (4 of this version, 4 of the one before) all ran. The same rare stall at start on Metal was seen
before this change (composite-luma-bandwidth.md's tests), so it is not taken as caused by it.

## Not done

- The full-pixel box (more points per pixel) would also take out the rest of the ripple in HDR and SDR; it costs
  more mask evaluations per pixel and softens the mask slightly. Not measured on the real chain.
- The brightness lost on strong masks in SDR is not compensated: a gain would clip more.
