# Lola Retro for Kodi

Every preset of [Lola Retro](https://github.com/zoran123456/lola-retro) for [Kodi](https://kodi.tv)'s game
player: the RetroArch shader converted to GLSL, on the same passes and with the same values, so each preset
gives the picture it gives in RetroArch. All fifteen come curved (`curved/`) and flat (`flat/`, no curvature
and square corners), as in RetroArch.

## Install

Kodi's video filter menu lists the presets of the **game.shader.presets** add-on, so Lola Retro goes into
that add-on:

1. Kodi 22 or newer, on a system that runs games with OpenGL or OpenGL ES (Linux, LibreELEC, Android,
   macOS). On Windows Kodi uses Direct3D, which this version can't run.
2. Copy this `lola-retro` folder into the add-on's `resources/glsl` folder, next to the libretro shaders.
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

## For developers

The files in this folder are generated; don't edit them. In the [repository](https://github.com/zoran123456/lola-retro),
change the slang passes in `shaders/lola-retro/shaders` or the presets in `tools/make_presets.py`, then run
`python3 tools/make_glsl.py`. How the conversion works is described at the top of that script.

## License

MIT, see the LICENSE file in this folder.
