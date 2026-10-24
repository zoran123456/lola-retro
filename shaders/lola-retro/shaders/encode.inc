// Lola Retro - pass 1: console video encoder.
// RGB -> YUV, chroma band-limited and QAM-modulated onto the colour subcarrier.
// Output: composite, one frame of the subcarrier cycle per channel (R, G, B); S-Video: R = luma,
// G, B, A = the chroma of each frame. No flicker uses up to three frames (see steadyFrames),
// otherwise only R (and G for S-Video's chroma).
// The output is 4 samples per source pixel, one row per native line (see main).

#include "common.inc"

#pragma stage vertex
layout(location = 0) in vec4 Position;
layout(location = 1) in vec2 TexCoord;
layout(location = 0) out vec2 vTexCoord;

void main()
{
    gl_Position = global.MVP * Position;
    vTexCoord = TexCoord;
}

#pragma stage fragment
layout(location = 0) in vec2 vTexCoord;
layout(location = 0) out vec4 FragColor;
layout(set = 0, binding = 2) uniform sampler2D Source;

// Source pixel at x position xs on the native line that starts at row y.
// An upscaled frame has k rows per native line: the native pass (native.slang, before this
// one) has already averaged them into the line's first row, so one read is enough.
// (The Amiberry and 86Box versions have no native pass; their frames are never upscaled.)
vec3 srcPix(float xs, float y, float k)
{
    if (xs < 0.0 || xs >= params.SourceSize.x) return vec3(0.0);
    return textureLod(Source, vec2((floor(xs) + 0.5) * params.SourceSize.z, (y + 0.5) * params.SourceSize.w), 0.0).rgb;
}

// Luma and the colour difference signals (Y, U, V) at sample position n (in samples), before
// modulation. Nothing here depends on the frame's subcarrier phase (the luma trap takes out a
// band around the subcarrier, the same in every frame), so the frames of No flicker share it.
// trap > 0: the encoder's luma trap takes that share of the luma near the colour
// subcarrier (about +-0.5 MHz) out before mixing, so fine stripes leak less into
// the colour (less rainbow). The band is narrow, so plain brightness is not touched.
// show: TV show, the console's RGB went through the studio and onto tape before the
// station's encoder (see SHOW_* in common.inc)
vec3 encYUV(float n, float y, float fs, Timing T, float trap, float blend, bool show)
{
    float ppx = T.pclk / fs;                 // source pixels per sample
    float xs = (n + 0.5) * ppx;
    vec3 c = srcPix(xs, y, T.scale);
    float Y = dot(c, vec3(0.299, 0.587, 0.114));
    float copies = show ? global.LR_TAPE : 0.0;

    if (copies > 0.0)
    {
        // every tape copy rounds the luma a little more (Gaussians add up in variance). The
        // console's pixels are flat steps, so each one's share is the Gaussian's integral over it;
        // the Gaussian is narrower than a pixel, so only two to four pixels are read.
        float sp = 0.1325 / SHOW_TAPE_Y * sqrt(copies) * T.pclk;   // sigma in frame pixels
        float j0 = floor(xs - 3.0 * sp), j1 = floor(xs + 3.0 * sp);
        float ay = 0.0, wy = 0.0;
        for (int k = 0; k < 16; k++)
        {
            float j = j0 + float(k);
            if (j > j1) break;
            vec3 z = gaussCdf(vec3(j - xs, j + 1.0 - xs, 0.0) / sp);
            float w = z.y - z.x;
            ay += w * dot(srcPix(j + 0.5, y, T.scale), vec3(0.299, 0.587, 0.114));
            wy += w;
        }
        Y = ay / wy;
    }

    if (blend > 0.0)
    {
        // dither blend (S-Video): take the 1-pixel alternating part out of luma.
        // Works on console pixels, so an upscaled frame blends the same way.
        float sp = T.scale;
        float j0 = floor(xs / sp);
        float y0 = dot(srcPix((j0 + 0.5) * sp, y, T.scale), vec3(0.299, 0.587, 0.114));
        float a = 0.0;
        for (int k = -4; k <= 4; k++)
        {
            float yk = dot(srcPix((j0 + float(k) + 0.5) * sp, y, T.scale), vec3(0.299, 0.587, 0.114));
            a += DBW[abs(k)] * dbSign(k) * (yk - y0);
        }
        Y -= blend * a / DBN;
    }
    float ph = phaseAt(n / fs, y, T);

    // the encoder limits chroma to about 1.5 MHz before modulation; on a TV show the tape
    // copies and the station's encoder (1.3 MHz) did it
    float sigUs = show ? 0.1325 * sqrt(copies / (SHOW_TAPE_C * SHOW_TAPE_C) + 1.0 / (SHOW_ENC_C * SHOW_ENC_C))
                       : 0.1325 / 1.5;
    vec2 uv = vec2(0.0);
    float ws = 0.0;
#ifdef LR_SUPER_LITE
    // the Gaussian integrated over the source pixels, which are flat steps: each pixel read once
    // (groups of st pixels for wide frames: an upscaled frame repeats its pixels anyway)
    {
        float sp = sigUs * T.pclk;                         // sigma in frame pixels
        float st = max(1.0, floor(sp / 1.5));
        float j0 = floor((xs - 3.0 * sp) / st) * st, j1 = xs + 3.0 * sp;
        for (int k = 0; k < 16; k++)
        {
            float j = j0 + float(k) * st;
            if (j > j1) break;
            vec3 z = gaussCdf(vec3(j - xs, j + st - xs, 0.0) / sp);
            float w = z.y - z.x;
            vec3 cc = srcPix(j + 0.5 * st, y, T.scale);
            float yy = dot(cc, vec3(0.299, 0.587, 0.114));
            uv += w * vec2(0.492 * (cc.b - yy), 0.877 * (cc.r - yy));
            ws += w;
        }
    }
#else
    for (int k = -8; k <= 8; k++)
    {
        float u = float(k) * 0.4;            // in sigmas, covers +-3.2
        float w = exp(-0.5 * u * u);
        vec3 cc = srcPix(xs + u * sigUs * T.pclk, y, T.scale);
        float yy = dot(cc, vec3(0.299, 0.587, 0.114));
        uv += w * vec2(0.492 * (cc.b - yy), 0.877 * (cc.r - yy));
        ws += w;
    }
#endif
    uv /= ws;

    if (trap > 0.0)
    {
        // demodulate the luma at the subcarrier over a long window (narrow band), then put that
        // band back at this sample and subtract it. The console's pixels are flat steps, each read
        // once, its share the window times the subcarrier integrated over the step (3 Gauss-Legendre
        // points: the subcarrier turns up to 240 degrees across a pixel, and the window changes too).
        // A step is one console pixel (k frame pixels in a frame upscaled k times, which repeats them).
        // Taps at fixed time steps (0.25 sigma) read the nearest pixel and so the steps' edges: 1-pixel
        // stripes came out 6% (256 wide) and 13% (320) weaker than the trap's filter gives and 8%
        // (512) and 18% (640) stronger; one point per pixel with a sinc, 11% stronger at 256
        // (docs/sources/composite-luma-bandwidth.md). Within 0.3% of the filter now.
        float sigT = 0.1325 / 0.5;
        float sp = sigT * T.pclk;                          // sigma in frame pixels
        float st = T.scale;
        float wpx = TAU * T.fsc / T.pclk;                  // subcarrier phase per frame pixel
        float gt = 0.38729833 * st;                        // the outer points, sqrt(3/5) / 2 of a step out
        float j0 = floor((xs - 3.0 * sp) / st) * st, j1 = xs + 3.0 * sp;
        float o = j0 + 0.5 * st - xs;                      // the first step's centre from this sample
        float is2 = 1.0 / (sp * sp);
        // the window and the subcarrier at a step's centre, carried to the next step and to the
        // outer points by factors, so no exp, sin or cos per point
        float g = exp(-0.5 * o * o * is2);                 // window at the centre
        float gq = exp(-(o * st + 0.5 * st * st) * is2);   // g at the next centre / g
        float gqq = exp(-st * st * is2);                   // how gq changes per step
        float e = exp(-o * gt * is2);                      // outer points: g * eg * e and g * eg / e
        float eq = exp(-st * gt * is2);
        float eg = 0.625 * exp(-0.5 * gt * gt * is2);      // with their weight, 5/8 of the centre's
        vec2 c = vec2(cos(ph + wpx * o), sin(ph + wpx * o));
        vec2 cs = vec2(cos(wpx * st), sin(wpx * st)), cg = vec2(cos(wpx * gt), sin(wpx * gt));
        vec2 yb = vec2(0.0);
        float wt = 0.0;
        for (int k = 0; k < 48; k++)
        {
            float j = j0 + float(k) * st;
            if (j > j1) break;
            float yy = dot(srcPix(j + 0.5 * st, y, T.scale), vec3(0.299, 0.587, 0.114));
            float gp = g * eg * e, gm = g * eg / e;
            vec2 sum = g * c + gp * vec2(c.x * cg.x - c.y * cg.y, c.y * cg.x + c.x * cg.y)
                             + gm * vec2(c.x * cg.x + c.y * cg.y, c.y * cg.x - c.x * cg.y);
            yb += yy * sum.yx;                             // (sin, cos) of the subcarrier, weighted
            wt += g + gp + gm;
            g *= gq; gq *= gqq; e *= eq;
            c = vec2(c.x * cs.x - c.y * cs.y, c.y * cs.x + c.x * cs.y);
        }
        Y -= trap * 2.0 * (yb.x * sin(ph) + yb.y * cos(ph)) / wt;
    }

    return vec3(Y, uv);
}

// The chroma of sample n: U and V modulated onto the subcarrier, off cycles later in the frame
// sequence, with the frame's PAL V-switch vsw (see steadyFrames)
float chromaAt(vec2 uv, float n, float y, float fs, Timing T, float off, float vsw)
{
    float ph = phaseAtOff(n / fs, y, T, off);
    return uv.x * sin(ph) + vSignW(y, T, vsw) * uv.y * cos(ph);
}

#ifdef LR_SUPER_LITE
// What the decoder demodulates, made here (super lite): the signal of each frame of the cycle
// times the TV decoder's reference subcarrier for that frame, as (sin, cos), with the frame's PAL
// V-switch on the cos part, averaged over the frames. The decoder then only has to low-pass it
// instead of demodulating every frame at every tap (decode.inc). The reference is the frame's own
// subcarrier phase plus the decoder's tint, which tint() gives as the decoder works it out.
float tint(Timing T, float cable)
{
    float t = T.pal > 0.5 ? 0.0 : radians(global.LR_TINT);
    if (cable < 0.5)
    {
        float ea = -TAU * T.fsc * RF_ECHO_US;
        t += atan(RF_ECHO * sin(ea), 1.0 + RF_ECHO * cos(ea));
    }
    else if (isShow(cable) && global.LR_GHOST > 0.0)
    {
        float ea = -TAU * T.fsc * SHOW_GHOST_US;
        t += atan(global.LR_GHOST * sin(ea), 1.0 + global.LR_GHOST * cos(ea));
    }
    return t;
}

vec2 products(vec3 s, float n, float y, float fs, Timing T, vec3 off, vec3 vsw, int nf, float tn)
{
    vec2 p = vec2(0.0);
    for (int k = 0; k < 3; k++)
    {
        if (k >= nf) break;
        float ph = phaseAtOff(n / fs, y, T, off[k]) + tn;
        p += s[k] * vec2(sin(ph), vSignW(y, T, vsw[k]) * cos(ph));
    }
    return p / float(nf);
}
#endif

// TV show: the transmitter's white clipper. With negative modulation the carrier runs out a
// little above peak white (PAL B/G: white at 10-15% of the carrier, so at about 114-120% of the
// picture signal; NTSC at about 120 IRE), so the composite signal is clipped a little below
// that, with a margin: at 110% (PAL) and 115% (NTSC). Only the brightest saturated yellows,
// cyans and greens (up to 133% in PAL) reach it: they come out a little darker and paler.
// A soft knee, like the clipper's diodes.
float whiteClip(float v, bool pal)
{
    float knee = 0.06;
    float k = (pal ? 1.10 : 1.15) - knee;
    return v < k ? v : k + knee * tanh((v - k) / knee);
}

void main()
{
    Timing T = getTiming(params.OriginalSize.xy, params.FrameCount);
    float SW = params.OutputSize.x;
    float fs = T.pclk * SW / params.SourceSize.x;     // sample rate (MHz)
    float n = floor(vTexCoord.x * SW);
    // Row r holds native line r. An upscaled frame has k rows per line, so only the top 1/k of
    // this pass is used: the rest stays black in one block, which a GPU skips cheaply (with the
    // used rows spread between unused ones, it worked through all of them).
    float row = floor(vTexCoord.y * params.SourceSize.y);
    float y = row * T.scale;                           // the line's first row in the frame
    float cable = T.cable;

    // RGB: no encoding, the decoder reads the original frame.
    bool show = isShow(cable);
    if ((cable > 2.5 && !show) || y >= params.SourceSize.y)
    {
        FragColor = vec4(0.0);
        return;
    }

    // S-Video keeps luma apart, no trap needed; on a TV show the console's encoder is not used
    float trap = (cable < 1.5 && !show) ? global.LR_YTRAP : 0.0;
    // composite and RF blend dither by themselves; on S-Video (RGB is not encoded) Dither blend takes
    // luma's share, its chroma filters take the colour (ditherBlend)
    float blend = (cable > 1.5 && !show) ? ditherBlend(T, cable).x : 0.0;
    vec3 a = encYUV(n, y, fs, T, trap, blend, show);

    // No flicker: the signal of up to three frames of the subcarrier cycle, one per channel
    // (S-Video: luma, then the chroma of each frame); the decoder averages what they show
    vec3 off, vsw;
    int nf = steadyFrames(T, off, vsw);
    vec3 cr = vec3(chromaAt(a.yz, n, y, fs, T, off.x, vsw.x), 0.0, 0.0);
    if (nf > 1) cr.y = chromaAt(a.yz, n, y, fs, T, off.y, vsw.y);
    if (nf > 2) cr.z = chromaAt(a.yz, n, y, fs, T, off.z, vsw.z);

    if (cable > 1.5 && !show)
    {
        // S-Video: luma and chroma on separate wires
#ifdef LR_SUPER_LITE
        FragColor = vec4(a.x, products(cr, n, y, fs, T, off, vsw, nf, tint(T, cable)), 1.0);
#else
        FragColor = nf > 1 ? vec4(a.x, cr) : vec4(a.x, cr.x, 0.0, 1.0);
#endif
        return;
    }

    vec3 comp = a.x + cr;                    // composite of each frame
    if (cable < 0.5)
    {
        // RF: composite plus an echo and snow
        vec3 g = encYUV(n - RF_ECHO_US * fs, y, fs, T, trap, 0.0, false);
        float ne = n - RF_ECHO_US * fs;
        comp.x += RF_ECHO * (g.x + chromaAt(g.yz, ne, y, fs, T, off.x, vsw.x));
        if (nf > 1) comp.y += RF_ECHO * (g.x + chromaAt(g.yz, ne, y, fs, T, off.y, vsw.y));
        if (nf > 2) comp.z += RF_ECHO * (g.x + chromaAt(g.yz, ne, y, fs, T, off.z, vsw.z));
        float seed = float(params.FrameCount % 997u);
        comp += (hash13(vec3(n, y, seed)) - 0.5) * global.LR_NOISE;
        comp += (hash13(vec3(floor(n / 7.0), y, seed + 3.0)) - 0.5) * global.LR_NOISE * 0.8;
        comp += sin(nativeLine(y, T) * 0.045 + seed * 0.37) * global.LR_NOISE * 0.12;
    }
    else if (show)
    {
        // TV show: the broadcast as it comes down the roof antenna, with a faint ghost
        // (a reflection from a building or a hill) and a little snow
        bool pal = T.pal > 0.5;
        comp = vec3(whiteClip(comp.x, pal), whiteClip(comp.y, pal), whiteClip(comp.z, pal));
        vec2 e = rfEcho(cable);
        if (e.x > 0.0)
        {
            float ne = n - e.y * fs;
            vec3 g = encYUV(ne, y, fs, T, 0.0, 0.0, true);
            comp.x += e.x * whiteClip(g.x + chromaAt(g.yz, ne, y, fs, T, off.x, vsw.x), pal);
            if (nf > 1) comp.y += e.x * whiteClip(g.x + chromaAt(g.yz, ne, y, fs, T, off.y, vsw.y), pal);
            if (nf > 2) comp.z += e.x * whiteClip(g.x + chromaAt(g.yz, ne, y, fs, T, off.z, vsw.z), pal);
        }
        // white noise, one value per sample: with more samples per microsecond (a faster pixel
        // clock, a higher internal resolution) each gets more, so the picture's band always holds
        // the same amount (calibrated at 26.6 MHz, a 320-wide PlayStation frame)
        float seed = float(params.FrameCount % 997u);
        comp += (hash13(vec3(n, y, seed)) - 0.5) * global.LR_NOISE * sqrt(fs / 26.6);
    }
    // composite: one frame per channel (the frames beyond nf stay 0)
    if (nf < 2) comp.y = 0.0;
    if (nf < 3) comp.z = 0.0;
#ifdef LR_SUPER_LITE
    // super lite: the frames' average in x, what the decoder demodulates in y and z
    FragColor = vec4((comp.x + comp.y + comp.z) / float(nf), products(comp, n, y, fs, T, off, vsw, nf, tint(T, cable)), 1.0);
#else
    FragColor = vec4(comp, 1.0);
#endif
}
