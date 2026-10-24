# Sharp X68000: video modes and what px68k sends

Researched 2026-10-22 for the X68000 monitor model (task 2 of issue #9). Code was read at px68k-libretro
0ad84d70 (2026-08-22) and MAME df241e3a (2026-10-21).

## Clocks and the CRTC

- Oscillators: 38.86363 MHz for the 15 kHz modes and 69.55199 MHz for the 31 kHz modes (MAME
  `src/mame/sharp/x68k.cpp` ~1170-1171); the X68030 and Compact XVI add 50.35 MHz (`x68k.cpp` ~1242).
- Dot clock divisor from CRTC register R20, low bits (MAME `x68k_crtc.cpp` ~178-203): $00 /8, $01 or $05 /4,
  $10 /6, $11 or $15 /3, $16 /2.
- R20 (`x68k_crtc.cpp` ~314-320): bit 4 selects 15.98 or 31.50 kHz; bits 2-3 256, 512 or 1024 lines (1024 is
  interlaced); bits 0-1 256, 512 or 768 dots (3: the 50 MHz clock on later models).
- At 31 kHz, 256-line modes are scanned twice: each line is drawn on two rasters (XEiJ's notes; MAME
  `gfx_double_scan()`, `x68k_crtc.h` ~42).

## Modes (IOCS _CRTMOD and common game modes)

Frequencies from XEiJ's CRTMOD table (https://stdkmd.net/xeij/iplrom16.htm#crtmod_list, IPLROM 1.6 = a
patched 1.3); register values from Seafy's crtc.dta (1993, https://groups.google.com/g/fj.sys.x68000/c/OubVeaPH_oQ).
Totals and dot clocks were worked out from those registers; they reproduce XEiJ's frequencies exactly.

| CRTMOD | Visible | f_H | f_V | Scan | Lines total / active | Dot clock (dots per line) |
|---|---|---|---|---|---|---|
| 16, 20, 24 | 768x512 | 31.50 kHz | 55.458 Hz | progressive | 568 / 512 | 69.552/2 = 34.78 MHz (1104) |
| 0, 4, 8, 12 | 512x512 | 31.50 kHz | 55.458 Hz | progressive | 568 / 512 | 69.552/3 = 23.18 MHz (736) |
| (games) | 512x256 | 31.50 kHz | 55.458 Hz | each line scanned twice | 568 / 512 rasters = 256 lines | 23.18 MHz |
| 2, 6, 10, 14 | 256x256 | 31.50 kHz | 55.458 Hz | each line scanned twice | 568 / 512 rasters = 256 lines | 69.552/6 = 11.59 MHz (368) |
| 3, 7, 11, 15 | 256x240 | 15.98 kHz | 61.463 Hz | progressive | 260 / 240 | 38.864/8 = 4.858 MHz (304) |
| (games) | 512x240 | 15.98 kHz | 61.463 Hz | progressive | 260 / 240 | 38.864/4 = 9.716 MHz (608) |
| 1, 5, 9, 13 | 512x480 | 15.98 kHz | 61.463 Hz per field | interlaced | 260 / 240 per field | 9.716 MHz |
| 17, 21, 25 | 1024x424 | 24.699 kHz | 53.116 Hz | progressive | about 465 / 424 | not found |
| 18, 22, 26 | 1024x848 | 24 kHz | | interlaced | | not found |
| 19, 23, 27 | 640x480 | 31.469 kHz | 59.940 Hz | progressive (VGA, later models) | | probably 50.35/2 (inferred) |

Worked out from the registers: at 31 kHz 22.08 us of a 31.75 us line is active (69.6%), at 15 kHz 52.7 of
62.58 us (84%); vertically 90% (31 kHz) and 92% (15 kHz) of the lines.

## Which modes games use

Of 119 titles with a default mode in the Arcade Hardware Power Up table
(https://pcbiroiro.blogspot.com/2015/06/x68000-games-technical-details.html), 99 run at 31 kHz and 20 at
15 kHz. 15 kHz by default: Space Harrier, Twinbee, Final Fight and Strider (both listed as 512x256). 31 kHz:
Gradius, Gradius II, R-Type, Parodius; Dragon Spirit 256x256, Marble Madness 384x512, Cotton 384x256 (or
448x240 / 512x240 at 15 kHz). Akumajou Dracula is listed as 31 kHz elsewhere
(https://assemblergames.org/viewtopic.php?t=59277). So the typical game is 256 lines at 31 kHz, each line
scanned twice (512 rasters, no gaps on the monitor), at 55 Hz.

## What px68k sends (px68k-libretro 0ad84d70)

- The frame is exactly the CRTC's display window, `TextDotX x TextDotY`, cut from an 800x600 buffer with an
  800-pixel stride (`libretro.c` ~2633, `libretro/windraw.c` ~60, ~119). No blanking, no borders.
  `TextDotX = (HEND - HSTART) x 8`, `TextDotY = VEND - VSTART` (`x68k/crtc.c` ~258-267, ~282, ~288).
- `CRTC_ScreenChanged` (`crtc.c` ~188-212): a 31 kHz 256-line mode (R20 & 0x14 = 0x10) is halved, so it
  arrives as 256 rows (only one of each pair of rasters is drawn); a 15 kHz 512-line mode (0x04) is doubled,
  both fields drawn into one frame, so 512x480 arrives without flicker (`libretro.c` ~2397-2409).
- So: 15 kHz games arrive at their own height (256x240, 512x240, not line-doubled); 31 kHz 256-line games as
  256 rows; 512x512 and 768x512 (the Human68k prompt) as they are; 15 kHz interlaced as 512x480.
- Aspect ratio fixed at 4:3 (`libretro.c` ~1648, ~2515): narrow windows such as 384x256 are stretched.
- Frame rate 55.46 Hz when R20's 31 kHz bit is set, 61.46 Hz otherwise (`libretro.c` ~61-62, `crtc.h` ~7-8);
  "Adjust Frame Rates" (on by default, `libretro_core_options.h` ~430-441) reports 55.5 and 59.94 Hz instead.
- Where 800x600 comes from: the initial geometry (`retrow`/`retroh`, `libretro.c` ~131-132) until the first
  frame sets the real size (`windraw.c` ~74-96), and px68k's own F12 menu (`libretro.c` ~2207-2219). Read from
  the code, not tested: leaving the menu through a reset (`winui.c` ~739-744, `libretro.c` ~2613-2617) does
  not restore the size, so frames may stay 800x600 with the 768x512 prompt in the top left corner and the
  rest of the buffer not cleared. A comment in px68k-libretro issue #70
  (https://github.com/libretro/px68k-libretro/issues/70) says the menu is 800x600 and the prompt mostly
  768x512.
- Windows wider than 800 or taller than 600 (1024x424) do not fit the buffer (read from the code).

## Consequences for the shader

- A 256-row frame from px68k can be a 31 kHz game (two rasters per line: no gaps on the real monitor) or a
  15 kHz game with a custom 256-line window (gaps). The standard 15 kHz modes show 240 lines. Only the frame
  rate tells them apart for sure (55 vs 61 Hz), and a slang shader does not get it reliably (OriginalFPS
  exists only in newer RetroArch versions; an unknown uniform stops the shader from loading in older ones).
  px68k does not report it anyway: 59.94 (or 61.46 with its adjusted rates off) for every mode
  ([core-frame-rates.md](core-frame-rates.md)).
- 15 kHz interlaced (512x480) and 31 kHz 512-line frames both arrive with every line, tall and close
  together; on the monitor the first is two interlaced fields of 240 lines, the second 512 progressive lines.

What the shader makes of it (Console timing 10 and 11): see [x68000-monitors.md](x68000-monitors.md).

## Not found

- An official Sharp (or "Inside X68000") CRTMOD register table; the values above are community sources.
- The dot clock and R00 of the 24 kHz modes; the 15 kHz interlace field structure (half-line offset).
- Gradius's exact resolution.
- A bug report confirming 800x600 frames at 31 kHz.
