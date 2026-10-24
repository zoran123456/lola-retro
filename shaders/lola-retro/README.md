# Lola Retro for RetroArch

A CRT shader that simulates the whole analog chain instead of drawing scanlines on top of pixels:

**console video encoder → cable → TV decoder → electron beam → phosphor mask → glass**

Named after Lola, my retriever. Retro because it is retro.

## Quick start

1. Copy this `lola-retro` folder into RetroArch's shader folder (see [Install](#install)).
2. Start a game, open **Quick Menu → Shaders → Load** and pick your system from **`lola-retro/systems/curved/`**
   (or `systems/flat/` for a flat screen), for example `snes.slangp`.

Each system preset is the TV or monitor most people had for that system, on the cable that came in the box,
with the system's timing already set (see [Systems](#systems)). The mask is drawn at the tube's real size; on a
lower-resolution display, or against moiré, set **Mask on screen pixels** to 1 (see [Parameters](#parameters)).
To try another TV, cable or monitor, use the presets by device in `curved/` and `flat/` (see [Presets](#presets)).
They guess the console from the frame size, which works for most games, but systems with the same frame size
(the NES, SNES, Master System, PC Engine and Mega Drive all have 256-wide modes) can only be told apart by hand.
3D consoles can run at a higher internal resolution: the shader reads the upscaled frame as blocks of one
console pixel, so the signal stays right and the extra detail only makes edges smoother.
A few cases need one setting, see [RECOMMENDED-CORES.md](RECOMMENDED-CORES.md).

On an HDR display, use the same presets from `lola-retro/hdr/curved` instead, see [HDR](#hdr).
On a weak GPU (older phones, handhelds, old integrated graphics), use them from `lola-retro/lite/systems/curved`,
see [Lite presets](#lite-presets); if that is still too slow, from `lola-retro/super-lite/systems/curved`
(see [Super lite presets](#super-lite-presets)).

## Systems

| Preset (`systems/`) | System | Device | Console timing |
|---|---|---|---|
| `nes` | NES / Famicom | Consumer TV (Composite) | 1 |
| `snes` | SNES / Super Famicom | Consumer TV (Composite) | 1 |
| `master-system` | Master System (also MSX, ColecoVision) | Consumer TV (Composite) | 3 |
| `mega-drive-genesis` | Mega Drive / Genesis, Mega CD, 32X | Consumer TV (Composite) | 2 |
| `pc-engine-turbografx` | PC Engine / TurboGrafx-16, PC Engine CD | Consumer TV (Composite), NTSC | 4 |
| `playstation` | PlayStation | Consumer TV (Composite) | auto (4 at 1× and 2×, see below) |
| `saturn` | Sega Saturn | Consumer TV (Composite) | 4, and Frames over 300 lines 1 (see below) |
| `nintendo-64` | Nintendo 64 | Consumer TV (Composite) | auto (4 at 1× and 2×, see below) |
| `playstation-2` | PlayStation 2 | Trinitron (S-Video) | 5 |
| `gamecube` | GameCube | Trinitron (S-Video) | 5 |
| `dreamcast` | Dreamcast on a TV (for the VGA cable use `dos-pc`) | Consumer TV (Composite) | 5 |
| `arcade-15khz` | 15 kHz arcade (CPS1/2, Neo Geo MVS, most 80s and 90s boards) | Amiga 1084S | 8 |
| `amiga` | Amiga | Amiga 1084S | 6 |
| `dos-pc` | DOS and Windows 9x | PC Monitor (VGA) | 7 |
| `pc-98` | NEC PC-98 (640×400) | PC Monitor (VGA): 400 sharp lines on a computer monitor, as on the PC-98's own (for HDR use `hdr/curved/pc-monitor-vga`) | 7 |
| `x68000` | Sharp X68000 (px68k) | X68000 monitor (Sharp CZ-600D): 15 kHz games with gaps between the lines, 31 kHz games and the 768×512 prompt without (for HDR use `hdr/curved/x68000-monitor`) | 10 (11, see [X68000 monitor](#x68000-monitor)) |

PlayStation and N64 stay on auto: their native 480i games (Tekken 3) and a 2× upscaled 240-line game both
send 480 lines, and only you know which one it is. Auto reads 480 lines as 480i
(with the PlayStation 2's timing) and 3× and up as upscaled. When you know what the core sends, set the
console's own timing (4) by hand:

- at 2× internal resolution: Console timing 4. Every 480-line frame is then read as a 2× upscaled 240-line one
  (the two fields of a 480i game are averaged into one line).
- at 1×, and on cores that never upscale (Beetle Saturn): Console timing 4 and **Frames over 300 lines** 1.
  Every frame over 300 lines is then the console's own 480i, drawn in two fields with the console's timing
  (960 lines are 480i at 2×).

The `saturn` preset sets that: Console timing 4 and Frames over 300 lines 1. Auto would pick the Mega Drive
timing for Beetle Saturn's 330×224 and 352×224 frames, Beetle Saturn has no upscaling, and Kronos and
YabaSanshiro send native frames unless their resolution option is raised (then set Frames over 300 lines to 0).

The presets are the device presets below with one or two values changed, so every parameter still works.
For a PAL console set **TV standard** to 2 if the auto setting picks NTSC (the frame size cannot always tell).

## Curved or flat

The device folders have the same 15 presets; `systems/curved` and `systems/flat` have one per system.

| Folder | Screen |
|---|---|
| `systems/curved/`, `systems/flat/` | One preset per system, curved or flat (see [Systems](#systems)). |
| `curved/` | The glass bulges like a real tube, with rounded corners. The picture on it stays nearly rectangular, as on a well adjusted set (see **Raster bend**). |
| `flat/` | Same presets, flat screen and square corners. Pick this if curvature bothers you. |
| `hdr/curved/`, `hdr/flat/` | The same presets for HDR displays, see [HDR](#hdr). |
| `lite/curved/`, `lite/flat/`, `lite/systems/curved/`, `lite/systems/flat/` | The same presets for weak GPUs, see [Lite presets](#lite-presets). |
| `super-lite/curved/`, `super-lite/flat/`, `super-lite/systems/curved/`, `super-lite/systems/flat/` | The same presets for very weak GPUs, with compromises, see [Super lite presets](#super-lite-presets). |

## Presets

| Preset | Use it for | What it simulates |
|---|---|---|
| `consumer-tv-composite` | **Start here.** Everything from NES to PS1, especially Mega Drive and other games drawn for composite. | Ordinary living-room TV on the composite cable. Dithered waterfalls turn translucent, colours bleed. |
| `consumer-tv-scart-rgb` | The same games with a clean picture. The European SCART setup. | The same TV fed RGB. Sharp, no composite artefacts, same tube. |
| `trinitron-s-video` | PS2, GameCube, N64 and other late-90s consoles. | Sony Trinitron on S-Video. Aperture grille with the two damper wires, cool white. |
| `studio-monitor-rgb` | The sharpest picture with strong scanlines (the PVM/BVM look). | Broadcast/studio monitor on RGB, calibrated 6500 K white. |
| `studio-monitor-composite` | A clean composite picture that keeps the dot crawl and the blending. | Sony PVM-14L2 on composite, from its spec sheet: 13-inch Trinitron (flat vertically), 0.25 mm aperture grille (600 TV lines), digital comb filter, standard colour decoder, white at D93 (9300 K). The beam was matched to photos of a real PVM-14L2: the lines merge on mid-tones. The comb filter only works where the subcarrier flips every line (PlayStation, PC Engine); on the Mega Drive, NES and SNES it falls back to the ordinary filter, as an adaptive comb does. The grille is so fine that it only shows at 4K. |
| `old-tv-rf` | Nostalgia for the antenna cable. Noisy on purpose. | Old TV on the antenna input. RF snow, ghosting, soft focus, round tube. |
| `tv-show-broadcast` | Games as you saw them on a TV programme about games (test). | The console in a TV studio, broadcast in PAL and received with a roof antenna on the same living-room TV. The studio made a standard interlaced picture of the game, so the dark gaps between the lines are gone. See [TV show](#tv-show). |
| `crt-projector` | 24 kHz arcade games such as Daytona USA (Sega Model 2). | Arcade CRT projector (three tubes on a flat screen). No mask, colour fringes, soft. |
| `pc-monitor-vga` | DOS and Windows 9x games (320×200 up to 1024×768), Dreamcast on the VGA cable. | A typical mid-90s 15-inch PC monitor, described in millimetres (see [PC monitor](#pc-monitor)). 320×200 is drawn twice (400 lines), fine dot mask, a thin black border. |
| `pc-monitor-vga-good`, `-premium`, `-premium-plus` | The same, on a better 15-inch monitor; sharper Windows desktops at 800×600 and 1024×768. | Finer dot mask and a smaller, better focused beam (see [Better PC monitors](#better-pc-monitors)). |
| `pc-monitor-vga-extreme` | Long work on the Windows desktop. | Sharper than any real 15-inch tube: the gaps between the lines show even at 1024×768. |
| `amiga-1084s` | Amiga, and 15 kHz arcade games (CPS1/2, Neo Geo MVS). | Commodore 1084S on RGB, built from its service manual (see [Amiga 1084S](#amiga-1084s)). 0.42 mm slot mask, the picture nearly filling the glass. |
| `x68000-monitor` | Sharp X68000. | Its own monitor, the Sharp CZ-600D: 15 and 31 kHz on one 15-inch tube, 0.39 mm dot mask (see [X68000 monitor](#x68000-monitor)). |

The CRT projector already has a flat screen, so its `curved` version only adds rounded corners.

## Install

1. In RetroArch, open **Settings → Directory → Video Shaders** to see where your shader folder is.
2. Copy this whole `lola-retro` folder into that folder. If an older copy is there, replace it.
3. Start a game, open **Quick Menu → Shaders → Load**, go into `lola-retro`, then `systems/curved` or `systems/flat`,
   and pick your system (or `curved` or `flat` for the presets by device).

The shaders are in the slang format, so the video driver must be **Vulkan, glcore, D3D11, D3D12 or Metal**
(**Settings → Drivers → Video**). The old `gl` driver does not run slang shaders.

To use a preset automatically for one system, load it and choose **Quick Menu → Shaders → Save → Save Core Preset**.

### Windows

Use **Vulkan** (or glcore). D3D11 and D3D12 work and show the same picture, but RetroArch turns the passes
into HLSL for Microsoft's compiler, which takes a long time over the full presets' CRT pass. On a laptop with
an Intel Core Ultra 5 225U (RetroArch 1.22.2), the seconds RetroArch took to start, load the preset and
show one second of picture:

| Driver | Full presets | Lite and super lite | No shader |
|---|---|---|---|
| Vulkan | 3 to 7 | 3.5 to 4.5 | 2 |
| glcore | 8 to 13 | 3.5 to 4.5 | 2 |
| D3D11, D3D12 | 24 to 31 | 4 to 6 | 2 to 3 |

That wait comes every time a game starts with the preset (changing a parameter does not recompile). The
lite presets leave out Around the tube, which is very likely what takes the time. For HDR use Vulkan too:
glcore has no HDR. On old Intel graphics glcore has shown a broken picture (see [Performance](#performance)).

## Core settings that matter

For every system (core, preset, console timing and settings), see
[RECOMMENDED-CORES.md](RECOMMENDED-CORES.md). The short version:

The composite simulation needs the console's real pixel grid:

- **PlayStation** (Beetle PSX, SwanStation): no texture filtering, dithering on. Internal resolution 1× or 3× and up
  works by itself; at 2× set **Console timing** to 4.
- **Mega Drive / Genesis** (Genesis Plus GX, PicoDrive): any built-in "Blargg NTSC" filter **off**.
- **SNES** (Snes9x, bsnes): built-in NTSC/blargg filters **off**, hi-res blending **off**.
- **DOS and Windows 9x** (DOSBox Pure): leave the default VGA output; use `pc-monitor-vga`. It covers every PC
  mode from 320×200 to 1024×768 (the other presets would read 640×480 as a 480i TV picture).
- **Sharp X68000** (px68k): use `systems/x68000`. For a game that shows 256 lines at 15 kHz (gaps between the
  lines on the real monitor), set **Console timing** to 11 (see [X68000 monitor](#x68000-monitor)).
- RetroArch: **Settings → Video → Scaling → Aspect Ratio**: *Core provided* or *4:3*. Integer scaling is optional.
  With **Around the tube** on, *Full* works too: the tube stays 4:3 and the monitor's surroundings fill the rest of the screen.

**Internal resolution.** Frames with more than 576 lines are read as an upscaled 240-line mode (3× and up).
At 2× an upscaled PS1 frame looks like 480i, so set Console timing 4 by hand. 480-line consoles
(PS2, GameCube, Dreamcast) upscaled: set Console timing 5, then the frame is read as upscaled 480i.
**Frames over 300 lines** 1 does the same for every TV timing, for cores that never upscale (Beetle Saturn)
or run at 1×: every frame over 300 lines is the console's own 480i or 576i (960 or 1152 lines: 2×).
Some heights fit two factors: 1440 lines are 240 lines at 6× and 288 at 5×, 1792 lines 224 at 8× and 256 at 7×.
The shader then takes the NTSC height (240 or 224 lines); for a PAL game set **TV standard** to 2, and 288 or
256 lines win. Up to 4× no height is ambiguous.
In the TV presets a higher internal resolution costs about as much GPU time as native: the encoder and
decoder always work at 1280 samples per line (see [Performance](#performance)).

## Parameters

Every preset only sets parameters, so you can tweak any preset in **Quick Menu → Shaders → Shader Parameters**.

| Parameter | Meaning |
|---|---|
| Console timing | Pixel clock and colour-subcarrier rhythm of the console. 0 = auto (see below). |
| TV standard | 0 auto (by line count), 1 NTSC, 2 PAL. Set it by hand for PAL consoles in 60 Hz mode (PAL60, common on PS2 and Dreamcast): the line count says NTSC but the colour is PAL. It also switches the colour decoder and the phosphors. On a TV show (Cable 4) it is the standard of the programme: `tv-show-broadcast` sets 2, a European programme, and a game in the other standard goes through the studio's standards converter (see [TV show](#tv-show)). |
| Frames over 300 lines | A 480-line frame can be a console's own 480i or a 240-line game at 2× internal resolution, and its size cannot tell which. 0 (default): auto. Up to 576 lines is the console's 480i or 576i, more is read as upscaled; with Console timing set by hand, already more than 360 lines (so on timing 4 a 480i game's two fields are averaged into one line). 1: every frame over 300 lines is the console's own 480i or 576i, on every TV timing, with the timing as set; an upscaled one is still found (960 lines: 480i at 2×, 1152: 576i at 2×). For cores that never upscale (Beetle Saturn) or run at 1×: a 240-line game at 2× would be read as 480i. 2: every frame over 300 lines goes to a computer monitor instead, as if you had a second screen for the high-res modes (a compromise, see [Computer monitor for high-res frames](#computer-monitor-for-high-res-frames)). The Amiga, VGA, 24 kHz and X68000 timings (6, 7, 9, 10, 11) are not affected. |
| Cable | 0 RF, 1 Composite, 2 S-Video, 3 RGB, 4 TV show: the game as seen on a TV programme, from a studio through the antenna (see [TV show](#tv-show)). |
| Comb filter | Better TVs separated colour with a comb filter. Only works when the console flips the subcarrier phase every line (PlayStation, Amiga). On a TV show (Cable 4) the broadcast's own NTSC timing lets it work for every console. |
| Luma trap in the console | How much of the fine luma detail the console's encoder filtered out before mixing in colour. Lower it for a stronger rainbow on fine stripes (Sonic's waterfall), raise it for a cleaner picture. Real consoles differed a lot here: 0 is like an early Mega Drive Model 1 (strong rainbow), 0.75 (default) a typical console, 1 a later model with a better encoder. |
| Dither blend on RGB and S-Video | Off by default. Modern processing, not something a real TV did (similar to the notch filter of the RetroTINK 4K Pro): 1-pixel dither stripes blend into the colour or transparency the artists meant, without composite's rainbow and blur. Lines one pixel thin get slightly softer. The composite presets do not use it (composite blends by itself); to blend as much as they do: on NTSC 1 for 320-wide modes (most PlayStation games, Mega Drive H40) and 0.5 for 256-wide modes (NES, SNES, Master System, Mega Drive H32), on PAL about 0.45 and 0.1. Composite takes out all of the stripes' colour and that share of their brightness; Dither blend takes out the same share of both. |
| Dither blend auto | Off by default (0). 1: Dither blend does what composite would have done, worked out from the shader's own composite filters (Luma trap in the console, Sharpness, the TV's trap or Comb filter) for the console's pixel clock and the TV standard: all of the stripes' colour and composite's share of their brightness, so on RGB and S-Video a 1-pixel pattern keeps the contrast it had on composite, without the rainbow. It follows the mode by itself (NTSC: about 0.5 of the brightness for 256-wide modes, 0.95 for 320-wide; PAL: almost none and about 0.45). On the consoles and the Amiga; arcade boards (Console timing 8) and computer monitors keep Dither blend as set. PAL or NTSC: TV standard when it is set, otherwise the core's frame rate where RetroArch passes it to shaders (1.22 does; under 52 Hz is PAL), otherwise the line count. Patterns wider than one pixel are not blended. In 512- and 640-wide modes the composite and RGB passes do not yet follow their filters exactly, so there it blends somewhat differently from the composite presets (`docs/sources/dither-blend.md` in the repository). |
| Sharpness, Colour, Tint, Brightness, Contrast | The TV's own knobs. Tint only exists on NTSC sets. |
| Colour decoder | 0 auto, 1 standard, 2 US TV, 3 Japanese TV. American and Japanese TVs decoded colour on shifted axes with extra red gain ("red push"): yellows lean orange, reds are stronger, skin looks warmer. Auto uses the US TV decoder (Sony CXA2025AS) for NTSC on composite, RF and S-Video, and the standard one for PAL and RGB. |
| RF noise | Snow on the antenna input (RF and TV show). |
| No flicker | On by default. Shows a still picture the way the eye saw the moving one: the dots and the cross-colour that crawl from frame to frame are averaged over the frames of their cycle (2 on the PlayStation), so they cancel, as the eye blended them at 50 or 60 Hz (the NES and SNES only alternate between two positions 2/3 of a cycle apart, so there they halve instead); both interlaced fields are drawn every frame. Turn it off for the real moving dot crawl and 480i field flicker. |
| TV show: tape copies | Cable 4 only. How many Betacam SP copies the game footage went through before it was broadcast (recorded, then edited onto the master tape: 2). Each copy softens luma and colour a little more. 0 is a live programme. |
| TV show: antenna ghost | Cable 4 only. A faint copy of the picture shifted to the right, from a reflection off a building or a hill on the way to the roof antenna. |
| Beam width in dark areas / on white | The beam spot grows with brightness, in both directions: bright lines merge and bright detail rounds off, dark lines show gaps and dark detail stays sharp. TVs; monitors in mm (PC monitors, the 1084S, the X68000's) use the spot sizes in mm below. |
| Horizontal focus | Horizontal spot size relative to the vertical one; 0.5 = a round spot. Not used on monitors in mm (their spot is round). |
| Tube gamma | 2.4 is typical. |
| Phosphor afterglow | Real phosphors fade within about a millisecond, so keep this low. |
| Misconvergence | How far the red and blue beams land from green, growing toward the edges. |
| Scanline smoothing | 0 (default) off. With narrow beams (dark gaps between the lines) and a line pitch that is not a whole number of screen pixels, some lines land on a pixel row and others between two, so they look unevenly thick and bands appear (moiré), stronger on a curved screen. 1 averages each line's light over the screen pixel it falls on, as the display shows it, so every line keeps its brightness wherever it lands; 1.5 to 2 averages over a taller band, which evens the lines out further and keeps the gaps dark. The lines get a little softer, mostly at 1080p; at 4K it hardly shows. |
| Mask | 0 none, 1 aperture grille, 2 slot mask, 3 shadow mask, 4 projection screen. |
| Mask strength / triads per screen height | Lower the triad count for a coarser mask. Below about 2 screen pixels per triad the mask fades out to avoid moiré, so the fine PC mask shows best at 4K. On monitors in mm the triad count comes from the mask pitch instead. |
| Mask on screen pixels | 0 (default): the mask at the tube's own size (triads per screen height, or the dot pitch in mm), the same on every display. 2–6: the mask drawn on whole screen pixels, one triad every 2 to 6 pixels, like the pixel masks of other CRT shaders: it lines up with the screen's pixels, so it shows no moiré and does not fade out on a low-resolution display, but the number of triads follows your resolution instead of the tube. 2 is magenta and green (fine), 3 red, green and blue, 4 and up coarser. 1 (auto) takes the whole number of pixels nearest the tube's own triads (for 360 triads: 3 at 1080p, 4 at 1440p, 6 at 4K). For the aperture grille, slot mask and shadow mask; best on an LCD with RGB stripes. |
| White point | 6500 K neutral, 9300 K is the bluish white many TVs and monitors had. |
| Phosphors | 0 auto, 1 sRGB, 2 SMPTE-C, 3 EBU, 4 Japanese P22. The colours of the tube's phosphors. Auto: SMPTE-C on NTSC sets, EBU on PAL sets, sRGB on PC monitors, Japanese P22 on arcade monitors and the X68000's; the Trinitron preset uses Japanese P22 and the studio monitor EBU. Colours outside your display's range are clipped in SDR and kept in HDR. |
| Curvature, Rounded corners, Glass glow, Glass glow size, Darker edges, Overscan, Overscan height, Room reflection | The glass. Curvature is how much the glass bulges: its edges bow outwards and crop the corners of the picture. Glass glow sets how strong the halo around bright things is, Glass glow size how far it reaches. Set curvature and corners to 0 for a flat screen (that is all the `flat` presets change). Overscan is how far the picture runs past the edges of the glass; negative overscan adds a black border, like PC monitors. Overscan height is added to it for the height alone, like the monitor's height knob: raise it to fill the height (a 224-line SNES game keeps thin black bars at the top and bottom otherwise), lower it for a border at the top and bottom only. Room reflection is the room's light the glass reflects, in % of white, in a dim room (Room light 1): 0.2 on a TV, 0 on the studio monitors. |
| Raster bend | How much of the glass curvature the picture follows. The deflection was corrected so that the raster looks nearly rectangular from the front; a well adjusted set kept the bow of its lines to about 1% of the height, which is the default (0.3). 0 is a perfectly corrected raster, 1 a picture bent as much as the glass. |
| Picture height | 0 (default): the picture sits in the TV's 240- or 288-line field, so a game with fewer lines (224) keeps a border, as on the real set. 1: the core's lines fill the height. Use it with **Aspect Ratio: Core provided** for cores that crop lines and set the aspect ratio from the lines they keep (Geargrafx, Beetle PCE/Saturn/PSX with their scanline options); with a fixed 4:3 it stretches the picture. It is a zoom of the same tube, so lines and beam keep their look. Not used on a TV show (Cable 4). On the X68000 monitor it works the same way: a 256-line game on Console timing 11 is taller than the monitor's 240-line 15 kHz picture, so at 0 eight lines at the top and bottom fall outside it, and at 1 it fills the height. |
| Linearity error horizontal, vertical | Off (0) by default. Real deflection was never perfectly linear: one side of the picture came out squeezed and the other stretched, differently on every set. Positive values squeeze the left or the top, negative the right or the bottom; 0.05 to 0.1 is a cheap set. |
| 15 kHz monitor in mm | Describes the tube in mm for 15 kHz modes too (on in the `amiga-1084s` preset): the parameters below then apply, the monitor shows the whole active line (a 320-pixel Amiga line leaves side borders), and 320×200 / 640×400 are read as an NTSC Amiga instead of VGA. PC monitors (31 kHz) and the X68000 monitor always use mm. |
| Monitor size, Dot pitch | Nominal size in inches (the viewable picture is one inch less) and the mask pitch in mm. See [PC monitor](#pc-monitor), [Amiga 1084S](#amiga-1084s) and [X68000 monitor](#x68000-monitor). |
| Spot size in dark areas / on white | The beam spot in mm (width at half brightness). 0.30 / 0.45 is a typical 15-inch PC monitor, 0.28 / 0.65 the 1084S (and the X68000 preset); lower both for a sharper tube. |
| Spot size in the corners | How much larger the spot is in the corners than in the centre (deflection defocus). 1.4 is typical for a PC monitor (dynamic focus kept good ones below 1.5, cheap ones reached 2); the 1084S had static focus, 1.5. |
| Real size: your screen's height, unit | Draws the tube as large as the monitor in **Monitor size** really was, with black (or **Around the tube**) around it, instead of filling your screen. Enter the height of your screen's picture area (measured, in cm, or in inches with unit 1); 0 fills the screen. On a large display this puts the monitor at its real size in front of you. Needs the picture area as tall as the screen (full screen). |
| Around the tube | What is around the tube: 0 black, 1 the monitor in a room, 2–11 the monitor in a scene (see [Scenes](#scenes)). The casing is measured on photos of real monitors and drawn as large as the real one, so it shows best with **Real size**. `amiga-1084s` gets an Amiga monitor (after the M1438S): warm off-white, a thick flat front, a tunnel with mitred corners down to a thin black mask at the glass, a plain chin with a green power light. The PC presets get a 90s PC monitor (after a Compaq 151FS): aged cream, a raised rim around a shallower recess, a blank plaque, and a control strip below with buttons and a green light. The TV presets get a 90s TV (after photos of several): dark grey plastic, thin sides, the glass almost flush with the front, and a tall chin with a speaker grille on each side of the controls (a power switch, a red light, four small buttons). TVs came from 14 to 29 inches, so the TV is sized to **Monitor size**. `x68000-monitor` gets the TV too: the CZ-600D was a TV set as well. The walls around the glass face the picture, so the screen lights them softly in its colours and they change with it (**Screen light on the casing**); the room lights them from above, darker at the top and lighter at the bottom, and the satin plastic catches a little of the ceiling and the lamp on the edges that face up. |
| Room light | How bright the room is: 1 a dim room (warm lamps), 3 a lit room, 20 daylight. 0 is a dark room: the glass reflects nothing, and black stays black (best on an OLED in the dark). It lights the casing and the wall (in a scene only the casing, in the scene's colour: white in space, pink in synthwave, like its sun), and sets the reflection on the glass too (Room reflection is how much the tube reflects in a dim room), so in daylight the tube's black turns grey, as on the real one. Lower Room reflection if you want it darker. |
| Screen light on the casing | How strongly the screen lights the walls around the glass: 0 off, 1 as on the real monitor (worked out from the screen's light, the angle of the walls and the tinted glass; about 3–5% of the picture beside them, softly spread, as plastic scatters it), up to 3. Best seen in a dark room. |
| Scene speed | How fast the scenes move: 1 normal, 0 a still picture, up to 3. |
| HDR: paper white, HDR: display peak | Only in the `hdr` presets. Paper white is how bright a full white screen is, display peak the most your display can show. See [HDR](#hdr). |

### Scenes

**Around the tube** 2–11 put the monitor in front of a scene instead of in a room. They are decoration, not a
simulation, all drawn by the shader (no pictures), and they move (**Scene speed**). **Room light** lights the
casing in the scene's colour.

| | Scene |
|---|---|
| 2 | Space: the Milky Way across the sky with dark lanes of dust, clouds of glowing gas, bright stars with spikes of light and now and then a small galaxy; nearer stars slowly come closer and drift past. |
| 3 | Synthwave: a big striped sun over two ranges of mountains (the near one with neon lines along its slopes), palm trees at the sides, a neon grid floor that runs toward you, a purple sky full of stars. |
| 4 | Tiles: a 90s desktop wallpaper in the 16 Windows colours, scrolling slowly and diagonally. Eight patterns (cubes, studs, raised bricks, scales, pearls, a woven mat, a honeycomb, argyle) take turns every two minutes. |
| 5 | Bouncing lines: two shapes whose corners bounce off the edges of the screen, followed by fading copies that change colour along the trail, as on 90s screensavers. |
| 6 | Underwater: a calm sea floor from a 16-bit game: the surface rippling at the top, light falling in slanted rays, a reef far away, fish passing and now and then a school of small fish, rocks, corals, sponges and kelp on the sand with patches of light drifting over it, bubbles rising. |
| 7 | Copper bars: Amiga raster bars swinging around an invisible cylinder, stars flying sideways over a sky the copper fades to violet, a polished checkerboard floor that shows the bars. |
| 8 | Amiga demo: a screen from an early-90s Amiga demo, in 320×256 and 4096 colours. A glenz vector (a see-through solid of white and blue triangles, lit from one side) and a cube of vector balls that turns into a ball swing out from behind the monitor, stars fly toward you, a twister turns along the bottom and a DYCP scroller runs along the top, over a copper background. |
| 9 | Hills: a 16-bit landscape in parallax layers: the sun, clouds near and far, birds, pale mountains far away and snowy ones nearer, hills with bushes, round trees and pines, grass with flowers. |
| 10 | Night city: a skyline in three layers under a full moon: windows lighting up and going dark, thin clouds drifting past, now and then a plane, rooftops with water tanks, red lights and a hotel sign, cars on the street below. |
| 11 | Arcade carpet: neon shapes on black, like the carpets of 90s arcades, glowing as under black light: planets, stars, moons, lightning, spirals and more, with confetti between them. |

The pixel-art scenes draw their pixels as squares of a whole number of screen pixels, so they stay sharp on any
display. Space, Bouncing lines and Amiga demo take the most GPU time; on a slow GPU the other scenes are lighter.

### Console timing ids

| Id | Console | Why it matters |
|---|---|---|
| 1 | SNES / NES | 227⅓ subcarrier cycles per line, so the dots run diagonally. Every other frame is 4 master clocks short (the NES skips a dot, the SNES shortens a line), so the pattern alternates between two positions: the dots jitter rather than crawl. |
| 2 | Mega Drive H40 (320 wide) | Exactly 228 cycles: still vertical stripes; 1-pixel dithers become rainbow transparency. |
| 3 | Mega Drive H32 (256 wide), Master System | Same rhythm as H40 at a slower pixel clock. The Master System (and MSX, ColecoVision) runs the same 228 cycles per line. |
| 4 | PlayStation | 227½ cycles: the pattern flips every line and every field, so a comb filter can remove it. |
| 5 | PlayStation 2 | 480i at 13.5 MHz. |
| 6 | Amiga | 320×256 PAL / 320×200 NTSC. The width tells lores, hires and superhires apart, and a frame that includes the overscan border (PUAE's default, 720 wide) keeps the right picture size. |
| 7 | PC VGA | 31 kHz; 200-line modes are drawn twice (400 lines). |
| 8 | Arcade 15 kHz | Generic 15 kHz RGB. |
| 9 | Arcade 24 kHz | Medium-res arcade, e.g. Sega Model 2 at 496×384 progressive. |
| 10 | Sharp X68000 | On its own monitor: up to 240 lines at 15 kHz (gaps between the lines), 256-line frames at 31 kHz with every line drawn twice (no gaps), taller frames line by line. RGB only. |
| 11 | Sharp X68000, 256 lines at 15 kHz | The same, but 256-line frames at 15 kHz, for the few games that show a 256-line window there. |

Systems that are not in the list use the id with the same timing: PC Engine, Saturn and Nintendo 64 use 4, the PC-98 uses 7
(its 640×400 on a computer monitor is the same picture as VGA's).
Some PC Engine games run 262 lines per frame instead of 263; their pattern then stands still instead of
alternating, which the shader does not model separately.

**Auto** guesses from the frame size: 256×192 → Master System, other 256-wide frames → SNES, 320×224 → Mega Drive, 320×240 and other 240-line
modes → PlayStation, 320×200, 640×350 or 640×400 → VGA (NTSC Amiga on the 1084S preset), 256 or 512 lines and PUAE's default
frames (360, 720 or 1440 wide with 287, 574, 242 or 484 lines) → Amiga, 336–400 lines → arcade 24 kHz,
more than 300 lines → interlaced, more than 576 lines → upscaled (more than 720 with **Frames over 300 lines** 1 or 2; see Internal resolution). Set the id by hand when the guess is wrong (for example a Mega Drive game
in 240-line PAL mode), or use a preset from `systems/`.

## TV show

`tv-show-broadcast` (Cable 4) shows a game the way it looked on a TV programme about games in the
90s: the same living-room TV as `consumer-tv-composite`, but the game reaches it from a TV studio,
through the transmitter and a roof antenna. On TV games looked smoother, brighter and cleaner than
on the RF or composite cable at home. Most of that is the chain, which the preset simulates:

- **No gaps between the lines.** A console cannot be locked to the studio's clock, so its picture
  went through a frame synchronizer, which writes out a standard interlaced picture. Each 240p/288p
  frame becomes one field and the next one lands half a line lower, so every console line is drawn
  twice and the dark gaps between the lines are filled. At living-room distance the 576-line raster
  of a broadcast is near the limit of the eye, while the 288-line one of a console at home is not.
  This is the biggest difference. With **No flicker** off, a thin horizontal line jumps up and down
  by half a line at 25 Hz, as on the real TV.
- **A clean source.** The preset assumes the studio took the console's RGB, as professional video
  did, instead of the RF or composite cable most homes used (how each programme connected its
  consoles is not documented), so there is no console encoder in the chain. The studio's
  Betacam SP tape (**TV show: tape copies**, Sony BVW-75P: luma 5.5 MHz, colour 1.5 MHz at -1.5 dB)
  and the station's PAL encoder (U and V 1.3 MHz) soften the picture a little. The broadcast is
  composite too, so dithering still melts into smooth shades and fine stripes still show a little
  rainbow, about as much as on the composite cable at home.
- **The transmitter.** A PAL B/G transmitter runs out of carrier a little above peak white (about
  114-120% of the picture signal), so the brightest saturated yellows and cyans (up to 133% in PAL)
  could not go out as they were. How stations handled it is not documented; the preset clips them
  softly a little below that, at 110%, so they come out slightly darker and paler. 75% colours pass untouched.
- **The antenna.** A little snow (**RF noise**: 0.06 is good reception, about 47 dB weighted,
  between "perceptible" and "imperceptible" on the ITU five-grade scale) and a faint ghost
  (**TV show: antenna ghost**, 3% at 1.2 µs). Unlike a console's RF modulator, the broadcast has
  stable sync, so the lines do not jitter.
- **TV standard.** The preset is a European (PAL) programme. A game in the other standard (an NTSC
  game, 240 lines) went through the studio's standards converter, which scaled it to the PAL raster,
  so it fills the screen; a PAL game with 256 lines keeps its black borders. Set **TV standard** to
  0 for a programme in the game's own standard (an American programme for NTSC games).

The rest was not in the signal: the footage was picked from the best moments, often from
pre-release versions or pre-rendered trailers, and seeing a game move at all was rare.

The preset has one pass more than the others (`show-lines`): it works out the beam of every line of
the programme once, so the CRT pass draws them as fast as any 480i or 576i picture. Cable 4 also works
in the other presets, but slower, because there the standards converter is worked out at every pixel.

## PC monitor

On 31 kHz modes (the `pc-monitor-vga` preset, Console timing 7 in any preset, or the high-res frames of
**Frames over 300 lines** 2) the tube is described in
millimetres, like a real monitor: viewable size, dot pitch, and the size of the beam spot on dark and on white.
Every video mode follows from the same tube, so 320×200, 640×480, 800×600 and 1024×768 each look the way they
did on that monitor.

The `pc-monitor-vga` preset is a typical mid-90s 15-inch monitor: 14-inch viewable picture, 0.28 mm dot mask, 85 MHz video
amplifier, a beam spot of 0.30 mm on dark and 0.45 mm on white, 1.4 times larger in the corners, a nearly flat
glass, and the picture filling it up to a thin black border, as owners set it with the monitor's controls. Monitors were
built with a spot about 1.2–1.3 times the pixel at their sharpest resolution, and an average 15-inch monitor was sharp at
800×600 and soft at 1024×768; that puts the spot at about 0.45 mm. Better monitors had smaller spots, see
[Better PC monitors](#better-pc-monitors).

What that gives (measured from the shader, centre of the screen, the picture size of the preset):

| Mode | Pixel width | 1-pixel stripes, white on black | Line structure, 30% grey / white |
|---|---|---|---|
| 320×200 (drawn as 400 lines) | 0.87 mm | 95% contrast | 46% / 7% |
| 640×480 | 0.44 mm | 49% | 24% / 2% |
| 800×600 | 0.35 mm | 28% | 7% / 0% |
| 1024×768 | 0.27 mm | 11% | 1% / 0% |

So 320×200 shows chunky pixels with fine lines that you see up close and in dark areas, 640×480 is sharp
with 1-pixel dots still visible, and 1024×768 is soft, as it was on an average 15-inch tube (for a sharper one use the presets below, or
set Monitor size to 17 for a 17-inch). The dot mask is too fine to show at 1080p, as it was on the real monitor at normal viewing
distance; at 4K it shows as a fine texture.

### Better PC monitors

The `pc-monitor-vga` preset is an average 15-inch monitor. Better ones had a finer mask and a smaller,
better focused beam, and on them 1024×768 was sharp. The same 15-inch tube in four more steps:

| Preset | Dot pitch | Spot dark / white | Corners | Like |
|---|---|---|---|---|
| `pc-monitor-vga` | 0.28 mm | 0.30 / 0.45 mm | 1.4× | an average 15-inch monitor |
| `pc-monitor-vga-good` | 0.25 mm | 0.25 / 0.35 mm | 1.4× | a good mid-range 15-inch monitor |
| `pc-monitor-vga-premium` | 0.25 mm | 0.20 / 0.28 mm | 1.3× | a premium 15-inch monitor |
| `pc-monitor-vga-premium-plus` | 0.24 mm | 0.17 / 0.24 mm | 1.25× | the best 15-inch monitors; misconvergence 0.08 |
| `pc-monitor-vga-extreme` | 0.22 mm | 0.13 / 0.18 mm | 1.15× | no real 15-inch monitor; misconvergence 0.05, glass glow 0.02 |

`extreme` goes past the real thing on purpose: the beam is narrower than the line pitch at 1024×768, so the
picture stays crisp and calm for long work on the desktop, with gaps between the lines no real monitor had in
that mode. For a Trinitron or Diamondtron, set **Mask** to 1 (aperture grille).

For the stand-alone PC emulator 86Box, the repository has these presets converted to GLSL (`86box/`).

### Computer monitor for high-res frames

**Frames over 300 lines** 2 draws every frame with more than 300 lines on this PC monitor, whatever the
preset's cable and Console timing (the TV timings: auto, 1–5 and 8), as if you had switched to a second
screen, as people did: an Atari ST owner had a high-res monitor for the desktop and a TV for games. The monitor
is the one above: VGA timing (every line once, filling the height), the tube in mm from the Monitor values
(Monitor size, Dot pitch, the spot sizes), RGB, sRGB phosphors, and a dot mask at the dot pitch (a mask set to
0 stays off). Frames of 300 lines or fewer keep the preset as it is. An upscaled frame is still found when it is
a whole multiple of a 480- or 576-line mode (960 lines: 640×480 at 2×); any other frame is taken as it is
(1024×768).

It is a compromise, so it is off by default: one screen stands in for two and switches by itself, and the rest
of the preset stays as it is: the glass and its curvature, overscan, misconvergence, white point, glow and the
TV's knobs. A TV's overscan cuts off the edges of a desktop, and its misconvergence gives small text coloured
edges; for a picture closer to `pc-monitor-vga`, set Overscan to −0.035 and Misconvergence to 0.12. The TV presets carry
the signal at 1280 samples per line, so frames up to 1280 pixels wide keep every pixel.

## Amiga 1084S

The `amiga-1084s` preset is built from the Commodore 1084S-P1 service manual and photos of a real 1084S:

- 14-inch Philips M34EAQ10X tube, 0.42 mm slot mask, 6.5 MHz video amplifier.
- White set to "D" (D65, 6500 K), European phosphors (EBU) whatever the Amiga sends, PAL or NTSC.
- Picture size as owners set the monitor up: width and height turned up until a 320×256 screen nearly fills
  the glass, with about 5 mm of black left around it (Overscan 0.1). At the factory setting (Overscan −0.015)
  the whole active picture fills the 13-inch face, and a 320-pixel line, 45 of the 52 µs, leaves wide black
  borders on all sides.
- The tube is described in mm (beam spot 0.28 mm on dark, 0.65 mm on white), so NTSC games, with 200 lines
  further apart, show stronger lines than PAL games with 256, as on the real monitor. The spot was calibrated
  on a photo of a real monitor: the line contrast inside mid-bright text (39% in the photo) is matched.
- Frames with the overscan border (PUAE's default, 720×287) show that border at its real size around the
  picture. Glow and misconvergence are measured in lores pixels, so hires and lores frames look the same.

For the stand-alone emulator Amiberry, the repository has this preset converted to GLSL (`amiberry/`).

## X68000 monitor

The Sharp X68000 came with its own monitor, the CZ-600D (1987), which took 15, 24 and 31 kHz on one tube
and switched by itself. The `x68000-monitor` preset (and `systems/x68000`, Console timing 10) draws every mode
on that one tube, described in millimetres like the PC monitor and the 1084S:

- From Sharp: a 15-inch tube with a 0.39 mm dot mask; one picture size for every mode, 278 × 209 mm, with
  240 active lines at 15 kHz, 400 at 24 kHz and 512 at 31 kHz. (Sharp's manuals for the CZ-605D, a CZ-600D
  successor with the same 0.39 mm pitch, give the tube type, the picture size and the timing table; the
  CZ-600D's own manual was not found.)
- Not found for any X68000 monitor: the beam spot, the video bandwidth and the white point. The spot, its
  growth in the corners, the misconvergence and the curvature are the 1084S's, a monitor of the same class
  and years whose spot was calibrated on a photo. White at 9300 K and Japanese phosphors: the Japanese TV
  standard (the CZ-600D was also a TV), not measured on the monitor itself.
- Because one tube in mm serves every mode, the same spot leaves clear gaps between 15 kHz lines and lets
  31 kHz lines merge, as photos of X68000 monitors show:

| Frame from px68k | Mode on the monitor | Line structure, 30% grey / white |
|---|---|---|
| 256×240, 512×240 | 15 kHz, 240 lines | 87% / 16% |
| 256×256, 512×256 | 31 kHz, every line drawn twice (512 lines) | 10% / 0.5% |
| 512×480 | 15 kHz interlaced, both fields | 15% / 0.5% |
| 768×512, 512×512 (the Human68k prompt) | 31 kHz, 512 lines | 10% / 0.5% |

(Line structure here: the contrast between the middle of a line and the gap, (max − min) / (max + min) in
linear light, at the centre of a flat-screen picture, mask and glow off.)

The frame alone does not say whether a 256-line game runs at 15 or 31 kHz: px68k sends both as 256 rows, and
only the frame rate (55 or 61 Hz) differs. Most X68000 games run at 31 kHz, so Console timing 10 draws 256-row
frames that way; for a game that shows 256 lines at 15 kHz (the gaps between the lines are then missing), set
Console timing 11. Those 256 lines are taller than the monitor's 240-line picture at 15 kHz, so the top and bottom
8 run past it; **Picture height** 1 fits them in. px68k's own menu (F12) is 800×600, and after a reset from that menu px68k may keep sending
800×600 with the picture in the top left corner; restart the content if that happens. The research behind
this preset is in the repository (`docs/sources/x68000-video.md`, `docs/sources/x68000-monitors.md`).

## HDR

A real tube concentrated its light in the phosphor dots and the centre of each scanline, with dark gaps
around them. On an SDR display the shader has to squeeze those bright dots under the white level, so the
picture loses brightness and contrast. On an HDR display the presets in `hdr/curved` and `hdr/flat` give the
dots the extra brightness instead, and the average stays at the paper white level.

1. Video driver **Vulkan, D3D11 or D3D12** (**Settings → Drivers → Video**, then restart RetroArch).
   On a Mac use Vulkan; the Metal driver has HDR only in nightly builds so far.
2. Turn HDR on for the display in the system: on Windows **Settings → System → Display → Use HDR**,
   on macOS **System Settings → Displays → High Dynamic Range**.
3. In RetroArch: **Settings → Video → HDR → Enable HDR**.
4. Load a preset from `lola-retro/hdr/curved` or `lola-retro/hdr/flat`.
5. In **Quick Menu → Shaders → Shader Parameters**, at the bottom:
   - **HDR: display peak (nits)**: the peak brightness of your display. About 400 for DisplayHDR 400
     monitors, 600–1000 for OLED TVs.
   - **HDR: paper white (nits)**: how bright a white screen should be. 200 is a good start; raise it for a
     brighter picture.

The shader writes HDR10 itself, so RetroArch's own HDR settings (paper white, peak, contrast) do not change
these presets. Use them only with HDR switched on, otherwise the picture looks grey and flat. The normal
presets keep working with HDR on as well (RetroArch converts them), they just don't use the extra brightness.

With a bright display (peak about 4× paper white or more) you can raise **Mask strength** towards 1.0:
the gaps between the phosphors go dark like on a real tube and the picture stays as bright.

**True black on an OLED.** The presets assume a dim room with a lamp on (Room light 1), so the glass reflects
a little of the room's light and the tube's black is a faint grey (about 0.35 nits at the default paper white),
as on a real CRT in such a room. If you play in a dark room, set **Room light** to 0: black is then exactly
black, as on a real tube in the dark. Glass glow still lifts the area right around bright things a little, as
the real glass did.

## Lite presets

For weak GPUs: older phones, handhelds, old integrated graphics. The folders `lite/curved`, `lite/flat`,
`lite/systems/curved` and `lite/systems/flat` hold the same presets with the same settings, and run about
1.6 to 3.4 times as fast (more on smaller screens and on RGB). The picture is the same:

- The beam pass works out each line on one sample per screen pixel instead of 8192 samples, the largest
  saving: the screen cannot show more. The tubes described in millimetres (PC monitors, Amiga 1084S, X68000)
  get two samples per pixel, because their spots are narrow next to the pixels of hires and 31 kHz modes.
- The CRT pass writes the screen itself, so one pass and one full-screen buffer are left out, and RetroArch
  does not add a copy pass.

Side by side with the full presets, at 3× zoom, no difference can be seen (measured: 44–66 dB PSNR).
Two things are left out, to save the GPU's time:

- **Phosphor afterglow**: the faint trail behind bright things that move. It reads the whole previous frame
  back every frame. **Phosphor afterglow** does nothing in these presets.
- **Around the tube** stays black: no casing, room or scenes. Their code is left out of the pass too, which
  keeps it small enough for weak shader compilers.

| Apple M4 Pro, ms per frame | 1440×1080 | 960×720 | 640×480 |
|---|---|---|---|
| `consumer-tv-composite` | 1.81 → 1.07 | 1.47 → 0.81 | 1.34 → 0.69 |
| `consumer-tv-scart-rgb` | 1.39 → 0.65 | 1.04 → 0.38 | 0.90 → 0.26 |
| `amiga-1084s` | 1.47 → 0.82 | 1.17 → 0.46 | 1.01 → 0.34 |
| `playstation` (640×448 interlaced) | 3.10 → 1.85 | 2.69 → 1.50 | 2.52 → 1.30 |

The composite chain stays the heavy part: even lite costs about as much as crt-royale or
crt-guest-advanced, so an old budget phone will still not reach full speed with composite. The RGB presets
(`consumer-tv-scart-rgb`, `amiga-1084s`) are the lightest. Still too slow? See
[Super lite presets](#super-lite-presets). How this was measured is in the repository
(`docs/sources/lite-presets.md`).

## Super lite presets

For GPUs too weak even for lite: older budget phones, small handhelds. The folders `super-lite/curved`,
`super-lite/flat`, `super-lite/systems/curved` and `super-lite/systems/flat` hold the same presets and
settings with the whole model still at work: the composite signal with its blended dithering and rainbow, the
beam that grows with brightness, the mask and the glass. They cost about a third of the full presets, a
quarter on smaller screens (full / lite / super lite):

| Apple M4 Pro, ms per frame | 1440×1080 | 960×720 | 640×480 |
|---|---|---|---|
| `consumer-tv-composite` | 1.81 / 1.06 / 0.62 | 1.49 / 0.82 / 0.41 | 1.34 / 0.68 / 0.31 |
| `consumer-tv-scart-rgb` | 1.37 / 0.65 / 0.52 | 1.05 / 0.39 / 0.29 | 0.89 / 0.27 / 0.19 |
| `trinitron-s-video` | 1.62 / 0.87 / 0.54 | 1.25 / 0.65 / 0.34 | 1.14 / 0.51 / 0.24 |
| `amiga-1084s` | 1.50 / 0.82 / 0.57 | 1.13 / 0.47 / 0.31 | 1.01 / 0.34 / 0.24 |
| `playstation` (640×448 interlaced) | 3.12 / 1.84 / 1.08 | 2.70 / 1.45 / 0.77 | 2.46 / 1.28 / 0.61 |

Unlike lite, they give up a little of the picture (37–51 dB PSNR against the full presets at 1440×1080):

- The decoder works out every other sample of the signal. The encoder keeps all of them, so the rainbow
  and the blended dithering stay as they were; the picture moves by half a sample (1/2560 of the line).
- The encoder reads each source pixel once for its colour filter and luma trap. It also multiplies its signal
  by the TV decoder's reference subcarrier, so the decoder only has to filter it: the same sums, to rounding,
  at less than half the decoder's work.
- The beam is worked out with half the taps, on one sample per screen pixel for every tube: dark detail can
  come out up to 1.5% brighter, and on a screen narrower than a hires frame, 1-pixel patterns come out as
  their average.
- The CRT pass adds up 3 lines per pixel instead of 4, with a cheaper dither.
- No `native` pass: run 3D cores at their native resolution (1×). At a higher internal resolution the
  picture still works, but the upscaled detail is read one row per console line instead of averaged.
- As in lite: no phosphor afterglow, nothing around the tube.

Even super lite simulates the whole chain, so it stays well above shaders that only draw scanlines and a
mask: on the same GPU and frame at 960×720, crt-guest-advanced-fastest takes about 0.12 ms and crt-royale
about 0.56 ms. An old budget phone may still not reach full speed on composite; the RGB presets are the
lightest.

## Performance

The chain has eight passes (`tv-show-broadcast` nine) and the encoder and decoder do real signal
filtering, so it needs a reasonably modern GPU. Integrated graphics from the last few years should be fine at 1080p.
The first pass (`native`) averages the rows of each console line of an upscaled frame once, and in the TV
presets the encoder and decoder work at a fixed 1280 samples per line (about 27 MHz, 4 per pixel of a
320-wide console), so a PS1 core at 4× or 8× internal resolution costs about as much as at 1×. (Before,
the encoder's work grew with the square of the internal resolution: 16 times as much at 4×.) The PC and
Amiga presets keep 4 samples per frame pixel, because their beam reads every pixel exactly.
The beam pass works out each source line once on an 8192-pixel-wide texture, so the GPU has to support
textures that wide (every desktop GPU of the last decade does). The beam pass is the largest of the chain;
the [lite presets](#lite-presets) make it as wide as the screen.
Older integrated graphics will not reach full speed: one user measured about 24 fps with the Amiga preset at
1080p on Intel Haswell graphics (2013) with Vulkan; on the same GPU the glcore driver showed a broken picture.
Recent integrated graphics have room to spare: on a laptop with an Intel Core Ultra 5 225U (Vulkan, a 1600×1200
picture) the full presets take 5.4 to 6.6 ms of the 16.7 ms a frame has at 60 Hz, lite 2.2 to 3.4 ms and
super lite 1.7 to 2.5 ms (`docs/sources/windows-test.md` in the repository).

## Tested

Every preset of v1.14 compiles and runs in RetroArch 1.22.2 on macOS with the Metal, glcore and Vulkan drivers,
and the Metal screenshots match, practically pixel for pixel, the offline renders every change is checked with.
Earlier versions were rendered in RetroArch 1.18 with the glcore and Vulkan drivers and reported working with
Vulkan and glcore on Windows (NVIDIA). Direct3D 10/11/12 failed in 1.0 and 1.1; 1.2 fixes the cause (every pass
now samples without derivatives, which the Direct3D compiler requires inside loops).
v1.16 was run on Windows 11 with Intel graphics (Core Ultra 5 225U) on D3D11, D3D12, Vulkan and glcore: 12
of the 15 device presets (all but three of the PC monitors) and lite and super lite composite start with no
errors, and D3D11, Vulkan and glcore give the same picture
(RetroArch cannot take a screenshot of the shader's output on D3D12, so its picture was not compared).
The HDR output has been checked numerically (the HDR10 signal decodes back to the intended brightness)
and confirmed on macOS with the Vulkan driver and a DisplayHDR 400 monitor. Reports from other HDR
displays are welcome. The Amiberry and 86Box versions are in use in Amiberry and 86Box on macOS.
The PC monitor model was checked against its physics (spot width, stripe contrast, line structure and brightness
agree within 2% in every mode) and against photos of real VGA monitors; the 1084S against photos of a real 1084S;
the X68000 monitor against Sharp's manuals and photos of X68000 monitors, not yet with frames from px68k itself.
Reports are welcome.

## License

MIT, see the LICENSE file in this folder.
