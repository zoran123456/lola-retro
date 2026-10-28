# Arcade monitors: how much of the game showed (`systems/arcade-15khz`)

## The question

A user on the libretro forum (2026-10-28) found MAME games "slightly cropped either on the top or bottom"
with `systems/arcade-15khz`, and integer scale didn't help. The preset was `amiga-1084s` with Console
timing 8, so it took the 1084S's picture size as Amiga owners set it (Overscan 0.1: the border that PUAE
sends around the Amiga's screen goes past the glass), and the TV's 240-line field. Worked out from
`crt.inc`: 90% of the field shows, 216 lines, so a 224-line game lost 4 lines at the top and 4 at the
bottom, a 240-line game 12 and 12, and a 256-line game at 55 Hz (still the 240-line field) 20 and 20. The
width lost about a pixel at each side. A render of a crosshatch with a frame line at the picture's edge
confirmed it: none of the top and bottom frame line showed, at 224, 240 or 256 lines.

## Sources

**Manufacturer's manuals (most trusted).** Sega's service manuals describe the test mode's C.R.T. TEST: a
crosshatch screen for the monitor's size, with a frame line around it, and say to adjust the monitor so
that the pattern stays on the screen:

- "Adjust the crosshatch frame line so that the checkered pattern does not extend beyond the screen."
  (Sega owner's manual 999-0921, C.R.T. TEST, 2) Monitor size adjustment screen:
  https://www.manualsdir.com/manuals/153620/sega-999-0921.html?page=26)
- "Adjust the Monitor to make sure that the crosshatch lines do not go beyond the screen size and
  crosshatch distortion does not occur." (Super GT, https://backup.segakore.fr/sauservice/Manuals/Super%20GT/Super%20GT%20Twin/SG17.html;
  the same wording in Manx TT, https://backup.segakore.fr/sauservice/Manuals/Manx%20Folder/MThtml/MT24.html)

These are mostly Sega's 24 kHz Model 2 and 3 games, but the instruction is about the monitor's size
controls, not the scan rate. 15 kHz boards had the same kind of pattern: the Neo Geo MVS's hardware test has a
crosshatch for the geometry (https://consolemods.org/wiki/Neo_Geo:Test_Mode, a community wiki), and
owners mention it on Street Fighter II (forum, least trusted).

**MAME's source (it follows the boards, so it counts as a measurement).**

- A board's visible area is its blanking window, and its line count differs from board to board. CPS1
  (`src/mame/capcom/cps1.h`): 8 MHz pixel clock, 512 x 262 in all, visible 384 x 224 (H 64-448, V 16-240).
  Irem M72 (`src/mame/irem/m72.cpp`, `set_raw(MASTER_CLOCK/4, 512, 64, 448, 284, 0, 256)`): 284 lines a
  frame, 384 x 256 visible, so about 55 Hz. A 256-line game doesn't fit a 240-line TV field at all.
- `screen_device::physical_aspect()` (`src/emu/screen.cpp`, master at 1ddcb58, 2026-10-09): a CRT screen
  whose driver gives no physical aspect is shown at 4:3 ("assume standard CRT"). MAME takes the visible
  area to fill a 4:3 screen, whatever its line count.

**Owners (least trusted).** On arcadecontrols, the aim is to fill the screen "both horizontally and vertically
without cutting off the image on the edges" (http://forum.arcadecontrols.com/index.php?topic=159544.80). One owner
set a monitor's H-SIZE jumper and could "finally see the full names on Samurai Shodown"
(https://www.fwaggle.org/2020/01/arcade-monitor-adjustments/). TVs were different: their makers set 5-10% of
overscan for line voltage and drift (https://www.repairfaq.org/REPAIR/F_monfaq4.html). An arcade monitor
was set up by the operator, for the board in the cabinet.

## What was worked out

- **The height.** The operator set the monitor for the game in the cabinet, so the game's lines fill the
  height whatever their number: Picture height 1 (`LR_FILL`). This also matches MAME, which shows the
  visible area at 4:3.
- **The height control on a tube in mm.** Picture height 1 used to be a zoom: the spot was given in lines of
  the 240-line field, so it grew or shrank with the picture. That suits a TV core that crops lines (the
  real set showed the whole field). On a monitor, the height control spreads the lines and the spot keeps
  its size in mm. So for tubes in mm (`inMM`), the spot in lines now comes from the lines across the height
  (`visLines`), not from the field (`visField`). A 224-line game then shows a little more of its gaps than
  a 240-line one (the line pitch is 7% larger). With Picture height 0 the two are the same, so no default
  preset changes except this one. The Amiga presets were checked byte for byte.
- **The overscan.** Sega's manuals want the whole pattern on the screen. On the 1084S's curved glass (Curvature
  0.035 / 0.045, Raster bend 0.3, Rounded corners 0.045) the corners of the picture are the first to go, so
  the picture is sized for its corners to just stay inside the glass, with the 4:3 kept. This is what the PC
  monitor preset does too. With Console timing 8 the game covers 0.906 of the active line (320 pixels at
  6.71 MHz, 47.7 of 52.6 us). Worked out with the glass and raster formulas of `crt.inc` (scratchpad
  `fit.py`): Overscan 0.0583 and Overscan height -0.0972. Rounded to the parameters' steps, towards a border:
  **Overscan 0.055, Overscan height -0.095**. The picture is then 4:3 to within 0.25%, and its corners are
  just inside the glass. The black at the middle of the sides is 2.0% of the width (5.4 mm on the 264 mm
  face) and at the middle of the top and bottom 1.9% of the height (3.8 mm). The flat preset is the same
  monitor set up the same way, so it has the same border, with square corners.

## Checked (2026-10-28)

RetroArch 1.22.2 (Vulkan, the image viewer, Aspect Ratio 4:3), with crosshatch pictures 384x224, 320x240 and
384x256 (TV standard 1, as MAME reports 55 Hz), each with a frame line at its very edge:

- New preset: the frame line shows at all four sides. At the middle of each side there is black of 1.7%
  of the height at the top and bottom and 1.9% of the width at the sides, up to the line's first lit pixel.
  The corners are inside the glass.
- Old preset: none of the top and bottom frame line showed, at any line count.
- Lite, super lite and HDR versions: the same picture, with no shader errors.
- `systems/amiga` and `amiga-1084s`: byte for byte the same as before.
- macOS OpenGL compiles every pass and the Amiberry, 86Box and Kodi ports.

## Not found

- How big a 15 kHz board's maker (Capcom, SNK, Konami) or a monitor maker (Wells-Gardner, Nanao, Hantarex)
  said the picture should be. Only Sega's wording was found.
- How much operators overscanned in practice. The preset follows the manual.
- An arcade monitor's own spot size and mask: the 1084S stands in for them.
- The real width of each board's line. Console timing 8 gives every width the same line time, so every game
  covers 0.906 of the line. Real boards differ, but the operator set the width for the game as well, so
  this only sets the border.

## Where the code uses it

- `tools/make_presets.py`: `SYSTEMS["arcade-15khz"]` (`LR_FILL` 1, `LR_OVERSCAN` 0.055, `LR_OVERSCAN_V` -0.095).
- `shaders/lola-retro/shaders/crt.inc`: the spot height in lines on a tube in mm (`visLines`).
- READMEs: the systems table, the `amiga-1084s` row and Picture height (`shaders/lola-retro/README.md`), and
  the arcade rows of `RECOMMENDED-CORES.md`.
