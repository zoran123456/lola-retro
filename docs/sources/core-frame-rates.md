# Core frame rates: what RetroArch passes as OriginalFPS

Researched 2026-10-24 for a better console guess (`autoConsole`, `getTiming` in `common.inc`) and the
automatic Dither blend, whose amount depends on NTSC or PAL. Lola Retro guesses the console from the frame size
alone: PAL from the line count (over 240), so PAL games with 224 or 240 lines run as NTSC; Beetle Saturn's
352x224 gets the Mega Drive's timing, PlayStation games 256 wide the SNES row, and the X68000's 256-line
frames need Console timing 11. This note gives the frame rate each core reports, measured where the core and a
game were at hand, and read from the core's source otherwise. TV standard auto uses it (below); the console
guess does not yet.

## What RetroArch passes

- `OriginalFPS` is `(float) av_info.timing.fps` (`gfx/video_driver.c`, `video_driver_get_original_fps`,
  RetroArch v1.22.2). The core sets it in `retro_get_system_av_info` and changes it with
  `RETRO_ENVIRONMENT_SET_SYSTEM_AV_INFO`; `SET_GEOMETRY` leaves it as it is. The Metal, Vulkan, glcore, D3D11
  and D3D12 drivers copy it into every pass every frame (`metal.m`, `shader_vulkan.cpp`, `d3d11.c`,
  `d3d12.c`: `pass[i].original_fps = video_driver_get_original_fps();`).
- RetroArch changes it in one place: `video_display_server_restore_refresh_rate` (Automatic refresh rate
  switch) writes the display's original rate into it when the switch is undone.
- It came with RetroArch 1.20.0 (CHANGES.md: "Add CoreFPS and FrameTimeDelta uniforms"; in the code the
  uniform is `OriginalFPS`). `glslang_util.c` then adds `#define _HAS_FRAMETIME_UNIFORMS` to every slang
  pass, so a shader can test for it. Older RetroArch, the Amiberry, 86Box, Kodi and Unity ports have no
  such uniform.
- `FrameTimeDelta`, the other uniform, is the time between two frames on the computer running the emulator
  (`cpu_features_get_time_usec`). It says nothing about the console: 120 to 16700 us in the runs below.

## How it was measured

RetroArch 1.22.2 on macOS (M4 Pro), the cores installed there on 2026-10-24, with a temporary config (the
user's config and core options were not touched: md5 checked before and after every run). A one-pass debug
shader wrote `floatBitsToUint(OriginalFPS)`, the frame size and FrameCount into the picture as bytes, and a
screenshot after N frames (`--max-frames`, `--max-frames-ss`) was decoded, so every value below is the exact
float the shader got. Region options set by hand where the table says so. Audio off, vsync off (the cores ran
as fast as they could).

The value did not depend on the video driver (Mesen: the same bits on Metal and Vulkan; PUAE: on Vulkan and
glcore). Side finding: with vsync off, the Metal driver stopped (main thread waiting for events, no more
frames) after a core's `SET_SYSTEM_AV_INFO` reinitialised the video (PUAE, DOSBox Pure); Vulkan and glcore
did not, so those runs used them.

## Measured

| Core | Game | Region / mode | Frame | OriginalFPS | Float bits | Frames |
|---|---|---|---|---|---|---|
| Mesen | Blaster Master | NTSC | 256x240 | 60.0998268 | 42706639 | 120 |
| Mesen | Blaster Master | PAL, Dendy (`mesen_region`) | 256x240 | 50.0069847 | 42480727 | 120 |
| bsnes-mercury Balanced | 240p Test Suite | NTSC | 256x224 | 60.0988121 | 4270652f | 120 |
| bsnes-mercury Balanced | 240p Test Suite PAL | PAL | 256x224 | 50.0069771 | 42480725 | 120 |
| bsnes 2014 Balanced | 240p Test Suite | NTSC | 256x224 | 60.0988121 | 4270652f | 120 |
| bsnes 2014 Balanced | 240p Test Suite PAL, Pierre le Chef (Europe) | PAL | 256x224 | 50.0069771 | 42480725 | 120 |
| Genesis Plus GX | Aladdin (USA) | NTSC (auto, ntsc-j) | 320x224 | 59.9227448 | 426fb0e4 | 200 |
| Genesis Plus GX | Bubble and Squeak (Europe); Aladdin with region pal | PAL | 256x224, 320x224 | 49.7014580 | 4246ce4b | 200 |
| BlastEm | Aladdin | NTSC | 320x224 | 59.9227448 | 426fb0e4 | 200 |
| BlastEm | Bubble and Squeak (Europe); Aladdin forced E | PAL | 256x240, 320x240 | 49.7014313 | 4246ce44 | 200 |
| PicoDrive | Aladdin; Bubble and Squeak (Europe) | NTSC; PAL | 320x224; 256x224 | 60.0; 50.0 | 42700000; 42480000 | 200 |
| SwanStation | Crash Bandicoot (USA), Klonoa (USA) | NTSC; BIOS, logo and game | 1x1, 1280x956, 1024x480, 640x480 | 59.8173332 | 426f44f3 | 60, 600, 1800 |
| SwanStation | Need for Speed III (Europe) | PAL; BIOS, logo and game | 1x1, 1280x956, 1024x510 | 49.7468185 | 4246fcbe | 60, 600, 1800 |
| LRPS2 | Tony Hawk's Pro Skater 3 (USA) | NTSC, menu and game | 1280x894, 1280x896 | 59.9400558 | 426fc29e | 600, 3000 |
| PUAE 2021 | Turrican (ADF) | PAL, `puae_video_allow_hz_change` locked (default) | 720x287 | 50.0 | 42480000 | 300, 900 |
| PUAE 2021 | Turrican | NTSC, locked | 720x242 | 59.9399986 | 426fc28f | 900 |
| PUAE 2021 | Turrican | PAL, enabled or disabled | 720x287 | 49.9204102 | 4247ae80 | 600 |
| PUAE 2021 | Turrican | NTSC, enabled or disabled | 720x242 | 59.8260994 | 426f4ded | 600, 900 |
| DOSBox Pure | DOOM, Monkey Island | VGA 320x200 | 320x200 | 70.0863037 | 428c2c30 | 30, 900 |
| DOSBox (dosbox_libretro) | DOOM | | 640x400 | 60.0 | 42700000 | 600 |
| FinalBurn Neo | Metal Slug | Neo Geo | 304x224 | 59.18 | 426cb852 | 600 |
| FinalBurn Neo | Magical Cat Adventure | | 320x224 | 60.0 | 42700000 | 600 |
| Image viewer | a PNG | | 320x256 | 60.0 | 42700000 | 60 |

Every one of these matches the core's source exactly (next section). Mesen's NTSC rate is FCEU's fixed-point
constant, 60.0998, not the NES's 60.0988. DOSBox Pure starts at 70.09 Hz in its text mode (log) and sends the
mode's rate with `SET_SYSTEM_AV_INFO` when the mode changes. bsnes-mercury ignored `bsnes_region=pal` for an
NTSC cartridge (it reported NTSC).

## From the source (not measured: core not installed or no game at hand)

Read on 2026-10-24 from the cores' default branches on GitHub (libretro forks unless named).

| Core | Value | Source |
|---|---|---|
| FCEUmm (NES) | as Mesen: 60.0998268 / 50.0069847 (Dendy as PAL); sent again on a region change | `src/drivers/libretro/libretro.c` |
| Nestopia (NES) | as the SNES: 21477272/357366 = 60.0988121, 212813700/(8x531960) = 50.0069771 | `libretro/libretro.cpp`, `NstBase.hpp` |
| QuickNES | 60.0 always | `nes_emu/Nes_Emu.h` |
| MesenCE (Mesen 2's libretro core) | NES and SNES: 60.0988121 / 50.0069771; PC Engine: 21477270/1365/262 = 60.0544434 at load, 263 lines 59.8260994 (not sent again) | `Core/SNES/SnesConsole.cpp`, `Core/PCE/PceConsole.cpp` |
| Snes9x, bsnes | 21477272/357366 = 60.0988121, 21281370/425568 = 50.0069771 | `libretro/libretro.cpp`, `target-libretro/libretro.cpp` |
| Beetle PCE | 7159090.9090909/455/263 = 59.8261070 | `libretro.cpp` |
| Beetle PCE Fast | 59.82 (59.8199997) | `libretro.c` |
| Geargrafx | 21477273/(1365x262) = 60.0544510 at load; 59.8261070 when the game sets 263 lines (VCE bit 2), sent with `SET_SYSTEM_AV_INFO` | `src/huc6260.h` |
| Gearsystem (SMS) | NTSC as Genesis Plus GX, 59.9227448; PAL 49.7014313 | `src/GearsystemCore.cpp` |
| SMS Plus GX | 60.0 / 50.0 | `source/sms.h` |
| Genesis Plus GX, `genesis_plus_gx_vdp_mode` | PAL game at 60 Hz: 59.3761711 (PAL clock, 262 lines); NTSC game at 50 Hz: 50.1589737. The same formula for MD, Mega CD, SMS, Game Gear | `libretro/libretro.c`, `core/system.h` |
| Beetle Saturn | 59.8265038 (`ts_freq / (455*4*263)`), PAL 49.9201279; never changes | `libretro.c` |
| Kronos, YabaSanshiro, Yabause | 60.0 / 50.0 | `yabause/src/libretro/libretro.c` |
| Beetle PSX (HW) | 240p 59.826 (59.8260002), 480i 59.94 (59.9399986), 288p 49.761 (49.7610016), 576i 50.0. Option `beetle_psx_core_timing_fps` auto_toggle (default) switches between them, starting at the interlaced rate until the game sets 240p | `rhi/rhi_intf.h`, `rhi/rhi_intf.c` |
| PCSX ReARMed | 60.0 / 50.0 by default; with `pcsx_rearmed_fractional_framerate` (auto: a few games) SwanStation's 59.8173332 / 49.7468185 | `libpcsxcore/psxcounters.c` |
| Mupen64Plus-Next | 60.0 / 50.0 (by the cartridge's country) | `vi_controller.c` |
| ParaLLEl N64 | at load 48681812/811125 = 60.0176430, PAL 50.0002823; the game's VI rate is sent only when a frame outgrows the declared size | `libretro/libretro.c` |
| Dolphin | 60/1.001 = 59.9400597 at load (PAL Wii games too, PAL60 on by default), PAL 50.0; sent again only across 55 Hz | `Source/Core/DolphinLibretro/Main.cpp` |
| Play! (PS2) | 60.0 always | `Source/ui_libretro/main_libretro.cpp` |
| Flycast | from the SPG registers: 480i and VGA 59.9453011, 240p 59.8266296, PAL 576i 50.0, 288p 49.9201279 (as Beetle Saturn PAL) | `shell/libretro/libretro.cpp`, `core/hw/pvr/spg.cpp` |
| PUAE | `#define PUAE_VIDEO_HZ_PAL 49.920410f`, `PUAE_VIDEO_HZ_NTSC 59.826099f`; locked: 50.0 / 59.94; enabled, interlaced: 50.0002823 / 59.9400520 | `libretro/libretro-core.c`, `sources/src/custom.c` |
| DOSBox Pure | the VGA mode's rate, as a float: 13h 70.0863037, text 720x400 70.0865936, 640x480 59.9404755; `dosbox_pure_force60fps` (off by default) forces 60 or a chosen rate | `dosbox_pure_libretro.cpp`, `src/hardware/vga_draw.cpp` |
| px68k (X68000) | `px68k_adjust_frame_rates` enabled (default): 59.94 for every mode; disabled: 61.46 for every mode. The 55.46 Hz of the 31 kHz modes is never reported (`VID_MODE` never changes) | `libretro.c`, `libretro_core_options.h` |
| NP2kai (PC-98) | 56.4 always | `sdl/libretro/libretro_params.h` |
| FinalBurn Neo | the driver's rate cut to hundredths (`nBurnFPS = (INT32)(100.0 * dFrameRate)`), 60.0 when the driver sets none: CPS1/CPS2 59.63, CPS3 and Neo Geo CD 59.59, Neo Geo 59.18, Toaplan 2 59.63, Toaplan 1 57.61 or 55.16, Midway T/W unit 54.71 | `src/burn/burn.cpp`, drivers |
| MAME (current) | the first screen's refresh as a float if 40-120 Hz, else 60.0 (not checked that the screen is set up before RetroArch asks) | `src/emu/screen.cpp` |
| MAME 2003-Plus | the driver's float (Neo Geo 15625/264 = 59.1856079) | `src/mame2003/mame2003.c` |

## Which rates tell the console

All values as floats, sorted (M measured, S source only):

| OriginalFPS | Bits | | Who |
|---|---|---|---|
| 49.7014313 | 4246ce44 | M | Mega Drive / SMS PAL: BlastEm, Gearsystem |
| 49.7014580 | 4246ce4b | M | Mega Drive / SMS PAL: Genesis Plus GX |
| 49.7468185 | 4246fcbe | M | PlayStation PAL: SwanStation (PCSX ReARMed fractional) |
| 49.7610016 | 42470b44 | S | PlayStation PAL 288p: Beetle PSX |
| 49.9201279 | 4247ae36 | S | Saturn PAL: Beetle Saturn; Dreamcast 288p: Flycast |
| 49.9204102 | 4247ae80 | M | Amiga PAL: PUAE (hz change enabled or disabled) |
| 50.0 | 42480000 | M | many: PicoDrive, SMS Plus GX, Mupen64Plus-Next, Kronos, Yabause, PCSX ReARMed, PUAE locked, and every 576i (LRPS2, Dolphin, Flycast, Beetle PSX) |
| 50.0002823 | 4248004a | S | ParaLLEl N64 PAL; PUAE PAL interlaced |
| 50.0069771 | 42480725 | M | SNES PAL (every core), Nestopia, MesenCE |
| 50.0069847 | 42480727 | M | NES PAL and Dendy: Mesen, FCEUmm |
| 50.1589737 | 4248a2ca | S | Genesis Plus GX, NTSC game forced to 50 Hz |
| 54.71 - 57.61 | | S | arcade (FinalBurn Neo: Midway, Toaplan 1), NP2kai 56.4 |
| 59.18 | 426cb852 | M | Neo Geo (FinalBurn Neo) |
| 59.2717247 | 426d163f | S | SwanStation, PAL game with Force NTSC timings |
| 59.3761711 | 426d8133 | S | Genesis Plus GX, PAL game forced to 60 Hz |
| 59.59, 59.63 | | S | arcade (FinalBurn Neo: CPS1/2/3, Toaplan 2, Neo Geo CD) |
| 59.8173332 | 426f44f3 | M | PlayStation NTSC: SwanStation (PCSX ReARMed fractional) |
| 59.8199997 | 426f47ae | S | PC Engine: Beetle PCE Fast |
| 59.8260002 | 426f4dd3 | S | PlayStation 240p: Beetle PSX |
| 59.8260994 | 426f4ded | M | Amiga NTSC: PUAE (enabled or disabled); PC Engine 263 lines: MesenCE |
| 59.8261070 | 426f4def | S | PC Engine: Beetle PCE, Geargrafx (263 lines) |
| 59.8265038 | 426f4e57 | S | Saturn: Beetle Saturn |
| 59.8266296 | 426f4e78 | S | Dreamcast 240p: Flycast |
| 59.9227448 | 426fb0e4 | M | Mega Drive / SMS NTSC: Genesis Plus GX, BlastEm, Gearsystem |
| 59.9399986 | 426fc28f | M | 59.94 written as such: PUAE NTSC locked (default), px68k (default), Beetle PSX 480i |
| 59.9400520 | 426fc29d | S | PUAE NTSC interlaced |
| 59.9400558 | 426fc29e | M | PlayStation 2: LRPS2 |
| 59.9400597 | 426fc29f | S | GameCube / Wii: Dolphin |
| 59.9404755 | 426fc30c | S | DOS 640x480: DOSBox Pure |
| 59.9453011 | 426fc7fd | S | Dreamcast 480i and VGA: Flycast |
| 60.0 | 42700000 | M | many: PicoDrive, SMS Plus GX, QuickNES, Mupen64Plus-Next, Kronos, Yabause, PCSX ReARMed, Play!, the old DOSBox core, FinalBurn Neo's default, the image viewer |
| 60.0176430 | 42701211 | S | N64: ParaLLEl N64 (at load) |
| 60.0544434, 60.0544510 | 427037c0, 427037c2 | S | PC Engine 262 lines at load: MesenCE, Geargrafx |
| 60.0988121 | 4270652f | M | SNES NTSC (every core), Nestopia, MesenCE |
| 60.0998268 | 42706639 | M | NES NTSC: Mesen, FCEUmm |
| 61.4599991 | 4275d70a | S | px68k with adjusted rates off (every mode) |
| 70.0863037, 70.0865936 | 428c2c30, 428c2c56 | M | DOS VGA 70 Hz modes: DOSBox Pure |

What follows (worked out from the tables):

- **PAL.** Every PAL rate is below 50.2 Hz, every 60 Hz rate at or above 54.7 Hz (the lowest is an arcade
  board; consoles start at 59.27). A limit of 52 Hz separates them by more than 1.8 Hz either way, and it
  needs no list of cores: PicoDrive's round 50.0 and Mupen64Plus-Next's are PAL too. It fixes the PAL games
  with 224 or 240 lines on every PAL core above. It cannot see PAL60 (PS2, Dreamcast, Wii games in 60 Hz
  mode: 59.94 with PAL colour): TV standard set by hand, as the README says. Genesis Plus GX's PAL game
  forced to 60 Hz (59.376) would read as NTSC.
- **Rates that name a console** (matched exactly, bit for bit; some neighbours are close: PS2, GameCube and
  PUAE's interlaced NTSC are one float step apart, Beetle Saturn and Flycast 240p 0.00013 Hz): NES and SNES (60.0988, 60.0998, 50.00698: Console timing 1 either way), Mega Drive and Master
  System (59.92274, 49.7014: timing 2 or 3, by the width), PlayStation on SwanStation and Beetle PSX
  (59.81733, 49.74682, 59.826, 49.761: timing 4), Beetle Saturn (59.82650: 4), PC Engine on Beetle PCE,
  Beetle PCE Fast, Geargrafx and MesenCE at load (59.82611, 59.82, 60.0544: 4), PS2 and GameCube (59.94006: 5),
  Dreamcast (59.94530: 5; VGA cable and TV cannot be told apart), ParaLLEl N64 (60.0176: 4), DOS VGA
  (70.086: 7), PC-98 on NP2kai (56.4: 7), and the arcade rates of FinalBurn Neo (59.18, 59.59, 59.63,
  57.61, 55.16, 54.71: 8).
- **Rates that name nothing:** round 60.0 and 50.0 (a dozen cores), 59.94 written as such (PUAE's NTSC
  default, px68k, Beetle PSX 480i), 59.8260994 (PUAE NTSC and MesenCE's PC Engine), 49.9201279 (Beetle
  Saturn PAL and Flycast 288p). They still say 60 or 50 Hz, nothing more.
- **The 59.82 Hz cluster.** PC Engine, Beetle PSX 240p, Beetle Saturn, Flycast 240p and PUAE NTSC lie within
  0.0007 Hz: all draw 263 lines of 227.5 subcarrier cycles (the Amiga 227.5 colour clocks). Only an exact
  match tells them apart, and all but the Amiga take Console timing 4 anyway (the Amiga is found by its frame
  size first).
- **The X68000 stays as it is.** px68k reports 59.94 (or 61.46) whatever the CRTC does, never the 55.46 Hz of
  its 31 kHz modes, so the frame rate cannot tell a 256-line game at 15 kHz from one at 31 kHz: Console
  timing 11 is still needed.
- **The value can change during a run** (`SET_SYSTEM_AV_INFO`): DOSBox Pure with every video mode, PUAE on a
  PAL/NTSC switch, Beetle PSX between 240p and 480i, Geargrafx between 262 and 263 lines, SwanStation and
  Flycast when the console's timing changes. The shader reads it every frame, so it follows.
- **Cores that crop or add borders.** Once the rate names the console, the frame width no longer has to give
  the pixel clock (`pclk = base * width / nominal`): the console's own mode nearest the width does, and the
  rest is a longer or shorter line, as the Amiga code does now.

Not checked: Genesis Plus GX's Master System mode, 32X and Mega CD were not run (the source gives one formula
for all of them); MAME's first screen rate at load; Flycast's switch between 240p and 480i reaching
RetroArch; Dolphin's rate at run time; Beetle PSX's switch timing.

## Where the code uses it

- `rateStandard()` in `common.inc` (2026-10-24): PAL below 52 Hz, NTSC at 52 or more, nothing when the
  uniform is missing (RetroArch before 1.20, the Amiberry and 86Box ports, where `make_glsl.py` drops the
  `#ifdef`) or the rate is exactly 60.0. Exactly 60.0 is left out because the image viewer, Play! (PAL games
  too) and FinalBurn Neo's default report it whatever the content; the cores that report it for NTSC
  (PicoDrive, SMS Plus GX, QuickNES, Mupen64Plus-Next, Kronos, YabaSanshiro, PCSX ReARMed) send at most 240
  lines a field, which the line count takes as NTSC too. Exactly 50.0 counts: every core found reporting it
  runs PAL content.
- Used for TV standard auto in `getTiming()` (`t.pal`, TV timings only; TV standard set by hand wins), for the
  console's own standard in front of the TV show's standards converter (`showLines`), and for which height
  wins in `upscaleOf()` when two fit. Dither blend auto takes `t.pal`. Where the rate says nothing, all three
  go by the line count as before, so the image viewer and the ports render as they did.
- Checked offscreen (macOS GL 4.1, a debug pass running `getTiming` and `showLines` of `common.inc`, old against
  new): with no uniform, a rate of 0 or exactly 60.0, 0 of 55566 cases differ (49 frame sizes from 1x1 to
  2560x2240, every Console timing, TV standard, Frames over 300 lines, Cable 1, 3 and 4, Monitor in mm on and
  off). With the cores' PAL rates, 224- and 240-line frames turn PAL (and the TV show keeps a PAL game's
  borders); with their NTSC rates, 256- and 287-line frames turn NTSC; a 1440-line frame at a PAL rate is
  288 lines at 5x instead of 240 at 6x. TV standard set by hand, VGA, the X68000, 24 kHz and the computer
  monitor are not affected. Every pass and both ports compile (with and without `_HAS_FRAMETIME_UNIFORMS`).
- Checked in RetroArch 1.22.2 (Vulkan), a debug pass reading `getTiming` with real cores: the PAL games with 224
  and 240 lines (bsnes-mercury and bsnes 2014 with the 240p Test Suite PAL and Pierre le Chef, Mesen PAL,
  Genesis Plus GX, PicoDrive and BlastEm with Bubble and Squeak) are PAL now and were NTSC on main; the NTSC
  games stay NTSC; PicoDrive NTSC (60.0) and the image viewer keep the line count. The whole consumer-tv-composite
  preset on the 240p Test Suite PAL renders the same on auto as with TV standard 2 set by hand (0 pixels
  differ); on the 240p Test Suite NTSC, and with the image viewer (two images, seven presets: composite flat and
  curved, TV show, 1084S, RF, lite, super lite), it renders as on main. (Genesis Plus GX's own picture differs
  from one run to the next at frame 200, so it was checked with the debug pass only.)
- Not yet: the console's row and pixel clock where the rate names the console (the list above).
