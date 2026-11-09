// Lola Retro - pass 5: horizontal beam profile of every source line.
// The spot shape, misconvergence and tube gamma only depend on the position along a
// line, so they are worked out here once per line, on a fine grid (the pass is 8192
// samples wide), instead of four times for every screen pixel in the CRT pass.
// Output: one row per native line, holding the square root of the beam's linear brightness.

#include "common.inc"

#pragma stage vertex
layout(location = 0) in vec4 Position;
layout(location = 1) in vec2 TexCoord;
layout(location = 0) out vec2 vTexCoord;
layout(location = 1) flat out float vScale;
layout(location = 2) flat out float vScan;
layout(location = 3) flat out vec2 vShare;   // share of the scan the source covers (x: active line, y: lines)
layout(location = 4) flat out float vConvW;  // 320 x frame pixels per pixel of a 320-wide mode (misconvergence unit)
layout(location = 5) flat out float vJitter; // RF: how far each line lands off (unstable sync)

void main()
{
    gl_Position = global.MVP * Position;
    vTexCoord = TexCoord;
    Timing T = getTiming(params.OriginalSize.xy, params.FrameCount);
    vScale = T.scale;
    vScan = T.scan;
    float vis = (T.pal > 0.5 ? 288.0 : 240.0) * (T.interlace > 0.5 ? 2.0 : 1.0);
    // Picture height 1: the core's lines fill the height (not on a TV show), as in the CRT pass
    bool fill = global.LR_FILL > 0.5 && !isShow(T.cable);
    vShare = vec2(activeShare(T, params.OriginalSize.xy),
                  (T.scan < 0.5 && !fill) ? min(params.OriginalSize.y / T.scale / vis, 1.0) : 1.0);
    vConvW = isAmiga(T) ? 320.0 * T.hres : params.OriginalSize.x;
    vJitter = T.cable < 0.5 ? 0.5 + global.LR_NOISE * 4.0 : 0.0;
}

#pragma stage fragment
layout(location = 0) in vec2 vTexCoord;
layout(location = 1) flat in float vScale;
layout(location = 2) flat in float vScan;
layout(location = 3) flat in vec2 vShare;
layout(location = 4) flat in float vConvW;
layout(location = 5) flat in float vJitter;
layout(location = 0) out vec4 FragColor;
layout(set = 0, binding = 3) uniform sampler2D LR_Decoded;

void main()
{
    // one row per native line; the rows past the last line are spare (a margin: the division
    // can land a hair over a whole number)
    float i = floor(vTexCoord.y * params.OutputSize.y);
    if (i + 0.01 >= params.OriginalSize.y / vScale)
    {
        FragColor = vec4(0.0);
        return;
    }
    // sample m sits at x = m / width (the CRT pass reads it with the same half-texel offset)
    float x = vTexCoord.x - 0.5 * params.OutputSize.z;

    // RF: every line lands slightly off (unstable sync)
    float jitter = vJitter;
    float seed = float(params.FrameCount % 997u);
    float jit = jitter > 0.0 ? (hash13(vec3(i, seed, 5.0)) - 0.5) * jitter * params.OriginalSize.z : 0.0;
    vec2 tc = vec2(x + jit, (i + 0.5) * params.OriginalSize.w);   // the decoder's row of line i (row i)

    bool pc = isPC(vScan);
    bool mm = inMM(vScan);
    // position on the tube face, -1..1: the picture is smaller than the tube with a black border,
    // and on a 15 kHz monitor in mm the source covers only part of the active line
    float cx = (x - 0.5) * 2.0 * vShare.x / monShown().x;
    float cy = ((i + 0.5) * vScale * params.OriginalSize.w - 0.5) * 2.0 * vShare.y / monShown().y;
    // tube in mm: sigma of a 1 mm spot (FWHM), in units of the source line's width
    float mmUnit = FWHM_TO_SIGMA * monCornerGrowth(vec2(cx, cy)) / (monScanMM().x * vShare.x);

    // Horizontal spot: like the vertical one, a Gaussian whose width grows with brightness,
    // so bright detail spreads and rounds off while dark detail stays sharp.
    // Every point along the line spreads its own light with its own width (energy is kept).
    vec3 acc = vec3(0.0), dacc = vec3(0.0);                // linear light, and its derivative along x
    vec3 inv = vec3(0.0);                                  // light / spot width, for the spot height below
    float spot = 1.0;                                      // tube in mm: which spot made this light (0 dark .. 1 white)
    float sLo, sHi;                                        // spot sigma on dark and on white
    if (pc)
    {
        // PC monitor: the 85 MHz amplifier keeps pixel edges sharp, so each pixel is a flat
        // step of beam current, and its light (with the spot width of its own brightness) is
        // integrated over the pixel exactly. Units here: source pixels.
        float W = params.OriginalSize.x;
        // The decoded line has 4 samples per pixel in the PC presets, but 1280 per line in the TV
        // presets (ENC_SAMPLES; Console timing 7 or Frames over 300 lines 2 there): 1.25 per pixel
        // at 1024 wide, where a read at the pixel's centre would fall between two samples and mix
        // up to 3/8 of the next pixel in. Then the sample that holds the pixel's centre is read.
        float DW = float(textureSize(LR_Decoded, 0).x);
        float spp = DW / W;                                // decoded samples per pixel
        bool own = abs(spp - floor(spp + 0.5)) > 0.01;
        sLo = global.LR_MON_SPOT_LO * mmUnit * W;
        sHi = max(global.LR_MON_SPOT_LO, global.LR_MON_SPOT_HI) * mmUnit * W;
        float px = tc.x * W;
        int j0 = int(floor(px - 3.0 * sHi));
        int j1 = int(floor(px + 3.0 * sHi));
        // 24 steps at most. A spot wider than that in pixels (a 29-inch tube at 4x internal resolution
        // or more) takes its pixels in groups of st, each read at its middle: the loop used to stop at
        // the 24th pixel, which cut the right side of the spot off.
        int st = (j1 - j0) / 24 + 1;
        float fst = float(st);
        for (int k = 0; k < 24; k++)
        {
            int j = j0 + k * st;
            if (j > j1) break;
            float fj = float(j);
            // the pixel's value (outside the line: black border)
            float fc = fj + 0.5 * fst;
            float u = own ? (floor(fc * spp) + 0.5) / DW : fc / W;
            vec3 b = pow(clamp(textureLod(LR_Decoded, vec2(u, tc.y), 0.0).rgb, 0.0, 1.0), vec3(0.5 * global.LR_GAMMA));
            vec3 sg = mix(vec3(sLo), vec3(sHi), b);
            vec3 zl = (fj - px) / sg, zr = (fj + fst - px) / sg;
            vec3 l = b * b * (gaussCdf(zr) - gaussCdf(zl));
            acc += l;
            inv += l / sg;
            dacc += b * b * (gaussPdf(zl) - gaussPdf(zr)) / sg;
        }
        dacc *= W;                                         // per pixel -> per texture width
    }
    else
    {
        // 15 kHz monitor in mm (1084S): spot sizes in mm, like the PC monitor, but its 6.5 MHz
        // amplifier rounds the pixel edges, so the decoded line is sampled as a smooth signal.
        // TV model: 1 = one pixel of a 320-wide mode, the same physical size as one TV line;
        // Horizontal focus 0.5 makes the spot round.
        float f = 2.0 * max(global.LR_HFOCUS, 0.05) / 320.0;
        sLo = mm ? global.LR_MON_SPOT_LO * mmUnit : global.LR_SIG_LO * f;
        sHi = mm ? max(global.LR_MON_SPOT_LO, global.LR_MON_SPOT_HI) * mmUnit : max(global.LR_SIG_LO, global.LR_SIG_HI) * f;
#ifdef LR_SUPER_LITE
        float dt = 2.0 * sLo;                              // half the taps: dark detail up to 1.5% brighter
#else
        float dt = sLo;                                    // tap spacing (a Gaussian sampled at 1 sigma still sums exactly)
#endif
        int nt = int(min(ceil(3.0 * sHi / dt), 16.0));
        for (int k = -nt; k <= nt; k++)
        {
            float o = float(k) * dt;                       // tap position minus x
            vec3 b = pow(clamp(textureLod(LR_Decoded, tc + vec2(o, 0.0), 0.0).rgb, 0.0, 1.0), vec3(0.5 * global.LR_GAMMA));
            vec3 is = 1.0 / mix(vec3(sLo), vec3(sHi), b);  // 1 / spot width of that point
            vec3 g = exp(-0.5 * o * o * is * is) * is * (0.39894228 * dt);
            acc += b * b * g;
            inv += b * b * g * is;
            dacc += b * b * g * o * is * is;
        }
    }
    if (mm)
    {
        // The light next to a bright pixel was made by that pixel's (wide) spot, so the CRT pass
        // must spread it vertically with the same spot, not with one sized by the local light.
        // Stored as 0 (dark spot) .. 1 (white spot); the light-weighted harmonic mean keeps the
        // brightness at the centre of the line.
        float lsum = acc.r + acc.g + acc.b, isum = inv.r + inv.g + inv.b;
        spot = (isum > 1e-9 && sHi > sLo) ? clamp((lsum / isum - sLo) / (sHi - sLo), 0.0, 1.0) : 0.0;
    }

    // misconvergence: red and blue land a fraction of a pixel off green, more toward the edges.
    // At most one console pixel: vScale frame pixels of an upscaled frame (the limit used to be one
    // frame pixel, so the error shrank as the internal resolution went up).
    float conv = clamp(global.LR_CONV * (0.35 + 0.65 * cx * abs(cx)) * vConvW / 320.0, -vScale, vScale);
    float sh = conv * params.OriginalSize.z;
    acc.r -= dacc.r * sh;
    acc.b += dacc.b * sh;

    // the square root is stored because the CRT pass needs both it and its square
#ifdef LR_PACKED_SPOT
    // no alpha channel (86Box's passes are RGB only): the spot rides on red, in whole steps of 4
    // above the light (0..3.99); the CRT pass takes it off again (beamAt)
    vec3 r = min(sqrt(max(acc, 0.0)), 3.99);
    FragColor = vec4(r.r + 4.0 * floor(spot * 255.0 + 0.5), r.g, r.b, 1.0);
#else
    FragColor = vec4(sqrt(max(acc, 0.0)), spot);
#endif
}
