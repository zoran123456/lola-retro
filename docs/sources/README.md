# Sources and research notes

Why the shader uses the values it uses: the sources behind them, what was measured or worked out, what
could not be found, and what the code does with it. One file per topic. These notes are not part of the
release zips (those are made from `shaders/lola-retro`, `amiberry/lola-retro` and `86box/lola-retro`).

Sources are trusted in the order CLAUDE.md gives: spec sheets, service manuals and measurements (emulator
source code that follows the hardware counts as a measurement of it); then photos of a real screen (beam,
line gaps, geometry, not colour); last, how people remember it. Every note says which kind each fact is,
and marks what was worked out (inferred) rather than read.

| Note | Used in |
|---|---|
| [high-res-frames.md](high-res-frames.md) | Frames over 300 lines (`LR_HIRES`), issue #9 |
| [480i-field-timing.md](480i-field-timing.md) | subcarrier phase per field of 480i/576i on Console timing 4 (`getTiming`) |
| [saturn-cores.md](saturn-cores.md) | the `systems/saturn` preset |
| [x68000-video.md](x68000-video.md) | the X68000 monitor model: video modes, what px68k sends |
| [x68000-monitors.md](x68000-monitors.md) | the X68000 monitor model: the monitors |
| [lite-presets.md](lite-presets.md) | the `lite/` and `super-lite/` presets (issue #12): what each pass costs, what was left out, speeds users reported |
| [internal-resolution.md](internal-resolution.md) | upscaled frames (`upscaleOf`, the native pass), issue #14 |
| [dither-blend.md](dither-blend.md) | which Dither blend (`LR_DBLEND`) matches composite (README); Dither blend auto (`ditherBlend`) |
| [mask-moire.md](mask-moire.md) | the mask at the tube's size on 1080p: moiré, and the shoulder per mask point (`maskPoints`, the CRT pass) |
| [composite-luma-bandwidth.md](composite-luma-bandwidth.md) | composite luma at 5-6 MHz: the consoles' encoder networks, TV decoders, the IF filter of RF and the TV show (`IF_NTSC`, `IF_PAL`), Luma trap in the console 0 for the NES and SNES |
| [windows-test.md](windows-test.md) | the presets on Windows (D3D11, D3D12, Vulkan, glcore), an Intel laptop: pictures, loading times, speed |
| [core-frame-rates.md](core-frame-rates.md) | the frame rate each core reports (`OriginalFPS`), measured and from source: which rates tell PAL and the console; TV standard auto (`rateStandard`, `getTiming`) |
