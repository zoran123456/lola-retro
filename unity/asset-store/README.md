# Lola Retro on the Unity Asset Store

What the Asset Store listing needs, ready to paste into the Publisher Portal. The pictures are in `images/`, made
in Unity by `tools/make_store_images.py` from the Demo's own pictures.

The Asset Store version goes up through the classic workflow (a package draft made with **Create a package**, a
.unitypackage): the folder `Assets/Lola Retro` of `upload-project/`, which `tools/make_asset_store_project.py`
makes from the UPM package (`unity/lola-retro`), the same files with the Demo as an ordinary folder. Run it again
after every change to the package.

**No license file.** Every package on the Asset Store is under the Asset Store End User License Agreement, and a
package with a license of its own is declined ("Sensitive and Restricted Content", request 3612798, 2026-11-16, for
the MIT LICENSE). The script leaves LICENSE out of `Assets/Lola Retro`, gives its README a License section that
names the EULA, makes its PDF manual again from that README, and stops if MIT is still named in a file. The UPM
package and the rest of the repository on GitHub stay MIT.

## Uploading

1. `tools/make_manual.py` when the package's README has changed (the PDF manual the Validator asks for), then
   `tools/make_asset_store_project.py` (needs only Python).
2. Unity Hub: **Add → Add project from disk**, choose `unity/asset-store/upload-project`, and open it with Unity
   6000.6.7f1.
3. Install the [Asset Store Publishing Tools](https://assetstore.unity.com/packages/package/5368745): on that page
   **Add to My Assets**, then in Unity **Window → Package Management → Package Manager → My Assets → Asset Store
   Publishing Tools → Download → Import → Import**.
4. **Tools → Asset Store → Validator → Add a path**, choose `Assets/Lola Retro`, **Validate**, and fix what it
   reports (warnings about textures that are not a power of two are the Demo's pixel art at its own size).
5. **Tools → Asset Store → Uploader**, sign in, choose the draft **Lola Retro - CRT Shader**, the folder
   `Assets/Lola Retro`, **Export and Upload**.
6. In the Publisher Portal, in the draft: the price (free), the texts and pictures below, then **Submit**.

The Unity version the package is uploaded from is, as far as Unity's forums tell, the oldest the Asset Store offers
it for. It is tested in 6000.6; uploading from an older Unity 6 (installed in Unity Hub) reaches more people, once
it is tested there.

**The Dracula picture** (`screenshot-09-dracula-real-crt.jpg`): its second panel is a photo by CRTpixels, and all
four show Konami's Castlevania. The Asset Store asks for content you have the rights to: ask CRTpixels before using
it there, and leave it out if Unity's review objects. Every other picture is the Demo's own.

## Publisher profile

**Promo banner:** `images/promo-banner-3000x1000.jpg` (shown at the top of the publisher page during a discount;
the TV is in the middle, so the portal can cut it narrower)

**Headline** (60 characters at most):
Free CRT shader that simulates the whole analog TV

**Paragraph** (300 characters at most):
I make Lola Retro, a CRT shader that recreates how 80s and 90s games really looked on a TV: the console's video
encoder, the cable, the electron beam, the phosphor mask and the curved glass. It began in RetroArch and is now free
for Unity. Open source on GitHub.

## Listing

**Name:** Lola Retro – CRT Shader

**Category:** Tools / Camera, or VFX / Shaders (Fullscreen & Camera Effects)

**Price:** Free

**Tagline (short description):**
A CRT shader that simulates the whole analog chain, not just scanlines. One component on your camera.

**Description:**

Make your game look like it ran on a real TV or monitor of the 80s and 90s.

Lola Retro does not draw scanlines on top of your pixels. It simulates the whole way a console's picture took to the
glass: the console's video encoder, the cable, the TV's decoder, the electron beam, the phosphor mask and the
glass. So composite blends dithering into new colours and makes 1-pixel stripes shimmer with a little rainbow, RGB
keeps them sharp, bright lines merge while dark ones show gaps, and the mask and the curved glass are drawn at your
screen's resolution.

**Easy to start**
1. Add Lola Retro to your camera (Add Component, Lola Retro).
2. If the component shows a Fix it button (URP and HDRP), press it.
3. Pick a preset and press Play.

The Demo shows it at once: open the scene Lola Retro/Demo/Lola Retro Demo, press Play, and change the TV with the
arrow keys.

**Presets**
- Consumer TV on composite, SCART RGB, S-Video and RF, an old TV, a Sony Trinitron, a Sony PVM studio monitor
- A CRT projector, five PC monitors (VGA, from an average 15-inch to sharper than any real tube), the Commodore
  1084S Amiga monitor
- A TV show: games as they looked on a TV programme about games
- One preset per system: NES, SNES, Master System, Mega Drive, PC Engine, PlayStation, Saturn, N64, PlayStation 2,
  GameCube, Dreamcast, 15 kHz arcade, Amiga, DOS PC, PC-98

**What is simulated**
- Composite and RF: each console's real pixel clock and colour subcarrier, so the SNES dots crawl, the Mega Drive's
  rainbow stands still and the PlayStation's flips every line
- The TV's decoder: luma trap or comb filter, PAL delay line, the knobs (sharpness, colour, tint, brightness,
  contrast), US and Japanese "red push"
- The electron beam, per colour gun, growing with brightness; interlace
- Aperture grille, slot mask, shadow mask or projection screen
- Curved glass, halation, white point, vignette, misconvergence, phosphor afterglow
- Monitors described in millimetres (size, dot pitch, beam spot), so every resolution looks as it did on that tube
- Around the tube: the TV or monitor at its real size in a room, or in one of ten moving scenes
- HDR displays: the phosphor dots and line centres use the display's headroom

**For your game**
- Built-in render pipeline, URP (Unity 6, Render Graph) and HDRP
- Pixel art at its own resolution (a render texture), or any game made into a 240-line picture
- 4:3 or widescreen tubes; a TV in your game's world (a camera with Lola Retro rendering into a render texture)
- Every parameter can be changed from a script while the game runs (an options menu with cables and presets)
- Desktop and WebGL 2; XR

**Technical details**
- Unity 6 (6000.0) or newer
- The whole chain takes 2 to 3 ms per frame at 1080p to 1440p on an Apple M4 Pro (measured in WebGL 2); integrated
  graphics from the last few years should be fine at 1080p
- The same picture as the RetroArch version it is made from, checked pixel for pixel; the RetroArch shader is on GitHub:
  https://github.com/zoran123456/lola-retro
- Documentation: the README in the package, and https://github.com/zoran123456/lola-retro/tree/main/unity/lola-retro

**Keywords:** crt, retro, shader, post processing, scanlines, composite, ntsc, pal, pixel art, tv, monitor, arcade,
vhs, 8-bit, 16-bit, ps1

## Pictures

| Field | File |
|---|---|
| Icon (160 × 160, no text) | `images/icon-160x160.png` |
| Card (420 × 280) | `images/card-420x280.png` |
| Cover (1950 × 1300) | `images/cover-1950x1300.jpg` |
| Social media (1200 × 630, no text) | `images/social-1200x630.jpg` |
| Publisher profile's promo banner | `images/promo-banner-3000x1000.jpg` |
| Screenshots | `images/screenshot-01` to `-09` (`-09` is the Dracula comparison, see above) |

Screenshot captions:
1. A 90s TV in front of the synthwave scene (Around the tube)
2. The raw pixels and the same part of the picture on a consumer TV on composite
3. A Mega Drive waterfall: composite (left) blends the stripes into a translucent waterfall, RGB (right) keeps them
4. A mid-90s 15-inch PC monitor with a DOS game, in a room
5. The Commodore 1084S with an Amiga game, in front of the Amiga demo scene
6. An old TV on the antenna cable: snow and ghosting
7. A Sony Trinitron on S-Video, in front of the night city scene
8. A TV show: the game as it looked on a TV programme about games
9. Raw pixels, a real Sony Trinitron on composite (photo by CRTpixels), and Lola Retro
