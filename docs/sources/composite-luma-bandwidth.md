# Composite luma above the subcarrier (5-6 MHz)

Researched 2026-10-24. While the automatic Dither blend was being worked out, the shader's composite turned out to
keep most of a 1-pixel stripe in 512-wide SNES hi-res (5.37 MHz) and almost none of a 320-wide one (3.36 MHz).
Games such as Kirby's Dream Land 3 use 512-wide stripes as pseudo-transparency that people remember as blended.
The question was whether real consumer composite passed 5-6 MHz like that. The same day two changes followed
from it (see [Changed in the shader](#changed-in-the-shader)):
- RF and the TV show got the TV's IF filter;
- the NES and SNES system presets got Luma trap in the console 0.

The composite filter itself stays as it was.

Short answer: yes. The SNES does not filter its composite luma at all. With a cathode amplifier, the TV decoders
in the datasheets below pass 5.37 MHz with 0.4-0.7 of its amplitude, against the shader's 0.55. Three things do take it out:
RF (the TV's IF filter), the luma networks of Sega's and Sony's consoles (not the SNES), and the slow DAC of the
2-chip SNES. Along the way it turned out that the shader's composite is softer than every real chain at 2-3 MHz.

## What the shader does

- Console (`encode.inc`, `encYUV`): Luma trap in the console (`LR_YTRAP`, 0.75 in all TV presets and systems/,
  0.6 in old-tv-rf) takes that share of a band around the subcarrier out of luma: a Gaussian, -3 dB at +-0.5 MHz.
- TV, composite (`decode.inc`): luma `(1 + s) G(f, fcY) - s G(f, fcY / 2.5)`, s = 1.4 x Sharpness (0.35), fcY 3.3 MHz
  NTSC, 4.2 PAL (G a Gaussian, -3 dB at fc). Then the trap: the decoded chroma, remodulated, 0.92 of it times the
  luma gain at fsc taken out of luma. It is as wide as the chroma filter (fcC 0.6 MHz NTSC, 0.8 PAL): -3 dB about
  1.1 MHz either side of fsc. The 6.5 MHz amplifier of the RGB path is not applied to composite, so fcY stands for
  the whole TV.
- RF: the same with fcY 2.8 MHz (NTSC) / 3.6 (PAL), notch 0.95, fcC 0.5, Sharpness 0.5, console trap 0.6.

Gain at a 1-pixel stripe's frequency (half the pixel clock), from these filters (worked out):

| 1-pixel stripe, NTSC | RGB (6.5 MHz) | Composite | Composite, console trap 0 | RF (before the IF filter) |
|---|---|---|---|---|
| 256 wide, 2.68 MHz | 0.94 | 0.50 | 0.66 | 0.68 |
| 320 wide, 3.36 MHz | 0.91 | 0.05 | 0.15 | 0.07 |
| 512 wide, 5.37 MHz | 0.79 | 0.55 | 0.55 | 0.46 |
| 640 wide, 6.71 MHz | 0.69 | 0.36 | 0.36 | 0.23 |

PAL, 512 wide (5.32 MHz): composite 0.19, RGB 0.79. The 4.43 MHz trap is closer and its Gaussian is wide.

The rendered shader does not quite follow these filters at hi-res widths. The session working on the automatic
Dither blend measured this with a ctypes render of the real chain: grey 1-pixel stripes 64/191, 224 lines, the
fundamental at the decoder output. It was not re-checked here. Against the filters above:
- composite: +0.7% at 256 wide, +8% at 448, +14% at 512 (+6% with the console trap 0), +37% at 640 (+16%);
- RGB: -0.3%, +4%, -9%, -34%.

The likely causes:
- the console trap's taps are 0.25 sigma apart (0.71 px at 512 wide, 0.89 px at 640), so they skip 1-pixel
  detail;
- the RGB amplifier reads the nearest pixel at each tap instead of integrating the pixel steps;
- the encoder has only 2 samples per pixel at 640 wide.

Up to 448 wide everything agrees within a few percent.

## Consoles: the encoder's luma path (composite only; S-Video Y and RGB bypass it)

- **SNES, S-ENC (ROHM BA6592F)**. Source: the jwdonal schematic (a redrawn schematic, "Revision 2 Boards:
  SNS-CPU-GPM-01 (1992), SNS-CPU-GPM-02 (1993), SNS-CPU-RGB-01 (1994), SNS-CPU-RGB-02 (1995)";
  https://fabiensanglard.net/10nes/snes_schematic.pdf, Wayback copy 2024-01-10).
  - The path: YO (pin 23) → R38 470 Ω → Q11 (C2412) emitter follower, with C17 10 pF and R39 10k at its base →
    C18 1 µF → R40/R41 39 Ω → YI (pin 9).
  - No trap and no delay line. The only pole is 470 Ω × 10 pF, at 34 MHz.
  - The BA6592F datasheet (ROHM, 1990-12-25, https://wiki.console5.com/tw/images/e/e6/BA6592F.pdf) shows YI →
    amplifier → Y/C sum. It gives no frequency response.
  - Conflict: the ConsoleMods wiki says the RGB-01/02 boards have a newer encoder (S-RGB). The S-RGB A (SNES
    1CHIP, SNS-101 / SHVC-101 Jr) has no Y-in, trap or delay pins in its pinout, so its luma path is internal and
    unknown. No datasheet was found (snesdev wiki: "actually a BA6596F", from a forum post).
- **NES**: no encoder. "The NES PPU does not encode anything into composite; instead, directly drawing the
  composite waveform itself" (https://www.nesdev.org/wiki/NTSC_video). No luma filter is mentioned.
- **SNES 2-chip RGB**. Chris Covell measured an old Super Famicom (oscilloscope at the multi-out,
  https://www.chrismcovell.com/gotRGB/snesblur.html). Black to medium grey "takes about 0.6 microseconds" to rise;
  transitions to black, white or between primaries are sharp, and the SFC Jr is sharper. A 512-wide pixel lasts
  93 ns, so hi-res stripes between intermediate colours are smeared at the source, on every cable. The effect
  depends on the level, so it is not a linear filter. The shader does not model it.
- **Mega Drive model 1, PAL VA4 (CXA1145P)**. Source: the PAL Mega Drive Model 1 service manual, schematic
  171-5872-20 (PDF p.66), read here.
  - The network: Y OUT (16) → R27 1.2k → L3 100 µH ∥ C35 12 pF → Y IN (18), with C34 180 pF to ground and R29 1k
    to VREF. There is no delay-line part.
  - Response (computed, 0 Ω source, ideal parts; the network divides DC by 1k/2.2k): -3 dB at 1.50 MHz, -11.5 dB at
    2.68 MHz, -18 dB at 3.36, a notch at 4.59 MHz (near PAL fsc), -28.5 dB at 5.37, -23 dB at 6.71.
  - So it is a low-pass with a trap, not a narrow trap. The Genesis II with CXA1145M (NTSC, C35 18 pF; read by a
    research agent from the VA0 manual, not re-checked) gives -3 dB at 1.48 MHz, -14 dB at 2.68, -25 dB at 3.36
    and -20 dB at 5.37. The MB3514 boards (12k / 100 µH ∥ 18 pF / 15 pF / 10k) give -3 dB at 2.05 MHz and about
    -10 dB from 3.6 to 6.7 MHz.
  - No NTSC model 1 schematic was found.
- **Sony CXA1645P/M** (Mega Drive II from 1994, PS1 PU-18). Sony datasheet E93411A41 (Wayback copy of
  consolemods.org/wiki/images/1/10/CXA1645.pdf):
  - built-in Y delay line;
  - YOUT and CVOUT frequency characteristic at least -3 dB at 5 MHz (re 200 kHz);
  - YTRAP pin 17, input resistance 1.5 kΩ: "connect a capacitor or a capacitor and an inductor in series between
    YTRAP and GND", e.g. L = 68 µH, C = 28 pF for NTSC; "No influence on the YOUT pin".
- **PlayStation**. Values from the Sony service manuals: SCPH-9000 (PU-23) read here on the schematic, the others
  read by the research agent.
  - SCPH-9000 (PU-23, BH7240AKV drawn): YTRAP (pin 10) → L507 56 µH → C523 33 pF → ground; AEP 47 µH + 27 pF.
    SCPH-7500 (PU-22) the same; L507 56 µH (47 µH on the 7502) checked here.
  - SCPH-5500 (PU-18, CXA1645M): 33 µH + 62 pF (39 pF on the 5502).
  - SCPH-9000 -51 and the PSone (CXA2106R): no LC; a resistor from YTRAP to AVCC2 (3.3k, 2.7k PAL) selects the
    internal trap. The CXA2075M datasheet gives -21.6 dB typ at 3.58 MHz and CVOUT -1.53 dB typ at 5 MHz (it is
    not clear if the trap was on in that test).
  - The earliest boards (PU-7/8/16, CXA1645M) and PU-20: not found.
  - Response of the series LC from the pin's source resistance Rs (computed, `|X| / sqrt(Rs^2 + X^2)`, ideal parts):
    PU-22/23 NTSC, Rs 1.5-2k: -6 to -8 dB at 2.68 MHz, -16 to -18 at 3.36, -5 to -7 at 5.37, -2.6 to -4 at 6.71.
    PU-18: -12, -27, -8, -5 dB. The trap is broad: its -3 dB points are about Rs/(2πL) = 4-7 MHz apart.

## TVs: the decoder's luma path (datasheets)

Composite luma in a TV of this era goes through the chroma trap, the luma delay line and the peaking (sharpness)
to the jungle IC's R, G, B outputs, then through the cathode amplifiers. Graph readings are to about +-1 dB, a
few dB on the steep sides of the notch. The Sony CXA2025AS and CXA1870S graphs were read here; the other chips
were read by a research agent and not re-checked.

- **Philips TDA8360/61/62** (objective specification, March 1994; https://radiobooka.ru/manuals/tda/TDA8360,_TDA8361,_TDA8362.pdf),
  PAL and PAL/NTSC single-chip TV processor, pp.16-17, 23-25:
  - chroma trap at fSC with quality factor 2 and 20 dB min subcarrier rejection; -3 dB bandwidth `fosc (1 - 1/2Q)`.
    It is switched off for S-VHS.
  - Y delay line 480 ns, bandwidth 8 MHz min.
  - peaking: `A(f) = 1 + K (1 - cos(180 deg x f / 3.1 MHz))`, 160 ns sections, neutral K = 0, minimum -0.5. The
    boost is largest at 3.1 MHz and back to 0 at 6.2 MHz.
  - RGB output bandwidth (-3 dB): RGB input 8 MHz min, CVBS input 2.8 MHz typ (3.58) and 3.5 MHz (4.43), S-VHS
    8 MHz min. The CVBS figure is the lower edge of the notch (0.75 fsc), not a low-pass: the same path without the
    trap passes 8 MHz.
- **Sony CXA2025AS** (NTSC Y/C/jungle, E96413-ST; https://pdf.jiepei.com/cxa2025-9174679.html). Lola already takes
  its demodulator axes from it.
  - Built-in trap, on/off by I2C. Item 13: -37.5 dB at fsc, measured at R out. "When inputting a signal which has
    been Y/C separated by a comb filter, etc., the trap should be turned OFF."
  - CTRAP-ADJ graph (p.34), trap on: +1.7 dB at 2 MHz, -3.5 at 3, about -30 near 3.7, -12 at 4, -5.9 at 5, -5.2 at
    6 MHz. Trap off: +2.6 at 2.5, +0.9 at 5, -0.6 at 6.
  - SHARPNESS graph (p.34): the three settings meet at about 6.2 MHz, -3.8 dB. A 1 - cos peaking around 3 MHz
    (the power-on default SHP-F0) is inferred.
- **Sony CXA1870S** (NTSC, E95431-TE; https://pdf.jiepei.com/cxa1870s-9806658.html).
  - Fig.3 p.37, trap on: +0.6 dB at 2 MHz, -3.5 at 3, about -31 at 3.5, -12 at 4, about -4 dB from 5 to 8 MHz.
  - "When the chroma trap is off, the Y system frequency response is approximately 8 MHz, -3 dB for R, G and B
    outputs." The sharpness curves (Fig.1) all cross 0 dB at 6 MHz.
- Read by the research agent only:
  - Sony CXA1464AS/1465AS (J92202B7X): trap -36 dB typ; RGB response 0 dB typ at 5 MHz.
  - Sony CXA1213AS (E90931-HP, external trap module): Y in to B out, sharpness centre, +3.7 dB at 2.3 MHz,
    -1.7 at 5, -3 at 5.6.
  - Panasonic AN5195K-C: external trap and delay line; Y chain -3 dB at 6.0 MHz typ.
  - Toshiba TA8879N (1997): external trap/delay module; Y process -1 dB at 6 MHz.
  - Sanyo LA7680/81: video amplifier -3 dB at 7 MHz typ.
  - Sanyo LA76810A: trap -26 dB, -3 dB at 2.6 MHz with the trap, 6.0 MHz without.
- **Cathode amplifiers** (Philips, https://electronix.org.ru/datasheet/TDA/; read by the agent), large-signal
  bandwidth min / typ:
  - TDA6103Q (1994) 5 / 7 MHz;
  - TDA6101Q (1995) 5.5 / 7 MHz;
  - TDA6111Q 10 / 13 MHz;
  - the later TDA6107JF 4.5 MHz typ.

  The shader's 6.5 MHz amplifier sits in this range.

No sheet has a luma low-pass near 3.3 MHz. The trap is a notch: symmetric in the Philips chip, and with a shelf of
-4 to -6 dB above it in the Sony chips. Peaking lifts 2-3 MHz by 1.5-3.5 dB and is back to 0 near 6 MHz.

## RF

The console's RF modulator puts composite on channel 3/4, and the TV's IF filter then limits it like a broadcast.
- **EPCOS M 3568 M**, 45.75 MHz IF filter for M/N (data sheet 2006,
  https://pccomponents.com/datasheets/EPCO-B39458-M3568-M201.pdf). Relative attenuation, typ:
  - colour carrier (42.17 MHz) 2.4 dB;
  - sound carrier (41.25 MHz) 43 dB (34 min);
  - adjacent picture carrier (39.75 MHz) 65 dB;
  - lower sidelobe, 35-39.75 MHz, 45 dB.
- **Where the stripes land.** A video frequency f sits at 45.75 - f in the IF:
  - 4.2 MHz sits at 41.55 MHz, on the steep side;
  - 5.37 MHz sits at 40.38 MHz, which the graph puts 40-55 dB down. It is gone.
- **RCA patent US4660087** (filed 1986): "the SAW filter sound trap commonly attenuates the 41.25 MHz sound carrier
  signal by approximately -25 db to -35 db". With a 4.5 MHz trap in the baseband video, "the two traps produce an
  overall attenuation of sound information in the video channel of -50 db or more".
- **PAL B/G** works the same way, with the sound carrier 5.5 MHz above the picture carrier, so a 5.32 MHz stripe
  sits next to the sound trap. The TV show's broadcast passes the same kind of IF filter.

Context, not a measurement:
- The Computer History Museum's 1991 Nintendo of America SNES (catalogue 102674793) consists of "main unit,
  2 control pads, AC adapter, AF [RF] switch, and outer box": no AV cable. In North America RF was the out-of-box
  connection.
- A collector catalogue lists an AV cable in the Super Famicom box (lastdodo; not checked further).

## Worked out: the SNES on composite

The SNES's own luma is flat. So a whole chain is a TV's luma curve times a 6.5 MHz cathode amplifier (the shader's
RGB amplifier). Gain at the stripe's frequency, before the beam:

| 1-pixel stripe, NTSC | RGB | Sony CXA2025AS | Sony CXA1870S | Philips TDA836x | shader (trap 0.75) | shader, trap 0 |
|---|---|---|---|---|---|---|
| 256 wide, 2.68 MHz | 0.94 | 0.89 | 0.79 | 0.72 | 0.50 | 0.66 |
| 320 wide, 3.36 MHz | 0.91 | 0.23 | 0.16 | 0.24 | 0.05 | 0.15 |
| 512 wide, 5.37 MHz | 0.79 | 0.41 | 0.52 | 0.68 | 0.55 | 0.55 |
| 640 wide, 6.71 MHz | 0.69 | - | 0.41 | 0.65 | 0.36 | 0.36 |

How the TV columns were made:
- Sony: read from the trap-on graphs (2.68 MHz -0.5 / -1.5 dB, 3.36 MHz about -12 / -15 dB, 5.37 MHz -5.6 /
  -3.7 dB, 6.71 MHz - / -4.5 dB);
- Philips: a second-order notch, Q 2, 20 dB deep, `(1 - x^2 + j x d/Q) / (1 - x^2 + j x/Q)`, x = f/fsc, d = 0.1,
  neutral peaking;
- the shader's 512-wide composite as rendered is about 14% higher (see above).

What the table shows:
- At 5.37 MHz the shader is inside the range of real sets. Compared with RGB, the real sets take out about 15-50%
  of a 512-wide stripe and the shader 30%.
- At 2.68 MHz the shader is below all of them. Its Gaussian luma is -2 dB there before peaking, and its wide trap
  still takes out about 0.39 of luma 0.9 MHz from fsc. Together they take out more than any datasheet curve, and
  the console trap the SNES does not have takes out more again.

For the Mega Drive and the PlayStation the console's network comes on top of the TV:
- MD1 PAL VA4: x0.27 at 2.68 MHz and x0.12 at 3.36;
- PS1 PU-23: about x0.4-0.5 at 2.68 MHz and x0.5 at 5.37.

So those consoles blend 256-wide stripes more than the shader's narrow console trap does, and the SNES and NES
blend them less.

Where 512-wide stripes did blend, the sources point to RF, the 2-chip SNES DAC, and Sega's and Sony's console
networks. A consumer TV's composite decoder is not among them.

## Changed in the shader

### RF and the TV show: the IF filter (`decode.inc`, `IF_NTSC`, `IF_PAL`)

The cut is written as 1 minus five Gaussian bands. They were fitted (least squares) to:
- NTSC: flat to 3.3 MHz, under 0.03 (-30 dB) from 4.4 MHz up. Result: -6 dB at 4.0 MHz, -12 dB at 4.2, -24 dB
  at 4.4.
- PAL B/G: flat to 4.5 MHz, under 0.03 from 5.4 MHz up. Result: -4 dB at 5.0 MHz, -15 dB at 5.32, -38 dB at
  5.5, the sound carrier.

The NTSC edge is gentler than the EPCOS filter at 4.2-4.4 MHz (there about -25 to -40 dB). That region is
inside the trap anyway. No PAL IF filter datasheet was read: the PAL edge follows the B/G standard (5 MHz video,
sound carrier at 5.5 MHz).

How it is applied:
- **On the luma Gaussian.** A Gaussian band times the luma Gaussian is again a Gaussian band, with its centre and
  width from the product of the two. So the cut multiplies the luma filter exactly, as cos-modulated Gaussians in
  the decoder's luma loop, with no extra pass. The peaking's wide Gaussian is not multiplied: it is under 0.03
  above 4 MHz.
- **On the trap.** The trap takes out the chroma band times the luma gain at fsc. With the cut that alone would
  take out too much just above fsc: -0.26 at 4.2 MHz on RF instead of +0.06. So the first two bands of the cut
  are multiplied by the trap's band too and added back.
- **What is left out.** Bands that come out weaker than 0.004 are skipped. The worst ripple after the cut is
  -0.03 to -0.07 (show PAL at 5.6-6.7 MHz).

Measured with a ctypes render of the real chain (as in [dither-blend.md](dither-blend.md); grey 1-pixel stripes
64/191, the fundamental at the decoder output), HEAD (2ccc5dc) vs after:

| Preset | 256 wide | 320 | 512 | 640 |
|---|---|---|---|---|
| old-tv-rf (NTSC) | 0.217 → 0.216 | 0.018 → 0.016 | 0.142 → 0.001 | 0.088 → 0.002 |
| old-tv-rf, PAL | 0.373 → 0.372 | 0.244 → 0.244 | 0.119 → 0.015 | 0.162 → 0.004 |
| tv-show-broadcast (PAL) | 0.257 → 0.257 | 0.158 → 0.158 | 0.042 → 0.001 | 0.067 → 0.005 |
| tv-show-broadcast, NTSC | 0.181 → 0.180 | 0.039 → 0.035 | 0.089 → 0.001 | 0.042 → 0.001 |
| consumer-tv-composite | unchanged | unchanged | unchanged | unchanged |

Other measurements:
- **Sharp edges** in 256- and 320-wide frames (random bars of 1-6 pixels, noise off) change too. The old RF
  luma, with Sharpness 0.5, still passed 0.4-0.5 at 4.4-6 MHz. Old-tv-rf: at most 18-24/255, RMS 4.5-6.6/255;
  the TV show: at most 6.5-7.4/255, RMS 1.5-1.7/255. No ringing shows on screen.
- **The snow** is cut as well (it comes in before the IF filter on a real set too). Worked out from the filters,
  its amplitude drops by 5-9%. RF noise was not recalibrated.
- **Cost**, the whole frame on the M4 Pro at 1440x1080 (it varies about 20% from run to run):
  - full and lite, old-tv-rf and tv-show-broadcast: about +1.0 ms. Full: 2.24 → 3.25 ms and 2.90 → 3.97;
    lite 0.97 → 1.97 and 1.23 → 2.29.
  - super lite: left out, so it stays as fast as before (its RF and TV show still pass 512-wide stripes). A
    shorter form (bands cut at 2 sigma, bands under 0.03 left out) cost 0.79 → 0.97 ms and 0.94 → 1.30 and
    was dropped: super lite is for slow computers and comes first for speed.
  - composite and the other cables: unchanged.

### NES and SNES: Luma trap in the console 0 (`tools/make_presets.py`, systems/)

Neither console has a luma trap (see Consoles above). In systems/snes the 1-pixel stripes on composite, against
RGB, now keep:
- 256 wide: 0.75 (was 0.53). The real chains above give about 0.77-0.95.
- 512 wide: 0.82 (was 0.88; the console trap's taps had added to it, see above).

The rainbow on 256-wide dither is stronger than before.

## Not found

- A measured luma response of a whole consumer TV on its video input, and a spec sheet stating horizontal
  resolution on the video input of a set without a comb filter.
- Datasheets of Sony CXA1587, Toshiba TA7698/TA8680/TA8690/TA8759/TA8880, Sanyo LA7687, Panasonic AN5601K, Samsung
  KA2131, and the response of the external trap and delay-line modules.
- How common each kind of set was (Philips-type symmetric notch vs Sony-type shelf).
- The SNES S-RGB's luma path (1CHIP, Jr), an NTSC Mega Drive model 1 schematic, the first PS1 boards (PU-7/8/16)
  and PU-20.
- A photo of Kirby's Dream Land 3 on a real composite CRT next to RGB.

## Where the code uses it

- `decode.inc`:
  - fcY, notch, fcC, the luma filter `(1 + sh) G(s1) - sh G(s2)` and the trap; the RGB path's 6.5 MHz;
  - the IF filter on RF and the TV show (`IF_NTSC`, `IF_PAL`, the bands in the luma loop; not in super lite).
- `encode.inc` (`encYUV`): the console trap.
- `tools/make_presets.py`: `LR_YTRAP` 0.75 in BASE (all TV presets and systems/), 0.6 in old-tv-rf, 0 in
  systems/nes and systems/snes.
- The README's Dither blend numbers and the automatic Dither blend follow these filters
  ([dither-blend.md](dither-blend.md)).
