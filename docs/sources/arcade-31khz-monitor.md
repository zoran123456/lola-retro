# Arcade 31 kHz monitors: the Nanao MS-2931 and the Sanwa 29PFX

Researched 2026-11-09, for `systems/arcade-31khz` (made the same day).

## The question

A user on the libretro forum (post 55, 2026-11-01) uses `systems/arcade-15khz` for Atomiswave and Naomi games
and finds them "too low res": those boards drove 31 kHz monitors. `arcade-15khz` sets Console timing 8, a 15 kHz
TV raster, so Flycast's 640x480 frame is drawn as an interlaced picture. The nearest preset now is
`systems/dos-pc` (480 lines, each drawn once), but that is a 15-inch PC monitor with a 0.28 mm dot mask. The
Batocera shader sets (issue #19) map Naomi and Atomiswave to `dos-pc` for the same reason. Is there a real
31 kHz arcade monitor with enough published data to describe it in mm, like the 1084S?

## Sources

**Manufacturer's documents (most trusted).**

- Eizo, *Service Manual MS-2931*, Ver. 10, Aug. 1999 (78 pages, a scan with a title page added by the person
  who scanned it: "Used in Airline Pilots DX, F355 Deluxe"; Sega part number 200-5710). The Nanao AmuseScan
  Multi 29, a 29-inch monitor for 15, 24 and 31 kHz. From the Arcade Otaku wiki
  (`wiki.arcadeotaku.com/images/3/34/MS-2931_Service-manual_full.pdf`; the wiki blocks scripts, the copy read
  was the Wayback Machine's of 2025-12-03:
  http://web.archive.org/web/20251203014503/https://wiki.arcadeotaku.com/images/3/34/MS-2931_Service-manual_full.pdf).
  Section I, Specifications, pages I-1 to I-8. The pages were read by OCR and the numbers below checked on
  the page images (the OCR had the light transmission as 19%; the page says 49.0%).
- Sanwa Electronics, *Specifications, product code 29PFX*, Rev. D, 2005-12-19 (24 pages, a scan), "29" PF CRT
  display". From the same wiki (`/images/1/15/Sanwa_29PFX_Manual.pdf`, Wayback Machine copy of 2025). Sections
  1-5 and 2, pages 3 to 5, by OCR; page 5 (the tube) was checked on the page image, pages 3 and 4 (line
  rates, convergence, white) were not.

**Community wiki (least trusted).** The Arcade Otaku wiki's MS-2931 page: made from 1998 to the early 2000s;
the MS-2930, MS-2931 and MS-2934 "are all compatible with each other" and share tube and yoke; known tubes
Toshiba A68KZN696X (MS-2930), A68LBT696X (MS-2931), A68KJU96X (MS-2932).

## What the manuals give

| | Nanao MS-2931 (1999) | Sanwa 29PFX (2005) |
|---|---|---|
| Tube | Toshiba A68LBT696X | Chunghwa A68AKY13X, "29 inches the flat style" |
| Trio pitch | horizontal 0.8 mm at the centre, 0.9 mm at the edges; vertical 0.6 mm | 0.84 mm at the centre |
| Screen (phosphor area) | 540.8 x 405.6 mm minimum, 676.0 mm diagonal | not read (resolution below gives 541 x 406 mm) |
| Curvature of the screen | radius 2400 mm horizontal, 2440 mm vertical, 2390 mm diagonal | flat |
| Glass | light transmission 49.0% approx., anti-static coating | transmission about 52.0% |
| "Resolution" (screen size / pitch) | 676 dots x 676 lines | 644 dots x 483 lines |
| Video bandwidth | 28.4 MHz typ. at -3 dB | 25 MHz typ. at -3 dB ("max video clock frequency") |
| Line rates | 15.75 kHz +-300 Hz, 24.4 and 31.5 kHz +-500 Hz; 55-65 Hz vertical | 15.75, 24.83, 31.50 kHz +-300 Hz; 55-70 Hz |
| Convergence | 1.5 mm max. inside a circle of 60% of the height, 2.5 mm inside one of the full height, 3.0 mm elsewhere | 1.4, 1.8 and 2.2 mm for the same three areas |
| White | x 0.285 +-0.02, y 0.285 +-0.02, "9700K approx." | x 0.275 +-0.03, y 0.285 +-0.03 |
| Brightness | 60 +-10 ft-L maximum (white field); the test conditions: 60 ft-L on a 33% window, 32 ft-L on a white field | 60 +-10 ft-L on a white window |
| Linearity | 10% horizontal, 8% vertical, max. | the same |
| Distortion | trapezoid and barrel/pincushion 3.0% max., tilt 2 degrees | 3.0%, 3.0% |
| Focus | "To be adjusted best." | adjusted by eye |
| Picture size as adjusted | a cross-hatch 5 +-5 mm inside the screen's edges, on every side; "100% scanned in each signal" | "scanned in the full size" |

The MS-2931's test signals (2.6, Recommended Signal Timing Chart) are Sega's own boards:

| Mode | Source | Line | Active | Lines shown / in all |
|---|---|---|---|---|
| 1 | ST-V, Golden Axe: The Duel | 63.56 us (15.734 kHz) | 49.17 us | 224 / 263 |
| 2 | Model 3 at 24 kHz | 41.0 us (24.39 kHz) | 30.69 us | 381 / 424 |
| 3 | Model 3 at 31 kHz | 31.58 us (31.67 kHz) | 25.92 us | 477 / 525 |

## What was worked out

- **There is a real monitor to describe.** The MS-2931's manual gives what the 1084S's service manual gave
  for `amiga-1084s`: the tube, its mask pitch, the screen in mm, the video bandwidth, the white, and how the
  picture was set up. It adds the glass's radii and Sega's signal timings. The 29PFX, six years later and
  from another maker, has nearly the same numbers (0.84 mm, 25 MHz, the same screen), so the MS-2931 is not
  an odd one out.
- **In the shader's units** (worked out, not read): the screen is 26.6 inches across the diagonal, which is
  Monitor size 27.6 (the model takes one inch off the nominal size). 405.6 mm / 0.8 mm is 507 triads per
  screen height: 2.1 screen pixels per triad at 1080p (the mask fades to about half strength there), 2.8 at
  1440p, 4.3 at 4K. With the 5 mm border, 480 lines are 0.82 mm apart, a little more than one trio.
- **The amplifier hardly matters at 640 wide.** 28.4 MHz is a Gaussian of 4.7 ns; a pixel of a 640-pixel
  line in 25.92 us lasts 40.5 ns. The PC monitor path (flat pixel steps, an 85 MHz amplifier) is within a
  tenth of a pixel of it.
- **One tube for 15, 24 and 31 kHz.** `arcade-15khz` stands on the 1084S because no arcade monitor's data was
  found (`arcade-monitors.md`, Not found). This monitor would serve all three line rates, as the X68000's
  does for 15 and 31 kHz.
- **The picture size confirms `arcade-monitors.md`**: the whole picture on the screen, with about 5 mm of
  black around it.

## What the preset does

`systems/arcade-31khz` (and its flat, HDR, lite and super lite versions) is the PC monitor model with this tube:

| Value | From |
|---|---|
| Console timing 12: 640 pixels at 27 MHz, every line once | Flycast, `core/hw/pvr/spg.cpp`: `PIXEL_CLOCK = 27 * 1000 * 1000`, halved unless the VGA bit is set |
| Monitor size 28 | the model's face is one inch under the nominal size: 27 inches, 548.6 x 411.5 mm, 1.4% over the manual's 540.8 x 405.6. Monitor size stays in whole inches (the Unity package keeps it as a whole number), so the two pitches are 1.4% up too |
| Dot pitch 0.81, Slot mask: vertical pitch 0.61, Mask 2 (slot) | the trio pitch, 0.8 x 0.6 mm. The manual's drawing of the screen shows blue, green and red in a row, which is a stripe tube |
| White point 9700 | the manual |
| Overscan -0.02, Overscan height -0.005 | the picture 5 mm inside the screen's edges |
| Curvature 0.01 across, 0.02 down | the radii, seen from 70 cm (assumed: a seated player). The corners lie (270.4 mm)^2 / (2 x 2400 mm) = 15 mm behind the middle of the top edge, so they look 15 / 700 = 2% of the half height nearer the middle; the sides (202.8 mm)^2 / (2 x 2440 x 700) = 1% |
| Phosphors auto: Japanese P22 | as the other arcade timings (not in the manual) |
| Spot 0.57 mm on dark, 1.33 mm on white | **assumed**: the 1084S's 0.28 and 0.65 mm, which were calibrated on a photo, times the screens' diagonals (676 / 330 mm). The trio pitches have nearly the same ratio (0.8 / 0.42), so the spot is as large against the mask as on the 1084S |
| Spot size in the corners 1.5 | **assumed**: the 1084S's |
| Misconvergence 0.3 | **assumed**: a third of the manual's limits. 0.3 puts red and blue 0.35 mm apart in the middle and 1.0 mm at the sides; the limits are 1.5 and 3.0 mm |
| Glass glow 0.06, Darker edges 0.25, afterglow 0.05, Room reflection 0.2, Rounded corners 0.045 | **assumed**: as `arcade-15khz` and the TV presets |
| Colour 1.08, Contrast 1.05 | kept from `pc-monitor-vga` |

In the shader (`common.inc`, `crt.inc`, `beam.inc`):

- **Console timing 12.** The board's picture is always 640x480, so a frame of a whole multiple of 480 lines is
  read as that picture at a higher internal resolution (`upscaleOf`), which the VGA timing never does: Naomi's
  3D games are usually run at 2x or more. Any other height is drawn line for line. RGB whatever Cable says.
- **The slot mask's vertical pitch** (`LR_MON_PITCH_V`, new; 0 keeps twice the dot pitch, as before). Where
  the breaks would be less than about 2.6 screen pixels apart they fade to their average, the way the whole
  mask fades on a fine trio pitch: at 1080p this tube's are 1.6 pixels apart, at 1440p 2.1, at 4K 3.2.
- **Ranges**: Monitor size to 29 inches (was 21), Dot pitch to 1.00 mm (0.70), White point to 9700 K (9300),
  Console timing to 12.
- **The beam along the line** takes at most 24 pixel steps. A spot wider than that in frame pixels (this
  tube from 4x internal resolution) now takes its pixels in groups; before, the loop stopped at the 24th pixel
  and cut the right side of the spot off.
- **Misconvergence on upscaled frames.** Its limit was one frame pixel, so it shrank as the internal
  resolution went up; it is one console pixel now. This changes upscaled frames on every preset a little.
- The preset's decoder runs at 2560 samples per line (4 per pixel of the 640), whatever the frame's width, so
  that a 4x frame does not make it 10240 wide; every frame pixel keeps a sample of its own up to 4x.

The 28.4 MHz amplifier is not modelled: the PC monitor path reads each pixel as a flat step. At 27 MHz its
Gaussian is an eighth of a pixel wide and would take about 7% off the contrast of 1-pixel stripes, far less
than the spot does.

## Checked (2026-11-09)

Offscreen on macOS OpenGL 4.1 (M4 Pro), the whole chain run as RetroArch sizes and feeds it (a ctypes script
in the session's scratchpad, not in the repository):

- **Nothing else changed.** 107 renders of the other presets (every system and device preset, flat, lite and
  super lite versions, four masks, Mask on screen pixels, 4K, Around the tube) against the commit before: 102
  byte for byte the same. The 5 that differ are upscaled frames (3x and 4x on the TV presets, 2x on the
  computer monitor for tall frames), from the misconvergence limit: 46 to 58 dB. A 4x frame is now 46.4 dB
  from the native one, before 43.4. `getTiming` old against new, 204,960 cases: none differ.
- **The border**: with a crosshatch whose frame line is at the very edge, 4.6 mm of black at the sides and
  3.8 to 4.0 mm at the top and bottom, up to the first lit pixel; the corners of the frame line are lit, on
  the curved preset too.
- **The lines** (flat field, mask off, the lines' modulation): 18% at 1% of white, 10% at 5%, 6% at 10%, 1% at
  30%, none on white. So 480 lines merge except in dark areas. Alternating white and black lines keep 15 to
  18% of their contrast, 1-pixel stripes across 17% at 1080p and 28% at 4K.
- **Mask and moiré**: on 30% grey and on white at 1080p, 1440p and 4K the slow ripple (a 25-pixel mean) is
  about 1%, the same as `amiga-1084s` in the same test.
- **Upscaled frames**: 2x, 3x, 4x and 6x of the same picture come out 41 to 43 dB from the native one. What
  differs is the glass glow of 1-line detail: the glow pass averages two lines of a native frame before it
  turns them into light, and a native frame's alternating lines glow 0.19 instead of 0.5. (That is in every
  preset and was not changed here.) 960x720 is drawn as 720 lines.
- Lite against full: 62 dB. Super lite: 50 dB. Every pass and the three ports compile.

In RetroArch 1.22.2 (Vulkan, macOS, a temporary config, the built-in image viewer with the same crosshatch at
640x480 and 1280x960, a screenshot after 90 frames): the preset and its lite, super lite and HDR versions load
with no errors in the log. At 2880x2160, 2x against 1x is 43.2 dB, lite against full 66.8 dB, super lite 51.4 dB,
as offscreen. `systems/snes` and `amiga-1084s` load as before.

Not checked: with Flycast and a game (the core is not installed here); the HDR version's picture; a real MS-2931.

## Not found

- **The spot size**, or any focus figure. Two searches for close-up photos of this monitor at 31 kHz found
  owners' remarks but no photo to measure. This is the value that decides how much of the lines shows, and it
  is an assumption.
- The phosphors' chromaticities.
- Whether the tube is a slot mask by name. A trio pitch with a vertical figure and the stripes in the drawing
  fit one; the manual does not say.
- The radius of the screen's corners.
- Which cabinets carried which monitor, from the makers. The scan's title page names two deluxe Sega games;
  that the Naomi Universal and Blast City cabinets used these Nanao monitors, and which monitor the
  Atomiswave SD cabinet had (forum posts name a Wei-Ya chassis with a Samsung tube), is community knowledge
  that was not checked here.
- The 29PFX's screen size and the rest of its manual beyond pages 3 to 5.
- An arcade cabinet for Around the tube: it draws the PC monitor's casing.

## Where the code uses it

- `tools/make_presets.py`: `SYSTEMS["arcade-31khz"]`, `SYSTEM_PASSES` (2560 samples), the tubes in mm of the
  lite presets.
- `shaders/lola-retro/shaders/common.inc`: Console timing 12 (`consoleTable`, `upscaleOf`, `getTiming`,
  `phosphorSet`), `LR_MON_PITCH_V` and the ranges.
- `shaders/lola-retro/shaders/crt.inc`: `slotGate`, `maskPoints`, `pixelMask` (the vertical pitch and its fade).
- `shaders/lola-retro/shaders/beam.inc`: the pixel steps in groups, the misconvergence limit.
- READMEs: the systems table, Console timing ids, Slot mask: vertical pitch and the Arcade 31 kHz monitor
  section (`shaders/lola-retro/README.md`), the arcade table of `RECOMMENDED-CORES.md`.
- `tools/make_unity.py` knows the new parameter and timing; the Unity package was not regenerated.
