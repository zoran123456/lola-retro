# Sharp X68000 monitors

Researched 2026-10-22 for the X68000 monitor model (task 2 of issue #9). See also
[x68000-video.md](x68000-video.md) for the video modes.

## Sharp manuals and labels (primary sources)

- CZ-614D manual, specification page (scan 24): https://archive.org/details/sharp-cz-614d-manual
  - 15-inch FS (flat square) tube, high contrast, non-glare, 0.31 mm dot type; picture 27.8 x 20.9 cm,
    35.1 cm diagonal.
  - Video 0.7 Vp-p positive; separate H and V sync, TTL, negative.
  - Timing table (the same in the CZ-605D/613D manual):

    | Mode | Scan rates | Active time (H x V) | Rated resolution |
    |---|---|---|---|
    | 15 kHz | 15.98 kHz x 61.5 Hz | 52.69 us x 15.02 ms | 640 x 200 |
    | 24 kHz | 24.86 kHz x 55.5 Hz | 29.8 us x 16.09 ms | 640 x 400 |
    | 31 kHz | 31.5 kHz x 55.5 Hz | 22.08 us x 16.25 ms | 768 x 512 |

    The active times are whole numbers of lines: 15.02 ms x 15.98 kHz = 240, 16.09 ms x 24.86 kHz = 400,
    16.25 ms x 31.5 kHz = 512 (worked out).
- CZ-605D / CZ-613D manual (OCR text): https://archive.org/details/cz-605-d-cz-613-d_202006
  - The same 15-inch FS dot-type tube and the same 27.8 x 20.9 cm picture; CZ-605D 0.39 mm pitch, CZ-613D
    0.31 mm; three-mode auto scan. "15-inch" is the tube's outer diagonal, not the picture.
- CZ-600DE rear label (auction photo):
  https://cdnyauction.buyee.jp/images.auctions.yahoo.co.jp/image/dr000/auc0105/user/bd9157ad8a19b672410c336d3bb7bd205c2b4a8f5faad4d7967b718cdc326af4/i-img1200x900-174813729979216chxxt2942.jpg
  - A colour TV receiver (VHF/UHF), 100 V, 99 W; inputs: digital RGB (8-pin), analog RGB (15-pin), composite
    video in and out, TV control. No tube data.

## The monitors

From a blog table built from Sharp catalogues (http://tomoretropc.blogspot.com/2019/09/x680x0-rgb.html), a
price list (http://www.x68000-jp.sakura.ne.jp/x68k_shuhenkiki.html), Sharp's model numbers
(http://retropc.net/ohishi/museum/cznum.htm) and GameSX (https://gamesx.com/wiki/doku.php?id=x68000:x68000_monitors).
Years are worked out from the computers each was sold with.

| Model | Size / pitch (mm) | kHz | TV tuner | Notes |
|---|---|---|---|---|
| CZ-600D | 15" / 0.39 | 15/24/31 | yes | digital and analog RGB; with the first X68000 (1987) and the X1turboZ |
| CZ-601D | 15" / 0.39 | 15/24/31 | yes | ACE (1988) |
| CZ-611D | 15" / 0.31 | 15/24/31 | yes | ACE-HD |
| CZ-602D / 612D | 15" / 0.39, 0.31 | 15/24/31 | yes | EXPERT, PRO (1989) |
| CZ-603D | 14" / 0.31 | 15/31 | no | "DUAL SCAN DISPLAY" |
| CZ-604D | 14" / 0.31 | 15/31 (or 15/24/31, sources disagree) | no | |
| CZ-605D / 613D | 15" FS / 0.39, 0.31 dot | 15/24/31 | yes | EXPERT II, PRO II (1990) |
| CZ-606D | 14" / 0.31 | 15/31 | no | |
| CZ-607D | 14" / 0.31 shadow mask | 15/31 (or 15/24/31) | yes | tube E8034B22 (crtdatabase.com) |
| CZ-614D | 15" FS / 0.31 dot | 15/24/31 | yes | tube M36KLJ180X (crtdatabase.com), XVI era (1991) |
| CZ-608D | 14" / 0.28 | 15/31 | no | Compact XVI, X68030 (1992) |
| CZ-615D | 15" / 0.28 or 0.31 | 15/24/31, VGA | yes | X68030 (1993) |
| CZ-621D | 21" / 0.52 | 15/24/31 | no | X68030 |

## Photos (good for line gaps and sharpness, not for colour)

- 15 kHz, CZ-600DE (15 kHz light on, a 1986 Konami title; the computer is not stated):
  https://cdnyauction.buyee.jp/images.auctions.yahoo.co.jp/image/dr000/auc0203/user/911297b3afe95459483f0946ba11e2758ba62f7860e2ca691047992f71625ffd/i-img1200x1200-17730180119407dcikep35.jpg
  Thin dark gaps between the lines, by eye no more than about a third of the line pitch; the dot mask shows.
- 15 kHz, qualitative: https://frogcube.net/2017/02/28/post-415/ compares an arcade monitor with the X68000
  monitor and prefers the arcade one because its gaps are less pronounced, so the X68000 monitor's gaps are
  clear.
- 31 kHz, CZ-601D ("3 MODE AUTO SCAN DISPLAY TV", 31 kHz light on, a boot error box):
  https://i.redd.it/tnl0gdnic74d1.jpeg (4000 px). No gaps, the lines merge; the kana are a little soft.
- 31 kHz, CZ-600DE (a file manager, but scaled to 640x480 by an X68000 Z, not the native 512 lines):
  https://pbs.twimg.com/media/G3cKYyUWYAAJF67.jpg. No gaps, fairly crisp text, mild bloom.

## What the shader does (Console timing 10 and 11, the x68000-monitor preset)

Decided with the author on 2026-10-22, from the notes above and [x68000-video.md](x68000-video.md):

- One tube in mm for every mode (scan mode 3, `x68Raster` in `common.inc`): the CZ-600D's 15-inch size and
  0.39 mm dot (shadow) mask; the CZ-605D's 278 x 209 mm picture for every mode (Overscan -0.02: the shader's
  15-inch tube face is 284 x 213 mm); 240 rasters across that height at 15 kHz, 512 at 31 kHz.
- px68k's rows tell the mode: up to 240 rows 15 kHz; 241-300 rows 31 kHz with every line scanned twice
  (timing 10; timing 11 takes them as 15 kHz); taller frames one raster per row, filling the height.
- RGB only; pixel steps integrated exactly in the beam pass (the PC monitor's path); the amplifier's
  bandwidth was not found, and at these dot clocks (up to 34.8 MHz) the spot, not the amplifier, sets the
  sharpness.
- Not found, so taken from elsewhere: the spot (0.28 mm dark, 0.65 mm white), its growth to the corners
  (1.5x), misconvergence (0.25) and curvature are the 1084S's (a monitor of the same class and years, its
  spot calibrated on a photo); white 9300 K and Japanese P22 phosphors are the Japanese TV standard.
- The casing drawn around the tube (Around the tube) is the TV casing: the CZ-600D was a TV set too.
- A 256-row frame on timing 11 is 256 rasters at 15 kHz in a picture 240 rasters high (the 15 kHz modes'
  figure), so 8 rasters at the top and bottom fall outside it, as a taller window would on the monitor.
  Picture height 1 (`LR_FILL`) fits the rows into the height, a zoom of the same tube as on the TV raster
  (added 2026-10-22 after a comment on issue #9; before, Picture height only applied to the TV raster).
  Since 2026-10-28 it is the monitor's height control instead of a zoom: the 256 rasters move closer together and the spot
  keeps its size in mm, so they merge a little more than 240 do ([arcade-monitors.md](arcade-monitors.md)).
  Checked in RetroArch (Metal, flat x68000-monitor, Overscan 0): a 256-row frame with its top 8 rows red
  and bottom 8 green, timing 11 and Picture height 1, showed only a sliver of each before and both bands in
  full after, at the same height as on timing 10; timing 10, Picture height 0 and 240-row frames gave
  byte-identical pictures before and after.
- Measured from the shader (contrast between line centre and gap, (max - min) / (max + min), linear light,
  centre of a flat screen, mask and glow off), 30% grey / white: 15 kHz 240 lines 87% / 16%; 31 kHz 256 lines
  scanned twice and 768x512 10% / 0.5%; 15 kHz interlaced 512x480 15% / 0.5%. For comparison, the 1084S:
  PAL 76% / 7.5%, NTSC 90% / 20%.
- Checked by eye against the photos (2026-10-22): the CZ-600DE 15 kHz photo, viewed at 3x, shows thin dark
  gaps on bright green and blue, as the model does on bright colours (deeper gaps on darker ones); at about
  2.4 photo pixels per line it is too coarse to measure. The 31 kHz CZ-601D photo (the XVI's boot error box,
  4000 px, about 2 photo pixels per dot and per line) was compared with the same box drawn in a 16-pixel
  kana font through the x68000-monitor preset at the same scale: no gaps between the lines in either, and
  the kana soft but readable in both (in the photo the strokes look darker and heavier, which the phone's
  own blur adds to). Not sharp enough to measure the spot, so the 1084S's spot stays.
- In RetroArch itself (Metal, the built-in image viewer; see high-res-frames.md for how): 240 rows show the
  15 kHz gaps, 256 rows on Console timing 10 none (31 kHz, every line twice), on timing 11 the gaps again;
  the screenshots match the ctypes renderer within 83-102 dB PSNR.

## Not found

- The CZ-600D's own manual or catalogue page: viewable size, tube, mask type (its 0.39 mm pitch comes from
  several secondary sources; the dot-type tube and the 278 x 209 mm picture come from its 0.39 mm sibling,
  the CZ-605D).
- Video bandwidth, beam spot size and white point for any model.
- A confirmed close-up photo of a native X68000 15 kHz game, or of native 512-line text.
