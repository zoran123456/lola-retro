# Recommended cores and settings

Lola Retro simulates the signal the console actually sent, so it needs the console's real pixels.
The simplest way is a preset from `systems/curved` or `systems/flat`: one per system, with its console
timing already set (the system presets are listed in the README). The tables below are for the presets by
device. Three rules cover almost everything:

1. **Internal resolution.** Native (1×) is the reference. Higher internal resolutions work too: the shader reads
   the frame as blocks of one console pixel, so the signal stays right and edges get smoother. 3× and up is
   detected by itself; for 2× and for upscaled 480-line consoles the table says which Console timing to set.
   A PAL game at 5× or more on RetroArch before 1.20: set **TV standard** to 2, as a few heights fit both
   standards (1440 lines are 240 lines at 6× and 288 at 5×); newer versions tell PAL by the core's frame rate.
   Cores that never upscale (Beetle Saturn) or run at 1×: with **Frames over 300 lines** at 1, every frame
   with more than 300 lines is the console's own 480i or 576i, with the Console timing you set.
2. **No filters inside the core.** Turn off any built-in "NTSC", "Blargg", "smoothing" or "blur" filter.
   The shader does that job.
3. **Check the console timing.** Auto mode guesses from the frame size. For systems where the guess is wrong,
   the table says which **Console timing** to set in **Quick Menu → Shaders → Shader Parameters**.
   Then save it with **Shaders → Save → Save Core Preset**, so it applies to every game on that core.

Every preset exists in `curved/` and `flat/`; the tables below apply to both.

Console timing ids: 1 SNES/NES, 2 Mega Drive H40, 3 Mega Drive H32 and Master System, 4 PlayStation,
5 PlayStation 2, 6 Amiga, 7 PC VGA (and PC-98), 8 Arcade 15 kHz, 9 Arcade 24 kHz, 10 X68000, 11 X68000
with 256-line frames at 15 kHz.
Systems that are not in that list use the id whose timing matches theirs.

## 8-bit and 16-bit

| System | Core | Preset | Console timing | Settings |
|---|---|---|---|---|
| NES / Famicom | Mesen, FCEUmm, Nestopia | Consumer TV (Composite) | auto (1) | Built-in NTSC filter off. The NES only ever had composite and RF, so those are the authentic look. |
| SNES / Super Famicom | Snes9x, bsnes | Consumer TV (Composite) or (SCART RGB) | auto (1) | NTSC/blargg filter off, hi-res blending off. 512-wide hi-res frames are handled. |
| Master System | Genesis Plus GX | Consumer TV (Composite) | auto (3) for 256×192; **3** for other frame sizes (borders on) | Same subcarrier rhythm as the Mega Drive in 256-wide mode. |
| Mega Drive / Genesis | Genesis Plus GX | Consumer TV (Composite) | auto (2 for 320 wide, set 3 for 256-wide games) | Blargg NTSC filter off, borders off. The famous transparent waterfalls need composite. |
| Mega CD / Sega CD | Genesis Plus GX | Consumer TV (Composite) | auto (2) | Same as Mega Drive. |
| 32X | PicoDrive | Consumer TV (Composite) | auto (2) | Same as Mega Drive. |
| PC Engine / TurboGrafx-16, PC Engine CD | Beetle PCE, Beetle PCE Fast | Consumer TV (Composite) | **4** (on RetroArch before 1.20 also TV standard 1, NTSC) | Its subcarrier rhythm (227½ cycles per line) matches the PlayStation's. With more than 240 lines shown, an older RetroArch reads the frame as PAL by its line count; from 1.20 the core's frame rate (59.82) says NTSC. |
| Neo Geo (AES/MVS) | FinalBurn Neo | Consumer TV (SCART RGB), or Amiga 1084S for the arcade look | auto | RGB arcade hardware, so composite timing does not matter. |

## Arcade

| Hardware | Core | Preset | Console timing | Settings |
|---|---|---|---|---|
| 15 kHz arcade (CPS1/2, Neo Geo MVS, most 80s and 90s boards) | FinalBurn Neo, MAME | Amiga 1084S | auto, or 8 | Arcade monitors were 15 kHz RGB. Vertical games: RetroArch rotates the whole picture, including scanlines and mask, the same as a monitor turned on its side. The 1084S shows the whole picture with a black border; raise Overscan to fill the screen like an arcade monitor. |
| Medium-res 24 kHz (Sega Model 1/2 at 496×384) | MAME | CRT Projector (deluxe cabinets) or Studio Monitor (RGB) | auto (9) | |

## 32-bit and 64-bit

| System | Core | Preset | Console timing | Settings |
|---|---|---|---|---|
| PlayStation | SwanStation, Beetle PSX HW | Consumer TV (Composite) | auto (4); **4** at 2× internal resolution; at 1× **4** and Frames over 300 lines **1** | Any internal resolution; 1× is the original look. At 1×, Frames over 300 lines 1 draws the 480i games (Tekken 3) in two fields with the PlayStation's own timing; at 2× leave it at 0, or every 2× frame is read as 480i. Dithering on, no texture filtering, no "true colour". PGXP off for the original wobble. Try the comb filter on composite. |
| Sega Saturn | Beetle Saturn | Consumer TV (Composite), or `systems/saturn` (sets both) | **4**, and Frames over 300 lines **1** | Auto picks Mega Drive timing for 320×224 games. Beetle Saturn never upscales: its 448- and 480-line frames are always the console's own 480i (Virtua Fighter 2), and Frames over 300 lines 1 draws them in two fields. At 0 they are read as a 240-line game at 2×, which averages the two fields into one line. (Kronos and YabaSanshiro send native frames at their default resolution; raised, set it to 0.) |
| Nintendo 64 | ParaLLEl N64, Mupen64Plus-Next | Consumer TV (Composite) or (S-Video) | auto (4); **4** at 2× upscaling; at 1× **4** and Frames over 300 lines **1** | Any upscaling; 1× is the original look. Keep the console's own VI filter on for the original look. |

## 128-bit (the PS2 generation)

These consoles mostly output 480i. **No flicker** is on by default, so the two fields are drawn together
and the picture is stable. Turn it off to see the fields alternate like on a real TV.

| System | Core | Preset | Console timing | Settings |
|---|---|---|---|---|
| PlayStation 2 | LRPS2 (PCSX2), Play! | Trinitron (S-Video) or Consumer TV (Composite) | auto (5); **5** when upscaled | Any internal resolution; with upscaling set Console timing 5, otherwise the frame is read as a 240-line mode. |
| Dreamcast | Flycast | Consumer TV (Composite) on TV, PC Monitor (VGA) with the VGA cable | auto (5); **5** when upscaled on TV; 7 is set by the PC Monitor preset | Match the core's cable type option to the preset. |
| GameCube | Dolphin | Trinitron (S-Video) or Consumer TV (Composite) | auto (5); **5** when upscaled | Any internal resolution. |

## Computers

| System | Core | Preset | Console timing | Settings |
|---|---|---|---|---|
| DOS, Windows 9x | DOSBox Pure | PC Monitor (VGA) | 7 (set by the preset) | Every PC mode on one 15-inch monitor: 320×200 is drawn with VGA line doubling (400 lines), 640×480 up to 1024×768 on the same tube. For a sharper Windows desktop use `pc-monitor-vga-premium`, `-premium-plus` or `-extreme`. For 86Box there is a GLSL version of these presets (`86box/` in the repository). |
| PC-98 | Neko Project II kai | `systems/pc-98` or PC Monitor (VGA); HDR: `hdr/curved/pc-monitor-vga` | 7 (auto for 640×400) | 640×400 on a computer monitor: 400 sharp lines, the same picture as VGA's 640×400 on a PC monitor. A real TV could not show the PC-98's 24 kHz picture, so use a computer monitor preset rather than a TV preset. |
| Sharp X68000 | px68k | `systems/x68000` or X68000 monitor (`x68000-monitor`) | **10** (set by the presets); **11** for a game that shows 256 lines at 15 kHz | The X68000's own monitor, the Sharp CZ-600D: 15 kHz modes show gaps between the lines, 31 kHz modes (most games, and the 768×512 command prompt) do not. A 256-line game arrives as 256 rows at either frequency; Console timing 10 takes it as 31 kHz, the usual case. px68k's own menu (F12) is 800×600; after a reset from that menu the core may keep sending 800×600 frames with the picture in the top left corner, so restart the content. |
| Amiga | PUAE | Amiga 1084S | auto (6) | PUAE's default output is recognised (720 wide with the overscan border, which shows like on the real monitor), and so are 320×256 / 640×512 (PAL) and 320×200 / 640×400 (NTSC) without border. With other crop settings, set timing 6 by hand. Keep **Line Mode** at Automatic: forced double lines would be read as an interlaced screen. The preset shows the whole picture with a black border, like the real monitor; raise Overscan to fill the screen. For Amiberry there is a GLSL version of this preset (`amiberry/` in the repository). |

## Not covered

Handhelds (Game Boy, Game Gear, GBA, PSP, DS) had LCD screens, not CRTs, so this shader is the wrong tool for them.
