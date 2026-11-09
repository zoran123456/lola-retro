# Arcade 31 kHz monitors: the Nanao MS-2931 and the Sanwa 29PFX

Researched 2026-11-09. No preset uses this yet: the note says what was found, and what a preset would need.

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

## What a preset would need (not done)

1. Parameter ranges: Monitor size stops at 21 inches (27.6 needed, so also a step of 0.5 or 0.1), Dot pitch
   at 0.70 mm (0.8 needed), White point at 9300 K (9700 in the manual). Wider ranges keep saved presets valid.
2. The slot mask's vertical pitch. `slotGate` in `crt.inc` repeats every two trio widths (1.6 mm here); the
   tube's vertical pitch is 0.6 mm. On a tube in mm it should come from the tube.
3. A timing for 31 kHz arcade boards. Console timing 7 (VGA) never reads a frame as upscaled, and Naomi's 3D
   games are usually run at 2x or more in Flycast: 1280x960 would be drawn as 960 lines. It needs the 480-line
   base that the TV timings have, drawn once per line.
4. The spot. Neither manual gives a number. As for the 1084S, it has to be calibrated on photos of the real
   screen at 31 kHz and at 15 kHz (line gaps and beam only, not colour).
5. Curvature from the radii (the sag of a 2400 mm radius over the 270 mm half width is 15 mm), the border
   from the 5 mm, and the convergence limits as an upper bound.

## Not found

- The spot size, or any focus figure.
- The phosphors' chromaticities. Phosphors auto gives Japanese P22 to the arcade timings.
- Whether the tube is a slot mask by name. A trio pitch with a vertical figure fits one; the manual does not
  say.
- Which cabinets carried which monitor, from the makers. The scan's title page names two deluxe Sega games;
  that the Naomi Universal and Blast City cabinets used these Nanao monitors, and which monitor the
  Atomiswave SD cabinet had (forum posts name a Wei-Ya chassis with a Samsung tube), is community knowledge
  that was not checked here.
- The 29PFX's screen size and the rest of its manual beyond pages 3 to 5.

## Where the code uses it

Nowhere yet.
