# Lola Retro

**A CRT shader that simulates the whole analog chain, not just scanlines. For RetroArch, with versions for
Amiberry (Amiga), 86Box (PC) and Unity (your own games).**

`console video encoder → cable → TV decoder → electron beam → phosphor mask → glass`

Games from the CRT era were drawn for that chain. Dithered waterfalls turned translucent on composite,
1-pixel stripes became rainbow shimmer, PlayStation's 4×4 dither melted into smooth gradients.
On an LCD you only see the raw pixels. Lola Retro brings the rest back.

Named after Lola, my retriever. Retro because it is retro.

![Raw pixels, a real Sony Trinitron on composite, and Lola Retro](docs/dracula-vs-real-crt.jpg)

<sub>Dracula from Castlevania: Symphony of the Night (PlayStation), the same frame in every picture. From left: the raw
pixels; a photo of a real Sony KV-13M51 Trinitron on composite, by [CRTpixels](https://x.com/CRTpixels/status/1408451743214616587);
Lola Retro with the Trinitron preset switched to composite, and with the consumer TV composite preset. The dithering in
the hair melts into soft shading, the red eyes bleed and the background keeps its stripes, as on the real set. The photo
was taken up close, so its lines and contrast look a little stronger.</sub>

![Sonic on composite and RGB](docs/sonic-composite-vs-rgb.jpg)

<sub>Same frame, same tube, different cable. On composite the striped background blends into soft colour with a
little rainbow, just as it did on a living-room TV. On RGB you see the stripes the artists actually drew.</sub>

## Videos

| | |
|---|---|
| [![Lola Retro on YouTube](https://img.youtube.com/vi/7losgxx2cp0/mqdefault.jpg)](https://www.youtube.com/watch?v=7losgxx2cp0) | **[Lola Retro in action](https://www.youtube.com/watch?v=7losgxx2cp0)**<br>An older version. The current one has a more realistic, more modest rainbow. |
| [![Super Turrican](https://img.youtube.com/vi/xdj4simbOp4/mqdefault.jpg)](https://www.youtube.com/watch?v=xdj4simbOp4) | **[Super Turrican on SNES](https://www.youtube.com/watch?v=xdj4simbOp4)** |
| [![Earthworm Jim](https://img.youtube.com/vi/Cz7tewURyZg/mqdefault.jpg)](https://www.youtube.com/watch?v=Cz7tewURyZg) | **[Earthworm Jim on SNES](https://www.youtube.com/watch?v=Cz7tewURyZg)** |
| [![Sonic the Hedgehog](https://img.youtube.com/vi/z7zlLLQVhZQ/mqdefault.jpg)](https://www.youtube.com/watch?v=z7zlLLQVhZQ) | **[Sonic the Hedgehog on Mega Drive: RGB vs composite](https://www.youtube.com/watch?v=z7zlLLQVhZQ)**<br>The waterfall: stripes on RGB, blended and translucent on composite. |
| [![Cannon Fodder](https://img.youtube.com/vi/lyLQ_6vd3tI/mqdefault.jpg)](https://www.youtube.com/watch?v=lyLQ_6vd3tI) | **[Cannon Fodder in Amiberry](https://www.youtube.com/watch?v=lyLQ_6vd3tI)**<br>Amiga 1084S preset in Amiberry. |
| [![Super Stardust](https://img.youtube.com/vi/DgMnenye7sw/mqdefault.jpg)](https://www.youtube.com/watch?v=DgMnenye7sw) | **[Super Stardust (AGA) in Amiberry](https://www.youtube.com/watch?v=DgMnenye7sw)**<br>Amiga 1084S preset in Amiberry. |
| [![Quake II](https://img.youtube.com/vi/BrCiiD1ZSj4/mqdefault.jpg)](https://www.youtube.com/watch?v=BrCiiD1ZSj4) | **[Quake II in 86Box](https://www.youtube.com/watch?v=BrCiiD1ZSj4)**<br>Windows 98 in 86Box. |
| [![Ignition](https://img.youtube.com/vi/xu_d-SCrHds/mqdefault.jpg)](https://www.youtube.com/watch?v=xu_d-SCrHds) | **[Ignition in 86Box](https://www.youtube.com/watch?v=xu_d-SCrHds)**<br>Windows 98 in 86Box. |
| [![Commander Keen 4](https://img.youtube.com/vi/DtX0MeD9JRU/mqdefault.jpg)](https://www.youtube.com/watch?v=DtX0MeD9JRU) | **[Commander Keen 4 in 86Box](https://www.youtube.com/watch?v=DtX0MeD9JRU)**<br>Windows 98 in 86Box. |
| [![Prince of Persia](https://img.youtube.com/vi/GueduP2tdMc/mqdefault.jpg)](https://www.youtube.com/watch?v=GueduP2tdMc) | **[Prince of Persia in 86Box](https://www.youtube.com/watch?v=GueduP2tdMc)**<br>Windows 98 in 86Box. |

## Quick start (RetroArch)

1. Copy `shaders/lola-retro` into RetroArch's shader folder (**Settings → Directory → Video Shaders** shows where it is).
2. Start a game, open **Quick Menu → Shaders → Load** and pick your system from `lola-retro/systems/curved`
   (or `systems/flat`), for example `snes.slangp`. Each one is the TV or monitor most people had for that system,
   with the system's timing set. The presets by device are in `curved` and `flat`.
3. Video driver must be Vulkan, glcore, D3D11, D3D12 or Metal (the old `gl` driver does not run slang shaders).
   On Windows use Vulkan, or glcore: with D3D11 or D3D12 a full preset takes about 25 seconds to load every time
   a game starts (on a laptop with Intel graphics; Vulkan 3 to 7 seconds, glcore 8 to 13), see
   [Windows](shaders/lola-retro/README.md#windows).
4. HDR display? Use the same presets from `lola-retro/hdr/systems/curved`; setup is in [HDR](shaders/lola-retro/README.md#hdr).
5. Older phone, handheld or weak GPU? Use the same presets from `lola-retro/lite/systems/curved`: about twice as
   fast, the same picture, see [Lite presets](shaders/lola-retro/README.md#lite-presets). Still too slow?
   `lola-retro/super-lite/systems/curved` is about three times as fast, with small compromises, see
   [Super lite presets](shaders/lola-retro/README.md#super-lite-presets).

Default core settings are fine for most systems. The few that matter are in
[RECOMMENDED-CORES.md](shaders/lola-retro/RECOMMENDED-CORES.md).

Using Amiberry or 86Box instead? See [Amiberry](#amiberry) and [86Box](#86box) below. Making a game in Unity?
See [Unity](#unity).

Every preset also comes in a `flat/` version without curvature:

![Curved and flat](docs/curved-vs-flat.jpg)

## Raw pixels, composite, RGB

Full-resolution RetroArch screenshots. The bottom row is a 1:1 crop of each.

**Sonic the Hedgehog (Mega Drive).** The background is drawn with 1-pixel vertical stripes. The Mega Drive's
pixel clock puts those stripes right next to the colour subcarrier, so composite turns them into blended colour
and a rainbow shimmer. RGB keeps the stripes.

How strong that rainbow was depended on the console and the TV. Early Model 1 Mega Drives had a cheap encoder
with weak filters and showed it strongly; later models and TVs with a comb filter showed much less. The default is
a typical console. Set **Luma trap in the console** to 0 for an early Model 1, or to 1 for a later model.

![Sonic: raw, composite, RGB](docs/sonic-raw-composite-rgb.jpg)

**Super Mario Bros. (NES).** Composite softens colour and lets it bleed past the edges, and the dithered side
of the pipe melts into a smooth shade. RGB stays sharp, only rounded by the beam.

![Mario: raw, composite, RGB](docs/mario-raw-composite-rgb.jpg)

## Optional: dither blend on RGB

Prefer the clean RGB picture but want the dithering blended? Turn on **Dither blend on RGB and S-Video** in the
shader parameters. It takes out only the stripes that alternate from one pixel to the next, so Sonic's background
and Mario's pipe blend without composite's rainbow and blur. It is off by default because no real TV did this;
it is modern processing, like the notch filter of the RetroTINK 4K Pro.

To blend as much as the composite presets do: on NTSC, 1 for 320-wide modes (most PlayStation games, Mega Drive
H40) and 0.5 for 256-wide modes (NES, SNES, Master System, Mega Drive H32). PAL composite blended much less, about
0.45 and 0.1, because its colour subcarrier sits further from the stripes.

Or turn on **Dither blend auto**, and the shader works that amount out itself, from its own composite filters: for
the mode the game is in (it follows a Mega Drive game that switches between 256 and 320 pixels), for NTSC or PAL
and for the TV's settings. Like composite, it takes out all of the stripes' colour and that share of their
brightness. It works on the consoles and the Amiga, which most people played through composite; arcade boards
(RGB monitors) and computer monitors keep Dither blend as you set it. For PAL or NTSC it uses TV standard, whose auto
setting goes by the core's frame rate in RetroArch 1.20 and newer and by the line count in older versions. The line
count takes PAL games with 224 or 240 lines (most PAL SNES games) for NTSC, so on an older RetroArch set TV standard
to PAL for those. It only knows 1-pixel stripes: wider patterns stay as they are.

![Dither blend off and on, with composite for comparison](docs/dither-blend-sonic.jpg)

## Colour like the TV you had

An American TV did not decode colour by the book. Its decoder shifted the colour axes and added red gain
("red push") for warmer skin tones, so yellows leaned orange and reds were stronger, and its phosphors were
not today's sRGB colours either. The presets follow the signal: NTSC games get a US TV decoder (Sony CXA2025AS)
and SMPTE-C phosphors, PAL games a standard decoder and EBU phosphors. In this frame the lavender sky turns blue
and the bricks turn orange-red through the US TV decoder.

![Standard decoder and US TV decoder](docs/tv-colour-us-vs-pal.jpg)

## TV show (broadcast)

The **TV show (broadcast)** preset shows a game the way it looked on a TV programme about games. The picture went
from the console through the studio, the transmitter and a roof antenna to the same living-room TV. On the way
the gaps between the lines were filled, so the picture is smoother and cleaner than on the composite cable at home.
How it works: [TV show](shaders/lola-retro/README.md#tv-show).

It suits PlayStation games best. The jagged polygon edges and the blocky textures soften, as they did on TV.

![PlayStation: raw pixels and TV show](docs/tv-show-ps1.jpg)

**Crash Bandicoot, Klonoa and Need for Speed III (PlayStation)** at 2x internal resolution (640x480), which makes
the polygon edges less jagged. For a 480-line frame set **Console timing** to 4 (PlayStation); in auto mode it is
read as an interlaced picture.

It works on the older consoles too. The pixels lose their hard edges and dithering blends into smooth shades.

![NES and SNES: raw pixels and TV show](docs/tv-show-nes-snes.jpg)

**Bionic Commando (NES) and Super Mario All-Stars (SNES)** at their native resolution.

## PC monitor, in millimetres

A PC monitor was not a TV. It ran at 31 kHz, drew 320×200 games twice (400 lines), and its beam and dot mask were
much finer. The PC Monitor preset describes a typical mid-90s 15-inch monitor the way its spec sheet would:
14-inch picture, 0.28 mm dot mask, a beam spot of 0.30–0.45 mm. Every mode follows from that one tube:
320×200 gives chunky pixels with fine lines you only see up close, 640×480 is sharp enough for 1-pixel dots,
and 1024×768 is a little soft, as it really was on a 15-inch screen. Four more presets put the same 15-inch
tube in better monitors (good, premium, premium+), up to `extreme`, sharper than any real tube, for long
work on the desktop.

![PC monitor at 320x200, 640x480 and 1024x768](docs/pc-monitor-modes.jpg)

The Amiga 1084S preset is built the same way, from the monitor's service manual: 0.42 mm slot mask, 6.5 MHz
amplifier, D65 white, and the picture as owners set it up, nearly filling the glass. Because its beam is described in
millimetres, NTSC games (200 lines, further apart) show stronger lines than PAL games (256 lines), as on the
real monitor. The beam was calibrated on a photo of a real 1084S.

![The same text on the 1084S in PAL and NTSC](docs/amiga-1084s-pal-ntsc.jpg)

## Around the tube

On a large display the tube can be drawn at its real size, with the monitor or TV around it: enter your
screen's height under **Real size** and set **Around the tube** to 1. In RetroArch set **Aspect Ratio** to
*Full* so the surroundings fill the whole screen. Amiberry and 86Box have the same settings.

Each casing is measured on photos of real ones and drawn in millimetres, like the tube. The Amiga preset gets
a Commodore monitor (after the M1438S), the PC presets a 90s PC monitor (after a Compaq 151FS), and the TV
presets a dark 90s TV with speakers and buttons under the screen, which grows with **Monitor size**.
**Room light** sets the room, from a dim room to daylight, and the screen lights the walls around the glass
in its own colours, changing with the picture.

![Amiga monitor, PC monitor and TV in a lit room](docs/around-the-tube-casings.jpg)

<sub>Real size on a screen 39.5 cm tall, Room light 6. All three at the same scale: the 14-inch Amiga monitor
is smaller than the 15-inch PC monitor and TV.</sub>

Around the tube 2 to 11 put the monitor in front of a scene instead, ten in all: floating in space, a synthwave
sunset, a 90s tiled wallpaper, bouncing lines, a sea floor, Amiga copper bars, an Amiga demo screen, a 16-bit
landscape, a city at night and an arcade carpet. They all move; **Scene speed** slows them down or stops them.
The list is in [Scenes](shaders/lola-retro/README.md#scenes), all the settings in
[Parameters](shaders/lola-retro/README.md#parameters).

| | |
|---|---|
| ![2 Space](docs/scene-02-space.jpg) **2 Space** | ![3 Synthwave](docs/scene-03-synthwave.jpg) **3 Synthwave** |
| ![4 Tiles](docs/scene-04-tiles.jpg) **4 Tiles** | ![5 Bouncing lines](docs/scene-05-lines.jpg) **5 Bouncing lines** |
| ![6 Underwater](docs/scene-06-underwater.jpg) **6 Underwater** | ![7 Copper bars](docs/scene-07-copper.jpg) **7 Copper bars** |
| ![8 Amiga demo](docs/scene-08-amiga-demo.jpg) **8 Amiga demo** | ![9 Hills](docs/scene-09-hills.jpg) **9 Hills** |
| ![10 Night city](docs/scene-10-city.jpg) **10 Night city** | ![11 Arcade carpet](docs/scene-11-carpet.jpg) **11 Arcade carpet** |

<sub>Around the tube 2 to 11, Room light 3.</sub>

## Amiberry

The Amiga 1084S preset also comes as GLSL for [Amiberry](https://amiberry.com), the stand-alone Amiga
emulator: copy [`amiberry/lola-retro`](amiberry/lola-retro) into Amiberry's shader folder and choose
`lola-retro/amiga-1084s.glslp` (or `amiga-1084s-flat.glslp`). Same picture as in RetroArch; setup and settings in its [README](amiberry/lola-retro/README.md).

![Cannon Fodder and Super Stardust AGA in Amiberry with the 1084S preset](docs/amiberry-1084s.jpg)

<sub>Amiberry with the 1084S preset: Cannon Fodder (PAL) and Super Stardust (AGA). The dithering stays visible as a
fine texture, the lines show in darker areas, and the picture sits in the black border of the real monitor.</sub>

## 86Box

The PC monitor presets also come as GLSL for [86Box](https://86box.net), the PC emulator: with the OpenGL
renderer, add one of the presets from `86box/lola-retro` in **View → Renderer options…**. Same picture as in
RetroArch, from text mode and 320×200 up to 1024×768; setup and settings in its [README](86box/lola-retro/README.md).

![Windows 98 in 86Box with the premium PC monitor preset](docs/86box-win98.jpg)

<sub>A Windows 98 frame from 86Box at 1024×768 through `pc-monitor-vga-premium`, rendered the way 86Box runs it
on a 3840×2560 screen.</sub>

Five presets put the same 15-inch tube in different monitors, from an average one to `extreme`, which is
sharper than any real tube and easy on the eyes for long work on the desktop (each also comes flat, as `-flat.glslp`):

![The same dialog through the five PC monitor presets](docs/86box-pc-presets.jpg)

<sub>The same part of the screen through each preset, 1:1 on that 3840×2560 screen. The average monitor is soft at
1024×768, as many were; the better ones keep the text sharp; `extreme` shows the gaps between the lines.</sub>

## Unity

The whole shader also comes as a package for [Unity](https://unity.com), for games with a retro look: every pass,
preset and parameter of the RetroArch version, in URP (Unity 6), HDRP and the Built-in render pipeline, on SDR
and HDR displays, in XR and on the web (WebGL 2). In the Package Manager, **Install package from git URL…** with

```
https://github.com/zoran123456/lola-retro.git?path=/unity/lola-retro
```

then put **Lola Retro** on the camera and pick a preset (in URP add the Lola Retro renderer feature too, in HDRP its
custom post-process). The
game can render at the screen's resolution, Lola Retro makes the console's picture from it, or into a
low-resolution render texture for pixel-exact games. The passes are translated from the slang shaders by
`tools/make_unity.py` and give the same picture as RetroArch. Setup and settings in its [README](unity/lola-retro/README.md).

## Presets

| | |
|---|---|
| ![](docs/consumer-tv-composite.jpg) **Consumer TV (Composite)**<br>Start here. The TV most people had. | ![](docs/consumer-tv-scart-rgb.jpg) **Consumer TV (SCART RGB)**<br>Same TV, clean picture. |
| ![](docs/trinitron-s-video.jpg) **Trinitron (S-Video)**<br>PS2, GameCube, N64. | ![](docs/old-tv-rf.jpg) **Old TV (RF)**<br>Antenna cable, snow and ghosting. |
| ![](docs/pc-monitor-vga.jpg) **PC Monitor (VGA)**<br>DOS and Windows 9x games, Dreamcast VGA. | ![](docs/amiga-1084s.jpg) **Amiga 1084S**<br>Amiga and 15 kHz arcade. |

Also included: **Studio Monitor (RGB)** for the PVM look, **Studio Monitor (Composite)** for a PVM on composite, **CRT Projector** for 24 kHz arcade games, four
sharper PC monitors (see [PC monitor, in millimetres](#pc-monitor-in-millimetres)), and **TV show (broadcast)**, a
test: games as you saw them on a TV programme about games (see [TV show (broadcast)](#tv-show-broadcast)).
Which preset and settings to use per system: [RECOMMENDED-CORES.md](shaders/lola-retro/RECOMMENDED-CORES.md).

## What is simulated

- **Composite and RF signal.** RGB is encoded to YUV and QAM-modulated onto the 3.58 MHz (NTSC) or 4.43 MHz (PAL)
  subcarrier, with each console's real pixel clock and subcarrier phase per line and per field.
  SNES (227⅓ cycles per line) crawls diagonally, Mega Drive (exactly 228) stands still, PlayStation (227½) flips every line.
  On RF (and on a TV show) the TV's IF filter keeps the picture below about 4.2 MHz (NTSC) or 5 MHz (PAL), so the
  1-pixel stripes of 512- and 640-wide modes do not get through.
- **The TV's decoder.** A luma trap or a 2-line comb filter, narrow consumer chroma bandwidth, PAL delay line,
  automatic gain and colour control, and the TV knobs (sharpness, colour, tint, brightness, contrast).
- **S-Video and RGB** skip the parts of that chain they skipped in real life.
- **Electron beam.** Each line is a spot whose width grows with brightness, in both directions and per colour gun.
  Bright detail merges and rounds off, dark detail stays sharp. Interlaced fields alternate; VGA 200-line modes are drawn twice.
- **Phosphor mask.** Aperture grille (with Trinitron damper wires), slot mask, shadow mask, or a projection screen,
  at the tube's real size, or drawn on whole screen pixels for lower-resolution displays (no moiré).
- **Monitors in millimetres.** PC monitors (31 kHz) and the Amiga 1084S use a tube described in millimetres (size,
  mask pitch, beam spot on dark and on white, larger in the corners), so 320×200, 640×480, 800×600 and 1024×768 each
  look as they did on that monitor, and NTSC Amiga games show stronger lines than PAL ones.
- **Colour of the TV.** US and Japanese TVs demodulate with "red push" (axes and gains from the Sony CXA2025AS
  datasheet), PAL TVs by the standard; phosphors are SMPTE-C, EBU or Japanese P22 instead of sRGB.
- **Glass.** Curvature (the glass bulges, the raster on it stays nearly rectangular, as the deflection was corrected), halation, white point (6500–9300 K), vignette, room reflection, misconvergence, afterglow
  (RetroArch only: Amiberry and 86Box have no feedback textures).
- **Around the tube.** The monitor or TV at its real size, its casing measured on real ones and lit by the room
  and by the picture. Or, just for fun, one of ten moving scenes.
- **Internal resolution.** PS1 and PS2 cores running at 2× and up are read as blocks of one console pixel,
  so the signal stays right and the extra detail only makes edges smoother.
- **HDR output.** On an HDR display the phosphor dots and scanline centres get the brightness a real tube
  had, instead of being squeezed under the SDR white level. The `hdr` presets write HDR10 themselves (RetroArch only).

## Tested against test patterns

The chain is checked with measured patterns, not only by eye.

**NTSC test patterns** ([patterns.wrwetzel.com](https://patterns.wrwetzel.com)). On composite the fine vertical
stripes and checkerboards turn into rainbow, and the resolution wedge shows colour where the lines get close to the
subcarrier. RGB shows none of that. Colour bars come out the same on every cable.

![NTSC test patterns](docs/ntsc-patterns.jpg)

**[240p Test Suite](https://junkerhq.net/240p/) on the Mega Drive.** Colour Bleed (1-pixel stripes) and
Checkerboard, the two patterns that show what composite does to a Mega Drive. On composite the white stripes become
a full rainbow and the coloured ones beat against the subcarrier. On SNES the same test gives a much weaker rainbow,
because its pixel clock puts the stripes further from the subcarrier. Nothing in the shader is tuned for this;
it follows from each console's real timing.

![240p Test Suite, Mega Drive](docs/240p-suite-mega-drive.jpg)

**PC monitor.** The same patch of glass in four PC modes: 1-pixel stripes both ways and a 30% grey area. In
320×200 the stripes are fully resolved and the lines show in the grey; by 1024×768 the stripes have almost
merged, as they did on a 15-inch tube, whose beam spot was about 1.6 pixels wide at that resolution.

![PC monitor test patterns](docs/pc-monitor-patterns.jpg)

Measured on synthetic patterns:

| Test | Result |
|---|---|
| 75% colour bars, every cable, NTSC and PAL | within about 2/255 of the source |
| Alternating lines (light output) | 0.4996 of white, 0.5 expected: the beam conserves energy |
| Composite at the subcarrier (3.58 MHz) | luma notched out, the energy shows up as colour (the rainbow) |
| Comb filter and S-Video | no false colour |
| RGB bandwidth | about 6.5 MHz, like a consumer TV's video amplifier |
| PC monitor (`pc-monitor-vga`), 320×200 to 1024×768 | spot width, 1-pixel stripe contrast, line structure and brightness within 2% of the physics |
| Amiga 1084S | line contrast inside text matched to a photo of a real monitor; NTSC 40%, PAL 27% in the same text |

## What is in here

| Folder | Contents |
|---|---|
| `shaders/lola-retro/` | The RetroArch shader pack (slang): one preset per system in `systems/`, and 15 presets by device, each in a `curved/` and a `flat/` version, plus the same for HDR displays in `hdr/` and for weak GPUs in `lite/` and `super-lite/`. Details in its [README](shaders/lola-retro/README.md). |
| `amiberry/lola-retro/` | The Amiga 1084S preset converted to GLSL for Amiberry. Details in its [README](amiberry/lola-retro/README.md). |
| `86box/lola-retro/` | The PC monitor presets converted to GLSL for 86Box. Details in its [README](86box/lola-retro/README.md). |
| `unity/lola-retro/` | The Unity package: every pass converted to HLSL, with all presets. Details in its [README](unity/lola-retro/README.md). |
| `unity/test-project/` | A small Unity project that shows the package's Demo, and makes it. Details in its [README](unity/test-project/README.md). |
| `unity/asset-store/` | The Unity Asset Store listing: description, upload steps and pictures, and the project the Asset Store version is uploaded from. |
| `web/lola-retro.html` | The original WebGL version. Open it in a browser, try test scenes or drop in your own screenshots. |
| `tools/` | Preset generator, GLSL and Unity converters, compile checker and headless preview renderers. |
| `test-images/` | Native-resolution test frames for the preview tools. |
| `docs/` | Screenshots used in this README. |

## Tools

```
python3 tools/make_presets.py     # regenerate the systems/, curved/, flat/ and hdr/ .slangp files from one table
python3 tools/make_glsl.py        # regenerate the Amiberry and 86Box versions (amiberry/, 86box/) from the slang passes
python3 tools/make_unity.py       # regenerate the Unity package's passes and tables (unity/) from the slang passes (glslang, spirv-cross)
python3 tools/check_shaders.py    # compile every pass (slang, GLSL and Unity's HLSL) with glslangValidator
tools/render-preview.sh PRESET IMAGE OUT.png [glcore|vulkan]   # Linux: render a frame in headless RetroArch
tools/amiberry-preview.py PRESET.glslp FRAME.png OUT.png       # render a frame the way Amiberry does (moderngl)
tools/86box-preview.py PRESET.glslp FRAME.png OUT.png          # render a frame the way 86Box does (moderngl)
tools/unity-preview.py PRESET FRAME.png OUT.png --compare RA.png  # the way the Unity package does, against RetroArch (moderngl, spirv-cross)
tools/webgl-preview.py PRESET FRAME.png OUT_DIR                   # a page that runs the Unity passes in WebGL 2 against RetroArch
tools/make_store_images.py                                        # the Unity Asset Store pictures (unity/asset-store), rendered in Unity
tools/make_asset_store_project.py                                 # the Asset Store version: the package as Assets/Lola Retro of the upload project
tools/make_manual.py                                              # the Unity package's PDF manual, from its README (macOS)
```

## License

MIT, see [LICENSE](LICENSE). Game screenshots are shown only to demonstrate the shader; the games belong to their owners.
