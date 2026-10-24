// Lola Retro - pass 2: the TV's decoder.
// Luma: low-pass with peaking ("sharpness"), plus a trap that removes the
// chroma band (done by re-modulating the decoded chroma, as a real LC trap does
// spectrally), or a 2-line comb filter.
// Chroma: synchronous demodulation and a narrow low-pass (consumer sets: ~0.6 MHz).
// PAL: delay-line averaging with the previous line.
// Filters are Gaussians in time, so they do not depend on the sample rate.

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
layout(set = 0, binding = 2) uniform sampler2D Source;    // encoded signal
layout(set = 0, binding = 3) uniform sampler2D Original;  // used directly for RGB

// Encoded signal at sample s of row r (row r holds native line r, see the encoder).
// Composite: one frame of the subcarrier cycle per channel; S-Video: luma, then the chroma
// of each frame (No flicker uses up to three frames, see steadyFrames).
vec4 sig(float s, float r)
{
    if (r < 0.0) return vec4(0.0);
    return textureLod(Source, vec2((s + 0.5) * params.SourceSize.z, (r + 0.5) * params.SourceSize.w), 0.0);
}

// Original pixel at x position xs on the native line that starts at row y (k rows averaged)
vec3 origPix(float xs, float y, float k)
{
    if (xs < 0.0 || xs >= params.OriginalSize.x) return vec3(0.0);
    float u = (floor(xs) + 0.5) * params.OriginalSize.z;
    vec3 c = vec3(0.0);
    for (float r = 0.0; r < k; r += 1.0)
        c += textureLod(Original, vec2(u, (y + r + 0.5) * params.OriginalSize.w), 0.0).rgb;
    return c / k;
}

// Rotate a (cos, sin) pair by the angle whose (cos, sin) is r
vec2 rotate(vec2 e, vec2 r) { return vec2(e.x * r.x - e.y * r.y, e.y * r.x + e.x * r.y); }

// RF and the TV show come down an aerial, so the TV's IF filter limits the picture: about 4.2 MHz
// in NTSC (M), 5 MHz in PAL B/G, with the sound carrier 4.5 / 5.5 MHz above the picture carrier
// trapped. EPCOS M 3568 M (an NTSC IF filter): the sound carrier 43 dB down, 5.4 MHz 40-55 dB down;
// 512-wide hi-res stripes do not get through (docs/sources/composite-luma-bandwidth.md). The cut is
// written as 1 minus Gaussian bands, fitted to: flat to 3.3 MHz (NTSC) / 4.5 (PAL), -6 dB at about
// 4.0 / 5.1, -12 dB at 4.2 / -15 at 5.32, under 30 dB from 4.5 / 5.5 MHz up. x: centre (MHz),
// y: sigma (MHz), z: depth.
const vec3 IF_NTSC[5] = vec3[5](vec3(4.444, 0.422, 0.5736), vec3(5.421, 0.813, 0.6596), vec3(7.190, 1.263, 0.6918),
                                vec3(10.061, 1.789, 0.8616), vec3(13.686, 1.703, 0.8472));
const vec3 IF_PAL[5] = vec3[5](vec3(5.495, 0.376, 0.6162), vec3(6.414, 0.721, 0.6375), vec3(7.995, 1.190, 0.6450),
                               vec3(10.754, 1.827, 0.8841), vec3(13.976, 1.479, 0.7296));
// How far each band reaches (sigmas) and the weakest band kept. Super lite leaves the IF filter out:
// it is for slow computers, and the filter would cost it a fifth of its frame (docs/sources/lite-presets.md).
const float IF_SIGMAS = 3.0, IF_MIN = 0.004;

void main()
{
    Timing T = getTiming(params.OriginalSize.xy, params.FrameCount);
    float SW = params.SourceSize.x;
    float fs = T.pclk * SW / params.OriginalSize.x;
    float n = floor(vTexCoord.x * SW);
    // row r holds native line r, as in the encoder: an upscaled frame only uses the top 1/k
    float r = floor(vTexCoord.y * params.SourceSize.y);
    float y = r * T.scale;                                  // the line's first row in the frame
    float sr = T.interlace > 0.5 ? 2.0 : 1.0;               // previous line of the same field (rows of this pass)
    float st = sr * T.scale;                                // the same in frame rows
    float cable = T.cable;
    bool show = isShow(cable);                   // TV show: the antenna brings composite
    float Y;
    vec2 uv;

    if (y >= params.OriginalSize.y)
    {
        FragColor = vec4(0.0);
        return;
    }

    if (cable > 2.5 && !show)
    {
        // RGB: no NTSC/PAL at all, only the video amplifier bandwidth: ~6.5 MHz in a TV,
        // ~85 MHz in a 15-inch PC monitor (spec sheets of the 90s: 65-120 MHz)
        float xs = (n + 0.5) * T.pclk / fs;
        float sigPx = 0.1325 / (isPC(T.scan) ? 85.0 : 6.5) * T.pclk;

        // dither blend: the 1-pixel alternating part around the five console pixels
        // the amplifier taps can reach, taken out of every tap below: db.x of its luma,
        // db.y of the rest, its colour (the same share with Dither blend, see ditherBlend)
        vec2 db = ditherBlend(T, cable);
        bool blend = db.x > 0.0 || db.y > 0.0;
        float sp = T.scale;
        float j0 = floor(xs / sp);
        vec3 alt[5];
        for (int i = 0; i < 5; i++) alt[i] = vec3(0.0);
        if (blend)
        {
            vec3 p[13];
            for (int i = 0; i < 13; i++) p[i] = origPix((j0 + float(i - 6) + 0.5) * sp, y, T.scale);
            for (int i = 0; i < 5; i++)
            {
                vec3 a = vec3(0.0);
                for (int k = -4; k <= 4; k++) a += DBW[abs(k)] * dbSign(k) * (p[i + 4 + k] - p[i + 4]);
                float aY = dot(a, vec3(0.299, 0.587, 0.114));
                alt[i] = (db.x * aY + db.y * (a - aY)) / DBN;
            }
        }

        // the amplifier's Gaussian over the frame's pixels, which are flat steps: each pixel's share
        // is the Gaussian's integral over it. Taps a sigma apart read the nearest pixel instead, and at
        // 512 and 640 wide (sigma 0.22 and 0.27 pixels) they stepped over 1-pixel detail: such stripes
        // came out up to a third weaker than 6.5 MHz passes (docs/sources/composite-luma-bandwidth.md)
        float pa = floor(xs - 3.0 * sigPx), pb = floor(xs + 3.0 * sigPx);
        vec3 acc = vec3(0.0);
        float ws = 0.0;
        for (int k = 0; k < 16; k++)
        {
            float j = pa + float(k);
            if (j > pb) break;
            vec3 z = gaussCdf(vec3(j - xs, j + 1.0 - xs, 0.0) / sigPx);
            float w = z.y - z.x;
            vec3 v = origPix(j + 0.5, y, T.scale);
            if (blend) v -= alt[clamp(int(floor((j + 0.5) / sp) - j0) + 2, 0, 4)];
            acc += w * v;
            ws += w;
        }
        vec3 c = acc / ws;
        Y = dot(c, vec3(0.299, 0.587, 0.114));
        uv = vec2(0.492 * (c.b - Y), 0.877 * (c.r - Y));
    }
    else
    {
        bool pal = T.pal > 0.5;
        bool sv = cable > 1.5 && !show;
        bool comb = global.LR_COMB > 0.5 && !sv && !pal && cable > 0.5 && abs(T.lineFrac - 0.5) < 0.05;

        float fcY, fcC, notch;
        if (cable < 0.5)  { fcY = pal ? 3.6 : 2.8; notch = 0.95; fcC = 0.5; }
        else if (!sv)     { fcY = comb ? 4.2 : (pal ? 4.2 : 3.3); notch = comb ? 0.0 : 0.92; fcC = pal ? 0.8 : 0.6; }
        else              { fcY = pal ? 5.0 : 4.6; notch = 0.0; fcC = pal ? 1.0 : 0.9; }

        float tn = n / fs;
        float sh = global.LR_SHARP * 1.4;

        // No flicker: the frames of the subcarrier cycle the eye blends (see steadyFrames).
        // Luma is filtered from their average (the cross-luma dots cancel there), chroma is
        // demodulated for each frame against its own subcarrier and then averaged.
        vec3 off, vsw;
        int nf = steadyFrames(T, off, vsw);
        vec3 lw = nf == 3 ? vec3(1.0 / 3.0) : vec3(0.5, 0.5, 0.0);   // weights of the frames (nf > 1)
        vec2 r1 = vec2(cos(TAU * off.y), sin(TAU * off.y));           // their subcarrier, turned on
        vec2 r2 = vec2(cos(TAU * off.z), sin(TAU * off.z));

        // All taps sit on whole samples. A tap between two samples would read a linear
        // blend of them, and that blend loses part of the subcarrier (colour came out
        // up to 9% weaker). The tap step is a whole number of samples, so the subcarrier
        // still advances by the same angle from tap to tap.

        // luma: (1 + sh) * G(s1) - sh * G(s2), unit gain at DC, boost in the middle.
        float s1 = 0.1325 / fcY;
        float s2 = s1 * 2.5;
        float mY = max(1.0, ceil(0.25 * s2 * fs)); // tap step in samples (at most s2 / 4)
        float nY = min(ceil(3.0 * s2 * fs / mY), 12.0);
        float c1 = -0.5 * mY * mY / (s1 * s1 * fs * fs);
        float c2 = -0.5 * mY * mY / (s2 * s2 * fs * fs);
        float a1 = 0.0, a2 = 0.0, w1s = 0.0, w2s = 0.0;
        int nYi = int(nY);
        // the luma gain at the subcarrier, for the trap
        float hf = (1.0 + sh) * exp(-19.7392 * s1 * s1 * T.fsc * T.fsc) - sh * exp(-19.7392 * s2 * s2 * T.fsc * T.fsc);
        bool trapY = !sv && !comb && notch > 0.0;

        // RF and the TV show: the IF filter (IF_NTSC, IF_PAL) multiplies luma and the trap. Each band
        // of the cut times the luma Gaussian, and the first two times the trap's band, is again a Gaussian
        // band (centre, sigma and depth from the product of two Gaussians), so here it is taken out of luma
        // as a cos-modulated Gaussian over its own taps: bn taps either side, bw its weight, the envelope by
        // the recurrence below (bv, bg, bq) and the cosine by rotation (bp by bc). Bands too weak to matter
        // after the product (luma Gaussian far down there) are left out.
        int nb = 0;
        float bn[7], bw[7], ba[7], bv[7], bg[7], bq[7];
        vec2 bc[7], bp[7];
        float nB = nY;
#ifndef LR_SUPER_LITE
        if (cable < 0.5 || show)
        {
            float sF = fcY / (TAU * 0.1325), sB = fcC / (TAU * 0.1325);   // sigmas in frequency (MHz)
            for (int i = 0; i < 7; i++)
            {
                bool trapBand = i >= 5;
                if (trapBand && !trapY) break;
                vec3 c = pal ? IF_PAL[trapBand ? i - 5 : i] : IF_NTSC[trapBand ? i - 5 : i];
                float s = trapBand ? sB : sF, f0 = trapBand ? T.fsc : 0.0;
                float vs2 = s * s + c.y * c.y;
                float mu = (c.x * s * s + f0 * c.y * c.y) / vs2;   // the product's centre (MHz)
                float tau = sqrt(vs2) / (TAU * s * c.y);            // and its sigma in time (us)
                float depth = c.z * exp(-0.5 * (c.x - f0) * (c.x - f0) / vs2);
                float w = trapBand ? -2.0 * notch * hf * depth : 2.0 * (1.0 + sh) * depth;
                if (abs(w) < IF_MIN) continue;
                float bk = -0.5 * mY * mY / (tau * tau * fs * fs);  // the envelope's exponent per tap^2
                float nt = min(ceil(IF_SIGMAS * tau * fs / mY), 40.0);
                float da = TAU * mu * mY / fs, a0 = -nt * da;
                a0 -= TAU * floor(a0 / TAU + 0.5);
                bn[nb] = nt;
                bw[nb] = w * sqrt(-2.0 * bk / TAU);                 // over the envelope's sum
                bv[nb] = exp(bk * nt * nt);
                bg[nb] = exp(bk * (1.0 - 2.0 * nt));
                bq[nb] = exp(2.0 * bk);
                bc[nb] = vec2(cos(da), sin(da));
                bp[nb] = vec2(cos(a0), sin(a0));                    // (cos, sin) at the band's first tap
                ba[nb] = 0.0;
                nB = max(nB, nt);
                nb++;
            }
        }
#endif
        int nBi = int(nB);
#ifdef LR_SUPER_LITE
        // the Gaussian weights by recurrence, w(u + 1) = w(u) exp(c (2u + 1)): no exp at every tap
        float w1 = exp(c1 * nY * nY), w2 = exp(c2 * nY * nY);
        float g1 = exp(c1 * (1.0 - 2.0 * nY)), g2 = exp(c2 * (1.0 - 2.0 * nY));
        float q1 = exp(2.0 * c1), q2 = exp(2.0 * c2);
#endif
        for (int k = -nBi; k <= nBi; k++)
        {
            float u = float(k);
            float sp = n + u * mY;
            vec4 v = sig(sp, r);
#ifdef LR_SUPER_LITE
            float s0 = v.x;                                 // the frames' average (S-Video: luma)
            if (comb) s0 = 0.5 * (s0 + sig(sp, r - sr).x);
#else
            float s0 = (nf == 1 || sv) ? v.x : dot(v.xyz, lw);
            if (comb)
            {
                vec4 vq = sig(sp, r - sr);
                s0 = 0.5 * (s0 + (nf == 1 ? vq.x : dot(vq.xyz, lw)));
            }
#endif
            if (abs(k) <= nYi)
            {
#ifdef LR_SUPER_LITE
                a1 += w1 * s0; a2 += w2 * s0; w1s += w1; w2s += w2;
                w1 *= g1; g1 *= q1; w2 *= g2; g2 *= q2;
#else
                float w1 = exp(c1 * u * u);
                float w2 = exp(c2 * u * u);
                a1 += w1 * s0; a2 += w2 * s0; w1s += w1; w2s += w2;
#endif
            }
            for (int i = 0; i < 7; i++)
            {
                if (i < nb && abs(u) <= bn[i])
                {
                    ba[i] += bv[i] * bp[i].x * s0;
                    bv[i] *= bg[i]; bg[i] *= bq[i];
                    bp[i] = rotate(bp[i], bc[i]);
                }
            }
        }
        Y = (1.0 + sh) * a1 / w1s - sh * a2 / w2s;
        for (int i = 0; i < 7; i++) if (i < nb) Y -= bw[i] * ba[i];

        // chroma: demodulate against the subcarrier, then low-pass.
        // The subcarrier's (cos, sin) is rotated from tap to tap instead of recomputed.
        float sc = 0.1325 / fcC;
        float mC = max(1.0, ceil(0.15 * sc * fs)); // tap step in samples (at most 0.15 sigma)
        float nC = min(ceil(3.0 * sc * fs / mC), 20.0);
        float cw = -0.5 * mC * mC / (sc * sc * fs * fs);
#ifdef LR_SUPER_LITE
        // The encoder wrote what this decoder demodulates (encode.inc, products): in y and z the
        // signal times this decoder's reference subcarrier (tint included), averaged over the frames
        // of the cycle, with the PAL V-switch; in x their average signal. The chroma is the same
        // low-pass of it as below, and the trap the band of x around the subcarrier (the reference's
        // phase cancels there). The same sums as below, to rounding.
        float da = TAU * T.fsc * mC / fs;
        vec2 rp = vec2(cos(da), sin(da));
        vec2 e = vec2(cos(nC * da), -sin(nC * da));      // (cos, sin) of the first tap's offset
        vec2 acc = vec2(0.0), accp = vec2(0.0);
        float tr = 0.0, wcs = 0.0;
        float w = exp(cw * nC * nC), gw = exp(cw * (1.0 - 2.0 * nC)), qw = exp(2.0 * cw);   // as for luma
        int nCi = int(nC);
        for (int k = -nCi; k <= nCi; k++)
        {
            float sp = n + float(k) * mC;
            vec4 v0 = sig(sp, r);
            acc += w * v0.yz;
            if (pal || comb) accp += w * sig(sp, r - sr).yz;
            tr += w * v0.x * e.x;
            wcs += w;
            e = rotate(e, rp);
            w *= gw; gw *= qw;
        }
        if (trapY) Y -= notch * hf * 2.0 * tr / wcs;
        uv = 2.0 * acc / wcs;
        if (comb)
        {
            // the previous line demodulated against this line's subcarrier: its own products
            // turned back by the phase difference dl between the lines
            float tn0 = n / fs;
            float dl = phaseAt(tn0, y - st, T) - phaseAt(tn0, y, T);
            vec2 q = vec2(accp.x * cos(dl) - accp.y * sin(dl), accp.y * cos(dl) + accp.x * sin(dl));
            uv = (acc - q) / wcs;
        }
        else if (pal)
            uv = 0.5 * (uv + 2.0 * accp / wcs);   // the delay line: the previous line's own products
#else
        float vs = vSign(y, T), vsp = vSign(y - st, T);
        float tint = pal ? 0.0 : radians(global.LR_TINT);
        if (cable < 0.5)
        {
            // RF: the echo is on the colour burst too, so the TV locks to the shifted phase
            float ea = -TAU * T.fsc * RF_ECHO_US;
            tint += atan(RF_ECHO * sin(ea), 1.0 + RF_ECHO * cos(ea));
        }
        else if (show && global.LR_GHOST > 0.0)
        {
            // TV show: the same for the antenna ghost of the broadcast
            float ea = -TAU * T.fsc * SHOW_GHOST_US;
            tint += atan(global.LR_GHOST * sin(ea), 1.0 + global.LR_GHOST * cos(ea));
        }
        float ph0 = phaseAt(tn, y, T) + tint;      // subcarrier phase at the centre tap
        float da = TAU * T.fsc * mC / fs;
        vec2 rp = vec2(cos(da), sin(da));
        vec2 e0 = vec2(cos(ph0), sin(ph0));
        float a0 = ph0 - nC * da;
        a0 -= TAU * floor(a0 / TAU + 0.5);         // keep the angle small for an accurate sin/cos
        vec2 e = vec2(cos(a0), sin(a0));           // (cos, sin) at the first tap
        vec2 acc = vec2(0.0), accp = vec2(0.0);    // sums of w * signal * (sin, cos)
        vec2 acc1 = vec2(0.0), accp1 = vec2(0.0), acc2 = vec2(0.0), accp2 = vec2(0.0);   // No flicker frames
        float wcs = 0.0;
        int nCi = int(nC);
        for (int k = -nCi; k <= nCi; k++)
        {
            float u = float(k);
            float w = exp(cw * u * u);
            float sp = n + u * mC;
            vec4 v0 = sig(sp, r);
            vec3 c3 = sv ? v0.yzw : v0.xyz;          // the chroma signal of each frame
            vec4 vp = (pal || comb) ? sig(sp, r - sr) : vec4(0.0);
            if (comb) c3 = 0.5 * (v0.xyz - vp.xyz);
            float s0 = c3.x;
            acc += w * s0 * e.yx;
            if (pal) accp += w * (sv ? vp.y : vp.x) * e.yx;
            if (nf > 1)
            {
                vec2 e1 = rotate(e, r1);
                vec3 cp = sv ? vp.yzw : vp.xyz;
                acc1 += w * c3.y * e1.yx;
                if (pal) accp1 += w * cp.y * e1.yx;
                if (nf > 2)
                {
                    vec2 e2 = rotate(e, r2);
                    acc2 += w * c3.z * e2.yx;
                    if (pal) accp2 += w * cp.z * e2.yx;
                }
            }
            wcs += w;
            e = rotate(e, rp);
        }
        vec2 cs = 2.0 * vec2(acc.x, vs * acc.y);
        uv = cs / wcs;
        // the previous line has its own subcarrier phase: rotate its sums by the difference
        // (the same for every frame of the cycle)
        float dl = phaseAt(tn, y - st, T) - (ph0 - tint);
        vec2 rd = vec2(cos(dl), sin(dl));

        if (nf == 1)
        {
            // trap: take the chroma band back out of luma
            if (trapY) Y -= notch * hf * (uv.x * e0.y + vs * uv.y * e0.x);
            if (pal)
            {
                vec2 csp = 2.0 * vec2(accp.x * rd.x + accp.y * rd.y, vsp * (accp.y * rd.x - accp.x * rd.y));
                uv = 0.5 * (uv + csp / wcs);
            }
        }
        else
        {
            // No flicker: the same for each frame, with its own subcarrier and V-switch, averaged
            vec2 uvs = vec2(0.0);
            float trapSum = 0.0;
            for (int k = 0; k < 3; k++)
            {
                if (k >= nf) break;
                vec2 a = k == 0 ? acc : (k == 1 ? acc1 : acc2);
                vec2 ap = k == 0 ? accp : (k == 1 ? accp1 : accp2);
                float vk = vSignW(y, T, vsw[k]), vkp = vSignW(y - st, T, vsw[k]);
                vec2 ek = k == 0 ? e0 : rotate(e0, k == 1 ? r1 : r2);
                vec2 u = 2.0 * vec2(a.x, vk * a.y) / wcs;
                trapSum += u.x * ek.y + vk * u.y * ek.x;
                if (pal)
                {
                    vec2 csp = 2.0 * vec2(ap.x * rd.x + ap.y * rd.y, vkp * (ap.y * rd.x - ap.x * rd.y));
                    u = 0.5 * (u + csp / wcs);
                }
                uvs += u;
            }
            if (trapY) Y -= notch * hf * trapSum / float(nf);
            uv = uvs / float(nf);
        }
#endif
        if (cable < 0.5)
        {
            // RF: the echo also lands on sync and burst, and the TV's automatic gain and
            // colour control scale the picture back, so flat areas keep their level and colour
            float ea = -TAU * T.fsc * RF_ECHO_US;
            Y /= 1.0 + RF_ECHO;
            uv /= length(vec2(1.0 + RF_ECHO * cos(ea), RF_ECHO * sin(ea)));
        }
        else if (show && global.LR_GHOST > 0.0)
        {
            // TV show: the same for the antenna ghost of the broadcast
            float ea = -TAU * T.fsc * SHOW_GHOST_US;
            Y /= 1.0 + global.LR_GHOST;
            uv /= length(vec2(1.0 + global.LR_GHOST * cos(ea), global.LR_GHOST * sin(ea)));
        }
    }

    uv *= global.LR_SAT * global.LR_CONTRAST;
    Y = Y * global.LR_CONTRAST + global.LR_BRIGHT;
    vec3 rgb = decodeRGB(Y, uv, decoderType(T, cable));
    FragColor = vec4(clamp(rgb, 0.0, 1.0), 1.0);
}
