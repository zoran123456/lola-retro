# Lola Retro for Kodi

Every preset of [Lola Retro](https://github.com/zoran123456/lola-retro) for [Kodi](https://kodi.tv)'s game
player: the RetroArch shader converted to GLSL, on the same passes and with the same values, so each preset
gives the picture it gives in RetroArch. All fifteen come curved (`curved/`) and flat (`flat/`, no curvature
and square corners), as in RetroArch.

## Install

Kodi's video filter menu lists the presets of the **game.shader.presets** add-on, so Lola Retro goes into
that add-on:

1. Kodi 22.0 RC2 or newer (RC1 doesn't have the fixes these presets need), on a system that runs games with
   OpenGL or OpenGL ES; tested on Linux, LibreELEC and macOS. On Windows Kodi uses Direct3D, which this
   version can't run.
2. Copy this `lola-retro` folder into the add-on's `resources/glsl` folder, next to the libretro shaders.
   On macOS the add-on is inside Kodi.app (`Contents/Resources/Kodi/addons/game.shader.presets`): copy that
   whole folder to `~/Library/Application Support/Kodi/addons/` first and change the copy. Kodi then uses
   the copy, and Kodi.app stays as it was signed.
3. Add the presets you want to the add-on's list: `resources/ShaderPresetsGLSLP_GLES.xml` on OpenGL ES
   (LibreELEC, Android, Raspberry Pi), `resources/ShaderPresetsGLSLP.xml` on OpenGL. One entry per preset:

   ```xml
   <preset>
       <path>glsl/lola-retro/curved/consumer-tv-composite.glslp</path>
       <folder>Lola Retro</folder>
       <name>Consumer TV (composite)</name>
   </preset>
   ```

4. Restart Kodi. In a game, the menu's **Settings → Video Filter** shows them in the folder you gave them.

An update of the add-on replaces its lists, so the entries have to be added again afterwards.

## Kodi settings

| Setting | Use | Why |
|---|---|---|
| Settings → Stretch Mode | **Normal** | The picture area keeps the game's shape, as on a TV. The tube draws its own 4:3 glass around it. |
| Settings → Video Filter | a Lola Retro preset | One filter runs at a time, and the preset needs the emulator's frame as its input. |

## Parameters

Kodi has no screen for shader parameters. A preset is the list of values at the end of its `.glslp`, and
they mean the same as in RetroArch (see the [shader pack's README](https://github.com/zoran123456/lola-retro/blob/main/shaders/lola-retro/README.md)).
To change one, edit its value there, or copy the preset under a new name and list that one as well.

## Differences from the RetroArch version

- No phosphor afterglow: Kodi has no feedback textures. A still picture is the same; moving objects leave
  no faint trail.
- No HDR, lite or per-system presets yet.
- On macOS (the only system where this was checked) Kodi re-encodes every game's picture as if it were
  gamma 2.4, into sRGB, with any video filter, Nearest neighbour too. Dark and middle tones come out darker
  than in RetroArch (a grey of 107 at 99, a dark blue's 33 at 21). Apart from that the presets give the
  same picture as in RetroArch.

## For developers

The files in this folder are generated; don't edit them. In the [repository](https://github.com/zoran123456/lola-retro),
change the slang passes in `shaders/lola-retro/shaders` or the presets in `tools/make_presets.py`, then run
`python3 tools/make_glsl.py`. How the conversion works is described at the top of that script.

## License

MIT, see the LICENSE file in this folder.
